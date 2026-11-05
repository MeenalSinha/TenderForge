"""
TenderForge Centralized Configuration Engine.

Adheres strictly to the "Nothing Hardcoded" principle by loading operational
parameters, thresholds, file limits, parser rules, and AI configurations
from environment variables, .env files, and external YAML configurations.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings validated via Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "TenderForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "sqlite:///./tenderforge.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Storage
    STORAGE_PROVIDER: str = "local"
    STORAGE_ROOT: str = "./storage"
    STORAGE_LOCAL_PATH: str = "./storage"
    TEMP_STORAGE_ROOT: str = "./temp_uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 52428800  # 50 MB

    # Config File Paths
    CONFIG_PATH_APP: str = "./config/application.yaml"
    CONFIG_PATH_DOC_PROCESSING: str = "./config/document_processing.yaml"
    PROMPTS_DIR: str = "./config/prompts"

    # AI Provider
    AI_PROVIDER: str = "mock"  # mock, openai, gemini, anthropic, ollama, or none/empty
    AI_MODEL_NAME: str = "gpt-4o"
    AI_API_KEY: Optional[str] = None
    AI_API_BASE_URL: Optional[str] = None
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4096
    AI_TIMEOUT_SECONDS: float = 60.0
    AI_MAX_RETRIES: int = 2

    # Cached YAML configurations loaded at runtime
    _app_yaml: Dict[str, Any] = {}
    _doc_yaml: Dict[str, Any] = {}

    def model_post_init(self, __context: Any) -> None:
        """Load external YAML files and verify critical paths."""
        self._load_yaml_configs()
        self._ensure_storage_directories()

    def _load_yaml_configs(self) -> None:
        app_path = Path(self.CONFIG_PATH_APP)
        if app_path.exists():
            with open(app_path, "r", encoding="utf-8") as f:
                self._app_yaml = yaml.safe_load(f) or {}

        doc_path = Path(self.CONFIG_PATH_DOC_PROCESSING)
        if doc_path.exists():
            with open(doc_path, "r", encoding="utf-8") as f:
                self._doc_yaml = yaml.safe_load(f) or {}

    def _ensure_storage_directories(self) -> None:
        Path(self.STORAGE_ROOT).mkdir(parents=True, exist_ok=True)
        Path(self.TEMP_STORAGE_ROOT).mkdir(parents=True, exist_ok=True)

    # Dynamic Accessors for YAML-governed properties
    @property
    def allowed_extensions(self) -> List[str]:
        return self._doc_yaml.get("formats", {}).get(
            "allowed_extensions", [".pdf", ".docx", ".txt", ".csv", ".xlsx"]
        )

    @property
    def mime_mappings(self) -> Dict[str, str]:
        return self._doc_yaml.get("formats", {}).get("mime_mappings", {})

    @property
    def chunk_size_chars(self) -> int:
        return self._doc_yaml.get("segmentation", {}).get("chunk_size_chars", 1200)

    @property
    def chunk_overlap_chars(self) -> int:
        return self._doc_yaml.get("segmentation", {}).get("chunk_overlap_chars", 200)

    @property
    def min_chunk_size_chars(self) -> int:
        return self._doc_yaml.get("segmentation", {}).get("min_chunk_size_chars", 100)

    @property
    def min_page_char_threshold(self) -> int:
        return (
            self._doc_yaml.get("parsers", {})
            .get("pdf", {})
            .get("min_page_char_threshold", 40)
        )

    @property
    def requirement_categories(self) -> List[str]:
        return self._doc_yaml.get("intelligence", {}).get(
            "categories", ["eligibility", "technical", "financial", "submission", "general"]
        )

    @property
    def requirement_classifications(self) -> List[str]:
        return self._doc_yaml.get("intelligence", {}).get(
            "classifications", ["mandatory", "optional", "desirable"]
        )

    @property
    def default_workspace_id(self) -> str:
        return self._app_yaml.get("workspaces", {}).get(
            "default_id", "ws-default-0000-0000-000000000000"
        )

    @property
    def default_organization_id(self) -> str:
        return self._app_yaml.get("workspaces", {}).get(
            "default_organization_id", "org-default-0000-0000-000000000000"
        )

    @property
    def is_ai_configured(self) -> bool:
        provider = (self.AI_PROVIDER or "").strip().lower()
        if not provider or provider in ("none", "disabled", "null"):
            return False
        if provider == "mock":
            return True
        # For remote providers, require an API key or base URL
        if provider in ("openai", "gemini", "anthropic"):
            return bool(self.AI_API_KEY and self.AI_API_KEY.strip())
        if provider == "ollama":
            return bool(self.AI_API_BASE_URL and self.AI_API_BASE_URL.strip())
        return False

    def masked_dict(self) -> Dict[str, Any]:
        """Return safe settings dictionary with sensitive fields redacted."""
        data = self.model_dump()
        if data.get("AI_API_KEY"):
            data["AI_API_KEY"] = "***REDACTED***"
        if "password" in data.get("DATABASE_URL", "").lower():
            data["DATABASE_URL"] = "***REDACTED_DB_URL***"
        return data


# Singleton instance
settings = Settings()

