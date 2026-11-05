"""
Server-side Role-Based Access Control (RBAC) Engine for TenderForge.

Roles:
- Viewer: Read-only access to workspaces, tenders, proposals, audits, and financial schedules.
- Author: Ingest documents, draft proposal sections, add BOQ line items, run AI extractions.
- Reviewer: Audit compliance, execute bid audits, trigger proposal optimizations, harvest risks.
- Approver: Executive sign-off for Bid/No-Bid decisions, proposal sign-offs, and financial locking.
- Admin: All permissions, workspace configuration, user role assignments.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security_auth import decode_access_token
from backend.app.infrastructure.database.models import User, UserRole
from backend.app.infrastructure.database.session import get_db

logger = logging.getLogger(__name__)


class Role(str, Enum):
    VIEWER = "Viewer"
    AUTHOR = "Author"
    REVIEWER = "Reviewer"
    APPROVER = "Approver"
    ADMIN = "Admin"


ROLE_HIERARCHY = {
    Role.VIEWER: 1,
    Role.AUTHOR: 2,
    Role.REVIEWER: 3,
    Role.APPROVER: 4,
    Role.ADMIN: 5,
}

ROLE_PERMISSIONS = {
    Role.VIEWER: ["read"],
    Role.AUTHOR: ["read", "write", "draft"],
    Role.REVIEWER: ["read", "write", "draft", "audit", "optimize"],
    Role.APPROVER: ["read", "write", "draft", "audit", "optimize", "approve"],
    Role.ADMIN: ["read", "write", "draft", "audit", "optimize", "approve", "admin"],
}


def verify_role_permission(
    user_role: str,
    required_role: Role,
) -> bool:
    """Check if the user's role meets or exceeds the required hierarchical role level."""
    try:
        user_r = Role(user_role)
    except ValueError:
        user_r = Role.VIEWER

    user_level = ROLE_HIERARCHY.get(user_r, 1)
    req_level = ROLE_HIERARCHY.get(required_role, 1)
    return user_level >= req_level


def get_current_user_claims(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> dict:
    """Extract authenticated user claims from Authorization header or fallback headers."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        if payload:
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "Author"),
                "org_id": payload.get("org_id", settings.default_organization_id),
            }

    # Fallback for API integration testing / scripts
    user_id = x_user_id or "usr-system-admin"
    role = x_user_role or "Admin"
    return {
        "user_id": user_id,
        "email": "admin@tenderforge.local",
        "role": role,
        "org_id": settings.default_organization_id,
    }


def require_role(required_role: Role):
    """FastAPI dependency to enforce minimum role authorization via JWT Bearer or X-User-Role header."""
    def dependency(
        authorization: Optional[str] = Header(None),
        x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
        x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    ) -> str:
        if not settings.rbac_config.get("enabled", True):
            return "Admin"

        # Check token claims first
        claims = get_current_user_claims(authorization, x_user_role, x_user_id)
        role_str = claims.get("role", "Viewer")

        if not verify_role_permission(role_str, required_role):
            logger.warning(
                "Access denied: User '%s' with role '%s' requires '%s'",
                claims.get("user_id"),
                role_str,
                required_role.value,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Action requires at least '{required_role.value}' role.",
            )
        return role_str

    return dependency
