# TenderForge Advanced ProofLink Intelligence

## 1. Overview & Problem Definition

In tender preparation, unsubstantiated claims lead to bid disqualification, legal disputes, or loss of credibility. Conventional AI proposals hallucinate statistics or cite outdated certificates.

**ProofLink** is TenderForge's proprietary cryptographic traceability and evidence governance engine. In Phase 3, ProofLink is upgraded to **Advanced ProofLink Intelligence**, introducing:
1. Multi-attribute Evidence Freshness Tracking & Expiration Auditing
2. Cross-Document Factual Contradiction Detection
3. End-to-End Cryptographic Claim Lineage Graph
4. Evidence Mutation Invalidation Cascades.

```
+--------------------------------------------------------------------------------------------------+
|                              ProofLink Cryptographic Lineage Graph                               |
+--------------------------------------------------------------------------------------------------+
   [Tender Requirement]           Clause 4.1: Audited annual turnover exceeding $10M
           |
           v
   [Company Evidence]             PwC Audited Financial Statements FY24 (ID: ev-992)
           |
           v
   [Verifiable Extract]           "Total consolidated net turnover for FY24: $18,500,000"
           |
           v
   [Proposal Claim]               "Apex Defense generated verified annual turnover of $18.5M"
           |
           v
   [Independent Audit]            BidAuditor Verdict: Verified (Score: 100%, 0 Contradictions)
           |
           v
   [Approved Section]             Section 2.1 — Financial Qualifications (Approved)
           |
           v
  SHA-256 Lineage Hash:           dd7df70f09334da9f5bc931ced2c62981fde04633727c9dfcbc0d5d0225405eb
```

---

## 2. Extended Evidence Metadata & Freshness Tracking

Every evidence asset registered in the repository contains extended governance metadata:
- `evidence_type`: `financial_audit`, `certification`, `past_project`, `statutory_registration`, `policy`, `cv_personnel`
- `issue_date` & `expiry_date`: Timezone-aware expiration horizons
- `issuer`: Verifying authority (e.g., BSI, Bureau Veritas, PwC, State Authority)
- `reference_number`: Official certificate or filing code
- `status`: `valid`, `expired`, `pending_verification`, `revoked`.

### Proactive Expiration Audit
The freshness audit checks every active evidence document against the tender's submission deadline and delivery timeframe:
- **`EXPIRED`**: The document's expiry date has already passed. The status is immediately updated to `expired`, and any active proposal claims relying on it are marked for re-verification.
- **`EXPIRING_SOON`**: The document will expire within a configurable warning window (default: 90 days, or before the tender submission deadline). Alerts are dispatched to the tender war room.
- **`VALID`**: Document is current throughout the tender lifecycle.

---

## 3. Cross-Document Contradiction Detection

Organizations often hold multiple documents with slightly different figures or dates (e.g., draft vs final audited reports, different accounting methodologies, or superseded certificates).

The contradiction detection engine runs pairwise and cross-repository consistency checks:

1. **Financial Discrepancies**: Compares values for reported `turnover`, `revenue`, `net_profit`, or fiscal year metrics across audits, annual reports, and bank letters.
2. **Certification Expiry Conflicts**: Compares claims in the corporate profile against actual certificates in the repository. If the profile claims active ISO 27001, but the certificate is expired, an alert is raised.
3. **Contradiction Severity Scoring**:
   - `Critical`: Numerical discrepancies on mandatory criteria (e.g., turnover, balance sheet).
   - `High`: Validity or expiry dates conflict.
   - `Medium`: Minor naming or jurisdictional variation.
4. **Resolution Tracking**: Contradictions can only be closed by an authorized human with mandatory explanatory notes and sign-off.

---

## 4. End-to-End Cryptographic Lineage Architecture

For every factual claim generated in a proposal, TenderForge constructs an immutable `ClaimLineage` node.

### Deterministic Lineage Hash
The lineage hash is computed over all linking nodes:
$$\text{LineageHash} = \text{SHA256}(\text{TenderID} \parallel \text{ProposalID} \parallel \text{ReqID} \parallel \text{EvidenceID} \parallel \text{Section} \parallel \text{ClaimText} \parallel \text{EvidenceExtract})$$

This creates a verifiable audit trail:
- Reviewers can click any claim in the proposal and inspect the exact source sentence in the original evidence document.
- The independent `BidAuditor` checks claim veracity against the lineage graph.

---

## 5. Evidence Change Invalidation Cascade

When an evidence record is modified, revoked, or marked expired:
1. `AdvancedProofLinkService.invalidate_on_evidence_change()` queries all dependent `ClaimLineage` records.
2. The `approval_status` of each linked claim is transitioned to `invalidated`.
3. The parent `Proposal` status is reset from `approved` to `drafting`.
4. A notification is posted to the tender Switch room alerting the team that an evidence modification requires proposal delta-review.
