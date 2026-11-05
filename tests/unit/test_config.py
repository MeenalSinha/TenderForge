"""
Unit Tests: Centralized Configuration Engine.
"""

from backend.app.core.config import Settings, settings


def test_settings_load_defaults():
    assert settings.APP_NAME == "TenderForge"
    assert settings.ENVIRONMENT in ["development", "testing", "production"]
    assert settings.MAX_UPLOAD_SIZE_BYTES > 0
    assert len(settings.allowed_extensions) > 0
    assert ".pdf" in settings.allowed_extensions
    assert ".docx" in settings.allowed_extensions


def test_settings_masked_dict():
    masked = settings.masked_dict()
    assert masked.get("AI_API_KEY") in [None, "", "***REDACTED***"]
    if "password" in settings.DATABASE_URL.lower():
        assert masked["DATABASE_URL"] == "***REDACTED_DB_URL***"


def test_yaml_config_accessors():
    assert settings.chunk_size_chars >= 200
    assert settings.chunk_overlap_chars >= 0
    assert "eligibility" in settings.requirement_categories
    assert "mandatory" in settings.requirement_classifications
