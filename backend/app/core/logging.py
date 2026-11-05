"""
Structured Logging & Redaction System for TenderForge.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

# Context variable for request correlation ID
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default="system"
)

SENSITIVE_KEYS = {"api_key", "password", "token", "secret", "authorization", "bearer"}


def redact_sensitive(obj: Any) -> Any:
    """Recursively mask sensitive values in dictionaries and lists."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                cleaned[k] = "***REDACTED***"
            else:
                cleaned[k] = redact_sensitive(v)
        return cleaned
    elif isinstance(obj, list):
        return [redact_sensitive(item) for item in obj]
    return obj


class StructuredJsonFormatter(logging.Formatter):
    """JSON formatter emitting structured logs with correlation IDs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include extra attributes if passed
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry["data"] = redact_sensitive(record.extra_data)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure root logger with structured JSON output."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return configured logger instance."""
    return logging.getLogger(name)

