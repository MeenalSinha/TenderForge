"""
Final Bid Package Export Service for TenderForge.
Generates submission-ready bundles containing DOCX proposals, XLSX compliance matrices, and audit certificates.
"""

from __future__ import annotations

import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import zipfile
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import EntityNotFoundError, SecurityError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    BidAudit,
    ComplianceMatrix,
    HumanApproval,
    Proposal,
    ProposalSection,
    Tender,
)
from backend.app.services.approval_service import ApprovalService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.proposal_service import ProposalService

logger = get_logger("export_service")


class ExportService:
    """Packages proposal deliverables, compliance matrices, audit reports, and human certificates into ZIP bundles."""

    def __init__(
        self,
        approval_service: Optional[ApprovalService] = None,
        compliance_service: Optional[ComplianceService] = None,
        proposal_service: Optional[ProposalService] = None,
    ):
        self.approval_service = approval_service or ApprovalService()
        self.compliance_service = compliance_service or ComplianceService()
        self.proposal_service = proposal_service or ProposalService()

    def generate_compliance_xlsx(self, matrix: ComplianceMatrix, output_path: Path) -> str:
        """Generate a formatted Excel (.xlsx) compliance matrix workbook using openpyxl."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Compliance Matrix"

        # Styles
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1"),
        )

        headers = [
            "Category",
            "Classification",
            "Requirement Description",
            "Source Page",
            "Compliance Status",
            "Risk Level",
            "Evidence Summary",
            "Required Remedial Action",
        ]
        ws.append(headers)

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Status fills
        green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        yellow_fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")

        for item in matrix.items:
            status = item.get("status", "")
            row = [
                str(item.get("category", "")).upper(),
                str(item.get("classification", "")).capitalize(),
                item.get("description", ""),
                item.get("source_page", "N/A"),
                status,
                item.get("risk_level", "Medium"),
                item.get("evidence_summary", "None"),
                item.get("action_required") or "None",
            ]
            ws.append(row)
            current_row = ws.max_row
            
            # Apply styling
            for col_idx in range(1, len(headers) + 1):
                c = ws.cell(row=current_row, column=col_idx)
                c.border = border
                c.alignment = Alignment(vertical="center", wrap_text=True)

            status_cell = ws.cell(row=current_row, column=5)
            if status == "Compliant":
                status_cell.fill = green_fill
            elif status == "Non-Compliant":
                status_cell.fill = red_fill
            else:
                status_cell.fill = yellow_fill

        # Adjust column widths
        ws.column_dimensions["A"].width = 16
        ws.column_dimensions["B"].width = 16
        ws.column_dimensions["C"].width = 45
        ws.column_dimensions["D"].width = 12
        ws.column_dimensions["E"].width = 20
        ws.column_dimensions["F"].width = 14
        ws.column_dimensions["G"].width = 35
        ws.column_dimensions["H"].width = 35

        wb.save(str(output_path))
        return str(output_path)

    def export_bid_package(
        self,
        db: Session,
        tender_id: str,
        proposal_id: str,
        require_human_approval: bool = True,
    ) -> str:
        """Create a complete submission-ready ZIP bundle."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise EntityNotFoundError(f"Proposal '{proposal_id}' not found.")

        # Human Approval Enforcement Gate
        approval = db.query(HumanApproval).filter(
            HumanApproval.proposal_id == proposal_id,
            HumanApproval.decision == "Approved",
        ).first()

        if require_human_approval and not approval:
            raise SecurityError(
                f"Bid Package submission blocked: Proposal '{proposal_id}' has not received mandatory human sign-off."
            )

        matrix = self.compliance_service.get_latest_matrix(db, tender_id)
        audit = db.query(BidAudit).filter(
            BidAudit.proposal_id == proposal_id
        ).order_by(BidAudit.created_at.desc()).first()

        # Output directory
        export_dir = Path(settings.STORAGE_LOCAL_PATH) / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        zip_path = export_dir / f"bid_package_{tender.reference_number or tender.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"

        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Proposal DOCX
            if proposal.docx_file_path and os.path.exists(proposal.docx_file_path):
                zip_file.write(proposal.docx_file_path, arcname=f"01_Technical_Proposal_v{proposal.current_version}.docx")

            # 2. Compliance Matrix XLSX
            if matrix:
                xlsx_temp = export_dir / f"compliance_matrix_{tender_id}.xlsx"
                self.generate_compliance_xlsx(matrix, xlsx_temp)
                zip_file.write(str(xlsx_temp), arcname="02_Compliance_Matrix.xlsx")
                if xlsx_temp.exists():
                    os.remove(xlsx_temp)

            # 3. Independent Bid Audit Report
            if audit:
                audit_summary = (
                    f"TENDERFORGE INDEPENDENT BID AUDIT REPORT\n"
                    f"{'='*50}\n"
                    f"Tender Reference : {tender.reference_number or 'N/A'}\n"
                    f"Proposal Title   : {proposal.title}\n"
                    f"Auditor ID       : {audit.auditor_id}\n"
                    f"Audit Verdict    : {audit.verdict}\n"
                    f"Readiness Score  : {audit.readiness_score} / 100.0\n"
                    f"Claims Audited   : Total={audit.total_claims}, Verified={audit.verified_claims}, Unsupported={audit.unsupported_claims}, Contradicted={audit.contradicted_claims}\n\n"
                    f"FINDINGS BREAKDOWN:\n"
                    f"{'-'*50}\n"
                )
                for f in audit.findings:
                    audit_summary += f"[{f.get('severity')}] {f.get('category')} - {f.get('section')}\n  Claim: {f.get('claim_text')}\n  Issue: {f.get('description')}\n  Action: {f.get('recommendation')}\n\n"
                zip_file.writestr("03_Independent_Bid_Audit_Report.txt", audit_summary)

            # 4. Human Sign-Off Certificate
            if approval:
                cert = {
                    "certificate_title": "TenderForge Digital Sign-Off Certificate",
                    "tender_id": tender.id,
                    "tender_title": tender.title,
                    "reference_number": tender.reference_number,
                    "proposal_id": proposal.id,
                    "approval_decision": approval.decision,
                    "authorized_user": {
                        "user_id": approval.user_id,
                        "name": approval.user_name,
                        "role": approval.user_role,
                    },
                    "decision_timestamp": approval.created_at.isoformat(),
                    "comments": approval.comments,
                    "cryptographic_signature_hash": approval.signature_hash,
                    "verification_algorithm": "SHA-256",
                }
                zip_file.writestr("04_Human_Sign_Off_Certificate.json", json.dumps(cert, indent=2))

        logger.info(f"Generated bid package bundle for tender {tender_id} at {zip_path}")
        return str(zip_path)
