"""
Compliance Assessment API endpoints for TenderForge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status as http_status
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.session import get_db
from backend.app.services.compliance_service import ComplianceService

router = APIRouter(tags=["Compliance Assessment"])
compliance_service = ComplianceService()


@router.post("/tenders/{tender_id}/compliance/evaluate", status_code=http_status.HTTP_200_OK)
def evaluate_compliance(
    tender_id: str,
    evaluator: str = "ComplianceOfficer",
    db: Session = Depends(get_db),
):
    matrix = compliance_service.evaluate_tender_compliance(
        db=db,
        tender_id=tender_id,
        evaluator_agent=evaluator,
    )
    return {
        "status": "success",
        "data": {
            "matrix_id": matrix.id,
            "overall_status": matrix.overall_status,
            "overall_risk_level": matrix.overall_risk_level,
            "evaluated_by_agent": matrix.evaluated_by_agent,
            "summary": matrix.summary,
            "items_count": len(matrix.items),
            "items": matrix.items,
        }
    }


@router.get("/tenders/{tender_id}/compliance", status_code=http_status.HTTP_200_OK)
def get_compliance_matrix(
    tender_id: str,
    db: Session = Depends(get_db),
):
    matrix = compliance_service.get_latest_matrix(db, tender_id)
    if not matrix:
        return {"status": "error", "message": f"No compliance matrix found for tender '{tender_id}'."}, 404
    return {
        "status": "success",
        "data": {
            "matrix_id": matrix.id,
            "overall_status": matrix.overall_status,
            "overall_risk_level": matrix.overall_risk_level,
            "evaluated_by_agent": matrix.evaluated_by_agent,
            "summary": matrix.summary,
            "items": matrix.items,
        }
    }
