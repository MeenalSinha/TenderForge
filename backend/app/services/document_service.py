"""
Document Service: Handles validation, storage persistence, and document retrieval.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    DocumentNotFoundError,
    DuplicateDocumentError,
    FileValidationException,
)
from backend.app.core.logging import get_logger
from backend.app.core.security import (
    compute_sha256,
    sanitize_filename,
    verify_file_signature,
)
from backend.app.infrastructure.database.models import (
    Document,
    DocumentVersion,
    ExtractedContent,
    Organization,
    ProcessingJob,
    Workspace,
)
from backend.app.infrastructure.storage.local_storage import get_storage_adapter
from backend.app.services.document_processing_service import DocumentProcessingService

logger = get_logger(__name__)


def ensure_default_workspace(db: Session, workspace_id: Optional[str] = None) -> str:
    """Ensure that the target workspace exists in the database."""
    ws_id = workspace_id or settings.default_workspace_id
    existing_ws = db.query(Workspace).filter(Workspace.id == ws_id).first()
    if existing_ws:
        return ws_id

    # Create default organization if missing
    org_id = settings.default_organization_id
    existing_org = db.query(Organization).filter(Organization.id == org_id).first()
    if not existing_org:
        existing_org = Organization(
            id=org_id,
            name="Default Organization",
            slug="default-org",
        )
        db.add(existing_org)
        db.commit()

    # Create default workspace
    new_ws = Workspace(
        id=ws_id,
        organization_id=org_id,
        name="Default Workspace",
        description="System default workspace",
    )
    db.add(new_ws)
    db.commit()
    return ws_id


class DocumentService:
    """Application service managing document lifecycles."""

    def __init__(self) -> None:
        self.storage = get_storage_adapter()
        self.processing_service = DocumentProcessingService()

    def upload_and_register_document(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str,
        workspace_id: Optional[str] = None,
        category: str = "tender_notice",
        db: Session = None,
    ) -> Document:
        """Validate, persist binary, register metadata, and parse document."""
        if not file_bytes:
            raise FileValidationException("Upload rejected: File is empty (0 bytes).")

        # 1. Size Validation
        file_size = len(file_bytes)
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileValidationException(
                f"File size ({file_size} bytes) exceeds configured ceiling ({settings.MAX_UPLOAD_SIZE_BYTES} bytes)."
            )

        # 2. Filename Sanitization & Extension Validation
        clean_name = sanitize_filename(original_filename)
        ext = Path(clean_name).suffix.lower()
        if not ext or ext not in settings.allowed_extensions:
            raise FileValidationException(
                f"Extension '{ext}' is not supported. Allowed formats: {', '.join(settings.allowed_extensions)}"
            )

        # 3. Magic Bytes Inspection
        header_sample = file_bytes[:16]
        if not verify_file_signature(header_sample, ext):
            raise FileValidationException(
                f"Binary header signature check failed for extension '{ext}'."
            )

        # 4. Checksum & Duplicate Detection
        checksum = compute_sha256(file_bytes)
        target_ws_id = ensure_default_workspace(db, workspace_id)

        duplicate = (
            db.query(Document)
            .filter(
                Document.workspace_id == target_ws_id,
                Document.checksum_sha256 == checksum,
            )
            .first()
        )
        if duplicate:
            raise DuplicateDocumentError(
                f"Document with identical content checksum already exists (Document ID: {duplicate.id}).",
                details={"duplicate_id": duplicate.id, "checksum": checksum},
            )

        # 5. Secure Binary Storage
        storage_path, storage_key = self.storage.save(file_bytes, ext)

        # 6. Database Registration
        doc = Document(
            workspace_id=target_ws_id,
            original_filename=clean_name,
            storage_path=storage_path,
            mime_type=content_type or settings.mime_mappings.get(ext, "application/octet-stream"),
            file_extension=ext,
            file_size_bytes=file_size,
            checksum_sha256=checksum,
            document_category=category,
            processing_status="pending",
        )
        db.add(doc)
        db.flush()

        # Add initial version
        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            storage_path=storage_path,
            checksum_sha256=checksum,
        )
        db.add(version)
        db.commit()
        db.refresh(doc)

        logger.info(f"Registered document {doc.id} ({doc.original_filename})")

        # 7. Execute Parsing and Segmentation
        doc = self.processing_service.process_document(doc, db)
        return doc

    def get_document_by_id(self, document_id: str, db: Session) -> Document:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise DocumentNotFoundError(f"Document with ID '{document_id}' not found.")
        return doc

    def list_documents(
        self,
        db: Session,
        workspace_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Document], int]:
        target_ws = ensure_default_workspace(db, workspace_id)
        query = db.query(Document).filter(Document.workspace_id == target_ws)

        if category:
            query = query.filter(Document.document_category == category)
        if status:
            query = query.filter(Document.processing_status == status)

        total = query.count()
        docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        return docs, total

    def get_document_content(self, document_id: str, db: Session) -> Dict[str, Any]:
        doc = self.get_document_by_id(document_id, db)
        chunks = (
            db.query(ExtractedContent)
            .filter(ExtractedContent.document_id == document_id)
            .order_by(ExtractedContent.chunk_index.asc())
            .all()
        )

        return {
            "document_id": doc.id,
            "filename": doc.original_filename,
            "processing_status": doc.processing_status,
            "ocr_required": doc.ocr_required,
            "total_chunks": len(chunks),
            "chunks": [
                {
                    "chunk_index": c.chunk_index,
                    "page_number": c.page_number,
                    "start_char": c.start_char,
                    "end_char": c.end_char,
                    "section_title": c.section_title,
                    "content": c.content,
                }
                for c in chunks
            ],
        }

    def get_processing_status(self, document_id: str, db: Session) -> Dict[str, Any]:
        doc = self.get_document_by_id(document_id, db)
        jobs = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.started_at.desc())
            .all()
        )

        return {
            "document_id": doc.id,
            "processing_status": doc.processing_status,
            "error_message": doc.error_message,
            "ocr_required": doc.ocr_required,
            "jobs": [
                {
                    "id": j.id,
                    "stage": j.stage,
                    "status": j.status,
                    "error_message": j.error_message,
                    "metadata": j.metadata_json,
                    "started_at": j.started_at.isoformat() if j.started_at else None,
                    "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                }
                for j in jobs
            ],
        }

