# TenderForge Phase 4: Organization & Team Governance

## 1. Multi-Tenant Enterprise Model

TenderForge provides strict multi-tenant data isolation and team governance. Every tender opportunity, ingested document, proposal draft, and financial BOQ belongs to an **Organization** or a specific **Workspace** within that organization.

```
+-------------------------------------------------------------------------+
|                              ORGANIZATION                               |
|   (ID: org-acme-corp, Name: "Acme Global Solutions", Tier: Enterprise)  |
+-------------------------------------------------------------------------+
       |                                                    |
       v                                                    v
+-------------------------------+            +-------------------------------+
|     ORGANIZATION MEMBERS      |            |      TENDER WORKSPACES        |
|  - Jane Doe (Role: admin)     |            |  - Smart City Transport RFP   |
|  - Bob Smith (Role: bid_mgr)  |            |  - Defence IT Infrastructure  |
|  - Alice Wang (Role: writer)  |            |  - Health Cloud Migration     |
+-------------------------------+            +-------------------------------+
```

---

## 2. 5-Tier Role-Based Access Control (RBAC) Matrix

TenderForge enforces a comprehensive 5-tier role hierarchy governed by `config/application.yaml`.

| Role | Description | Ingestion & Analysis | Proposal Writing | Financial BOQ | Risk Assessment | Executive Approval | User Administration |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`admin`** | Full organizational authority | Yes | Yes | Yes | Yes | Yes | Yes |
| **`bid_manager`** | Manages bid lifecycle & deadlines | Yes | Yes | Yes | Yes | Yes | Members Only |
| **`proposal_writer`** | Authors response sections & matches evidence | Yes | Yes | View Only | View Only | No | No |
| **`reviewer`** | Reviews compliance & flags contradictions | View Only | View / Comment | View Only | View / Assess | No | No |
| **`viewer`** | Read-only executive stakeholder | View Only | View Only | View Only | View Only | No | No |

---

## 3. Database Schema: `organization_members`

```sql
CREATE TABLE organization_members (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    invited_by_id VARCHAR(36) REFERENCES users(id),
    joined_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT uq_org_user UNIQUE (organization_id, user_id)
);
CREATE INDEX ix_org_members_user ON organization_members(user_id);
CREATE INDEX ix_org_members_org ON organization_members(organization_id);
```

---

## 4. Organization Management REST APIs

| Method | Endpoint | Description | Permitted Roles |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/organizations` | List all organizations user belongs to | Any Authenticated |
| `POST` | `/api/v1/organizations` | Create a new organization entity | Any Authenticated |
| `GET` | `/api/v1/organizations/{id}` | Retrieve organization details and stats | Member |
| `PUT` | `/api/v1/organizations/{id}` | Update organization metadata | `admin` |
| `GET` | `/api/v1/organizations/{id}/members` | List active team members and roles | Member |
| `POST` | `/api/v1/organizations/{id}/members` | Invite new member with designated role | `admin`, `bid_manager` |
| `PUT` | `/api/v1/organizations/{id}/members/{user_id}` | Modify member role | `admin` |
| `DELETE`| `/api/v1/organizations/{id}/members/{user_id}` | Remove member from organization | `admin` |

---

## 5. Security & Isolation Guarantees
1. **Tenant Segregation**: Database queries filtering tenders and evidence enforce `WHERE organization_id = :org_id`.
2. **Preventing Self-Orphaning**: The last remaining `admin` of an organization cannot be deleted or downgraded.
3. **Audit Logging**: Every invitation, role change, and member revocation is written to the immutable audit log with actor ID, timestamp, and client IP.
