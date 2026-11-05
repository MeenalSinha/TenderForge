"""
Analytics & Operational Intelligence API Routes for TenderForge.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.get("/workspaces/{workspace_id}/analytics")
def get_workspace_analytics(
    workspace_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = AnalyticsService(db)
    try:
        return svc.get_workspace_analytics(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
