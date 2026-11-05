# TenderForge Phase 4: Financial Workspace & BOQ Engine

## 1. Overview & High-Precision Financial Policies

In government and enterprise tenders, commercial disqualification frequently results from arithmetic inconsistencies, rounding discrepancies, or improper tax calculations. The TenderForge Financial Workspace and Bill of Quantities (BOQ) Engine guarantees deterministic, auditable commercial proposals.

---

## 2. Deterministic Arithmetic & Precision Guarantee

### 2.1 Fixed-Point Decimal Math
- Floating-point arithmetic (`float` / IEEE 754) is strictly prohibited across all financial services.
- All pricing, unit rates, sub-totals, overheads, margins, and taxes are calculated using Python's `decimal.Decimal` with fixed-precision rounding (`ROUND_HALF_UP`).
- Database columns store financial figures as `NUMERIC(15, 2)` or `NUMERIC(15, 4)` to eliminate floating-point drift.

### 2.2 Mathematical Formulae
For each line item $i$:
$$\text{Line Total}_i = \text{ROUND}(\text{Quantity}_i \times \text{Unit Rate}_i, 2)$$

For the overall BOQ:
$$\text{Base Direct Cost} = \sum_{i=1}^{n} \text{Line Total}_i$$
$$\text{Overhead Amount} = \text{ROUND}(\text{Base Direct Cost} \times \text{Overhead Rate}, 2)$$
$$\text{Contingency Amount} = \text{ROUND}(\text{Base Direct Cost} \times \text{Contingency Rate}, 2)$$
$$\text{Subtotal before Margin} = \text{Base Direct Cost} + \text{Overhead Amount} + \text{Contingency Amount}$$
$$\text{Profit Margin Amount} = \text{ROUND}(\text{Subtotal before Margin} \times \text{Profit Margin Rate}, 2)$$
$$\text{Net Price (Pre-Tax)} = \text{Subtotal before Margin} + \text{Profit Margin Amount}$$
$$\text{Tax Amount} = \text{ROUND}(\text{Net Price} \times \text{Tax Rate}, 2)$$
$$\text{Gross Total Proposal Price} = \text{Net Price} + \text{Tax Amount}$$

---

## 3. Financial Workspace UI & Scenario Modeling

```
+-----------------------------------------------------------------------------------------+
|                               FINANCIAL BOQ WORKSPACE                                   |
+-----------------------------------------------------------------------------------------+
| Line Item Description        | Qty  | Unit | Rate ($)    | Total ($)     | Action       |
+------------------------------+------+------+-------------+---------------+--------------+
| Cloud Architect (Lead)       | 160  | Hrs  | 175.00      | 28,000.00     | [Edit] [Del] |
| DevOps / SRE Engineer        | 320  | Hrs  | 135.00      | 43,200.00     | [Edit] [Del] |
| Security & Compliance Audit  | 1    | Lot  | 15,000.00   | 15,000.00     | [Edit] [Del] |
| High-Availability DB Cluster | 12   | Mos  | 1,200.00    | 14,400.00     | [Edit] [Del] |
+------------------------------+------+------+-------------+---------------+--------------+
| Base Direct Cost:                                        | $100,600.00                  |
| Overhead Rate (10.0%):                                   | $10,060.00                   |
| Contingency Buffer (5.0%):                               | $5,030.00                    |
| Target Margin (15.0%):                                   | $17,353.50                   |
| Subtotal (Pre-Tax):                                      | $133,043.50                  |
| Applicable Tax / GST (18.0%):                            | $23,947.83                   |
| TOTAL COMMERCIAL BID:                                    | $156,991.33                  |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Multi-Scenario Modeling & Competitiveness Sensitivity
The workspace enables bid managers to evaluate 3 real-time commercial scenarios:
1. **Aggressive Price-to-Win**: Minimum sustainable margin (e.g., 8%) with reduced overhead allocation.
2. **Standard Benchmark**: Balanced target margin (e.g., 15%) conforming to organizational financial policies.
3. **High-Risk Premium**: Elevated margin (e.g., 22%) and contingency buffer (10%) for complex regulatory or penalty-prone tenders.

---

## 5. Export Formats
- Structured financial tables export directly to standard Microsoft Excel (`.xlsx`) workbooks featuring live formulas (`=SUM()`, `=PRODUCT()`) rather than static pasted strings.
- Complete snapshot exported to the tender deliverables release archive.
