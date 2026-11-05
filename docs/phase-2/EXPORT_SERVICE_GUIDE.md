# TENDERFORGE — FINAL BID PACKAGE EXPORT SERVICE GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Business Purpose

Responding to tenders requires delivering comprehensive, multi-format submission packages. Evaluators require technical proposals in Word/PDF, compliance declarations in structured spreadsheets, and formal non-collusion/sign-off certificates.

The **Final Bid Package Export Service** (`backend/app/services/export_service.py`) automates the compilation, styling, and packaging of the complete submission bundle into an encrypted, verified `.zip` archive.

---

## 2. Submission Bundle Contents

| Filename | Format | Description | Engine / Library |
| :--- | :---: | :--- | :--- |
| `01_Technical_Proposal_vX.docx` | DOCX | Complete 5-chapter proposal containing technical approach, solution architecture, past performance, and ProofLink citations. | `python-docx` |
| `02_Compliance_Matrix.xlsx` | XLSX | Styled compliance spreadsheet with green/red/yellow conditional highlights, risk ratings, and evidence summaries. | `openpyxl` |
| `03_Independent_Bid_Audit_Report.txt` | TXT | Full audit report containing the Bid Readiness Score, claim breakdown, and severity findings. | Internal Audit Engine |
| `04_Human_Sign_Off_Certificate.json` | JSON | Cryptographic digital signature certificate containing the SHA-256 hash, signatory identity, and formal approval remarks. | Internal Cryptographic Signer |

---

## 3. Human Approval Enforcement Gate

The export service strictly refuses to package proposals that lack verified human approval:

```python
approval = db.query(HumanApproval).filter(
    HumanApproval.proposal_id == proposal_id,
    HumanApproval.decision == "Approved",
).first()

if require_human_approval and not approval:
    raise SecurityError("Bid package cannot be exported without verified human approval sign-off.")
```

If a user or automated agent attempts to export a package prior to sign-off, an HTTP 403 Forbidden error is returned, guaranteeing zero unapproved submissions.

---

## 4. API Usage

`POST /api/v1/proposals/{proposal_id}/export`
```json
{
  "tender_id": "8414d51d-7d41-46f8-94dd-b221a06da32f",
  "require_human_approval": true
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "package_path": "storage/exports/bid_package_RFP-2026-DEFENSE-01_20261105_080229.zip",
    "filename": "bid_package_RFP-2026-DEFENSE-01_20261105_080229.zip"
  }
}
```
