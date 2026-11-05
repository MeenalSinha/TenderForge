"""
Financial Proposal & Commercial Workspace API Routes for TenderForge.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.models import FinancialProposal
from backend.app.infrastructure.database.session import get_db
from backend.app.services.financial_service import FinancialService

router = APIRouter(tags=["Financial Workspace"])


class CreateFinancialProposalRequest(BaseModel):
    proposal_id: Optional[str] = None
    title: str = "Commercial Proposal & Pricing Schedule"
    currency: Optional[str] = None
    tax_rate_percent: Optional[str] = None
    contingency_rate_percent: Optional[str] = None
    overhead_rate_percent: Optional[str] = None
    margin_rate_percent: Optional[str] = None
    initial_items: Optional[List[Dict[str, Any]]] = None


class AddLineItemRequest(BaseModel):
    item_code: str
    description: str
    category: str = "Services"
    unit: str = "each"
    quantity: str = "1.00"
    unit_rate: str = "0.00"
    tax_percent: Optional[str] = None
    notes: Optional[str] = None


@router.post("/tenders/{tender_id}/financial-proposal", status_code=status.HTTP_201_CREATED)
def create_financial_proposal(
    tender_id: str,
    payload: CreateFinancialProposalRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = FinancialService(db)
    try:
        fin_prop = svc.create_financial_proposal(
            tender_id=tender_id,
            proposal_id=payload.proposal_id,
            title=payload.title,
            currency=payload.currency,
            tax_rate_percent=payload.tax_rate_percent,
            contingency_rate_percent=payload.contingency_rate_percent,
            overhead_rate_percent=payload.overhead_rate_percent,
            margin_rate_percent=payload.margin_rate_percent,
            initial_items=payload.initial_items,
        )
        return _serialize_financial_proposal(fin_prop)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tenders/{tender_id}/financial-proposal")
def get_financial_proposal(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    prop = (
        db.query(FinancialProposal)
        .filter(FinancialProposal.tender_id == tender_id)
        .order_by(FinancialProposal.created_at.desc())
        .first()
    )
    if not prop:
        raise HTTPException(status_code=404, detail="No financial proposal found for this tender.")
    return _serialize_financial_proposal(prop)


@router.post("/financial-proposals/{proposal_id}/line-items", status_code=status.HTTP_201_CREATED)
def add_line_item(
    proposal_id: str,
    payload: AddLineItemRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = FinancialService(db)
    try:
        item = svc.add_line_item(
            financial_proposal_id=proposal_id,
            item_code=payload.item_code,
            description=payload.description,
            category=payload.category,
            unit=payload.unit,
            quantity=payload.quantity,
            unit_rate=payload.unit_rate,
            tax_percent=payload.tax_percent,
            notes=payload.notes,
        )
        return {
            "id": item.id,
            "item_code": item.item_code,
            "description": item.description,
            "category": item.category,
            "quantity": item.quantity,
            "unit_rate": item.unit_rate,
            "line_total": item.line_total,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/financial-proposals/{proposal_id}/scenarios")
def generate_scenarios(
    proposal_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> List[Dict[str, Any]]:
    svc = FinancialService(db)
    try:
        scenarios = svc.generate_scenarios(proposal_id)
        return [
            {
                "id": s.id,
                "scenario_name": s.scenario_name,
                "margin_rate_percent": s.margin_rate_percent,
                "contingency_rate_percent": s.contingency_rate_percent,
                "discount_percent": s.discount_percent,
                "calculated_total": s.calculated_total,
                "summary_metrics": s.summary_metrics,
            }
            for s in scenarios
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/financial-proposals/{proposal_id}/export-excel")
def export_excel(
    proposal_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
):
    svc = FinancialService(db)
    try:
        path = svc.export_excel(proposal_id)
        return FileResponse(
            path=path,
            filename=f"commercial_proposal_{proposal_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _serialize_financial_proposal(prop: FinancialProposal) -> Dict[str, Any]:
    return {
        "id": prop.id,
        "tender_id": prop.tender_id,
        "title": prop.title,
        "currency": prop.currency,
        "subtotal": prop.subtotal,
        "contingency_amount": prop.contingency_amount,
        "contingency_rate_percent": prop.contingency_rate_percent,
        "overhead_amount": prop.overhead_amount,
        "overhead_rate_percent": prop.overhead_rate_percent,
        "margin_amount": prop.margin_amount,
        "margin_rate_percent": prop.margin_rate_percent,
        "tax_amount": prop.tax_amount,
        "tax_rate_percent": prop.tax_rate_percent,
        "total_price": prop.total_price,
        "status": prop.status,
        "validation_errors": prop.validation_errors,
        "line_items": [
            {
                "id": item.id,
                "item_code": item.item_code,
                "description": item.description,
                "category": item.category,
                "unit": item.unit,
                "quantity": item.quantity,
                "unit_rate": item.unit_rate,
                "tax_percent": item.tax_percent,
                "line_total": item.line_total,
                "notes": item.notes,
            }
            for item in prop.line_items
        ],
        "scenarios": [
            {
                "id": s.id,
                "scenario_name": s.scenario_name,
                "calculated_total": s.calculated_total,
            }
            for s in prop.scenarios
        ],
        "created_at": prop.created_at.isoformat(),
    }
