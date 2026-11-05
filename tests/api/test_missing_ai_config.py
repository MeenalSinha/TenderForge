"""
API Tests: Missing AI Configuration Behavior.
Validates that document processing works 100%, but AI analysis endpoint returns
explicit 'ai_configuration_required' without fabricating data.
"""

from fastapi.testclient import TestClient
from backend.app.core.config import settings
from tests.helpers import create_synthetic_pdf_bytes


def test_graceful_handling_when_ai_not_configured(client: TestClient, monkeypatch):
    # Temporarily set AI provider to none / empty
    monkeypatch.setattr(settings, "AI_PROVIDER", "none")
    assert settings.is_ai_configured is False

    pdf_bytes = create_synthetic_pdf_bytes()

    # 1. Ingestion still works perfectly
    upload_resp = client.post(
        "/api/v1/documents",
        files={"file": ("unassisted_tender.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["data"]["id"]

    # 2. Content extraction still works perfectly
    content_resp = client.get(f"/api/v1/documents/{doc_id}/content")
    assert content_resp.status_code == 200
    assert content_resp.json()["data"]["total_chunks"] >= 2

    # 3. Create Tender
    tender_resp = client.post(
        "/api/v1/tenders",
        json={
            "title": "Defense Radar Upgrade",
            "document_ids": [doc_id],
        },
    )
    assert tender_resp.status_code == 201
    tender_id = tender_resp.json()["data"]["id"]

    # 4. Trigger Analysis -> Must return ai_configuration_required with 0 fake requirements
    analyze_resp = client.post(f"/api/v1/tenders/{tender_id}/analyze")
    assert analyze_resp.status_code == 200
    res = analyze_resp.json()
    assert res["success"] is True
    assert res["data"]["analysis_status"] == "ai_configuration_required"
    assert res["data"]["total_requirements"] == 0
    assert len(res["data"]["requirements"]) == 0
    assert "ai_provider" in res["data"]["message"].lower()
