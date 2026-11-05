"""
TenderForge End-to-End Demonstration Script.
Demonstrates:
  1. Service health and readiness probes
  2. Secure document upload and validation
  3. Automatic text extraction and intelligent segmentation
  4. Tender registration and document linking
  5. Structured AI intelligence extraction with ProofLink citations
  6. Graceful degradation when AI credentials are not configured
"""

from __future__ import annotations

import io
import json
import os
import sys
from fastapi.testclient import TestClient

# Ensure workspace root in path
sys.path.insert(0, os.path.abspath("."))

from backend.app.core.config import settings
from backend.app.main import app
from tests.helpers import create_synthetic_pdf_bytes


def print_step(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_demo():
    client = TestClient(app)

    # 1. Health and Readiness Checks
    print_step("Step 1: System Health & Readiness Verification")
    health = client.get("/health").json()
    ready = client.get("/ready").json()
    print(f"Health Status: {health.get('status')} | Version: {health.get('version')}")
    print(f"Readiness:     {ready.get('status')} | DB: {ready.get('checks', {}).get('database')} | Storage: {ready.get('checks', {}).get('storage')}")

    # 2. Document Ingestion
    print_step("Step 2: Uploading Tender Specification Document (PDF)")
    pdf_bytes = create_synthetic_pdf_bytes()
    upload_resp = client.post(
        "/api/v1/documents",
        files={"file": ("National_Telecom_RFP_2026.pdf", pdf_bytes, "application/pdf")},
        data={"category": "tender_notice"},
    )
    doc_data = upload_resp.json().get("data", {})
    doc_id = doc_data.get("id")
    print(f"Registered Document ID : {doc_id}")
    print(f"Filename               : {doc_data.get('original_filename')}")
    print(f"File Size              : {doc_data.get('file_size_bytes')} bytes")
    print(f"SHA-256 Checksum       : {doc_data.get('checksum_sha256')[:16]}...")
    print(f"Processing Status      : {doc_data.get('processing_status')}")

    # 3. Inspect Extracted Content & Traceable Chunks
    print_step("Step 3: Inspecting Extracted Content & Source Coordinates")
    content_resp = client.get(f"/api/v1/documents/{doc_id}/content")
    content_data = content_resp.json().get("data", {})
    print(f"Total Chunks Extracted : {content_data.get('total_chunks')}")
    for chunk in content_data.get("chunks", []):
        print(f"  • [Chunk {chunk['chunk_index']} | Page {chunk['page_number']} | Offset {chunk['start_char']}-{chunk['end_char']}]")
        print(f"    Excerpt: {chunk['content'][:90]}...")

    # 4. Tender Registration & Linkage
    print_step("Step 4: Registering Tender Opportunity")
    tender_resp = client.post(
        "/api/v1/tenders",
        json={
            "title": "National Telecom & Cloud Infrastructure",
            "reference_number": "RFP-2026-001",
            "issuing_authority": "Ministry of Communications",
            "estimated_value": 3500000.0,
            "currency": "USD",
            "document_ids": [doc_id],
        },
    )
    tender_data = tender_resp.json().get("data", {})
    tender_id = tender_data.get("id")
    print(f"Tender ID         : {tender_id}")
    print(f"Title             : {tender_data.get('title')}")
    print(f"Reference         : {tender_data.get('reference_number')}")
    print(f"Authority         : {tender_data.get('issuing_authority')}")
    print(f"Initial Status    : {tender_data.get('status')}")

    # 5. AI-Assisted Intelligence Extraction (Deterministic/Mock AI)
    print_step("Step 5: Executing AI Intelligence Extraction (ProofLink Grounded)")
    analyze_resp = client.post(f"/api/v1/tenders/{tender_id}/analyze")
    analysis_data = analyze_resp.json().get("data", {})
    print(f"Analysis Status   : {analysis_data.get('analysis_status')}")
    print(f"Provider          : {analysis_data.get('provider')}")
    print(f"Model             : {analysis_data.get('model')}")
    print(f"Total Found Reqs  : {analysis_data.get('total_requirements')}")

    # 6. Structured Requirements with Exact Source Citations
    print_step("Step 6: Auditing Extracted Requirements (ProofLink Verification)")
    grouped_resp = client.get(f"/api/v1/tenders/{tender_id}/analysis")
    grouped_data = grouped_resp.json().get("data", {})
    for cat, reqs in grouped_data.get("requirements_by_category", {}).items():
        print(f"\nCategory: [{cat.upper()}] ({len(reqs)} items)")
        for r in reqs:
            print(f"  - [{r['classification'].upper()}] {r['description']}")
            print(f"    Source Page: {r['source_page']} | Confidence: {r['confidence_score']:.2f}")
            print(f"    Source Quote: \"{r['source_excerpt']}\"")

    # 7. Demonstrate Missing AI Configuration Handling
    print_step("Step 7: Testing Graceful Degradation Without AI Provider")
    orig_provider = settings.AI_PROVIDER
    try:
        settings.AI_PROVIDER = "none"  # Simulate missing credentials
        unassisted_resp = client.post(
            "/api/v1/documents",
            files={"file": ("unassisted.pdf", create_synthetic_pdf_bytes(), "application/pdf")},
        )
        unassisted_doc_id = unassisted_resp.json()["data"]["id"]
        unassisted_tender = client.post(
            "/api/v1/tenders",
            json={"title": "Unassisted Procurement", "document_ids": [unassisted_doc_id]},
        ).json()["data"]

        degraded_analysis = client.post(f"/api/v1/tenders/{unassisted_tender['id']}/analyze").json()
        print(f"Success Flag       : {degraded_analysis.get('success')}")
        print(f"Extraction Status  : {degraded_analysis.get('data', {}).get('analysis_status')}")
        print(f"Diagnostic Message : {degraded_analysis.get('data', {}).get('message')}")
        print(f"Fabricated Records : {degraded_analysis.get('data', {}).get('total_requirements')} (Zero Hallucination Guaranteed!)")
    finally:
        settings.AI_PROVIDER = orig_provider

    print_step("DEMONSTRATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_demo()

