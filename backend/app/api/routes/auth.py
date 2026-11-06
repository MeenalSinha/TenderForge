"""
Authentication and User Account REST API Routes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.api.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from backend.app.api.schemas.common import ResponseEnvelope
from backend.app.core.config import settings
from backend.app.core.exceptions import AuthenticationException
from backend.app.core.logging import correlation_id_ctx
from backend.app.core.rbac import get_current_user_claims
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ResponseEnvelope[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> ResponseEnvelope[TokenResponse]:
    user, token = AuthService.register_user(db, payload)
    data = TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user),
    )
    return ResponseEnvelope[TokenResponse](
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="User account registered successfully.",
        data=data,
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/login",
    response_model=ResponseEnvelope[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT token",
)
def login(
    payload: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ResponseEnvelope[TokenResponse]:
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user, token = AuthService.authenticate_user(
        db,
        email=payload.email,
        password=payload.password,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    data = TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user),
    )
    return ResponseEnvelope[TokenResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Authentication successful.",
        data=data,
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/logout",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_200_OK,
    summary="Revoke the current authentication session",
)
def logout(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> ResponseEnvelope[dict]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        AuthService.logout_user(db, token)

    return ResponseEnvelope[dict](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Logged out successfully.",
        data={"revoked": True},
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/me",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get profile of the currently authenticated user",
)
def get_current_user_profile(
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
) -> ResponseEnvelope[UserResponse]:
    user_id = claims.get("user_id")
    user = AuthService.get_user_by_id(db, user_id) if user_id else None

    if not user:
        user = AuthService.get_user_by_email(db, claims.get("email", ""))
        if not user:
            raise AuthenticationException("User account not found or session has expired.")

    return ResponseEnvelope[UserResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="User profile retrieved.",
        data=UserResponse.model_validate(user),
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/forgot-password",
    response_model=ResponseEnvelope[ForgotPasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Request a password reset token",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ResponseEnvelope[ForgotPasswordResponse]:
    token = AuthService.request_password_reset(db, payload.email)
    return ResponseEnvelope[ForgotPasswordResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="If this email is registered, a password reset link has been dispatched.",
        data=ForgotPasswordResponse(
            message="Password reset instructions dispatched.",
            reset_token=token,
        ),
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/reset-password",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_200_OK,
    summary="Reset password using a valid reset token",
)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResponseEnvelope[dict]:
    AuthService.reset_password(db, payload.token, payload.new_password)
    return ResponseEnvelope[dict](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Password has been successfully updated. You may now log in.",
        data={"reset": True},
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/change-password",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_200_OK,
    summary="Change password for authenticated user",
)
def change_password(
    payload: ChangePasswordRequest,
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
) -> ResponseEnvelope[dict]:
    user_id = claims.get("user_id")
    if not user_id:
        raise AuthenticationException("Authentication required to change password.")

    AuthService.change_password(db, user_id, payload.current_password, payload.new_password)
    return ResponseEnvelope[dict](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Password updated successfully.",
        data={"changed": True},
        correlation_id=correlation_id_ctx.get(),
    )
