"""
TenderForge Switch & MCP Tool Integration Package.
"""

from backend.app.integrations.switch.tools.definitions import (
    TOOLS_REGISTRY,
    get_mcp_tools,
)
from backend.app.integrations.switch.tools.handlers import (
    ToolDispatcher,
    tool_dispatcher,
)

__all__ = [
    "TOOLS_REGISTRY",
    "get_mcp_tools",
    "ToolDispatcher",
    "tool_dispatcher",
]
