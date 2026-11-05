# TENDERFORGE — MULTI-AGENT UI & UX COLLABORATION GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. UX Philosophy: Human-Agent Teaming

The TenderForge user experience is built around the principle of **collaborative transparency**. Rather than functioning as a black-box document generator, the platform surfaces the reasoning, citations, and risk assessments of specialized AI agents in real time, placing human experts in active command.

---

## 2. Key UI Components

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TenderForge Collaboration Hub                   │
├──────────────────────────────────┬─────────────────────────────────────┤
│   Tender War Room Chat           │   Live Tender Artifact Pane         │
│   (Powered by Switch/Mattermost) │   (Dynamic Multi-Tab Inspector)     │
│                                  │                                     │
│  [@TenderAnalyst] Extracted      │  [Tab: Requirements] [Tab: ProofLink]│
│  6 mandatory requirements.       │  [Tab: Compliance]   [Tab: Proposal] │
│                                  │                                     │
│  [@ComplianceOfficer] Turnover   │  Requirement 1.1: Turnover $3M      │
│  requirement is $3M.             │  ProofLink: FY25 Audit (PWC)        │
│                                  │  Status: [VERIFIED - 95% Confidence]│
│  [@EvidenceResearcher] Found PWC │                                     │
│  audit confirming $4.9M revenue. │  [Action: Review Citation]          │
│                                  │                                     │
│  [@BidAuditor] Score: 100.0%.    │  Readiness Verdict: READY           │
│  Ready for Submission.           │  Score: 100.0 / 100.0               │
│                                  │                                     │
│  [Human Sign-Off Bar]            │  [Download DOCX] [Export Package]   │
│  [Approve Bid]  [Request Changes]│                                     │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### 2.1 The Tender War Room Stream
- Displays conversation threads between agents and human team members.
- Agent avatars visually indicate specialization:
  - 🔍 **Tender Analyst:** Blue icon (Document Intelligence).
  - ⚖️ **Compliance Officer:** Purple icon (Regulatory Evaluation).
  - 📂 **Evidence Researcher:** Amber icon (Corporate Evidence).
  - ✍️ **Proposal Architect:** Green icon (Technical Writing).
  - 🛡️ **Bid Auditor:** Red/Gold icon (Independent Risk Assessment).
- Interactive action cards: `[Approve Link]`, `[Review Gap]`, `[View Proposal Chapter]`.

### 2.2 ProofLink Interactive Inspector
- Hovering over any claim in the proposal highlights the corresponding source document and page.
- Clicking a citation opens a side-by-side view showing the exact paragraph excerpt and document metadata.

### 2.3 Compliance Matrix Heatmap
- Clean visual grid categorizing requirements by category and risk level.
- Green badges for `Compliant`, Red for `Non-Compliant`, Yellow for `Clarification Required`.
- One-click filters to surface high-risk disqualification items.

### 2.4 Human Sign-Off Modal
- Displays full proposal audit summary and checklist before allowing submission.
- Requires mandatory text comments and role verification.
- Generates visual digital certificate with the SHA-256 hash.
