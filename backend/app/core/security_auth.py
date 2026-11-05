"""
Security and Cryptography Module for TenderForge Phase 4.

Provides enterprise password hashing (bcrypt), JWT authentication,
and secure single-use token hashing.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt
from fastapi import HTTPException, status
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger("tenderforge.security_auth")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with configured salt rounds."""
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plaintext password matches a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception as e:
        logger.warning(f"Password verification failure: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token containing arbitrary payload claims."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a signed JWT access token. Returns claims dict or None."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("Access token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid access token: {e}")
        return None


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a cryptographically secure random token string for URL/reset use."""
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    """Compute a SHA-256 hash of a token for secure database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
