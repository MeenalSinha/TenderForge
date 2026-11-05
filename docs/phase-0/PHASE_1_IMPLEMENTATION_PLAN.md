# TenderForge — Phase 0: Phase 1 Implementation Plan

## 1. Plan Overview & Execution Principles

This implementation plan translates the Phase 0 architecture into concrete, testable software engineering tasks for **Phase 1: Core Backend & Intelligent Document Processing**.

---

## 2. Work Breakdown Structure (WBS)

```
Phase 1: Core Backend & Intelligent Document Processing
├── WBS 1.1: Backend Foundation & Directory Architecture
├── WBS 1.2: Centralized Configuration & Environment Management
├── WBS 1.3: Database Models & Alembic Migration Engine
├── WBS 1.4: Storage Adapter & Secure Document Ingestion
├── WBS 1.5: Modular Document Parser Infrastructure (PDF, DOCX, TXT, Excel/CSV)
├── WBS 1.6: Text Normalization & Intelligent Traceable Segmentation
├── WBS 1.7: Tender Intelligence Schema & AI Provider Abstraction
├── WBS 1.8: Application Services Layer
├── WBS 1.9: REST API Endpoints & OpenAPI Contracts
├── WBS 1.10: Future Switch Integration Contracts & Interfaces
├── WBS 1.11: Observability, Logging & Error Handling Middleware
├── WBS 1.12: Automated Test Harness (Unit, Integration, API, Security)
└── WBS 1.13: Documentation & Verification
```

---

## 3. Detailed Task Specifications

### WBS 1.1 — Backend Foundation & Directory Architecture
- **Objective**: Establish the modular codebase structure, FastAPI application factory, and dependency injection setup.
- **Affected Components**: `backend/app/main.py`, `backend/app/core/`, `backend/app/api/`.
- **Dependencies**: Python 3.14 runtime, FastAPI, Uvicorn.
- **Completion Condition**: Application boots via Uvicorn; `/health` returns `200 OK`.

### WBS 1.2 — Centralized Configuration & Environment Management
- **Objective**: Implement `pydantic-settings` loader reading from `.env` and YAML configuration files.
- **Affected Components**: `backend/app/core/config.py`, `config/application.example.yaml`, `config/document_processing.example.yaml`, `.env.example`.
- **Requirements**: Zero hardcoded values; clear startup validation errors if mandatory fields are missing.
- **Testing**: Unit tests validating YAML loading, environment overrides, and missing-key behavior.

### WBS 1.3 — Database Models & Alembic Migration Engine
- **Objective**: Implement SQLAlchemy 2.0 declarative models for Organization, Workspace, Document, ProcessingJob, ExtractedContent, Tender, TenderRequirement, and ExtractionResult.
- **Affected Components**: `backend/app/infrastructure/database/`, `alembic/`.
- **Dependencies**: WBS 1.2.
- **Testing**: Migration apply/rollback tests, CRUD tests on SQLite and PostgreSQL compatibility.

### WBS 1.4 — Storage Adapter & Secure Document Ingestion
- **Objective**: Implement local filesystem storage adapter, path sanitization, SHA-256 calculation, magic bytes inspection, and duplicate detection.
- **Affected Components**: `backend/app/infrastructure/storage/`, `backend/app/services/document_service.py`.
- **Dependencies**: WBS 1.2, WBS 1.3.
- **Testing**: Path traversal attack rejection, oversized upload rejection, duplicate upload detection.

### WBS 1.5 — Modular Document Parser Infrastructure
- **Objective**: Implement `BaseParser` interface and concrete adapters:
  - `PyMuPDFParser` (page-by-page extraction, header detection, OCR requirement flagging).
  - `DocxParser` (paragraph and table extraction).
  - `TxtParser` (multi-encoding fallback).
  - `SpreadsheetParser` (openpyxl + csv).
- **Affected Components**: `backend/app/infrastructure/parsers/`.
- **Dependencies**: `pymupdf`, `python-docx`, `openpyxl`.
- **Testing**: Unit tests on synthetic PDF, DOCX, TXT, and Excel documents; corrupted file handling.

### WBS 1.6 — Text Normalization & Intelligent Traceable Segmentation
- **Objective**: Implement text cleaner and chunking engine with configurable chunk size/overlap, preserving page numbers, character offsets, and section titles.
- **Affected Components**: `backend/app/services/document_processing_service.py`.
- **Dependencies**: WBS 1.5.
- **Testing**: Offset accuracy tests, overlap verification, empty text handling.

### WBS 1.7 — Tender Intelligence Schema & AI Provider Abstraction
- **Objective**: Create typed Pydantic models for structured requirements, external versioned prompt templates in `config/prompts/`, and provider-neutral AI adapter (`BaseAIProvider`, `OpenAICompatibleProvider`, `MockAIProvider`).
- **Affected Components**: `backend/app/domain/intelligence/`, `backend/app/infrastructure/ai/`, `config/prompts/`.
- **Dependencies**: WBS 1.2, WBS 1.6.
- **Testing**: Schema validation tests, mock extraction with exact source citations, graceful fallback when no provider key is configured.

### WBS 1.8 — Application Services Layer
- **Objective**: Decouple business workflows into `DocumentService`, `DocumentProcessingService`, `TenderService`, and `TenderIntelligenceService`.
- **Affected Components**: `backend/app/services/`.
- **Dependencies**: WBS 1.3, 1.4, 1.5, 1.6, 1.7.
- **Testing**: Service integration tests covering the full pipeline.

### WBS 1.9 — REST API Endpoints & OpenAPI Contracts
- **Objective**: Implement endpoints for documents, content inspection, tender management, and intelligence analysis with standard response envelopes.
- **Affected Components**: `backend/app/api/routes/`.
- **Dependencies**: WBS 1.8.
- **Testing**: FastAPI `TestClient` endpoint tests for all routes (200, 201, 400, 404, 422).

### WBS 1.10 — Future Switch Integration Contracts
- **Objective**: Create typed interface contracts and documentation for Switch room agents to interact with TenderForge without hard runtime coupling.
- **Affected Components**: `backend/app/integrations/switch/contracts/`, `docs/phase-1/FUTURE_SWITCH_INTEGRATION.md`.
- **Dependencies**: WBS 1.9.

### WBS 1.11 — Observability, Logging & Error Handling Middleware
- **Objective**: Centralized exception handler mapping domain errors to HTTP envelopes; structured logging with token/secret masking and request correlation ID.
- **Affected Components**: `backend/app/core/logging.py`, `backend/app/core/exceptions.py`.
- **Dependencies**: WBS 1.1.

### WBS 1.12 — Automated Test Harness
- **Objective**: Full pytest suite covering unit, integration, API, and security test cases.
- **Affected Components**: `backend/tests/`.
- **Dependencies**: All prior tasks.
- **Completion Condition**: 100% of automated tests pass cleanly.

### WBS 1.13 — Phase 1 Documentation & Deliverables
- **Objective**: Produce the 8 required Phase 1 reports in `docs/phase-1/` and reproducible demonstration script.

