"""
Unit tests for Bid/No-Bid Decision Intelligence Engine.
Tests multi-dimensional evaluation, non-compensable eligibility gates, and human decision tracking.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    BidEvaluation,
    ComplianceMatrix,
    Organization,
    OrganizationProfile,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.bid_decision_service import BidDecisionService


@pytest.fixture
def sample_tender_for_bid(db_session: Session):
    org = Organization(name="GovCorp Solutions", slug="govcorp-sol")
    db_session.add(org)
    db_session.commit()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name="GovCorp Solutions Inc.",
        registration_number="REG-998877",
        tax_id="TAX-445566",
        jurisdiction="United States",
        financial_metrics={"turnover_fy24": 5000000},
        certifications=["ISO 9001:2015", "ISO 27001"],
    )
    db_session.add(profile)

    ws = Workspace(name="Gov Bid WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(
        workspace_id=ws.id,
        title="Federal IT Modernization Tender",
        reference_number="FED-IT-2026",
        estimated_value=1200000.0,
        currency="USD",
    )
    db_session.add(tender)
    db_session.commit()

    # Add requirements
    r1 = TenderRequirement(
        tender_id=tender.id,
        category="eligibility",
        classification="mandatory",
        description="Vendor must hold active ISO 9001:2015 certification.",
        source_excerpt="Clause 3.1: ISO 9001 mandatory",
    )
    r2 = TenderRequirement(
        tender_id=tender.id,
        category="technical",
        classification="mandatory",
        description="Cloud microservices architecture with 99.95% uptime.",
        source_excerpt="Clause 4.2: Uptime SLA",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    return tender, org


def test_bid_decision_full_pass(db_session: Session, sample_tender_for_bid):
    tender, org = sample_tender_for_bid
    svc = BidDecisionService(db_session)

    # Compliance matrix all compliant
    matrix = ComplianceMatrix(
        tender_id=tender.id,
        overall_status="Compliant",
        overall_risk_level="Low",
        summary="All mandatory clauses verified.",
        items=[
            {"requirement_id": "req-1", "category": "eligibility", "status": "Compliant", "description": "ISO 9001 certified"},
            {"requirement_id": "req-2", "category": "technical", "status": "Compliant", "description": "Cloud architecture"},
        ],
    )
    db_session.add(matrix)
    db_session.commit()

    eval_result = svc.evaluate_tender(tender_id=tender.id, db=db_session)

    assert eval_result.overall_score >= 75.0
    assert eval_result.eligibility_gates_passed is True
    assert len(eval_result.failed_gates) == 0
    assert eval_result.recommendation == "BID"
    assert "BID/NO-BID ADVISORY RECOMMENDATION: BID" in eval_result.executive_summary
    assert eval_result.human_decision == "PENDING"


def test_bid_decision_non_compensable_gate_failure(db_session: Session, sample_tender_for_bid):
    """Critical rule: Non-compensable gates must strictly override recommendation even if other dimensions score 100."""
    tender, org = sample_tender_for_bid
    svc = BidDecisionService(db_session)

    # Compliance matrix contains a failed mandatory eligibility gate
    matrix = ComplianceMatrix(
        tender_id=tender.id,
        overall_status="Non-Compliant",
        overall_risk_level="High",
        summary="Failed mandatory turnover criteria.",
        items=[
            {"requirement_id": "req-gate", "category": "eligibility", "status": "Non-Compliant", "description": "Minimum turnover $10M mandatory."},
        ],
    )
    db_session.add(matrix)
    db_session.commit()

    # Even with 100% on other dimensions, gate failure must enforce NO-BID RECOMMENDED
    eval_result = svc.evaluate_tender(
        tender_id=tender.id,
        db=db_session,
        custom_dimension_overrides={
            "technical_capability": 100.0,
            "past_performance": 100.0,
            "financial_capacity": 100.0,
            "resource_availability": 100.0,
            "timeline_feasibility": 100.0,
            "strategic_alignment": 100.0,
        },
    )

    assert eval_result.eligibility_gates_passed is False
    assert len(eval_result.failed_gates) > 0
    assert eval_result.recommendation == "NO-BID RECOMMENDED"
    assert any("Cannot be compensated" in c for c in eval_result.conditions)


def test_bid_decision_human_override_tracking(db_session: Session, sample_tender_for_bid):
    tender, org = sample_tender_for_bid
    svc = BidDecisionService(db_session)

    eval_record = svc.evaluate_tender(tender_id=tender.id, db=db_session)

    # Human Executive approves bid with formal rationale
    updated = svc.record_human_decision(
        evaluation_id=eval_record.id,
        decision="APPROVED_BID",
        user_id="usr-exec-01",
        user_name="Sarah Jenkins",
        rationale="Executive committee reviewed margin profile and authorized pursuit.",
        db=db_session,
    )

    assert updated.human_decision == "APPROVED_BID"
    assert "Sarah Jenkins" in updated.human_decision_by
    assert updated.human_decision_at is not None

    # Test rejection of trivial rationale
    with pytest.raises(ValueError, match="substantive decision rationale"):
        svc.record_human_decision(
            evaluation_id=eval_record.id,
            decision="APPROVED_BID",
            user_id="usr-02",
            user_name="John",
            rationale="ok",
            db=db_session,
        )
