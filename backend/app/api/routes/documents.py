"""
Document Management REST Endpoints.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi import status as http_status
from sqlalchemy.orm import Session
from backend.app.api.dependencies import get_db, get_doc_service
from backend.app.api.schemas.common import ResponseEnvelope
from backend.app.api.schemas.document import (
    DocumentContentResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusResponse,
)
from backend.app.core.logging import correlation_id_ctx
from backend.app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=ResponseEnvelope[DocumentResponse],
    status_code=http_status.HTTP_201_CREATED,
    summary="Upload and register a tender or evidence document",
)
def upload_document(
    file: UploadFile = File(..., description="Document binary payload"),
    category: str = Form("tender_notice", description="Category: tender_notice, technical_rfp, financial_boq, evidence_cert"),
    workspace_id: Optional[str] = Form(None, description="Optional target workspace ID"),
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_doc_service),
) -> ResponseEnvelope[DocumentResponse]:
    file_bytes = file.file.read()
    doc = service.upload_and_register_document(
        file_bytes=file_bytes,
        original_filename=file.filename or "uploaded_document",
        content_type=file.content_type or "",
        workspace_id=workspace_id,
        category=category,
        db=db,
    )

    return ResponseEnvelope[DocumentResponse](
        success=True,
        status_code=http_status.HTTP_201_CREATED,
        message="Document uploaded and processed successfully.",
        data=DocumentResponse.model_validate(doc),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "",
    response_model=ResponseEnvelope[DocumentListResponse],
    summary="List registered documents with filtering and pagination",
)
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    doc_status: Optional[str] = Query(None, alias="status"),
    workspace_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_doc_service),
) -> ResponseEnvelope[DocumentListResponse]:
    docs, total = service.list_documents(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        category=category,
        status=doc_status,
    )

    return ResponseEnvelope[DocumentListResponse](
        success=True,
        status_code=http_status.HTTP_200_OK,
        message="Documents retrieved successfully.",
        data=DocumentListResponse(
            total=total,
            items=[DocumentResponse.model_validate(d) for d in docs],
        ),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{document_id}",
    response_model=ResponseEnvelope[DocumentResponse],
    summary="Retrieve document metadata by ID",
)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_doc_service),
) -> ResponseEnvelope[DocumentResponse]:
    doc = service.get_document_by_id(document_id, db)
    return ResponseEnvelope[DocumentResponse](
        success=True,
        status_code=http_status.HTTP_200_OK,
        message="Document retrieved successfully.",
        data=DocumentResponse.model_validate(doc),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{document_id}/content",
    response_model=ResponseEnvelope[DocumentContentResponse],
    summary="Retrieve extracted text blocks and segmented chunks with coordinates",
)
def get_document_content(
    document_id: str,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_doc_service),
) -> ResponseEnvelope[DocumentContentResponse]:
    content_data = service.get_document_content(document_id, db)
    return ResponseEnvelope[DocumentContentResponse](
        success=True,
        status_code=http_status.HTTP_200_OK,
        message="Document content retrieved successfully.",
        data=DocumentContentResponse.model_validate(content_data),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{document_id}/status",
    response_model=ResponseEnvelope[DocumentStatusResponse],
    summary="Retrieve processing history and job stages for document",
)
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_doc_service),
) -> ResponseEnvelope[DocumentStatusResponse]:
    status_data = service.get_processing_status(document_id, db)
    return ResponseEnvelope[DocumentStatusResponse](
        success=True,
        status_code=http_status.HTTP_200_OK,
        message="Document processing status retrieved successfully.",
        data=DocumentStatusResponse.model_validate(status_data),
        correlation_id=correlation_id_ctx.get(),
    )
