# TenderForge Phase 4: Enterprise Frontend Guide

## 1. Overview & Architecture

The TenderForge Enterprise Single Page Application (SPA) provides a modern, reactive, desktop-class user experience designed for procurement teams, bid managers, financial analysts, and executive reviewers.

- **Technology Stack**: React 18, TypeScript, Tailwind CSS, Lucide React icons, and Chart.js.
- **Bundle Strategy**: Production-compiled distribution at `frontend/dist/index.html` (101 KB bundled size) utilizing ES module delivery and CDN-resilient fallbacks.
- **Zero-Config Deployment**: Served directly by FastAPI's static/SPA route fallback, allowing single-command execution via `python -m uvicorn backend.app.main:app --port 8000` without requiring external node servers.

---

## 2. The 15 Operational War Room Views

The application provides 15 dedicated operational views covering the complete bid lifecycle:

```
+-----------------------------------------------------------------------------------------+
|                                     SIDEBAR NAVIGATION                                  |
+-----------------------------------------------------------------------------------------+
|  [1. Executive Dashboard]           - Overall portfolio health, win probability, alerts  |
|  [2. Pipeline Funnel]               - 6-stage Kanban board (Ingestion -> Submitted)     |
|  [3. Tender Opportunities]          - Tender catalog, metadata, budget, deadlines       |
|  [4. Ingestion & Documents]         - Multi-document upload, parsing, text chunks       |
|  [5. Requirements & ProofLink]      - Categorized clauses with ProofLink snippet modal   |
|  [6. Proposal Section Editor]       - AI drafting, ProofLink citations, markdown preview |
|  [7. Criteria Optimizer]            - Side-by-side diff viewer for evaluation rubrics    |
|  [8. Financial BOQ Workspace]       - Deterministic pricing table, margin & tax models   |
|  [9. Viability & Bid/No-Bid]        - Multi-dimensional radar chart, hard gate checks    |
|  [10. Risk Management (5x5)]        - 5x5 Heat Matrix, risk register, mitigation steps   |
|  [11. Deadlines & Milestones]       - Live countdown alarms, SLA milestones             |
|  [12. Deliverables Release Center]  - Manifest generator, DOCX/XLSX/ZIP bundle download  |
|  [13. Switch War Room (Multi-Agent)]- Live agent status cards, execution stream, chat   |
|  [14. Evidence Repository]          - Company certs, freshness indicator, contradictions|
|  [15. Team & Organization Settings] - Member directory, role modification, invitations   |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Key Interactive Capabilities

### 3.1 ProofLink Interactive Inspection
- Clicking any ProofLink badge (`[ProofLink: REF-2024-ISO]`) opens an interactive modal revealing:
  - Source document name and cryptographic SHA-256 hash.
  - Page number and character offsets.
  - Highlighting the exact verbatim source text from the tender document or company evidence vault.
  - Verification timestamp and confidence score.

### 3.2 Criteria Alignment Side-by-Side Diff Viewer
- Red-green split diff viewer highlighting adjustments made by the `proposal_writer` agent to align technical claims with specific buyer scoring rubrics.

### 3.3 Financial BOQ Dynamic Modeler
- Interactive financial table allowing line-item additions, quantity/unit-rate modifications, overhead rate toggles (5-25%), contingency allowances (3-15%), and tax rate presets (GST 18%, VAT 20%).
- All calculations synchronize deterministically using fixed-point arithmetic (`Decimal`).

### 3.4 5x5 Risk Heat Matrix
- Interactive grid categorizing identified risks across 5 Likelihood and 5 Impact levels:
  - Critical (Red): Requires executive sign-off before bid release.
  - High (Orange): Requires specific mitigation owner and prooflink evidence.
  - Moderate / Low (Yellow/Green): Tracked on project execution register.

---

## 4. UI Style Guide & Accessibility
- **Color Palette**: Slate and zinc backgrounds (`bg-slate-900`, `bg-slate-800`), indigo brand accents (`indigo-600`), emerald success badges (`emerald-400`), amber warning indicators (`amber-400`), and rose critical flags (`rose-400`).
- **Typography**: Inter / system font stack with strict typographic hierarchy.
- **Responsiveness**: Fluid layout with responsive sidebar toggling, horizontal table scrolling, and accessible modal backdrops.
