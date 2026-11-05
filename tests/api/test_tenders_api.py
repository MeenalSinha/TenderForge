"""
API Tests: Tender Management and Intelligence Endpoints.
"""

from fastapi.testclient import TestClient
from tests.helpers import create_synthetic_pdf_bytes


def test_tender_api_flow(client: TestClient):
    pdf_bytes = create_synthetic_pdf_bytes()

    # 1. Ingest document first
    doc_resp = client.post(
        "/api/v1/documents",
        files={"file": ("rfp.pdf", pdf_bytes, "application/pdf")},
    )
    assert doc_resp.status_code == 201
    doc_id = doc_resp.json()["data"]["id"]

    # 2. Register Tender
    tender_resp = client.post(
        "/api/v1/tenders",
        json={
            "title": "National Grid Telecom Infrastructure",
            "reference_number": "NG-2026-TEL-01",
            "issuing_authority": "Ministry of Energy",
            "estimated_value": 7500000.0,
            "currency": "USD",
            "document_ids": [doc_id],
        },
    )
    assert tender_resp.status_code == 201
    tender_body = tender_resp.json()["data"]
    tender_id = tender_body["id"]
    assert tender_body["title"] == "National Grid Telecom Infrastructure"

    # 3. List Tenders
    list_resp = client.get("/api/v1/tenders")
    assert list_resp.status_code == 200
    assert list_resp.json()["data"]["total"] >= 1

    # 4. Get Tender Details
    get_resp = client.get(f"/api/v1/tenders/{tender_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == tender_id

    # 5. Trigger Analysis (with configured mock AI)
    analyze_resp = client.post(f"/api/v1/tenders/{tender_id}/analyze")
    assert analyze_resp.status_code == 200
    analysis_data = analyze_resp.json()["data"]
    assert analysis_data["analysis_status"] == "completed"
    assert analysis_data["total_requirements"] > 0

    # 6. Retrieve Grouped Analysis Requirements
    grouped_resp = client.get(f"/api/v1/tenders/{tender_id}/analysis")
    assert grouped_resp.status_code == 200
    grouped_data = grouped_resp.json()["data"]
    assert grouped_data["total_requirements"] == analysis_data["total_requirements"]
    assert "eligibility" in grouped_data["requirements_by_category"]
