"""
Unit tests for Evidence-Backed Proposal Architect Service.
"""

import os
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    EvidenceRequirementLink,
    Organization,
    OrganizationProfile,
    Proposal,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.prooflink_service import ProofLinkStatus
from backend.app.services.proposal_service import ProposalService


def test_proposal_drafting_and_docx_generation(db_session: Session):
    service = ProposalService()
    org = Organization(name="Veritas Solutions", slug="veritas-sol")
    db_session.add(org)
    db_session.commit()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name="Veritas Solutions LLC",
        registration_number="REG-778899",
        tax_id="TAX-112233",
        financial_metrics={"turnover_fy24": 4200000},
    )
    db_session.add(profile)

    ws = Workspace(name="WS_Prop", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Smart City IoT Network", reference_number="RFP-IOT-2026")
    db_session.add(tender)
    db_session.commit()

    req = TenderRequirement(
        tender_id=tender.id,
        category="technical",
        classification="mandatory",
        description="Provide 99.99% high-availability core network switches.",
        source_excerpt="Core switches with 99.99% uptime SLA.",
    )
    db_session.add(req)
    db_session.commit()

    ev = CompanyEvidence(
        organization_id=org.id,
        evidence_type="certification",
        title="ISO 9001:2015 Quality Certificate",
        issuer="BSI Global",
        status="valid",
    )
    db_session.add(ev)
    db_session.commit()

    # Create proposal draft
    proposal = service.create_proposal_draft(db_session, tender.id, title="Smart City IoT Bid")

    assert proposal.title == "Smart City IoT Bid"
    assert proposal.current_version == 1
    assert proposal.status == "drafting"
    assert len(proposal.sections) == 5

    # Check that DOCX file was generated and exists on disk
    assert proposal.docx_file_path is not None
    assert os.path.exists(proposal.docx_file_path)

    # Check zero fabrication rule: missing past projects should trigger ACTION REQUIRED
    past_sec = next(s for s in proposal.sections if s.section_number == "3.0")
    assert "[ACTION REQUIRED" in past_sec.content
