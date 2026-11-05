# TENDERFORGE — PHASE 2 TOOL CATALOGUE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Protocol:** Model Context Protocol (MCP) & Switch Agent Bridge  
**Date:** November 2026  

---

## 1. Overview

TenderForge exposes 17 strictly typed, deterministic tools. Agents invoke these tools via the Switch Agent Bridge or standard Model Context Protocol (MCP) clients.

Every tool call undergoes runtime authorization checks against the calling agent's permissions declared in its configuration YAML.

---

## 2. Complete Tool Catalogue

| # | Tool Name | Description | Parameters | Permitted Callers |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `create_tender_workspace` | Creates an isolated workspace for a procurement response. | `name` (str), `organization_id` (str), `description` (str, opt) | Humans, System |
| **2** | `upload_tender_document` | Uploads, validates, hashes, and segments a tender document (PDF, DOCX, TXT, XLSX). | `workspace_id` (str), `filename` (str), `content_base64` (str), `category` (str, opt) | Humans, System |
| **3** | `upload_company_evidence` | Ingests and registers an organizational proof record (audit, ISO certificate, past project, policy). | `organization_id` (str), `workspace_id` (str), `title` (str), `evidence_type` (str), `filename` (str), `content_base64` (str), `issuer` (str, opt), `reference_number` (str, opt), `tags` (list, opt) | `@EvidenceResearcher`, Humans |
| **4** | `get_tender_overview` | Retrieves tender metadata, reference numbers, dates, authority, and status. | `tender_id` (str) | `@TenderAnalyst`, `@ProposalArchitect`, `@BidAuditor`, Humans |
| **5** | `analyze_tender` | Triggers the Tender Analyst to extract structured requirements with page and character coordinates. | `tender_id` (str) | `@TenderAnalyst`, Humans |
| **6** | `get_tender_requirements` | Retrieves extracted requirements filtered by category or classification. | `tender_id` (str), `category` (str, opt), `classification` (str, opt) | All 5 Agents, Humans |
| **7** | `search_company_evidence` | Searches the company evidence repository by query, type, or tags. | `organization_id` (str), `query` (str, opt), `evidence_type` (str, opt) | `@ComplianceOfficer`, `@EvidenceResearcher`, `@ProposalArchitect`, Humans |
| **8** | `get_evidence_details` | Fetches full metadata, extracted facts, and document links for a specific evidence item. | `evidence_id` (str) | `@EvidenceResearcher`, `@ProposalArchitect`, `@BidAuditor`, Humans |
| **9** | `evaluate_compliance` | Evaluates requirements against evidence to compute compliance statuses and risk levels. | `tender_id` (str) | `@ComplianceOfficer`, Humans |
| **10** | `get_compliance_matrix` | Retrieves the latest compliance matrix, risk profile, and remedial action items. | `tender_id` (str) | `@ComplianceOfficer`, `@ProposalArchitect`, Humans |
| **11** | `create_proposal_draft` | Generates a 5-chapter evidence-backed proposal with embedded ProofLink citations and DOCX export. | `tender_id` (str), `title` (str, opt) | `@ProposalArchitect`, Humans |
| **12** | `get_proposal_revision` | Retrieves proposal text, claims, and ProofLink citations by version number. | `proposal_id` (str), `version` (int, opt) | `@ProposalArchitect`, `@BidAuditor`, Humans |
| **13** | `audit_proposal` | Triggers the independent Bid Auditor to review veracity, calculate readiness score, and issue verdict. | `proposal_id` (str) | `@BidAuditor`, Humans |
| **14** | `get_audit_report` | Retrieves latest audit findings, claim statistics, and submission readiness verdict. | `proposal_id` (str) | `@BidAuditor`, Humans |
| **15** | `request_human_review` | Broadcasts a high-priority review request to the Tender War Room for human decision. | `tender_id` (str), `reason` (str), `severity` (str, opt), `proposal_id` (str, opt) | All 5 Agents, Humans |
| **16** | `record_human_decision` | Records an immutable human approval or rejection decision with cryptographic SHA-256 signature hash. | `tender_id` (str), `proposal_id` (str), `user_id` (str), `user_name` (str), `user_role` (str), `decision` (str), `comments` (str) | **Humans Only** (AI Agents Blocked) |
| **17** | `export_bid_package` | Packages the complete submission-ready ZIP bundle (DOCX proposal, XLSX matrix, audit, and sign-off certificate). | `tender_id` (str), `proposal_id` (str), `require_human_approval` (bool, opt) | Humans, System |

---

## 3. Tool Schema Example: Model Context Protocol (MCP)

```json
{
  "name": "create_proposal_draft",
  "description": "Generate an evidence-backed proposal draft with embedded ProofLink citations.",
  "parameters": {
    "type": "object",
    "properties": {
      "tender_id": {
        "type": "string",
        "description": "Unique identifier of the tender"
      },
      "title": {
        "type": "string",
        "description": "Optional custom proposal title"
      }
    },
    "required": ["tender_id"]
  }
}
```
