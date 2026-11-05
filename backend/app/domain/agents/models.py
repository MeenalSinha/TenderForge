"""
Domain models for Specialized AI Agents in TenderForge.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    TENDER_ANALYST = "tender_analyst"
    COMPLIANCE_OFFICER = "compliance_officer"
    EVIDENCE_RESEARCHER = "evidence_researcher"
    PROPOSAL_ARCHITECT = "proposal_architect"
    BID_AUDITOR = "bid_auditor"


class AgentCollaborationConfig(BaseModel):
    triggers: List[str] = Field(default_factory=list)
    hands_off_to: List[str] = Field(default_factory=list)


class AgentDefinition(BaseModel):
    id: str
    name: str
    handle: str
    role: str
    description: str
    prompt_file: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 4000
    permitted_tools: List[str] = Field(default_factory=list)
    collaboration: AgentCollaborationConfig = Field(default_factory=AgentCollaborationConfig)
    system_prompt: Optional[str] = None


class AgentMessage(BaseModel):
    message_id: str
    agent_id: str
    agent_name: str
    agent_handle: str
    room_id: str
    content: str
    mentions: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
