# TenderForge Phase 4: Risk Management & 5x5 Matrix

## 1. Overview & Risk Policy

Tender responses entail legal, commercial, operational, and delivery liabilities. Uncapped indemnities, stringent service level agreements (SLAs), or unrealistic implementation schedules can cause massive financial losses post-award. The TenderForge Risk Management Engine provides continuous, automated risk identification, 5x5 heat matrix scoring, and structured mitigation workflows.

---

## 2. 5x5 Risk Heat Matrix

Risks are quantified along two axes: **Likelihood (1 to 5)** and **Impact (1 to 5)**, governed by rules in `config/risk_matrix.yaml`.

$$\text{Risk Score} = \text{Likelihood} \times \text{Impact} \quad (1 \le \text{Score} \le 25)$$

```
 IMPACT ->     1: Negligible   2: Minor     3: Moderate   4: Major     5: Critical
LIKELIHOOD v
5: Almost Certain   [5 - Med]   [10 - High]  [15 - High]   [20 - Crit]  [25 - Crit]
4: Likely           [4 - Low]   [8 - Med]    [12 - High]   [16 - Crit]  [20 - Crit]
3: Possible         [3 - Low]   [6 - Med]    [9 - Med]     [12 - High]  [15 - High]
2: Unlikely         [2 - Low]   [4 - Low]    [6 - Med]     [8 - Med]    [10 - High]
1: Rare             [1 - Low]   [2 - Low]    [3 - Low]     [4 - Low]    [5 - Med]
```

### Risk Severity Tiers & Governance Rules
- **Critical (Score 16 - 25, Red)**: Blocks proposal release bundle until formal mitigation plan is approved by an `admin` or `bid_manager`.
- **High (Score 10 - 15, Orange)**: Requires documented mitigation strategy, designated risk owner, and contingency budget allocation.
- **Moderate (Score 5 - 9, Yellow)**: Included in the tender operational risk register for project handover.
- **Low (Score 1 - 4, Green)**: Standard operational tracking.

---

## 3. Automated Risk Detection Categories

The Risk Engine scans ingested tender specifications across 5 operational domains:
1. **Commercial & Financial**: Liquidated damages exceeding 10% of contract value, uncapped liability, performance bank guarantee requirements.
2. **Legal & Contractual**: Ambiguous IP ownership clauses, one-sided termination for convenience, foreign governing law jurisdictions.
3. **Technical & Delivery**: Complex multi-vendor integration dependencies, proprietary legacy hardware requirements, severe uptime penalties (> 99.99%).
4. **Staffing & Resources**: Highly specialized key personnel certifications, short deployment lead times (< 14 calendar days).
5. **Regulatory & Compliance**: Stringent data sovereignty mandates, specialized national security clearances.

---

## 4. Risk Mitigation Workflow & UI Register

```
+-----------------------------------------------------------------------------------------+
|                                    RISK REGISTER                                        |
+-----------------------------------------------------------------------------------------+
| ID      | Category    | Risk Description             | L x I = Score | Status | Owner   |
+---------+-------------+------------------------------+---------------+--------+---------+
| RSK-001 | Legal       | Uncapped indemnification     | 4 x 5 = 20    | ACTIVE | J. Doe  |
| RSK-002 | Financial   | Liquidated damages: 1%/day   | 3 x 4 = 12    | MITIG  | B. Smith|
| RSK-003 | Delivery    | Go-live required in 30 days  | 4 x 3 = 12    | MITIG  | A. Wang |
| RSK-004 | Compliance  | Data residency within EU     | 2 x 4 = 8     | CLOSED | J. Doe  |
+-----------------------------------------------------------------------------------------+
```

### Mitigation Actions
- **Accept**: Accept risk with justification and insurance coverage.
- **Mitigate**: Implement specific technical or contractual safeguards (e.g., submit formal tender query/clarification).
- **Transfer**: Subcontract high-risk scope or secure third-party performance underwriting.
- **Avoid**: Propose alternative compliance deviation or decline tender submission.

