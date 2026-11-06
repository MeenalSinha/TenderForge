"""
End-to-End Integration Workflow Test for Phase 5:
Discovery -> 9-Dimension Match -> Workspace Promotion -> Continuous Monitoring ->
Amendment Impact Propagation -> Knowledge Reuse -> Bid Submission Receipt -> Closed-Loop Learning.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    HumanApproval,
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
    Workspace,
)
from backend.app.services.amendment_service import AmendmentService
from backend.app.services.bid_outcome_service import BidOutcomeService
from backend.app.services.knowledge_library_service import KnowledgeLibraryService
from backend.app.services.opportunity_matching_service import OpportunityMatchingService
from backend.app.services.opportunity_service import OpportunityService
from backend.app.services.tender_monitoring_service import TenderMonitoringService
from tests.helpers import run_sync


def test_complete_phase5_e2e_procurement_workflow(db_session: Session):
    # 1. Organization Setup
    org = Organization(name="AeroDefense Systems", slug="aerodefense-systems")
    db_session.add(org)
    db_session.flush()

    profile = OrganizationProfile(
        organization_id=org.id,
        legal_name=org.name,
        registration_number="REG-AERO-01",
        tax_id="TAX-AERO-01",
        financial_metrics={"annual_turnover": 35000000.0, "turnover": 35000000.0},
        core_capabilities=["cloud", "cybersecurity", "kubernetes", "defense"],
        certifications=["ISO 27001", "SOC2 Type II", "minimum_turnover_10m", "past_experience_3_contracts"],
    )
    db_session.add(profile)

    ev1 = CompanyEvidence(
        organization_id=org.id,
        title="ISO 27001 Information Security Management Certificate",
        evidence_type="certification",
        tags=["iso_27001", "compliance", "security"],
        summary="ISO 27001 certified until 2028.",
    )
    ev2 = CompanyEvidence(
        organization_id=org.id,
        title="Federal Hybrid Cloud Migration Case Study",
        evidence_type="past_performance",
        tags=["cloud", "kubernetes", "past_experience_3_contracts"],
        summary="Delivered 3 successful multi-cloud migrations for federal agencies.",
    )
    db_session.add_all([ev1, ev2])
    db_session.commit()

    # 2. Opportunity Ingestion & Discovery
    opp_service = OpportunityService()
    source = opp_service.get_or_create_source(
        db=db_session,
        organization_id=org.id,
        name="Enterprise Discovery Source",
        connector_type="mock_sandbox",
    )
    run, opportunities = run_sync(opp_service.sync_source(db_session, source.id, limit=3))
    assert run.status == "completed"
    assert len(opportunities) >= 1
    target_opp = opportunities[0]

    # 3. 9-Dimension AI Opportunity Matching & Explainability
    match_service = OpportunityMatchingService()
    match = match_service.evaluate_opportunity(db_session, target_opp.id, org.id)
    assert match.overall_match_score > 50.0
    assert match.mandatory_gates_passed is True
    assert len(match.dimension_scores) == 9
    assert len(match.explainability_breakdown["strengths"]) > 0

    # 4. Promote Opportunity to Active Tender Workspace
    tender = opp_service.promote_opportunity_to_tender(
        db=db_session,
        opportunity_id=target_opp.id,
        custom_title="Pursuit: Cloud Infrastructure Modernization",
    )
    assert tender.id is not None
    assert tender.title == "Pursuit: Cloud Infrastructure Modernization"

    # 5. Continuous Monitoring & Snapshot Baseline
    mon_service = TenderMonitoringService()
    sub = mon_service.create_subscription(db_session, tender.id, org.id, source.id)
    assert sub.is_active is True

    snap1, amd1 = mon_service.capture_snapshot(
        db=db_session,
        subscription_id=sub.id,
        content_text="RFP Baseline Specifications v1.0",
        metadata={"submission_deadline": "2026-12-15", "estimated_value": 4850000.0},
    )
    assert snap1.snapshot_version == 1
    assert amd1 is None

    # Simulate executive preliminary sign-off
    approval = HumanApproval(
        tender_id=tender.id,
        decision="Approved",
        user_id="usr-exec",
        user_name="VP Pursuit",
        user_role="Approver",
        comments="Initial bid pursuit approved.",
        signature_hash="sha-sign-initial",
    )
    db_session.add(approval)
    db_session.commit()

    # 6. Corrigendum Arrival: Snapshot 2 with Deadline & Scope Revision -> Triggers Critical Amendment
    snap2, amd2 = mon_service.capture_snapshot(
        db=db_session,
        subscription_id=sub.id,
        content_text="RFP Corrigendum Notice: Tightened delivery schedules and penalty terms.",
        metadata={"submission_deadline": "2026-11-28", "estimated_value": 4850000.0},
        amendment_notice_title="Corrigendum 01 - Submission Deadline Advanced",
    )
    assert snap2.snapshot_version == 2
    assert amd2 is not None
    assert amd2.materiality == "critical"
    assert amd2.approval_invalidated is True

    # Verify downstream impact: Executive approval was invalidated
    db_session.refresh(approval)
    assert approval.decision == "Changes Requested"
    assert "Approval invalidated due to Critical Corrigendum" in approval.comments

    # 7. Human Acknowledgement
    amd_service = AmendmentService()
    acked = amd_service.acknowledge_amendment(
        db=db_session,
        amendment_id=amd2.id,
        user_id="usr-lead-architect",
        notes="Reviewed schedule revision. Team mobilization schedule updated.",
    )
    assert acked.acknowledged_at is not None

    # 8. Knowledge Library: Reuse Approved Narrative Asset into Proposal Section
    knowledge_service = KnowledgeLibraryService()
    asset = knowledge_service.create_asset(
        db=db_session,
        organization_id=org.id,
        title="Enterprise Sovereign Cloud Security Framework",
        content="Our solution implements Zero Trust architecture with continuous identity verification.",
        category="technical_approach",
        auto_approve=True,
    )
    assert asset.times_reused == 0

    proposal = Proposal(tender_id=tender.id, title="Proposal Draft v1", status="draft")
    db_session.add(proposal)
    db_session.flush()

    section = ProposalSection(
        proposal_id=proposal.id,
        section_number="3.1",
        title="Security Architecture",
        content="Section outline.",
    )
    db_session.add(section)
    db_session.commit()

    use_res = knowledge_service.use_asset(db_session, asset.id, proposal_section_id=section.id)
    assert use_res["times_reused"] == 1
    assert use_res["section_updated"] is True

    # 9. Formal Bid Submission & Cryptographic Receipt Generation
    outcome_service = BidOutcomeService()
    sub_record = outcome_service.record_bid_submission(
        db=db_session,
        tender_id=tender.id,
        organization_id=org.id,
        final_bid_amount=4720000.0,
        currency="USD",
        submitted_by_user_id="usr-exec",
        notes="Final competitive bid submitted after addressing Corrigendum 01.",
    )
    assert sub_record.submission_receipt_hash is not None
    assert len(sub_record.submission_receipt_hash) == 64
    assert sub_record.lifecycle_stage == "submitted_to_buyer"

    # 10. Record Outcome & Closed-Loop Learning
    outcome_record = outcome_service.record_bid_outcome(
        db=db_session,
        submission_id=sub_record.id,
        outcome="won",
        winning_bidder="AeroDefense Systems",
        winning_amount=4720000.0,
        win_factors=["highest_technical_score", "robust_knowledge_asset_reuse"],
        debrief_notes="Client debrief confirmed superiority of our sovereign cloud security architecture.",
    )
    assert outcome_record.outcome == "won"
    assert sub_record.lifecycle_stage == "awarded_won"

    # Query closed-loop analytics
    analytics = outcome_service.get_closed_loop_learning(db_session, org.id)
    assert analytics["total_recorded_outcomes"] >= 1
    assert analytics["counts"]["won"] >= 1
