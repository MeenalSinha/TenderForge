# TenderForge — Phase 1: REST API Documentation

## 1. Overview & Conventions

All endpoints adhere to OpenAPI 3.1 specifications and return standard JSON response envelopes.

Base URL: `http://localhost:8000` (or configured host)
API Version Prefix: `/api/v1`

### 1.1 Universal Response Envelope
```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation completed successfully.",
  "data": { ... },
  "errors": null,
  "correlation_id": "96430093-e43a-40b4-8500-3c3ceb0a9ee8",
  "timestamp": "2026-11-05T10:45:00.000000Z"
}
```

### 1.2 Error Envelope
```json
{
  "success": false,
  "status_code": 404,
  "message": "Document with ID 'xyz' not found.",
  "data": null,
  "errors": [
    {
      "code": "DOCUMENT_NOT_FOUND",
      "detail": "Document with ID 'xyz' not found."
    }
  ],
  "correlation_id": "96430093-e43a-40b4-8500-3c3ceb0a9ee8",
  "timestamp": "2026-11-05T10:45:00.000000Z"
}
```

---

## 2. Health & Diagnostics Endpoints

### `GET /health`
- **Description**: Lightweight liveness check for orchestrators.
- **Status**: `200 OK`
```json
{
  "status": "healthy",
  "app_name": "TenderForge",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-11-05T11:40:00Z"
}
```

### `GET /ready`
- **Description**: Readiness check verifying database connection and storage writeability.
- **Status**: `200 OK` or `503 Service Unavailable`
```json
{
  "status": "ready",
  "checks": {
    "database": "connected",
    "storage": "writable",
    "ai_provider": "configured"
  },
  "timestamp": "2026-11-05T11:40:00Z"
}
```

---

## 3. Document Management Endpoints

### `POST /api/v1/documents`
- **Description**: Upload a tender specification or evidence document.
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Binary file stream (required)
  - `category`: String form field (`tender_notice`, `technical_rfp`, `financial_boq`, `evidence_cert`)
  - `workspace_id`: String form field (optional)
- **Status**: `201 Created`
- **Response**:
```json
{
  "success": true,
  "status_code": 201,
  "message": "Document uploaded and processed successfully.",
  "data": {
    "id": "808da8e4-2dbe-4284-975e-4841435c30b5",
    "workspace_id": "ws-default-0000-0000-000000000000",
    "original_filename": "National_Telecom_RFP_2026.pdf",
    "file_size_bytes": 1636,
    "mime_type": "application/pdf",
    "file_extension": ".pdf",
    "checksum_sha256": "b49d527a1df799b6...",
    "document_category": "tender_notice",
    "processing_status": "parsed",
    "ocr_required": false,
    "error_message": null,
    "created_at": "2026-11-05T11:40:00Z",
    "updated_at": "2026-11-05T11:40:00Z"
  }
}
```

### `GET /api/v1/documents`
- **Description**: List registered documents.
- **Query Parameters**: `skip` (int), `limit` (int), `category` (str), `status` (str), `workspace_id` (str).
- **Status**: `200 OK`

### `GET /api/v1/documents/{document_id}`
- **Description**: Retrieve single document metadata.
- **Status**: `200 OK`

### `GET /api/v1/documents/{document_id}/content`
- **Description**: Retrieve all extracted text segments with page numbers and character offsets.
- **Status**: `200 OK`
```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "document_id": "808da8e4-2dbe-4284-975e-4841435c30b5",
    "filename": "National_Telecom_RFP_2026.pdf",
    "processing_status": "parsed",
    "ocr_required": false,
    "total_chunks": 2,
    "chunks": [
      {
        "chunk_index": 0,
        "page_number": 1,
        "start_char": 0,
        "end_char": 223,
        "section_title": "SECTION 1: TENDER NOTICE",
        "content": "SECTION 1: TENDER NOTICE\nTender Ref: RFP-2026-001..."
      }
    ]
  }
}
```

### `GET /api/v1/documents/{document_id}/status`
- **Description**: Retrieve pipeline execution stages and history for a document.
- **Status**: `200 OK`

---

## 4. Tender & Intelligence Endpoints

### `POST /api/v1/tenders`
- **Description**: Register a new procurement tender and link documents.
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "title": "National Telecom & Cloud Infrastructure",
  "reference_number": "RFP-2026-001",
  "issuing_authority": "Ministry of Communications",
  "estimated_value": 3500000.0,
  "currency": "USD",
  "submission_deadline": "2026-12-15T17:00:00Z",
  "document_ids": ["808da8e4-2dbe-4284-975e-4841435c30b5"]
}
```
- **Status**: `201 Created`

### `GET /api/v1/tenders`
- **Description**: List registered tenders with pagination.
- **Status**: `200 OK`

### `GET /api/v1/tenders/{tender_id}`
- **Description**: Retrieve tender metadata and linked documents.
- **Status**: `200 OK`

### `POST /api/v1/tenders/{tender_id}/analyze`
- **Description**: Trigger AI intelligence extraction over linked documents.
- **Content-Type**: `application/json` (optional overrides)
- **Status**: `200 OK`
- **Response**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Tender intelligence extraction completed successfully.",
  "data": {
    "tender_id": "0fef390c-bc3f-4e65-ba44-c87ce8db9cd5",
    "analysis_status": "completed",
    "provider": "mock",
    "model": "deterministic-tender-extractor-v1",
    "total_requirements": 5,
    "requirements": [
      {
        "id": "req-uuid-1",
        "category": "eligibility",
        "classification": "mandatory",
        "description": "Annual Financial Turnover Requirement...",
        "source_page": 1,
        "source_offset": 52,
        "source_excerpt": "Minimum annual turnover of USD 2,000,000 required over the last 3 fiscal years.",
        "confidence_score": 0.92,
        "human_review_status": "unreviewed"
      }
    ]
  }
}
```

### `GET /api/v1/tenders/{tender_id}/analysis`
- **Description**: Retrieve structured requirements grouped by category (`eligibility`, `technical`, `financial`, `submission`) with auditable ProofLink references.
- **Status**: `200 OK`

