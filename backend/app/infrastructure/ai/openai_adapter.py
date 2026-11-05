"""
OpenAI-Compatible Remote LLM Provider Adapter.
Supports OpenAI, Gemini (OpenAI compat), Ollama, and local endpoints.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple
import httpx
from backend.app.core.config import settings
from backend.app.core.exceptions import AIExecutionError
from backend.app.domain.intelligence.models import StructuredTenderIntelligence
from backend.app.infrastructure.ai.base import BaseAIProvider


class OpenAICompatibleProvider(BaseAIProvider):
    """Invokes remote OpenAI-compatible chat completion endpoints."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_name
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider_id = "openai_compatible"

    async def extract_intelligence(
        self,
        document_text: str,
        prompt_template: str,
        parameters: Dict[str, Any],
    ) -> Tuple[StructuredTenderIntelligence, Dict[str, Any]]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Format system prompt and untrusted document content
        formatted_prompt = prompt_template.replace("{document_content}", document_text)

        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "You are TenderForge Intelligence Extractor. Always return raw JSON.",
                },
                {"role": "user", "content": formatted_prompt},
            ],
            "temperature": parameters.get("temperature", settings.AI_TEMPERATURE),
            "max_tokens": parameters.get("max_tokens", settings.AI_MAX_TOKENS),
            "response_format": {"type": "json_object"},
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                    content_str = data["choices"][0]["message"]["content"]
                    parsed_json = json.loads(content_str)
                    structured = StructuredTenderIntelligence.model_validate(parsed_json)
                    return structured, data
            except (httpx.HTTPError, json.JSONDecodeError, ValueError) as e:
                last_error = e
                continue

        raise AIExecutionError(f"Failed to extract intelligence via {self.provider_id}: {str(last_error)}")

