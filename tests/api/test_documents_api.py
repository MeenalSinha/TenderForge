"""
API Tests: Document Ingestion, Retrieval, Content, and Status Endpoints.
"""

import io
import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.datastructures import Headers
from backend.app.api.routes.documents import (
    get_document,
    get_document_content,
    get_document_status,
    list_documents,
    upload_document,
)
from backend.app.core.exceptions import FileValidationException
from backend.app.services.document_service import DocumentService
from tests.helpers import create_synthetic_pdf_bytes


def test_document_api_flow(db_session: Session):
    pdf_bytes = create_synthetic_pdf_bytes()
    doc_service = DocumentService()

    # 1. Upload Document
    upload_file = UploadFile(
        file=io.BytesIO(pdf_bytes),
        filename="tender_notice.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )
    upload_resp = upload_document(
        file=upload_file,
        category="tender_notice",
        workspace_id=None,
        db=db_session,
        service=doc_service,
    )
    assert upload_resp.status_code == 201
    assert upload_resp.success is True
    doc_id = upload_resp.data.id
    assert doc_id is not None
    assert upload_resp.data.original_filename == "tender_notice.pdf"

    # 2. Get Document Metadata
    get_resp = get_document(document_id=doc_id, db=db_session, service=doc_service)
    assert get_resp.status_code == 200
    assert get_resp.data.id == doc_id

    # 3. List Documents
    list_resp = list_documents(
        skip=0,
        limit=20,
        category=None,
        doc_status=None,
        workspace_id=None,
        db=db_session,
        service=doc_service,
    )
    assert list_resp.status_code == 200
    assert list_resp.data.total >= 1

    # 4. Get Document Content & Chunks
    content_resp = get_document_content(document_id=doc_id, db=db_session, service=doc_service)
    assert content_resp.status_code == 200
    content_body = content_resp.data
    assert content_body.total_chunks >= 2
    assert "RFP-2026-001" in content_body.chunks[0].content

    # 5. Get Document Processing Status
    status_resp = get_document_status(document_id=doc_id, db=db_session, service=doc_service)
    assert status_resp.status_code == 200
    assert status_resp.data.processing_status == "parsed"
    assert len(status_resp.data.jobs) >= 1


def test_document_upload_invalid_extension(db_session: Session):
    doc_service = DocumentService()
    upload_file = UploadFile(
        file=io.BytesIO(b"fake binary"),
        filename="malicious.exe",
        headers=Headers({"content-type": "application/octet-stream"}),
    )
    with pytest.raises(FileValidationException) as excinfo:
        upload_document(
            file=upload_file,
            category="tender_notice",
            workspace_id=None,
            db=db_session,
            service=doc_service,
        )
    assert "not supported" in str(excinfo.value).lower()
