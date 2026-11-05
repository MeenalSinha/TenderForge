"""
Compliance Assessment Engine for TenderForge.
Evaluates regulatory, technical, and commercial requirements against evidence to generate compliance matrices.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    ComplianceMatrix,
    EvidenceRequirementLink,
    Tender,
    TenderRequirement,
)
from backend.app.services.prooflink_service import ProofLinkStatus

logger = get_logger("compliance_service")


class ComplianceStatus:
    COMPLIANT = "Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    NON_COMPLIANT = "Non-Compliant"
    CLARIFICATION_REQUIRED = "Clarification Required"


class RiskLevel:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplianceService:
    """Evaluates tender requirements against ProofLink evidence links to produce structured compliance matrices."""

    def evaluate_tender_compliance(
        self,
        db: Session,
        tender_id: str,
        evaluator_agent: str = "ComplianceOfficer",
    ) -> ComplianceMatrix:
        """Evaluate full compliance matrix for a tender opportunity."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        requirements = db.query(TenderRequirement).filter(
            TenderRequirement.tender_id == tender_id
        ).all()

        evaluated_items: List[Dict[str, Any]] = []
        has_critical_failure = False
        has_high_risk = False
        has_clarification = False

        for req in requirements:
            links = db.query(EvidenceRequirementLink).filter(
                EvidenceRequirementLink.requirement_id == req.id
            ).all()

            # Determine requirement compliance
            item_status = ComplianceStatus.NON_COMPLIANT
            item_risk = RiskLevel.CRITICAL if req.classification == "mandatory" else RiskLevel.MEDIUM
            evidence_summary = "No evidence found."
            evidence_id = None
            action_required = None

            if not links:
                item_status = ComplianceStatus.NON_COMPLIANT
                item_risk = RiskLevel.CRITICAL if req.classification == "mandatory" else RiskLevel.HIGH
                evidence_summary = "No evidence mapped."
                action_required = "Upload supporting evidence or obtain waiver before proposal finalization."
            else:
                # Inspect highest status link
                verified_links = [l for l in links if l.match_status in (ProofLinkStatus.VERIFIED, ProofLinkStatus.HUMAN_CONFIRMED)]
                contradicted_links = [l for l in links if l.match_status == ProofLinkStatus.CONTRADICTED]
                pending_links = [l for l in links if l.match_status == ProofLinkStatus.PENDING]

                if contradicted_links:
                    item_status = ComplianceStatus.NON_COMPLIANT
                    item_risk = RiskLevel.CRITICAL if req.classification == "mandatory" else RiskLevel.HIGH
                    evidence_summary = f"Contradicted by record: {contradicted_links[0].notes}"
                    evidence_id = contradicted_links[0].evidence_id
                    action_required = "Resolve contradiction or form joint venture to meet mandatory threshold."
                    has_critical_failure = True
                elif verified_links:
                    item_status = ComplianceStatus.COMPLIANT
                    item_risk = RiskLevel.LOW
                    evidence_summary = f"Verified: {verified_links[0].notes or verified_links[0].source_excerpt}"
                    evidence_id = verified_links[0].evidence_id
                    action_required = None
                elif pending_links:
                    item_status = ComplianceStatus.CLARIFICATION_REQUIRED
                    item_risk = RiskLevel.MEDIUM
                    evidence_summary = f"Pending confirmation: {pending_links[0].notes}"
                    evidence_id = pending_links[0].evidence_id
                    action_required = "Human review needed to confirm evidence suitability."
                    has_clarification = True
                else:
                    item_status = ComplianceStatus.NON_COMPLIANT
                    item_risk = RiskLevel.CRITICAL if req.classification == "mandatory" else RiskLevel.MEDIUM
                    evidence_summary = "Supporting evidence absent."
                    action_required = "Procure missing documentation."
                    if req.classification == "mandatory":
                        has_critical_failure = True

            evaluated_items.append({
                "requirement_id": req.id,
                "category": req.category,
                "classification": req.classification,
                "description": req.description,
                "source_page": req.source_page,
                "status": item_status,
                "risk_level": item_risk,
                "evidence_id": evidence_id,
                "evidence_summary": evidence_summary,
                "action_required": action_required,
            })

        # Calculate overall status and risk
        if has_critical_failure:
            overall_status = ComplianceStatus.NON_COMPLIANT
            overall_risk = RiskLevel.CRITICAL
            summary = "Tender has CRITICAL non-compliance issues in mandatory eligibility requirements that risk immediate disqualification."
        elif has_clarification:
            overall_status = ComplianceStatus.CLARIFICATION_REQUIRED
            overall_risk = RiskLevel.MEDIUM
            summary = "Tender requirements partially satisfied; pending human review or clarifications required."
        else:
            overall_status = ComplianceStatus.COMPLIANT
            overall_risk = RiskLevel.LOW
            summary = "All mandatory and technical requirements are fully compliant and supported by verified evidence."

        matrix = ComplianceMatrix(
            tender_id=tender_id,
            overall_status=overall_status,
            overall_risk_level=overall_risk,
            evaluated_by_agent=evaluator_agent,
            summary=summary,
            items=evaluated_items,
        )
        db.add(matrix)
        db.commit()
        db.refresh(matrix)
        logger.info(f"Generated compliance matrix for tender {tender_id}: {overall_status} (Risk: {overall_risk})")
        return matrix

    def get_latest_matrix(self, db: Session, tender_id: str) -> Optional[ComplianceMatrix]:
        return db.query(ComplianceMatrix).filter(
            ComplianceMatrix.tender_id == tender_id
        ).order_by(ComplianceMatrix.created_at.desc()).first()
