# Tender Portfolio Management & Multi-Workspace Lifecycle

## 1. Overview & Objectives

Enterprises manage dozens of bids concurrently across diverse procurement sectors. The **Tender Portfolio Management Service** provides an executive command center to track pipeline stages, active pipeline value, win rates, and stage distribution across workspaces.

---

## 2. Standardized Pipeline Stages

Every tender transitions through a 10-stage lifecycle:

```
  [Opportunity] -> [Qualified] -> [Bid Decision] -> [Preparation] -> [Review]
                                                                        |
                                                                        v
  [Won] <---------- [Submitted] <--------------------------------- [Approved]
    |
  [Lost]
    |
  [Abandoned]
```

1. **Opportunity**: Initial discovery and document ingestion.
2. **Qualified**: Requirements extracted and preliminary capability verified.
3. **Bid Decision**: Bid Intelligence Engine advisory recommendation and executive sign-off.
4. **Preparation**: Proposal drafting, ProofLink mapping, and BOQ pricing.
5. **Review**: Compliance evaluation, independent bid audit, and quality check.
6. **Approved**: Final human executive signature hash generated.
7. **Submitted**: Formal tender package submitted to issuing authority.
8. **Won**: Tender awarded to the organization.
9. **Lost**: Tender awarded to a competitor.
10. **Abandoned**: Bid withdrawn due to risk, feasibility, or client cancellation.

---

## 3. Aggregate Portfolio Metrics

The portfolio engine calculates:
- **Active Pipeline Value**: Sum of estimated values across non-terminal tenders (`Opportunity` through `Submitted`).
- **Win Rate Percentage**:
  $$\text{Win Rate} = \frac{\text{Won}}{\text{Won} + \text{Lost}} \times 100$$
- **Stage Distribution**: Count of tenders active in each lifecycle stage.
- **Urgency Distribution**: Tenders sorted by submission deadline countdown.

---

## 4. Multi-Tenant Workspace Isolation

Tenders, documents, and evidence repository assets are strictly partitioned by `workspace_id` and `organization_id`. Database queries strictly filter by foreign keys to prevent cross-organization data leakage.
