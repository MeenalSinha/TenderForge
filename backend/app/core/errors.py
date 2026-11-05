"""
Centralized Error Aliases and Domain Exception Extensions.
"""

from backend.app.core.exceptions import (
    AIConfigurationRequiredError,
    AIExecutionError,
    DocumentNotFoundError,
    DuplicateDocumentError,
    FileValidationException,
    ParserException,
    StorageException,
    TenderForgeException,
    TenderNotFoundError,
)


class EntityNotFoundError(TenderForgeException):
    status_code = 404
    code = "ENTITY_NOT_FOUND"


class SecurityError(TenderForgeException):
    status_code = 403
    code = "SECURITY_VIOLATION"


class WorkflowError(TenderForgeException):
    status_code = 400
    code = "INVALID_WORKFLOW_TRANSITION"


class InvalidFileError(FileValidationException):
    pass


class DocumentParsingError(ParserException):
    pass


__all__ = [
    "TenderForgeException",
    "EntityNotFoundError",
    "DocumentNotFoundError",
    "TenderNotFoundError",
    "DuplicateDocumentError",
    "FileValidationException",
    "InvalidFileError",
    "ParserException",
    "DocumentParsingError",
    "AIConfigurationRequiredError",
    "AIExecutionError",
    "StorageException",
    "SecurityError",
    "WorkflowError",
]
