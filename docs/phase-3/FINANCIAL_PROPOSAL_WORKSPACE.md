# Financial Proposal & Commercial Workspace Architecture

## 1. Executive Summary & Design Principles

Commercial tender pricing demands mathematical determinism. Standard IEEE 754 floating-point arithmetic (used by standard Python `float` and JavaScript `Number`) introduces cumulative rounding errors (e.g., `0.1 + 0.2 = 0.30000000000000004`). In a multi-million-dollar government proposal with thousands of itemized quantities, floating-point drift can result in rejected bids due to penny discrepancies.

### Principles:
1. **Deterministic Decimal Arithmetic**: Every financial calculation strictly utilizes Python's `decimal.Decimal` with explicit `ROUND_HALF_UP` quantization.
2. **Database String Representation**: All financial amounts and rates are stored as exact numeric string representations (e.g., `"125000.00"`) in SQLite and PostgreSQL.
3. **Structured Bill of Quantities (BOQ)**: Granular line items categorized by Labor, Hardware, Software, Services, and Travel.
4. **Multi-Scenario Modeling**: Side-by-side comparison of Base Case, Conservative, and Aggressive commercial models.
5. **Publication-Grade Excel Export**: Styled spreadsheets generated using `openpyxl` with dynamic currency formats, borders, formulas, and scenario tabs.

---

## 2. Pricing Calculation Architecture

All pricing calculations follow a standardized, auditable formula hierarchy:

```
  Line Item Total = Quantity * Unit Rate
  
  Subtotal = SUM(Line Item Totals)
  
  Contingency Amount = Subtotal * (Contingency Rate % / 100)
  Overhead Amount    = Subtotal * (Overhead Rate % / 100)
  
  Base Delivery Cost = Subtotal + Contingency Amount + Overhead Amount
  
  Gross Margin Amount = Base Delivery Cost * (Margin Rate % / 100)
  
  Net Price Before Tax = Base Delivery Cost + Gross Margin Amount
  
  Statutory Tax Amount = Net Price Before Tax * (Tax Rate % / 100)
  
  GRAND TOTAL PRICE = Net Price Before Tax + Statutory Tax Amount
```

### Deterministic Implementation Example
```python
from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")

subtotal = (qty * unit_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
contingency = (subtotal * (contingency_rate / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
overhead = (subtotal * (overhead_rate / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
base_cost = subtotal + contingency + overhead
margin = (base_cost * (margin_rate / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
net_price = base_cost + margin
tax = (net_price * (tax_rate / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
grand_total = net_price + tax
```

---

## 3. Multi-Scenario Modeling

TenderForge supports instant scenario evaluation defined in `config/financial_policies.yaml`:

| Scenario | Margin % | Contingency Buffer % | Discount % | Strategic Objective |
|---|---|---|---|---|
| **Base Case** | `15.00%` | `5.00%` | `0.00%` | Standard delivery with healthy profitability and balanced risk buffer. |
| **Conservative** | `22.00%` | `10.00%` | `0.00%` | Risk-averse model with high contingencies for complex, unfamiliar environments. |
| **Aggressive** | `9.50%` | `3.00%` | `5.00%` | Price-competitive model designed to win high-volume commoditized awards. |

---

## 4. Bill of Quantities (BOQ) Validation

The workspace runs automated validation checks on every save:
- **Negative Rates**: Rejects negative unit rates.
- **Zero / Negative Quantities**: Disallows non-positive quantities.
- **Margin Threshold Warnings**: Warns if net margin falls below corporate minimum policy (`5.00%`).
- **Contingency Floor Warnings**: Warns if contingency buffer is below `2.00%` on fixed-price contracts.
