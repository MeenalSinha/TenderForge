# TENDERFORGE — HUMAN-IN-THE-LOOP GOVERNANCE & APPROVAL GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Governance Principle: Zero Autonomous Submission

A non-negotiable rule of TenderForge is that **AI agents cannot submit bids or grant final approvals autonomously**.

While AI agents extract requirements, map evidence, draft chapters, and compute audit readiness, the final authority and legal accountability reside exclusively with authorized human directors.

The system enforces a hard architectural gate: the Final Bid Package Export Service (`backend/app/services/export_service.py`) strictly refuses to generate or export submission packages unless an immutable, verified `Approved` decision is present in the `human_approvals` database table.

---

## 2. Decision Workflow & Roles

```
Proposal Drafted ──► Bid Audit ──► Human Review Request ──► Sign-Off Decision ──► Signature Hash ──► Submission Unlocked
(@ProposalArchitect) (@BidAuditor)   (War Room Mention)      (Approved/Rejected)     (SHA-256 Digest)   (Export Bundle)
```

### Authorized Signatory Roles
- **Bid Director / VP of Proposals:** Authorized to grant final submission approval.
- **Legal Counsel:** Authorized to verify statutory declarations and liability caps.
- **Commercial Lead:** Authorized to confirm pricing, turnover declarations, and bid bond amounts.

---

## 3. Cryptographic Signature Hash

When a human records an approval decision, TenderForge computes a deterministic SHA-256 cryptographic signature hash:

$$\text{Signature Hash} = \text{SHA-256}(\text{TenderID} \parallel \text{ProposalID} \parallel \text{AuditID} \parallel \text{Decision} \parallel \text{UserID} \parallel \text{Role} \parallel \text{Timestamp} \parallel \text{Comments})$$

This creates an immutable digital certificate stored in `human_approvals` and exported inside the final bid bundle (`04_Human_Sign_Off_Certificate.json`). Any post-approval modification to the proposal invalidates the certificate.

---

## 4. API & Command Usage

### Slash Command (in Tender War Room)
```bash
/approve Comprehensive technical and compliance audit verified. Authorized for formal submission.
```

### REST API Endpoint
`POST /api/v1/proposals/{proposal_id}/approve`
```json
{
  "tender_id": "8414d51d-7d41-46f8-94dd-b221a06da32f",
  "user_id": "lead_vp_marcus",
  "user_name": "Marcus Vance",
  "user_role": "Senior Vice President & Bid Director",
  "decision": "Approved",
  "comments": "Inspected technical architecture and audited turnover verification. Approved."
}
```
