# Phase 5: Complete REST API Reference

## 1. Overview

Phase 5 registers 6 new production API routers mounted under `/api/v1`, expanding the total endpoint surface to 87 OpenAPI endpoints.

---

## 2. Procurement Sources API (`/api/v1/procurement/sources`)

### `GET /api/v1/procurement/sources/registered-connectors`
- **Description**: Lists all available connector types in the system registry.
- **Roles**: All authenticated users.
- **Response**: `[{"connector_type": "manual", ...}, {"connector_type": "open_tender", ...}, {"connector_type": "mock_sandbox", ...}]`

### `GET /api/v1/procurement/sources`
- **Description**: Lists configured procurement sources for the organization.
- **Roles**: All authenticated users.

### `POST /api/v1/procurement/sources`
- **Description**: Registers a new procurement data source.
- **Roles**: `Admin`, `BidManager`.
- **Payload**: `{"name": "Gov Tender Portal", "connector_type": "open_tender", "configuration": {...}}`

### `POST /api/v1/procurement/sources/{source_id}/sync`
- **Description**: Triggers an immediate ingestion run from the specified source.
- **Roles**: `Admin`, `BidManager`.
- **Query Params**: `limit: int = 50`

---

## 3. Opportunities API (`/api/v1/opportunities`)

### `GET /api/v1/opportunities`
- **Description**: Lists discovered procurement notices with filtering on category, buyer, status, and budget.
- **Query Params**: `category`, `buyer`, `status`, `min_budget`, `max_budget`, `page`, `page_size`.

### `GET /api/v1/opportunities/{opportunity_id}`
- **Description**: Retrieves full details and raw portal payload for an opportunity.

### `POST /api/v1/opportunities/{opportunity_id}/evaluate-match`
- **Description**: Computes 9-dimension match scores and explainability against organization profile.
- **Roles**: `Admin`, `BidManager`, `Author`.

### `POST /api/v1/opportunities/{opportunity_id}/promote-to-tender`
- **Description**: Promotes an opportunity into an active Tender Workspace for proposal response.
- **Roles**: `Admin`, `BidManager`.

---

## 4. Monitoring & Amendments API (`/api/v1/monitoring`)

### `GET /api/v1/monitoring/subscriptions`
- **Description**: Lists active tender monitoring subscriptions.

### `POST /api/v1/monitoring/subscriptions`
- **Description**: Creates a continuous monitoring watch on a tender workspace.
- **Roles**: `Admin`, `BidManager`.

### `GET /api/v1/monitoring/tenders/{tender_id}/snapshots`
- **Description**: Returns chronological SHA-256 snapshots for a tender.

### `GET /api/v1/monitoring/tenders/{tender_id}/amendments`
- **Description**: Lists all recorded corrigenda and addenda with materiality tiers.

### `POST /api/v1/monitoring/amendments/{amendment_id}/acknowledge`
- **Description**: Records human certification and review notes for an amendment.
- **Roles**: `Admin`, `BidManager`, `Author`.

---

## 5. Market & Competitor Intelligence API (`/api/v1/market`)

### `GET /api/v1/market/awards`
- **Description**: Queries verified public contract awards with filters.

### `GET /api/v1/market/analytics`
- **Description**: Computes market aggregate benchmarks, average discount rates, and top buyers.

### `GET /api/v1/market/competitors`
- **Description**: Lists competitor intelligence profiles with empirical win rates and typical discounts.

### `GET /api/v1/market/competitors/{competitor_id}`
- **Description**: Returns detailed competitor profile and observed historical public awards.

---

## 6. Bid Lifecycle & Outcomes API (`/api/v1/bid-outcomes`)

### `POST /api/v1/bid-outcomes/submissions`
- **Description**: Records formal proposal submission and generates cryptographic SHA-256 receipt.
- **Roles**: `Admin`, `BidManager`, `Approver`.

### `GET /api/v1/bid-outcomes/submissions`
- **Description**: Lists submitted bids for the organization.

### `POST /api/v1/bid-outcomes/outcomes`
- **Description**: Records final tender outcome (`won`, `lost`, `withdrawn`), debrief notes, and win/loss factors.
- **Roles**: `Admin`, `BidManager`.

### `GET /api/v1/bid-outcomes/learning-analytics`
- **Description**: Computes statistical win rates, loss reason distributions, and closed-loop recommendations ($N \ge 5$ threshold).

---

## 7. Knowledge Library API (`/api/v1/knowledge`)

### `GET /api/v1/knowledge/assets`
- **Description**: Searches reusable narrative assets by keyword, category, and lifecycle status.

### `POST /api/v1/knowledge/assets`
- **Description**: Creates a new reusable knowledge narrative.
- **Roles**: `Admin`, `BidManager`, `Author`.

### `POST /api/v1/knowledge/assets/{asset_id}/versions`
- **Description**: Submits an updated version of a knowledge narrative.

### `POST /api/v1/knowledge/assets/{asset_id}/approve`
- **Description**: Formally approves an asset version for live proposal reuse.
- **Roles**: `Admin`, `Reviewer`, `Approver`.

### `POST /api/v1/knowledge/assets/{asset_id}/use`
- **Description**: Injects an approved narrative into an active proposal section and tracks reuse count.
- **Roles**: `Admin`, `BidManager`, `Author`.

