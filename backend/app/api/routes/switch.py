"""
Switch Integration & MCP Tool Exposure API endpoints for TenderForge.
"""

from __future__ import annotations

import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status as http_status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.domain.agents.registry import agent_registry
from backend.app.infrastructure.database.session import get_db
from backend.app.integrations.switch.agent_bridge import switch_bridge
from backend.app.integrations.switch.room_manager import SwitchRoomManager
from backend.app.integrations.switch.tools.definitions import get_mcp_tools
from backend.app.integrations.switch.tools.handlers import tool_dispatcher

router = APIRouter(tags=["Switch & MCP Integration"])
room_manager = SwitchRoomManager()


class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    caller_id: str
    caller_type: str = "agent"  # agent or human


class RoomCommandRequest(BaseModel):
    command_line: str
    user_id: str = "user_lead"
    user_role: str = "Bid Director"


@router.get("/switch/status", status_code=http_status.HTTP_200_OK)
def get_switch_status():
    """
    Check actual Switch Mesh connectivity and multi-agent subsystem health.
    Returns honest, evidence-based status: connected, degraded, disconnected, or not_configured.
    """
    agents = agent_registry.list_agents()
    tools = get_mcp_tools()

    switch_url = settings.SWITCH_API_URL
    switch_key = settings.SWITCH_API_KEY

    if not switch_url:
        status_state = "not_configured"
        message = "Switch Mesh integration is not configured. Running in internal agent broker mode."
    else:
        try:
            req = urllib.request.Request(
                f"{switch_url.rstrip('/')}/health",
                headers={"Authorization": f"Bearer {switch_key}"} if switch_key else {},
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    status_state = "connected"
                    message = "Switch Mesh connected and synchronized."
                else:
                    status_state = "degraded"
                    message = f"Switch Mesh returned non-200 status: {resp.status}."
        except Exception as e:
            status_state = "disconnected"
            message = f"Switch Mesh unreachable at {switch_url}: {str(e)}."

    return {
        "status": status_state,
        "message": message,
        "agents_registered": len(agents),
        "tools_registered": len(tools),
        "switch_url": switch_url or "none",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/switch/tools", status_code=http_status.HTTP_200_OK)
def list_mcp_tools():
    """List all available tools in Model Context Protocol (MCP) schema format."""
    return {
        "status": "success",
        "tools": get_mcp_tools(),
    }


@router.post("/switch/tools/execute", status_code=http_status.HTTP_200_OK)
def execute_tool(
    payload: ToolExecuteRequest,
    db: Session = Depends(get_db),
):
    """Execute a tool call with role-based permission verification."""
    result = tool_dispatcher.execute(
        db=db,
        tool_name=payload.tool_name,
        arguments=payload.arguments,
        caller_id=payload.caller_id,
        caller_type=payload.caller_type,
    )
    return result


@router.post("/switch/rooms/{tender_id}/command", status_code=http_status.HTTP_200_OK)
def execute_room_command(
    tender_id: str,
    payload: RoomCommandRequest,
    db: Session = Depends(get_db),
):
    """Parse and execute a slash command typed into the Tender War Room."""
    result = switch_bridge.handle_slash_command(
        db=db,
        tender_id=tender_id,
        command_line=payload.command_line,
        user_id=payload.user_id,
        user_role=payload.user_role,
    )
    return result


@router.get("/switch/rooms/{tender_id}/history", status_code=http_status.HTTP_200_OK)
def get_room_history(
    tender_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the event and message history for the active Tender War Room."""
    room = room_manager.get_room_by_tender(db, tender_id)
    history = switch_bridge.get_room_history()
    return {
        "status": "success",
        "room_name": room.room_name if room else None,
        "history": history,
    }


@router.get("/switch/agents", status_code=http_status.HTTP_200_OK)
def list_agents():
    """List all configured specialized AI agents and their capabilities."""
    agents = agent_registry.list_agents()
    return {
        "status": "success",
        "count": len(agents),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "handle": a.handle,
                "role": a.role,
                "description": a.description,
                "model": a.model,
                "permitted_tools": a.permitted_tools,
                "collaboration": a.collaboration.model_dump(),
            }
            for a in agents
        ]
    }
