"""
API tests for Phase 2 REST Endpoints.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import Organization, Tender, Workspace


def test_phase2_api_endpoints_flow(client: TestClient, db_session: Session):
    # Setup Organization and Workspace
    org = Organization(name="API Test Org", slug="api-test-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="API WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(workspace_id=ws.id, title="API Tender Test", reference_number="API-RFP-001")
    db_session.add(tender)
    db_session.commit()

    # 1. Organization Profile API
    res_prof = client.post(
        f"/api/v1/organizations/{org.id}/profile",
        json={
            "legal_name": "API Test Org LLC",
            "registration_number": "REG-12345",
            "tax_id": "TAX-12345",
            "financial_metrics": {"turnover_fy25": 5500000},
        },
    )
    assert res_prof.status_code == 200
    assert res_prof.json()["data"]["legal_name"] == "API Test Org LLC"

    # 2. Company Evidence API
    res_ev = client.post(
        f"/api/v1/organizations/{org.id}/evidence",
        json={
            "title": "ISO 9001:2015 Certificate",
            "evidence_type": "certification",
            "issuer": "TUV SUD",
            "reference_number": "TUV-9001",
            "summary": "Valid ISO 9001 quality certificate.",
            "tags": ["iso", "quality"],
        },
    )
    assert res_ev.status_code == 201
    ev_id = res_ev.json()["data"]["id"]

    # 3. Search Evidence API
    res_search = client.get(f"/api/v1/organizations/{org.id}/evidence?query=iso")
    assert res_search.status_code == 200
    assert res_search.json()["count"] == 1

    # 4. Switch Tools API
    res_tools = client.get("/api/v1/switch/tools")
    assert res_tools.status_code == 200
    assert len(res_tools.json()["tools"]) >= 16

    # 5. Switch Agents API
    res_agents = client.get("/api/v1/switch/agents")
    assert res_agents.status_code == 200
    assert res_agents.json()["count"] == 5

    # 6. Workflow API
    res_wf = client.get(f"/api/v1/tenders/{tender.id}/workflow")
    assert res_wf.status_code == 200
    assert res_wf.json()["data"]["current_stage"] == "WORKSPACE_INITIALIZED"
