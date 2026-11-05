# TenderForge

> **From Tender to Trustworthy Proposal.**
> *Flip the Switch Hackathon 2026 — Track: Best Business Workflow*
> *Core Technology: Switch + AI Coding Agents + Multi-Agent Collaboration*

---

## 1. Overview

**TenderForge** is an enterprise AI-assisted tender intelligence and proposal preparation platform. Responding to government tenders and corporate RFPs is notoriously complex, error-prone, and time-consuming. Critical eligibility criteria and mandatory certifications are distributed across hundreds of pages, and unsupported or inaccurate claims frequently cause proposal disqualification.

TenderForge solves this by introducing collaborative multi-agent intelligence, evidence traceability (**ProofLink**), structured validation, and human sign-off.

---

## 2. Key Capabilities (Phase 0 & Phase 1)

- **Multi-Format Ingestion**: Ingests `.pdf`, `.docx`, `.txt`, `.csv`, and `.xlsx` procurement documents with strict MIME inspection and magic binary signature validation.
- **Path Traversal & Storage Security**: Uploaded files are isolated under UUID-partitioned storage trees with SHA-256 deduplication.
- **Intelligent Document Intelligence**:
  - **PDF**: Page-by-page extraction, structural headers, and automatic OCR requirement detection via PyMuPDF.
  - **DOCX**: Paragraph, heading, and multi-row/multi-column table parsing via python-docx.
  - **TXT**: Plain text with multi-encoding recovery (`utf-8`, `latin-1`, `cp1252`, `utf-16`).
  - **Spreadsheets**: Sheet, row, and column parsing for financial pricing schedules.
- **Intelligent Traceable Segmentation**: Token-aware sliding-window chunking that preserves source page numbers, character offsets, and section titles.
- **Structured Tender Intelligence**: Extracts general tender info, eligibility requirements, technical scope, financial conditions, and submission guidelines.
- **ProofLink Foundation**: Every extracted requirement includes the source document ID, page number, character offset, and a verbatim source quotation.
- **Zero Fabrication Rule**: Missing data is marked as `null` or `not_found` — never hallucinated. When an AI provider is unconfigured, the system returns `ai_configuration_required` with 0 fabricated items.
- **Prompt Injection Defense**: Untrusted document text is encapsulated within protective delimiter tags and filtered against adversarial override directives.
- **Future Switch Integration**: Decoupled typed schemas (`SwitchRoomContext`, `SwitchAgentCommand`, `SwitchRequirementCitation`) ready for Phase 2 multi-agent Switch War Rooms.

---

## 3. Project Structure

```text
TenderForge/
├── backend/
│   ├── app/
│   │   ├── main.py                    # ASGI application & middleware
│   │   ├── api/
│   │   │   ├── routes/                # Health, documents, tenders REST routes
│   │   │   ├── dependencies/          # Dependency injection (DB, Services)
│   │   │   └── schemas/               # Pydantic v2 request/response schemas
│   │   ├── core/
│   │   │   ├── config.py              # Centralized Pydantic-Settings & YAML loader
│   │   │   ├── logging.py             # Structured JSON logger with secret redaction
│   │   │   ├── exceptions.py          # Domain exceptions with HTTP mapping
│   │   │   └── security.py            # Path sanitization, magic bytes, hashing
│   │   ├── domain/
│   │   │   ├── documents/             # Text normalizer & intelligent segmenter
│   │   │   ├── tenders/               # Tender business models
│   │   │   └── intelligence/          # Typed schemas for structured extraction
│   │   ├── infrastructure/
│   │   │   ├── database/              # SQLAlchemy 2.0 models & connection session
│   │   │   ├── storage/               # Local filesystem UUID storage adapter
│   │   │   ├── parsers/               # PDF, DOCX, TXT, Spreadsheet parsers
│   │   │   └── ai/                    # AI provider abstraction (Mock, OpenAI, Fallback)
│   │   ├── integrations/
│   │   │   └── switch/                # Switch Room contracts & agent bridge interface
│   │   └── services/                  # Document, processing, tender, and intelligence services
│   ├── alembic/                       # Database migrations (initial schema)
│   ├── alembic.ini                    # Alembic configuration
│   └── requirements.txt               # Backend dependencies
├── config/
│   ├── application.yaml               # Enterprise workspaces, security, logging
│   ├── document_processing.yaml       # File limits, parsers, chunking, categories
│   └── prompts/
│       └── tender_analysis_v1.txt     # Versioned external prompt template
├── docs/
│   ├── phase-0/                       # 9 Phase 0 architectural deliverables
│   └── phase-1/                       # 8 Phase 1 engineering & testing reports
├── scripts/
│   └── demo.py                        # Reproducible end-to-end demonstration script
├── tests/
│   ├── unit/                          # Config, security, parser, segmentation, AI tests
│   ├── integration/                   # Full ingestion and tender analysis pipelines
│   ├── api/                           # Health, documents, tenders, missing AI tests
│   └── security/                      # Path traversal, MIME spoofing, prompt injection
├── .env.example                       # Centralized configuration template
└── pytest.ini                         # Test runner configuration
```

