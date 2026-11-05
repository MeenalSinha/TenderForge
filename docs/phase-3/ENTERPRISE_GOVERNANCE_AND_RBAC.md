# Enterprise Governance & Server-Side Role-Based Access Control (RBAC)

## 1. Overview & Principle of Human Authority

TenderForge enforces strict governance boundaries:
- AI agents are specialized assistants that extract intelligence, audit compliance, draft proposals, and recommend decisions.
- **AI agents can never approve bids, sign off on submissions, or commit corporate pricing**.
- Human executive sign-off is mandatory and cryptographically logged.

---

## 2. Role Hierarchy & Permissions

Permissions are enforced server-side via `backend/app/core/rbac.py` on all API routes:

```
  Viewer (1) < Author (2) < Reviewer (3) < Approver (4) < Admin (5)
```

| Role | Hierarchy Level | Key Permissions | Allowed Operations |
|---|---|---|---|
| **Viewer** | 1 | Read-only | View tenders, proposals, audits, financial models, analytics. |
| **Author** | 2 | Draft / Edit | Ingest documents, add line items, draft proposal sections, create risks. |
| **Reviewer** | 3 | Audit / Validate | Run compliance audits, trigger proposal optimizations, harvest risks, diff versions. |
| **Approver** | 4 | Executive Authority | Authorize Bid/No-Bid decisions, sign human approval certificates, lock pricing. |
| **Admin** | 5 | Enterprise Admin | Workspace configuration, role assignments, system-wide overrides. |

---

## 3. Enforcement in FastAPI Endpoints

```python
from backend.app.core.rbac import Role, require_role

@router.post("/bid-evaluations/{evaluation_id}/decision")
def record_human_bid_decision(
    evaluation_id: str,
    payload: HumanDecisionRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.APPROVER)),  # Requires Approver or Admin
):
    ...
```

If an unauthorized user attempts an operation, the engine immediately responds with `403 Forbidden` and records an audit log.
