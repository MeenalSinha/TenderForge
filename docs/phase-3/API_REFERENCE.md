# TenderForge REST API Reference

All API routes are mounted under `/api/v1/` and protected by server-side RBAC dependencies (`require_role`).

## 1. Bid Intelligence Endpoints

### `POST /api/v1/tenders/{tender_id}/bid-evaluation`
Execute multi-dimensional evaluation and generate advisory recommendation.
- **Required Role**: `Reviewer`
- **Request**:
  ```json
  {
    "evaluator_type": "agent",
    "evaluator_id": "BidIntelligenceEngine",
    "dimension_overrides": null
  }
  ```
- **Response**: `201 Created` with full evaluation, failed gates, dimensions, and recommendation.

### `GET /api/v1/tenders/{tender_id}/bid-evaluation`
Retrieve the latest bid evaluation record for a tender.
- **Required Role**: `Viewer`

### `POST /api/v1/bid-evaluations/{evaluation_id}/decision`
Record human executive decision or override.
- **Required Role**: `Approver`
- **Request**:
  ```json
  {
    "decision": "APPROVED_BID",
    "user_id": "usr-01",
    "user_name": "Marcus Vance",
    "rationale": "Strategic pursuit approved by executive board."
  }
  ```

---

## 2. Financial Proposal Endpoints

### `POST /api/v1/tenders/{tender_id}/financial-proposal`
Create a financial proposal with baseline rates and optional initial items.
- **Required Role**: `Author`

### `GET /api/v1/tenders/{tender_id}/financial-proposal`
Retrieve the commercial proposal, itemized BOQ, and scenarios.
- **Required Role**: `Viewer`

### `POST /api/v1/financial-proposals/{id}/line-items`
Add an itemized BOQ line item and trigger deterministic recalculation.
- **Required Role**: `Author`

### `POST /api/v1/financial-proposals/{id}/scenarios`
Generate Base Case, Conservative, and Aggressive scenario comparisons.
- **Required Role**: `Reviewer`

### `GET /api/v1/financial-proposals/{id}/export-excel`
Download a formatted Excel spreadsheet (`.xlsx`).
- **Required Role**: `Viewer`

---

## 3. Proposal Optimization & Quality Endpoints

### `POST /api/v1/proposals/{id}/optimize`
Audit coverage against criteria and generate Before/After recommendations.
- **Required Role**: `Reviewer`

### `POST /api/v1/optimizations/{id}/apply`
Apply accepted optimization directly to proposal section.
- **Required Role**: `Author`

### `POST /api/v1/proposals/{id}/quality-check`
Audit document for placeholders (`TODO`), formatting score, and citations.
- **Required Role**: `Reviewer`

### `GET /api/v1/proposals/{id}/diff`
Generate line-by-line unified diff between version snapshots.
- **Required Role**: `Viewer`

---

## 4. Risk & Deadline Endpoints

### `GET /api/v1/tenders/{tender_id}/risks`
List scored risks sorted by severity.
- **Required Role**: `Viewer`

### `POST /api/v1/tenders/{tender_id}/risks/harvest`
Auto-harvest risks from compliance, financials, and approaching deadlines.
- **Required Role**: `Reviewer`

### `POST /api/v1/tenders/{tender_id}/deadlines`
Register milestone date with reminder lead intervals.
- **Required Role**: `Author`

---

## 5. Portfolio & Analytics Endpoints

### `GET /api/v1/workspaces/{id}/portfolio`
Retrieve active pipeline value, win rate, and stage breakdown.
- **Required Role**: `Viewer`

### `GET /api/v1/workspaces/{id}/analytics`
Retrieve measured operational, compliance, and multi-agent metrics.
- **Required Role**: `Viewer`
