# TenderForge

> **From Tender to Trustworthy Proposal.**
> *Flip the Switch Hackathon 2026 — Track: Best Business Workflow*
> *Core Technology: Switch AI + Multi-Agent Collaboration + Cryptographic ProofLink Traceability*

---

## 1. Overview

**TenderForge** is an enterprise AI-assisted tender intelligence and proposal preparation platform. Responding to government tenders and corporate RFPs is notoriously complex, error-prone, and time-consuming. Critical eligibility criteria and mandatory certifications are distributed across hundreds of pages, and unsupported or inaccurate claims frequently cause proposal disqualification.

TenderForge turns complicated tender workflows into a collaborative, evidence-backed workspace where human bid teams and specialized AI agents collaborate with absolute cryptographic integrity.

---

## 2. Key Capabilities by Phase

### Phase 1: Core Backend & Intelligent Document Processing
- **Multi-Format Ingestion**: Ingests `.pdf`, `.docx`, `.txt`, `.csv`, and `.xlsx` procurement documents with strict MIME inspection and magic binary signature validation.
- **Traceable Segmentation**: Token-aware chunking preserving source page numbers, character offsets, and section headings.
- **Structured Tender Intelligence**: Extracts general tender metadata, eligibility criteria, technical requirements, financial covenants, and submission deadlines.
- **Zero Fabrication Rule**: Missing information is explicitly marked as `null` or `not_found` — never fabricated.

### Phase 2: Multi-Agent Collaboration & Switch Integration
- **5 Specialized AI Agents**:
  1. `Tender Analyst` (@TenderAnalyst): Document intelligence and requirement extraction.
  2. `Compliance Officer` (@ComplianceOfficer): Multi-criteria evaluation against company repository.
  3. `Evidence Researcher` (@EvidenceResearcher): Proof discovery and semantic matching.
  4. `Proposal Architect` (@ProposalArchitect): Proposal drafting with embedded ProofLink citations.
  5. `Bid Auditor` (@BidAuditor): Independent verification, readiness scoring, and contradiction discovery.
- **Switch Room Integration**: Real-time collaborative war rooms bridging human teams and AI agents.
- **Cryptographic Human Sign-Off**: Mandatory human approval workflow generating SHA-256 digital signature hashes.

### Phase 3: Advanced Bid Intelligence & Enterprise Workspace
- **Bid/No-Bid Decision Intelligence**: Multi-dimensional evaluation governed by **non-compensable eligibility gates** (a failed mandatory gate strictly enforces `NO-BID RECOMMENDED` or `BID WITH CONDITIONS`, preventing unviable pursuits).
- **Advanced ProofLink Intelligence**:
  - Proactive freshness tracking and expiration horizon warnings.
  - Cross-document contradiction detection (e.g. discrepancies in reported turnover across audits).
  - Cryptographic claim lineage graph (`Requirement -> Evidence -> Extract -> Claim -> Review -> Approved Section`).
- **Tender Evaluation Criteria & Proposal Optimization**:
  - Extracts evaluation schemes, weights, and scoring rubrics.
  - Side-by-side Before-and-After improvement recommendations to maximize evaluation scores.
- **Financial Proposal & Commercial Workspace**:
  - Strict deterministic calculations using Python's `decimal.Decimal` (zero floating-point drift).
  - Itemized Bill of Quantities (BOQ) with negative/zero rate validations.
  - Multi-scenario commercial modeling (Base Case, Conservative, Aggressive).
  - Publication-grade styled Excel export (`.xlsx`) via `openpyxl`.
- **Centralized Bid Risk Registry**: Automated risk harvesting into a unified $5 \times 5$ severity matrix with actionable mitigation tracking.
- **Proposal Revision Governance & Quality Validation**:
  - Automated approval invalidation upon any content mutation.
  - Line-by-line unified revision diffing via `difflib`.
  - Pre-submission quality scanner detecting placeholders (`TODO`, `TBD`, `XXX`), missing citations, and formatting defects.
- **Timezone-Aware Deadlines & Switch Reminders**: Automated countdowns and notification dispatches to Switch rooms.
- **Server-Side Role-Based Access Control (RBAC)**: Enforces `Viewer`, `Author`, `Reviewer`, `Approver`, and `Admin` permissions across all endpoints.

---

## 3. Project Structure

