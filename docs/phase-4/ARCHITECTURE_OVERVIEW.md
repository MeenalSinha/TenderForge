# TenderForge Phase 4: Architecture Overview

## 1. Executive Summary

TenderForge is an enterprise-grade, multi-agent tender intelligence and proposal preparation platform engineered for the **Flip the Switch Hackathon 2026** (Track: Best Business Workflow). Phase 4 culminates the platform's evolution from a backend intelligence pipeline into a production-ready, full-stack, distributed enterprise product.

```
+---------------------------------------------------------------------------------------+
|                               TENDERFORGE ENTERPRISE SPA                              |
|   (React 18, Tailwind CSS, Lucide Icons, Chart.js, 15 Operational War Room Views)     |
+---------------------------------------------------------------------------------------+
                                        | (HTTPS / REST API / SSE)
                                        v
+---------------------------------------------------------------------------------------+
|                                  NGINX REVERSE PROXY                                  |
|   (Gzip compression, Rate Limiting, TLS Termination, Security Headers, SPA Fallback)  |
+---------------------------------------------------------------------------------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
+------------------------------------+    +------------------------------------+
|         TENDERFORGE ASGI           |    |           SWITCH PLATFORM          |
|  FastAPI, Pydantic, Python 3.14    |    |  Multi-Agent War Room, Event Bus,  |
|  Correlation IDs, Security Headers |<-->|  5 Specialized Collaborative Agent |
|  JWT Auth, 5-Tier RBAC Matrix      |    |  Instances (Coordinator, Analyst...) |
+------------------------------------+    +------------------------------------+
                   |
         +---------+---------+
         |                   |
         v                   v
+-----------------+ +---------------------------------------------------------------+
|   POSTGRESQL    | |                 OBJECT STORAGE ABSTRACTION                    |
|   (SQLAlchemy   | |  (Local Filesystem, MinIO, AWS S3, Google Cloud Storage       |
|    Connection   | |   with SHA-256 Content-Addressed Verification)                |
|    Pool 16+)    | +---------------------------------------------------------------+
+-----------------+
```

---

## 2. Core Architectural Pillars

### 2.1 Full-Stack Decoupled Architecture
1. **Frontend Tier**:
   - Single-Page Application (SPA) built with React 18, modern ES modules, and Tailwind CSS.
   - 15 specialized operational views reflecting the end-to-end tender lifecycle: from ingestion to financial BOQ modeling, 5x5 risk analysis, Switch agent collaboration, and deliverable release bundles.
   - Built to production distribution at `frontend/dist/index.html` (101 KB bundled) and mounted cleanly in FastAPI as static/fallback assets for single-command zero-configuration execution.
2. **Backend API Tier**:
   - High-throughput asynchronous FastAPI framework running under ASGI (Uvicorn / Gunicorn).
   - Strict input validation via Pydantic v2 schemas and centralized `ResponseEnvelope[T]` format with correlation ID tracing.
   - Defense-in-depth security middleware enforcing `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and strict CORS policies.
3. **Multi-Agent Orchestration Tier**:
   - Native integration with the Switch multi-agent collaboration platform.
   - Five specialized agent personas with bounded tool authorization:
     - `tender_analyst`: Requirement breakdown, compliance classification.
     - `evidence_finder`: Semantic repository search, freshness auditing.
     - `proposal_writer`: Evidence-anchored proposal section authoring.
     - `compliance_officer`: Independent cross-checking and contradiction detection.
     - `bid_strategist`: Win/loss viability modeling, BOQ financial review.
4. **Data & Storage Persistence Tier**:
   - Relational Database: SQLAlchemy ORM with support for PostgreSQL 16 connection pooling (`pool_size`, `max_overflow`, `pool_recycle`, `pool_pre_ping`) and SQLite fallback.
   - Alembic Migration Engine: Versioned schema migrations tracking revisions `001` through `004`.
   - Pluggable Object Storage: Abstracted storage provider supporting local air-gapped disks, MinIO, Amazon S3, and Google Cloud Storage.

---

## 3. Component Interactions & Request Flow

```
[User Browser]
       |
       | 1. HTTP POST /api/v1/auth/login
       v
[FastAPI Auth Route] --> [AuthService] --> [Bcrypt / JWT] --> Return Access Token
       |
       | 2. HTTP POST /api/v1/tenders (Bearer Token)
       v
[RBAC Middleware] --> Checks role in [OrganizationMember]
       |
       | 3. Ingest Documents -> [StorageProvider.save()] -> Calculate SHA-256
       v
[TenderIntelligenceEngine] --> Extract Clauses & Categorize Requirements
       |
       | 4. Sync to Switch War Room
       v
[SwitchAgentBridge] --> Provision Collaborative Room -> Trigger 5 AI Agents
       |
       | 5. Evidence Match -> ProofLink Lineage -> Contradiction Resolution
       v
[ProposalOptimizer] --> Side-by-Side Diff -> Executive Sign-Off -> Export Bundle
```

---

## 4. Production Readiness Attributes

| Attribute | Implementation Standard |
| :--- | :--- |
| **Authentication** | Cryptographic bcrypt salt rounds (4-12), HS256 JWT tokens with 24h expiration, cryptographically random single-use password reset tokens with SHA-256 verification. |
| **Authorization** | 5-tier role-based access control (`admin`, `bid_manager`, `proposal_writer`, `reviewer`, `viewer`) with multi-tenant organization boundary enforcement. |
| **Auditability** | Complete immutable audit log capturing every human decision, agent tool execution, and release export. |
| **Resilience** | Connection health checks (`/health`, `/ready`, `/diagnostics`), automated database backups with SHA-256 checksums, and graceful degradation for cloud object storage. |
