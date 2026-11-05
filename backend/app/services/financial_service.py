"""
Financial Proposal & Commercial Workspace Service for TenderForge.

Strictly enforces deterministic calculations using Python's Decimal arithmetic.
Provides Bill of Quantities (BOQ) management, multi-scenario pricing modeling,
and Excel/Word commercial proposal export.
"""

from __future__ import annotations

import io
import logging
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from backend.app.core.config import settings
from backend.app.infrastructure.database.models import (
    FinancialLineItem,
    FinancialProposal,
    FinancialScenario,
    Proposal,
    Tender,
    utcnow,
)

logger = logging.getLogger(__name__)

# Two decimal places rounding context
TWOPLACES = Decimal("0.01")


def to_decimal(val: Any) -> Decimal:
    """Safely convert any numeric/string value to Decimal."""
    if val is None or val == "":
        return Decimal("0.00")
    try:
        if isinstance(val, (int, float)):
            return Decimal(str(val)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        return Decimal(str(val).replace(",", "").strip()).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")


def fmt_decimal(val: Decimal) -> str:
    """Format decimal to exact string representation with 2 decimal places."""
    return str(val.quantize(TWOPLACES, rounding=ROUND_HALF_UP))


class FinancialService:
    """Manages commercial bid workspace, line items, scenarios, and deterministic financial math."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.policy = settings.financial_policies_config

    def create_financial_proposal(
        self,
        tender_id: str,
        proposal_id: Optional[str] = None,
        title: str = "Commercial Proposal & Pricing Schedule",
        currency: Optional[str] = None,
        tax_rate_percent: Optional[str] = None,
        contingency_rate_percent: Optional[str] = None,
        overhead_rate_percent: Optional[str] = None,
        margin_rate_percent: Optional[str] = None,
        initial_items: Optional[List[Dict[str, Any]]] = None,
        db: Optional[Session] = None,
    ) -> FinancialProposal:
        """Create a new financial proposal with baseline rates and line items."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tender = session.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        default_rates = self.policy.get("default_rates", {})
        curr = currency or tender.currency or self.policy.get("currency_defaults", {}).get("default_currency", "USD")
        tax_pct = tax_rate_percent or default_rates.get("tax_rate_percent", "10.00")
        cont_pct = contingency_rate_percent or default_rates.get("contingency_rate_percent", "5.00")
        oh_pct = overhead_rate_percent or default_rates.get("overhead_rate_percent", "8.00")
        margin_pct = margin_rate_percent or default_rates.get("margin_rate_percent", "15.00")

        fin_prop = FinancialProposal(
            tender_id=tender_id,
            proposal_id=proposal_id,
            title=title,
            currency=curr,
            tax_rate_percent=tax_pct,
            contingency_rate_percent=cont_pct,
            overhead_rate_percent=oh_pct,
            margin_rate_percent=margin_pct,
            status="Draft",
            validation_errors=[],
            assumptions=[
                "All prices quoted in designated currency.",
                "Tax rates applied as per prevailing statutory guidelines.",
                "Contingency provision allocated for unforeseen scope variations.",
            ],
        )
        session.add(fin_prop)
        session.flush()

        if initial_items:
            for idx, item in enumerate(initial_items):
                qty = to_decimal(item.get("quantity", 1))
                rate = to_decimal(item.get("unit_rate", 0))
                line_total = qty * rate
                line_item = FinancialLineItem(
                    financial_proposal_id=fin_prop.id,
                    item_code=item.get("item_code", f"ITEM-{idx+1:03d}"),
                    description=item.get("description", "Line Item"),
                    category=item.get("category", "Services"),
                    unit=item.get("unit", "each"),
                    quantity=fmt_decimal(qty),
                    unit_rate=fmt_decimal(rate),
                    tax_percent=str(item.get("tax_percent", tax_pct)),
                    line_total=fmt_decimal(line_total),
                    notes=item.get("notes"),
                    order_index=idx,
                )
                session.add(line_item)

        session.commit()
        self.recalculate(fin_prop.id, db=session)
        session.refresh(fin_prop)
        return fin_prop

    def add_line_item(
        self,
        financial_proposal_id: str,
        item_code: str,
        description: str,
        category: str,
        unit: str,
        quantity: Any,
        unit_rate: Any,
        tax_percent: Optional[Any] = None,
        notes: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> FinancialLineItem:
        """Add a single line item and trigger deterministic recalculation."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        prop = session.query(FinancialProposal).filter(FinancialProposal.id == financial_proposal_id).first()
        if not prop:
            raise ValueError(f"FinancialProposal '{financial_proposal_id}' not found.")

        qty_dec = to_decimal(quantity)
        rate_dec = to_decimal(unit_rate)
        line_total_dec = qty_dec * rate_dec
        tax_pct = str(tax_percent if tax_percent is not None else prop.tax_rate_percent)

        order_idx = len(prop.line_items)
        item = FinancialLineItem(
            financial_proposal_id=financial_proposal_id,
            item_code=item_code,
            description=description,
            category=category,
            unit=unit,
            quantity=fmt_decimal(qty_dec),
            unit_rate=fmt_decimal(rate_dec),
            tax_percent=tax_pct,
            line_total=fmt_decimal(line_total_dec),
            notes=notes,
            order_index=order_idx,
        )
        session.add(item)
        session.commit()

        self.recalculate(financial_proposal_id, db=session)
        session.refresh(item)
        return item

    def recalculate(
        self,
        financial_proposal_id: str,
        db: Optional[Session] = None,
    ) -> FinancialProposal:
        """Perform exact deterministic Decimal calculation of all subtotals, overhead, contingencies, margins, and taxes."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        prop = session.query(FinancialProposal).filter(FinancialProposal.id == financial_proposal_id).first()
        if not prop:
            raise ValueError(f"FinancialProposal '{financial_proposal_id}' not found.")

        subtotal_dec = Decimal("0.00")
        validation_errors: List[str] = []

        for item in prop.line_items:
            qty = to_decimal(item.quantity)
            rate = to_decimal(item.unit_rate)

            if qty <= Decimal("0.00"):
                validation_errors.append(f"Line item {item.item_code} has invalid quantity: {item.quantity}")
            if rate < Decimal("0.00"):
                validation_errors.append(f"Line item {item.item_code} has negative rate: {item.unit_rate}")

            line_tot = (qty * rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            item.line_total = fmt_decimal(line_tot)
            subtotal_dec += line_tot

        # Rates as Decimals
        contingency_rate = to_decimal(prop.contingency_rate_percent) / Decimal("100.00")
        overhead_rate = to_decimal(prop.overhead_rate_percent) / Decimal("100.00")
        margin_rate = to_decimal(prop.margin_rate_percent) / Decimal("100.00")
        tax_rate = to_decimal(prop.tax_rate_percent) / Decimal("100.00")

        contingency_amt = (subtotal_dec * contingency_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        overhead_amt = (subtotal_dec * overhead_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        # Base cost = subtotal + contingency + overhead
        base_cost = subtotal_dec + contingency_amt + overhead_amt
        margin_amt = (base_cost * margin_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        # Net price before tax = base_cost + margin
        net_before_tax = base_cost + margin_amt
        tax_amt = (net_before_tax * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        # Grand Total
        total_price = net_before_tax + tax_amt

        # Update record
        prop.subtotal = fmt_decimal(subtotal_dec)
        prop.contingency_amount = fmt_decimal(contingency_amt)
        prop.overhead_amount = fmt_decimal(overhead_amt)
        prop.margin_amount = fmt_decimal(margin_amt)
        prop.tax_amount = fmt_decimal(tax_amt)
        prop.total_price = fmt_decimal(total_price)
        prop.validation_errors = validation_errors
        prop.updated_at = utcnow()

        session.commit()
        session.refresh(prop)
        return prop

    def generate_scenarios(
        self,
        financial_proposal_id: str,
        db: Optional[Session] = None,
    ) -> List[FinancialScenario]:
        """Generate and evaluate multi-scenario pricing models (Base Case, Conservative, Aggressive)."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        prop = self.recalculate(financial_proposal_id, db=session)
        subtotal_dec = to_decimal(prop.subtotal)
        tax_rate = to_decimal(prop.tax_rate_percent) / Decimal("100.00")
        overhead_rate = to_decimal(prop.overhead_rate_percent) / Decimal("100.00")
        overhead_amt = (subtotal_dec * overhead_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        # Clear existing scenarios
        session.query(FinancialScenario).filter(
            FinancialScenario.financial_proposal_id == financial_proposal_id
        ).delete()

        scenario_templates = self.policy.get("scenario_templates", {})
        scenarios: List[FinancialScenario] = []

        for key, tpl in scenario_templates.items():
            margin_pct = to_decimal(tpl.get("margin_rate_percent", "15.00"))
            cont_pct = to_decimal(tpl.get("contingency_rate_percent", "5.00"))
            disc_pct = to_decimal(tpl.get("discount_percent", "0.00"))

            cont_amt = (subtotal_dec * (cont_pct / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            base_cost = subtotal_dec + cont_amt + overhead_amt
            margin_amt = (base_cost * (margin_pct / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

            gross_price = base_cost + margin_amt
            disc_amt = (gross_price * (disc_pct / Decimal("100.00"))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            net_before_tax = gross_price - disc_amt
            tax_amt = (net_before_tax * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            calculated_total = net_before_tax + tax_amt

            scen = FinancialScenario(
                financial_proposal_id=financial_proposal_id,
                scenario_name=tpl.get("name", key.title()),
                margin_rate_percent=fmt_decimal(margin_pct),
                contingency_rate_percent=fmt_decimal(cont_pct),
                discount_percent=fmt_decimal(disc_pct),
                calculated_total=fmt_decimal(calculated_total),
                summary_metrics={
                    "subtotal": fmt_decimal(subtotal_dec),
                    "overhead_amount": fmt_decimal(overhead_amt),
                    "contingency_amount": fmt_decimal(cont_amt),
                    "margin_amount": fmt_decimal(margin_amt),
                    "discount_amount": fmt_decimal(disc_amt),
                    "tax_amount": fmt_decimal(tax_amt),
                    "net_before_tax": fmt_decimal(net_before_tax),
                    "grand_total": fmt_decimal(calculated_total),
                    "currency": prop.currency,
                },
            )
            session.add(scen)
            scenarios.append(scen)

        session.commit()
        for s in scenarios:
            session.refresh(s)
        return scenarios

    def export_excel(
        self,
        financial_proposal_id: str,
        output_path: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> str:
        """Export financial schedule to a formatted, publication-ready Excel spreadsheet (.xlsx)."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        prop = session.query(FinancialProposal).filter(FinancialProposal.id == financial_proposal_id).first()
        if not prop:
            raise ValueError(f"FinancialProposal '{financial_proposal_id}' not found.")

        wb = openpyxl.Workbook()
        ws_boq = wb.active
        ws_boq.title = "Pricing Schedule (BOQ)"

        # Styles
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="1F4E79")
        bold_font = Font(name="Calibri", size=11, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9"),
        )
        total_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

        # Title Block
        ws_boq["A1"] = f"{prop.title} - {prop.currency}"
        ws_boq["A1"].font = title_font
        ws_boq["A2"] = f"Tender Reference: {prop.tender.reference_number or prop.tender.title}"
        ws_boq["A2"].font = Font(name="Calibri", size=10, italic=True)

        headers = ["Item Code", "Description", "Category", "Unit", "Quantity", "Unit Rate", "Tax %", f"Line Total ({prop.currency})"]
        for col_idx, h in enumerate(headers, 1):
            cell = ws_boq.cell(row=4, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center" if col_idx in [1, 3, 4] else "left")

        current_row = 5
        for item in prop.line_items:
            ws_boq.cell(row=current_row, column=1, value=item.item_code).alignment = Alignment(horizontal="center")
            ws_boq.cell(row=current_row, column=2, value=item.description)
            ws_boq.cell(row=current_row, column=3, value=item.category).alignment = Alignment(horizontal="center")
            ws_boq.cell(row=current_row, column=4, value=item.unit).alignment = Alignment(horizontal="center")
            ws_boq.cell(row=current_row, column=5, value=float(item.quantity)).number_format = "#,##0.00"
            ws_boq.cell(row=current_row, column=6, value=float(item.unit_rate)).number_format = f"#,##0.00"
            ws_boq.cell(row=current_row, column=7, value=f"{item.tax_percent}%").alignment = Alignment(horizontal="center")
            ws_boq.cell(row=current_row, column=8, value=float(item.line_total)).number_format = f"#,##0.00"

            for c in range(1, 9):
                ws_boq.cell(row=current_row, column=c).border = thin_border
            current_row += 1

        # Summary Block
        current_row += 1
        summary_rows = [
            ("Subtotal", float(prop.subtotal)),
            (f"Contingency ({prop.contingency_rate_percent}%)", float(prop.contingency_amount)),
            (f"Overhead ({prop.overhead_rate_percent}%)", float(prop.overhead_amount)),
            (f"Margin ({prop.margin_rate_percent}%)", float(prop.margin_amount)),
            (f"Applicable Taxes ({prop.tax_rate_percent}%)", float(prop.tax_amount)),
            (f"TOTAL PROPOSAL PRICE ({prop.currency})", float(prop.total_price)),
        ]

        for label, val in summary_rows:
            ws_boq.cell(row=current_row, column=7, value=label).font = bold_font
            tot_cell = ws_boq.cell(row=current_row, column=8, value=val)
            tot_cell.number_format = f"#,##0.00"
            tot_cell.font = bold_font
            if "TOTAL" in label:
                tot_cell.fill = total_fill
                ws_boq.cell(row=current_row, column=7).fill = total_fill
            current_row += 1

        # Auto-adjust column widths
        for col in ws_boq.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_boq.column_dimensions[col_letter].width = max(max_len + 3, 12)

        # Scenarios Tab
        if prop.scenarios:
            ws_scen = wb.create_sheet(title="Commercial Scenarios")
            ws_scen["A1"] = "Commercial Pricing Scenarios"
            ws_scen["A1"].font = title_font

            scen_headers = ["Scenario", "Margin %", "Contingency %", "Discount %", f"Total ({prop.currency})"]
            for c_idx, h in enumerate(scen_headers, 1):
                c = ws_scen.cell(row=3, column=c_idx, value=h)
                c.fill = header_fill
                c.font = header_font
                c.alignment = Alignment(horizontal="center")

            s_row = 4
            for s in prop.scenarios:
                ws_scen.cell(row=s_row, column=1, value=s.scenario_name).font = bold_font
                ws_scen.cell(row=s_row, column=2, value=f"{s.margin_rate_percent}%").alignment = Alignment(horizontal="center")
                ws_scen.cell(row=s_row, column=3, value=f"{s.contingency_rate_percent}%").alignment = Alignment(horizontal="center")
                ws_scen.cell(row=s_row, column=4, value=f"{s.discount_percent}%").alignment = Alignment(horizontal="center")
                tot_c = ws_scen.cell(row=s_row, column=5, value=float(s.calculated_total))
                tot_c.number_format = "#,##0.00"
                tot_c.font = bold_font
                for col_i in range(1, 6):
                    ws_scen.cell(row=s_row, column=col_i).border = thin_border
                s_row += 1

            for col in ws_scen.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws_scen.column_dimensions[col_letter].width = max(max_len + 3, 14)

        dest_path = output_path or f"{settings.STORAGE_ROOT}/financial_proposals/{prop.id}.xlsx"
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        wb.save(dest_path)
        logger.info("Saved Excel financial proposal to %s", dest_path)
        return dest_path
