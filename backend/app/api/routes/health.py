"""
Health and Readiness Probes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.infrastructure.database.session import get_db

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict:
    """Liveness probe returning application status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness probe verifying database connectivity, storage writeability, and AI configuration."""
    checks = {
        "database": "unknown",
        "storage": "unknown",
        "ai_provider": "configured" if settings.is_ai_configured else "not_configured",
    }

    # 1. DB check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # 2. Storage check
    try:
        test_file = Path(settings.STORAGE_ROOT) / ".health_check"
        test_file.write_text("probe")
        test_file.unlink()
        checks["storage"] = "writable"
    except Exception as e:
        checks["storage"] = f"unhealthy: {str(e)}"

    is_ready = checks["database"] == "connected" and checks["storage"] == "writable"
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

