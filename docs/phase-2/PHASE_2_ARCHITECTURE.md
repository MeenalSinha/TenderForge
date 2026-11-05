# TENDERFORGE — PHASE 2 SYSTEM ARCHITECTURE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2 (Multi-Agent Collaboration, Switch Integration, Evidence Intelligence)  
**Date:** November 2026  

---

## 1. Architectural Vision & Scope

Phase 2 elevates TenderForge from a core document-processing backend into an autonomous, collaborative multi-agent platform integrated with the Switch ecosystem. Specialized AI agents and human procurement professionals collaborate in real-time inside dedicated **Tender War Rooms** to evaluate eligibility, map company proof, draft verifiable technical responses, and independently audit proposal veracity.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Switch Communication Plane                      │
│                  (Mattermost / Slack / Teams / Web)                    │
├────────────────────────────────────────────────────────────────────────┤
│  #tender-rfp-2026-001                                                  │
│  [Human Bid Director]  [Human Legal Counsel]  [Specialized AI Agents]  │
│  @TenderAnalyst  @ComplianceOfficer  @EvidenceResearcher               │
│  @ProposalArchitect  @BidAuditor                                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ WebSocket / HTTP Stream
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Switch Agent Bridge                             │
│  - Agent Protocol Frame Serialization                                  │
│  - Handshake, Session, Room Management (`SwitchRoomManager`)           │
│  - Event Stream & Notification Broadcaster (`SwitchEventStream`)       │
│  - Slash Command Parser (`/analyze`, `/compliance`, `/draft`, etc.)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      TenderForge MCP & Tool Layer                      │
│  17 Deterministic Tools (Schemas defined in `TOOLS_REGISTRY`)          │
│  Role-Based Access Control Guardrail (`is_tool_permitted`)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        TenderForge Core Services                       │
│  ┌───────────────────────┐  ┌──────────────────────────────────────┐  │
│  │ Evidence Repository   │  │ ProofLink Traceability Engine        │  │
│  │ Company Profiles      │  │ 5 Statuses: Verified, Human Confirmed│  │
│  │ Audits, Certs, Past   │  │ Pending, Unsupported, Contradicted   │  │
│  └───────────┬───────────┘  └──────────────────┬───────────────────┘  │
│              │                                 │                      │
│  ┌───────────▼───────────┐  ┌──────────────────▼───────────────────┐  │
│  │ Compliance Assessment │  │ Evidence-Backed Proposal Architect   │  │
│  │ Pass/Fail/Risk Matrix │  │ Zero Fabrication Enforced            │  │
│  │ Gap Analysis          │  │ Real DOCX Generation via python-docx │  │
│  └───────────┬───────────┘  └──────────────────┬───────────────────┘  │
│              │                                 │                      │
│  ┌───────────▼───────────┐  ┌──────────────────▼───────────────────┐  │
│  │ Independent Bid Audit │  │ Human-in-the-Loop Governance Gate    │  │
│  │ Readiness Score 0-100 │  │ Immutable Digital Sign-Off           │  │
│  │ Severity Findings     │  │ Cryptographic SHA-256 Signature Hash │  │
│  └───────────┬───────────┘  └──────────────────┬───────────────────┘  │
│              │                                 │                      │
│              └────────────────┬────────────────┘                      │
│                               ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Final Bid Package Export Service                                │  │
│  │ Bundles: DOCX Proposal + XLSX Matrix + Audit + Digital Sign-Off │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Persistence Layer                               │
│  SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy 2.0 & Alembic         │
│  Local Filesystem / Object Storage (`storage/proposals`, `exports`)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystems

### 2.1 Switch Agent Bridge (`backend/app/integrations/switch/agent_bridge.py`)
- Coordinates real-time bi-directional messaging between Switch chat channels and the TenderForge backend.
- Conforms to the Switch Agent Protocol, supporting `HANDSHAKE`, `EVENT`, `COMMAND`, `RESPONSE`, and `HEARTBEAT` frames.
- Exposes interactive slash commands (`/analyze`, `/compliance`, `/draft`, `/audit`, `/approve`, `/export`).

### 2.2 Model Context Protocol (MCP) & Tool Dispatcher (`backend/app/integrations/switch/tools/`)
- Exposes 17 strictly typed tools conforming to JSON Schema.
- Enforces runtime Role-Based Access Control (RBAC): agents are restricted to tools declared in their external YAML configurations.
- Human-only governance tools (`record_human_decision`) cannot be executed by AI agents.

### 2.3 Evidence Repository (`backend/app/services/evidence_service.py`)
- Manages organizational profiles (`legal_name`, `registration_number`, `financial_metrics`, `certifications`, `core_capabilities`).
- Ingests and stores proof records across 7 evidence types (`financial_audit`, `certification`, `past_project`, `statutory_registration`, `policy`, `cv_personnel`, `other`).
- Leverages Phase 1 document parsers (PDF, DOCX, XLSX, TXT) to parse proof documents and extract factual summaries.

