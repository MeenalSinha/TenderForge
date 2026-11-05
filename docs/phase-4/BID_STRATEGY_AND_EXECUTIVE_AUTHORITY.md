# TenderForge Phase 4: Bid Strategy & Executive Authority

## 1. Overview & Decision Framework

The Bid/No-Bid decision is the most critical commercial milestone in tender preparation. Bidding on unwinnable, non-compliant, or margin-negative tenders wastes organizational resources. TenderForge provides an evidence-based **Bid Strategy Engine** that calculates multi-dimensional viability while enforcing strict non-compensable hard gates and executive sign-off authority.

---

## 2. Multi-Dimensional Viability Model

The Bid Strategy Engine computes scores across 5 distinct strategic dimensions:

```
                      1. Technical Fit (25%)
                                ^
                                |
        5. Resource Fit (15%)  / \  2. Commercial Margin (20%)
                             \     /
                              \   /
                               \ /
      4. Risk & Compliance (20%) v 3. Past Experience (20%)
```

### Dimension Definitions & Evaluation Logic
1. **Technical Fit (25% Weight)**: Alignment between technical specifications, scope of work, and organizational core capabilities.
2. **Commercial Margin (20% Weight)**: Projected gross margin relative to organizational hurdle rates defined in `config/financial_policies.yaml`.
3. **Past Experience (20% Weight)**: Availability of verified past performance records and client completion certificates meeting tender scale criteria.
4. **Risk & Compliance (20% Weight)**: Regulatory liability exposure, penalty clauses, and compliance fulfillment ratio.
5. **Resource Fit (15% Weight)**: Availability of qualified personnel and specialized tooling during the delivery window.

---

## 3. Non-Compensable Hard Gates

A fundamental innovation of TenderForge is that **a high aggregate viability score can never mask a fatal eligibility failure**.

The following non-compensable gates trigger an automatic `NO-BID RECOMMENDED` or require formal executive override:
1. **Financial Solvency Gate**: Tender requires annual turnover exceeding organizational certified turnover.
2. **Mandatory Certification Gate**: Mandatory regulatory certification (e.g., ISO 27001, CMMI Level 5, Secret Clearance) is missing or expired.
3. **Blacklisting / Debarment Gate**: Debarment or exclusion from specific procurement portals.
4. **Unacceptable Liability Gate**: Unlimited liquidated damages or uncapped indemnification clauses.

---

## 4. Recommendation Classifications

| Recommendation | Conditions | Permitted Next Actions |
| :--- | :--- | :--- |
| **`BID`** | Aggregate Score $\ge 75\%$, All Hard Gates Passed, Margin $\ge$ Policy Target | Full team mobilization, proposal drafting |
| **`BID WITH CONDITIONS`** | Aggregate Score $60-74\%$, Hard Gates Passed with mitigations | Requires mitigation plan sign-off by Bid Manager |
| **`NO-BID RECOMMENDED`** | Aggregate Score $< 60\%$ OR Any Hard Gate Failed | Automatic recommendation to decline tender |

---

## 5. Executive Authority & Override Protocol
- AI recommendations are strictly advisory. The platform **never** makes autonomous go/no-go commitments.
- An authorized executive possessing the `admin` or `bid_manager` role can execute an **Executive Override**:
  - Requires entering a mandatory justification narrative (minimum 25 characters).
  - Must specify compensating factors (e.g., "Subcontracting specialist partner to satisfy ISO 27001 requirement").
  - The override event, user identity, timestamp, and justification are permanently sealed in the immutable audit log.
