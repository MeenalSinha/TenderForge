"""
Organization and Team Management REST API Routes.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.api.schemas.auth import (
    OrganizationCreateRequest,
    OrganizationMemberInviteRequest,
    OrganizationMemberResponse,
    OrganizationMemberUpdateRoleRequest,
    OrganizationResponse,
)
from backend.app.api.schemas.common import ResponseEnvelope
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.core.logging import correlation_id_ctx
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations & Teams"])


@router.get(
    "",
    response_model=ResponseEnvelope[List[OrganizationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List all accessible organizations",
)
def list_organizations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> ResponseEnvelope[List[OrganizationResponse]]:
    orgs = OrganizationService.list_organizations(db, skip=skip, limit=limit)
    data = [OrganizationResponse.model_validate(o) for o in orgs]
    return ResponseEnvelope[List[OrganizationResponse]](
        success=True,
        status_code=status.HTTP_200_OK,
        message=f"Retrieved {len(data)} organizations.",
        data=data,
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "",
    response_model=ResponseEnvelope[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
def create_organization(
    payload: OrganizationCreateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.ADMIN)),
) -> ResponseEnvelope[OrganizationResponse]:
    org = OrganizationService.create_organization(db, payload.name, payload.slug)
    return ResponseEnvelope[OrganizationResponse](
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="Organization created successfully.",
        data=OrganizationResponse.model_validate(org),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{org_id}",
    response_model=ResponseEnvelope[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get organization details",
)
def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> ResponseEnvelope[OrganizationResponse]:
    org = OrganizationService.get_organization(db, org_id)
    if not org:
        raise EntityNotFoundException(f"Organization '{org_id}' not found.")

    return ResponseEnvelope[OrganizationResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Organization details retrieved.",
        data=OrganizationResponse.model_validate(org),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{org_id}/members",
    response_model=ResponseEnvelope[List[OrganizationMemberResponse]],
    status_code=status.HTTP_200_OK,
    summary="List team members of an organization",
)
def list_organization_members(
    org_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> ResponseEnvelope[List[OrganizationMemberResponse]]:
    members = OrganizationService.list_members(db, org_id)
    data = [OrganizationMemberResponse(**m) for m in members]
    return ResponseEnvelope[List[OrganizationMemberResponse]](
        success=True,
        status_code=status.HTTP_200_OK,
        message=f"Retrieved {len(data)} members.",
        data=data,
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/{org_id}/members",
    response_model=ResponseEnvelope[OrganizationMemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Invite or add a team member to an organization",
)
def invite_member(
    org_id: str,
    payload: OrganizationMemberInviteRequest,
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.APPROVER)),
) -> ResponseEnvelope[OrganizationMemberResponse]:
    member = OrganizationService.invite_member(
        db,
        org_id=org_id,
        email=payload.email,
        role=payload.role,
        inviter_id=claims.get("user_id"),
        full_name=payload.full_name,
    )
    return ResponseEnvelope[OrganizationMemberResponse](
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="Member invited successfully.",
        data=OrganizationMemberResponse(**member),
        correlation_id=correlation_id_ctx.get(),
    )


@router.put(
    "/{org_id}/members/{user_id}",
    response_model=ResponseEnvelope[OrganizationMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Update member role within organization",
)
def update_member_role(
    org_id: str,
    user_id: str,
    payload: OrganizationMemberUpdateRoleRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.ADMIN)),
) -> ResponseEnvelope[OrganizationMemberResponse]:
    member = OrganizationService.update_member_role(db, org_id, user_id, payload.role)
    return ResponseEnvelope[OrganizationMemberResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Member role updated.",
        data=OrganizationMemberResponse(**member),
        correlation_id=correlation_id_ctx.get(),
    )


@router.delete(
    "/{org_id}/members/{user_id}",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove a member from the organization",
)
def remove_member(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.ADMIN)),
) -> ResponseEnvelope[dict]:
    OrganizationService.remove_member(db, org_id, user_id)
    return ResponseEnvelope[dict](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Member removed from organization.",
        data={"removed": True},
        correlation_id=correlation_id_ctx.get(),
    )

