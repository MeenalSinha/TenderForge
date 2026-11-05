"""
Unit tests for Human-in-the-Loop Governance & Digital Approval Service.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    HumanApproval,
    Organization,
    Proposal,
    Tender,
    Workspace,
)
from backend.app.services.approval_service import ApprovalDecision, ApprovalService


def test_human_approval_lifecycle_and_signature_hash(db_session: Session):
    service = ApprovalService()
    org = Organization(name="GovCorp", slug="govcorp")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_Gov", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="National Grid Proposal")
    db_session.add(tender)
    db_session.commit()

    proposal = Proposal(
        tender_id=tender.id,
        title="National Grid Bid",
        current_version=1,
        status="pending_human_review",
    )
    db_session.add(proposal)
    db_session.commit()

    # Verify not approved yet
    assert not service.is_proposal_approved_by_human(db_session, proposal.id)

    # Record Human Decision: Approved
    approval = service.record_decision(
        db=db_session,
        tender_id=tender.id,
        proposal_id=proposal.id,
        user_id="dir_sarah_connor",
        user_name="Sarah Connor",
        user_role="Bid Director & Authorized Signatory",
        decision=ApprovalDecision.APPROVED,
        comments="Fully audited and verified against technical tender specs. Authorized for formal submission.",
    )

    assert approval.decision == ApprovalDecision.APPROVED
    assert approval.user_name == "Sarah Connor"
    assert len(approval.signature_hash) == 64  # SHA-256 length

    # Proposal and tender status should be updated
    db_session.refresh(proposal)
    db_session.refresh(tender)
    assert proposal.status == "approved"
    assert tender.status == "approved"

    # Verify helper method
    assert service.is_proposal_approved_by_human(db_session, proposal.id)


def test_human_approval_requires_substantive_comments(db_session: Session):
    service = ApprovalService()
    org = Organization(name="TestCorp", slug="testcorp")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_Test", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="RFP Test")
    db_session.add(tender)
    db_session.commit()

    # Reject empty or trivial comments
    with pytest.raises(ValueError, match="Substantive comments"):
        service.record_decision(
            db=db_session,
            tender_id=tender.id,
            user_id="user1",
            user_name="User",
            user_role="Lead",
            decision=ApprovalDecision.APPROVED,
            comments="ok",
        )
