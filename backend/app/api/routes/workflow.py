"""
Workflow State Machine API endpoints for TenderForge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status as http_status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.session import get_db
from backend.app.services.workflow_orchestrator import WorkflowOrchestrator

router = APIRouter(tags=["Workflow Orchestration"])
workflow_orchestrator = WorkflowOrchestrator()


class WorkflowStepRequest(BaseModel):
    organization_id: str


@router.get("/tenders/{tender_id}/workflow", status_code=http_status.HTTP_200_OK)
def get_workflow_state(
    tender_id: str,
    db: Session = Depends(get_db),
):
    state = workflow_orchestrator.get_or_create_workflow(db, tender_id)
    return {
        "status": "success",
        "data": {
            "tender_id": state.tender_id,
            "current_stage": state.current_stage,
            "stage_history": state.stage_history,
        }
    }


@router.post("/tenders/{tender_id}/workflow/step", status_code=http_status.HTTP_200_OK)
def execute_workflow_step(
    tender_id: str,
    payload: WorkflowStepRequest,
    db: Session = Depends(get_db),
):
    result = workflow_orchestrator.execute_next_stage(
        db=db,
        tender_id=tender_id,
        organization_id=payload.organization_id,
    )
    return {
        "status": "success",
        "data": result,
    }
