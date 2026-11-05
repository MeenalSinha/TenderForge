"""
Integration tests for Phase 2 End-to-End Multi-Agent Workflow Orchestration.
"""

import os
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Organization,
    OrganizationProfile,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.approval_service import ApprovalDecision, ApprovalService
from backend.app.services.audit_service import AuditService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.export_service import ExportService
from backend.app.services.prooflink_service import ProofLinkService, ProofLinkStatus
from backend.app.services.proposal_service import ProposalService
from backend.app.services.workflow_orchestrator import WorkflowOrchestrator, WorkflowStage


def test_complete_phase2_multi_agent_workflow(db_session: Session):
    """End-to-end multi-agent orchestration test covering all Phase 2 capabilities."""
    evidence_svc = EvidenceService()
    prooflink_svc = ProofLinkService()
    compliance_svc = ComplianceService()
    proposal_svc = ProposalService()
    audit_svc = AuditService()
    approval_svc = ApprovalService()
    export_svc = ExportService()
    orchestrator = WorkflowOrchestrator()

    # Step 1: Organization & Profile Ingestion
    org = Organization(name="Stratum Technologies", slug="stratum-tech")
    db_session.add(org)
    db_session.commit()

    profile = evidence_svc.get_or_create_profile(
        db=db_session,
        organization_id=org.id,
        profile_data={
            "legal_name": "Stratum Technologies Inc.",
            "registration_number": "REG-STRATUM-2026",
            "tax_id": "TAX-US-9911",
            "financial_metrics": {"turnover_fy23": 4200000, "turnover_fy24": 4900000, "turnover_fy25": 5800000},
            "certifications": ["ISO 9001:2015", "ISO 27001"],
            "core_capabilities": ["Cloud Systems", "Enterprise Telecom", "Cybersecurity"],
        },
    )

    # Ingest company evidence records
    ev_turnover = evidence_svc.register_evidence(
        db=db_session,
        organization_id=org.id,
        title="Audited Financial Report FY 2024-2025",
        evidence_type="financial_audit",
        issuer="PricewaterhouseCoopers",
        reference_number="PWC-AUD-2025",
        status="valid",
        summary="Independent auditor report confirming 3-year average turnover of USD 4,966,666.",
        extracted_data={"average_turnover": 4966666},
    )

    ev_iso = evidence_svc.register_evidence(
        db=db_session,
        organization_id=org.id,
        title="ISO 9001:2015 Quality Management System",
        evidence_type="certification",
        issuer="DNV GL",
        reference_number="DNV-ISO-9001",
        status="valid",
        summary="Certified quality management standard valid through 2028.",
        tags=["iso 9001"],
    )

    ev_proj = evidence_svc.register_evidence(
        db=db_session,
        organization_id=org.id,
        title="National Enterprise Cloud Backbone",
        evidence_type="past_project",
        issuer="Ministry of Infrastructure",
        reference_number="PROJ-MIN-2024",
        status="valid",
        summary="Turnkey deployment of high-availability cloud backbone completed on time.",
    )

    # Step 2: Tender Registration & Requirements
    ws = Workspace(name="Federal_Tenders", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    tender = Tender(
        workspace_id=ws.id,
        title="National Secure Infrastructure RFP",
        reference_number="RFP-SEC-2026",
        issuing_authority="Federal Procurement Agency",
        estimated_value=3500000,
        currency="USD",
    )
    db_session.add(tender)
    db_session.commit()

    r1 = TenderRequirement(
        tender_id=tender.id,
        category="financial",
        classification="mandatory",
        description="Minimum annual turnover of USD 3,000,000 required.",
        source_excerpt="Clause 1.1: Minimum annual turnover of USD 3,000,000 required.",
    )
    r2 = TenderRequirement(
        tender_id=tender.id,
        category="eligibility",
        classification="mandatory",
        description="Bidder must have active ISO 9001 certification.",
        source_excerpt="Clause 1.2: Valid ISO 9001 certification is mandatory.",
    )
    r3 = TenderRequirement(
        tender_id=tender.id,
        category="technical",
        classification="mandatory",
        description="Demonstrated past project experience in enterprise cloud backbone delivery.",
        source_excerpt="Clause 2.1: Minimum 1 enterprise cloud deployment project.",
    )
    db_session.add_all([r1, r2, r3])
    db_session.commit()

    # Step 3: Workflow State Machine - Initialize
    wf = orchestrator.get_or_create_workflow(db_session, tender.id)
    assert wf.current_stage == WorkflowStage.WORKSPACE_INITIALIZED

    # Step 4: ProofLink Matching Engine
    links = prooflink_svc.match_all_tender_requirements(db_session, tender.id, org.id)
    assert len(links) >= 3
    for l in links:
        assert l.match_status == ProofLinkStatus.VERIFIED

    # Step 5: Compliance Assessment Engine
    matrix = compliance_svc.evaluate_tender_compliance(db_session, tender.id)
    assert matrix.overall_status == "Compliant"
    assert matrix.overall_risk_level == "Low"

    # Step 6: Evidence-Backed Proposal Generation
    proposal = proposal_svc.create_proposal_draft(db_session, tender.id)
    assert proposal.current_version == 1
    assert proposal.docx_file_path is not None
    assert os.path.exists(proposal.docx_file_path)

    # Step 7: Independent Bid Auditor
    audit = audit_svc.audit_proposal(db_session, proposal.id)
    assert audit.verdict == "Ready for Submission"
    assert audit.readiness_score >= 90.0

    # Step 8: Export Gate Blocked Before Human Sign-Off
    with pytest.raises(Exception, match="human sign-off"):
        export_svc.export_bid_package(db_session, tender.id, proposal.id, require_human_approval=True)

    # Step 9: Human Sign-Off & Governance
    approval = approval_svc.record_decision(
        db=db_session,
        tender_id=tender.id,
        proposal_id=proposal.id,
        user_id="lead_director_1",
        user_name="Marcus Vance",
        user_role="Senior Vice President & Bid Director",
        decision=ApprovalDecision.APPROVED,
        comments="Comprehensive technical and compliance audit verified. Ready for formal submission.",
    )
    assert approval.decision == "Approved"
    assert len(approval.signature_hash) == 64

    # Step 10: Final Bid Package Export Service (Unlocked)
    zip_bundle = export_svc.export_bid_package(db_session, tender.id, proposal.id, require_human_approval=True)
    assert os.path.exists(zip_bundle)
    assert zip_bundle.endswith(".zip")
