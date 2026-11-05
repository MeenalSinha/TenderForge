"""
AI Provider Factory & Fallback Management.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple
from backend.app.core.config import settings
from backend.app.core.exceptions import AIConfigurationRequiredError
from backend.app.domain.intelligence.models import StructuredTenderIntelligence
from backend.app.infrastructure.ai.base import BaseAIProvider
from backend.app.infrastructure.ai.mock_adapter import MockAIProvider
from backend.app.infrastructure.ai.openai_adapter import OpenAICompatibleProvider


class MissingConfigProvider(BaseAIProvider):
    """Graceful placeholder raised when no active AI provider is configured."""

    provider_id: str = "none"
    model_id: str = "not_configured"

    async def extract_intelligence(
        self,
        document_text: str,
        prompt_template: str,
        parameters: Dict[str, Any],
    ) -> Tuple[StructuredTenderIntelligence, Dict[str, Any]]:
        raise AIConfigurationRequiredError(
            "AI intelligence extraction requires an active AI provider. "
            "Please configure AI_PROVIDER and valid credentials (e.g. AI_API_KEY) in .env or settings."
        )


def get_ai_provider() -> BaseAIProvider:
    """Factory returning configured AI Provider instance."""
    provider_type = (settings.AI_PROVIDER or "").strip().lower()

    if not provider_type or provider_type in ("none", "disabled", "null"):
        return MissingConfigProvider()

    if provider_type == "mock":
        return MockAIProvider()

    if provider_type in ("openai", "gemini", "anthropic", "ollama"):
        if not settings.is_ai_configured:
            return MissingConfigProvider()

        base_url = settings.AI_API_BASE_URL or "https://api.openai.com/v1"
        if provider_type == "ollama" and not settings.AI_API_BASE_URL:
            base_url = "http://localhost:11434/v1"

        return OpenAICompatibleProvider(
            api_key=settings.AI_API_KEY or "dummy_for_ollama",
            model_name=settings.AI_MODEL_NAME,
            base_url=base_url,
            timeout=settings.AI_TIMEOUT_SECONDS,
            max_retries=settings.AI_MAX_RETRIES,
        )

    return MissingConfigProvider()

