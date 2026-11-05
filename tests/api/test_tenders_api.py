"""
API Tests: Tender Management and Intelligence Endpoints.
"""

from sqlalchemy.orm import Session
from backend.app.api.routes.tenders import (
    analyze_tender,
    create_tender,
    get_tender,
    get_tender_analysis,
    list_tenders,
)
from backend.app.api.schemas.tender import TenderCreateRequest
from backend.app.services.document_service import DocumentService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService
from tests.helpers import create_synthetic_pdf_bytes


def test_tender_api_flow(db_session: Session):
    pdf_bytes = create_synthetic_pdf_bytes()
    doc_service = DocumentService()
    tender_service = TenderService()
    intel_service = TenderIntelligenceService()

    # 1. Ingest document first
    doc = doc_service.upload_and_register_document(
        file_bytes=pdf_bytes,
        original_filename="rfp.pdf",
        content_type="application/pdf",
        db=db_session,
    )
    doc_id = doc.id

    # 2. Register Tender
    tender_req = TenderCreateRequest(
        title="National Grid Telecom Infrastructure",
        reference_number="NG-2026-TEL-01",
        issuing_authority="Ministry of Energy",
        estimated_value=7500000.0,
        currency="USD",
        document_ids=[doc_id],
    )
    tender_resp = create_tender(payload=tender_req, db=db_session, service=tender_service)
    assert tender_resp.status_code == 201
    tender_body = tender_resp.data
    tender_id = tender_body.id
    assert tender_body.title == "National Grid Telecom Infrastructure"

    # 3. List Tenders
    list_resp = list_tenders(skip=0, limit=20, workspace_id=None, db=db_session, service=tender_service)
    assert list_resp.status_code == 200
    assert list_resp.data.total >= 1

    # 4. Get Tender Details
    get_resp = get_tender(tender_id=tender_id, db=db_session, service=tender_service)
    assert get_resp.status_code == 200
    assert get_resp.data.id == tender_id

    # 5. Trigger Analysis (with configured mock AI)
    analyze_resp = analyze_tender(tender_id=tender_id, payload=None, db=db_session, intel_service=intel_service)
    assert analyze_resp.status_code == 200
    analysis_data = analyze_resp.data
    assert analysis_data.analysis_status == "completed"
    assert analysis_data.total_requirements > 0

    # 6. Retrieve Grouped Analysis Requirements
    grouped_resp = get_tender_analysis(tender_id=tender_id, db=db_session, service=tender_service)
    assert grouped_resp.status_code == 200
    grouped_data = grouped_resp.data
    assert grouped_data.total_requirements == analysis_data.total_requirements
    assert "eligibility" in grouped_data.requirements_by_category
