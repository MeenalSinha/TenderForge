"""
Unit tests for Advanced ProofLink Intelligence Service.
Tests evidence freshness tracking, cross-document contradiction detection, and claim lineage integrity.
"""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Organization,
    OrganizationProfile,
    Proposal,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.advanced_prooflink_service import AdvancedProofLinkService


@pytest.fixture
def prooflink_setup(db_session: Session):
    org = Organization(name="ProofLink Org", slug="prooflink-org")
    db_session.add(org)
    db_session.commit()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name="ProofLink Systems LLC",
        registration_number="PL-8899",
        tax_id="TX-1122",
        jurisdiction="United States",
        certifications=["ISO 9001:2015"],
    )
    db_session.add(profile)

    ws = Workspace(name="ProofLink WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="High Assurance Security Tender")
    db_session.add(tender)
    db_session.commit()

    req = TenderRequirement(
        tender_id=tender.id,
        category="eligibility",
        classification="mandatory",
        description="Must hold active ISO 9001 certification and audited accounts.",
        source_excerpt="Clause 1.1",
    )
    db_session.add(req)

    prop = Proposal(tender_id=tender.id, title="Security Bid Proposal")
    db_session.add(prop)
    db_session.commit()

    return org, tender, req, prop


def test_evidence_freshness_audit(db_session: Session, prooflink_setup):
    org, tender, req, prop = prooflink_setup
    svc = AdvancedProofLinkService(db_session)

    now = datetime.now(timezone.utc)

    # 1. Expired evidence
    ev_expired = CompanyEvidence(
        organization_id=org.id,
        title="Old ISO 9001 Certificate",
        evidence_type="certification",
        expiry_date=(now - timedelta(days=30)).replace(tzinfo=None),
        status="valid",
    )
    # 2. Expiring soon evidence (within 30 days)
    ev_soon = CompanyEvidence(
        organization_id=org.id,
        title="Current Audited Financial Statements",
        evidence_type="financial_audit",
        expiry_date=(now + timedelta(days=20)).replace(tzinfo=None),
        status="valid",
    )
    # 3. Valid long-term evidence
    ev_valid = CompanyEvidence(
        organization_id=org.id,
        title="Permanent Incorporation Certificate",
        evidence_type="statutory_registration",
        expiry_date=None,
        status="valid",
    )
    db_session.add_all([ev_expired, ev_soon, ev_valid])
    db_session.commit()

    audit = svc.audit_evidence_freshness(org.id, target_date=now, warning_window_days=60, db=db_session)

    assert audit["total_evidence_audited"] == 3
    assert audit["expired_count"] == 1
    assert audit["expiring_soon_count"] == 1
    assert audit["valid_count"] == 1
    assert ev_expired.status == "expired"


def test_cross_document_contradiction_detection(db_session: Session, prooflink_setup):
    org, tender, req, prop = prooflink_setup
    svc = AdvancedProofLinkService(db_session)

    # Two financial documents with conflicting reported turnover
    ev1 = CompanyEvidence(
        organization_id=org.id,
        title="Audited Balance Sheet FY24",
        evidence_type="financial_audit",
        extracted_data={"turnover": "$4,200,000"},
        status="valid",
    )
    ev2 = CompanyEvidence(
        organization_id=org.id,
        title="Director Annual Report FY24",
        evidence_type="annual_report",
        extracted_data={"turnover": "$3,800,000"},
        status="valid",
    )
    db_session.add_all([ev1, ev2])
    db_session.commit()

    contradictions = svc.detect_evidence_contradictions(org.id, db=db_session)

    assert len(contradictions) >= 1
    contra = next(c for c in contradictions if c.claim_field == "turnover")
    assert contra.contradiction_severity == "Critical"
    assert contra.status == "Open"
    assert "$4,200,000" in (contra.value_1, contra.value_2)
    assert "$3,800,000" in (contra.value_1, contra.value_2)

    # Resolve contradiction
    resolved = svc.resolve_contradiction(
        contradiction_id=contra.id,
        resolution_notes="Director report stated preliminary numbers; audited balance sheet represents official filing.",
        resolved_by="Chief Financial Officer",
        db=db_session,
    )
    assert resolved.status == "Resolved"
    assert resolved.resolved_by == "Chief Financial Officer"


def test_claim_lineage_and_invalidation(db_session: Session, prooflink_setup):
    org, tender, req, prop = prooflink_setup
    svc = AdvancedProofLinkService(db_session)

    ev = CompanyEvidence(
        organization_id=org.id,
        title="ISO 9001:2015 Certificate",
        evidence_type="certification",
        reference_number="CERT-9001-2024",
        status="valid",
    )
    db_session.add(ev)
    db_session.commit()

    # Record complete lineage chain
    lineage = svc.record_claim_lineage(
        tender_id=tender.id,
        proposal_id=prop.id,
        requirement_id=req.id,
        evidence_id=ev.id,
        section_number="2.1",
        claim_text="Company maintains continuous ISO 9001:2015 certification.",
        evidence_extract="Certified by Bureau Veritas on 2024-01-15.",
        review_status="verified",
        approval_status="approved",
        db=db_session,
    )

    assert lineage.lineage_hash is not None
    assert lineage.approval_status == "approved"

    # Invalidate when evidence is modified
    count = svc.invalidate_on_evidence_change(
        evidence_id=ev.id,
        reason="Certificate revoked by registrar.",
        db=db_session,
    )

    assert count == 1
    db_session.refresh(lineage)
    assert lineage.approval_status == "invalidated"
    assert lineage.review_status == "unreviewed"
