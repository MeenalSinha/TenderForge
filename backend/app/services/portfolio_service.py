"""
Tender Portfolio & Multi-Workspace Lifecycle Service for TenderForge.

Manages pipeline stages across the organizational tender portfolio:
Opportunity -> Qualified -> Bid Decision -> Preparation -> Review -> Approved -> Submitted -> Won / Lost / Abandoned.
Computes aggregate pipeline metrics, win rates, and deadline heatmaps.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    BidEvaluation,
    Tender,
    TenderDeadline,
    WorkflowState,
    Workspace,
    utcnow,
)

logger = logging.getLogger(__name__)

PORTFOLIO_STAGES = [
    "Opportunity",
    "Qualified",
    "Bid Decision",
    "Preparation",
    "Review",
    "Approved",
    "Submitted",
    "Won",
    "Lost",
    "Abandoned",
]


class PortfolioService:
    """Manages multi-tender enterprise portfolio, stage progressions, and aggregate analytics."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    def update_tender_stage(
        self,
        tender_id: str,
        new_stage: str,
        notes: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> WorkflowState:
        """Advance or update the tender's portfolio pipeline stage."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        if new_stage not in PORTFOLIO_STAGES and new_stage != "WORKSPACE_INITIALIZED":
            raise ValueError(f"Invalid stage '{new_stage}'. Must be one of {PORTFOLIO_STAGES}")

        wf = session.query(WorkflowState).filter(WorkflowState.tender_id == tender_id).first()
        if not wf:
            wf = WorkflowState(
                tender_id=tender_id,
                current_stage=new_stage,
                stage_history=[],
            )
            session.add(wf)

        history_entry = {
            "from_stage": wf.current_stage,
            "to_stage": new_stage,
            "timestamp": utcnow().isoformat(),
            "notes": notes or f"Stage transitioned to {new_stage}",
        }
        history = list(wf.stage_history or [])
        history.append(history_entry)
        wf.stage_history = history
        wf.current_stage = new_stage
        wf.updated_at = utcnow()

        # Update tender status as well
        tender = session.query(Tender).filter(Tender.id == tender_id).first()
        if tender:
            tender.status = new_stage.lower().replace(" ", "_")
            tender.updated_at = utcnow()

        session.commit()
        session.refresh(wf)
        return wf

    def get_portfolio_overview(
        self,
        workspace_id: str,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate high-level executive portfolio metrics and pipeline distribution."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tenders = session.query(Tender).filter(Tender.workspace_id == workspace_id).all()
        total_count = len(tenders)

        stage_counts = {s: 0 for s in PORTFOLIO_STAGES}
        total_pipeline_value = 0.0
        won_count = 0
        decided_count = 0

        tender_summaries: List[Dict[str, Any]] = []

        now = datetime.now(timezone.utc)

        for t in tenders:
            stage = "Opportunity"
            if t.workflow_state and t.workflow_state.current_stage in stage_counts:
                stage = t.workflow_state.current_stage
            elif t.status:
                for s in PORTFOLIO_STAGES:
                    if s.lower().replace(" ", "_") == t.status.lower():
                        stage = s
                        break

            stage_counts[stage] = stage_counts.get(stage, 0) + 1

            val = float(t.estimated_value or 0.0)
            if stage not in ["Won", "Lost", "Abandoned"]:
                total_pipeline_value += val

            if stage == "Won":
                won_count += 1
                decided_count += 1
            elif stage == "Lost":
                decided_count += 1

            # Deadline status
            deadline_str = None
            days_left = None
            if t.submission_deadline:
                dl = t.submission_deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                deadline_str = dl.isoformat()
                days_left = (dl - now).days

            # Bid Decision
            latest_bid_eval = (
                session.query(BidEvaluation)
                .filter(BidEvaluation.tender_id == t.id)
                .order_by(BidEvaluation.created_at.desc())
                .first()
            )

            tender_summaries.append({
                "id": t.id,
                "reference_number": t.reference_number,
                "title": t.title,
                "issuing_authority": t.issuing_authority,
                "stage": stage,
                "estimated_value": val,
                "currency": t.currency,
                "submission_deadline": deadline_str,
                "days_remaining": days_left,
                "bid_recommendation": latest_bid_eval.recommendation if latest_bid_eval else "UNASSESSED",
                "bid_score": latest_bid_eval.overall_score if latest_bid_eval else None,
            })

        win_rate = round((won_count / decided_count * 100.0) if decided_count > 0 else 0.0, 1)

        return {
            "workspace_id": workspace_id,
            "total_tenders": total_count,
            "active_pipeline_value": round(total_pipeline_value, 2),
            "win_rate_percent": win_rate,
            "stage_distribution": stage_counts,
            "tenders": tender_summaries,
        }
