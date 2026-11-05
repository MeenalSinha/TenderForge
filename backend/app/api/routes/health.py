"""
Health, Readiness and Diagnostics Probes for TenderForge.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.storage.object_storage import get_storage_provider

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict:
    """Liveness probe returning application runtime status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness probe verifying database connectivity, storage writeability, and subsystem health."""
    checks = {
        "database": "unknown",
        "storage": "unknown",
        "ai_provider": "configured" if settings.is_ai_configured else "not_configured",
        "auth_subsystem": "operational",
    }

    # 1. Database connectivity
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # 2. Storage writeability & adapter check
    try:
        storage = get_storage_provider()
        test_path = ".health_probe.tmp"
        storage.save(test_path, b"probe_ok")
        if storage.exists(test_path):
            storage.delete(test_path)
            checks["storage"] = f"healthy ({settings.STORAGE_PROVIDER})"
        else:
            checks["storage"] = "write_failed"
    except Exception as e:
        checks["storage"] = f"unhealthy: {str(e)}"

    is_ready = checks["database"] == "connected" and "healthy" in checks["storage"]
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/diagnostics", status_code=status.HTTP_200_OK)
def system_diagnostics(db: Session = Depends(get_db)) -> dict:
    """Detailed non-sensitive operational diagnostics for monitoring and DevOps telemetry."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "system": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
        },
        "database": {
            "status": db_status,
            "driver": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
        },
        "storage": {
            "provider": settings.STORAGE_PROVIDER,
            "root_path": settings.STORAGE_ROOT,
        },
        "security": {
            "jwt_algorithm": settings.JWT_ALGORITHM,
            "jwt_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "bcrypt_rounds": settings.BCRYPT_ROUNDS,
            "auth_rate_limit_per_minute": settings.AUTH_RATE_LIMIT_PER_MINUTE,
        },
        "integrations": {
            "ai_configured": settings.is_ai_configured,
            "ai_provider": settings.AI_PROVIDER,
            "ai_model": settings.AI_MODEL_NAME,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

