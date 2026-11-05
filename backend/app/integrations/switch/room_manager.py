"""
Tender War Room Manager for Switch Multi-Agent Collaboration.
Maps tenders to isolated collaborative rooms across Mattermost, Slack, Teams, or Web.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError
from backend.app.core.logging import get_logger
from backend.app.domain.agents.registry import agent_registry
from backend.app.infrastructure.database.models import (
    SwitchRoom,
    Tender,
    WorkflowState,
)

logger = get_logger("switch_room_manager")


class SwitchRoomManager:
    """Manages creation, membership, isolation, and message delivery in Tender War Rooms."""

    def create_or_get_room(
        self,
        db: Session,
        tender_id: str,
        room_name: Optional[str] = None,
        channel_type: str = "mattermost",
    ) -> SwitchRoom:
        """Create a dedicated collaborative room or retrieve the existing one."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        existing = db.query(SwitchRoom).filter(
            SwitchRoom.tender_id == tender_id,
            SwitchRoom.status == "active",
        ).first()

        if existing:
            return existing

        name = room_name or f"tender-{tender.reference_number or tender.id[:8].lower()}"
        channel_id = f"chan_{uuid.uuid4().hex[:12]}"

        room = SwitchRoom(
            tender_id=tender_id,
            room_name=name,
            channel_id=channel_id,
            channel_type=channel_type,
            status="active",
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        logger.info(f"Created Switch War Room '{name}' ({channel_id}) for tender {tender_id}")
        return room

    def get_room_participants(self, room: SwitchRoom) -> List[Dict[str, Any]]:
        """List all active participants including specialized AI agent personas and human leads."""
        participants = []
        for agent in agent_registry.list_agents():
            participants.append({
                "id": agent.id,
                "name": agent.name,
                "handle": agent.handle,
                "role": agent.role,
                "is_agent": True,
            })
        
        # Add default human participants
        participants.extend([
            {"id": "user_lead", "name": "Bid Director", "handle": "@BidDirector", "role": "Authorized Signatory", "is_agent": False},
            {"id": "user_legal", "name": "Legal Counsel", "handle": "@LegalCounsel", "role": "Compliance Reviewer", "is_agent": False},
        ])
        return participants

    def get_room_by_tender(self, db: Session, tender_id: str) -> Optional[SwitchRoom]:
        return db.query(SwitchRoom).filter(
            SwitchRoom.tender_id == tender_id,
            SwitchRoom.status == "active",
        ).first()