### 2.4 ProofLink Traceability Engine (`backend/app/services/prooflink_service.py`)
- Resolves requirement constraints against company evidence records.
- Grounded citations include exact document ID, page, offset, confidence score, and factual notes.
- Enforces 5 traceable statuses:
  1. `Verified`: Evidence meets or exceeds requirement criteria.
  2. `Human Confirmed`: Explicitly validated by an authorized human expert.
  3. `Pending`: Unconfirmed candidate match identified via semantic or keyword correlation.
  4. `Unsupported`: No documentary evidence exists in the repository.
  5. `Contradicted`: Documentary evidence conflicts with requirement thresholds (e.g. turnover deficit).

### 2.5 Compliance Assessment Engine (`backend/app/services/compliance_service.py`)
- Evaluates full compliance matrices across Eligibility, Technical, Financial, and Submission categories.
- Assigns compliance statuses (`Compliant`, `Partially Compliant`, `Non-Compliant`, `Clarification Required`) and risk levels (`Low`, `Medium`, `High`, `Critical`).
- Generates actionable remediation items (e.g. joint venture, subcontracting, certificate renewal).

### 2.6 Evidence-Backed Proposal Architect (`backend/app/services/proposal_service.py`)
- Synthesizes 5 comprehensive proposal sections aligned with evaluation criteria:
  - Section 1.0: Executive Summary & Corporate Profile
  - Section 2.0: Technical Approach & Solution Architecture
  - Section 3.0: Past Performance & Verifiable References
  - Section 4.0: Quality Assurance & Certified Standards
  - Section 5.0: Compliance Matrix & Statutory Undertakings
- **Zero Fabrication Mandate:** When evidence is missing or pending, the engine refuses to hallucinate claims and instead inserts explicit `[ACTION REQUIRED: ...]` markers.
- Automatically generates formatted Word documents (`.docx`) with ProofLink footnotes.

### 2.7 Independent Bid Auditor (`backend/app/services/audit_service.py`)
- Performs unsparing adversarial verification of proposal claims against original tender clauses and repository evidence.
- Detects unsupported claims, contradictions, and unresolved action markers.
- Calculates the Bid Readiness Score (0.0 to 100.0) with severity-weighted deductions:
  - Critical: -25 pts (disqualification hazard)
  - Major: -10 pts (scoring penalty)
  - Minor: -3 pts (clarification)
- Issues readiness verdicts: `Ready for Submission` (Score >= 90%, zero Critical), `Conditional Approval Required` (Score >= 75%), or `Submission Blocked - High Risk`.

### 2.8 Human-in-the-Loop Governance & Digital Approval (`backend/app/services/approval_service.py`)
- Strictly enforces human oversight: proposals cannot be submitted or packaged for release without explicit human sign-off.
- Generates cryptographic SHA-256 digital signature hashes binding the tender ID, proposal version, audit ID, decision, user ID, role, and comments.

### 2.9 Final Bid Package Export Service (`backend/app/services/export_service.py`)
- Bundles complete proposal deliverables into a submission-ready `.zip` archive:
  1. `01_Technical_Proposal_vX.docx`: Formatted Word proposal with ProofLink footnotes.
  2. `02_Compliance_Matrix.xlsx`: Formatted Excel workbook with conditional status color coding.
  3. `03_Independent_Bid_Audit_Report.txt`: Comprehensive audit findings and readiness metrics.
  4. `04_Human_Sign_Off_Certificate.json`: Cryptographic digital sign-off certificate.

---

## 3. Workflow State Machine Lifecycle

```
WORKSPACE_INITIALIZED
        │
        ▼ (Tender Analyst: Extract Clauses)
 TENDER_ANALYZED
        │
        ▼ (Evidence Researcher: Map ProofLink)
 EVIDENCE_MAPPED
        │
        ▼ (Compliance Officer: Matrix Evaluation)
COMPLIANCE_EVALUATED
        │
        ▼ (Proposal Architect: Evidence-Backed Drafting)
 PROPOSAL_DRAFTED ◄─────────────────────────┐
        │                                  │
        ▼ (Bid Auditor: Independent Audit) │
 PROPOSAL_AUDITED                          │
        │                                  │
   ┌────┴───────────────────────────┐      │
   ▼                                ▼      │
HUMAN_REVIEW_PENDING       REVISION_REQUIRED
   │                                       │
   ├───────────────────────────────────────┘
   ▼ (Human Sign-Off)
BID_APPROVED (Export Unlocked)
```
