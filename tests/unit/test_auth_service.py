"""
Unit tests for Authentication, Hashing, JWTs, and AuthService.
"""

import pytest
from backend.app.api.schemas.auth import UserRegisterRequest
from backend.app.core.exceptions import AuthenticationException, ConflictException, ValidationException
from backend.app.core.security_auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.app.services.auth_service import AuthService
from backend.app.services.organization_service import OrganizationService


def test_password_hashing():
    pwd = "SecurePassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "user-123", "role": "Author", "email": "test@example.com"}
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "Author"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded


def test_user_registration_and_authentication(db_session):
    req = UserRegisterRequest(
        email="bidmaster@enterprise.org",
        password="MasterPassword2026!",
        full_name="Bid Master",
        role="Author",
        organization_name="Enterprise Solutions",
    )

    user, token = AuthService.register_user(db_session, req)
    assert user.id is not None
    assert user.email == "bidmaster@enterprise.org"
    assert user.full_name == "Bid Master"
    assert token is not None

    # Duplicate registration should raise ConflictException
    with pytest.raises(ConflictException):
        AuthService.register_user(db_session, req)

    # Authenticate with correct credentials
    auth_user, auth_token = AuthService.authenticate_user(
        db_session,
        email="bidmaster@enterprise.org",
        password="MasterPassword2026!",
    )
    assert auth_user.id == user.id
    assert auth_token is not None

    # Authenticate with wrong credentials
    with pytest.raises(AuthenticationException):
        AuthService.authenticate_user(
            db_session,
            email="bidmaster@enterprise.org",
            password="WrongPassword999!",
        )


def test_password_reset_flow(db_session):
    req = UserRegisterRequest(
        email="forgot@enterprise.org",
        password="InitialPassword123!",
        full_name="Forgot User",
        role="Author",
    )
    user, _ = AuthService.register_user(db_session, req)

    # Request reset token
    raw_token = AuthService.request_password_reset(db_session, "forgot@enterprise.org")
    assert raw_token is not None

    # Consume reset token
    success = AuthService.reset_password(db_session, raw_token, "NewSecurePassword2026!")
    assert success is True

    # Token cannot be reused (single-use check)
    with pytest.raises(ValidationException):
        AuthService.reset_password(db_session, raw_token, "AnotherPassword123!")

    # Verify user can log in with new password
    auth_user, _ = AuthService.authenticate_user(
        db_session,
        email="forgot@enterprise.org",
        password="NewSecurePassword2026!",
    )
    assert auth_user.id == user.id


def test_organization_and_team_management(db_session):
    org = OrganizationService.create_organization(
        db_session,
        name="Global Tender Corp",
    )
    assert org.id is not None
    assert org.name == "Global Tender Corp"

    # Invite a member
    member = OrganizationService.invite_member(
        db_session,
        org_id=org.id,
        email="member1@globaltender.com",
        role="Reviewer",
        full_name="Jane Reviewer",
    )
    assert member["email"] == "member1@globaltender.com"
    assert member["role"] == "Reviewer"

    # List members
    members = OrganizationService.list_members(db_session, org.id)
    assert len(members) >= 1

    # Update role
    updated = OrganizationService.update_member_role(
        db_session,
        org_id=org.id,
        user_id=member["user_id"],
        new_role="Approver",
    )
    assert updated["role"] == "Approver"

    # Remove member
    removed = OrganizationService.remove_member(
        db_session,
        org_id=org.id,
        user_id=member["user_id"],
    )
    assert removed is True
