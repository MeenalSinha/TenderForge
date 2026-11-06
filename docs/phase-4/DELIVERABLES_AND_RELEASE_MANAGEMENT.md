# TenderForge Phase 4: Deliverables & Release Management

## 1. Overview & Release Packaging

When a proposal completes technical authoring, financial modeling, and executive approval, TenderForge generates a comprehensive, sealed **Submission Release Bundle**. This bundle contains all artifacts required for official tender submission along with a tamper-evident cryptographic manifest.

---

## 2. Release Package Contents

The generated ZIP archive (`TenderForge_Submission_[Tender_Ref].zip`) includes:

```
TenderForge_Submission_TND-2026-081/
|-- 01_Executive_Summary.pdf
|-- 02_Technical_Proposal.docx
|-- 03_Financial_BOQ_Proposal.xlsx
|-- 04_Compliance_Traceability_Matrix.pdf
|-- 05_Evidence_Vault/
|   |-- ISO_27001_Certificate.pdf
|   |-- Audited_Financial_Statement_FY24.pdf
|   |-- Client_Completion_Certificate_Alpha.pdf
|-- 06_Risk_Register_and_Mitigations.pdf
|-- MANIFEST.json
|-- CHECKSUMS.sha256
```

---

## 3. Cryptographic Manifest & Integrity Verification

To prevent post-approval tampering or corrupt uploads, TenderForge computes SHA-256 digests for every individual file and records them in `MANIFEST.json`.

```json
{
  "tender_id": "tnd-smart-city-transport-2026",
  "tender_reference": "TND-2026-081",
  "organization_id": "org-acme-global",
  "release_timestamp": "2026-11-05T19:30:00Z",
  "released_by": {
    "user_id": "usr-jane-doe-admin",
    "email": "jane.doe@acme.com",
    "role": "admin"
  },
  "executive_approval": {
    "approved_at": "2026-11-05T19:25:00Z",
    "signed_off_by": "usr-john-smith-vp",
    "approval_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "artifacts": [
    {
      "filename": "02_Technical_Proposal.docx",
      "sha256": "8a3f9b1c7d2e5a6b0c4d8e1f3a5b7c9d0e2f4a6b8c1d3e5a7b9c0d2e4f6a8b1c",
      "size_bytes": 142580,
      "prooflinks_count": 24
    },
    {
      "filename": "03_Financial_BOQ_Proposal.xlsx",
      "sha256": "4b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c",
      "size_bytes": 48210,
      "calculated_gross_total": "156991.33"
    }
  ]
}
```

---

## 4. Release Validation Gates

Before a submission release package can be compiled:
1. **Zero Open Contradictions**: All flagged evidence contradictions must be formally resolved.
2. **Zero Unapproved Critical Risks**: All risks scored $\ge 16$ on the 5x5 matrix must have approved mitigations.
3. **Mandatory Executive Sign-Off**: The proposal status must be transitioned to `APPROVED` by a user with `admin` or `bid_manager` credentials.
4. **BOQ Mathematical Verification**: Line item totals must match the grand total exactly with zero arithmetic drift.

---

## 5. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/proposals/{id}/release` | Trigger release packaging and generate sealed ZIP archive |
| `GET` | `/api/v1/proposals/{id}/manifest` | Retrieve cryptographic manifest and SHA-256 hashes |
| `GET` | `/api/v1/proposals/{id}/download` | Download complete submission release bundle |

