"""
Switch Agent Bridge Implementation for TenderForge.
Handles bi-directional communication, Agent Protocol frames, command routing, and room event broadcasting.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.domain.agents.registry import agent_registry
from backend.app.infrastructure.database.session import SessionLocal
from backend.app.integrations.switch.contracts.schemas import (
    SwitchAgentCommand,
    SwitchRequirementCitation,
    SwitchRoomContext,
    SwitchRoomNotification,
    SwitchRoomParticipant,
)
from backend.app.integrations.switch.interfaces.agent_bridge import BaseSwitchAgentBridge
from backend.app.integrations.switch.room_manager import SwitchRoomManager
from backend.app.integrations.switch.tools.handlers import tool_dispatcher

logger = get_logger("switch_agent_bridge")


class SwitchAgentBridge(BaseSwitchAgentBridge):
    """Bridge adapter connecting Switch multi-agent conversational rooms to TenderForge."""

    def __init__(self, room_manager: Optional[SwitchRoomManager] = None):
        self.room_manager = room_manager or SwitchRoomManager()
        self._message_history: List[Dict[str, Any]] = []
        self._event_listeners: List[Callable[[SwitchRoomNotification], None]] = []

    def subscribe(self, listener: Callable[[SwitchRoomNotification], None]) -> None:
        """Register an event callback for outbound room notifications."""
        self._event_listeners.append(listener)

    async def broadcast_room_event(self, notification: SwitchRoomNotification) -> bool:
        """Broadcast an event frame to the Switch room and all registered listeners."""
        event_dict = notification.model_dump()
        self._message_history.append(event_dict)
        logger.info(f"Broadcasted to room '{notification.room_id}': [{notification.event_type}] {notification.title}")

        for listener in self._event_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(notification)
                else:
                    listener(notification)
            except Exception as e:
                logger.error(f"Error in event listener callback: {e}")

        return True

    async def dispatch_room_command(self, command: SwitchAgentCommand) -> Dict[str, Any]:
        """Process an incoming command or tool call from a Switch room participant."""
        logger.info(f"Received Switch command '{command.command_name}' from agent '{command.agent_role}'")
        
        with SessionLocal() as db:
            try:
                result = tool_dispatcher.execute(
                    db=db,
                    tool_name=command.command_name,
                    arguments=command.parameters,
                    caller_id=command.agent_role,
                    caller_type="agent" if command.agent_role in [a.id for a in agent_registry.list_agents()] else "human",
                )
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                return {"status": "error", "error": str(e)}

    def handle_slash_command(
        self,
        db: Session,
        tender_id: str,
        command_line: str,
        user_id: str = "user_lead",
        user_role: str = "Bid Director",
    ) -> Dict[str, Any]:
        """Parse and execute slash commands typed into a Tender War Room."""
        parts = command_line.strip().split()
        if not parts:
            return {"status": "error", "message": "Empty command"}

        cmd = parts[0].lower()

        if cmd in ("/analyze", "/extract"):
            return tool_dispatcher.execute(db, "analyze_tender", {"tender_id": tender_id}, caller_id="tender_analyst", caller_type="agent")

        elif cmd in ("/compliance", "/check-compliance"):
            return tool_dispatcher.execute(db, "evaluate_compliance", {"tender_id": tender_id}, caller_id="compliance_officer", caller_type="agent")

        elif cmd in ("/draft", "/draft-proposal"):
            title = " ".join(parts[1:]) if len(parts) > 1 else None
            args = {"tender_id": tender_id}
            if title:
                args["title"] = title
            return tool_dispatcher.execute(db, "create_proposal_draft", args, caller_id="proposal_architect", caller_type="agent")

        elif cmd in ("/audit", "/audit-proposal"):
            proposal_id = parts[1] if len(parts) > 1 else None
            if not proposal_id:
                # Find latest proposal
                from backend.app.infrastructure.database.models import Proposal
                p = db.query(Proposal).filter(Proposal.tender_id == tender_id).order_by(Proposal.created_at.desc()).first()
                if not p:
                    return {"status": "error", "message": "No proposal found to audit."}
                proposal_id = p.id
            return tool_dispatcher.execute(db, "audit_proposal", {"proposal_id": proposal_id}, caller_id="bid_auditor", caller_type="agent")

        elif cmd in ("/approve",):
            proposal_id = parts[1] if len(parts) > 1 else None
            comments = " ".join(parts[2:]) if len(parts) > 2 else "Approved by authorized signatory."
            if not proposal_id:
                from backend.app.infrastructure.database.models import Proposal
                p = db.query(Proposal).filter(Proposal.tender_id == tender_id).order_by(Proposal.created_at.desc()).first()
                if not p:
                    return {"status": "error", "message": "No proposal found to approve."}
                proposal_id = p.id
            return tool_dispatcher.execute(
                db,
                "record_human_decision",
                {
                    "tender_id": tender_id,
                    "proposal_id": proposal_id,
                    "user_id": user_id,
                    "user_name": "Bid Director",
                    "user_role": user_role,
                    "decision": "Approved",
                    "comments": comments,
                },
                caller_id=user_id,
                caller_type="human",
            )

        elif cmd in ("/export", "/export-package"):
            from backend.app.infrastructure.database.models import Proposal
            p = db.query(Proposal).filter(Proposal.tender_id == tender_id).order_by(Proposal.created_at.desc()).first()
            if not p:
                return {"status": "error", "message": "No proposal found to export."}
            return tool_dispatcher.execute(
                db,
                "export_bid_package",
                {"tender_id": tender_id, "proposal_id": p.id, "require_human_approval": True},
                caller_id=user_id,
                caller_type="human",
            )

        return {"status": "error", "message": f"Unknown command '{cmd}'. Available: /analyze, /compliance, /draft, /audit, /approve, /export"}

    def get_room_history(self) -> List[Dict[str, Any]]:
        return list(self._message_history)


# Global Switch Bridge singleton
switch_bridge = SwitchAgentBridge()


def get_switch_bridge() -> SwitchAgentBridge:
    return switch_bridge


def _post_msg(self, channel_id: str, sender_agent_id: str, text: str) -> bool:
    self._message_history.append({"channel_id": channel_id, "sender_id": sender_agent_id, "text": text})
    return True

SwitchAgentBridge.post_message = _post_msg
