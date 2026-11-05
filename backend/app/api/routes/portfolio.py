"""
Tender Portfolio & Multi-Workspace Lifecycle API Routes for TenderForge.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["Portfolio Management"])


class UpdateStageRequest(BaseModel):
    stage: str = Field(..., description="Target pipeline stage")
    notes: Optional[str] = None


@router.get("/workspaces/{workspace_id}/portfolio")
def get_portfolio_overview(
    workspace_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = PortfolioService(db)
    try:
        return svc.get_portfolio_overview(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tenders/{tender_id}/stage")
def update_tender_stage(
    tender_id: str,
    payload: UpdateStageRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = PortfolioService(db)
    try:
        wf = svc.update_tender_stage(tender_id, payload.stage, payload.notes)
        return {
            "tender_id": wf.tender_id,
            "current_stage": wf.current_stage,
            "stage_history": wf.stage_history,
            "updated_at": wf.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
