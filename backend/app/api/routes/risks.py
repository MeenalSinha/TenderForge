"""
Bid Risk & Mitigation Registry API Routes for TenderForge.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.risk_service import RiskService

router = APIRouter(tags=["Bid Risks"])


class CreateRiskRequest(BaseModel):
    title: str
    category: str = "Compliance"
    likelihood: int = Field(1, ge=1, le=5)
    impact: int = Field(1, ge=1, le=5)
    description: str
    mitigation_strategy: str
    consequences: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner: str = "Bid Manager"


class UpdateRiskStatusRequest(BaseModel):
    status: str = Field(..., description="Open, In_Progress, Mitigated, or Accepted")
    mitigation_strategy: Optional[str] = None
    owner: Optional[str] = None


@router.get("/tenders/{tender_id}/risks")
def list_risks(
    tender_id: str,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> List[Dict[str, Any]]:
    svc = RiskService(db)
    risks = svc.list_risks(tender_id, category=category, risk_level=risk_level)
    return [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "likelihood": r.likelihood,
            "impact": r.impact,
            "severity_score": r.severity_score,
            "risk_level": r.risk_level,
            "description": r.description,
            "consequences": r.consequences,
            "mitigation_strategy": r.mitigation_strategy,
            "contingency_plan": r.contingency_plan,
            "owner": r.owner,
            "status": r.status,
            "source_module": r.source_module,
            "created_at": r.created_at.isoformat(),
        }
        for r in risks
    ]


@router.post("/tenders/{tender_id}/risks", status_code=status.HTTP_201_CREATED)
def create_risk(
    tender_id: str,
    payload: CreateRiskRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = RiskService(db)
    try:
        r = svc.create_risk(
            tender_id=tender_id,
            title=payload.title,
            category=payload.category,
            likelihood=payload.likelihood,
            impact=payload.impact,
            description=payload.description,
            mitigation_strategy=payload.mitigation_strategy,
            consequences=payload.consequences,
            contingency_plan=payload.contingency_plan,
            owner=payload.owner,
            source_module="manual",
        )
        return {
            "id": r.id,
            "title": r.title,
            "severity_score": r.severity_score,
            "risk_level": r.risk_level,
            "status": r.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tenders/{tender_id}/risks/harvest")
def harvest_risks(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> List[Dict[str, Any]]:
    svc = RiskService(db)
    try:
        harvested = svc.harvest_risks_for_tender(tender_id)
        return [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "severity_score": r.severity_score,
                "risk_level": r.risk_level,
                "source_module": r.source_module,
            }
            for r in harvested
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/risks/{risk_id}")
def update_risk(
    risk_id: str,
    payload: UpdateRiskStatusRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = RiskService(db)
    try:
        r = svc.update_risk_status(
            risk_id=risk_id,
            status=payload.status,
            mitigation_strategy=payload.mitigation_strategy,
            owner=payload.owner,
        )
        return {
            "id": r.id,
            "title": r.title,
            "status": r.status,
            "mitigation_strategy": r.mitigation_strategy,
            "owner": r.owner,
            "updated_at": r.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
