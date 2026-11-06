"""
Bid Submissions, Outcomes & Closed-Loop Learning API Routes.
Manages the 14-stage bid lifecycle, cryptographic submission receipts, and statistical learning.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import BidSubmissionRecord
from backend.app.infrastructure.database.session import get_db
from backend.app.services.bid_outcome_service import BidOutcomeService

router = APIRouter(tags=["Bid Submissions & Outcomes"])


class RecordSubmissionRequest(BaseModel):
    final_bid_amount: float = Field(..., gt=0.0)
    currency: str = "USD"
    submission_reference: Optional[str] = None
    notes: Optional[str] = None


class RecordOutcomeRequest(BaseModel):
    outcome: str = Field(..., description="won, lost, or cancelled")
    winning_bidder: Optional[str] = None
    winning_amount: Optional[float] = None
    our_score: Optional[float] = None
    winning_score: Optional[float] = None
    primary_loss_reason: Optional[str] = None
    debrief_notes: Optional[str] = None
    win_factors: Optional[List[str]] = None


@router.post("/tenders/{tender_id}/submissions", status_code=status.HTTP_201_CREATED)
def submit_bid(
    tender_id: str,
    payload: RecordSubmissionRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.APPROVER)),
) -> Dict[str, Any]:
    org_id = claims.get("org_id") or settings.default_organization_id
    user_id = claims.get("sub")
    svc = BidOutcomeService()
    try:
        sub = svc.record_bid_submission(
            db=db,
            tender_id=tender_id,
            organization_id=org_id,
            final_bid_amount=payload.final_bid_amount,
            currency=payload.currency,
            submitted_by_user_id=user_id,
            submission_reference=payload.submission_reference,
            notes=payload.notes,
        )
        return {
            "status": "success",
            "message": "Bid submitted successfully. Cryptographic receipt generated.",
            "submission": {
                "id": sub.id,
                "tender_id": sub.tender_id,
                "submission_reference": sub.submission_reference,
                "lifecycle_stage": sub.lifecycle_stage,
                "final_bid_amount": sub.final_bid_amount,
                "currency": sub.currency,
                "submission_receipt_hash": sub.submission_receipt_hash,
                "submitted_at": sub.submitted_at.isoformat(),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/submissions")
def list_submissions(
    organization_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or (claims.get("org_id") if isinstance(claims, dict) else None) or settings.default_organization_id
    skp = skip if isinstance(skip, int) else 0
    lmt = limit if isinstance(limit, int) else 50
    svc = BidOutcomeService()
    submissions = svc.list_submissions(db, org_id, skip=skp, limit=lmt)
    return {
        "count": len(submissions),
        "submissions": [
            {
                "id": s.id,
                "tender_id": s.tender_id,
                "submission_reference": s.submission_reference,
                "lifecycle_stage": s.lifecycle_stage,
                "final_bid_amount": s.final_bid_amount,
                "currency": s.currency,
                "submission_receipt_hash": s.submission_receipt_hash,
                "has_outcome": bool(s.outcome),
                "outcome": s.outcome.outcome if s.outcome else None,
                "submitted_at": s.submitted_at.isoformat(),
            }
            for s in submissions
        ],
    }


@router.post("/submissions/{submission_id}/outcome")
def record_outcome(
    submission_id: str,
    payload: RecordOutcomeRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = BidOutcomeService()
    try:
        record = svc.record_bid_outcome(
            db=db,
            submission_id=submission_id,
            outcome=payload.outcome,
            winning_bidder=payload.winning_bidder,
            winning_amount=payload.winning_amount,
            our_score=payload.our_score,
            winning_score=payload.winning_score,
            primary_loss_reason=payload.primary_loss_reason,
            debrief_notes=payload.debrief_notes,
            win_factors=payload.win_factors,
        )
        return {
            "status": "success",
            "message": f"Bid outcome recorded as '{record.outcome}'.",
            "outcome": {
                "id": record.id,
                "submission_id": record.submission_id,
                "tender_id": record.tender_id,
                "outcome": record.outcome,
                "winning_bidder": record.winning_bidder,
                "primary_loss_reason": record.primary_loss_reason,
                "win_factors": record.win_factors,
                "recorded_at": record.recorded_at.isoformat(),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/analytics/bid-learning")
def get_bid_learning_analytics(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = BidOutcomeService()
    return svc.get_closed_loop_learning(db, org_id)
