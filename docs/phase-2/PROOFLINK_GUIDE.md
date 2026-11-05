# TENDERFORGE — PROOFLINK™ EVIDENCE TRACEABILITY ENGINE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Executive Summary & Value Proposition

The single most critical differentiator of TenderForge is:

**ProofLink™ — The Evidence Traceability Engine**

Existing proposal tools often hallucinate qualifications or make ungrounded claims (e.g. "We have delivered 20 major telecom networks") without verifying whether the company actually has supporting documentation. If an evaluation committee asks for supporting proof, unsubstantiated claims result in bid disqualification.

ProofLink creates a verifiable, bidirectional citation link between every factual assertion in a proposal, every tender requirement, and the physical company records supporting it.

---

## 2. Traceable Status Lifecycle

Every ProofLink match is assigned one of five explicit statuses:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ProofLink Status Topology                       │
├────────────────────────────────────────────────────────────────────────┤
│  [VERIFIED]         ◄── Evidence exists, verified, dates/values valid  │
│  [HUMAN CONFIRMED]  ◄── Authorized human expert signed off on match    │
│  [PENDING]          ◄── Candidate match located; requires review       │
│  [UNSUPPORTED]      ◄── Zero supporting records found in repository    │
│  [CONTRADICTED]     ◄── Evidence explicitly conflicts with requirement │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Status Definitions & Business Rules
1. **`Verified`:** Documented evidence directly satisfies requirement criteria (e.g. audited revenue is $4.9M and requirement demands $3.0M; or valid ISO 9001 certificate is active).
2. **`Human Confirmed`:** An authorized human user (Bid Director, Legal Counsel) has inspected and confirmed the assertion.
3. **`Pending`:** Evidence candidate located via semantic/keyword similarity, but exact numbers or validity dates require human inspection.
4. **`Unsupported`:** The repository contains no documentary proof supporting the requirement. Triggers an explicit `[ACTION REQUIRED]` placeholder in proposal drafts.
5. **`Contradicted`:** Official company records explicitly contradict the requirement or proposal claim (e.g. company reports 3 years of experience, but tender demands 5 years; or certificate has expired).

---

## 3. Discrepancy & Contradiction Detection

ProofLink evaluates quantitative criteria programmatically:
- **Financial Turnover:** Extracts dollar amounts from clauses and compares them against audited statements. If `audited_turnover < required_turnover`, marks as `Contradicted`.
- **Quality Certifications:** Extracts ISO codes and checks expiration dates. If `expiry_date < now`, marks as `Contradicted` with the note `"Certificate expired; renewal needed."`
- **Years of Experience:** Compares incorporation date from `OrganizationProfile` against minimum years. If `years_in_business < required_years`, flags contradiction.

---

## 4. Citation Marker Structure

Inside proposal sections, ProofLink citations are embedded verbatim:
```text
In direct fulfillment of Clause 1.2, our organization maintains an active ISO 9001:2015 
quality management certification certified by DNV GL. 
[ProofLink: 72003018-0fb0-48c3-998a-d8e7689aef32 | Status: Verified]
```

When exported to Microsoft Word (`.docx`), ProofLink markers are formatted as professional footnote citations with color-coded provenance indicators (Green for Verified, Red for Contradicted, Amber for Pending).
