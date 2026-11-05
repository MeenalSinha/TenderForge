"""
Tender Intelligence Service: Orchestrates AI extraction, validation, and provenance recording.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AIConfigurationRequiredError,
    FileValidationException,
    TenderNotFoundError,
)
from backend.app.core.logging import get_logger
from backend.app.domain.intelligence.models import (
    ExtractedRequirement,
    StructuredTenderIntelligence,
)
from backend.app.infrastructure.ai.factory import get_ai_provider
from backend.app.infrastructure.database.models import (
    ExtractedContent,
    ExtractionResult,
    Tender,
    TenderDocument,
    TenderRequirement,
)

logger = get_logger(__name__)


class TenderIntelligenceService:
    """Coordinates AI extraction pipelines and preserves requirement provenance."""

    def __init__(self) -> None:
        pass

    def _load_prompt_template(self) -> str:
        prompt_file = Path(settings.PROMPTS_DIR) / "tender_analysis_v1.txt"
        if not prompt_file.exists():
            return "You are TenderForge Intelligence Extractor. Extract requirements from: {document_content}"
        return prompt_file.read_text(encoding="utf-8")

    async def analyze_tender(
        self,
        tender_id: str,
        db: Session = None,
        force_reanalysis: bool = False,
    ) -> Dict[str, Any]:
        """Run intelligence extraction against linked documents."""
        # Support either argument order (db, tender_id) or (tender_id, db)
        if isinstance(tender_id, Session):
            db, tender_id = tender_id, db

        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise TenderNotFoundError(f"Tender '{tender_id}' not found.")

        # 1. Fetch linked documents
        linked_docs = (
            db.query(TenderDocument)
            .filter(TenderDocument.tender_id == tender_id)
            .all()
        )
        if not linked_docs:
            raise FileValidationException(
                "Cannot analyze tender: No documents are linked to this tender. "
                "Upload a tender document and link it to the tender before requesting analysis."
            )

        doc_ids = [l.document_id for l in linked_docs]

        # 2. Gather extracted content chunks
        chunks = (
            db.query(ExtractedContent)
            .filter(ExtractedContent.document_id.in_(doc_ids))
            .order_by(ExtractedContent.chunk_index.asc())
            .limit(settings.max_context_chunks_for_ai if hasattr(settings, "max_context_chunks_for_ai") else 30)
            .all()
        )

        if not chunks:
            raise FileValidationException(
                "Linked documents have not yielded extractable text. Check document status or OCR requirement."
            )

        combined_text = "\n\n".join(
            [f"[Page {c.page_number or 1} - {c.section_title or 'Section'}]\n{c.content}" for c in chunks]
        )

        primary_doc_id = doc_ids[0]

        # 3. Check AI Provider Configuration
        if not settings.is_ai_configured:
            # Graceful degradation without active AI keys: record transparent status, NO fake data
            result = ExtractionResult(
                tender_id=tender.id,
                provider_id="none",
                model_id="not_configured",
                prompt_version="tender_analysis_v1",
                raw_response=None,
                structured_data=None,
                validation_status="ai_configuration_required",
                error_message=(
                    "AI intelligence extraction requires an active AI provider. "
                    "All document parsing, text extraction, and segmentation steps completed successfully. "
                    "Configure AI_PROVIDER and valid credentials (e.g. AI_API_KEY) in .env to perform AI analysis."
                ),
                execution_timestamp=datetime.now(timezone.utc),
            )
            db.add(result)
            tender.status = "pending_ai_configuration"
            db.commit()

            return {
                "tender_id": tender.id,
                "analysis_status": "ai_configuration_required",
                "message": result.error_message,
                "total_requirements": 0,
                "requirements": [],
            }

        # 4. Invoke Configured AI Provider
        ai_provider = get_ai_provider()
        prompt_tmpl = self._load_prompt_template()

        tender.status = "analyzing"
        db.commit()

        structured, raw_meta = await ai_provider.extract_intelligence(
            document_text=combined_text,
            prompt_template=prompt_tmpl,
            parameters={},
        )

        # 5. Clear previous requirements if reanalyzing
        if force_reanalysis:
            db.query(TenderRequirement).filter(TenderRequirement.tender_id == tender.id).delete()

        # 6. Persist extracted requirements with exact source provenance
        created_reqs: List[TenderRequirement] = []
        for req in structured.requirements:
            db_req = TenderRequirement(
                tender_id=tender.id,
                source_document_id=primary_doc_id,
                category=req.category,
                classification=req.classification,
                description=req.description,
                source_page=req.source_page or 1,
                source_offset=req.source_offset or 0,
                source_excerpt=req.source_excerpt,
                confidence_score=req.confidence_score,
                human_review_status="unreviewed",
                extra_metadata=req.extra_metadata,
            )
            db.add(db_req)
            created_reqs.append(db_req)

        # 7. Update Tender metadata if not already filled
        if structured.general_info:
            if not tender.reference_number and structured.general_info.reference_number:
                tender.reference_number = structured.general_info.reference_number
            if not tender.issuing_authority and structured.general_info.issuing_authority:
                tender.issuing_authority = structured.general_info.issuing_authority
            if not tender.estimated_value and structured.general_info.estimated_value:
                tender.estimated_value = structured.general_info.estimated_value

        # 8. Record Extraction Result
        result = ExtractionResult(
            tender_id=tender.id,
            provider_id=ai_provider.provider_id,
            model_id=ai_provider.model_id,
            prompt_version="tender_analysis_v1",
            raw_response=raw_meta,
            structured_data=structured.model_dump(),
            validation_status="valid",
            execution_timestamp=datetime.now(timezone.utc),
        )
        db.add(result)

        tender.status = "analyzed"
        db.commit()
        db.refresh(tender)

        logger.info(f"Tender {tender.id} analysis complete. Extracted {len(created_reqs)} requirements.")

        return {
            "tender_id": tender.id,
            "analysis_status": "completed",
            "provider": ai_provider.provider_id,
            "model": ai_provider.model_id,
            "total_requirements": len(created_reqs),
            "requirements": [
                {
                    "id": r.id,
                    "category": r.category,
                    "classification": r.classification,
                    "description": r.description,
                    "source_page": r.source_page,
                    "source_offset": r.source_offset,
                    "source_excerpt": r.source_excerpt,
                    "confidence_score": r.confidence_score,
                    "human_review_status": r.human_review_status,
                }
                for r in created_reqs
            ],
        }

    def analyze_tender_sync(
        self,
        tender_id: str,
        db: Session = None,
        force_reanalysis: bool = False,
    ) -> Dict[str, Any]:
        """Synchronous execution wrapper for analyze_tender."""
        import asyncio
        if isinstance(tender_id, Session):
            db, tender_id = tender_id, db
        return asyncio.run(self.analyze_tender(tender_id, db, force_reanalysis))

