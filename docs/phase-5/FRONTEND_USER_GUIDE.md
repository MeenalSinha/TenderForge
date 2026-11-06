# Phase 5: Enterprise Frontend User Guide

## 1. Overview

Phase 5 introduces **8 new dedicated frontend views**, expanding TenderForge’s enterprise UI from 15 to **23 comprehensive operational views**.

The frontend is accessible at `http://localhost:8000/` or via the standalone development server at `http://localhost:5173/`.

---

## 2. Phase 5 Navigation & Views Overview

```
TenderForge Enterprise Navigation
├── Workspace & Core (Phase 1-4)
│   ├── Dashboard
│   ├── Tender Workspace
│   ├── Document Intelligence
│   ├── ProofLink Vault
│   ├── Compliance Matrix
│   ├── Financial Workspace
│   ├── Proposal Studio
│   └── Switch War Room
│
└── Procurement Intelligence (Phase 5)
    ├── 1. Opportunity Discovery (`/opportunities`)
    ├── 2. Recommendations & Matching (`/recommendations`)
    ├── 3. Procurement Sources (`/sources`)
    ├── 4. Continuous Monitoring (`/monitoring`)
    ├── 5. Corrigenda & Amendments (`/amendments`)
    ├── 6. Market Analytics (`/market`)
    ├── 7. Competitor Benchmarks (`/competitors`)
    └── 8. Closed-Loop Bid Learning (`/learning`)
```

---

## 3. Detailed Walkthrough of Phase 5 Views

### 3.1 Opportunity Discovery View
- **Purpose**: Search, filter, and inspect discovered procurement notices from external feeds.
- **Features**:
  - Filter by Procurement Category (IT, Healthcare, Infrastructure, Defense).
  - Search by Issuing Authority or Title keywords.
  - Interactive "Evaluate Match" and "Promote to Workspace" action triggers.

### 3.2 Recommendations & Matching View
- **Purpose**: View AI-assessed opportunity recommendations ranked by suitability score.
- **Features**:
  - Visual color-coded recommendation badges:
    - Green: `STRONGLY RECOMMENDED` ($\ge 75\%$)
    - Amber: `RECOMMENDED WITH CONDITIONS` ($55-74\%$)
    - Red: `PURSUIT NOT RECOMMENDED` ($< 55\%$ or hard gate failure)
  - Interactive 9-dimension radar breakdown.
  - Transparent Explainability Drawer detailing Strengths, Weaknesses, Gate Failures, and Missing Evidence Artifacts.

### 3.3 Procurement Sources View
- **Purpose**: Manage configured procurement portals and ingest feeds.
- **Features**:
  - Connector cards displaying connector type (`open_tender`, `mock_sandbox`, `manual`), URL, and status.
  - "Sync Now" button providing real-time ingestion telemetry (new notices, duplicates bypassed, errors).

### 3.4 Continuous Monitoring View
- **Purpose**: Monitor active tender pursuits for specification changes.
- **Features**:
  - Active watch cards showing tender title, polling frequency, and last checked timestamp.
  - Snapshot version timeline with cryptographic SHA-256 badge inspection.

### 3.5 Corrigenda & Amendments View
- **Purpose**: Triage published corrigenda and review downstream impact.
- **Features**:
  - Materiality badge (`Minor`, `Material`, `Critical`).
  - Affected requirements list and clause diff overview.
  - Alert banner indicating if executive approvals were invalidated.
  - "Acknowledge Amendment" modal with mandatory human sign-off notes.

### 3.6 Market Analytics View
- **Purpose**: Macro-level procurement trends and public spend analytics.
- **Features**:
  - Total award volume metric cards.
  - Average discount below budget ceiling widget.
  - Top issuing authorities ranked by contract expenditure.

### 3.7 Competitor Benchmarks View
- **Purpose**: Inspect competitor profiles derived from public award gazettes.
- **Features**:
  - Empirical win rates and observed discount percentages.
  - Known technical strengths, delivery gaps, and common aliases.

### 3.8 Closed-Loop Bid Learning View
- **Purpose**: Post-tender intelligence and win/loss feedback analysis.
- **Features**:
  - 14-stage bid lifecycle pipeline funnel.
  - Root-cause loss reason distribution chart ($N \ge 5$ threshold indicator).
  - Reusable Knowledge Asset library with one-click narrative injection into proposals.
