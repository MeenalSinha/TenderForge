"""
Switch Room Event Stream & Persona Messaging Engine for TenderForge.
Formats collaborative agent utterances, ProofLink citations, and room notifications.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.core.logging import get_logger
from backend.app.domain.agents.models import AgentMessage
from backend.app.integrations.switch.agent_bridge import switch_bridge
from backend.app.integrations.switch.contracts.schemas import (
    SwitchRequirementCitation,
    SwitchRoomNotification,
)

logger = get_logger("event_stream")


class SwitchEventStream:
    """Publishes formatted multi-agent interactions and ProofLink notifications to the room stream."""

    def __init__(self, bridge=None):
        self.bridge = bridge or switch_bridge

    def emit_agent_message(
        self,
        room_id: str,
        agent_handle: str,
        agent_name: str,
        content: str,
        mentions: Optional[List[str]] = None,
        action_items: Optional[List[str]] = None,
        citations: Optional[List[SwitchRequirementCitation]] = None,
    ) -> SwitchRoomNotification:
        """Publish an agent utterance into the room event stream."""
        notification = SwitchRoomNotification(
            room_id=room_id,
            event_type="agent.message",
            title=f"{agent_name} ({agent_handle})",
            summary=content,
            citations=citations or [],
            metadata={
                "agent_handle": agent_handle,
                "mentions": mentions or [],
                "action_items": action_items or [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        # In synchronous context, schedule or append
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.bridge.broadcast_room_event(notification))
            else:
                loop.run_until_complete(self.bridge.broadcast_room_event(notification))
        except RuntimeError:
            asyncio.run(self.bridge.broadcast_room_event(notification))

        return notification

    def emit_milestone(
        self,
        room_id: str,
        milestone_name: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SwitchRoomNotification:
        """Publish a lifecycle milestone achieved by the team."""
        notification = SwitchRoomNotification(
            room_id=room_id,
            event_type="milestone.reached",
            title=f"Milestone: {milestone_name}",
            summary=summary,
            citations=[],
            metadata=metadata or {},
        )
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.bridge.broadcast_room_event(notification))
            else:
                loop.run_until_complete(self.bridge.broadcast_room_event(notification))
        except RuntimeError:
            asyncio.run(self.bridge.broadcast_room_event(notification))

        return notification


# Global event stream instance
room_event_stream = SwitchEventStream()
