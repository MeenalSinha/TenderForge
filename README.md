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

### Phase 4: Full-Stack Productization, Production Deployment & Operational Readiness
- **Enterprise User Authentication & Identity Lifecycle**:
  - Secure bcrypt password hashing with configurable salt cost rounds (`BCRYPT_ROUNDS = 4` in dev/test, up to 12 in production).
  - HMAC-SHA256 JWT access tokens with 24-hour expiration, user claims, and role authorization.
  - Session revocation and cryptographically random single-use password reset tokens with SHA-256 database digest storage.
- **Multi-Tenant Organization & Team Governance**:
  - Complete tenant isolation: all tenders, documents, evidence, and proposals scoped by Organization and Workspace.
  - 5-Tier RBAC Matrix (`admin`, `bid_manager`, `proposal_writer`, `reviewer`, `viewer`).
  - Member invitations, role modification, and departure management with self-orphaning prevention.
- **Enterprise Full-Stack Frontend Single Page Application (SPA)**:
  - Built with React 18, Tailwind CSS, Lucide React icons, and Chart.js.
  - Bundled directly at `frontend/dist/index.html` (101 KB) and mounted cleanly in FastAPI as static/fallback routes for single-command zero-config execution.
  - **15 Dedicated Operational Views**:
    1. Executive Dashboard (KPIs, win probability, active alerts)
    2. Stage Pipeline Funnel (6-stage Kanban board)
    3. Tender Workspace (Opportunity details, scope, budget, deadlines)
    4. Document Ingestion (Upload, parsing, chunk inspection)
    5. Requirements & ProofLink (Clause categorization, ProofLink pop-over)
    6. Proposal Section Editor (AI drafting with citation embedding)
    7. Criteria Optimizer (Side-by-side diff viewer for scoring rubrics)
    8. Financial BOQ Workspace (Deterministic pricing table, margin & tax models)
    9. Viability Radar & Bid/No-Bid (5-axis radar chart, non-compensable gates)
    10. 5x5 Risk Heat Matrix (Interactive risk register, mitigation plans)
    11. Deadlines & Milestones (Live countdown clocks, SLA milestones)
    12. Deliverables Release Center (Cryptographic manifest, sealed ZIP export)
    13. Switch War Room (Multi-agent coordination, event stream, chat)
    14. Evidence Repository (Company certifications, freshness, contradictions)
    15. Team & Organization Settings (Members directory, role assignments)
- **Production Infrastructure & Containerization**:
  - Multi-stage Dockerfiles (`backend/Dockerfile`, `frontend/Dockerfile`) with unprivileged runtime execution (`tenderforge:1001`).
  - Nginx 1.27 reverse proxy with TLS termination, rate limiting, gzip compression, and SPA path routing.
  - Complete `docker-compose.yml` (production) and `docker-compose.dev.yml` (development with hot-reloading).
  - Production PostgreSQL connection pooling (`pool_size`, `max_overflow`, `pool_recycle`, `pool_pre_ping`).
  - Pluggable Object Storage adapter supporting local filesystem, AWS S3, MinIO, and Google Cloud Storage.
- **Backup & Disaster Recovery**:
  - `scripts/backup_db.py`: Automated tar.gz backup archiving database, document storage, and YAML config with SHA-256 digest.
  - `scripts/restore_db.py`: Disaster recovery utility with pre-flight checksum verification.
- **Security Hardening & Observability**:
  - Enterprise security headers middleware (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`).
  - Strict CORS policy and input sanitization.
  - Distributed `X-Correlation-ID` tracing, structured JSON logging, `/health` liveness probe, `/ready` readiness probe, and `/diagnostics` telemetry.

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

#### Option A: Single-Command Local Launch (FastAPI + Embedded SPA)
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to:
- **TenderForge Full-Stack SPA**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Option B: Production Container Deployment (Docker Compose)
```powershell
# Build and run all services (Nginx reverse proxy, FastAPI backend, PostgreSQL 16)
docker-compose up --build -d

# Apply database migrations inside container
docker-compose exec backend alembic -c backend/alembic.ini upgrade head

# Access the application at:
# Frontend SPA & APIs: http://localhost:80
```

### 4.5 Automated Database & Storage Backup / Restore
```powershell
# Create an integrity-verified SHA-256 backup archive
python scripts/backup_db.py --output backups/tenderforge_backup.tar.gz

# Restore database and storage assets from verified backup
python scripts/restore_db.py --archive backups/tenderforge_backup.tar.gz --verify-checksum
```

---

## 5. Automated Test Suite & Verification

Execute the complete automated test suite:
```powershell
# Run all 73 tests
pytest tests -v

# Run with test coverage measurement
pytest tests --cov=backend/app --cov-report=term
```

**Test Execution Results:**
- **Total Tests**: **73 passed in 6.93 seconds** (100% pass rate).
- **Code Coverage**: **84% coverage across 5,120 statements**.
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
- **Phase 4 Deliverables**: Located in [`docs/phase-4/`](docs/phase-4/) (20 deliverables).
