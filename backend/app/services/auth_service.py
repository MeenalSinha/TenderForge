"""
Authentication and User Account Service for TenderForge Phase 4.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.schemas.auth import UserRegisterRequest
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AuthenticationException,
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from backend.app.core.logging import get_logger
from backend.app.core.security_auth import (
    create_access_token,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)
from backend.app.infrastructure.database.models import (
    Organization,
    OrganizationMember,
    PasswordResetToken,
    User,
    UserSession,
    Workspace,
)

logger = get_logger("tenderforge.auth_service")


def slugify(text: str) -> str:
    """Convert text into an alphanumeric slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "org"


class AuthService:
    """Enterprise authentication, user identity, and session manager."""

    @staticmethod
    def register_user(
        db: Session,
        req: UserRegisterRequest,
    ) -> Tuple[User, str]:
        """Register a new user account, assign organization membership, and return JWT token."""
        normalized_email = req.email.lower().strip()

        # Check existing user
        existing = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()
        if existing:
            raise ConflictException(f"User with email '{normalized_email}' is already registered.")

        # Hash password and create user
        hashed = hash_password(req.password)
        user = User(
            email=normalized_email,
            hashed_password=hashed,
            full_name=req.full_name.strip(),
            role=req.role or "Author",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.flush()

        # Associate with organization
        org: Optional[Organization] = None
        if req.organization_name:
            slug = slugify(req.organization_name)
            org = db.execute(
                select(Organization).where(Organization.slug == slug)
            ).scalar_one_or_none()
            if not org:
                org = Organization(name=req.organization_name.strip(), slug=slug)
                db.add(org)
                db.flush()

                # Also create a default workspace for the new org
                ws = Workspace(
                    organization_id=org.id,
                    name=f"{org.name} Main Workspace",
                    description=f"Primary workspace for {org.name}",
                )
                db.add(ws)
                db.flush()
                member_role = "Admin"
            else:
                member_role = req.role or "Author"
        else:
            # Fall back to default organization
            org = db.execute(
                select(Organization).where(Organization.id == settings.default_organization_id)
            ).scalar_one_or_none()
            if not org:
                # Create default org if not present
                org = Organization(
                    id=settings.default_organization_id,
                    name="Default Organization",
                    slug="default-org",
                )
                db.add(org)
                db.flush()
            member_role = req.role or "Author"

        # Create organization membership
        membership = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role=member_role,
        )
        db.add(membership)
        db.commit()
        db.refresh(user)

        # Generate JWT access token
        claims = {
            "sub": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": org.id,
        }
        token = create_access_token(claims)
        logger.info(f"Registered user '{user.email}' (ID: {user.id}) in organization '{org.name}'")
        return user, token

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str]:
        """Authenticate user by email and password, creating a logged session."""
        normalized_email = email.lower().strip()
        user = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: '{normalized_email}'")
            raise AuthenticationException("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationException("User account is inactive. Please contact your administrator.")

        # Determine user's active organization ID if present
        membership = db.execute(
            select(OrganizationMember).where(OrganizationMember.user_id == user.id)
        ).scalars().first()
        org_id = membership.organization_id if membership else settings.default_organization_id

        # Generate JWT token
        claims = {
            "sub": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": org_id,
        }
        token = create_access_token(claims)

        # Save session
        token_digest = hash_token(token)
        session = UserSession(
            user_id=user.id,
            token_hash=token_digest,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else None,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            is_revoked=False,
        )
        db.add(session)
        db.commit()

        logger.info(f"User '{user.email}' logged in successfully.")
        return user, token

    @staticmethod
    def logout_user(db: Session, token: str) -> bool:
        """Revoke the current session by token hash."""
        token_digest = hash_token(token)
        session = db.execute(
            select(UserSession).where(UserSession.token_hash == token_digest)
        ).scalar_one_or_none()
        if session:
            session.is_revoked = True
            db.commit()
            return True
        return False

    @staticmethod
    def request_password_reset(db: Session, email: str) -> Optional[str]:
        """Generate a single-use password reset token with 1-hour expiration."""
        normalized_email = email.lower().strip()
        user = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

        if not user:
            # For security, avoid leaking whether the email exists
            logger.info(f"Password reset requested for non-existent email '{normalized_email}'")
            return None

        raw_token = generate_secure_token(32)
        token_digest = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_digest,
            expires_at=expires_at,
            is_used=False,
        )
        db.add(reset_token)
        db.commit()
        logger.info(f"Generated password reset token for user '{user.email}'")
        return raw_token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Validate single-use reset token and update password."""
        token_digest = hash_token(token)
        now = datetime.now(timezone.utc)

        token_record = db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_digest,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > now,
            )
        ).scalar_one_or_none()

        if not token_record:
            raise ValidationException("Password reset token is invalid or has expired.")

        user = db.execute(
            select(User).where(User.id == token_record.user_id)
        ).scalar_one_or_none()

        if not user:
            raise EntityNotFoundException("User not found.")

        user.hashed_password = hash_password(new_password)
        user.updated_at = now
        token_record.is_used = True
        db.commit()
        logger.info(f"Password successfully reset for user '{user.email}'")
        return True

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change password for an authenticated user after verifying their current password."""
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if not user:
            raise EntityNotFoundException("User not found.")

        if not verify_password(current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect.")

        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Password changed for user '{user.email}'")
        return True

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.execute(select(User).where(User.email == email.lower().strip())).scalar_one_or_none()

