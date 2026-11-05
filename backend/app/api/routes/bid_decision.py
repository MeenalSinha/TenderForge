"""
Bid/No-Bid Decision Intelligence API Routes for TenderForge.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.bid_decision_service import BidDecisionService

router = APIRouter(tags=["Bid Intelligence"])


class EvaluateBidRequest(BaseModel):
    evaluator_type: str = "agent"
    evaluator_id: str = "BidIntelligenceEngine"
    dimension_overrides: Optional[Dict[str, float]] = None


class HumanDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVED_BID, APPROVED_NO_BID, or OVERRIDDEN")
    user_id: str
    user_name: str
    rationale: str = Field(..., min_length=10)


@router.post("/tenders/{tender_id}/bid-evaluation", status_code=status.HTTP_201_CREATED)
def evaluate_tender(
    tender_id: str,
    payload: EvaluateBidRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> Dict[str, Any]:
    svc = BidDecisionService(db)
    try:
        eval_record = svc.evaluate_tender(
            tender_id=tender_id,
            evaluator_type=payload.evaluator_type,
            evaluator_id=payload.evaluator_id,
            custom_dimension_overrides=payload.dimension_overrides,
        )
        return {
            "evaluation_id": eval_record.id,
            "tender_id": eval_record.tender_id,
            "recommendation": eval_record.recommendation,
            "overall_score": eval_record.overall_score,
            "eligibility_gates_passed": eval_record.eligibility_gates_passed,
            "failed_gates": eval_record.failed_gates,
            "conditions": eval_record.conditions,
            "dimensions": eval_record.dimensions,
            "executive_summary": eval_record.executive_summary,
            "human_decision": eval_record.human_decision,
            "created_at": eval_record.created_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tenders/{tender_id}/bid-evaluation")
def get_latest_bid_evaluation(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = BidDecisionService(db)
    eval_record = svc.get_latest_evaluation(tender_id)
    if not eval_record:
        raise HTTPException(status_code=404, detail="No bid evaluation found for this tender.")

    return {
        "evaluation_id": eval_record.id,
        "tender_id": eval_record.tender_id,
        "recommendation": eval_record.recommendation,
        "overall_score": eval_record.overall_score,
        "eligibility_gates_passed": eval_record.eligibility_gates_passed,
        "failed_gates": eval_record.failed_gates,
        "conditions": eval_record.conditions,
        "dimensions": eval_record.dimensions,
        "executive_summary": eval_record.executive_summary,
        "human_decision": eval_record.human_decision,
        "human_decision_by": eval_record.human_decision_by,
        "human_decision_rationale": eval_record.human_decision_rationale,
        "human_decision_at": eval_record.human_decision_at.isoformat() if eval_record.human_decision_at else None,
        "created_at": eval_record.created_at.isoformat(),
    }


@router.post("/bid-evaluations/{evaluation_id}/decision")
def record_human_bid_decision(
    evaluation_id: str,
    payload: HumanDecisionRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.APPROVER)),
) -> Dict[str, Any]:
    svc = BidDecisionService(db)
    try:
        updated = svc.record_human_decision(
            evaluation_id=evaluation_id,
            decision=payload.decision,
            user_id=payload.user_id,
            user_name=payload.user_name,
            rationale=payload.rationale,
        )
        return {
            "evaluation_id": updated.id,
            "human_decision": updated.human_decision,
            "human_decision_by": updated.human_decision_by,
            "human_decision_rationale": updated.human_decision_rationale,
            "human_decision_at": updated.human_decision_at.isoformat() if updated.human_decision_at else None,
            "status": "recorded",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
