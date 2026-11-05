# TENDERFORGE — COMPLIANCE ASSESSMENT ENGINE GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Objectives

The **Compliance Assessment Engine** (`backend/app/services/compliance_service.py`) automates the evaluation of tender requirements against verified company evidence to generate a structured, auditable **Compliance Matrix**.

It serves as the analytical foundation for the `@ComplianceOfficer` agent persona inside the Tender War Room.

---

## 2. Evaluation Logic & Categories

Requirements are evaluated across four standardized procurement categories:
1. **Eligibility & Registration:** Legal entity existence, statutory good standing, tax clearance, local presence.
2. **Technical Specifications:** Equipment capabilities, SLA metrics, high-availability architecture, cybersecurity.
3. **Financial Capacity:** Minimum annual turnover, net worth, bid security / Earnest Money Deposit (EMD).
4. **Submission Requirements:** Certified copies, notarized declarations, bid format compliance.

---

## 3. Compliance Statuses & Risk Ratings

### 3.1 Status Classification
- **`Compliant`:** All mandatory aspects of the clause are fully substantiated by `Verified` or `Human Confirmed` evidence.
- **`Partially Compliant`:** Meets core aspects but misses minor technical specifications or requires subcontracting.
- **`Clarification Required`:** Grounding evidence is pending human inspection or ambiguous.
- **`Non-Compliant`:** Requirement is `Unsupported` or `Contradicted`. If the clause is `mandatory`, this triggers an immediate disqualification risk.

### 3.2 Risk Levels
- **`Low`:** Fully compliant, verified documentation on file.
- **`Medium`:** Clarification needed or minor optional clause missing.
- **`High`:** Missing documentation on important technical specifications.
- **`Critical`:** Non-compliance on mandatory eligibility criteria (immediate disqualification).

---

## 4. Output Formats

1. **REST API JSON Payload:** Available via `GET /api/v1/tenders/{id}/compliance`.
2. **Excel Workbook (`.xlsx`):** Formatted spreadsheet generated via `openpyxl` with conditional green/red/yellow status highlights, suitable for inclusion in formal bid packages.
3. **Switch War Room Announcement:** Markdown-formatted summary posted to the Tender War Room channel by `@ComplianceOfficer`.
