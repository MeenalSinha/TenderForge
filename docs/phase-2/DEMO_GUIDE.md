# TENDERFORGE — SYNTHETIC DEMONSTRATION GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview

The synthetic demonstration script (`scripts/demo_phase2.py`) provides an end-to-end, zero-cost, fully reproducible execution of TenderForge Phase 2 capabilities.

It runs headlessly, requires no external cloud credentials, and exercises the entire collaborative multi-agent workflow from organization setup to final submission bundle generation.

---

## 2. How to Run the Demonstration

From the project root:

```bash
# Execute the Phase 2 Synthetic Demonstration
python scripts/demo_phase2.py
```

---

## 3. Step-by-Step Execution Walkthrough

### Step 1: Bidding Organization Setup & Evidence Ingestion
- Creates organization `Aegis Defense & Technologies Inc.`
- Ingests audited turnover metrics ($4,933,333 3-year avg) and active ISO 9001/ISO 27001 certifications.
- Registers 3 verified proof records (PWC Audit Report, DNV GL ISO Certificate, DoD Tactical Network Project).

### Step 2: Switch Tender War Room Initialization
- Creates procurement tender `National Enterprise Communications Network RFP` (Ref: `RFP-2026-DEFENSE-01`).
- Establishes isolated Switch War Room channel `#tender-rfp-2026-defense`.
- Registers 7 collaborative personas (5 AI agents + Bid Director + Legal Counsel).

### Step 3: Tender Analyst Deconstruction
- Ingests synthetic tender specification text.
- Extracts 6 structured requirements with exact source page numbers and verbatim excerpts.
- Emits handoff notification to `@ComplianceOfficer`.

### Step 4: ProofLink Evidence Matching Engine
- Connects mandatory requirements to verified corporate evidence.
- Verified audited turnover meets the $3,000,000 threshold.
- Verified active ISO 9001:2015 certificate from DNV GL.
- Verified past performance in tactical defense networks.

### Step 5: Compliance Officer Evaluation
- Evaluates compliance matrix: Status=`Compliant`, Risk=`Low`.
- Verifies zero critical eligibility gaps.

### Step 6: Proposal Architect Drafting & DOCX Export
- Generates complete 5-chapter technical and compliance proposal.
- Embeds ProofLink citations and verifies zero hallucinations.
- Creates styled Microsoft Word document (`proposal_..._v1.docx`).

### Step 7: Independent Bid Auditor
- Conducts blind audit of proposal claims against tender and evidence records.
- Computes Bid Readiness Score (100.0 / 100.0).
- Issues formal verdict: `READY FOR SUBMISSION`.

### Step 8: Human Governance Gate & Digital Sign-Off
- **Security Check:** Attempts export before approval; verified blocked by security gate.
- Authorized Bid Director (Marcus Vance) records approval with formal justification.
- Computes cryptographic SHA-256 digital signature hash.

### Step 9: Final Bid Package Export
- Compiles submission ZIP bundle containing:
  1. `01_Technical_Proposal_v1.docx`
  2. `02_Compliance_Matrix.xlsx`
  3. `03_Independent_Bid_Audit_Report.txt`
  4. `04_Human_Sign_Off_Certificate.json`
- Prints final success confirmation.
