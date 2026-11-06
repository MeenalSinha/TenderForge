"""
Unit tests for 9-Dimension Opportunity Matching and Hard Eligibility Gates.
"""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Organization,
    OrganizationProfile,
    SourceOpportunity,
)
from backend.app.services.opportunity_matching_service import OpportunityMatchingService


def test_opportunity_matching_with_passed_gates(db_session: Session):
    org = Organization(name="Prime Defense Tech", slug="prime-def-tech")
    db_session.add(org)
    db_session.flush()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name=org.name,
        registration_number="REG-PRIME-01",
        tax_id="TAX-PRIME-01",
        financial_metrics={"annual_turnover": 25000000.0, "turnover": 25000000.0},
        core_capabilities=["cloud", "kubernetes", "cybersecurity"],
        certifications=["ISO 27001", "SOC2 Type II"],
    )
    db_session.add(profile)

    ev = CompanyEvidence(
        organization_id=org.id,
        title="ISO 27001 Security Audit",
        evidence_type="certification",
        issuer="BSI",
        tags=["iso_27001", "security"],
    )
    db_session.add(ev)

    opp = SourceOpportunity(
        source_id="src-01",
        organization_id=org.id,
        external_id="TND-CLOUD-1",
        title="Enterprise Cloud Migration",
        buyer_name="Federal Reserve Bank",
        procurement_category="information_technology",
        estimated_budget=5000000.0,
        currency="USD",
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=30),
        status="open",
        raw_payload={"mandatory_gates": ["iso_27001"]},
        deduplication_hash="hash-123",
    )
    db_session.add(opp)
    db_session.commit()

    svc = OpportunityMatchingService()
    match = svc.evaluate_opportunity(db_session, opp.id, org.id)

    assert match.overall_match_score >= 70.0
    assert match.mandatory_gates_passed is True
    assert match.recommendation_tier in ("STRONGLY RECOMMENDED", "RECOMMENDED WITH CONDITIONS")
    assert "mandatory_eligibility" in match.dimension_scores
    assert match.dimension_scores["mandatory_eligibility"] == 100.0
    assert len(match.explainability_breakdown["strengths"]) > 0


def test_non_compensable_gate_failure_overrides_score(db_session: Session):
    """Verify that failing a non-compensable mandatory gate strictly caps score and rejects."""
    org = Organization(name="Small Software Shop", slug="small-soft-shop")
    db_session.add(org)
    db_session.flush()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name=org.name,
        registration_number="REG-SMALL-01",
        tax_id="TAX-SMALL-01",
        financial_metrics={"annual_turnover": 500000.0, "turnover": 500000.0},
        core_capabilities=["web"],
        certifications=[],  # Missing Top Secret clearance
    )
    db_session.add(profile)

    opp = SourceOpportunity(
        source_id="src-02",
        organization_id=org.id,
        external_id="TND-DEF-99",
        title="Top Secret Sovereign Defense Cloud",
        buyer_name="Cyber Command",
        procurement_category="defense",
        estimated_budget=8000000.0,
        currency="USD",
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=20),
        status="open",
        raw_payload={"mandatory_gates": ["top_secret_fcl"]},
        deduplication_hash="hash-456",
    )
    db_session.add(opp)
    db_session.commit()

    svc = OpportunityMatchingService()
    match = svc.evaluate_opportunity(db_session, opp.id, org.id)

    # Gate failure must force score <= 48.0 and tier to PURSUIT NOT RECOMMENDED
    assert match.mandatory_gates_passed is False
    assert match.overall_match_score <= 48.0
    assert match.recommendation_tier == "PURSUIT NOT RECOMMENDED"
    assert len(match.explainability_breakdown["gate_failures"]) > 0
    assert "Missing mandatory qualification requirement: 'top_secret_fcl'." in match.explainability_breakdown["gate_failures"]
