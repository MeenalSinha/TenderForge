"""
Integration Tests: Full Document Ingestion and Segmentation Pipeline.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.core.exceptions import DuplicateDocumentError, FileValidationException
from backend.app.infrastructure.database.models import Document, ExtractedContent
from backend.app.services.document_service import DocumentService
from tests.helpers import create_synthetic_pdf_bytes


def test_document_full_ingestion_pipeline(db_session: Session):
    service = DocumentService()
    pdf_bytes = create_synthetic_pdf_bytes()

    # 1. Ingest valid PDF
    doc = service.upload_and_register_document(
        file_bytes=pdf_bytes,
        original_filename="Tender_Specifications_2026.pdf",
        content_type="application/pdf",
        category="tender_notice",
        db=db_session,
    )

    assert doc.id is not None
    assert doc.processing_status == "parsed"
    assert doc.ocr_required is False
    assert doc.file_size_bytes == len(pdf_bytes)

    # 2. Verify Database Records
    db_doc = db_session.query(Document).filter(Document.id == doc.id).first()
    assert db_doc is not None
    assert db_doc.checksum_sha256 is not None

    # 3. Verify Extracted Chunks
    chunks = db_session.query(ExtractedContent).filter(ExtractedContent.document_id == doc.id).all()
    assert len(chunks) >= 2
    assert any("RFP-2026-001" in c.content for c in chunks)


def test_document_duplicate_rejection(db_session: Session):
    service = DocumentService()
    pdf_bytes = create_synthetic_pdf_bytes()

    # First upload succeeds
    service.upload_and_register_document(
        file_bytes=pdf_bytes,
        original_filename="Doc_A.pdf",
        content_type="application/pdf",
        db=db_session,
    )

    # Duplicate upload is rejected
    with pytest.raises(DuplicateDocumentError):
        service.upload_and_register_document(
            file_bytes=pdf_bytes,
            original_filename="Doc_Duplicate.pdf",
            content_type="application/pdf",
            db=db_session,
        )
