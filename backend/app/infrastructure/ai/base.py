"""
Base AI Provider Interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from backend.app.domain.intelligence.models import StructuredTenderIntelligence


class BaseAIProvider(ABC):
    """Abstract interface decoupling tender intelligence extraction from LLM vendors."""

    provider_id: str = "base"
    model_id: str = "default"

    @abstractmethod
    async def extract_intelligence(
        self,
        document_text: str,
        prompt_template: str,
        parameters: Dict[str, Any],
    ) -> Tuple[StructuredTenderIntelligence, Dict[str, Any]]:
        """
        Execute intelligence extraction.
        Returns (StructuredTenderIntelligence, raw_response_metadata).
        """
        pass

