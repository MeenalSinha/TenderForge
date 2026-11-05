"""
Switch Ecosystem Integration Contracts & Schemas.
Establishes the communication contract for future Switch Room agents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SwitchRoomParticipant(BaseModel):
    user_id: str
    display_name: str
    is_agent: bool = False
    agent_role: Optional[str] = None  # e.g. "Tender Analyst", "Compliance Officer"


class SwitchRoomContext(BaseModel):
    """Context payload representing an active Switch War Room."""

    room_id: str = Field(..., description="Unique Switch Room identifier")
    room_name: str = Field(..., description="E.g. Tender-WarRoom-RFP2026")
    channel_type: str = Field("web", description="slack, teams, discord, web")
    participants: List[SwitchRoomParticipant] = Field(default_factory=list)
    system_instructions: Optional[str] = None


class SwitchAgentCommand(BaseModel):
    """Command payload emitted by a Switch Agent targeting TenderForge."""

    command_id: str
    command_name: str  # analyze_document, audit_claims, match_evidence
    agent_role: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SwitchRequirementCitation(BaseModel):
    """ProofLink-compatible citation structure transmitted to Switch chat channels."""

    requirement_id: str
    category: str
    classification: str
    source_document_id: str
    source_page: int
    source_offset: int
    source_excerpt: str
    confidence_score: float


class SwitchRoomNotification(BaseModel):
    """Structured notification emitted by TenderForge to a Switch Room."""

    room_id: str
    event_type: str  # document.parsed, analysis.completed, compliance.warning
    title: str
    summary: str
    citations: List[SwitchRequirementCitation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

