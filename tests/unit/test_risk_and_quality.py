"""
Unit tests for Risk Management, Proposal Revisions, Optimization, and Quality Validation.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    ComplianceMatrix,
    EvaluationCriteria,
    Organization,
    Proposal,
    ProposalSection,
    Tender,
    Workspace,
)
from backend.app.services.proposal_optimization_service import ProposalOptimizationService
from backend.app.services.proposal_revision_service import ProposalRevisionService
from backend.app.services.risk_service import RiskService


@pytest.fixture
def risk_quality_setup(db_session: Session):
    org = Organization(name="Risk Quality Org", slug="rq-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="RQ WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="Mission Critical Defence Tender")
    db_session.add(tender)
    db_session.commit()

    prop = Proposal(tender_id=tender.id, title="Technical Response Proposal", status="approved", current_version=1)
    db_session.add(prop)
    db_session.commit()

    s1 = ProposalSection(
        proposal_id=prop.id,
        section_number="1.0",
        title="Executive Summary",
        content="This proposal outlines our solution. [TODO: Insert exact completion date]. Turnover exceeds $5M [ProofLink: FIN-01].",
    )
    s2 = ProposalSection(
        proposal_id=prop.id,
        section_number="2.0",
        title="Technical Architecture",
        content="We implement high availability architecture across dual data centers.",
    )
    db_session.add_all([s1, s2])
    db_session.commit()

    return tender, prop, s1, s2


def test_risk_scoring_and_harvesting(db_session: Session, risk_quality_setup):
    tender, prop, s1, s2 = risk_quality_setup
    svc = RiskService(db_session)

    # 1. Manual risk creation
    r = svc.create_risk(
        tender_id=tender.id,
        title="Key Personnel Shortage",
        category="Technical",
        likelihood=4,
        impact=4,
        description="Lead architect may not be available on short notice.",
        mitigation_strategy="Pre-contract standby agreement with senior contractor.",
        db=db_session,
    )
    assert r.severity_score == 16
    assert r.risk_level == "High"

    # 2. Risk harvesting from compliance gap
    matrix = ComplianceMatrix(
        tender_id=tender.id,
        overall_status="Non-Compliant",
        overall_risk_level="High",
        summary="Failed compliance clause",
        items=[
            {"status": "Non-Compliant", "description": "Mandatory security clearance Level 3 required."}
        ],
    )
    db_session.add(matrix)
    db_session.commit()

    harvested = svc.harvest_risks_for_tender(tender.id, db=db_session)
    assert len(harvested) >= 1
    assert any("security clearance" in h.description.lower() for h in harvested)


def test_proposal_revision_and_approval_invalidation(db_session: Session, risk_quality_setup):
    tender, prop, s1, s2 = risk_quality_setup
    svc = ProposalRevisionService(db_session)

    assert prop.status == "approved"
    assert prop.current_version == 1

    # Edit section content
    updated_sec, invalidated = svc.update_section_with_invalidation(
        proposal_id=prop.id,
        section_number="2.0",
        new_content="We implement high availability active-active clustering across three availability zones.",
        author_id="usr-author-01",
        change_summary="Upgraded from dual DC to active-active triple AZ",
        db=db_session,
    )

    assert invalidated is True
    assert prop.status == "drafting"
    assert prop.current_version == 2


def test_proposal_quality_check_detects_placeholders(db_session: Session, risk_quality_setup):
    tender, prop, s1, s2 = risk_quality_setup
    svc = ProposalRevisionService(db_session)

    qc = svc.validate_proposal_quality(prop.id, checked_by="QualityAuditor", db=db_session)

    assert qc.placeholder_count >= 1
    assert any("TODO" in p for p in qc.placeholders_found)
    assert qc.passed is False
    assert qc.word_count > 0


def test_proposal_optimization_generates_recommendations(db_session: Session, risk_quality_setup):
    tender, prop, s1, s2 = risk_quality_setup

    crit = EvaluationCriteria(
        tender_id=tender.id,
        criterion_code="CRIT-QUAL-01",
        title="Quality Assurance & Testing Framework",
        category="Quality",
        weight_percentage=20.0,
        max_marks=20.0,
        description="Demonstrated automated regression testing and CI/CD security scanning.",
        mandatory=True,
        scoring_rules={},
    )
    db_session.add(crit)
    db_session.commit()

    svc = ProposalOptimizationService(db_session)
    opts = svc.analyze_and_optimize(prop.id, db=db_session)

    assert len(opts) >= 1
    missing_opt = next(o for o in opts if o.criterion_id == crit.id)
    assert missing_opt.coverage_status in ("Missing", "Weak")
    assert missing_opt.after_text is not None

    # Apply optimization
    applied = svc.apply_optimization(missing_opt.id, db=db_session)
    assert applied.status == "Applied"
