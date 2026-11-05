"""
Unit tests for Independent Bid Auditor Service.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    BidAudit,
    ComplianceMatrix,
    Organization,
    Proposal,
    ProposalSection,
    Tender,
    Workspace,
)
from backend.app.services.audit_service import AuditService, AuditSeverity, AuditVerdict
from backend.app.services.prooflink_service import ProofLinkStatus


def test_audit_proposal_with_contradicted_and_verified_claims(db_session: Session):
    service = AuditService()
    org = Organization(name="AuditTest Org", slug="audit-test")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_Audit", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Defense Communications RFP")
    db_session.add(tender)
    db_session.commit()

    proposal = Proposal(
        tender_id=tender.id,
        title="Defense Comms Response",
        current_version=1,
        status="drafting",
    )
    db_session.add(proposal)
    db_session.flush()

    # Section 1 with 1 Verified claim and 1 Contradicted claim
    s1 = ProposalSection(
        proposal_id=proposal.id,
        section_number="1.0",
        title="Executive Summary",
        content="Our organization meets all defense requirements.",
        claims=[
            {"text": "Incorporated for 10 years", "status": ProofLinkStatus.VERIFIED},
            {"text": "Annual turnover of $50M", "status": ProofLinkStatus.CONTRADICTED},
        ],
    )
    db_session.add(s1)
    db_session.commit()

    audit = service.audit_proposal(db_session, proposal.id)

    assert audit.proposal_id == proposal.id
    assert audit.total_claims == 2
    assert audit.verified_claims == 1
    assert audit.contradicted_claims == 1

    # Because a critical finding exists, verdict must be SUBMISSION_BLOCKED
    assert audit.verdict == AuditVerdict.SUBMISSION_BLOCKED
    assert audit.readiness_score < 75.0

    critical_findings = [f for f in audit.findings if f["severity"] == AuditSeverity.CRITICAL]
    assert len(critical_findings) >= 1
    assert "contradicted" in critical_findings[0]["description"].lower()


def test_audit_proposal_all_verified(db_session: Session):
    service = AuditService()
    org = Organization(name="Clean Org", slug="clean-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_Clean", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Municipal Fiber RFP")
    db_session.add(tender)
    db_session.commit()

    proposal = Proposal(
        tender_id=tender.id,
        title="Municipal Fiber Bid",
        current_version=1,
        status="drafting",
    )
    db_session.add(proposal)
    db_session.flush()

    s1 = ProposalSection(
        proposal_id=proposal.id,
        section_number="1.0",
        title="Solution Overview",
        content="Delivering verified gigabit fiber architecture.",
        claims=[
            {"text": "Certified ISO 9001", "status": ProofLinkStatus.VERIFIED},
            {"text": "Audited turnover $5M", "status": ProofLinkStatus.VERIFIED},
            {"text": "Delivered 12 municipal networks", "status": ProofLinkStatus.HUMAN_CONFIRMED},
        ],
    )
    db_session.add(s1)
    db_session.commit()

    audit = service.audit_proposal(db_session, proposal.id)

    assert audit.total_claims == 3
    assert audit.verified_claims == 3
    assert audit.readiness_score >= 90.0
    assert audit.verdict == AuditVerdict.READY_FOR_SUBMISSION
