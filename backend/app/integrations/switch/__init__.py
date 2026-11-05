"""
Switch integration package for TenderForge.
"""

from backend.app.integrations.switch.agent_bridge import (
    SwitchAgentBridge,
    switch_bridge,
)
from backend.app.integrations.switch.contracts.schemas import (
    SwitchAgentCommand,
    SwitchRequirementCitation,
    SwitchRoomContext,
    SwitchRoomNotification,
    SwitchRoomParticipant,
)
from backend.app.integrations.switch.event_stream import (
    SwitchEventStream,
    room_event_stream,
)
from backend.app.integrations.switch.interfaces.agent_bridge import BaseSwitchAgentBridge
from backend.app.integrations.switch.room_manager import SwitchRoomManager
from backend.app.integrations.switch.tools import (
    TOOLS_REGISTRY,
    ToolDispatcher,
    get_mcp_tools,
    tool_dispatcher,
)

__all__ = [
    "SwitchAgentBridge",
    "switch_bridge",
    "SwitchAgentCommand",
    "SwitchRequirementCitation",
    "SwitchRoomContext",
    "SwitchRoomNotification",
    "SwitchRoomParticipant",
    "SwitchEventStream",
    "room_event_stream",
    "BaseSwitchAgentBridge",
    "SwitchRoomManager",
    "TOOLS_REGISTRY",
    "ToolDispatcher",
    "get_mcp_tools",
    "tool_dispatcher",
]
