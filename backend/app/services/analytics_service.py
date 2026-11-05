"""
Analytics & Performance Intelligence Service for TenderForge.

Calculates operational intelligence metrics across:
1. Tender Pipeline Performance (processing duration, volume, pipeline value).
2. Compliance & Evidence Health (pass rates, gap frequency, ProofLink density).
3. Proposal Quality & Depth (citation ratios, audit readiness, word counts).
4. Multi-Agent Performance & Human Collaboration (tool runs, override ratios).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    BidAudit,
    BidEvaluation,
    ClaimLineage,
    ComplianceMatrix,
    HumanApproval,
    Proposal,
    Tender,
    TenderRequirement,
    Workspace,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Computes measured operational, compliance, proposal, and agent performance analytics."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    def get_workspace_analytics(
        self,
        workspace_id: str,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Aggregate operational analytics for an entire workspace."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tenders = session.query(Tender).filter(Tender.workspace_id == workspace_id).all()
        tender_ids = [t.id for t in tenders]

        total_tenders = len(tenders)
        total_value = sum(float(t.estimated_value or 0.0) for t in tenders)

        # 1. Compliance Analytics
        requirements = session.query(TenderRequirement).filter(TenderRequirement.tender_id.in_(tender_ids)).all() if tender_ids else []
        total_reqs = len(requirements)
        mandatory_reqs = sum(1 for r in requirements if r.classification == "mandatory")

        compliance_matrices = session.query(ComplianceMatrix).filter(ComplianceMatrix.tender_id.in_(tender_ids)).all() if tender_ids else []
        compliant_count = sum(1 for c in compliance_matrices if c.overall_status == "Compliant")
        comp_rate = round((compliant_count / len(compliance_matrices) * 100.0) if compliance_matrices else 100.0, 1)

        # 2. Proposal & ProofLink Analytics
        proposals = session.query(Proposal).filter(Proposal.tender_id.in_(tender_ids)).all() if tender_ids else []
        proposal_ids = [p.id for p in proposals]

        audits = session.query(BidAudit).filter(BidAudit.proposal_id.in_(proposal_ids)).all() if proposal_ids else []
        avg_readiness = round(sum(a.readiness_score for a in audits) / len(audits), 1) if audits else 0.0

        lineages = session.query(ClaimLineage).filter(ClaimLineage.tender_id.in_(tender_ids)).all() if tender_ids else []
        verified_lineages = sum(1 for l in lineages if l.review_status == "verified")
        lineage_verification_rate = round((verified_lineages / len(lineages) * 100.0) if lineages else 100.0, 1)

        # 3. Bid Decision & Human Collaboration Analytics
        bid_evals = session.query(BidEvaluation).filter(BidEvaluation.tender_id.in_(tender_ids)).all() if tender_ids else []
        bid_recs = {"BID": 0, "BID WITH CONDITIONS": 0, "NO-BID RECOMMENDED": 0}
        overridden_count = 0
        decided_count = 0

        for b in bid_evals:
            bid_recs[b.recommendation] = bid_recs.get(b.recommendation, 0) + 1
            if b.human_decision != "PENDING":
                decided_count += 1
                if b.human_decision == "OVERRIDDEN":
                    overridden_count += 1

        override_rate = round((overridden_count / decided_count * 100.0) if decided_count > 0 else 0.0, 1)

        return {
            "workspace_id": workspace_id,
            "pipeline": {
                "total_tenders": total_tenders,
                "total_estimated_value": round(total_value, 2),
                "proposals_drafted": len(proposals),
            },
            "compliance": {
                "total_requirements_analyzed": total_reqs,
                "mandatory_requirements_count": mandatory_reqs,
                "compliance_matrices_evaluated": len(compliance_matrices),
                "compliance_pass_rate_percent": comp_rate,
            },
            "prooflink": {
                "total_claim_lineages": len(lineages),
                "verified_claims_count": verified_lineages,
                "prooflink_verification_rate_percent": lineage_verification_rate,
                "average_bid_readiness_score": avg_readiness,
            },
            "collaboration": {
                "bid_evaluations_count": len(bid_evals),
                "recommendation_breakdown": bid_recs,
                "human_decisions_recorded": decided_count,
                "human_override_rate_percent": override_rate,
            },
        }
