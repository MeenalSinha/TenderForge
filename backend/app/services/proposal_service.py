"""
Evidence-Backed Proposal Architect Service for TenderForge.
Generates structured proposal drafts with embedded ProofLink citations and DOCX export.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import EntityNotFoundError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    ComplianceMatrix,
    EvidenceRequirementLink,
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalRevision,
    ProposalSection,
    Tender,
    TenderRequirement,
)
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.prooflink_service import ProofLinkStatus

logger = get_logger("proposal_service")


class ProposalService:
    """Drafts evidence-backed proposal responses with embedded ProofLink citations."""

    def __init__(self, compliance_service: Optional[ComplianceService] = None):
        self.compliance_service = compliance_service or ComplianceService()

    def create_proposal_draft(
        self,
        db: Session,
        tender_id: str,
        title: Optional[str] = None,
        author_id: str = "ProposalArchitect",
    ) -> Proposal:
        """Generate a complete evidence-backed proposal draft for a tender."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        # Fetch latest compliance matrix
        matrix = self.compliance_service.get_latest_matrix(db, tender_id)
        if not matrix:
            matrix = self.compliance_service.evaluate_tender_compliance(db, tender_id)

        # Retrieve organization profile
        profile = None
        if tender.workspace and tender.workspace.organization_id:
            profile = db.query(OrganizationProfile).filter(
                OrganizationProfile.organization_id == tender.workspace.organization_id
            ).first()

        proposal_title = title or f"Technical & Commercial Proposal: {tender.title}"
        proposal = Proposal(
            tender_id=tender_id,
            title=proposal_title,
            current_version=1,
            status="drafting",
            executive_summary=f"Responsive bid submitted for {tender.title} (Ref: {tender.reference_number or 'N/A'}).",
        )
        db.add(proposal)
        db.flush()

        # Build Section 1: Executive Summary & Corporate Profile
        sec1_content, sec1_claims = self._build_executive_summary_section(tender, profile, db)
        s1 = ProposalSection(
            proposal_id=proposal.id,
            section_number="1.0",
            title="Executive Summary & Corporate Profile",
            content=sec1_content,
            claims=sec1_claims,
        )
        db.add(s1)

        # Build Section 2: Technical Approach & Solution Architecture
        sec2_content, sec2_claims = self._build_technical_section(tender, matrix, db)
        s2 = ProposalSection(
            proposal_id=proposal.id,
            section_number="2.0",
            title="Technical Approach & Solution Architecture",
            content=sec2_content,
            claims=sec2_claims,
        )
        db.add(s2)

        # Build Section 3: Past Performance & Verifiable References
        sec3_content, sec3_claims = self._build_past_performance_section(tender, db)
        s3 = ProposalSection(
            proposal_id=proposal.id,
            section_number="3.0",
            title="Past Performance & Experience Records",
            content=sec3_content,
            claims=sec3_claims,
        )
        db.add(s3)

        # Build Section 4: Quality Management, Standards & Team
        sec4_content, sec4_claims = self._build_quality_section(profile, db)
        s4 = ProposalSection(
            proposal_id=proposal.id,
            section_number="4.0",
            title="Quality Assurance & Certified Standards",
            content=sec4_content,
            claims=sec4_claims,
        )
        db.add(s4)

        # Build Section 5: Compliance Matrix & Mandatory Undertakings
        sec5_content, sec5_claims = self._build_compliance_matrix_section(matrix)
        s5 = ProposalSection(
            proposal_id=proposal.id,
            section_number="5.0",
            title="Compliance Matrix & Statutory Undertakings",
            content=sec5_content,
            claims=sec5_claims,
        )
        db.add(s5)

        db.flush()

        # Create initial snapshot revision
        snapshot = {
            "title": proposal.title,
            "version": proposal.current_version,
            "sections": [
                {"number": s.section_number, "title": s.title, "content": s.content, "claims": s.claims}
                for s in [s1, s2, s3, s4, s5]
            ]
        }
        revision = ProposalRevision(
            proposal_id=proposal.id,
            version_number=1,
            author_type="agent",
            author_id=author_id,
            change_summary="Initial evidence-grounded proposal draft generated.",
            snapshot=snapshot,
        )
        db.add(revision)

        # Generate DOCX export
        docx_path = self.export_to_docx(proposal, [s1, s2, s3, s4, s5], tender)
        proposal.docx_file_path = docx_path

        db.commit()
        db.refresh(proposal)
        logger.info(f"Generated proposal '{proposal.title}' ({proposal.id}) with {len(snapshot['sections'])} sections.")
        return proposal

    def export_to_docx(
        self,
        proposal: Proposal,
        sections: List[ProposalSection],
        tender: Tender,
    ) -> str:
        """Export proposal sections and ProofLink citations into a formatted Word (.docx) document."""
        doc = docx.Document()

        # Document Header
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(proposal.title)
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(15, 23, 42)  # Slate-900

        sub_p = doc.add_paragraph()
        sub_run = sub_p.add_run(
            f"Tender Reference: {tender.reference_number or 'N/A'} | Issuing Authority: {tender.issuing_authority or 'Procurement Authority'}\n"
            f"Generated by TenderForge Multi-Agent Workspace | Version: {proposal.current_version}.0"
        )
        sub_run.font.size = Pt(10)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(100, 116, 139)  # Slate-500

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        # Add Sections
        for sec in sorted(sections, key=lambda s: s.section_number):
            h = doc.add_heading(f"{sec.section_number} {sec.title}", level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)

            # Paragraphs
            for paragraph_text in sec.content.split("\n\n"):
                if paragraph_text.strip():
                    p = doc.add_paragraph(paragraph_text.strip())
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(6)

            # Claims / ProofLink Footnotes
            if sec.claims:
                claim_p = doc.add_paragraph()
                claim_p.paragraph_format.space_before = Pt(6)
                claim_title = claim_p.add_run("ProofLink™ Evidence Citations:")
                claim_title.font.bold = True
                claim_title.font.size = Pt(9)
                claim_title.font.color.rgb = RGBColor(30, 41, 59)

                for c in sec.claims:
                    cp = doc.add_paragraph(style="List Bullet")
                    cp.paragraph_format.space_after = Pt(2)
                    c_run = cp.add_run(f"[{c.get('status')}] {c.get('text')}")
                    c_run.font.size = Pt(8.5)
                    if c.get("status") in (ProofLinkStatus.VERIFIED, ProofLinkStatus.HUMAN_CONFIRMED):
                        c_run.font.color.rgb = RGBColor(22, 101, 52)  # Green-800
                    elif c.get("status") == ProofLinkStatus.CONTRADICTED:
                        c_run.font.color.rgb = RGBColor(153, 27, 27)  # Red-800
                    else:
                        c_run.font.color.rgb = RGBColor(180, 83, 9)  # Amber-700

        # Save DOCX
        storage_dir = Path(settings.STORAGE_LOCAL_PATH) / "proposals"
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / f"proposal_{proposal.id}_v{proposal.current_version}.docx"
        doc.save(str(file_path))
        return str(file_path)

    def _build_executive_summary_section(
        self,
        tender: Tender,
        profile: Optional[OrganizationProfile],
        db: Session,
    ) -> tuple[str, List[Dict[str, Any]]]:
        org_name = profile.legal_name if profile else "The Bidder Organization"
        reg_num = profile.registration_number if profile else "N/A"
        claims = []

        turnover_text = "audited financial records"
        if profile and profile.financial_metrics:
            turnover_items = [f"{k.upper()}: ${v:,.2f}" for k, v in profile.financial_metrics.items()]
            turnover_text = ", ".join(turnover_items)
            claims.append({
                "text": f"Financial turnover capacity documented: {turnover_text}",
                "status": ProofLinkStatus.VERIFIED,
                "evidence_id": profile.id,
                "citation": "Profile Financial Metrics",
            })

        content = (
            f"{org_name} is pleased to submit this comprehensive technical and commercial proposal in response to "
            f"{tender.title} (Ref: {tender.reference_number or 'N/A'}).\n\n"
            f"Our organization is duly incorporated and registered under reference {reg_num}, operating with full legal standing. "
            f"We offer proven technical excellence backed by verified operational capacity: {turnover_text}."
        )
        return content, claims

    def _build_technical_section(
        self,
        tender: Tender,
        matrix: ComplianceMatrix,
        db: Session,
    ) -> tuple[str, List[Dict[str, Any]]]:
        tech_items = [item for item in matrix.items if item.get("category") == "technical"]
        claims = []
        body_parts = [
            f"Our technical architecture is formulated to satisfy all core deliverables stipulated in {tender.title}. "
            f"We implement high-availability, modular enterprise solutions ensuring scalability, business continuity, and adherence to service level agreements."
        ]

        for item in tech_items:
            req_desc = item.get("description", "")
            status = item.get("status")
            if status == "Compliant":
                body_parts.append(
                    f"In direct fulfillment of Clause ({req_desc}), our solution integrates verified enterprise infrastructure "
                    f"configured for continuous operational availability. [ProofLink: {item.get('evidence_id') or 'EVID-SYS'} | Status: Verified]"
                )
                claims.append({
                    "text": f"Satisfies technical clause: {req_desc[:80]}...",
                    "status": ProofLinkStatus.VERIFIED,
                    "evidence_id": item.get("evidence_id"),
                    "citation": item.get("evidence_summary"),
                })
            else:
                body_parts.append(
                    f"[ACTION REQUIRED: Technical deliverable '{req_desc}' requires specific architecture documentation. "
                    f"Remedial action: {item.get('action_required')}]"
                )
                claims.append({
                    "text": f"Technical clause requires action: {req_desc[:80]}...",
                    "status": ProofLinkStatus.PENDING,
                    "evidence_id": None,
                    "citation": "Action Required - Human Input Needed",
                })

        return "\n\n".join(body_parts), claims

    def _build_past_performance_section(
        self,
        tender: Tender,
        db: Session,
    ) -> tuple[str, List[Dict[str, Any]]]:
        # Search past project evidence
        projects = db.query(CompanyEvidence).filter(
            CompanyEvidence.evidence_type == "past_project"
        ).all()

        claims = []
        body_parts = [
            "We present the following audited past performance records demonstrating successful execution of similar scope and complexity:"
        ]

        if not projects:
            body_parts.append(
                "[ACTION REQUIRED: No past performance certificates currently verified in evidence repository. "
                "Upload client completion certificates to substantiate project credentials.]"
            )
            claims.append({
                "text": "Past performance verification pending evidence upload.",
                "status": ProofLinkStatus.UNSUPPORTED,
                "evidence_id": None,
                "citation": "Zero records in repository",
            })
        else:
            for p in projects:
                body_parts.append(
                    f"• {p.title} (Issuer: {p.issuer or 'Enterprise Client'})\n"
                    f"  {p.summary or 'Successfully delivered on schedule and within budget.'}\n"
                    f"  [ProofLink: {p.id} | Status: Verified]"
                )
                claims.append({
                    "text": f"Delivered project: {p.title}",
                    "status": ProofLinkStatus.VERIFIED,
                    "evidence_id": p.id,
                    "citation": p.reference_number or p.title,
                })

        return "\n\n".join(body_parts), claims

    def _build_quality_section(
        self,
        profile: Optional[OrganizationProfile],
        db: Session,
    ) -> tuple[str, List[Dict[str, Any]]]:
        certs = db.query(CompanyEvidence).filter(
            CompanyEvidence.evidence_type == "certification"
        ).all()

        claims = []
        body_parts = [
            "Our operations adhere strictly to internationally benchmarked quality, information security, and governance standards."
        ]

        if certs:
            for c in certs:
                body_parts.append(
                    f"• {c.title} (Certified by {c.issuer or 'Accredited Registrar'}, Status: {c.status.upper()})\n"
                    f"  [ProofLink: {c.id} | Valid Through: {c.expiry_date.strftime('%Y-%m-%d') if c.expiry_date else 'Active'}]"
                )
                claims.append({
                    "text": f"Accreditation: {c.title}",
                    "status": ProofLinkStatus.VERIFIED if c.status == "valid" else ProofLinkStatus.CONTRADICTED,
                    "evidence_id": c.id,
                    "citation": c.reference_number or c.title,
                })
        else:
            body_parts.append(
                "[ACTION REQUIRED: Quality certificates not linked. Verification from registrar required.]"
            )

        return "\n\n".join(body_parts), claims

    def _build_compliance_matrix_section(
        self,
        matrix: ComplianceMatrix,
    ) -> tuple[str, List[Dict[str, Any]]]:
        claims = []
        body_parts = [
            f"The bidder provides the following structured compliance matrix evaluated against all mandatory tender requirements (Overall Evaluation: {matrix.overall_status.upper()}, Risk Profile: {matrix.overall_risk_level.upper()}):"
        ]

        for item in matrix.items:
            status = item.get("status")
            desc = item.get("description", "")
            cat = item.get("category", "").upper()
            body_parts.append(
                f"• [{cat}] {desc[:90]}...\n"
                f"  Status: {status} | Risk: {item.get('risk_level')} | Evidence: {item.get('evidence_summary')}"
            )
            claims.append({
                "text": f"Compliance declaration for {cat}: {desc[:60]}...",
                "status": ProofLinkStatus.VERIFIED if status == "Compliant" else ProofLinkStatus.PENDING,
                "evidence_id": item.get("evidence_id"),
                "citation": item.get("evidence_summary"),
            })

        return "\n\n".join(body_parts), claims

    def get_proposal(self, db: Session, proposal_id: str) -> Optional[Proposal]:
        return db.query(Proposal).filter(Proposal.id == proposal_id).first()

    def get_latest_proposal(self, db: Session, tender_id: str) -> Optional[Proposal]:
        return db.query(Proposal).filter(
            Proposal.tender_id == tender_id
        ).order_by(Proposal.created_at.desc()).first()
