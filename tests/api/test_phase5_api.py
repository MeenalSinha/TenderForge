"""
API route tests for Phase 5 REST endpoints.
Tests sources, opportunities, matching, monitoring, amendments, market, bid outcomes, and knowledge library.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.api.routes.procurement_sources import (
    CreateSourceRequest,
    create_source,
    list_sources,
    sync_source,
)
from backend.app.api.routes.opportunities import (
    PromoteOpportunityRequest,
    evaluate_opportunity_match,
    list_opportunities,
    list_recommendations,
    promote_opportunity,
)
from backend.app.api.routes.monitoring import (
    AcknowledgeAmendmentRequest,
    CaptureSnapshotRequest,
    SubscribeMonitoringRequest,
    acknowledge_amendment,
    capture_snapshot,
    list_amendments,
    list_snapshots,
    subscribe_tender_monitoring,
)
from backend.app.api.routes.market import (
    CompetitorProfileRequest,
    RecordAwardRequest,
    get_market_trends,
    list_awards,
    list_competitors,
    record_award,
    upsert_competitor,
)
from backend.app.api.routes.bid_outcomes import (
    RecordOutcomeRequest,
    RecordSubmissionRequest,
    get_bid_learning_analytics,
    list_submissions,
    record_outcome,
    submit_bid,
)
from backend.app.api.routes.knowledge import (
    CreateAssetRequest,
    ReuseAssetRequest,
    UpdateAssetRequest,
    approve_asset,
    create_asset,
    get_asset,
    list_assets,
    reuse_asset,
    update_asset,
)
from backend.app.core.security_auth import decode_access_token, create_test_token
from backend.app.infrastructure.database.models import Organization, Tender, Workspace
from tests.helpers import run_sync


@pytest.fixture
def phase5_setup(db_session: Session):
    org = Organization(name="Phase 5 Org", slug="phase5-org")
    db_session.add(org)
    db_session.flush()

    ws = Workspace(name="P5 Workspace", organization_id=org.id)
    db_session.add(ws)
    db_session.flush()

    tender = Tender(
        workspace_id=ws.id,
        title="P5 Enterprise Architecture Support",
        reference_number="P5-ARCH-01",
        estimated_value=3000000.0,
        currency="USD",
    )
    db_session.add(tender)
    db_session.commit()

    token = create_test_token(role="Admin", user_id="usr-p5-admin", org_id=org.id)
    claims = decode_access_token(token)

    return {"org": org, "ws": ws, "tender": tender, "claims": claims}


def test_sources_api_lifecycle(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    org = phase5_setup["org"]

    # 1. Create source
    create_req = CreateSourceRequest(
        name="Test Sandbox Source",
        connector_type="mock_sandbox",
        organization_id=org.id,
    )
    res = create_source(payload=create_req, db=db_session, claims=claims, _role="Admin")
    assert res["status"] == "success"
    source_id = res["source"]["id"]

    # 2. List sources
    list_res = list_sources(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert list_res["count"] >= 1


def test_sources_sync_and_opportunities_api(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    org = phase5_setup["org"]

    # Register source
    create_req = CreateSourceRequest(
        name="Auto Sync Sandbox",
        connector_type="mock_sandbox",
        organization_id=org.id,
    )
    src_res = create_source(payload=create_req, db=db_session, claims=claims, _role="Admin")
    source_id = src_res["source"]["id"]

    # Sync source
    sync_res = run_sync(sync_source(source_id=source_id, limit=5, db=db_session, _role="Admin"))
    assert sync_res["status"] == "success"
    assert sync_res["items_discovered"] >= 1

    # List opportunities
    opps_res = list_opportunities(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert opps_res["total"] >= 1
    opp = opps_res["opportunities"][0]

    # Evaluate opportunity match
    match_res = evaluate_opportunity_match(
        opportunity_id=opp["id"],
        organization_id=org.id,
        db=db_session,
        claims=claims,
        _role="Admin",
    )
    assert match_res["status"] == "success"
    assert "overall_match_score" in match_res["match"]

    # List recommendations
    rec_res = list_recommendations(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert rec_res["count"] >= 1

    # Promote opportunity to tender
    promote_req = PromoteOpportunityRequest(custom_title="Promoted Tender Response")
    prom_res = promote_opportunity(
        opportunity_id=opp["id"],
        payload=promote_req,
        db=db_session,
        _role="Admin",
    )
    assert prom_res["status"] == "success"
    assert prom_res["tender"]["title"] == "Promoted Tender Response"


def test_monitoring_and_amendments_api(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    tender = phase5_setup["tender"]

    # 1. Subscribe monitoring
    sub_req = SubscribeMonitoringRequest(check_frequency_minutes=30)
    sub_res = subscribe_tender_monitoring(tender.id, sub_req, db_session, claims, _role="Admin")
    assert sub_res["status"] == "success"

    # 2. Capture baseline snapshot
    snap1_req = CaptureSnapshotRequest(
        content_text="Initial RFP specification baseline v1.0",
        metadata={"submission_deadline": "2026-12-01"},
    )
    snap1_res = capture_snapshot(tender.id, snap1_req, db_session, claims, _role="Admin")
    assert snap1_res["status"] == "success"
    assert snap1_res["snapshot"]["version"] == 1
    assert snap1_res["detected_amendment"] is None

    # 3. Capture second snapshot with deadline change -> triggers amendment
    snap2_req = CaptureSnapshotRequest(
        content_text="RFP revision with tightened timeline specifications.",
        metadata={"submission_deadline": "2026-11-20"},
        amendment_notice_title="Corrigendum 1 - Schedule Revision",
    )
    snap2_res = capture_snapshot(tender.id, snap2_req, db_session, claims, _role="Admin")
    assert snap2_res["snapshot"]["version"] == 2
    assert snap2_res["detected_amendment"] is not None
    assert snap2_res["detected_amendment"]["materiality"] == "critical"
    amd_id = snap2_res["detected_amendment"]["id"]

    # 4. List amendments
    amd_list = list_amendments(tender.id, db_session, _role="Admin")
    assert amd_list["count"] == 1

    # 5. Acknowledge amendment
    ack_req = AcknowledgeAmendmentRequest(notes="Schedule verified and approved.")
    ack_res = acknowledge_amendment(amd_id, ack_req, db_session, claims, _role="Admin")
    assert ack_res["status"] == "success"


def test_market_and_competitor_api(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    org = phase5_setup["org"]

    # 1. Ingest verified public award
    award_req = RecordAwardRequest(
        tender_reference="PUB-2026-880",
        buyer_name="Metro Transit Commission",
        winning_bidder="Apex Technologies",
        award_amount=4500000.0,
        currency="USD",
        procurement_category="infrastructure",
    )
    award_res = record_award(award_req, org.id, db_session, claims, _role="Admin")
    assert award_res["status"] == "success"

    # 2. List awards
    awards = list_awards(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert awards["total"] >= 1

    # 3. Market trends summary
    trends = get_market_trends(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert trends["total_awards_observed"] >= 1
    assert trends["total_spend_observed"] >= 4500000.0

    # 4. Upsert competitor profile
    comp_req = CompetitorProfileRequest(
        competitor_name="Vanguard Logistics",
        domain="vanguard.example.com",
        observed_tenders_count=3,
        estimated_win_rate=60.0,
        key_strengths=["Incumbent advantage"],
        pricing_strategy_notes="Aggressive discounting on initial year.",
    )
    comp_res = upsert_competitor(comp_req, org.id, db_session, claims, _role="Admin")
    assert comp_res["status"] == "success"

    # 5. List competitors
    comp_list = list_competitors(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert comp_list["count"] >= 1


def test_bid_submissions_outcomes_and_learning_api(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    org = phase5_setup["org"]
    tender = phase5_setup["tender"]

    # 1. Submit bid & generate receipt
    sub_req = RecordSubmissionRequest(
        final_bid_amount=2850000.0,
        currency="USD",
        notes="Executive approved final bid submission.",
    )
    sub_res = submit_bid(tender.id, sub_req, db_session, claims, _role="Admin")
    assert sub_res["status"] == "success"
    assert "submission_receipt_hash" in sub_res["submission"]
    sub_id = sub_res["submission"]["id"]

    # 2. List submissions
    subs_list = list_submissions(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert subs_list["count"] >= 1

    # 3. Record outcome
    out_req = RecordOutcomeRequest(
        outcome="won",
        winning_bidder="Our Company",
        winning_amount=2850000.0,
        win_factors=["highest_technical_score", "clear_compliance_matrix"],
    )
    out_res = record_outcome(sub_id, out_req, db_session, _role="Admin")
    assert out_res["status"] == "success"
    assert out_res["outcome"]["outcome"] == "won"

    # 4. Closed loop learning analytics
    learning = get_bid_learning_analytics(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert "total_recorded_outcomes" in learning
    assert "meets_statistical_threshold" in learning


def test_knowledge_library_api(db_session: Session, phase5_setup):
    claims = phase5_setup["claims"]
    org = phase5_setup["org"]

    # 1. Create asset
    asset_req = CreateAssetRequest(
        title="Corporate Quality Assurance Manual",
        content="Our QA procedures comply with ISO 9001 guidelines.",
        category="quality_assurance",
        keywords=["iso_9001", "quality"],
        auto_approve=False,
    )
    create_res = create_asset(asset_req, org.id, db_session, claims, _role="Admin")
    assert create_res["status"] == "success"
    asset_id = create_res["asset"]["id"]
    assert create_res["asset"]["review_status"] == "draft"

    # 2. Update asset (creates version 2)
    upd_req = UpdateAssetRequest(
        content="Our QA procedures comply with ISO 9001:2015 and CMMI Level 3 standards.",
        change_summary="Upgraded to ISO 9001:2015 and CMMI 3.",
    )
    upd_res = update_asset(asset_id, upd_req, db_session, claims, _role="Admin")
    assert upd_res["status"] == "success"

    # 3. Approve asset
    app_res = approve_asset(asset_id, db_session, claims, _role="Admin")
    assert app_res["status"] == "success"
    assert app_res["review_status"] == "approved"

    # 4. Reuse asset
    reuse_res = reuse_asset(asset_id, ReuseAssetRequest(), db_session, _role="Admin")
    assert reuse_res["status"] == "success"
    assert reuse_res["result"]["times_reused"] == 1

    # 5. List assets
    list_res = list_assets(organization_id=org.id, db=db_session, claims=claims, _role="Admin")
    assert list_res["total"] >= 1
