# TenderForge

> **From Tender to Trustworthy Proposal.**  
> *Flip the Switch Hackathon 2026 — Track: Best Business Workflow*  
> *Core Technology: Switch AI + Multi-Agent Collaboration + Cryptographic ProofLink Traceability*  
> **Release Status:** **RELEASE READY WITH DOCUMENTED LIMITATIONS** (101 Tests Passing, 81% Statement Coverage)

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

### Phase 5: Proactive Procurement Intelligence, Discovery & Closed-Loop Learning
- **Pluggable Procurement Connector Framework**:
  - Extensible connector architecture implementing `BaseProcurementConnector` and `ProcurementConnectorRegistry`.
  - Built-in connectors for `OpenTender` (Open Contracting Data Standard OCDS 1.1), `ManualConnector` (JSON/CSV bulk import), and `MockSandboxConnector` (deterministic multi-sector tender stream).
  - Protocol-level SSRF defense rejecting private IP spaces, link-local addresses, and loopback endpoints.
- **Multi-Feature Deduplication & Discrepancy Reconciliation**:
  - Deterministic exact reference blocking, canonical URL normalization, and `SequenceMatcher` fuzzy title matching ($T \ge 0.88$).
  - Discrepancy reconciliation engine resolving conflicting submission deadlines, altered budgets, and syndicated portal descriptions.
- **9-Dimension Opportunity Matching & Explainability**:
  - Scores opportunities across 9 dimensions: Mandatory Eligibility, Technical Alignment, Past Performance, Financial Capacity, Resource Availability, Geographic Alignment, Buyer Relationship, Strategic Fit, and Risk Runway.
  - **Non-Compensable Hard Gate Rule**: Any failed mandatory qualification gate caps overall suitability at 48.0 and forces `"PURSUIT NOT RECOMMENDED"`.
  - Transparent explainability breakdown detailing Strengths, Weaknesses, Uncertainties, Gate Failures, and Missing Evidence Artifacts.
- **Continuous Tender Monitoring & Corrigendum Intelligence**:
  - Background polling daemon taking cryptographic SHA-256 snapshots (`TenderSnapshot`) of tender specifications.
  - Automatic materiality classification: `Minor`, `Material`, and `Critical`.
  - Downstream impact propagation: automatically invalidates preliminary executive approvals, reverts compliance matrices to `Clarification Required`, flags affected requirements, and mandates human acknowledgement.
- **Market & Competitor Intelligence**:
  - Verified public contract award registry (`AwardRecord`) capturing buyer spend patterns, winner shares, and discount distributions.
  - Competitor profiling (`CompetitorRecord`) tracking empirical win rates and typical discount percentages with strict multi-tenant isolation.
- **14-Stage Bid Lifecycle & Cryptographic Submission Receipts**:
  - Tracks bids through 14 standardized stages from `discovered` to `awarded_won`/`awarded_lost`.
  - Generates tamper-evident SHA-256 submission receipts upon proposal dispatch.
  - Strict human authority mandate: AI agents cannot submit bids.
- **Closed-Loop Bid Learning & Proposal Knowledge Library**:
  - Structured capture of root-cause loss reasons (`price_too_high`, `non_compliant_technical`, etc.) and winning differentiators.
  - Enforces statistical significance threshold ($N \ge 5$) before projecting automated predictive adjustments.
  - Centralized Knowledge Asset library (`KnowledgeAsset`, `KnowledgeAssetVersion`) enabling cross-bid narrative reuse with review status governance.
