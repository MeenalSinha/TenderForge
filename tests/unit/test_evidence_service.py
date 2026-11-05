"""
Unit tests for Organization Profile & Evidence Repository Service.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import Organization
from backend.app.services.evidence_service import EvidenceService


def test_organization_profile_lifecycle(db_session: Session):
    service = EvidenceService()
    org = Organization(name="Quantum Dynamics Inc", slug="quantum-dynamics")
    db_session.add(org)
    db_session.commit()

    # Create profile
    profile = service.get_or_create_profile(
        db=db_session,
        organization_id=org.id,
        profile_data={
            "registration_number": "REG-2024-9988",
            "tax_id": "TAX-99-8877",
            "financial_metrics": {"turnover_fy24": 5000000, "turnover_fy25": 6200000},
            "certifications": ["ISO 9001:2015", "ISO 27001"],
            "core_capabilities": ["Cloud Computing", "AI Systems", "Cybersecurity"],
        },
    )

    assert profile.organization_id == org.id
    assert profile.registration_number == "REG-2024-9988"
    assert profile.financial_metrics["turnover_fy25"] == 6200000
    assert "ISO 9001:2015" in profile.certifications

    # Update profile
    updated = service.get_or_create_profile(
        db=db_session,
        organization_id=org.id,
        profile_data={"headquarters_address": "100 Tech Blvd, Silicon Valley, CA"},
    )
    assert updated.headquarters_address == "100 Tech Blvd, Silicon Valley, CA"


def test_company_evidence_registration_and_search(db_session: Session):
    service = EvidenceService()
    org = Organization(name="Apex Systems Ltd", slug="apex-systems")
    db_session.add(org)
    db_session.commit()

    # Register multiple pieces of evidence
    ev1 = service.register_evidence(
        db=db_session,
        organization_id=org.id,
        title="ISO 9001:2015 Quality Management Certificate",
        evidence_type="certification",
        issuer="Bureau Veritas",
        reference_number="CERT-ISO-9001",
        status="valid",
        summary="Official ISO 9001 quality management system certification valid through 2027.",
        tags=["iso", "quality", "iso 9001"],
    )

    ev2 = service.register_evidence(
        db=db_session,
        organization_id=org.id,
        title="Audited Financial Statements FY 2024-2025",
        evidence_type="financial_audit",
        issuer="Deloitte & Touche",
        reference_number="AUD-2025-01",
        status="valid",
        summary="Independent audit report confirming annual revenue of USD 4,500,000.",
        extracted_data={"average_turnover": 4500000, "net_profit_margin": 0.18},
        tags=["financial", "audit", "turnover"],
    )

    # Search by keyword
    results_iso = service.search_evidence(db=db_session, organization_id=org.id, query="iso 9001")
    assert len(results_iso) == 1
    assert results_iso[0].id == ev1.id

    # Search by type
    results_fin = service.search_evidence(db=db_session, organization_id=org.id, evidence_type="financial_audit")
    assert len(results_fin) == 1
    assert results_fin[0].reference_number == "AUD-2025-01"

    # Search by general query
    results_all = service.search_evidence(db=db_session, organization_id=org.id)
    assert len(results_all) == 2
