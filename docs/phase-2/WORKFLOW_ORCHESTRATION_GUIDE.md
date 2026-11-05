# TENDERFORGE — MULTI-AGENT WORKFLOW ORCHESTRATION GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & State Machine Engine

The **Workflow Orchestrator** (`backend/app/services/workflow_orchestrator.py`) implements a deterministic Finite State Machine (FSM) governing the procurement response lifecycle. It manages lifecycle stages, enforces valid transitions, triggers specialized agents, and preserves an auditable transition history.

---

## 2. Finite State Machine Stages

| Stage Identifier | Description | Triggering Actor | Permitted Next Stages |
| :--- | :--- | :--- | :--- |
| `WORKSPACE_INITIALIZED` | Tender created, documents uploaded, war room initialized | System / User | `TENDER_ANALYZED` |
| `TENDER_ANALYZED` | Tender Analyst deconstructs clauses with source coordinates | `@TenderAnalyst` | `EVIDENCE_MAPPED` |
| `EVIDENCE_MAPPED` | ProofLink maps company evidence to requirements | `@EvidenceResearcher` | `COMPLIANCE_EVALUATED` |
| `COMPLIANCE_EVALUATED` | Compliance Officer evaluates matrix, gaps, and risk levels | `@ComplianceOfficer` | `PROPOSAL_DRAFTED` |
| `PROPOSAL_DRAFTED` | Proposal Architect drafts 5-chapter response with ProofLink citations | `@ProposalArchitect` | `PROPOSAL_AUDITED` |
| `PROPOSAL_AUDITED` | Bid Auditor evaluates veracity and issues Readiness Verdict | `@BidAuditor` | `HUMAN_REVIEW_PENDING`, `REVISION_REQUIRED` |
| `HUMAN_REVIEW_PENDING` | Awaiting authorized human review and sign-off in War Room | Human Lead | `BID_APPROVED`, `REVISION_REQUIRED` |
| `REVISION_REQUIRED` | Audit findings or human reviewer requested modifications | Auditor / Human | `PROPOSAL_DRAFTED` |
| `BID_APPROVED` | Formal sign-off recorded; submission package export unlocked | Bid Director | *(Terminal Stage)* |

---

## 3. Transition Rules & Error Handling

- **Invalid Transition Blocking:** Attempting to skip stages (e.g. going directly from `WORKSPACE_INITIALIZED` to `PROPOSAL_DRAFTED`) raises a `WorkflowError` with HTTP 400 status.
- **Rollback and Re-drafting:** If a proposal receives a `REVISION_REQUIRED` verdict, the workflow transitions back to `PROPOSAL_DRAFTED`, incrementing the proposal version (`v2.0`) and preserving the previous version in `proposal_revisions`.
- **Immutable Transition Log:** Every transition stores the prior stage, target stage, executing actor, UTC timestamp, and justification notes in `workflow_states.stage_history`.

---

## 4. Automatic Step Execution

Calling `POST /api/v1/tenders/{tender_id}/workflow/step` evaluates the current state and triggers the next logical pipeline step automatically, enabling both step-by-step interactive human orchestration and end-to-end automated pipelines.
