"""
Agent Registry for discovering, loading, and managing specialized AI agent definitions.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from backend.app.core.logging import get_logger
from backend.app.domain.agents.models import AgentDefinition, AgentRole

logger = get_logger("agent_registry")


class AgentRegistry:
    """Central registry for TenderForge specialized agents."""

    def __init__(self, agents_dir: Optional[str] = None):
        if agents_dir:
            self._agents_dir = Path(agents_dir)
        else:
            # Default to project_root/config/agents
            root = Path(__file__).resolve().parent.parent.parent.parent.parent
            self._agents_dir = root / "config" / "agents"

        self._agents: Dict[str, AgentDefinition] = {}
        self.reload()

    def reload(self) -> None:
        """Scan directory and load all agent YAML specifications."""
        self._agents.clear()
        if not self._agents_dir.exists():
            logger.warning(f"Agents configuration directory not found at {self._agents_dir}")
            return

        for filepath in self._agents_dir.glob("*.yaml"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                
                agent = AgentDefinition(**data)
                
                # Load system prompt from file if specified
                if agent.prompt_file:
                    root = Path(__file__).resolve().parent.parent.parent.parent.parent
                    prompt_path = root / agent.prompt_file
                    if prompt_path.exists():
                        with open(prompt_path, "r", encoding="utf-8") as pf:
                            agent.system_prompt = pf.read().strip()
                    else:
                        logger.warning(f"Prompt file not found for agent {agent.id}: {prompt_path}")

                self._agents[agent.id] = agent
                logger.info(f"Loaded agent definition '{agent.name}' ({agent.id}) with {len(agent.permitted_tools)} permitted tools.")
            except Exception as e:
                logger.error(f"Failed to load agent definition from {filepath}: {e}")

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        return self._agents.get(agent_id)

    def get_by_handle(self, handle: str) -> Optional[AgentDefinition]:
        clean_handle = handle.lower().lstrip("@")
        for agent in self._agents.values():
            if agent.handle.lower().lstrip("@") == clean_handle:
                return agent
        return None

    def list_agents(self) -> List[AgentDefinition]:
        return list(self._agents.values())

    def is_tool_permitted(self, agent_id: str, tool_name: str) -> bool:
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        return tool_name in agent.permitted_tools


# Global singleton instance
agent_registry = AgentRegistry()
