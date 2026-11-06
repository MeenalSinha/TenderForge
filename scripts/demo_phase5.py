#!/usr/bin/env python3
"""
TenderForge Phase 5: Proactive Procurement Intelligence, Tender Discovery & Closed-Loop Learning
End-to-End Live Demonstration Script.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.session import SessionLocal
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    HumanApproval,
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
)
from backend.app.services.amendment_service import AmendmentService
from backend.app.services.bid_outcome_service import BidOutcomeService
from backend.app.services.knowledge_library_service import KnowledgeLibraryService
from backend.app.services.opportunity_matching_service import OpportunityMatchingService
from backend.app.services.opportunity_service import OpportunityService
from backend.app.services.tender_monitoring_service import TenderMonitoringService


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def print_step(step_num: int, title: str):
    print(f"\n[STEP {step_num}] {title}")
    print("-" * 60)


def main():
    print_header("TenderForge Phase 5: End-to-End Procurement Intelligence Live Demo")
    db: Session = SessionLocal()

    try:
        # STEP 1: Organization & Evidence Setup
        print_step(1, "Setting Up Enterprise Organization Profile & Evidence Vault")
        org = db.query(Organization).filter(Organization.slug == "apex-defense-demo").first()
        if not org:
            org = Organization(name="Apex Defense & Cloud Technologies", slug="apex-defense-demo")
            db.add(org)
            db.flush()

        profile = db.query(OrganizationProfile).filter(OrganizationProfile.organization_id == org.id).first()
        if not profile:
            profile = OrganizationProfile(
                organization_id=org.id,
                legal_name=org.name,
                registration_number="US-DEF-88291",
                tax_id="EIN-99-88221",
                financial_metrics={"annual_turnover": 45000000.0, "turnover": 45000000.0},
                core_capabilities=["cloud", "cybersecurity", "kubernetes", "defense", "devops"],
                certifications=["ISO 27001", "SOC2 Type II", "FedRAMP High Ready"],
            )
            db.add(profile)
            ev1 = CompanyEvidence(
                organization_id=org.id,
                title="ISO 27001 Information Security Management Certificate",
                evidence_type="certification",
                tags=["iso_27001", "compliance", "security"],
                summary="ISO 27001 certified until 2028 across all datacenter zones.",
            )
            ev2 = CompanyEvidence(
                organization_id=org.id,
                title="Department of Energy Cloud Migration Case Study",
                evidence_type="past_performance",
                tags=["cloud", "kubernetes", "past_experience_3_contracts"],
                summary="Successfully completed 3 large-scale cloud modernization contracts.",
            )
            db.add_all([ev1, ev2])
            db.commit()

        print(f"  Organization: {org.name} (ID: {org.id})")
        print(f"  Turnover: ${profile.financial_metrics.get('annual_turnover', 0):,.2f}")
        print(f"  Core Capabilities: {', '.join(profile.core_capabilities or [])}")

        # STEP 2: Procurement Connector Ingestion
        print_step(2, "Ingesting Notices via Mock Sandbox Procurement Connector")
        opp_service = OpportunityService()
        source = opp_service.get_or_create_source(
            db=db,
            organization_id=org.id,
            name="Federal Procurement Gateway",
            connector_type="mock_sandbox",
        )
        print(f"  Registered Source: {source.name} [Type: {source.connector_type}]")

        # Run synchronous coroutine step
        gen = opp_service.sync_source(db, source.id, limit=3)
        try:
            gen.send(None)
        except StopIteration as e:
            run, opportunities = e.value

        print(f"  Ingestion Run ID: {run.id} | Status: {run.status}")
        print(f"  Opportunities Ingested: {len(opportunities)}")
        for opp in opportunities:
            print(f"    * [{opp.external_id}] {opp.title[:65]}... (Budget: ${opp.estimated_budget:,.2f})")

        target_opp = opportunities[0]

        # STEP 3: 9-Dimension AI Opportunity Matching
        print_step(3, "Evaluating 9-Dimension Match & Non-Compensable Hard Gates")
        match_service = OpportunityMatchingService()
        match = match_service.evaluate_opportunity(db, target_opp.id, org.id)

        print(f"  Target: {target_opp.title}")
        print(f"  Overall Match Score: {match.overall_match_score:.1f}%")
        print(f"  Recommendation Tier: {match.recommendation_tier}")
        print(f"  Mandatory Gates Passed: {match.mandatory_gates_passed}")
        print("  Dimension Scores:")
        for dim, score in match.dimension_scores.items():
            print(f"    - {dim.replace('_', ' ').title():<28}: {score:.1f}/100")

        print("  Top Strengths:")
        for s in match.explainability_breakdown.get("strengths", [])[:3]:
            print(f"    + {s}")

        # STEP 4: Promote Opportunity to Tender Workspace
        print_step(4, "Promoting High-Match Opportunity to Active Tender Workspace")
        tender = opp_service.promote_opportunity_to_tender(
            db=db,
            opportunity_id=target_opp.id,
            custom_title="Pursuit: Sovereign Cloud Infrastructure Modernization",
        )
        print(f"  Active Tender Workspace Created: '{tender.title}' (ID: {tender.id})")

        # STEP 5: Continuous Monitoring & Baseline Snapshot
        print_step(5, "Establishing Continuous Monitoring Subscription & Snapshot Baseline")
        mon_service = TenderMonitoringService()
        sub = mon_service.create_subscription(db, tender.id, org.id, source.id)
        snap1, _ = mon_service.capture_snapshot(
            db=db,
            subscription_id=sub.id,
            content_text="RFP Baseline Specification Document v1.0",
            metadata={"submission_deadline": "2026-12-15", "estimated_value": target_opp.estimated_budget},
        )
        print(f"  Monitoring Active: Polling every {sub.check_frequency_minutes} minutes")
        print(f"  Snapshot 1 Captured | Hash: {snap1.content_hash[:32]}... | Version: {snap1.snapshot_version}")

        # Preliminary approval
        approval = HumanApproval(
            tender_id=tender.id,
            decision="Approved",
            user_id="usr-vp-sales",
            user_name="Sarah Jenkins",
            user_role="Approver",
            comments="Preliminary pursuit approved based on high technical match score.",
            signature_hash="sha256-sign-baseline-001",
        )
        db.add(approval)
        db.commit()
        print(f"  Preliminary Executive Sign-off: {approval.user_name} [{approval.decision}]")

        # STEP 6: Corrigendum Detection & Approval Invalidation
        print_step(6, "Detecting Corrigendum Notice & Propagating Downstream Impact")
        snap2, amd = mon_service.capture_snapshot(
            db=db,
            subscription_id=sub.id,
            content_text="Corrigendum 01: Submission Deadline Advanced due to fiscal calendar requirements.",
            metadata={"submission_deadline": "2026-11-20", "estimated_value": target_opp.estimated_budget},
            amendment_notice_title="Corrigendum 01 - Submission Deadline Advanced",
        )
        print(f"  Snapshot 2 Captured | Version: {snap2.snapshot_version}")
        print(f"  Amendment Recorded: {amd.title}")
        print(f"  Materiality Level: {amd.materiality.upper()}")
        print(f"  Executive Approval Invalidated: {amd.approval_invalidated}")

        db.refresh(approval)
        print(f"  Updated Approval Status: {approval.decision}")
        print(f"  Audit Comment: {approval.comments}")

        # STEP 7: Human Acknowledgment
        print_step(7, "Human Certification & Amendment Acknowledgement")
        amd_service = AmendmentService()
        acked = amd_service.acknowledge_amendment(
            db=db,
            amendment_id=amd.id,
            user_id="usr-lead-architect",
            notes="Reviewed accelerated deadline. Sprint schedule mobilized.",
        )
        print(f"  Acknowledged By: {acked.acknowledged_by_user_id} at {acked.acknowledged_at}")

        # STEP 8: Knowledge Library Narrative Reuse
        print_step(8, "Reusing Verified Narrative from Knowledge Library")
        knowledge_service = KnowledgeLibraryService()
        asset = knowledge_service.create_asset(
            db=db,
            organization_id=org.id,
            title="Enterprise Zero Trust Security Posture",
            content="Our architecture enforces micro-segmentation, mTLS 1.3, and continuous identity assertion.",
            category="technical_approach",
            auto_approve=True,
        )
        print(f"  Knowledge Asset: '{asset.title}' [Status: {asset.review_status}]")

        proposal = Proposal(tender_id=tender.id, title="Technical Volume I", status="draft")
        db.add(proposal)
        db.flush()
        section = ProposalSection(
            proposal_id=proposal.id,
            section_number="2.3",
            title="Security Architecture",
            content="To be drafted.",
        )
        db.add(section)
        db.commit()

        use_res = knowledge_service.use_asset(db, asset.id, proposal_section_id=section.id)
        print(f"  Asset Injected into Section {section.section_number}: {section.title}")
        print(f"  Asset Reuse Count Incremented to: {use_res['times_reused']}")

        # STEP 9: Bid Submission & Cryptographic Receipt
        print_step(9, "Submitting Bid Proposal & Generating SHA-256 Cryptographic Receipt")
        outcome_service = BidOutcomeService()
        submission = outcome_service.record_bid_submission(
            db=db,
            tender_id=tender.id,
            organization_id=org.id,
            final_bid_amount=4725000.0,
            currency="USD",
            submitted_by_user_id="usr-vp-sales",
            notes="Formal submission incorporating Corrigendum 01.",
        )
        print(f"  Submission ID: {submission.id}")
        print(f"  Final Bid Amount: ${submission.final_bid_amount:,.2f} {submission.currency}")
        print(f"  SHA-256 Receipt Hash: {submission.submission_receipt_hash}")
        print(f"  Lifecycle Stage: {submission.lifecycle_stage}")

        # STEP 10: Closed-Loop Bid Learning & Win Outcome
        print_step(10, "Capturing Contract Win Outcome & Updating Closed-Loop Analytics")
        outcome = outcome_service.record_bid_outcome(
            db=db,
            submission_id=submission.id,
            outcome="won",
            winning_bidder=org.name,
            winning_amount=4725000.0,
            win_factors=["highest_technical_score", "robust_knowledge_asset_reuse"],
            debrief_notes="Client noted outstanding Zero Trust architecture narrative and flawless compliance.",
        )
        print(f"  Outcome: {outcome.outcome.upper()}")
        print(f"  Winning Bidder: {outcome.winning_bidder}")
        print(f"  Key Win Factors: {', '.join(outcome.win_factors or [])}")

        analytics = outcome_service.get_closed_loop_learning(db, org.id)
        print("\n  Closed-Loop Analytics Summary:")
        print(f"    - Total Recorded Outcomes: {analytics['total_recorded_outcomes']}")
        print(f"    - Win Rate: {analytics['win_rate_percentage']:.1f}%")
        print(f"    - Won: {analytics['counts']['won']} | Lost: {analytics['counts']['lost']}")

        print_header("Phase 5 Live Demonstration Successfully Completed")

    finally:
        db.close()


if __name__ == "__main__":
    main()