- **Upgraded Full-Stack Frontend**:
  - Expanded from 15 to **23 operational enterprise views** with dedicated screens for Opportunity Discovery, Recommendations, Procurement Sources, Continuous Monitoring, Corrigenda Triage, Market Spend Analytics, Competitor Benchmarks, and Closed-Loop Bid Learning.


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
│   ├── alembic/                       # Database migrations (001, 002, 003, 004, 005)
│   ├── alembic.ini                    # Alembic configuration
│   └── requirements.txt               # Backend dependencies
├── config/
│   ├── application.yaml               # Enterprise workspaces, security, logging, rbac
│   ├── document_processing.yaml       # File limits, parsers, chunking, categories
│   ├── bid_evaluation.yaml            # Evaluation dimensions, weights, gates, thresholds
│   ├── financial_policies.yaml        # Tax rates, margins, scenarios, currencies
│   ├── risk_matrix.yaml               # 5x5 severity grid, probability bands, categories
│   ├── procurement_sources.yaml       # Connector definitions, timeouts, batching
│   ├── opportunity_matching.yaml      # 9-dimension weights, non-compensable gates
│   ├── monitoring_policies.yaml       # Polling frequencies, materiality criteria
│   ├── market_intelligence.yaml       # Sample thresholds, provenance rules
│   ├── agents/*.yaml                  # 5 specialized agent definitions
│   └── prompts/                       # Versioned prompt templates
├── docs/
│   ├── phase-0/                       # 9 Phase 0 architectural deliverables
│   ├── phase-1/                       # 8 Phase 1 engineering & testing reports
│   ├── phase-2/                       # 22 Phase 2 multi-agent & Switch deliverables
│   ├── phase-3/                       # 20 Phase 3 bid intelligence & enterprise deliverables
│   ├── phase-4/                       # 20 Phase 4 full-stack & production deliverables
│   └── phase-5/                       # 20 Phase 5 procurement intelligence deliverables
├── scripts/
│   ├── demo.py                        # Phase 1 end-to-end demo
│   ├── demo_phase2.py                 # Phase 2 multi-agent workflow demo
│   ├── demo_phase3.py                 # Phase 3 advanced bid intelligence & enterprise demo
│   ├── demo_phase4.py                 # Phase 4 full-stack productization demo
│   └── demo_phase5.py                 # Phase 5 proactive intelligence & closed-loop demo
├── tests/
│   ├── unit/                          # 20+ test suites covering all services, connectors & engines
│   ├── integration/                   # End-to-end multi-agent & procurement workflows
│   ├── api/                           # 87 REST endpoints across all domains
│   └── security/                      # RBAC, tenant isolation, path traversal, SSRF defense
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
# Run all 101 unit, API, integration, and security tests
pytest tests -v

# Run with test coverage measurement
pytest tests --cov=backend/app --cov-report=term
```

**Final Test Execution Results:**
- **Total Tests**: **101 passed in 8.49 seconds** (100% pass rate).
- **Code Coverage**: **81% statement coverage across 7,142 statements**.
- **REST Operations**: **88 OpenAPI Paths, 106 HTTP Operations** across 24 domain routers.
- **Security Hardening**: Zero client-header trust, SSRF defenses on external feeds, MIME spoofing protection, path traversal defenses, and production CORS isolation verified.

---

## 6. End-to-End Demonstrations & Demo Accounts

### 6.1 Pre-Seeded Verified Demo Profiles
TenderForge provides a production-grade database seeding utility (`scripts/seed_demo_data.py`) creating three pre-verified accounts with bcrypt-hashed passwords:

| Role | Email | Password | Intended Capabilities |
|:---|:---|:---|:---|
| **System Admin** | `admin@tenderforge.com` | `TenderForge2026!Admin` | Full administrative control, team invitations, source configuration |
| **Proposal Author** | `author@tenderforge.com` | `TenderForge2026!Author` | Document ingestion, tender creation, proposal drafting, BOQ costing |
| **Compliance Reviewer** | `reviewer@tenderforge.com` | `TenderForge2026!Review` | ProofLink verification, compliance audit, risk harvesting |

To seed or reset demo users:
```powershell
python scripts/seed_demo_data.py
```

### 6.2 Executable Lifecycle Demonstrations

TenderForge includes reproducible demonstration scripts exercising the full platform:

#### Phase 1 Core Ingestion & Intelligence Demo
```powershell
python scripts/demo_phase1.py
```

#### Phase 2 Multi-Agent Collaborative War Room Demo
```powershell
python scripts/demo_phase2.py
```

#### Phase 3 Advanced Bid Intelligence & Enterprise Workspace Demo
```powershell
python scripts/demo_phase3.py
```
*Demonstrates: 7-dimension Bid/No-Bid intelligence, executive sign-off authority, ProofLink contradiction detection & freshness audit, claim lineage hashing, criteria extraction, deterministic Decimal BOQ pricing, scenario modeling (Base, Conservative, Aggressive), Excel export, centralized risk registry, automated approval invalidation, quality check placeholder scanning, and multi-workspace portfolio analytics.*

#### Phase 4 Full-Stack Enterprise Productization Demo
```powershell
python scripts/demo_phase4.py
```

#### Phase 5 Proactive Procurement Intelligence, Discovery & Closed-Loop Learning Demo
```powershell
python scripts/demo_phase5.py
```
*Demonstrates: Automated tender ingestion from procurement feeds, 9-dimension matching with non-compensable hard gates, workspace promotion, continuous monitoring with SHA-256 snapshots, critical corrigendum detection with approval invalidation, human acknowledgement, proposal knowledge library reuse, 14-stage bid submission with tamper-evident receipt, and closed-loop win/loss analytics.*

---

## 7. Master Documentation Index & Final Audit Reports

- **Final Audit Reports (Release Verification)**: Located in [`docs/final-audit/`](docs/final-audit/) (16 comprehensive audit reports):
  1. [`REPOSITORY_AUDIT.md`](docs/final-audit/REPOSITORY_AUDIT.md): Complete repository tree, component mapping, and hygiene.
  2. [`PHASE_0_TO_5_VERIFICATION.md`](docs/final-audit/PHASE_0_TO_5_VERIFICATION.md): Phase-by-phase functional verification.
  3. [`API_ENDPOINT_AUDIT.md`](docs/final-audit/API_ENDPOINT_AUDIT.md): Inventory of 88 OpenAPI paths and 106 HTTP operations.
  4. [`DATABASE_INTEGRITY_REPORT.md`](docs/final-audit/DATABASE_INTEGRITY_REPORT.md): 51 relational tables, 5 migrations, fresh DB test.
  5. [`FRONTEND_FUNCTIONAL_AUDIT.md`](docs/final-audit/FRONTEND_FUNCTIONAL_AUDIT.md): React views, dynamic Switch status, auth flows.
  6. [`AUTHENTICATION_AND_RBAC_AUDIT.md`](docs/final-audit/AUTHENTICATION_AND_RBAC_AUDIT.md): Bcrypt, signed JWT, zero client-header trust.
  7. [`AGENT_AND_SWITCH_AUDIT.md`](docs/final-audit/AGENT_AND_SWITCH_AUDIT.md): 5 specialized agents, 31 MCP tools, Switch Mesh status checks.
  8. [`SECURITY_AUDIT.md`](docs/final-audit/SECURITY_AUDIT.md): OWASP Top 10 evaluation, SSRF defenses, CORS hardening.
  9. [`HARDCODING_AUDIT.md`](docs/final-audit/HARDCODING_AUDIT.md): Elimination of hardcoded secrets and mock shortcuts.
  10. [`PERFORMANCE_AND_CODE_QUALITY.md`](docs/final-audit/PERFORMANCE_AND_CODE_QUALITY.md): Decimal arithmetic, N+1 query prevention.
  11. [`TEST_REPORT.md`](docs/final-audit/TEST_REPORT.md): 101 tests, 100% pass rate, 8.49s runtime, 81% statement coverage.
  12. [`END_TO_END_VALIDATION.md`](docs/final-audit/END_TO_END_VALIDATION.md): Walkthrough of complete 14-stage lifecycle.
  13. [`DEPLOYMENT_READINESS.md`](docs/final-audit/DEPLOYMENT_READINESS.md): Docker Compose, PostgreSQL health check, Nginx runbook.
  14. [`DOCUMENTATION_AUDIT.md`](docs/final-audit/DOCUMENTATION_AUDIT.md): Cross-phase reconciliation and master manifest.
  15. [`KNOWN_LIMITATIONS.md`](docs/final-audit/KNOWN_LIMITATIONS.md): Transparent operational boundaries and fallbacks.
  16. [`FINAL_RELEASE_REPORT.md`](docs/final-audit/FINAL_RELEASE_REPORT.md): Executive release sign-off and classification.
- **Phase 0 Deliverables**: Located in [`docs/phase-0/`](docs/phase-0/) (9 deliverables).
- **Phase 1 Deliverables**: Located in [`docs/phase-1/`](docs/phase-1/) (8 deliverables).
- **Phase 2 Deliverables**: Located in [`docs/phase-2/`](docs/phase-2/) (22 deliverables).
- **Phase 3 Deliverables**: Located in [`docs/phase-3/`](docs/phase-3/) (20 deliverables).
- **Phase 4 Deliverables**: Located in [`docs/phase-4/`](docs/phase-4/) (20 deliverables).
- **Phase 5 Deliverables**: Located in [`docs/phase-5/`](docs/phase-5/) (20 deliverables).
