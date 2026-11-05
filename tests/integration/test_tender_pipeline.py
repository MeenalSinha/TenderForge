"""
Integration Tests: Tender Registration, Linkage, and AI Intelligence Extraction.
"""

import asyncio
from sqlalchemy.orm import Session
from backend.app.infrastructure.database.models import ExtractionResult, TenderRequirement
from backend.app.services.document_service import DocumentService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService
from tests.helpers import create_synthetic_pdf_bytes


def test_tender_pipeline_with_mock_ai(db_session: Session):
    async def _run():
        doc_service = DocumentService()
        tender_service = TenderService()
        intel_service = TenderIntelligenceService()

        # 1. Ingest tender PDF
        pdf_bytes = create_synthetic_pdf_bytes()
        doc = doc_service.upload_and_register_document(
            file_bytes=pdf_bytes,
            original_filename="Tender_Doc.pdf",
            content_type="application/pdf",
            db=db_session,
        )

        # 2. Register Tender & link document
        tender = tender_service.create_tender(
            title="Procurement of Enterprise Server Infrastructure",
            reference_number="RFP-2026-001",
            estimated_value=250000.0,
            document_ids=[doc.id],
            db=db_session,
        )

        assert tender.id is not None
        assert tender.status == "draft"

        # 3. Analyze Tender
        analysis = await intel_service.analyze_tender(
            tender_id=tender.id,
            db=db_session,
        )

        assert analysis["analysis_status"] == "completed"
        assert analysis["total_requirements"] > 0

        # 4. Verify Database Persistence of Requirements & ProofLink data
        reqs = db_session.query(TenderRequirement).filter(TenderRequirement.tender_id == tender.id).all()
        assert len(reqs) == analysis["total_requirements"]
        for r in reqs:
            assert r.source_document_id == doc.id
            assert r.source_excerpt is not None
            assert len(r.source_excerpt) > 0
            assert r.confidence_score > 0.0

        # 5. Verify ExtractionResult audit record
        ext_result = db_session.query(ExtractionResult).filter(ExtractionResult.tender_id == tender.id).first()
        assert ext_result is not None
        assert ext_result.validation_status == "valid"

    asyncio.run(_run())
