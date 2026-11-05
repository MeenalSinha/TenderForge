"""
Unit tests for TenderForge Agent Tool Interface & RBAC Guardrails.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.core.errors import SecurityError
from backend.app.infrastructure.database.models import Organization, Workspace
from backend.app.integrations.switch.tools.definitions import get_mcp_tools
from backend.app.integrations.switch.tools.handlers import ToolDispatcher


def test_mcp_tools_definitions_count():
    tools = get_mcp_tools()
    assert len(tools) >= 16
    tool_names = [t["name"] for t in tools]
    assert "create_tender_workspace" in tool_names
    assert "upload_tender_document" in tool_names
    assert "analyze_tender" in tool_names
    assert "evaluate_compliance" in tool_names
    assert "create_proposal_draft" in tool_names
    assert "audit_proposal" in tool_names
    assert "record_human_decision" in tool_names
    assert "export_bid_package" in tool_names


def test_agent_rbac_tool_execution(db_session: Session):
    dispatcher = ToolDispatcher()
    org = Organization(name="RBAC Org", slug="rbac-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="WS_RBAC", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    from backend.app.infrastructure.database.models import Tender
    tender = Tender(workspace_id=ws.id, title="RBAC Test Tender", reference_number="RBAC-001")
    db_session.add(tender)
    db_session.commit()

    # 1. Permitted invocation: Tender Analyst executing get_tender_overview
    overview = dispatcher.execute(
        db=db_session,
        tool_name="get_tender_overview",
        arguments={"tender_id": tender.id},
        caller_id="tender_analyst",
        caller_type="agent",
    )
    assert overview["status"] == "success"
    assert overview["tender_id"] == tender.id
    # Even if tender not found, it won't raise SecurityError
    # (TenderNotFoundError is expected)
    # Let's test with create_tender_workspace with human caller
    ws_res = dispatcher.execute(
        db=db_session,
        tool_name="create_tender_workspace",
        arguments={"name": "New WS", "organization_id": org.id},
        caller_id="human_admin",
        caller_type="human",
    )
    assert ws_res["status"] == "success"
    assert ws_res["name"] == "New WS"

    # 2. Blocked invocation: Tender Analyst attempting to execute audit_proposal
    with pytest.raises(SecurityError, match="Permission denied"):
        dispatcher.execute(
            db=db_session,
            tool_name="audit_proposal",
            arguments={"proposal_id": "prop_123"},
            caller_id="tender_analyst",
            caller_type="agent",
        )

    # 3. Blocked invocation: Agent attempting to execute human governance tool
    with pytest.raises(SecurityError, match="strictly forbidden"):
        dispatcher.execute(
            db=db_session,
            tool_name="record_human_decision",
            arguments={"tender_id": "t1", "decision": "Approved"},
            caller_id="bid_auditor",
            caller_type="agent",
        )
