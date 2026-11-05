"""
TenderForge Phase 3 Advanced Bid Intelligence & Enterprise Workspace Demonstration.

Exercises and demonstrates:
1. Bid/No-Bid Decision Intelligence (multi-dimensional, non-compensable gates, advisory recommendation).
2. Human Executive Decision & Override Tracking.
3. Advanced ProofLink Intelligence (freshness audit, cross-document contradiction detection & resolution, claim lineage).
4. Tender Evaluation Criteria extraction & Proposal Optimization (Before/After side-by-side).
5. Financial Proposal Workspace (Deterministic Decimal arithmetic, BOQ items, scenario generation, publication-grade Excel export).
6. Centralized Bid Risk & Mitigation Registry harvesting and scoring.
7. Proposal Revision & Pre-submission Quality Validation (placeholders, formatting hygiene, citation integrity).
8. Deadline and Notification Intelligence (milestone countdowns, Switch reminders).
9. Tender Portfolio Management & Measured Analytics.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, setup_logging
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.infrastructure.database.session import SessionLocal
from backend.app.services.advanced_prooflink_service import AdvancedProofLinkService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.bid_decision_service import BidDecisionService
from backend.app.services.deadline_service import DeadlineService
from backend.app.services.evaluation_criteria_service import EvaluationCriteriaService
from backend.app.services.financial_service import FinancialService
from backend.app.services.portfolio_service import PortfolioService
from backend.app.services.proposal_optimization_service import ProposalOptimizationService
from backend.app.services.proposal_revision_service import ProposalRevisionService
from backend.app.services.risk_service import RiskService

setup_logging("INFO")
logger = get_logger("demo_phase3")


def banner(step: int, title: str):
    print("\n" + "=" * 78)
    print(f"  Step {step}: {title}")
    print("=" * 78)


def run_phase3_demo():
    print("""
==============================================================================
         TENDERFORGE — PHASE 3 ADVANCED BID INTELLIGENCE & ENTERPRISE
         Flip the Switch Hackathon 2026 | Best Business Workflow
==============================================================================
Tagline: From Tender to Trustworthy Proposal
Core Focus: Bid/No-Bid Decision Intelligence, Advanced ProofLink, Financial BOQ,
            Evaluation Optimization, Risk Registry & Multi-Workspace Portfolio.
