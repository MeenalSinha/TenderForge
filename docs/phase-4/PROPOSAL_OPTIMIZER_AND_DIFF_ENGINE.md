# TenderForge Phase 4: Proposal Optimizer & Diff Engine

## 1. Overview & Purpose

In competitive tender procurement, winning bids are evaluated against explicit, weighted scoring criteria published in the Request for Proposal (RFP). The **Proposal Optimizer and Diff Engine** automates the alignment of proposal drafts with these criteria while providing complete visibility and control to human bid authors through a side-by-side visual diff viewer.

---

## 2. Optimization Mechanism

### 2.1 Criteria Alignment Pipeline
1. **Clause Extraction**: The engine extracts published scoring rubrics (e.g., "Technical Merit: 40 points, Cloud Security: 25 points, SLA Responsiveness: 15 points").
2. **Gap Analysis**: The existing proposal section draft is compared against rubric keywords, required certifications, and compliance benchmarks.
3. **Structured Optimization**: The optimizer suggests targeted adjustments to emphasize required qualifications, insert relevant ProofLinks, and remove ambiguous filler language.
4. **Zero Fabrication Enforcement**: The optimizer is strictly prohibited from inventing new metrics or claims; any suggested enhancement must cite an existing document in the corporate evidence vault.

---

## 3. Side-by-Side Visual Diff Viewer

The enterprise frontend incorporates an inline diff engine comparing:
- **Baseline Draft (Left Column)**: The original author narrative with highlighted omissions and weak phrasing.
- **Optimized Proposal (Right Column)**: The enhanced, criteria-aligned text with additions, ProofLink anchors, and improved structural clarity.

```
+-----------------------------------------------------------------------------------------+
|                               PROPOSAL CRITERIA OPTIMIZER                               |
+-----------------------------------------------------------------------------------------+
| Section 3.2: Cloud Infrastructure & Resilience                                          |
| Target Criterion: "Technical Resilience & SLA (Weight: 25%)"                             |
+-----------------------------------------------------------------------------------------+
| ORIGINAL BASELINE DRAFT                       | OPTIMIZED ALIGNED PROPOSAL              |
+-----------------------------------------------+-----------------------------------------+
| Our team provides very fast cloud backup and  | We provide automated multi-region backup|
| reliable disaster recovery. We have completed | with RPO < 15 min and RTO < 1 hr        |
| multiple cloud projects for clients.          | [ProofLink: CASE-STUDY-CLOUD-2025].     |
|                                               | All infrastructure complies with        |
|                                               | ISO 27001 [ProofLink: CERT-ISO-27001].  |
+-----------------------------------------------+-----------------------------------------+
| [- Dismiss Changes]                                             [+ Accept Optimization] |
+-----------------------------------------------------------------------------------------+
```

---

## 4. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/optimizations/analyze` | Evaluate section draft against target scoring rubric |
| `POST` | `/api/v1/optimizations/apply` | Generate optimized text with inline ProofLink citations |
| `GET` | `/api/v1/optimizations/history/{section_id}` | Retrieve audit trail of prior revisions and diffs |

---

## 5. Governance & Human Approval
- Revisions are never committed automatically to the final proposal bundle.
- Acceptance requires explicit human review and click-through approval from a user possessing the `proposal_writer`, `bid_manager`, or `admin` role.
- All diffs and acceptance decisions are permanently recorded in the immutable audit log.

