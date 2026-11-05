"""
Bid Risk & Mitigation Intelligence Service for TenderForge.

Centralized risk registry aggregating exposures across:
- Compliance & Statutory Eligibility
- Evidence Integrity & Expiration
- Commercial & Financial Margins
- Schedule & Timeline Constraints
- Legal & Contractual Penalties
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.infrastructure.database.models import (
    BidRisk,
    ComplianceMatrix,
    CompanyEvidence,
    FinancialProposal,
    Tender,
    TenderDeadline,
    utcnow,
)

logger = logging.getLogger(__name__)


class RiskService:
    """Aggregates, scores, and tracks bid risks across the tender lifecycle."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.matrix_cfg = settings.risk_matrix_config

    def create_risk(
        self,
        tender_id: str,
        title: str,
        category: str,
        likelihood: int,
        impact: int,
        description: str,
        mitigation_strategy: str,
        consequences: Optional[str] = None,
        contingency_plan: Optional[str] = None,
        owner: str = "Bid Manager",
        source_module: str = "manual",
        status: str = "Open",
        db: Optional[Session] = None,
    ) -> BidRisk:
        """Create a scored risk entry in the centralized registry."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        likelihood = max(1, min(5, likelihood))
        impact = max(1, min(5, impact))
        sev_score = likelihood * impact

        risk_level = "Low"
        if sev_score >= 15:
            risk_level = "High"
        elif sev_score >= 7:
            risk_level = "Medium"

        risk = BidRisk(
            tender_id=tender_id,
            title=title,
            category=category,
            likelihood=likelihood,
            impact=impact,
            severity_score=sev_score,
            risk_level=risk_level,
            description=description,
            consequences=consequences,
            mitigation_strategy=mitigation_strategy,
            contingency_plan=contingency_plan,
            owner=owner,
            source_module=source_module,
            status=status,
        )
        session.add(risk)
        session.commit()
        session.refresh(risk)
        return risk

    def harvest_risks_for_tender(
        self,
        tender_id: str,
        db: Optional[Session] = None,
    ) -> List[BidRisk]:
        """Automatically aggregate risks from compliance matrices, evidence repository, financial proposals, and deadlines."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tender = session.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        harvested: List[BidRisk] = []

        # 1. Harvest from Compliance Matrix
        comp = (
            session.query(ComplianceMatrix)
            .filter(ComplianceMatrix.tender_id == tender_id)
            .order_by(ComplianceMatrix.created_at.desc())
            .first()
        )
        if comp and comp.items:
            for item in comp.items:
                if item.get("status") == "Non-Compliant":
                    title = f"Compliance Gap: {item.get('description', '')[:60]}"
                    existing = session.query(BidRisk).filter(
                        BidRisk.tender_id == tender_id,
                        BidRisk.title == title,
                    ).first()
                    if not existing:
                        r = self.create_risk(
                            tender_id=tender_id,
                            title=title,
                            category="Compliance",
                            likelihood=4,
                            impact=5,
                            description=item.get("description", ""),
                            consequences="Disqualification or mandatory compliance rejection.",
                            mitigation_strategy="Request official clarification from issuing authority or seek joint venture partner.",
                            owner="Compliance Officer",
                            source_module="compliance",
                            db=session,
                        )
                        harvested.append(r)

        # 2. Harvest from Financial Proposal
        fin = (
            session.query(FinancialProposal)
            .filter(FinancialProposal.tender_id == tender_id)
            .order_by(FinancialProposal.created_at.desc())
            .first()
        )
        if fin and fin.validation_errors:
            for err in fin.validation_errors:
                title = f"Pricing Defect: {err[:60]}"
                existing = session.query(BidRisk).filter(
                    BidRisk.tender_id == tender_id,
                    BidRisk.title == title,
                ).first()
                if not existing:
                    r = self.create_risk(
                        tender_id=tender_id,
                        title=title,
                        category="Financial",
                        likelihood=4,
                        impact=4,
                        description=err,
                        consequences="Incorrect pricing schedule or rejection of commercial bid.",
                        mitigation_strategy="Correct itemized BOQ quantities and recalculate commercial total.",
                        owner="Financial Estimator",
                        source_module="financial",
                        db=session,
                    )
                    harvested.append(r)

        # 3. Harvest from Deadlines
        deadlines = (
            session.query(TenderDeadline)
            .filter(TenderDeadline.tender_id == tender_id, TenderDeadline.status == "Upcoming")
            .all()
        )
        for dl in deadlines:
            # If approaching within 48 hours
            time_diff = dl.deadline_date - utcnow().replace(tzinfo=None)
            if 0 < time_diff.total_seconds() < 172800:
                title = f"Imminent Deadline: {dl.title}"
                existing = session.query(BidRisk).filter(
                    BidRisk.tender_id == tender_id,
                    BidRisk.title == title,
                ).first()
                if not existing:
                    r = self.create_risk(
                        tender_id=tender_id,
                        title=title,
                        category="Timeline",
                        likelihood=3,
                        impact=4,
                        description=f"Submission deadline '{dl.title}' expires in less than 48 hours.",
                        consequences="Risk of late bid submission.",
                        mitigation_strategy="Mobilize senior review team and finalize executive sign-offs.",
                        owner="Bid Manager",
                        source_module="deadlines",
                        db=session,
                    )
                    harvested.append(r)

        return harvested

    def update_risk_status(
        self,
        risk_id: str,
        status: str,  # Open, In_Progress, Mitigated, Accepted
        mitigation_strategy: Optional[str] = None,
        owner: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> BidRisk:
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        risk = session.query(BidRisk).filter(BidRisk.id == risk_id).first()
        if not risk:
            raise ValueError(f"BidRisk '{risk_id}' not found.")

        risk.status = status
        if mitigation_strategy:
            risk.mitigation_strategy = mitigation_strategy
        if owner:
            risk.owner = owner
        risk.updated_at = utcnow()

        session.commit()
        session.refresh(risk)
        return risk

    def list_risks(
        self,
        tender_id: str,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> List[BidRisk]:
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        query = session.query(BidRisk).filter(BidRisk.tender_id == tender_id)
        if category:
            query = query.filter(BidRisk.category == category)
        if risk_level:
            query = query.filter(BidRisk.risk_level == risk_level)

        return query.order_by(BidRisk.severity_score.desc()).all()
