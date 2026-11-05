"""
Unit tests for ProofLink Evidence Matching Engine.
"""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Organization,
    OrganizationProfile,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.prooflink_service import ProofLinkService, ProofLinkStatus


def test_prooflink_turnover_matching(db_session: Session):
    service = ProofLinkService()
    org = Organization(name="OmniCorp Global", slug="omnicorp")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS1", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Telecom Upgrade RFP")
    db_session.add(tender)
    db_session.commit()

    # Case A: Requirement for $2,000,000, evidence has $3,500,000 -> VERIFIED
    ev_verified = CompanyEvidence(
        organization_id=org.id,
        evidence_type="financial_audit",
        title="FY25 Audited Financial Statement",
        status="valid",
        extracted_data={"average_turnover": 3500000},
        summary="Annual turnover audited at USD 3,500,000.",
    )
    db_session.add(ev_verified)
    db_session.commit()

    req_pass = TenderRequirement(
        tender_id=tender.id,
        category="financial",
        classification="mandatory",
        description="Minimum annual turnover of USD 2,000,000 required over the last 3 fiscal years.",
        source_excerpt="Minimum annual turnover of USD 2,000,000 required.",
    )
    db_session.add(req_pass)
    db_session.commit()

    links = service.match_requirement_to_evidence(db_session, req_pass, org.id)
    assert len(links) >= 1
    assert links[0].match_status == ProofLinkStatus.VERIFIED
    assert "meets or exceeds" in links[0].notes

    # Case B: Requirement for $5,000,000, evidence has only $3,500,000 -> CONTRADICTED
    req_fail = TenderRequirement(
        tender_id=tender.id,
        category="financial",
        classification="mandatory",
        description="Minimum annual turnover of USD 5,000,000 required.",
        source_excerpt="Minimum annual turnover of USD 5,000,000 required.",
    )
    db_session.add(req_fail)
    db_session.commit()

    links_fail = service.match_requirement_to_evidence(db_session, req_fail, org.id)
    assert len(links_fail) >= 1
    assert links_fail[0].match_status == ProofLinkStatus.CONTRADICTED
    assert "below mandatory threshold" in links_fail[0].notes


def test_prooflink_iso_certification_expiration(db_session: Session):
    service = ProofLinkService()
    org = Organization(name="CertCorp", slug="certcorp")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS2", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Gov Procurement")
    db_session.add(tender)
    db_session.commit()

    req_iso = TenderRequirement(
        tender_id=tender.id,
        category="eligibility",
        classification="mandatory",
        description="Bidder must possess valid ISO 9001 quality management certification.",
        source_excerpt="Valid ISO 9001 certification is mandatory.",
    )
    db_session.add(req_iso)
    db_session.commit()

    # Expired ISO certificate -> CONTRADICTED
    ev_expired = CompanyEvidence(
        organization_id=org.id,
        evidence_type="certification",
        title="ISO 9001:2015 Certificate",
        issuer="Lloyds Register",
        expiry_date=datetime.now(timezone.utc) - timedelta(days=60),  # expired 2 months ago
        status="expired",
        summary="ISO 9001 expired certificate.",
        tags=["iso 9001"],
    )
    db_session.add(ev_expired)
    db_session.commit()

    links = service.match_requirement_to_evidence(db_session, req_iso, org.id)
    assert len(links) >= 1
    assert links[0].match_status == ProofLinkStatus.CONTRADICTED
    assert "expired" in links[0].notes.lower()


def test_prooflink_human_confirmation(db_session: Session):
    service = ProofLinkService()
    org = Organization(name="ConfirmOrg", slug="confirmorg")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS3", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="IT Procurement")
    db_session.add(tender)
    db_session.commit()

    req = TenderRequirement(
        tender_id=tender.id,
        category="technical",
        classification="mandatory",
        description="Must provide dedicated 24x7 support desk with 15-minute response SLA.",
        source_excerpt="24x7 support desk SLA required.",
    )
    db_session.add(req)
    db_session.commit()

    ev = CompanyEvidence(
        organization_id=org.id,
        evidence_type="policy",
        title="Corporate SLA and Support Desk Operations Manual",
        status="valid",
        summary="Document outlining support desk shift roster and SLA commitments.",
    )
    db_session.add(ev)
    db_session.commit()

    links = service.match_requirement_to_evidence(db_session, req, org.id)
    assert len(links) >= 1
    link = links[0]

    # Human lead confirms the link
    confirmed = service.confirm_evidence_link(
        db=db_session,
        link_id=link.id,
        user_id="lead_reviewer_1",
        status=ProofLinkStatus.HUMAN_CONFIRMED,
        notes="Reviewed shift schedule, satisfies 15-min SLA.",
    )

    assert confirmed.match_status == ProofLinkStatus.HUMAN_CONFIRMED
    assert confirmed.verified_by_user_id == "lead_reviewer_1"
    assert "Reviewed shift schedule" in confirmed.notes
