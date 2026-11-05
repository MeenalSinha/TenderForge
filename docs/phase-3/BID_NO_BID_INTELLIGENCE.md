# TenderForge Bid/No-Bid Decision Intelligence Architecture

## 1. Executive Summary

In government and enterprise procurement, submitting a proposal requires substantial financial, engineering, and managerial resources. Pursuing an unviable tender diverts critical talent and risks disqualification or liquidated damages. Conversely, rejecting an eligible high-margin tender sacrifices strategic revenue.

The **TenderForge Bid/No-Bid Decision Intelligence Engine** solves this dilemma by performing rigorous, multi-dimensional feasibility evaluations governed by strict, non-compensable eligibility gates.

```
+-----------------------------------------------------------------------------------+
|                        TenderForge Bid Intelligence Engine                        |
+-----------------------------------------------------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                                                   |
        v                                                                   v
+-----------------------+                                         +-------------------+
| Non-Compensable Gates |                                         | Weighted Scoring  |
| - Statutory Inc.      |                                         | - Technical Fit   |
| - Minimum Turnover    |                                         | - Past Perf.      |
| - Mandatory Certs     |                                         | - Financials      |
| - Security Clearance  |                                         | - Staffing        |
+-----------------------+                                         | - Timelines       |
        |                                                         +-------------------+
        | If ANY gate fails:                                                |
        +---------------------> [ NO-BID RECOMMENDED ] <--------------------+
                                (Cannot be compensated)
                                          |
                                          | If all gates pass:
                                          v
                              [ BID / BID WITH CONDITIONS ]
                                          |
                                          v
                             [ Human Executive Authority ]
```

---

## 2. Evaluation Dimensions & Configurable Weights

Evaluation criteria are completely decoupled from code and defined declaratively in `config/bid_evaluation.yaml`:

| Dimension | Baseline Weight | Minimum Pass Score | Type | Description |
|---|---|---|---|---|
| **Mandatory Eligibility** | `0.25` | `100.0` (Pass/Fail) | **Hard Gate** | Legal entity standing, incorporation, tax registration, non-blacklisting. |
| **Technical Capability** | `0.20` | `70.0` | Compensable | Fit between scope of work and technical core capabilities. |
| **Past Performance** | `0.15` | `65.0` | Compensable | Verified delivery track record in similar scale and complexity. |
| **Financial Capacity** | `0.15` | `70.0` | Compensable | Turnover hurdles, liquidity, bank guarantee limits, and working capital. |
| **Resource Availability** | `0.10` | `60.0` | Compensable | Availability of certified key personnel and engineering talent. |
| **Timeline Feasibility** | `0.10` | `60.0` | Compensable | Pacing between submission date, award, and milestone delivery dates. |
| **Strategic Alignment** | `0.05` | `50.0` | Compensable | Margin potential, account entry, and repeatable IP acquisition. |

---

## 3. Non-Compensable Hard Eligibility Gates

A fundamental architectural principle of TenderForge is that **mandatory eligibility criteria are non-compensable**:

> [!CRITICAL]
> Even if an organization achieves a perfect `100.0/100` score across Technical Capability, Past Performance, Staffing, and Margins, failure on any single mandatory statutory or legal gate (e.g., missing ISO 27001, lack of security clearance, or turnover below the required threshold) **strictly overrides the recommendation to `NO-BID RECOMMENDED` or `BID WITH CONDITIONS`**. High technical scores can never compensate for statutory disqualification.

### Gate Evaluation Algorithm
```python
def evaluate_gates(compliance_items, org_profile, mandatory_gates):
    failed_gates = []
    for item in compliance_items:
        if item.status == "Non-Compliant" and item.is_mandatory:
            failed_gates.append(item.description)
    
    if not org_profile.registration_number or not org_profile.tax_id:
        failed_gates.append("Statutory corporate identity records missing.")
        
    return failed_gates, len(failed_gates) == 0
```

---

## 4. Advisory Recommendations & Thresholds

The engine outputs one of three explicit advisory statuses:

1. **`BID`**:
   - All mandatory eligibility gates passed (`100%`).
   - Overall weighted viability score $\ge 75.0$.
   - No individual dimension score below its minimum threshold.
2. **`BID WITH CONDITIONS`**:
   - All mandatory gates passed, but overall score is between `60.0` and `74.9`, OR
   - One or more individual dimensions fall below threshold (e.g., timeline is tight, requiring additional staffing commitments).
   - Generates actionable condition items required prior to formal release.
3. **`NO-BID RECOMMENDED`**:
   - Any mandatory eligibility gate failed, OR
   - Overall weighted viability score falls below `60.0`.

---

## 5. Human Executive Authority & Override Tracking

The system adheres strictly to the rule of **Human Executive Authority**:
- The AI engine's recommendations are strictly **advisory**.
- The platform tracks human executive decisions via `record_human_decision()`:
  - `APPROVED_BID`: Executive signs off on pursuing the opportunity.
  - `APPROVED_NO_BID`: Executive ratifies the recommendation to abandon the opportunity.
  - `OVERRIDDEN`: Executive chooses to pursue a tender despite an advisory `NO-BID` or `BID WITH CONDITIONS` (e.g., strategic account acquisition, consortium agreement).
- Every decision requires:
  - Executive User ID and Name
  - User Authority Role (must hold `Approver` or `Admin` RBAC role)
  - Substantive rationale (minimum 10 characters)
  - Timezone-aware UTC timestamp.
