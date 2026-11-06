"""
Unit tests for Bid Lifecycle Stages, Cryptographic Submission Receipts, and Closed-Loop Learning Engine.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.models import (
    BidSubmissionRecord,
    BidOutcomeRecord,
    Organization,
    Tender,
    Workspace,
)
from backend.app.services.bid_outcome_service import BidOutcomeService


def test_submission_receipt_generation_and_verification(db_session: Session):
    org = Organization(name="Receipt Org", slug="receipt-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="WS", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    tender = Tender(workspace_id=ws.id, title="High-Speed Rail Phase 2", reference_number="HSR-02")
    db_session.add(tender)
    db_session.commit()

    svc = BidOutcomeService()
    sub = svc.record_bid_submission(
        db=db_session,
        tender_id=tender.id,
        organization_id=org.id,
        final_bid_amount=14500000.0,
        currency="USD",
        submitted_by_user_id="usr-approver",
        submission_reference="SUB-2026-HSR-01",
        notes="Final executive signoff granted.",
    )

    assert sub.submission_receipt_hash is not None
    assert len(sub.submission_receipt_hash) == 64  # SHA-256 length
    assert sub.lifecycle_stage == "submitted_to_buyer"

    # Tender status should advance
    db_session.refresh(tender)
    assert tender.status == "submitted"


def test_minimum_sample_threshold_enforcement(db_session: Session):
    """When sample size N < 5, engine must enforce threshold and report projection notice."""
    org = Organization(name="Learning Org", slug="learning-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="WS-Learn", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    svc = BidOutcomeService()

    # Record only 2 outcomes (below N=5 threshold)
    for i in range(2):
        tender = Tender(workspace_id=ws.id, title=f"Tender {i}", reference_number=f"TND-{i}")
        db_session.add(tender)
        db_session.flush()

        sub = svc.record_bid_submission(
            db=db_session,
            tender_id=tender.id,
            organization_id=org.id,
            final_bid_amount=1000000.0,
        )
        svc.record_bid_outcome(
            db=db_session,
            submission_id=sub.id,
            outcome="lost" if i == 0 else "won",
            primary_loss_reason="pricing_uncompetitive" if i == 0 else None,
            win_factors=["technical_score_highest"] if i == 1 else [],
        )

    analytics = svc.get_closed_loop_learning(db_session, org.id)
    assert analytics["total_recorded_outcomes"] == 2
    assert analytics["min_sample_threshold"] == 5
    assert analytics["meets_statistical_threshold"] is False
    assert "Insufficient sample size" in analytics["projection_notice"]


def test_closed_loop_learning_with_sufficient_sample(db_session: Session):
    """When N >= 5, closed-loop engine calculates statistical loss reason clusters and win attributions."""
    org = Organization(name="Big Data Org", slug="big-data-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="WS-BigData", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    svc = BidOutcomeService()

    # Record 6 outcomes (3 won, 3 lost)
    for i in range(6):
        tender = Tender(workspace_id=ws.id, title=f"Tender Big {i}", reference_number=f"TB-{i}")
        db_session.add(tender)
        db_session.flush()

        sub = svc.record_bid_submission(
            db=db_session,
            tender_id=tender.id,
            organization_id=org.id,
            final_bid_amount=2000000.0,
        )
        outcome_val = "won" if i % 2 == 0 else "lost"
        svc.record_bid_outcome(
            db=db_session,
            submission_id=sub.id,
            outcome=outcome_val,
            primary_loss_reason="pricing_uncompetitive" if outcome_val == "lost" else None,
            win_factors=["strong_past_performance", "low_risk_rating"] if outcome_val == "won" else [],
        )

    analytics = svc.get_closed_loop_learning(db_session, org.id)
    assert analytics["total_recorded_outcomes"] == 6
    assert analytics["meets_statistical_threshold"] is True
    assert analytics["win_rate_percentage"] == 50.0
    assert analytics["counts"]["won"] == 3
    assert analytics["counts"]["lost"] == 3
    assert len(analytics["top_loss_reasons"]) > 0
    assert analytics["top_loss_reasons"][0]["reason"] == "pricing_uncompetitive"
    assert len(analytics["top_win_factors"]) > 0

