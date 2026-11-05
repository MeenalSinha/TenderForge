"""
API Tests: Missing AI Configuration Behavior.
Validates that document processing works 100%, but AI analysis endpoint returns
explicit 'ai_configuration_required' without fabricating data.
"""

from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.api.routes.tenders import analyze_tender, create_tender
from backend.app.api.schemas.tender import TenderCreateRequest
from backend.app.services.document_service import DocumentService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService
from tests.helpers import create_synthetic_pdf_bytes


def test_graceful_handling_when_ai_not_configured(db_session: Session, monkeypatch):
    # Temporarily set AI provider to none / empty
    monkeypatch.setattr(settings, "AI_PROVIDER", "none")
    assert settings.is_ai_configured is False

    pdf_bytes = create_synthetic_pdf_bytes()
    doc_service = DocumentService()
    tender_service = TenderService()
    intel_service = TenderIntelligenceService()

    # 1. Ingestion still works perfectly
    doc = doc_service.upload_and_register_document(
        file_bytes=pdf_bytes,
        original_filename="unassisted_tender.pdf",
        content_type="application/pdf",
        db=db_session,
    )
    doc_id = doc.id

    # 2. Content extraction still works perfectly
    from backend.app.api.routes.documents import get_document_content
    content_resp = get_document_content(document_id=doc_id, db=db_session, service=doc_service)
    assert content_resp.data.total_chunks >= 2

    # 3. Create Tender
    tender_req = TenderCreateRequest(
        title="Defense Radar Upgrade",
        document_ids=[doc_id],
    )
    tender_resp = create_tender(payload=tender_req, db=db_session, service=tender_service)
    assert tender_resp.status_code == 201
    tender_id = tender_resp.data.id

    # 4. Trigger Analysis -> Must return ai_configuration_required with 0 fake requirements
    analyze_resp = analyze_tender(tender_id=tender_id, payload=None, db=db_session, intel_service=intel_service)
    assert analyze_resp.status_code == 200
    assert analyze_resp.success is True
    assert analyze_resp.data.analysis_status == "ai_configuration_required"
    assert analyze_resp.data.total_requirements == 0
    assert len(analyze_resp.data.requirements) == 0
    assert "ai_provider" in analyze_resp.data.message.lower()
