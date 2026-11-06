"""
Authentication and Organization Pydantic Schemas for TenderForge Phase 4.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password with minimum 8 characters")
    full_name: str = Field(..., min_length=2, max_length=255)
    role: Optional[str] = Field("Author", description="Initial role: Viewer, Author, Reviewer, Approver, Admin")
    organization_name: Optional[str] = Field(None, description="Optional organization name to create or join")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(...)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None  # Included for dev/testing environment convenience


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class OrganizationMemberInviteRequest(BaseModel):
    email: EmailStr
    role: str = Field("Author", description="Viewer, Author, Reviewer, Approver, Admin")
    full_name: Optional[str] = Field(None, min_length=2)


class OrganizationMemberUpdateRoleRequest(BaseModel):
    role: str = Field(..., description="Viewer, Author, Reviewer, Approver, Admin")


class OrganizationMemberResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    email: str
    full_name: str
    role: str
    invited_by: Optional[str] = None
    created_at: datetime

