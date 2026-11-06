"""
Organization and Team Management Service for TenderForge Phase 4.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.app.core.exceptions import (
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from backend.app.core.logging import get_logger
from backend.app.core.security_auth import hash_password
from backend.app.infrastructure.database.models import (
    Organization,
    OrganizationMember,
    User,
    Workspace,
)

logger = get_logger("tenderforge.organization_service")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "org"


class OrganizationService:
    """Manages organization profiles, workspaces, and team memberships."""

    @staticmethod
    def create_organization(
        db: Session,
        name: str,
        slug: Optional[str] = None,
    ) -> Organization:
        org_slug = slug or slugify(name)
        existing = db.execute(
            select(Organization).where(Organization.slug == org_slug)
        ).scalar_one_or_none()
        if existing:
            raise ConflictException(f"Organization with slug '{org_slug}' already exists.")

        org = Organization(name=name.strip(), slug=org_slug)
        db.add(org)
        db.flush()

        # Create primary workspace
        ws = Workspace(
            organization_id=org.id,
            name=f"{org.name} Workspace",
            description=f"Default collaborative workspace for {org.name}",
        )
        db.add(ws)
        db.commit()
        db.refresh(org)
        logger.info(f"Created organization '{org.name}' ({org.id})")
        return org

    @staticmethod
    def get_organization(db: Session, org_id: str) -> Optional[Organization]:
        return db.execute(
            select(Organization).where(Organization.id == org_id)
        ).scalar_one_or_none()

    @staticmethod
    def list_organizations(
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Organization]:
        return list(
            db.execute(
                select(Organization).offset(skip).limit(limit)
            ).scalars().all()
        )

    @staticmethod
    def list_members(db: Session, org_id: str) -> List[Dict[str, Any]]:
        org = OrganizationService.get_organization(db, org_id)
        if not org:
            raise EntityNotFoundException(f"Organization '{org_id}' not found.")

        query = (
            select(OrganizationMember, User)
            .join(User, OrganizationMember.user_id == User.id)
            .where(OrganizationMember.organization_id == org_id)
        )
        results = db.execute(query).all()

        members = []
        for member, user in results:
            members.append({
                "id": member.id,
                "organization_id": member.organization_id,
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": member.role,
                "invited_by": member.invited_by,
                "created_at": member.created_at,
            })
        return members

    @staticmethod
    def invite_member(
        db: Session,
        org_id: str,
        email: str,
        role: str = "Author",
        inviter_id: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        org = OrganizationService.get_organization(db, org_id)
        if not org:
            raise EntityNotFoundException(f"Organization '{org_id}' not found.")

        normalized_email = email.lower().strip()
        user = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

        if not user:
            # Create user with a generated temporary password
            temp_pwd = hash_password("TenderForge2026!Temp")
            user = User(
                email=normalized_email,
                hashed_password=temp_pwd,
                full_name=(full_name or normalized_email.split("@")[0]).strip(),
                role=role,
                is_active=True,
                is_verified=False,
            )
            db.add(user)
            db.flush()

        # Check existing membership
        existing_member = db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user.id,
            )
        ).scalar_one_or_none()

        if existing_member:
            raise ConflictException(f"User '{normalized_email}' is already a member of this organization.")

        member = OrganizationMember(
            organization_id=org_id,
            user_id=user.id,
            role=role,
            invited_by=inviter_id,
        )
        db.add(member)
        db.commit()
        db.refresh(member)

        logger.info(f"Added member '{user.email}' to organization '{org.name}' with role '{role}'")
        return {
            "id": member.id,
            "organization_id": member.organization_id,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": member.role,
            "invited_by": member.invited_by,
            "created_at": member.created_at,
        }

    @staticmethod
    def update_member_role(
        db: Session,
        org_id: str,
        user_id: str,
        new_role: str,
    ) -> Dict[str, Any]:
        member = db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
        ).scalar_one_or_none()

        if not member:
            raise EntityNotFoundException(f"User is not a member of organization '{org_id}'.")

        valid_roles = ["Viewer", "Author", "Reviewer", "Approver", "Admin"]
        if new_role not in valid_roles:
            raise ValidationException(f"Role must be one of: {', '.join(valid_roles)}")

        member.role = new_role
        db.commit()

        user = db.execute(select(User).where(User.id == user_id)).scalar_one()
        return {
            "id": member.id,
            "organization_id": member.organization_id,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": member.role,
            "invited_by": member.invited_by,
            "created_at": member.created_at,
        }

    @staticmethod
    def remove_member(
        db: Session,
        org_id: str,
        user_id: str,
    ) -> bool:
        member = db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
        ).scalar_one_or_none()

        if not member:
            raise EntityNotFoundException(f"Member not found in organization '{org_id}'.")

        db.delete(member)
        db.commit()
        logger.info(f"Removed member '{user_id}' from organization '{org_id}'")
        return True

