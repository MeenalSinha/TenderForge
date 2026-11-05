"""
Security Utilities: Path sanitization, magic bytes verification, cryptographic hashing.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Tuple
from backend.app.core.exceptions import FileValidationException

# Binary signatures (magic numbers)
MAGIC_SIGNATURES = {
    ".pdf": [b"%PDF"],
    ".docx": [b"PK\x03\x04"],
    ".xlsx": [b"PK\x03\x04"],
    ".csv": [],  # plain text, handled via text decoder
    ".txt": [],  # plain text
}


def sanitize_filename(filename: str) -> str:
    """Strip path separators, null bytes, and non-safe characters."""
    if not filename:
        return "unnamed_document"
    # Take basename only
    base = Path(filename).name
    # Strip null bytes and control chars
    base = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)
    # Strip directory navigation patterns
    base = base.replace("..", "").replace("/", "").replace("\\", "")
    # Keep alphanumeric, dot, underscore, dash, space
    clean = re.sub(r"[^\w\.\-\s]", "_", base).strip()
    return clean or "sanitized_document"


def compute_sha256(data: bytes) -> str:
    """Compute standard SHA-256 hex digest for binary content."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def verify_file_signature(header: bytes, extension: str) -> bool:
    """Verify that file's leading bytes match expected binary signature."""
    ext = extension.lower()
    if ext not in MAGIC_SIGNATURES:
        return False
    expected_signatures = MAGIC_SIGNATURES[ext]
    if not expected_signatures:
        # Text based formats (txt, csv)
        return True
    return any(header.startswith(sig) for sig in expected_signatures)

