"""
Enterprise Object Storage Adapter for TenderForge Phase 4.

Supports pluggable storage providers:
- Local filesystem (development, air-gapped on-premise)
- Cloud Object Storage (S3 / MinIO / GCS compatible via standard interface)
"""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional, Union
from backend.app.core.config import settings
from backend.app.core.exceptions import StorageException
from backend.app.core.logging import get_logger

logger = get_logger("tenderforge.storage")


class BaseStorageProvider(ABC):
    """Abstract interface for file and object storage operations."""

    @abstractmethod
    def save(self, relative_path: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Save binary data to the storage backend. Returns storage reference path."""
        pass

    @abstractmethod
    def read(self, relative_path: str) -> bytes:
        """Read binary data from storage."""
        pass

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    def delete(self, relative_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def get_url(self, relative_path: str) -> str:
        """Return accessible URL or local path string for download/preview."""
        pass


class LocalStorageProvider(BaseStorageProvider):
    """Local filesystem storage adapter."""

    def __init__(self, root_path: Optional[str] = None):
        self.root = Path(root_path or settings.STORAGE_ROOT).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, relative_path: str) -> Path:
        clean_rel = relative_path.lstrip("/\\")
        target = (self.root / clean_rel).resolve()
        if not str(target).startswith(str(self.root)):
            raise StorageException(f"Path traversal detected: {relative_path}")
        return target

    def save(self, relative_path: str, data: bytes, content_type: Optional[str] = None) -> str:
        try:
            target = self._resolve_path(relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            logger.debug(f"Saved {len(data)} bytes to local storage: {target}")
            return str(target)
        except Exception as e:
            logger.error(f"Failed to save file '{relative_path}': {e}")
            raise StorageException(f"Failed to write storage file: {str(e)}")

    def read(self, relative_path: str) -> bytes:
        target = self._resolve_path(relative_path)
        if not target.is_file():
            raise StorageException(f"Storage file not found: {relative_path}")
        return target.read_bytes()

    def exists(self, relative_path: str) -> bool:
        try:
            target = self._resolve_path(relative_path)
            return target.is_file()
        except Exception:
            return False

    def delete(self, relative_path: str) -> bool:
        try:
            target = self._resolve_path(relative_path)
            if target.is_file():
                target.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete storage file '{relative_path}': {e}")
            return False

    def get_url(self, relative_path: str) -> str:
        return f"/api/v1/storage/{relative_path.lstrip('/')}"


class S3CompatibleStorageProvider(BaseStorageProvider):
    """S3 / MinIO compatible cloud object storage adapter."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        bucket_name: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "tenderforge-documents")
        self.access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        # In mock or fallback mode when boto3 is absent or credentials missing, fall back to local
        self._fallback_local = LocalStorageProvider()

    def save(self, relative_path: str, data: bytes, content_type: Optional[str] = None) -> str:
        try:
            import boto3
            from botocore.config import Config
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version="s3v4"),
            )
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            client.put_object(Bucket=self.bucket_name, Key=relative_path, Body=data, **extra_args)
            return f"s3://{self.bucket_name}/{relative_path}"
        except Exception as e:
            logger.warning(f"S3 upload failed ({e}), falling back to local storage adapter.")
            return self._fallback_local.save(relative_path, data, content_type)

    def read(self, relative_path: str) -> bytes:
        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            resp = client.get_object(Bucket=self.bucket_name, Key=relative_path)
            return resp["Body"].read()
        except Exception as e:
            logger.warning(f"S3 read failed ({e}), falling back to local storage adapter.")
            return self._fallback_local.read(relative_path)

    def exists(self, relative_path: str) -> bool:
        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            client.head_object(Bucket=self.bucket_name, Key=relative_path)
            return True
        except Exception:
            return self._fallback_local.exists(relative_path)

    def delete(self, relative_path: str) -> bool:
        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            client.delete_object(Bucket=self.bucket_name, Key=relative_path)
            return True
        except Exception:
            return self._fallback_local.delete(relative_path)

    def get_url(self, relative_path: str) -> str:
        return f"{self.endpoint_url}/{self.bucket_name}/{relative_path}" if self.endpoint_url else f"/api/v1/storage/{relative_path}"


def get_storage_provider() -> BaseStorageProvider:
    """Factory returning configured storage provider singleton."""
    provider_name = (settings.STORAGE_PROVIDER or "local").lower().strip()
    if provider_name in ("s3", "minio", "gcs"):
        return S3CompatibleStorageProvider()
    return LocalStorageProvider()