```text
TenderForge/
├── backend/
│   ├── app/
│   │   ├── main.py                    # ASGI application & middleware
│   │   ├── api/
│   │   │   ├── routes/                # REST endpoints (health, tenders, documents, bid-eval, financial, risks, etc.)
│   │   │   ├── dependencies/          # Dependency injection (DB, Services)
│   │   │   └── schemas/               # Pydantic v2 schemas
│   │   ├── core/
│   │   │   ├── config.py              # Centralized Pydantic-Settings & YAML configuration
│   │   │   ├── rbac.py                # Server-side Role-Based Access Control
│   │   │   ├── logging.py             # Structured JSON logger with secret masking
│   │   │   └── security.py            # Path sanitization, magic bytes, hashing
│   │   ├── infrastructure/
│   │   │   ├── database/              # SQLAlchemy 2.0 models & connection session
│   │   │   ├── storage/               # Local filesystem UUID storage adapter
│   │   │   ├── parsers/               # PDF, DOCX, TXT, Spreadsheet parsers
│   │   │   └── ai/                    # AI provider abstraction (Mock, OpenAI, Fallback)
│   │   ├── integrations/
│   │   │   └── switch/                # Switch Room contracts, bridge, and 26 MCP tools
│   │   └── services/                  # 14 core business services (bid-decision, prooflink, financial, risks, etc.)
│   ├── alembic/                       # Database migrations (001, 002, 003)
│   ├── alembic.ini                    # Alembic configuration
│   └── requirements.txt               # Backend dependencies
├── config/
│   ├── application.yaml               # Enterprise workspaces, security, logging, rbac
│   ├── document_processing.yaml       # File limits, parsers, chunking, categories
│   ├── bid_evaluation.yaml            # Evaluation dimensions, weights, gates, thresholds
│   ├── financial_policies.yaml        # Tax rates, margins, scenarios, currencies
│   ├── risk_matrix.yaml               # 5x5 severity grid, probability bands, categories
│   ├── agents/*.yaml                  # 5 specialized agent definitions
│   └── prompts/                       # Versioned prompt templates
├── docs/
│   ├── phase-0/                       # 9 Phase 0 architectural deliverables
│   ├── phase-1/                       # 8 Phase 1 engineering & testing reports
│   ├── phase-2/                       # 22 Phase 2 multi-agent & Switch deliverables
│   └── phase-3/                       # 20 Phase 3 bid intelligence & enterprise deliverables
├── scripts/
│   ├── demo.py                        # Phase 1 end-to-end demo
│   ├── demo_phase2.py                 # Phase 2 multi-agent workflow demo
│   └── demo_phase3.py                 # Phase 3 advanced bid intelligence & enterprise demo
├── tests/
│   ├── unit/                          # 14 test suites covering all services and engines
│   ├── integration/                   # Full ingestion and multi-agent workflow pipelines
│   ├── api/                           # Health, documents, tenders, phase 2 and phase 3 APIs
│   └── security/                      # Path traversal, MIME spoofing, prompt injection
├── .env.example                       # Centralized configuration template
└── pytest.ini                         # Test runner configuration
```

---

## 4. Quickstart Guide

### 4.1 Prerequisites
- Python 3.10+ (tested on Python 3.14.2 AMD64)
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
alembic -c backend/alembic.ini upgrade head
```

### 4.4 Run the Application
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open interactive Swagger API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Automated Test Suite & Verification

Execute the complete automated test suite:
```powershell
# Run all 65 tests
pytest tests -v

# Run with test coverage measurement
pytest tests --cov=backend/app --cov-report=term
```

**Test Execution Results:**
- **Total Tests**: **65 passed in 4.03 seconds** (100% pass rate).
- **Code Coverage**: **81% coverage across 4,874 statements**.
- **Security Tests**: Path traversal, MIME spoofing, oversized upload, and prompt injection attacks verified blocked.

---

## 6. End-to-End Demonstrations

TenderForge includes reproducible demonstration scripts exercising the full platform:

### Phase 1 Core Ingestion & Intelligence Demo
```powershell
python scripts/demo.py
```

### Phase 2 Multi-Agent Collaborative War Room Demo
```powershell
python scripts/demo_phase2.py
```

### Phase 3 Advanced Bid Intelligence & Enterprise Workspace Demo
```powershell
python scripts/demo_phase3.py
```
*Demonstrates: Non-compensable eligibility gates, executive override sign-off, contradiction detection and resolution, cryptographic claim lineage, tender evaluation optimization, deterministic Decimal BOQ pricing, styled Excel export, pre-submission quality checks, and multi-workspace portfolio analytics.*

---

## 7. Documentation Index

- **Phase 0 Deliverables**: Located in [`docs/phase-0/`](docs/phase-0/) (9 deliverables).
- **Phase 1 Deliverables**: Located in [`docs/phase-1/`](docs/phase-1/) (8 deliverables).
- **Phase 2 Deliverables**: Located in [`docs/phase-2/`](docs/phase-2/) (22 deliverables).
- **Phase 3 Deliverables**: Located in [`docs/phase-3/`](docs/phase-3/) (20 deliverables).
