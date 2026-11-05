"""Storage package."""
from backend.app.infrastructure.storage.local_storage import (
    BaseStorageAdapter,
    LocalStorageAdapter,
    get_storage_adapter,
)

__all__ = ["BaseStorageAdapter", "LocalStorageAdapter", "get_storage_adapter"]

