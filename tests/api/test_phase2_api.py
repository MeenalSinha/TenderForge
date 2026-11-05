"""
API tests for Phase 2 REST Endpoints.
"""

from sqlalchemy.orm import Session
from backend.app.api.routes.evidence import (
    CompanyEvidenceCreateRequest,
    OrganizationProfileRequest,
    register_evidence,
    search_evidence,
    update_organization_profile,
)
from backend.app.api.routes.switch import list_agents, list_mcp_tools
from backend.app.api.routes.workflow import get_workflow_state
from backend.app.infrastructure.database.models import Organization, Tender, Workspace


def test_phase2_api_endpoints_flow(db_session: Session):
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
    prof_req = OrganizationProfileRequest(
        legal_name="API Test Org LLC",
        registration_number="REG-12345",
        tax_id="TAX-12345",
        financial_metrics={"turnover_fy25": 5500000},
    )
    res_prof = update_organization_profile(organization_id=org.id, payload=prof_req, db=db_session)
    assert res_prof["status"] == "success"
    assert res_prof["data"]["legal_name"] == "API Test Org LLC"

    # 2. Company Evidence API
    ev_req = CompanyEvidenceCreateRequest(
        title="ISO 9001:2015 Certificate",
        evidence_type="certification",
        issuer="TUV SUD",
        reference_number="TUV-9001",
        summary="Valid ISO 9001 quality certificate.",
        tags=["iso", "quality"],
    )
    res_ev = register_evidence(organization_id=org.id, payload=ev_req, db=db_session)
    assert res_ev["status"] == "success"
    ev_id = res_ev["data"]["id"]
    assert ev_id is not None

    # 3. Search Evidence API
    res_search = search_evidence(organization_id=org.id, query="iso", evidence_type=None, db=db_session)
    assert res_search["status"] == "success"
    assert res_search["count"] == 1

    # 4. Switch Tools API
    res_tools = list_mcp_tools()
    assert res_tools["status"] == "success"
    assert len(res_tools["tools"]) >= 16

    # 5. Switch Agents API
    res_agents = list_agents()
    assert res_agents["status"] == "success"
    assert res_agents["count"] == 5

    # 6. Workflow API
    res_wf = get_workflow_state(tender_id=tender.id, db=db_session)
    assert res_wf["status"] == "success"
    assert res_wf["data"]["current_stage"] == "WORKSPACE_INITIALIZED"
