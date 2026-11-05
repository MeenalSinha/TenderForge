# TenderForge Bid Risk & Mitigation Intelligence

## 1. Executive Summary

Bidding on large public and commercial contracts exposes organizations to multidimensional risks: uncapped liquidated damages, unrealistic delivery milestones, ambiguous specifications, currency fluctuations, and subcontractor default.

The **Bid Risk Management Engine** acts as an enterprise risk register, automatically aggregating risks identified by specialized engines (Compliance, ProofLink, Financial, Deadlines) into a unified $5 \times 5$ severity matrix.

```
       IMPACT ->
   L   1:Negligible  2:Minor      3:Moderate   4:Major       5:Catastrophic
   I +-------------+------------+------------+-------------+---------------+
   K |  1 (Low)    |  2 (Low)   |  3 (Low)   |  4 (Low)    |   5 (Low)     | 1:Rare
   E |  2 (Low)    |  4 (Low)   |  6 (Low)   |  8 (Medium) |  10 (Medium)  | 2:Unlikely
   L |  3 (Low)    |  6 (Low)   |  9 (Medium)| 12 (Medium) |  15 (High)    | 3:Possible
   I |  4 (Low)    |  8 (Medium)| 12 (Medium)| 16 (High)   |  20 (High)    | 4:Likely
   H |  5 (Low)    | 10 (Medium)| 15 (High)  | 20 (High)   |  25 (High)    | 5:Almost Certain
   O +-------------+------------+------------+-------------+---------------+
```

---

## 2. Risk Scoring & Classification

- **Severity Score**: $\text{Likelihood (1–5)} \times \text{Impact (1–5)} = \text{Score (1–25)}$
- **Risk Bands**:
  - `Low (1–6)`: Managed via standard operational procedures.
  - `Medium (7–14)`: Requires assigned owner and specific mitigation plan.
  - `High (15–25)`: Executive blocker; requires explicit executive review and approved mitigation before proposal submission.

---

## 3. Automated Cross-Engine Risk Harvesting

Rather than relying purely on manual data entry, the Risk Service automatically scans and harvests risks from platform activity:

1. **Compliance Matrix**: Non-compliant mandatory criteria $\rightarrow$ Harvested as `Compliance` risks with Severity Score 20 (High).
2. **Financial BOQ**: Negative quantities or unit rates $\rightarrow$ Harvested as `Financial` risks with Severity Score 16 (High).
3. **ProofLink Freshness**: Documents expiring before submission $\rightarrow$ Harvested as `Evidence` risks.
4. **Milestone Deadlines**: Deadlines approaching in $< 48$ hours $\rightarrow$ Harvested as `Timeline` risks.

---

## 4. Mitigation Workflow & Tracking

Every risk in the register tracks:
- `owner`: Responsible team member (e.g., Compliance Officer, Financial Lead, Bid Director)
- `mitigation_strategy`: Actionable plan to reduce likelihood or impact
- `contingency_plan`: Fallback plan if risk occurs
- `status`: `Open`, `In_Progress`, `Mitigated`, `Accepted`.