==============================================================================
""")

    db = SessionLocal()
    run_token = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    try:
        # --------------------------------------------------------------------
        # Step 1: Enterprise Workspace & Organizational Profile
        # --------------------------------------------------------------------
        banner(1, "Enterprise Workspace & Organization Baseline Initialization")
        org = Organization(
            name=f"Apex Global Defense & IT Solutions ({run_token})",
            slug=f"apex-global-{run_token}",
        )
        db.add(org)
        db.commit()

        profile = OrganizationProfile(
            organization_id=org.id,
            legal_name=f"Apex Global Defense & IT Solutions Inc.",
            trade_name="Apex Defense",
            registration_number=f"CORP-US-994821",
            tax_id=f"EIN-84-1928374",
            jurisdiction="United States",
            headquarters_address="8200 Defense Boulevard, Arlington, VA 22202",
            primary_contact_name="Elena Vance",
            primary_contact_email="elena.vance@apexdefense.com",
            financial_metrics={"turnover_fy23": 14200000, "turnover_fy24": 18500000},
            core_capabilities=["C4ISR", "Zero Trust Cloud", "AI Battle Management", "Secure Satellite Comms"],
            certifications=["ISO 9001:2015", "ISO 27001:2022", "CMMC Level 3"],
        )
        db.add(profile)

        ws = Workspace(
            name=f"Defense & Aerospace Bids ({run_token})",
            organization_id=org.id,
            description="Enterprise workspace for classified and federal defense opportunities.",
        )
        db.add(ws)
        db.commit()
        print(f"[OK] Workspace Created: '{ws.name}' (ID: {ws.id})")
        print(f"[OK] Organization Profile Established: {profile.legal_name}")

        # --------------------------------------------------------------------
        # Step 2: Tender Opportunity Registration & Requirements
        # --------------------------------------------------------------------
        banner(2, "Tender Ingestion & Mandatory Requirements Baseline")
        tender = Tender(
            workspace_id=ws.id,
            title="Joint Multi-Domain Command & Control (JADC2) Cloud Integration",
            reference_number=f"DOD-DISA-2026-RFP-{run_token[:8]}",
            issuing_authority="Defense Information Systems Agency (DISA)",
            procurement_category="Defense Information Technology",
            estimated_value=12500000.0,
            currency="USD",
            submission_deadline=(datetime.now(timezone.utc) + timedelta(days=21)).replace(tzinfo=None),
            status="opportunity",
        )
        db.add(tender)
        db.commit()

        r1 = TenderRequirement(
            tender_id=tender.id,
            category="eligibility",
            classification="mandatory",
            description="Vendor must hold active ISO 27001 or FedRAMP High certification.",
            source_excerpt="RFP Section C.1.1: Mandatory Information Security Certifications",
        )
        r2 = TenderRequirement(
            tender_id=tender.id,
            category="technical",
            classification="mandatory",
            description="Sub-50ms latency tactical data distribution across air, land, and sea nodes.",
            source_excerpt="RFP Section C.3.4: Tactical Distribution SLA Requirements",
        )
        r3 = TenderRequirement(
            tender_id=tender.id,
            category="financial",
            classification="mandatory",
            description="Minimum annual average audited turnover of $10,000,000 across last 2 fiscal years.",
            source_excerpt="RFP Section C.4.1: Financial Turnover Qualifications",
        )
        db.add_all([r1, r2, r3])
        db.commit()
        print(f"[OK] Tender Registered: '{tender.title}' (Est. Value: ${tender.estimated_value:,.2f})")
        print(f"[OK] Ingested 3 Mandatory Requirements (Eligibility, Technical SLA, Financial Turnover)")

        # --------------------------------------------------------------------
        # Step 3: Bid/No-Bid Decision Intelligence Execution
        # --------------------------------------------------------------------
        banner(3, "Bid/No-Bid Decision Intelligence Engine Execution")
        bid_svc = BidDecisionService(db)
        bid_eval = bid_svc.evaluate_tender(
            tender_id=tender.id,
            db=db,
            evaluator_id="BidDecisionEngine_v3",
        )

        print(f"-> Advisory Recommendation : {bid_eval.recommendation}")
        print(f"-> Overall Viability Score  : {bid_eval.overall_score}/100.0")
        print(f"-> Eligibility Gates Status : {'PASSED' if bid_eval.eligibility_gates_passed else 'FAILED'}")
        print("\nDimension Breakdown:")
        for dim, info in bid_eval.dimensions.items():
            print(f"   [{info['status']:<11}] {info['label']:<36} : {info['score']:>5.1f}/100 (Weight: {info['weight']})")

        # --------------------------------------------------------------------
        # Step 4: Human Executive Decision & Authority Sign-Off
        # --------------------------------------------------------------------
        banner(4, "Human Executive Authority Sign-Off Tracking")
        approved_eval = bid_svc.record_human_decision(
            evaluation_id=bid_eval.id,
            decision="APPROVED_BID",
            user_id="usr-exec-general-01",
            user_name="Maj. Gen. (Ret.) Marcus Vance",
            rationale="Approved pursuit: Opportunity aligns with our C4ISR growth roadmap and audited capabilities.",
            db=db,
        )
        print(f"[OK] Human Decision Recorded: {approved_eval.human_decision}")
        print(f"[OK] Sign-Off Authority     : {approved_eval.human_decision_by}")
        print(f"[OK] Executive Rationale    : \"{approved_eval.human_decision_rationale}\"")

        # --------------------------------------------------------------------
        # Step 5: Advanced ProofLink Intelligence & Contradiction Detection
        # --------------------------------------------------------------------
        banner(5, "Advanced ProofLink Intelligence & Contradiction Audit")
        proof_svc = AdvancedProofLinkService(db)

        # Register evidence with deliberate discrepancy to test cross-document contradiction
        ev_audit = CompanyEvidence(
            organization_id=org.id,
            title="Audited Financial Statement FY24",
            evidence_type="financial_audit",
            extracted_data={"turnover": "$18,500,000", "turnover_fy24": "$18,500,000"},
            issuer="PricewaterhouseCoopers LLP",
            expiry_date=(datetime.now(timezone.utc) + timedelta(days=365)).replace(tzinfo=None),
            status="valid",
        )
        ev_interim = CompanyEvidence(
            organization_id=org.id,
            title="Q4 Interim Financial Review FY24",
            evidence_type="annual_report",
            extracted_data={"turnover": "$16,200,000", "turnover_fy24": "$16,200,000"},
            issuer="Apex Internal Audit",
            status="valid",
        )
        ev_iso = CompanyEvidence(
            organization_id=org.id,
            title="ISO 27001:2022 Information Security Certificate",
            evidence_type="certification",
            reference_number="CERT-ISO27001-9988",
            issuer="BSI Assurance Services",
            expiry_date=(datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None),  # Expiring soon!
            status="valid",
        )
        db.add_all([ev_audit, ev_interim, ev_iso])
        db.commit()

        # 1. Freshness Audit
        freshness = proof_svc.audit_evidence_freshness(org.id, warning_window_days=60, db=db)
        print(f"-> Evidence Audited        : {freshness['total_evidence_audited']} records")
        print(f"-> Expiring Soon (<60 days): {freshness['expiring_soon_count']} item(s)")
        for exp_item in freshness["expiring_soon"]:
            print(f"   * WARNING: '{exp_item['title']}' expires in {exp_item.get('days_remaining')} days!")

        # 2. Contradiction Detection
        contradictions = proof_svc.detect_evidence_contradictions(org.id, db=db)
        print(f"\n-> Contradictions Detected : {len(contradictions)} conflict(s)")
        for c in contradictions:
            print(f"   * [{c.contradiction_severity}] Discrepancy on '{c.claim_field}': '{c.value_1}' vs '{c.value_2}'")

        if contradictions:
            resolved_contra = proof_svc.resolve_contradiction(
                contradiction_id=contradictions[0].id,
                resolution_notes="Q4 internal interim was unadjusted cash accounting; PwC audited balance sheet is the authoritative filing.",
                resolved_by="CFO Arthur Pendelton",
                db=db,
            )
            print(f"   * RESOLVED by {resolved_contra.resolved_by}: {resolved_contra.resolution_notes[:70]}...")

        # --------------------------------------------------------------------
        # Step 6: Claim Lineage & Cryptographic ProofLink Traceability
        # --------------------------------------------------------------------
        banner(6, "Cryptographic Claim Lineage (Requirement -> Evidence -> Claim)")
        prop = Proposal(
            tender_id=tender.id,
            title="Technical & Operational Response Proposal",
            status="drafting",
            current_version=1,
        )
        db.add(prop)
        db.commit()

        sec = ProposalSection(
            proposal_id=prop.id,
            section_number="2.1",
            title="Financial Strength & Turnover Qualifications",
            content="Apex Defense generated verified annual turnover exceeding $18.5M in FY24 [ProofLink: AUDIT-FY24-PWC].",
        )
        db.add(sec)
        db.commit()

        lineage = proof_svc.record_claim_lineage(
            tender_id=tender.id,
            proposal_id=prop.id,
            requirement_id=r3.id,
            evidence_id=ev_audit.id,
            section_number="2.1",
            claim_text="Apex Defense generated verified annual turnover exceeding $18.5M in FY24.",
            evidence_extract="PwC Audited Statement FY24: Net Revenue $18,500,000.",
            review_status="verified",
            auditor_verdict="Ready for Submission",
            approval_status="approved",
            db=db,
        )
        print(f"[OK] Cryptographic Claim Lineage Hash: {lineage.lineage_hash}")
        print(f"[OK] Traceability Node: Requirement '{r3.description[:35]}...' -> Evidence '{ev_audit.title}' -> Section 2.1")

        # --------------------------------------------------------------------
        # Step 7: Tender Evaluation Criteria & Proposal Optimization Engine
        # --------------------------------------------------------------------
        banner(7, "Tender Evaluation Criteria & Proposal Optimization Engine")
        crit_svc = EvaluationCriteriaService(db)
        criteria = crit_svc.extract_evaluation_criteria(tender.id, db=db)
        print(f"[OK] Extracted {len(criteria)} Tender Evaluation Criteria:")
        for cr in criteria:
            print(f"   - [{cr.criterion_code}] {cr.title:<42} Weight: {cr.weight_percentage}% (Max Marks: {cr.max_marks})")

        opt_svc = ProposalOptimizationService(db)
        optimizations = opt_svc.analyze_and_optimize(prop.id, db=db)
        print(f"\n[OK] Proposal Coverage Gaps Identified: {len(optimizations)} recommendations")
        for opt in optimizations[:2]:
            print(f"\n   * [Coverage: {opt.coverage_status}] Section {opt.section_number} (Criterion: {opt.criterion.title if opt.criterion else 'General'})")
            print(f"     Gap Analysis : {opt.gap_analysis}")
            print(f"     Score Impact : Est. {opt.current_score_estimate} -> {opt.potential_score_estimate} Marks")
            print(f"     Before Text  : {opt.before_text[:80]}...")
            print(f"     After Text   : {opt.after_text[:80]}...")

        # --------------------------------------------------------------------
        # Step 8: Financial Proposal Workspace & Deterministic Decimal Math
        # --------------------------------------------------------------------
        banner(8, "Financial Proposal Workspace (Strict Decimal Precision)")
        fin_svc = FinancialService(db)

        boq_items = [
            {"item_code": "TACT-01", "description": "Tactical Edge Server Units", "category": "Hardware", "unit": "unit", "quantity": "40.00", "unit_rate": "18500.00"},
            {"item_code": "SAT-02", "description": "High Throughput Satellite Terminals", "category": "Hardware", "unit": "terminal", "quantity": "12.00", "unit_rate": "45000.00"},
            {"item_code": "ENG-03", "description": "Principal Zero-Trust Integration Engineer", "category": "Labor", "unit": "hrs", "quantity": "1200.00", "unit_rate": "225.00"},
            {"item_code": "SW-04", "description": "Battlefield AI Distributed OS Licenses", "category": "Software", "unit": "license", "quantity": "40.00", "unit_rate": "8750.50"},
        ]

        fin_prop = fin_svc.create_financial_proposal(
            tender_id=tender.id,
            proposal_id=prop.id,
            title="JADC2 Tactical Cloud Commercial Schedule",
            currency="USD",
            tax_rate_percent="10.00",
            contingency_rate_percent="5.00",
            overhead_rate_percent="8.00",
            margin_rate_percent="15.00",
            initial_items=boq_items,
            db=db,
        )

        print(f"Deterministic Pricing Breakdown ({fin_prop.currency}):")
        print(f"   Subtotal (Raw BOQ)        : ${Decimal(fin_prop.subtotal):>14,.2f}")
        print(f"   Contingency ({fin_prop.contingency_rate_percent}%)        : ${Decimal(fin_prop.contingency_amount):>14,.2f}")
        print(f"   Overhead ({fin_prop.overhead_rate_percent}%)           : ${Decimal(fin_prop.overhead_amount):>14,.2f}")
        print(f"   Gross Margin ({fin_prop.margin_rate_percent}%)       : ${Decimal(fin_prop.margin_amount):>14,.2f}")
        print(f"   Statutory Taxes ({fin_prop.tax_rate_percent}%)    : ${Decimal(fin_prop.tax_amount):>14,.2f}")
        print("   " + "-" * 45)
        print(f"   GRAND TOTAL PROPOSAL PRICE: ${Decimal(fin_prop.total_price):>14,.2f}")

        # Multi-Scenario Pricing
        scenarios = fin_svc.generate_scenarios(fin_prop.id, db=db)
        print("\nMulti-Scenario Commercial Models:")
        for sc in scenarios:
            print(f"   * {sc.scenario_name:<16} -> Total: ${Decimal(sc.calculated_total):>12,.2f} (Margin: {sc.margin_rate_percent}%, Buffer: {sc.contingency_rate_percent}%)")

        # Export Excel
        excel_path = f"./storage/demo_phase3_financial_{tender.id[:8]}.xlsx"
        fin_svc.export_excel(fin_prop.id, output_path=excel_path, db=db)
        print(f"[OK] Exported Publication-Grade Excel BOQ: {excel_path} ({os.path.getsize(excel_path):,} bytes)")

        # --------------------------------------------------------------------
        # Step 9: Centralized Bid Risk Registry & Mitigation Intelligence
        # --------------------------------------------------------------------
        banner(9, "Centralized Bid Risk & Mitigation Registry")
        risk_svc = RiskService(db)
        r_entry = risk_svc.create_risk(
            tender_id=tender.id,
            title="Aggressive 21-Day Hardware Delivery Window",
            category="Timeline",
            likelihood=4,
            impact=4,
            description="Procuring tactical satellite terminals typically requires a 6-week lead time.",
            mitigation_strategy="Pre-allocate existing reserved warehouse inventory and issue expedited supplier PO.",
            owner="Logistics Lead Col. Danvers",
            db=db,
        )
        print(f"[OK] Registered High Exposure Risk: '{r_entry.title}'")
        print(f"     Severity Score : {r_entry.severity_score}/25 ({r_entry.risk_level} Risk)")
        print(f"     Mitigation     : {r_entry.mitigation_strategy}")

        # --------------------------------------------------------------------
        # Step 10: Proposal Quality Hygiene & Approval Invalidation
        # --------------------------------------------------------------------
        banner(10, "Proposal Document Hygiene & Revision Governance")
        rev_svc = ProposalRevisionService(db)

        # Invalidate when section content is updated
        prop.status = "approved"
        db.commit()

        updated_sec, invalidated = rev_svc.update_section_with_invalidation(
            proposal_id=prop.id,
            section_number="2.1",
            new_content="Apex Defense generated verified audited turnover exceeding $18.5M in FY24. [TODO: attach notary seal]",
            author_id="usr-elena-vance",
            change_summary="Appended notary requirement note",
            db=db,
        )
        print(f"[OK] Section 2.1 Edited -> Approval Status Automatically Invalidated: {invalidated}")
        print(f"[OK] Proposal Version Advanced to v{prop.current_version}")

        # Pre-submission quality check
        qc = rev_svc.validate_proposal_quality(prop.id, checked_by="QualityAssuranceBot", db=db)
        print(f"\nDocument Quality Audit Result:")
        print(f"   Formatting Score  : {qc.formatting_score}/100.0")
        print(f"   Submission Passed : {'YES' if qc.passed else 'NO - BLOCKERS IDENTIFIED'}")
        print(f"   Placeholders Found: {qc.placeholder_count} ({', '.join(qc.placeholders_found)})")
        print(f"   Word Count        : {qc.word_count} words (~{qc.page_count_estimate} pages)")

        # --------------------------------------------------------------------
        # Step 11: Milestone Deadlines & Proactive Switch Reminders
        # --------------------------------------------------------------------
        banner(11, "Tender Deadlines & Notification Intelligence")
        dl_svc = DeadlineService(db)
        dl_rfp = dl_svc.create_deadline(
            tender_id=tender.id,
            deadline_type="Technical Bid Submission",
            title="Final JADC2 RFP Submission Cutoff",
            deadline_date=datetime.now(timezone.utc) + timedelta(days=21),
            reminder_intervals_hours=[168, 72, 24, 2],
            db=db,
        )
        print(f"[OK] Monitored Deadline Registered: '{dl_rfp.title}' (Due: {dl_rfp.deadline_date})")

        # --------------------------------------------------------------------
        # Step 12: Enterprise Portfolio Dashboard & Operational Analytics
        # --------------------------------------------------------------------
        banner(12, "Enterprise Portfolio Dashboard & Measured Analytics")
        port_svc = PortfolioService(db)
        port_svc.update_tender_stage(tender.id, "Preparation", db=db)
        portfolio = port_svc.get_portfolio_overview(ws.id, db=db)

        print(f"Portfolio Status for Workspace '{ws.name}':")
        print(f"   Total Tenders Monitored: {portfolio['total_tenders']}")
        print(f"   Active Pipeline Value  : ${portfolio['active_pipeline_value']:,.2f}")
        print(f"   Stage Distribution     : {portfolio['stage_distribution']}")

        ana_svc = AnalyticsService(db)
        analytics = ana_svc.get_workspace_analytics(ws.id, db=db)
        print("\nOperational & Compliance Metrics:")
        print(f"   Compliance Pass Rate     : {analytics['compliance']['compliance_pass_rate_percent']}%")
        print(f"   ProofLink Density/Claims  : {analytics['prooflink']['total_claim_lineages']} verifiable lineages")
        print(f"   Human Decision Tracking   : {analytics['collaboration']['human_decisions_recorded']} executive decisions")

        print("""
==============================================================================
               PHASE 3 SYNTHETIC DEMONSTRATION COMPLETE
==============================================================================
All Phase 3 capabilities executed successfully:
  - Multi-Dimensional Bid/No-Bid Decision Intelligence with Hard Gates
  - Human Executive Authority Sign-Off Tracking
  - Advanced ProofLink Contradiction Detection & Freshness Audits
  - Tender Evaluation Criteria Extraction & Proposal Optimization
  - Financial BOQ Workspace with Deterministic Decimal Arithmetic & Excel Export
  - Centralized Bid Risk & Mitigation Registry
  - Automated Approval Invalidation & Pre-Submission Quality Check
  - Timezone-Aware Milestone Deadlines & Switch Reminders
  - Enterprise Multi-Workspace Portfolio Dashboard & Analytics
==============================================================================
""")

    finally:
        db.close()


if __name__ == "__main__":
    run_phase3_demo()
