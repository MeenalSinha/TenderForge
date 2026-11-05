"""API schemas package."""
from backend.app.api.schemas.common import ErrorDetail, ResponseEnvelope
from backend.app.api.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentContentResponse,
    DocumentStatusResponse,
)
from backend.app.api.schemas.tender import (
    TenderCreateRequest,
    TenderResponse,
    TenderListResponse,
    TenderAnalysisRequest,
    TenderAnalysisResponse,
    TenderRequirementsGroupedResponse,
)

__all__ = [
    "ErrorDetail",
    "ResponseEnvelope",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentContentResponse",
    "DocumentStatusResponse",
    "TenderCreateRequest",
    "TenderResponse",
    "TenderListResponse",
    "TenderAnalysisRequest",
    "TenderAnalysisResponse",
    "TenderRequirementsGroupedResponse",
]

