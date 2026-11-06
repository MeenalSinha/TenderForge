"""
Bid Lifecycle, Submission Verification & Closed-Loop Learning Service.
Tracks the 14-stage bid lifecycle, issues cryptographic submission receipts,
records tender outcomes, and runs statistical closed-loop learning.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    BidOutcomeRecord,
    BidSubmissionRecord,
    Tender,
    generate_uuid,
)

logger = get_logger(__name__)


class BidOutcomeService:
    """Manages formal bid submissions, outcome debriefs, and closed-loop statistical learning."""

    LIFECYCLE_STAGES = [
        "identified",
        "evaluating_opportunity",
        "bid_approved",
        "no_bid_archived",
        "team_mobilized",
        "compliance_underway",
        "proposal_drafting",
        "internal_review",
        "final_executive_signoff",
        "submitted_to_buyer",
        "clarification_phase",
        "under_buyer_evaluation",
        "awarded_won",
        "lost_or_cancelled",
    ]

    @staticmethod
    def generate_submission_receipt(
        tender_id: str,
        organization_id: str,
        amount: float,
        timestamp: datetime,
        user_id: Optional[str] = None,
    ) -> str:
        raw = f"{tender_id}:{organization_id}:{amount:.2f}:{timestamp.isoformat()}:{user_id or 'anon'}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_bid_submission(
        self,
        db: Session,
        tender_id: str,
        organization_id: str,
        final_bid_amount: float,
        currency: str = "USD",
        submitted_by_user_id: Optional[str] = None,
        submission_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> BidSubmissionRecord:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        now = datetime.now(timezone.utc)
        receipt_hash = self.generate_submission_receipt(
            tender_id=tender_id,
            organization_id=organization_id,
            amount=final_bid_amount,
            timestamp=now,
            user_id=submitted_by_user_id,
        )

        ref_no = submission_reference or f"SUB-{now.strftime('%Y%m%d')}-{generate_uuid()[:6].upper()}"

        submission = BidSubmissionRecord(
            tender_id=tender_id,
            organization_id=organization_id,
            lifecycle_stage="submitted_to_buyer",
            submission_reference=ref_no,
            submitted_by_user_id=submitted_by_user_id,
            submitted_at=now,
            final_bid_amount=final_bid_amount,
            currency=currency,
            submission_receipt_hash=receipt_hash,
            verification_status="submitted",
            notes=notes,
        )
        db.add(submission)

        # Advance tender status
        tender.status = "submitted"
        db.commit()
        db.refresh(submission)
        return submission

    def record_bid_outcome(
        self,
        db: Session,
        submission_id: str,
        outcome: str,  # won, lost, cancelled
        winning_bidder: Optional[str] = None,
        winning_amount: Optional[float] = None,
        our_score: Optional[float] = None,
        winning_score: Optional[float] = None,
        primary_loss_reason: Optional[str] = None,
        debrief_notes: Optional[str] = None,
        win_factors: Optional[List[str]] = None,
    ) -> BidOutcomeRecord:
        sub = db.query(BidSubmissionRecord).filter(BidSubmissionRecord.id == submission_id).first()
        if not sub:
            raise ValueError(f"Bid submission '{submission_id}' not found.")

        norm_outcome = outcome.lower()
        if norm_outcome not in ("won", "lost", "cancelled"):
            raise ValueError(f"Invalid outcome '{outcome}'. Expected 'won', 'lost', or 'cancelled'.")

        existing_outcome = db.query(BidOutcomeRecord).filter(BidOutcomeRecord.submission_id == submission_id).first()
        if existing_outcome:
            record = existing_outcome
            record.outcome = norm_outcome
            record.winning_bidder = winning_bidder
            record.winning_amount = winning_amount
            record.our_score = our_score
            record.winning_score = winning_score
            record.primary_loss_reason = primary_loss_reason
            record.debrief_notes = debrief_notes
            record.win_factors = win_factors or []
            record.recorded_at = datetime.now(timezone.utc)
        else:
            record = BidOutcomeRecord(
                submission_id=sub.id,
                tender_id=sub.tender_id,
                organization_id=sub.organization_id,
                outcome=norm_outcome,
                winning_bidder=winning_bidder,
                winning_amount=winning_amount,
                our_score=our_score,
                winning_score=winning_score,
                primary_loss_reason=primary_loss_reason,
                debrief_notes=debrief_notes,
                win_factors=win_factors or [],
                recorded_at=datetime.now(timezone.utc),
            )
            db.add(record)

        # Update lifecycle stages
        if norm_outcome == "won":
            sub.lifecycle_stage = "awarded_won"
            tender = db.query(Tender).filter(Tender.id == sub.tender_id).first()
            if tender:
                tender.status = "awarded_won"
        elif norm_outcome == "lost":
            sub.lifecycle_stage = "lost_or_cancelled"
            tender = db.query(Tender).filter(Tender.id == sub.tender_id).first()
            if tender:
                tender.status = "lost"
        else:
            sub.lifecycle_stage = "lost_or_cancelled"

        db.commit()
        db.refresh(record)
        return record

    def get_closed_loop_learning(self, db: Session, organization_id: str) -> Dict[str, Any]:
        """
        Calculates organizational win/loss metrics, loss reason distributions, and win attributions.
        Strictly enforces min_sample_size (N >= 5) before projecting statistical learning models.
        """
        outcomes = (
            db.query(BidOutcomeRecord)
            .filter(BidOutcomeRecord.organization_id == organization_id)
            .all()
        )

        total_samples = len(outcomes)
        min_threshold = settings.market_intelligence_config.get(
            "learning_engine", {}
        ).get("min_sample_size_for_statistical_projection", 5)

        won_records = [o for o in outcomes if o.outcome == "won"]
        lost_records = [o for o in outcomes if o.outcome == "lost"]
        cancelled_records = [o for o in outcomes if o.outcome == "cancelled"]

        total_won_value = sum(
            (o.submission.final_bid_amount if o.submission else 0.0) for o in won_records
        )

        win_rate = (len(won_records) / (len(won_records) + len(lost_records)) * 100.0) if (len(won_records) + len(lost_records)) > 0 else 0.0

        # Loss reason frequencies
        loss_reasons_map: Dict[str, int] = {}
        for l in lost_records:
            reason = l.primary_loss_reason or "unspecified_loss_reason"
            loss_reasons_map[reason] = loss_reasons_map.get(reason, 0) + 1

        top_loss_reasons = sorted(
            [{"reason": k, "count": v} for k, v in loss_reasons_map.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        # Win factor attribution
        win_factors_map: Dict[str, int] = {}
        for w in won_records:
            factors = w.win_factors or []
            for f in factors:
                win_factors_map[f] = win_factors_map.get(f, 0) + 1

        top_win_factors = sorted(
            [{"factor": k, "count": v} for k, v in win_factors_map.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        meets_threshold = total_samples >= min_threshold
        statistical_projection_message = (
            "Statistical projection model active."
            if meets_threshold
            else f"Insufficient sample size (N = {total_samples} < {min_threshold}) to project statistically reliable win patterns. Continue recording bid outcomes."
        )

        return {
            "total_recorded_outcomes": total_samples,
            "min_sample_threshold": min_threshold,
            "meets_statistical_threshold": meets_threshold,
            "projection_notice": statistical_projection_message,
            "counts": {
                "won": len(won_records),
                "lost": len(lost_records),
                "cancelled": len(cancelled_records),
            },
            "win_rate_percentage": round(win_rate, 1),
            "total_won_contract_value": round(total_won_value, 2),
            "top_loss_reasons": top_loss_reasons,
            "top_win_factors": top_win_factors,
            "outcomes_detail": [
                {
                    "submission_id": o.submission_id,
                    "tender_id": o.tender_id,
                    "outcome": o.outcome,
                    "winning_bidder": o.winning_bidder,
                    "primary_loss_reason": o.primary_loss_reason,
                    "recorded_at": o.recorded_at.isoformat(),
                }
                for o in outcomes[:20]
            ],
        }

    def list_submissions(
        self,
        db: Session,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[BidSubmissionRecord]:
        return (
            db.query(BidSubmissionRecord)
            .filter(BidSubmissionRecord.organization_id == organization_id)
            .order_by(desc(BidSubmissionRecord.submitted_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

