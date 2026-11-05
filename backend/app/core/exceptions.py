"""
Domain Exceptions for TenderForge with HTTP Mapping.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class TenderForgeException(Exception):
    """Base domain exception."""

    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocumentNotFoundError(TenderForgeException):
    status_code = 404
    code = "DOCUMENT_NOT_FOUND"


class TenderNotFoundError(TenderForgeException):
    status_code = 404
    code = "TENDER_NOT_FOUND"


class DuplicateDocumentError(TenderForgeException):
    status_code = 409
    code = "DUPLICATE_DOCUMENT"


class FileValidationException(TenderForgeException):
    status_code = 400
    code = "FILE_VALIDATION_ERROR"


class ParserException(TenderForgeException):
    status_code = 422
    code = "DOCUMENT_PARSER_ERROR"


class AIConfigurationRequiredError(TenderForgeException):
    """Raised when an operation requires an AI provider but none is configured."""
    status_code = 503
    code = "AI_CONFIGURATION_REQUIRED"


class AIExecutionError(TenderForgeException):
    status_code = 502
    code = "AI_EXECUTION_ERROR"


class StorageException(TenderForgeException):
    status_code = 500
    code = "STORAGE_ERROR"


class AuthenticationException(TenderForgeException):
    status_code = 401
    code = "AUTHENTICATION_ERROR"


class AuthorizationException(TenderForgeException):
    status_code = 403
    code = "AUTHORIZATION_ERROR"


class ConflictException(TenderForgeException):
    status_code = 409
    code = "CONFLICT_ERROR"


class ValidationException(TenderForgeException):
    status_code = 400
    code = "VALIDATION_ERROR"


class EntityNotFoundException(TenderForgeException):
    status_code = 404
    code = "ENTITY_NOT_FOUND"


