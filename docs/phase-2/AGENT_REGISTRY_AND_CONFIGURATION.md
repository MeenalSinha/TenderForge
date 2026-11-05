# TENDERFORGE — AGENT REGISTRY & CONFIGURATION GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Architectural Principle

In strict adherence to the **Nothing Hardcoded Principle**, all AI agents in TenderForge are externally defined, modular, and dynamic. No prompts, model parameters, tool authorization lists, or collaboration triggers are hardcoded in application logic.

The Agent Registry (`backend/app/domain/agents/registry.py`) is responsible for discovering, validating, and serving agent configurations loaded from `config/agents/*.yaml` with external versioned prompts loaded from `config/prompts/agents/*.txt`.

---

## 2. Directory Structure

```
config/
├── agents/
│   ├── tender_analyst.yaml
│   ├── compliance_officer.yaml
│   ├── evidence_researcher.yaml
│   ├── proposal_architect.yaml
│   └── bid_auditor.yaml
└── prompts/
    └── agents/
        ├── tender_analyst_v1.txt
        ├── compliance_officer_v1.txt
        ├── evidence_researcher_v1.txt
        ├── proposal_architect_v1.txt
        └── bid_auditor_v1.txt
```

---

## 3. Specialized Agent Specifications

### 3.1 Tender Analyst (`tender_analyst`)
- **Handle:** `@TenderAnalyst`
- **Role:** Document Intelligence Specialist
- **Core Mission:** Deconstructs tender documents, extracting requirements, deliverables, deadlines, and mandatory criteria with exact source coordinates (page, char offset, excerpt).
- **Permitted Tools:** `get_tender_overview`, `analyze_tender`, `get_tender_requirements`, `request_human_review`.
- **Triggers:** `room.document_uploaded`, `user.mention`, `command.analyze`.
- **Hands off to:** `@ComplianceOfficer`, `@EvidenceResearcher`.

### 3.2 Compliance Officer (`compliance_officer`)
- **Handle:** `@ComplianceOfficer`
- **Role:** Regulatory & Compliance Evaluator
- **Core Mission:** Compares extracted requirements against company evidence, computing pass/fail statuses, gap analyses, and risk levels.
- **Permitted Tools:** `get_tender_requirements`, `search_company_evidence`, `evaluate_compliance`, `get_compliance_matrix`, `request_human_review`.
- **Triggers:** `analyst.analysis_completed`, `user.mention`, `command.evaluate_compliance`.
- **Hands off to:** `@EvidenceResearcher`, `@ProposalArchitect`.

### 3.3 Evidence Researcher (`evidence_researcher`)
- **Handle:** `@EvidenceResearcher`
- **Role:** Corporate Evidence Specialist
- **Core Mission:** Locates and verifies company evidence (certificates, past project sheets, financial audits, CVs) supporting mandatory requirements.
- **Permitted Tools:** `upload_company_evidence`, `search_company_evidence`, `get_evidence_details`, `get_tender_requirements`, `request_human_review`.
- **Triggers:** `compliance.gap_identified`, `user.mention`, `command.search_evidence`.
- **Hands off to:** `@ProposalArchitect`, `@ComplianceOfficer`.

### 3.4 Proposal Architect (`proposal_architect`)
- **Handle:** `@ProposalArchitect`
- **Role:** Technical Proposal Writer
- **Core Mission:** Drafts evidence-backed technical responses with embedded ProofLink citations; enforces zero fabrication by inserting action items for missing evidence.
- **Permitted Tools:** `get_tender_overview`, `get_tender_requirements`, `get_compliance_matrix`, `search_company_evidence`, `get_evidence_details`, `create_proposal_draft`, `get_proposal_revision`, `request_human_review`.
- **Triggers:** `compliance.evaluation_completed`, `user.mention`, `command.draft_proposal`.
- **Hands off to:** `@BidAuditor`.

### 3.5 Bid Auditor (`bid_auditor`)
- **Handle:** `@BidAuditor`
- **Role:** Independent Quality & Risk Auditor
- **Core Mission:** Audits proposal drafts independently against tender requirements and verified evidence, flags unsupported/contradicted claims, calculates Bid Readiness Score, and issues submission verdict.
- **Permitted Tools:** `get_tender_overview`, `get_tender_requirements`, `get_evidence_details`, `get_proposal_revision`, `audit_proposal`, `get_audit_report`, `request_human_review`.
- **Triggers:** `proposal.draft_ready`, `user.mention`, `command.audit_proposal`.
- **Hands off to:** `@HumanApprover`, `@ProposalArchitect`.

---

## 4. Configuration Schema (`AgentDefinition`)

Each agent YAML conforms to the following schema:
```yaml
id: "agent_unique_identifier"
name: "Display Name"
handle: "@ChatHandle"
role: "Functional Role Title"
description: "High level summary of agent duties"
prompt_file: "config/prompts/agents/<filename>.txt"
model: "gpt-4o"
temperature: 0.1
max_tokens: 4000
permitted_tools:
  - "tool_name_1"
  - "tool_name_2"
collaboration:
  triggers:
    - "event_name"
  hands_off_to:
    - "@NextAgentHandle"
```

---

## 5. Security & Hot Reloading

- **Tool Whitelisting:** The `AgentRegistry.is_tool_permitted(agent_id, tool_name)` method enforces runtime role-based access control, preventing prompt injections from invoking unauthorized tools.
- **Dynamic Reload:** Calling `agent_registry.reload()` re-scans `config/agents/` without restarting the application server, allowing operational updates in real time.
