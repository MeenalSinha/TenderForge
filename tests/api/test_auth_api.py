"""
API Route tests for Authentication and Organization endpoints.
Tests route handlers directly to ensure 100% test reliability on Python 3.14.
"""

import pytest
from unittest.mock import MagicMock
from fastapi import Request
from backend.app.api.routes.auth import (
    change_password,
    forgot_password,
    get_current_user_profile,
    login,
    logout,
    register,
    reset_password,
)
from backend.app.api.routes.organizations import (
    create_organization,
    get_organization,
    invite_member,
    list_organization_members,
    list_organizations,
    remove_member,
    update_member_role,
)
from backend.app.api.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    OrganizationCreateRequest,
    OrganizationMemberInviteRequest,
    OrganizationMemberUpdateRoleRequest,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
)


def test_auth_api_routes_lifecycle(db_session):
    # 1. Register new user
    reg_req = UserRegisterRequest(
        email="apitester@enterprise.com",
        password="Password2026!Secure",
        full_name="API Tester",
        role="Author",
        organization_name="API Testing Org",
    )
    reg_resp = register(reg_req, db=db_session)
    assert reg_resp.success is True
    assert reg_resp.data.access_token is not None
    user_id = reg_resp.data.user.id

    # 2. Login
    dummy_req = MagicMock(spec=Request)
    dummy_req.client.host = "127.0.0.1"
    dummy_req.headers = {"user-agent": "pytest-client"}

    login_req = UserLoginRequest(
        email="apitester@enterprise.com",
        password="Password2026!Secure",
    )
    login_resp = login(login_req, request=dummy_req, db=db_session)
    assert login_resp.success is True
    assert login_resp.data.access_token is not None

    # 3. Get profile /me
    claims = {
        "user_id": user_id,
        "email": "apitester@enterprise.com",
        "role": "Author",
    }
    me_resp = get_current_user_profile(claims=claims, db=db_session)
    assert me_resp.success is True
    assert me_resp.data.email == "apitester@enterprise.com"

    # 4. Forgot password & reset password
    forgot_resp = forgot_password(
        ForgotPasswordRequest(email="apitester@enterprise.com"),
        db=db_session,
    )
    assert forgot_resp.success is True
    reset_token = forgot_resp.data.reset_token
    assert reset_token is not None

    reset_resp = reset_password(
        ResetPasswordRequest(token=reset_token, new_password="NewSecret2026!Updated"),
        db=db_session,
    )
    assert reset_resp.success is True

    # 5. Change password
    chg_resp = change_password(
        ChangePasswordRequest(
            current_password="NewSecret2026!Updated",
            new_password="EvenMoreSecure2026!P4",
        ),
        claims=claims,
        db=db_session,
    )
    assert chg_resp.success is True

    # 6. Logout
    logout_resp = logout(
        authorization=f"Bearer {login_resp.data.access_token}",
        db=db_session,
    )
    assert logout_resp.success is True


def test_organizations_api_routes(db_session):
    # 1. Create organization
    create_req = OrganizationCreateRequest(
        name="Aerospace Defense Group",
        slug="aerospace-defense-group",
    )
    create_resp = create_organization(create_req, db=db_session, _role="Admin")
    assert create_resp.success is True
    org_id = create_resp.data.id

    # 2. Get organization
    get_resp = get_organization(org_id, db=db_session, _role="Viewer")
    assert get_resp.success is True
    assert get_resp.data.name == "Aerospace Defense Group"

    # 3. List organizations
    list_resp = list_organizations(db=db_session, _role="Viewer")
    assert list_resp.success is True
    assert any(o.id == org_id for o in list_resp.data)

    # 4. Invite member
    invite_req = OrganizationMemberInviteRequest(
        email="engineer@defense.org",
        role="Author",
        full_name="Chief Engineer",
    )
    claims = {"user_id": "usr-admin-01"}
    invite_resp = invite_member(org_id, invite_req, claims=claims, db=db_session, _role="Approver")
    assert invite_resp.success is True
    invited_user_id = invite_resp.data.user_id

    # 5. List members
    members_resp = list_organization_members(org_id, db=db_session, _role="Viewer")
    assert members_resp.success is True
    assert len(members_resp.data) >= 1

    # 6. Update member role
    update_role_req = OrganizationMemberUpdateRoleRequest(role="Reviewer")
    update_resp = update_member_role(org_id, invited_user_id, update_role_req, db=db_session, _role="Admin")
    assert update_resp.success is True
    assert update_resp.data.role == "Reviewer"

    # 7. Remove member
    del_resp = remove_member(org_id, invited_user_id, db=db_session, _role="Admin")
    assert del_resp.success is True
