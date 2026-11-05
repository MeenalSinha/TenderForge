"""
Independent Bid Auditor Service for TenderForge.
Performs adversarial, objective reviews of proposal drafts against original tender requirements and evidence.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    BidAudit,
    ComplianceMatrix,
    Proposal,
    ProposalSection,
    Tender,
    TenderRequirement,
)
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.prooflink_service import ProofLinkStatus

logger = get_logger("audit_service")


class AuditSeverity:
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    ADVISORY = "Advisory"


class AuditVerdict:
    READY_FOR_SUBMISSION = "Ready for Submission"
    CONDITIONAL_APPROVAL = "Conditional Approval Required"
    SUBMISSION_BLOCKED = "Submission Blocked - High Risk"


class AuditService:
    """Independent auditor evaluating proposal veracity, completeness, and submission readiness."""

    def __init__(self, compliance_service: Optional[ComplianceService] = None):
        self.compliance_service = compliance_service or ComplianceService()

    def audit_proposal(
        self,
        db: Session,
        proposal_id: str,
        auditor_id: str = "BidAuditor",
    ) -> BidAudit:
        """Conduct an independent audit on a proposal draft."""
        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise EntityNotFoundError(f"Proposal '{proposal_id}' not found.")

        tender = db.query(Tender).filter(Tender.id == proposal.tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender for proposal '{proposal_id}' not found.")

        sections = db.query(ProposalSection).filter(
            ProposalSection.proposal_id == proposal_id
        ).all()

        matrix = self.compliance_service.get_latest_matrix(db, tender.id)

        # Audit variables
        findings: List[Dict[str, Any]] = []
        total_claims = 0
        verified_claims = 0
        unsupported_claims = 0
        contradicted_claims = 0

        # 1. Audit Section Claims & ProofLink Grounding
        for sec in sections:
            if not sec.claims:
                continue

            for claim in sec.claims:
                total_claims += 1
                status = claim.get("status")
                text = claim.get("text", "")

                if status in (ProofLinkStatus.VERIFIED, ProofLinkStatus.HUMAN_CONFIRMED):
                    verified_claims += 1
                elif status == ProofLinkStatus.CONTRADICTED:
                    contradicted_claims += 1
                    findings.append({
                        "severity": AuditSeverity.CRITICAL,
                        "category": "Factual Veracity",
                        "section": sec.title,
                        "claim_text": text,
                        "description": "Claim contradicted by official repository records. High risk of bid disqualification.",
                        "recommendation": "Correct assertion or remove contradicted claim immediately.",
                    })
                elif status == ProofLinkStatus.UNSUPPORTED:
                    unsupported_claims += 1
                    findings.append({
                        "severity": AuditSeverity.CRITICAL,
                        "category": "Missing Proof",
                        "section": sec.title,
                        "claim_text": text,
                        "description": "Factual assertion lacks supporting documentary evidence in the repository.",
                        "recommendation": "Upload certified completion proof or obtain human sign-off.",
                    })
                elif status == ProofLinkStatus.PENDING:
                    findings.append({
                        "severity": AuditSeverity.MAJOR,
                        "category": "Unconfirmed Candidate",
                        "section": sec.title,
                        "claim_text": text,
                        "description": "Claim relies on unverified candidate evidence.",
                        "recommendation": "Human reviewer must verify and approve this proof link.",
                    })

            # Check for unfulfilled action items in text
            if "[ACTION REQUIRED" in sec.content:
                findings.append({
                    "severity": AuditSeverity.MAJOR,
                    "category": "Incomplete Section",
                    "section": sec.title,
                    "claim_text": "Section contains unresolved action placeholders.",
                    "description": "Draft contains unresolved '[ACTION REQUIRED]' markers.",
                    "recommendation": "Address all missing evidence gaps before final submission.",
                })

        # 2. Audit Mandatory Requirements Coverage
        requirements = db.query(TenderRequirement).filter(
            TenderRequirement.tender_id == tender.id
        ).all()
        mandatory_reqs = [r for r in requirements if r.classification == "mandatory"]

        if matrix:
            for item in matrix.items:
                if item.get("classification") == "mandatory" and item.get("status") == "Non-Compliant":
                    findings.append({
                        "severity": AuditSeverity.CRITICAL,
                        "category": "Mandatory Disqualification Risk",
                        "section": "Compliance Matrix",
                        "claim_text": item.get("description", "")[:100],
                        "description": f"Mandatory requirement non-compliant: {item.get('evidence_summary')}",
                        "recommendation": item.get("action_required") or "Resolve non-compliance before bid release.",
                    })

        # 3. Calculate Readiness Score (0.0 to 100.0)
        base_score = 100.0
        if total_claims > 0:
            claim_ratio = (verified_claims / total_claims) * 100.0
            base_score = claim_ratio

        # Deduct penalties
        critical_count = sum(1 for f in findings if f["severity"] == AuditSeverity.CRITICAL)
        major_count = sum(1 for f in findings if f["severity"] == AuditSeverity.MAJOR)
        minor_count = sum(1 for f in findings if f["severity"] == AuditSeverity.MINOR)

        score = base_score - (critical_count * 25.0) - (major_count * 10.0) - (minor_count * 3.0)
        readiness_score = max(0.0, min(100.0, round(score, 1)))

        # 4. Formulate Readiness Verdict
        if critical_count > 0 or readiness_score < 75.0:
            verdict = AuditVerdict.SUBMISSION_BLOCKED
        elif major_count > 0 or readiness_score < 90.0:
            verdict = AuditVerdict.CONDITIONAL_APPROVAL
        else:
            verdict = AuditVerdict.READY_FOR_SUBMISSION

        # Persist audit
        audit = BidAudit(
            proposal_id=proposal_id,
            tender_id=tender.id,
            auditor_type="agent",
            auditor_id=auditor_id,
            readiness_score=readiness_score,
            verdict=verdict,
            total_claims=total_claims,
            verified_claims=verified_claims,
            unsupported_claims=unsupported_claims,
            contradicted_claims=contradicted_claims,
            findings=findings,
        )
        db.add(audit)
        
        # Update proposal status to 'auditing' or 'pending_human_review'
        proposal.status = "pending_human_review" if verdict != AuditVerdict.SUBMISSION_BLOCKED else "auditing"
        
        db.commit()
        db.refresh(audit)
        logger.info(f"Completed bid audit for proposal {proposal_id}: Verdict='{verdict}', Score={readiness_score}%, Findings={len(findings)}")
        return audit

    def get_audit(self, db: Session, audit_id: str) -> Optional[BidAudit]:
        return db.query(BidAudit).filter(BidAudit.id == audit_id).first()

    def get_latest_audit(self, db: Session, proposal_id: str) -> Optional[BidAudit]:
        return db.query(BidAudit).filter(
            BidAudit.proposal_id == proposal_id
        ).order_by(BidAudit.created_at.desc()).first()
