"""
Secure Storage Adapter for TenderForge.
"""

from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.exceptions import StorageException


class BaseStorageAdapter(ABC):
    """Abstract interface for document binary persistence."""

    @abstractmethod
    def save(self, data: bytes, extension: str, prefix: Optional[str] = None) -> Tuple[str, str]:
        """Save bytes and return (storage_path, storage_key)."""
        pass

    @abstractmethod
    def read(self, storage_path: str) -> bytes:
        """Read bytes from storage path."""
        pass

    @abstractmethod
    def delete(self, storage_path: str) -> bool:
        """Delete file at storage path."""
        pass

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check if file exists."""
        pass


class LocalStorageAdapter(BaseStorageAdapter):
    """Local filesystem storage with UUID-partitioned directories."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root = Path(root_dir or settings.STORAGE_ROOT).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, relative_or_abs_path: str) -> Path:
        """Resolve path and verify it stays within storage root boundary."""
        target = Path(relative_or_abs_path)
        if not target.is_absolute():
            target = (self.root / target).resolve()
        else:
            target = target.resolve()

        if not str(target).startswith(str(self.root)):
            raise StorageException(f"Path traversal detected: {relative_or_abs_path}")
        return target

    def save(self, data: bytes, extension: str, prefix: Optional[str] = None) -> Tuple[str, str]:
        try:
            ext = extension.lower()
            if not ext.startswith("."):
                ext = f".{ext}"

            file_id = str(uuid.uuid4())
            bucket = file_id[:2]
            target_dir = self.root / bucket
            target_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{file_id}{ext}"
            file_path = target_dir / filename

            file_path.write_bytes(data)
            relative_path = str(file_path.relative_to(self.root))
            return str(file_path), relative_path
        except Exception as e:
            raise StorageException(f"Failed to persist file: {str(e)}")

    def read(self, storage_path: str) -> bytes:
        target = self._resolve_safe_path(storage_path)
        if not target.exists() or not target.is_file():
            raise StorageException(f"Stored file not found: {storage_path}")
        return target.read_bytes()

    def delete(self, storage_path: str) -> bool:
        try:
            target = self._resolve_safe_path(storage_path)
            if target.exists() and target.is_file():
                target.unlink()
                return True
            return False
        except Exception:
            return False

    def exists(self, storage_path: str) -> bool:
        try:
            target = self._resolve_safe_path(storage_path)
            return target.exists() and target.is_file()
        except StorageException:
            return False


def get_storage_adapter() -> BaseStorageAdapter:
    """Factory returning configured storage adapter."""
    # Configurable: 'local' for Phase 1, S3 / GCS in future
    return LocalStorageAdapter()

