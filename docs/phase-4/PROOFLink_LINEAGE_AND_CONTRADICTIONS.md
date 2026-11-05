# TenderForge Phase 4: ProofLink Lineage & Contradiction Resolution

## 1. Overview & Anti-Hallucination Philosophy

The primary reason AI-generated proposals fail scrutiny is **unsubstantiated claims and factual hallucination**. TenderForge addresses this at the architectural core via **ProofLink** — a cryptographic lineage and evidence-anchoring system connecting every factual statement in a proposal to an audited corporate source document.

```
+-----------------------------------------------------------------------------------------+
|                                    PROPOSAL DRAFT                                       |
|  "Our primary data center maintains Tier III uptime with ISO 27001 certified controls   |
|   [ProofLink: REF-2024-ISO27001-P12] and SOC 2 Type II compliance."                    |
+-----------------------------------------------------------------------------------------+
                                        | (Resolves Lineage)
                                        v
+-----------------------------------------------------------------------------------------+
|                                 PROOFLink LINEAGE ANCHOR                                |
|  - Reference ID: REF-2024-ISO27001-P12                                                  |
|  - Source File: "ISO_27001_Certificate_BSI_2024.pdf"                                    |
|  - Content SHA-256: 4a8e2b9c7d1f5e8a3c...                                               |
|  - Extracted Text: "...certifies that Acme Corp operates an ISMS compliant with..."     |
|  - Target Coordinates: Page 1, Paragraph 2, Characters 142-288                          |
|  - Evidence Freshness: VALID (Expires: 2027-10-15, 345 days remaining)                  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Cryptographic Lineage Verification

Every ProofLink anchor records:
1. **Document Fingerprint**: SHA-256 checksum of the exact source PDF/DOCX binary.
2. **Positional Coordinates**: Page number, start char offset, end char offset.
3. **Verbatim Excerpt**: Exact byte-matched snippet from the parsed document.
4. **Extraction Confidence**: Numerical confidence metric (0.00 to 1.00) assigned during parsing.
5. **Freshness Assessment**: Evaluated against the tender submission deadline to ensure certificates do not expire during the tender evaluation or contract award period.

---

## 3. Contradiction Resolution Engine

When multiple corporate documents present conflicting factual assertions, the **Contradiction Resolution Engine** intercepts the discrepancy before proposal export.

### 3.1 Common Contradiction Types
- **Conflicting Metrics**: Document A states "Turnover is $15M", Document B states "Turnover is $12.5M".
- **Date Inconsistencies**: Document A indicates project completion in 2023; Document B indicates 2024.
- **Jurisdictional Clashes**: Different corporate entities or tax identifiers referenced across past performance sheets.

### 3.2 Resolution Workflow
1. **Automated Interception**: During compliance cross-check, the `compliance_officer` agent runs semantic comparison across all cited evidence.
2. **Flagged Anomaly**: The proposal section is marked with a `CONTRADICTION_FLAG` and locked against final release.
3. **Interactive Resolver UI**: The frontend presents both contradictory snippets side-by-side with document metadata, creation dates, and issuing authorities.
4. **Authoritative Human Designation**: The user designates the prevailing document (e.g., "Audited Financial Report 2024 supersedes preliminary balance sheet") and enters a resolution rationale.
5. **Audit Sealing**: The resolution is archived with timestamp, user ID, and rationale.

```
+-----------------------------------------------------------------------------------------+
|                             CONTRADICTION RESOLVER MODAL                                |
+-----------------------------------------------------------------------------------------+
| Requirement: "Minimum Annual Turnover > $10,000,000 for FY 2023-24"                     |
+-----------------------------------------------------------------------------------------+
| SOURCE A: Audited_Financials_2024.pdf       | SOURCE B: Marketing_Overview_2024.pdf      |
| Excerpt: "Net turnover: $12,450,000"        | Excerpt: "Annual revenue exceeded $18M"   |
| Date: 2024-06-30 | Confidence: 1.00        | Date: 2024-02-15 | Confidence: 0.72       |
+---------------------------------------------+-------------------------------------------+
| [(*) Select Source A as Canonical Authority]                                            |
| Resolution Rationale: "Audited financial statements by KPMG reflect legal net turnover." |
| [Confirm Resolution & Unlock Section]                                                   |
+-----------------------------------------------------------------------------------------+
```
