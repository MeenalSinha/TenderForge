"""
Standardized API Envelope and Error Schemas.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    detail: str = Field(..., description="Human-readable error explanation")


class ResponseEnvelope(BaseModel, Generic[DataT]):
    """Standardized API response wrapper."""

    success: bool = Field(True, description="Indicates if operation succeeded")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Operation completed successfully.", description="Summary message")
    data: Optional[DataT] = Field(None, description="Response payload")
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of errors if failed")
    correlation_id: str = Field("system", description="Request tracking correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

