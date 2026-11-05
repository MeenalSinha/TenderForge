"""
Unit tests for Portfolio Management and Tender Deadlines.
"""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    Organization,
    SwitchRoom,
    Tender,
    Workspace,
)
from backend.app.services.deadline_service import DeadlineService
from backend.app.services.portfolio_service import PortfolioService


@pytest.fixture
def portfolio_setup(db_session: Session):
    org = Organization(name="Portfolio Test Org", slug="pf-org")
    db_session.add(org)
    db_session.commit()

    ws = Workspace(name="Portfolio WS", organization_id=org.id)
    db_session.add(ws)
    db_session.commit()

    t1 = Tender(workspace_id=ws.id, title="Tender Alpha", estimated_value=500000.0, status="draft")
    t2 = Tender(workspace_id=ws.id, title="Tender Beta", estimated_value=750000.0, status="submitted")
    t3 = Tender(workspace_id=ws.id, title="Tender Gamma", estimated_value=250000.0, status="won")
    db_session.add_all([t1, t2, t3])
    db_session.commit()

    return ws, t1, t2, t3


def test_portfolio_overview_and_win_rate(db_session: Session, portfolio_setup):
    ws, t1, t2, t3 = portfolio_setup
    svc = PortfolioService(db_session)

    # Set stages
    svc.update_tender_stage(t1.id, "Preparation", db=db_session)
    svc.update_tender_stage(t2.id, "Submitted", db=db_session)
    svc.update_tender_stage(t3.id, "Won", db=db_session)

    overview = svc.get_portfolio_overview(ws.id, db=db_session)

    assert overview["total_tenders"] == 3
    # Active pipeline includes t1 and t2: 500k + 750k = 1.25M
    assert overview["active_pipeline_value"] == 1250000.0
    assert overview["win_rate_percent"] == 100.0  # 1 won out of 1 decided


def test_deadline_creation_and_reminders(db_session: Session, portfolio_setup):
    ws, t1, t2, t3 = portfolio_setup
    svc = DeadlineService(db_session)

    # Link Switch room
    room = SwitchRoom(
        tender_id=t1.id,
        room_name="War Room Alpha",
        channel_id="chan-alpha-001",
        channel_type="mattermost",
    )
    db_session.add(room)
    db_session.commit()

    # Create approaching deadline in 12 hours
    deadline_dt = datetime.now(timezone.utc) + timedelta(hours=12)
    dl = svc.create_deadline(
        tender_id=t1.id,
        deadline_type="Technical Bid Submission",
        title="Final RFP Technical Submission",
        deadline_date=deadline_dt,
        reminder_intervals_hours=[72, 24, 2],
        db=db_session,
    )

    assert dl.status == "Upcoming"
    assert t1.submission_deadline is not None

    # Check reminders
    notifications = svc.check_and_send_reminders(db=db_session)
    assert len(notifications) >= 1
    assert notifications[0]["deadline_id"] == dl.id
    assert notifications[0]["channel_id"] == "chan-alpha-001"
