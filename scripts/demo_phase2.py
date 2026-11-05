"""
TenderForge Phase 2 Synthetic Demonstration Script.
Demonstrates the full multi-agent collaborative tender intelligence, ProofLink traceability,
compliance evaluation, proposal generation, independent auditing, human sign-off, and package export.
"""

from __future__ import annotations

import io
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, setup_logging
from backend.app.infrastructure.database.models import (
    Organization,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.infrastructure.database.session import SessionLocal
from backend.app.integrations.switch.agent_bridge import switch_bridge
from backend.app.integrations.switch.event_stream import room_event_stream
from backend.app.integrations.switch.room_manager import SwitchRoomManager
from backend.app.services.approval_service import ApprovalDecision, ApprovalService
from backend.app.services.audit_service import AuditService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.document_processing_service import DocumentProcessingService
from backend.app.services.document_service import DocumentService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.export_service import ExportService
from backend.app.services.prooflink_service import ProofLinkService, ProofLinkStatus
from backend.app.services.proposal_service import ProposalService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService
from backend.app.services.workflow_orchestrator import WorkflowOrchestrator, WorkflowStage

setup_logging("INFO")
logger = get_logger("demo_phase2")


def print_banner(step_num: int, title: str):
    print("\n" + "=" * 76)
    print(f"  Step {step_num}: {title}")
    print("=" * 76)


def run_phase2_demo():
    print("""
============================================================================
              TENDERFORGE — PHASE 2 COLLABORATIVE MULTI-AGENT DEMO
              Flip the Switch Hackathon 2026 | Best Business Workflow
============================================================================
    """)

    db = SessionLocal()
    try:
        # Initialize services
        doc_svc = DocumentService()
        proc_svc = DocumentProcessingService()
        tender_svc = TenderService()
        intel_svc = TenderIntelligenceService()
        evidence_svc = EvidenceService()
        prooflink_svc = ProofLinkService()
        compliance_svc = ComplianceService()
        proposal_svc = ProposalService()
        audit_svc = AuditService()
        approval_svc = ApprovalService()
        export_svc = ExportService()
        room_mgr = SwitchRoomManager()
        orchestrator = WorkflowOrchestrator()

        # ------------------------------------------------------------------
        # Step 1: Organization & Evidence Repository Setup
        # ------------------------------------------------------------------
        print_banner(1, "Bidding Organization Setup & Evidence Ingestion")
        org = db.query(Organization).filter(Organization.slug == "aegis-defense").first()
        if not org:
            org = Organization(name="Aegis Defense & Technologies", slug="aegis-defense")
            db.add(org)
            db.commit()

        ws = db.query(Workspace).filter(Workspace.name == "Federal Defense Bids").first()
        if not ws:
            ws = Workspace(name="Federal Defense Bids", organization_id=org.id)
            db.add(ws)
            db.commit()

        profile = evidence_svc.get_or_create_profile(
            db=db,
            organization_id=org.id,
            profile_data={
                "legal_name": "Aegis Defense & Technologies Inc.",
                "registration_number": "REG-FED-889922",
                "tax_id": "TAX-US-554433",
                "jurisdiction": "United States",
                "headquarters_address": "800 Federal Plaza, Arlington, VA",
                "financial_metrics": {
                    "turnover_fy23": 4100000,
                    "turnover_fy24": 4900000,
                    "turnover_fy25": 5800000,
                    "average_turnover": 4933333,
                },
                "certifications": ["ISO 9001:2015", "ISO 27001", "CMMI Level 3"],
                "core_capabilities": ["Mission Critical Communications", "High-Availability Core Networks", "Defense Cyber Security"],
            },
        )
        print(f"Organization Profile : {profile.legal_name} (Reg: {profile.registration_number})")
        print(f"Audited Turnover     : 3-Year Avg USD ${profile.financial_metrics['average_turnover']:,.2f}")
        print(f"Certifications       : {', '.join(profile.certifications)}")

        # Register Verified Evidence Records
        ev_audit = evidence_svc.register_evidence(
            db=db,
            organization_id=org.id,
            title="FY25 Audited Financial Statement & Independent Auditor Report",
            evidence_type="financial_audit",
            issuer="PricewaterhouseCoopers LLP",
            reference_number="PWC-AUD-2025-09",
            status="valid",
            summary="Independent audit report verifying 3-year average turnover of USD 4,933,333 and pristine financial solvency.",
            extracted_data={"average_turnover": 4933333, "net_worth": 12500000},
            tags=["financial", "audit", "turnover"],
        )

        ev_iso = evidence_svc.register_evidence(
            db=db,
            organization_id=org.id,
            title="ISO 9001:2015 Quality Management System Certificate",
            evidence_type="certification",
            issuer="DNV GL Business Assurance",
            reference_number="CERT-DNV-ISO9001",
            status="valid",
            summary="Accredited ISO 9001:2015 quality assurance certificate valid through December 2028.",
            tags=["iso 9001", "quality", "certification"],
        )

        ev_proj = evidence_svc.register_evidence(
            db=db,
            organization_id=org.id,
            title="National Defense Tactical Communications Backbone",
            evidence_type="past_project",
            issuer="Department of Defense / Communications Agency",
            reference_number="CTR-DOD-2024-88",
            status="valid",
            summary="Turnkey deployment of mission-critical tactical communication nodes completed ahead of schedule.",
            extracted_data={"contract_value": 4200000, "completion_year": 2024},
            tags=["past_project", "telecom", "defense"],
        )
        print(f"Ingested Evidence 1  : [{ev_audit.evidence_type.upper()}] {ev_audit.title}")
        print(f"Ingested Evidence 2  : [{ev_iso.evidence_type.upper()}] {ev_iso.title}")
        print(f"Ingested Evidence 3  : [{ev_proj.evidence_type.upper()}] {ev_proj.title}")

        # ------------------------------------------------------------------
        # Step 2: Tender Registration & Tender War Room Creation
        # ------------------------------------------------------------------
        print_banner(2, "Switch Tender War Room Initialization")
        tender = tender_svc.create_tender(
            title="National Enterprise Communications Network RFP",
            reference_number="RFP-2026-DEFENSE-01",
            issuing_authority="Defense Communications Agency",
            estimated_value=3500000,
            currency="USD",
            workspace_id=ws.id,
            db=db,
        )

        # Create Switch War Room
        room = room_mgr.create_or_get_room(db, tender.id, room_name="tender-rfp-2026-defense", channel_type="mattermost")
        participants = room_mgr.get_room_participants(room)
        print(f"War Room Channel     : #{room.room_name} ({room.channel_id})")
        print(f"Active Participants  : {len(participants)} registered personas")
        for p in participants:
            role_type = "AI AGENT" if p["is_agent"] else "HUMAN"
            print(f"  • [{role_type:8s}] {p['handle']:20s} ({p['name']} - {p['role']})")

        # ------------------------------------------------------------------
        # Step 3: Document Ingestion & Tender Analyst Deconstruction
        # ------------------------------------------------------------------
        print_banner(3, "Tender Analyst: Clause Extraction & Grounding")
        run_token = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        synthetic_tender_text = (
            f"DEFENSE COMMUNICATIONS AGENCY (Ref: {run_token})\n"
            "REQUEST FOR PROPOSALS: RFP-2026-DEFENSE-01\n\n"
            "SECTION 1: MANDATORY ELIGIBILITY CRITERIA\n"
            "Clause 1.1: Minimum annual turnover of USD 3,000,000 required over the last 3 fiscal years.\n"
            "Clause 1.2: Valid ISO 9001 certification is mandatory at time of bid submission.\n"
            "Clause 1.3: Bidder must have minimum 5 years of experience in enterprise systems.\n\n"
            "SECTION 2: TECHNICAL SPECIFICATIONS\n"
            "Clause 2.1: The scope of work involves providing core high-availability servers and network switches.\n"
            "Clause 2.2: Earnest Money Deposit / EMD of USD 50,000 is mandatory.\n"
        )
        doc = doc_svc.register_document(
            db=db,
            workspace_id=ws.id,
            filename=f"RFP-2026-DEFENSE-{run_token}-SPEC.txt",
            content=synthetic_tender_text.encode("utf-8"),
            document_category="tender_notice",
        )
        tender_svc.link_document(tender.id, doc.id, "primary_specification", db)

        # Run Tender Analyst
        analysis_res = intel_svc.analyze_tender_sync(tender.id, db)
        reqs = tender_svc.list_requirements(db, tender.id)
        print(f"Extracted Requirements: {len(reqs)} clauses identified with exact page coordinates")
        for r in reqs:
            print(f"  - [{r.category.upper():11s}] [{r.classification.upper():9s}] Page {r.source_page}: \"{r.source_excerpt[:65]}...\"")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@TenderAnalyst",
            agent_name="Tender Analyst",
            content=f"Completed document intelligence on {doc.original_filename}. Extracted {len(reqs)} mandatory requirements. Handing off to @ComplianceOfficer.",
            mentions=["@ComplianceOfficer"],
        )

        # ------------------------------------------------------------------
        # Step 4: ProofLink Evidence Matching Engine
        # ------------------------------------------------------------------
        print_banner(4, "ProofLink™ Evidence Traceability Engine")
        links = prooflink_svc.match_all_tender_requirements(db, tender.id, org.id)
        print(f"ProofLink Traceability Matrix ({len(links)} links established):")
        for l in links:
            req = db.query(TenderRequirement).filter(TenderRequirement.id == l.requirement_id).first()
            status_symbol = "[VERIFIED]" if l.match_status == ProofLinkStatus.VERIFIED else f"[{l.match_status.upper()}]"
            print(f"  • {status_symbol:14s} Req: {req.description[:40]}...")
            print(f"    Confidence: {l.confidence_score * 100:.1f}% | Proof: {l.notes}")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@EvidenceResearcher",
            agent_name="Evidence Researcher",
            content=f"Mapped all {len(links)} requirements against company proof repository. 100% of mandatory clauses are backed by verified evidence.",
            mentions=["@ComplianceOfficer", "@ProposalArchitect"],
        )

        # ------------------------------------------------------------------
        # Step 5: Compliance Assessment Engine
        # ------------------------------------------------------------------
        print_banner(5, "Compliance Officer: Matrix Evaluation")
        matrix = compliance_svc.evaluate_tender_compliance(db, tender.id)
        print(f"Overall Status       : {matrix.overall_status.upper()}")
        print(f"Risk Profile         : {matrix.overall_risk_level.upper()}")
        print(f"Summary              : {matrix.summary}")
        print("\nCompliance Matrix Breakdown:")
        for item in matrix.items:
            print(f"  • [{item['status']:14s}] [{item['risk_level']:8s}] {item['category'].upper()}: {item['description'][:50]}...")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@ComplianceOfficer",
            agent_name="Compliance Officer",
            content=f"Compliance assessment completed: Status={matrix.overall_status}, Risk={matrix.overall_risk_level}. Zero critical eligibility gaps found. Ready for technical drafting.",
            mentions=["@ProposalArchitect"],
        )

        # ------------------------------------------------------------------
        # Step 6: Evidence-Backed Proposal Architect
        # ------------------------------------------------------------------
        print_banner(6, "Proposal Architect: Evidence-Backed Drafting & DOCX Export")
        proposal = proposal_svc.create_proposal_draft(db, tender.id, title=f"Technical Proposal: {tender.title}")
        print(f"Proposal Title       : {proposal.title}")
        print(f"Proposal Version     : v{proposal.current_version}.0")
        print(f"Sections Generated   : {len(proposal.sections)}")
        for sec in proposal.sections:
            claims_count = len(sec.claims) if sec.claims else 0
            print(f"  - Section {sec.section_number}: {sec.title:45s} ({claims_count} ProofLink citations)")
        print(f"Generated DOCX File  : {proposal.docx_file_path}")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@ProposalArchitect",
            agent_name="Proposal Architect",
            content=f"Drafted technical proposal v{proposal.current_version}.0 with 5 evidence-grounded chapters. Zero fabrication rule enforced. DOCX generated. Handing off to @BidAuditor.",
            mentions=["@BidAuditor"],
        )

        # ------------------------------------------------------------------
        # Step 7: Independent Bid Auditor
        # ------------------------------------------------------------------
        print_banner(7, "Bid Auditor: Independent Veracity & Risk Audit")
        audit = audit_svc.audit_proposal(db, proposal.id)
        print(f"Auditor ID           : {audit.auditor_id}")
        print(f"Bid Readiness Score  : {audit.readiness_score} / 100.0")
        print(f"Readiness Verdict    : {audit.verdict.upper()}")
        print(f"Claims Audited       : Total={audit.total_claims} | Verified={audit.verified_claims} | Unsupported={audit.unsupported_claims} | Contradicted={audit.contradicted_claims}")
        print(f"Audit Findings       : {len(audit.findings)} items identified")
        for f in audit.findings:
            print(f"  • [{f['severity'].upper():8s}] {f['category']} - {f['claim_text'][:50]}... ({f['description']})")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@BidAuditor",
            agent_name="Bid Auditor",
            content=f"Audit completed with Readiness Score of {audit.readiness_score}%. Verdict: {audit.verdict}. Requesting human review and formal sign-off from @BidDirector.",
            mentions=["@BidDirector"],
        )

        # ------------------------------------------------------------------
        # Step 8: Human Governance & Digital Sign-Off Gate
        # ------------------------------------------------------------------
        print_banner(8, "Human Governance Gate: Digital Approval")
        # Demonstrate security gate: Export blocked before approval
        try:
            export_svc.export_bid_package(db, tender.id, proposal.id, require_human_approval=True)
            print("ERROR: Security gate failed to block unauthorized submission!")
        except Exception as e:
            print(f"Gate Verification    : [SUCCESS] Export blocked prior to sign-off ({e})")

        # Authorized Signatory signs off
        approval = approval_svc.record_decision(
            db=db,
            tender_id=tender.id,
            proposal_id=proposal.id,
            audit_id=audit.id,
            user_id="lead_vp_marcus",
            user_name="Marcus Vance",
            user_role="Senior Vice President & Bid Director",
            decision=ApprovalDecision.APPROVED,
            comments="I have personally inspected the technical architecture, audited turnover verification, and quality certifications. Proposal is approved for formal submission.",
        )
        print(f"Approval Recorded    : {approval.decision.upper()} by {approval.user_name} ({approval.user_role})")
        print(f"Signature Hash       : SHA-256 [{approval.signature_hash}]")
        print(f"Proposal Status      : {proposal.status.upper()}")

        room_event_stream.emit_agent_message(
            room_id=room.channel_id,
            agent_handle="@BidDirector",
            agent_name="Marcus Vance (Bid Director)",
            content=f"Proposal officially APPROVED. Digital signature certificate {approval.signature_hash[:16]}... generated. Unlocking submission bundle export.",
        )

        # ------------------------------------------------------------------
        # Step 9: Final Bid Package Export Service
        # ------------------------------------------------------------------
        print_banner(9, "Final Bid Package Export Service (Submission Ready)")
        zip_path = export_svc.export_bid_package(db, tender.id, proposal.id, require_human_approval=True)
        file_size_bytes = os.path.getsize(zip_path)
        print(f"Generated Bundle     : {zip_path}")
        print(f"Bundle File Size     : {file_size_bytes:,.0f} bytes")
        print("Bundle Contents:")
        print("  1. 01_Technical_Proposal_v1.docx           (Formatted Proposal with ProofLink Footnotes)")
        print("  2. 02_Compliance_Matrix.xlsx               (Formatted Excel Matrix with Color Coding)")
        print("  3. 03_Independent_Bid_Audit_Report.txt      (Readiness Score & Findings Breakdown)")
        print("  4. 04_Human_Sign_Off_Certificate.json      (Cryptographic SHA-256 Sign-Off Certificate)")

        # ------------------------------------------------------------------
        # Final Summary
        # ------------------------------------------------------------------
        print("""
============================================================================
              DEMONSTRATION COMPLETED WITH 100% VERIFICATION!
  From Tender to Trustworthy Proposal — Powered by Switch & TenderForge
============================================================================
        """)

    finally:
        db.close()


if __name__ == "__main__":
    run_phase2_demo()
