"""
API Integration tests for Phase 3 REST endpoints and Server-Side RBAC.
"""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.api.routes.analytics import get_workspace_analytics
from backend.app.api.routes.bid_decision import (
    EvaluateBidRequest,
    HumanDecisionRequest,
    evaluate_tender,
    get_latest_bid_evaluation,
    record_human_bid_decision,
)
from backend.app.api.routes.deadlines import CreateDeadlineRequest, create_deadline
from backend.app.api.routes.financial import (
    AddLineItemRequest,
    CreateFinancialProposalRequest,
    add_line_item,
    create_financial_proposal,
    export_excel,
    generate_scenarios,
)
from backend.app.api.routes.optimizations import validate_proposal_quality
from backend.app.api.routes.portfolio import get_portfolio_overview
from backend.app.api.routes.risks import CreateRiskRequest, create_risk
from backend.app.infrastructure.database.models import (
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
    Tender,
    Workspace,
)


@pytest.fixture
def phase3_api_setup(db_session: Session):
    org = Organization(name="API Test Org", slug="api-org-p3")
    db_session.add(org)
    db_session.commit()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name="API Test Org Inc.",
        registration_number="REG-API-01",
        tax_id="TAX-API-01",
        jurisdiction="United States",
    )
    db_session.add(profile)

    ws = Workspace(name="API Phase 3 WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(
        workspace_id=ws.id,
        title="API Test Tender Phase 3",
        reference_number="API-TND-03",
        estimated_value=850000.0,
        currency="USD",
    )
    db_session.add(tender)
    db_session.commit()

    prop = Proposal(
        tender_id=tender.id,
        title="API Draft Proposal",
        status="drafting",
        current_version=1,
    )
    db_session.add(prop)
    db_session.commit()

    sec = ProposalSection(
        proposal_id=prop.id,
        section_number="1.0",
        title="Executive Summary",
        content="Our solution meets requirements. [TODO: Confirm scope]",
    )
    db_session.add(sec)
    db_session.commit()

    return ws, tender, prop


def test_bid_evaluation_api_flow(db_session: Session, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Trigger Bid Evaluation
    eval_req = EvaluateBidRequest(evaluator_type="agent", evaluator_id="BidEngine")
    data = evaluate_tender(tender_id=tender.id, payload=eval_req, db=db_session, _role="reviewer")
    assert "recommendation" in data
    assert "overall_score" in data
    eval_id = data["evaluation_id"]

    # 2. Query Latest Evaluation
    data_get = get_latest_bid_evaluation(tender_id=tender.id, db=db_session, _role="viewer")
    assert data_get["evaluation_id"] == eval_id

    # 3. Record Human Decision
    dec_req = HumanDecisionRequest(
        decision="APPROVED_BID",
        user_id="usr-dir-01",
        user_name="Director Lee",
        rationale="High strategic value account approved by management.",
    )
    data_dec = record_human_bid_decision(evaluation_id=eval_id, payload=dec_req, db=db_session, _role="approver")
    assert data_dec["human_decision"] == "APPROVED_BID"


def test_financial_workspace_api_flow(db_session: Session, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Create Financial Proposal
    fin_req = CreateFinancialProposalRequest(
        title="Commercial Pricing BOQ",
        currency="USD",
        tax_rate_percent="10.00",
        margin_rate_percent="15.00",
        initial_items=[
            {"item_code": "DEV-01", "description": "Cloud Engineer", "unit": "hrs", "quantity": "100", "unit_rate": "120.00"}
        ],
    )
    data = create_financial_proposal(tender_id=tender.id, payload=fin_req, db=db_session, _role="author")
    fin_id = data["id"]
    assert data["subtotal"] == "12000.00"

    # 2. Add Line Item
    item_req = AddLineItemRequest(
        item_code="INF-02",
        description="Server Hosting",
        category="Hardware",
        unit="month",
        quantity="12.00",
        unit_rate="500.00",
    )
    item_data = add_line_item(proposal_id=fin_id, payload=item_req, db=db_session, _role="author")
    assert item_data["id"] is not None

    # 3. Generate Scenarios
    scenarios = generate_scenarios(proposal_id=fin_id, db=db_session, _role="reviewer")
    assert len(scenarios) == 3

    # 4. Export Excel
    resp = export_excel(proposal_id=fin_id, db=db_session, _role="viewer")
    assert resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_risks_and_deadlines_api_flow(db_session: Session, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Create Risk
    risk_req = CreateRiskRequest(
        title="Unclear SLA Penalties",
        category="Legal_Commercial",
        likelihood=3,
        impact=4,
        description="Clause 8.4 mentions uncapped liquidated damages.",
        mitigation_strategy="Submit clarification request before query deadline.",
    )
    res_risk = create_risk(tender_id=tender.id, payload=risk_req, db=db_session, _role="author")
    assert res_risk["risk_level"] == "Medium"

    # 2. Create Deadline
    dl_time = datetime.now(timezone.utc) + timedelta(days=5)
    dl_req = CreateDeadlineRequest(
        deadline_type="Query Submission",
        title="Vendor Query Cutoff",
        deadline_date=dl_time,
    )
    res_dl = create_deadline(tender_id=tender.id, payload=dl_req, db=db_session, _role="author")
    assert res_dl["title"] == "Vendor Query Cutoff"


def test_quality_and_portfolio_api_flow(db_session: Session, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Quality Check
    data_qc = validate_proposal_quality(proposal_id=prop.id, checked_by="QualityAuditor", db=db_session, _role="reviewer")
    assert data_qc["placeholder_count"] >= 1

    # 2. Portfolio Overview
    data_port = get_portfolio_overview(workspace_id=ws.id, db=db_session, _role="viewer")
    assert data_port["total_tenders"] == 1

    # 3. Workspace Analytics
    data_ana = get_workspace_analytics(workspace_id=ws.id, db=db_session, _role="viewer")
    assert "pipeline" in data_ana
