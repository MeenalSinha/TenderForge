"""
Unit tests for Financial Proposal & Commercial Workspace Service.
Tests deterministic Decimal arithmetic, BOQ line items, multi-scenario generation, and Excel export.
"""

from decimal import Decimal
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    FinancialProposal,
    Organization,
    Tender,
    Workspace,
)
from backend.app.services.financial_service import FinancialService, to_decimal


@pytest.fixture
def financial_tender(db_session: Session):
    org = Organization(name="Finance Org", slug="fin-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="Finance WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(
        workspace_id=ws.id,
        title="Commercial Infrastructure Bid",
        reference_number="COMM-2026-001",
        currency="USD",
    )
    db_session.add(tender)
    db_session.commit()
    return tender


def test_deterministic_decimal_arithmetic(db_session: Session, financial_tender):
    """Ensure financial calculations are exact without binary floating point errors."""
    svc = FinancialService(db_session)

    items = [
        {"item_code": "LAB-01", "description": "Senior Solution Architect", "category": "Labor", "unit": "hrs", "quantity": "160.00", "unit_rate": "150.00"},
        {"item_code": "HW-02", "description": "High Availability Server Rack", "category": "Hardware", "unit": "units", "quantity": "2.00", "unit_rate": "12500.50"},
        {"item_code": "LIC-03", "description": "Enterprise Database Licenses", "category": "Software", "unit": "licenses", "quantity": "4.00", "unit_rate": "3750.25"},
    ]

    prop = svc.create_financial_proposal(
        tender_id=financial_tender.id,
        title="Deterministic Commercial Pricing",
        currency="USD",
        tax_rate_percent="10.00",
        contingency_rate_percent="5.00",
        overhead_rate_percent="8.00",
        margin_rate_percent="15.00",
        initial_items=items,
        db=db_session,
    )

    # Subtotal:
    # 160 * 150 = 24,000.00
    # 2 * 12500.50 = 25,001.00
    # 4 * 3750.25 = 15,001.00
    # Total Subtotal = 64,002.00
    expected_subtotal = Decimal("64002.00")
    assert to_decimal(prop.subtotal) == expected_subtotal

    # Contingency (5%): 64,002.00 * 0.05 = 3,200.10
    expected_contingency = Decimal("3200.10")
    assert to_decimal(prop.contingency_amount) == expected_contingency

    # Overhead (8%): 64,002.00 * 0.08 = 5,120.16
    expected_overhead = Decimal("5120.16")
    assert to_decimal(prop.overhead_amount) == expected_overhead

    # Base cost = 64,002.00 + 3,200.10 + 5,120.16 = 72,322.26
    # Margin (15%): 72,322.26 * 0.15 = 10,848.34
    expected_margin = Decimal("10848.34")
    assert to_decimal(prop.margin_amount) == expected_margin

    # Net before tax = 72,322.26 + 10,848.34 = 83,170.60
    # Tax (10%): 83,170.60 * 0.10 = 8,317.06
    expected_tax = Decimal("8317.06")
    assert to_decimal(prop.tax_amount) == expected_tax

    # Total Price = 83,170.60 + 8,317.06 = 91,487.66
    expected_total = Decimal("91487.66")
    assert to_decimal(prop.total_price) == expected_total


def test_scenario_generation(db_session: Session, financial_tender):
    svc = FinancialService(db_session)
    prop = svc.create_financial_proposal(
        tender_id=financial_tender.id,
        initial_items=[{"item_code": "SVC-1", "description": "Consulting", "quantity": "100", "unit_rate": "100.00"}],
        db=db_session,
    )

    scenarios = svc.generate_scenarios(prop.id, db=db_session)
    assert len(scenarios) == 3

    names = [s.scenario_name for s in scenarios]
    assert "Base Case" in names
    assert "Conservative" in names
    assert "Aggressive" in names

    # Conservative total should be higher than Aggressive
    conservative = next(s for s in scenarios if s.scenario_name == "Conservative")
    aggressive = next(s for s in scenarios if s.scenario_name == "Aggressive")
    assert to_decimal(conservative.calculated_total) > to_decimal(aggressive.calculated_total)


def test_excel_commercial_export(db_session: Session, financial_tender, tmp_path):
    svc = FinancialService(db_session)
    prop = svc.create_financial_proposal(
        tender_id=financial_tender.id,
        initial_items=[
            {"item_code": "ENG-01", "description": "DevOps Engineer", "category": "Labor", "unit": "hrs", "quantity": "80", "unit_rate": "120.00"},
        ],
        db=db_session,
    )
    svc.generate_scenarios(prop.id, db=db_session)

    export_file = str(tmp_path / "test_boq_export.xlsx")
    saved_path = svc.export_excel(prop.id, output_path=export_file, db=db_session)

    assert Path(saved_path).exists()
    assert Path(saved_path).stat().st_size > 1000
