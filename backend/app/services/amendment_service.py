"""
Amendment Intelligence & Impact Propagation Engine.
Analyzes tender corrigenda, classifies materiality, and propagates downstream impacts.
"""

from __future__ import annotations

import difflib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    ComplianceMatrix,
    HumanApproval,
    ProposalSection,
    Tender,
    TenderAmendment,
    TenderRequirement,
    generate_uuid,
)

logger = get_logger(__name__)


class AmendmentService:
    """Detects, classifies, and propagates tender amendments and corrigenda."""

    def classify_materiality(
        self,
        changes: List[str],
        deadline_changed: bool = False,
        budget_changed: bool = False,
        eligibility_changed: bool = False,
    ) -> str:
        """Determines materiality level: critical, major, or minor."""
        if deadline_changed or budget_changed or eligibility_changed:
            return "critical"

        for ch in changes:
            ch_lower = ch.lower()
            if any(k in ch_lower for k in ("mandatory", "penalty", "sla", "liquidated damages", "warranty", "scope")):
                return "major"

        return "minor"

    def record_amendment(
        self,
        db: Session,
        tender_id: str,
        amendment_number: str,
        title: str,
        diff_summary: str,
        affected_clauses: List[Dict[str, Any]],
        deadline_changed: bool = False,
        budget_changed: bool = False,
        eligibility_changed: bool = False,
    ) -> TenderAmendment:
        """
        Creates an amendment record and automatically executes downstream impact propagation.
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        materiality = self.classify_materiality(
            changes=[c.get("description", "") for c in affected_clauses],
            deadline_changed=deadline_changed,
            budget_changed=budget_changed,
            eligibility_changed=eligibility_changed,
        )

        downstream_impact = {
            "affected_requirements": [],
            "affected_compliance_items": [],
            "affected_proposal_sections": [],
            "approval_invalidated": False,
            "required_actions": [],
        }

        # 1. Flag affected requirements
        requirements = db.query(TenderRequirement).filter(TenderRequirement.tender_id == tender_id).all()
        for clause in affected_clauses:
            clause_kw = str(clause.get("keyword", "")).lower()
            for req in requirements:
                desc = req.description or ""
                excerpt = req.source_excerpt or ""
                if clause_kw and (clause_kw in desc.lower() or clause_kw in excerpt.lower()):
                    downstream_impact["affected_requirements"].append({
                        "id": req.id,
                        "description": desc[:100],
                        "impact": clause.get("description", "Clause wording updated"),
                    })

        # 2. Flag compliance matrix for re-assessment
        matrix = db.query(ComplianceMatrix).filter(ComplianceMatrix.tender_id == tender_id).first()
        if matrix:
            matrix.overall_status = "Clarification Required"
            matrix.summary = f"Flagged for reassessment due to Amendment {amendment_number}."
            downstream_impact["affected_compliance_items"].append(matrix.id)

        # 3. Check and invalidate existing executive approvals if Critical
        approval_invalidated = False
        if materiality == "critical":
            existing_approvals = db.query(HumanApproval).filter(HumanApproval.tender_id == tender_id).all()
            for app in existing_approvals:
                if app.decision == "Approved":
                    app.decision = "Changes Requested"
                    app.comments = f"Approval invalidated due to Critical Corrigendum {amendment_number}. Requires re-approval."
                    approval_invalidated = True

            downstream_impact["approval_invalidated"] = approval_invalidated
            downstream_impact["required_actions"].append("Executive re-approval required before proposal finalization.")

        amendment = TenderAmendment(
            tender_id=tender_id,
            amendment_number=amendment_number,
            title=title,
            publication_date=datetime.now(timezone.utc),
            materiality=materiality,
            diff_summary=diff_summary,
            affected_clauses=affected_clauses,
            downstream_impact=downstream_impact,
            approval_invalidated=approval_invalidated,
            created_at=datetime.now(timezone.utc),
        )
        db.add(amendment)
        db.commit()
        db.refresh(amendment)
        return amendment

    def acknowledge_amendment(
        self,
        db: Session,
        amendment_id: str,
        user_id: str,
        notes: Optional[str] = None,
    ) -> TenderAmendment:
        amendment = db.query(TenderAmendment).filter(TenderAmendment.id == amendment_id).first()
        if not amendment:
            raise ValueError(f"Amendment '{amendment_id}' not found.")

        amendment.acknowledged_by_user_id = user_id
        amendment.acknowledged_at = datetime.now(timezone.utc)
        if notes:
            from sqlalchemy.orm.attributes import flag_modified
            impact = dict(amendment.downstream_impact or {})
            impact["acknowledgement_notes"] = notes
            amendment.downstream_impact = impact
            flag_modified(amendment, "downstream_impact")

        db.commit()
        db.refresh(amendment)
        return amendment

    def list_amendments(self, db: Session, tender_id: str) -> List[TenderAmendment]:
        return (
            db.query(TenderAmendment)
            .filter(TenderAmendment.tender_id == tender_id)
            .order_by(TenderAmendment.created_at.desc())
            .all()
        )
