"""
Unit tests for Amendment Intelligence, Materiality Classification, and Downstream Impact Propagation.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.models import (
    ComplianceMatrix,
    HumanApproval,
    Organization,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.amendment_service import AmendmentService


def test_materiality_classifier():
    svc = AmendmentService()
    # Critical triggers
    assert svc.classify_materiality([], deadline_changed=True) == "critical"
    assert svc.classify_materiality([], budget_changed=True) == "critical"
    assert svc.classify_materiality([], eligibility_changed=True) == "critical"

    # Major triggers
    assert svc.classify_materiality(["Revision to penalty liquidated damages clause"]) == "major"
    assert svc.classify_materiality(["Updated technical scope specification"]) == "major"

    # Minor triggers
    assert svc.classify_materiality(["Corrected spelling in section 4.1"]) == "minor"


def test_downstream_impact_and_approval_invalidation(db_session: Session):
    org = Organization(name="Audit Target Org", slug="audit-target-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="Test WS", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    tender = Tender(
        workspace_id=ws.id,
        title="Rail System Signaling Upgrade",
        reference_number="RAIL-2026-001",
        status="approved",
    )
    db_session.add(tender)
    db_session.flush()

    req = TenderRequirement(
        tender_id=tender.id,
        category="technical",
        classification="mandatory",
        description="Delivery Milestones: Phase 1 delivery required within 120 days.",
        source_excerpt="Delivery Milestones: Phase 1 delivery required within 120 days.",
    )
    db_session.add(req)

    comp = ComplianceMatrix(
        tender_id=tender.id,
        overall_status="Compliant",
        overall_risk_level="Low",
        summary="Baseline technical and financial compliance verified.",
        items=[],
    )
    db_session.add(comp)

    approval = HumanApproval(
        tender_id=tender.id,
        decision="Approved",
        user_id="usr-exec",
        user_name="VP Procurement",
        user_role="Approver",
        comments="Executive sign-off granted.",
        signature_hash="sha-sign-999",
    )
    db_session.add(approval)
    db_session.commit()

    svc = AmendmentService()
    amd = svc.record_amendment(
        db=db_session,
        tender_id=tender.id,
        amendment_number="CORR-01",
        title="Addendum 1 - Delivery Schedule Shortened",
        diff_summary="Deadline moved earlier by 30 days.",
        affected_clauses=[{"keyword": "Milestones", "description": "Delivery shortened to 90 days"}],
        deadline_changed=True,
    )

    assert amd.materiality == "critical"
    assert amd.approval_invalidated is True

    # Check that compliance matrix was flagged
    db_session.refresh(comp)
    assert comp.overall_status == "Clarification Required"

    # Check that executive approval was invalidated to 'Changes Requested'
    db_session.refresh(approval)
    assert approval.decision == "Changes Requested"
    assert "invalidated due to Critical Corrigendum" in approval.comments


def test_acknowledge_amendment(db_session: Session):
    org = Organization(name="Ack Org", slug="ack-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="Ack WS", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    tender = Tender(workspace_id=ws.id, title="Smart Metering Tender", reference_number="MTR-01")
    db_session.add(tender)
    db_session.flush()

    svc = AmendmentService()
    amd = svc.record_amendment(
        db=db_session,
        tender_id=tender.id,
        amendment_number="CORR-02",
        title="Clarification on Meter Hardware",
        diff_summary="Minor specification clarification.",
        affected_clauses=[],
    )

    assert amd.acknowledged_at is None

    acked = svc.acknowledge_amendment(
        db=db_session,
        amendment_id=amd.id,
        user_id="usr-engineer-1",
        notes="Reviewed and confirmed compatible.",
    )
    assert acked.acknowledged_at is not None
    assert acked.acknowledged_by_user_id == "usr-engineer-1"
    assert acked.downstream_impact["acknowledgement_notes"] == "Reviewed and confirmed compatible."

