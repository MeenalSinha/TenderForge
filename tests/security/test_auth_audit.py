"""
Authentication, Header Injection, and Switch Connectivity Security Tests.
Tests route handlers, RBAC dependencies, and Switch status directly.
"""

from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.api.routes.auth import get_current_user_profile, login
from backend.app.api.routes.switch import get_switch_status
from backend.app.api.schemas.auth import UserLoginRequest
from backend.app.core.exceptions import AuthenticationException
from backend.app.core.rbac import get_current_user_claims


def test_auth_me_unauthorized_no_token():
    """Verify missing authorization raises 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_claims(authorization=None)
    assert exc_info.value.status_code == 401
    assert "Authentication token required" in exc_info.value.detail


def test_auth_me_invalid_token():
    """Verify invalid authorization token raises 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_claims(authorization="Bearer invalid.token.value")
    assert exc_info.value.status_code == 401
    assert "Invalid or expired access token" in exc_info.value.detail


def test_auth_me_no_fallback_admin(db_session: Session):
    """Verify nonexistent user claims in /me raises AuthenticationException without fallback."""
    with pytest.raises(AuthenticationException) as exc_info:
        get_current_user_profile(
            claims={"user_id": "usr-nonexistent-synthetic", "email": "ghost@tenderforge.com"},
            db=db_session,
        )
    assert "not found or session has expired" in str(exc_info.value).lower()


def test_switch_status_endpoint():
    """Verify /api/v1/switch/status returns genuine connectivity diagnostic status."""
    resp = get_switch_status()
    assert isinstance(resp, dict)
    assert resp["status"] in ["connected", "degraded", "disconnected", "not_configured"]
    assert resp["agents_registered"] >= 5
    assert resp["tools_registered"] >= 30
    assert "timestamp" in resp


def test_invalid_login_credentials(db_session: Session):
    """Verify login with invalid password rejects access cleanly with 401."""
    mock_request = MagicMock(spec=Request)
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest-test-runner"}

    with pytest.raises(AuthenticationException):
        login(
            payload=UserLoginRequest(
                email="ghost@tenderforge.com",
                password="WrongPassword123!",
            ),
            request=mock_request,
            db=db_session,
        )