---

## 4. Quickstart Guide

### 4.1 Prerequisites
- Python 3.10+ (tested on Python 3.14.2)
- Git

### 4.2 Installation
```powershell
# Clone or enter workspace
cd TenderForge

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 4.3 Database Migration
```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

### 4.4 Run the Application
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open interactive Swagger API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Running the Automated Test Suite

```powershell
# Run all 31 tests
python -m pytest tests -v

# Run with test coverage measurement
python -m pytest tests --cov=backend/app --cov-report=term-missing
```

**Test Results:**
- **Total Tests**: 31
- **Passed**: 31 (100%)
- **Failed**: 0
- **Coverage**: 85% across 1,518 statements

---

## 6. End-to-End Demonstration

To run the automated, reproducible demonstration script:
```powershell
python scripts/demo.py
```
This script exercises:
1. Health and readiness checks (`/health`, `/ready`).
2. Uploading and parsing a tender document (PDF).
3. Inspecting extracted text chunks with exact page and character offsets.
4. Registering a tender opportunity.
5. Extracting structured tender requirements with ProofLink citations.
6. Grouping extracted requirements by category (`eligibility`, `technical`, `financial`, `submission`).
7. Graceful degradation when AI credentials are absent (guaranteed 0 fabricated items).

---

## 7. Documentation Index

### Phase 0 Deliverables (`docs/phase-0/`)
1. [REPOSITORY_AUDIT.md](docs/phase-0/REPOSITORY_AUDIT.md)
2. [PRODUCT_REQUIREMENTS.md](docs/phase-0/PRODUCT_REQUIREMENTS.md)
3. [SWITCH_INTEGRATION_AUDIT.md](docs/phase-0/SWITCH_INTEGRATION_AUDIT.md)
4. [TECHNICAL_FEASIBILITY.md](docs/phase-0/TECHNICAL_FEASIBILITY.md)
5. [SYSTEM_ARCHITECTURE.md](docs/phase-0/SYSTEM_ARCHITECTURE.md)
6. [DATA_MODEL_DESIGN.md](docs/phase-0/DATA_MODEL_DESIGN.md)
7. [API_DESIGN.md](docs/phase-0/API_DESIGN.md)
8. [RISK_REGISTER.md](docs/phase-0/RISK_REGISTER.md)
9. [PHASE_1_IMPLEMENTATION_PLAN.md](docs/phase-0/PHASE_1_IMPLEMENTATION_PLAN.md)

### Phase 1 Deliverables (`docs/phase-1/`)
1. [IMPLEMENTATION_REPORT.md](docs/phase-1/IMPLEMENTATION_REPORT.md)
2. [API_DOCUMENTATION.md](docs/phase-1/API_DOCUMENTATION.md)
3. [DATABASE_SCHEMA.md](docs/phase-1/DATABASE_SCHEMA.md)
4. [DOCUMENT_PROCESSING_GUIDE.md](docs/phase-1/DOCUMENT_PROCESSING_GUIDE.md)
5. [CONFIGURATION_GUIDE.md](docs/phase-1/CONFIGURATION_GUIDE.md)
6. [TEST_REPORT.md](docs/phase-1/TEST_REPORT.md)
7. [SECURITY_REPORT.md](docs/phase-1/SECURITY_REPORT.md)
8. [FUTURE_SWITCH_INTEGRATION.md](docs/phase-1/FUTURE_SWITCH_INTEGRATION.md)
