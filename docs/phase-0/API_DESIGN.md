# TenderForge — Phase 0: REST API Design & Contracts

## 1. Design Standards

The TenderForge REST API adheres to modern RESTful principles, OpenAPI 3.1 specifications, and strict input/output validation via Pydantic v2.

### 1.1 Universal Response Envelope
All API endpoints (except binary downloads and health checks) return a standard JSON envelope:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation completed successfully.",
  "data": { ... },
  "errors": null,
  "correlation_id": "c7a8b84e-3c9f-4f27-8911-3918a28f7d9a",
  "timestamp": "2026-11-05T10:45:00.000000Z"
}
```

### 1.2 Error Envelope
When an error occurs, the response maintains the standard structure with a non-null `errors` object:

```json
{
  "success": false,
  "status_code": 404,
  "message": "Document not found.",
  "data": null,
  "errors": [
    {
      "code": "DOCUMENT_NOT_FOUND",
      "detail": "Document with ID 'c7a8b84e-3c9f-4f27-8911-3918a28f7d9a' does not exist."
    }
  ],
  "correlation_id": "c7a8b84e-3c9f-4f27-8911-3918a28f7d9a",
  "timestamp": "2026-11-05T10:45:00.000000Z"
}
```

---

## 2. API Endpoints Specification

### 2.1 Health & Diagnostics

#### `GET /health`
- **Purpose**: Liveness probe for load balancers and orchestrators.
- **Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-11-05T10:45:00Z"
}
```

#### `GET /ready`
- **Purpose**: Readiness probe checking database connectivity and storage directory writeability.
- **Response**: `200 OK` or `503 Service Unavailable`
```json
{
  "status": "ready",
  "database": "connected",
  "storage": "writable",
  "ai_provider": "configured" // or "not_configured" (ready=true nonetheless)
}
```

---

### 2.2 Document Management Endpoints

#### `POST /api/v1/documents`
- **Purpose**: Upload and ingest a tender or evidence document.
- **Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `file`: UploadFile (binary, required)
  - `category`: string (optional, default `"tender_notice"`)
  - `workspace_id`: string (optional, defaults to default workspace)
- **Validation Rules**:
  - Max size: `MAX_UPLOAD_SIZE_BYTES` (e.g., 52,428,800 bytes).
  - Allowed extensions: `.pdf`, `.docx`, `.txt`, `.csv`, `.xlsx`.
  - Signature check: magic bytes verification.
- **Response**: `201 Created`
```json
{
  "success": true,
  "status_code": 201,
  "message": "Document uploaded and registered successfully.",
  "data": {
    "id": "doc-uuid-1234",
    "original_filename": "Defense_Procurement_RFP.pdf",
    "file_size_bytes": 1048576,
    "mime_type": "application/pdf",
    "file_extension": ".pdf",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "document_category": "tender_notice",
    "processing_status": "parsed",
    "ocr_required": false,
    "created_at": "2026-11-05T10:45:00Z"
  }
}
```

#### `GET /api/v1/documents`
- **Purpose**: List documents with pagination and filtering.
- **Query Parameters**:
  - `skip`: int (default 0)
  - `limit`: int (default 20, max 100)
  - `category`: string (optional)
  - `status`: string (optional)
- **Response**: `200 OK`

#### `GET /api/v1/documents/{document_id}`
- **Purpose**: Retrieve single document metadata.
- **Response**: `200 OK` or `404 Not Found`

#### `GET /api/v1/documents/{document_id}/content`
- **Purpose**: Retrieve extracted text blocks and segmented chunks with page and offset coordinates.
- **Response**: `200 OK`
```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "document_id": "doc-uuid-1234",
    "total_chunks": 12,
    "total_pages": 4,
    "chunks": [
      {
        "chunk_index": 0,
        "page_number": 1,
        "start_char": 0,
        "end_char": 820,
        "section_title": "Section 1: Scope of Work",
        "content": "..."
      }
    ]
  }
}
```

#### `GET /api/v1/documents/{document_id}/status`
- **Purpose**: Poll or inspect processing job history and current status.
- **Response**: `200 OK`

---

### 2.3 Tender Management Endpoints

#### `POST /api/v1/tenders`
- **Purpose**: Register a tender record and optionally link existing document IDs.
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "reference_number": "RFP-2026-DEF-001",
  "title": "Supply of Secure Communications Equipment",
  "issuing_authority": "Ministry of Communications",
  "procurement_category": "Hardware & Systems",
  "estimated_value": 4500000.0,
  "currency": "USD",
  "submission_deadline": "2026-12-15T17:00:00Z",
  "document_ids": ["doc-uuid-1234"]
}
```
- **Response**: `201 Created`

#### `GET /api/v1/tenders`
- **Purpose**: List registered tenders with pagination.
- **Response**: `200 OK`

#### `GET /api/v1/tenders/{tender_id}`
- **Purpose**: Retrieve tender record, linked documents, and extraction overview.
- **Response**: `200 OK`

#### `POST /api/v1/tenders/{tender_id}/analyze`
- **Purpose**: Initiate AI-assisted tender intelligence extraction over linked documents.
- **Content-Type**: `application/json`
- **Request Body** (optional configuration overrides):
```json
{
  "force_reanalysis": false,
  "categories": ["eligibility", "technical", "financial", "submission"]
}
```
- **Behavior**:
  - If a valid AI provider is configured: Ingests normalized chunks, executes prompt, parses structured requirements, records exact source citations, persists to `tender_requirements`, and returns `200 OK`.
  - If AI provider is NOT configured: Completes metadata linking, records an audit entry with `validation_status="ai_configuration_required"`, and returns `200 OK` (or `202 Accepted`) with a clear message explaining that document processing succeeded but AI intelligence extraction requires runtime credentials. **Zero fabricated results are returned.**

#### `GET /api/v1/tenders/{tender_id}/analysis`
- **Purpose**: Retrieve structured requirements extracted from the tender, organized by category with source references.
- **Response**: `200 OK`
```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "tender_id": "tender-uuid-5678",
    "analysis_status": "completed",
    "total_requirements": 14,
    "requirements_by_category": {
      "eligibility": [
        {
          "id": "req-uuid-001",
          "category": "eligibility",
          "classification": "mandatory",
          "description": "Bidder must have an average annual financial turnover of at least USD 2,000,000 over the past 3 audited fiscal years.",
          "source_page": 4,
          "source_offset": 1240,
          "source_excerpt": "Clause 4.1: Average annual turnover during the last 3 financial years ending 31st March must be minimum USD 2.0 Million.",
          "confidence_score": 0.95,
          "human_review_status": "unreviewed"
        }
      ],
      "technical": [ ... ],
      "financial": [ ... ],
      "submission": [ ... ]
    }
  }
}
```

