"""
Unit tests for Compliance Assessment Engine.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    EvidenceRequirementLink,
    Organization,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.compliance_service import ComplianceService, ComplianceStatus, RiskLevel
from backend.app.services.prooflink_service import ProofLinkStatus


def test_compliance_matrix_evaluation(db_session: Session):
    service = ComplianceService()
    org = Organization(name="GovSupply Co", slug="govsupply")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_Comp", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="National Cloud Project")
    db_session.add(tender)
    db_session.commit()

    # Requirement 1: Compliant
    r1 = TenderRequirement(
        tender_id=tender.id,
        category="eligibility",
        classification="mandatory",
        description="Must be ISO 27001 certified.",
        source_excerpt="ISO 27001 certification required.",
    )
    # Requirement 2: Non-compliant (contradicted)
    r2 = TenderRequirement(
        tender_id=tender.id,
        category="financial",
        classification="mandatory",
        description="Minimum annual turnover USD 10,000,000.",
        source_excerpt="Turnover USD 10,000,000 required.",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    ev1 = CompanyEvidence(organization_id=org.id, evidence_type="certification", title="ISO 27001 Cert", status="valid")
    ev2 = CompanyEvidence(organization_id=org.id, evidence_type="financial_audit", title="Audit 2024", status="valid")
    db_session.add_all([ev1, ev2])
    db_session.commit()

    # Link 1: Verified
    l1 = EvidenceRequirementLink(requirement_id=r1.id, evidence_id=ev1.id, match_status=ProofLinkStatus.VERIFIED, confidence_score=0.95, notes="Valid ISO 27001 verified.")
    # Link 2: Contradicted
    l2 = EvidenceRequirementLink(requirement_id=r2.id, evidence_id=ev2.id, match_status=ProofLinkStatus.CONTRADICTED, confidence_score=0.90, notes="Turnover of $3M fails requirement.")
    db_session.add_all([l1, l2])
    db_session.commit()

    matrix = service.evaluate_tender_compliance(db_session, tender.id)

    assert matrix.tender_id == tender.id
    assert matrix.overall_status == ComplianceStatus.NON_COMPLIANT
    assert matrix.overall_risk_level == RiskLevel.CRITICAL
    assert len(matrix.items) == 2

    r1_eval = next(i for i in matrix.items if i["requirement_id"] == r1.id)
    r2_eval = next(i for i in matrix.items if i["requirement_id"] == r2.id)

    assert r1_eval["status"] == ComplianceStatus.COMPLIANT
    assert r1_eval["risk_level"] == RiskLevel.LOW

    assert r2_eval["status"] == ComplianceStatus.NON_COMPLIANT
    assert r2_eval["risk_level"] == RiskLevel.CRITICAL
    assert "Resolve contradiction" in r2_eval["action_required"]
