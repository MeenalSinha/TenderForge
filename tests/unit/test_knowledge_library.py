"""
Unit tests for Reusable Proposal Knowledge Library, Versioning, and Approval Workflows.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.models import (
    KnowledgeAsset,
    KnowledgeAssetVersion,
    Organization,
    Proposal,
    ProposalSection,
    Tender,
    Workspace,
)
from backend.app.services.knowledge_library_service import KnowledgeLibraryService


def test_knowledge_asset_lifecycle_and_versioning(db_session: Session):
    org = Organization(name="Knowledge Org", slug="knowledge-org")
    db_session.add(org)
    db_session.commit()

    svc = KnowledgeLibraryService()
    asset = svc.create_asset(
        db=db_session,
        organization_id=org.id,
        title="Zero Trust Security Architecture Boilerplate",
        content="Our enterprise architecture adheres to NIST SP 800-207 Zero Trust Architecture.",
        category="technical_approach",
        keywords=["zero_trust", "nist", "security"],
        author_user_id="usr-architect",
    )

    assert asset.id is not None
    assert asset.review_status == "draft"
    assert asset.times_reused == 0
    assert len(asset.versions) == 1
    assert asset.versions[0].version_number == 1

    # Update asset -> creates version 2
    updated = svc.update_asset(
        db=db_session,
        asset_id=asset.id,
        content="Our enterprise architecture adheres to NIST SP 800-207 and FedRAMP High benchmarks.",
        change_summary="Added FedRAMP High citation.",
        modified_by_user_id="usr-architect",
    )

    assert len(updated.versions) == 2
    assert updated.versions[-1].version_number == 2
    assert "FedRAMP High" in updated.content

    # Human Approver signs off on asset
    approved = svc.approve_asset(db_session, asset.id, approver_user_id="usr-compliance-lead")
    assert approved.review_status == "approved"
    assert approved.approved_by_user_id == "usr-compliance-lead"


def test_knowledge_asset_reuse_in_proposal_section(db_session: Session):
    org = Organization(name="Reuse Org", slug="reuse-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="WS-Reuse", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    tender = Tender(workspace_id=ws.id, title="IT Cloud Tender")
    db_session.add(tender)
    db_session.flush()

    proposal = Proposal(tender_id=tender.id, title="Proposal Draft v1", status="draft")
    db_session.add(proposal)
    db_session.flush()

    section = ProposalSection(
        proposal_id=proposal.id,
        section_number="2.1",
        title="Technical Methodology",
        content="Initial section draft outline.",
    )
    db_session.add(section)
    db_session.commit()

    svc = KnowledgeLibraryService()
    asset = svc.create_asset(
        db=db_session,
        organization_id=org.id,
        title="Agile Delivery Methodology",
        content="We follow a Scrum framework with two-week sprint cadences.",
        auto_approve=True,
    )

    assert asset.times_reused == 0

    # Reuse asset in proposal section
    result = svc.use_asset(db_session, asset.id, proposal_section_id=section.id)

    assert result["times_reused"] == 1
    assert result["section_updated"] is True

    db_session.refresh(section)
    assert "We follow a Scrum framework" in section.content
    assert "Initial section draft outline." in section.content

    db_session.refresh(asset)
    assert asset.times_reused == 1

