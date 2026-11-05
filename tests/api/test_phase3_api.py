"""
API Integration tests for Phase 3 REST endpoints and Server-Side RBAC.
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from backend.app.infrastructure.database.models import (
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
    Tender,
    Workspace,
)


@pytest.fixture
def phase3_api_setup(db_session):
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


def test_bid_evaluation_api_flow(client: TestClient, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Trigger Bid Evaluation
    res = client.post(
        f"/api/v1/tenders/{tender.id}/bid-evaluation",
        json={"evaluator_type": "agent", "evaluator_id": "BidEngine"},
        headers={"X-User-Role": "Reviewer"},
    )
    assert res.status_code == 201
    data = res.json()
    assert "recommendation" in data
    assert "overall_score" in data
    eval_id = data["evaluation_id"]

    # 2. Query Latest Evaluation
    res_get = client.get(
        f"/api/v1/tenders/{tender.id}/bid-evaluation",
        headers={"X-User-Role": "Viewer"},
    )
    assert res_get.status_code == 200
    assert res_get.json()["evaluation_id"] == eval_id

    # 3. Record Human Decision
    res_dec = client.post(
        f"/api/v1/bid-evaluations/{eval_id}/decision",
        json={
            "decision": "APPROVED_BID",
            "user_id": "usr-dir-01",
            "user_name": "Director Lee",
            "rationale": "High strategic value account approved by management.",
        },
        headers={"X-User-Role": "Approver"},
    )
    assert res_dec.status_code == 200
    assert res_dec.json()["human_decision"] == "APPROVED_BID"


def test_financial_workspace_api_flow(client: TestClient, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Create Financial Proposal
    res = client.post(
        f"/api/v1/tenders/{tender.id}/financial-proposal",
        json={
            "title": "Commercial Pricing BOQ",
            "currency": "USD",
            "tax_rate_percent": "10.00",
            "margin_rate_percent": "15.00",
            "initial_items": [
                {"item_code": "DEV-01", "description": "Cloud Engineer", "unit": "hrs", "quantity": "100", "unit_rate": "120.00"}
            ],
        },
        headers={"X-User-Role": "Author"},
    )
    assert res.status_code == 201
    data = res.json()
    fin_id = data["id"]
    assert data["subtotal"] == "12000.00"

    # 2. Add Line Item
    res_add = client.post(
        f"/api/v1/financial-proposals/{fin_id}/line-items",
        json={
            "item_code": "INF-02",
            "description": "Server Hosting",
            "category": "Hardware",
            "unit": "month",
            "quantity": "12.00",
            "unit_rate": "500.00",
        },
        headers={"X-User-Role": "Author"},
    )
    assert res_add.status_code == 201

    # 3. Generate Scenarios
    res_scen = client.post(
        f"/api/v1/financial-proposals/{fin_id}/scenarios",
        headers={"X-User-Role": "Reviewer"},
    )
    assert res_scen.status_code == 200
    assert len(res_scen.json()) == 3

    # 4. Export Excel
    res_exp = client.get(
        f"/api/v1/financial-proposals/{fin_id}/export-excel",
        headers={"X-User-Role": "Viewer"},
    )
    assert res_exp.status_code == 200
    assert res_exp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_risks_and_deadlines_api_flow(client: TestClient, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Create Risk
    res_risk = client.post(
        f"/api/v1/tenders/{tender.id}/risks",
        json={
            "title": "Unclear SLA Penalties",
            "category": "Legal_Commercial",
            "likelihood": 3,
            "impact": 4,
            "description": "Clause 8.4 mentions uncapped liquidated damages.",
            "mitigation_strategy": "Submit clarification request before query deadline.",
        },
        headers={"X-User-Role": "Author"},
    )
    assert res_risk.status_code == 201
    assert res_risk.json()["risk_level"] == "Medium"

    # 2. Create Deadline
    dl_time = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    res_dl = client.post(
        f"/api/v1/tenders/{tender.id}/deadlines",
        json={
            "deadline_type": "Query Submission",
            "title": "Vendor Query Cutoff",
            "deadline_date": dl_time,
        },
        headers={"X-User-Role": "Author"},
    )
    assert res_dl.status_code == 201


def test_quality_and_portfolio_api_flow(client: TestClient, phase3_api_setup):
    ws, tender, prop = phase3_api_setup

    # 1. Quality Check
    res_qc = client.post(
        f"/api/v1/proposals/{prop.id}/quality-check",
        headers={"X-User-Role": "Reviewer"},
    )
    assert res_qc.status_code == 200
    data_qc = res_qc.json()
    assert data_qc["placeholder_count"] >= 1

    # 2. Portfolio Overview
    res_port = client.get(
        f"/api/v1/workspaces/{ws.id}/portfolio",
        headers={"X-User-Role": "Viewer"},
    )
    assert res_port.status_code == 200
    assert res_port.json()["total_tenders"] == 1

    # 3. Workspace Analytics
    res_ana = client.get(
        f"/api/v1/workspaces/{ws.id}/analytics",
        headers={"X-User-Role": "Viewer"},
    )
    assert res_ana.status_code == 200
    assert "pipeline" in res_ana.json()
