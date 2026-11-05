"""
Document Processing Service: Coordinates parsing, normalization, and segmentation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import ParserException
from backend.app.core.logging import get_logger
from backend.app.domain.documents.segmentation import IntelligentSegmenter
from backend.app.infrastructure.database.models import (
    Document,
    ExtractedContent,
    ProcessingJob,
)
from backend.app.infrastructure.parsers.registry import parser_registry
from backend.app.infrastructure.storage.local_storage import get_storage_adapter

logger = get_logger(__name__)


class DocumentProcessingService:
    """Orchestrates parsing and segmentation pipelines."""

    def __init__(self) -> None:
        self.storage = get_storage_adapter()
        self.segmenter = IntelligentSegmenter()

    def process_document(self, document: Document, db: Session) -> Document:
        """Execute parsing and segmentation pipeline synchronously."""
        job = ProcessingJob(
            document_id=document.id,
            stage="parsing_and_segmentation",
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.commit()

        try:
            # 1. Read binary content
            file_bytes = self.storage.read(document.storage_path)

            # 2. Select parser from registry
            parser = parser_registry.get_parser(document.file_extension)
            document.parser_name = parser.name
            document.parser_version = parser.version

            # 3. Parse content
            parsed_doc = parser.parse(file_bytes, document.original_filename)
            document.ocr_required = parsed_doc.ocr_required

            # 4. Segment content into chunks
            segments = self.segmenter.segment_parsed_document(parsed_doc)

            # 5. Persist extracted chunks
            # Clean old chunks if re-processing
            db.query(ExtractedContent).filter(ExtractedContent.document_id == document.id).delete()

            for seg in segments:
                db_chunk = ExtractedContent(
                    document_id=document.id,
                    chunk_index=seg.chunk_index,
                    page_number=seg.page_number,
                    start_char=seg.start_char,
                    end_char=seg.end_char,
                    section_title=seg.section_title,
                    content=seg.content,
                )
                db.add(db_chunk)

            # 6. Mark success
            document.processing_status = "parsed"
            document.error_message = None
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            job.metadata_json = {
                "total_pages": parsed_doc.total_pages,
                "total_chunks": len(segments),
                "warnings": parsed_doc.warnings,
                "statistics": parsed_doc.statistics,
            }

            db.commit()
            db.refresh(document)
            logger.info(f"Document {document.id} parsed and segmented successfully ({len(segments)} chunks).")
            return document

        except Exception as e:
            db.rollback()
            err_msg = str(e)
            logger.error(f"Failed processing document {document.id}: {err_msg}", exc_info=True)
            document.processing_status = "failed"
            document.error_message = err_msg

            job.status = "failed"
            job.error_message = err_msg
            job.completed_at = datetime.now(timezone.utc)

            db.commit()
            raise ParserException(f"Document processing failed: {err_msg}")

