"""
API Tests: Document Ingestion, Retrieval, Content, and Status Endpoints.
"""

from fastapi.testclient import TestClient
from tests.helpers import create_synthetic_pdf_bytes


def test_document_api_flow(client: TestClient):
    pdf_bytes = create_synthetic_pdf_bytes()

    # 1. Upload Document
    upload_resp = client.post(
        "/api/v1/documents",
        files={"file": ("tender_notice.pdf", pdf_bytes, "application/pdf")},
        data={"category": "tender_notice"},
    )
    assert upload_resp.status_code == 201
    body = upload_resp.json()
    assert body["success"] is True
    doc_id = body["data"]["id"]
    assert doc_id is not None
    assert body["data"]["original_filename"] == "tender_notice.pdf"

    # 2. Get Document Metadata
    get_resp = client.get(f"/api/v1/documents/{doc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == doc_id

    # 3. List Documents
    list_resp = client.get("/api/v1/documents")
    assert list_resp.status_code == 200
    assert list_resp.json()["data"]["total"] >= 1

    # 4. Get Document Content & Chunks
    content_resp = client.get(f"/api/v1/documents/{doc_id}/content")
    assert content_resp.status_code == 200
    content_body = content_resp.json()["data"]
    assert content_body["total_chunks"] >= 2
    assert "RFP-2026-001" in content_body["chunks"][0]["content"]

    # 5. Get Document Processing Status
    status_resp = client.get(f"/api/v1/documents/{doc_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["data"]["processing_status"] == "parsed"
    assert len(status_resp.json()["data"]["jobs"]) >= 1


def test_document_upload_invalid_extension(client: TestClient):
    resp = client.post(
        "/api/v1/documents",
        files={"file": ("malicious.exe", b"fake binary", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert resp.json()["success"] is False
    assert "not supported" in resp.json()["errors"][0]["detail"]
