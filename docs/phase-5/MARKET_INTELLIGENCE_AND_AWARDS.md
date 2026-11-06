# Phase 5: Market Intelligence & Public Awards Ingestion

## 1. Overview

Competitive bidding requires deep understanding of buyer spending trends, historical winning price ranges, contract award frequencies, and market pricing dynamics. 

TenderForge aggregates, verifies, and analyzes **public contract awards** (`AwardRecord`), generating evidence-backed procurement market analytics while preserving strict provenance.

---

## 2. Public Award Ingestion & Schema

The `AwardRecord` model stores public contract outcomes:

```python
class AwardRecord(Base):
    __tablename__ = "award_records"

    id = Column(String(36), primary_key=True)
    external_award_id = Column(String(128), unique=True, index=True)
    buyer_name = Column(String(255), nullable=False)
    procurement_category = Column(String(128), nullable=False)
    title = Column(String(512), nullable=False)
    winning_supplier = Column(String(255), nullable=False)
    award_amount = Column(Float, nullable=False)
    currency = Column(String(8), default="USD")
    award_date = Column(DateTime, nullable=False)
    estimated_budget = Column(Float, nullable=True)
    number_of_bidders = Column(Integer, nullable=True)
    provenance_source = Column(String(128), nullable=False)
```

---

## 3. Provenance & Anti-Fabrication Principles

To maintain trust and data integrity:
1. **Zero Fabrication**: Market statistics are computed strictly from recorded `AwardRecord` entries. The service never improvises or hallucinates competitor pricing.
2. **Explicit Provenance**: Every record explicitly documents its `provenance_source` (e.g. `open_contracting_portal`, `ted_europa`, `manual_audit`).
3. **Public Data Boundary**: Only verified, publicly published contract award announcements are entered into the market registry. Proprietary client submissions are strictly segregated.

---

## 4. Market Analytics & Computations

The `MarketIntelligenceService.get_market_analytics()` endpoint computes:

- **Total Award Volume**: Sum of all awarded contract amounts.
- **Average & Median Award Value**: Benchmark sizing for procurement categories.
- **Average Discount Ratio**: 
  $$\text{Discount} = \frac{\text{Estimated Budget} - \text{Winning Award Amount}}{\text{Estimated Budget}}$$
  Provides pricing teams with empirical guidance on how aggressively competitors discount below government budget ceilings.
- **Top Buyers by Spend**: Ranked list of issuing authorities with contract counts and total expenditures.
- **Top Winning Suppliers**: Market share leaders in each procurement category.

---

## 5. REST API Endpoints

- `GET /api/v1/market/awards`: Filter awards by buyer, category, date range, or supplier.
- `GET /api/v1/market/analytics`: Aggregated market benchmarks and buyer breakdown.
- `POST /api/v1/market/awards`: Ingest verified public award records (Admin / Business Analyst only).
