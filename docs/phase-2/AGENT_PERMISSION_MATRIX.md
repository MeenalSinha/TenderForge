# TENDERFORGE — AGENT PERMISSION & RBAC MATRIX

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Security Principle: Strict Least Privilege

In TenderForge, AI agents operate under the principle of **strict least privilege**. Each agent is granted access only to the tools required to fulfill its specialized domain responsibility.

Runtime enforcement is verified by `ToolDispatcher.execute()` against the configuration loaded in `AgentRegistry`. If an agent attempts to execute an unauthorized tool or if prompt injection attempts to alter its permissions, execution is blocked immediately with a `SecurityError`.

Furthermore, **governance and approval tools cannot be executed by any AI agent under any circumstances**. Only human users with verified authority can record approval decisions.

---

## 2. Agent Role Permission Matrix

| Tool Name | Tender Analyst | Compliance Officer | Evidence Researcher | Proposal Architect | Bid Auditor | Human Lead / Director |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `create_tender_workspace` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `upload_tender_document` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `upload_company_evidence` | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| `get_tender_overview` | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `analyze_tender` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `get_tender_requirements` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `search_company_evidence` | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `get_evidence_details` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `evaluate_compliance` | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| `get_compliance_matrix` | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| `create_proposal_draft` | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| `get_proposal_revision` | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `audit_proposal` | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `get_audit_report` | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `request_human_review` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `record_human_decision` | 🚫 BLOCKED | 🚫 BLOCKED | 🚫 BLOCKED | 🚫 BLOCKED | 🚫 BLOCKED | ✅ **HUMAN ONLY** |
| `export_bid_package` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 3. Tool Segregation Rationale

1. **Separation of Drafting and Auditing:**
   - `@ProposalArchitect` cannot invoke `audit_proposal` or `get_audit_report`.
   - `@BidAuditor` cannot invoke `create_proposal_draft`.
   - This prevents conflict of interest and preserves independent scrutiny.
2. **Separation of Extraction and Evaluation:**
   - `@TenderAnalyst` identifies what the tender demands.
   - `@ComplianceOfficer` evaluates whether the organization qualifies.
3. **Hard Governance Gate:**
   - `record_human_decision` is blocked at the dispatcher level for any caller with `caller_type == "agent"`, ensuring zero autonomous bid submission.
