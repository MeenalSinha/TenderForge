"""
Deadline & Notification Intelligence Service for TenderForge.

Monitors critical tender milestones:
- Pre-bid Meeting
- Query / Clarification Submission Deadline
- Addendum / Corrigendum Cutoff
- Technical Bid Submission Deadline
- Commercial Bid Submission Deadline
- Bid Validity Period

Dispatches proactive Switch notifications and alerts as milestones approach.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.infrastructure.database.models import (
    SwitchRoom,
    Tender,
    TenderDeadline,
    utcnow,
)
from backend.app.integrations.switch.agent_bridge import get_switch_bridge

logger = logging.getLogger(__name__)


class DeadlineService:
    """Tracks milestone dates, timezones, reminder intervals, and triggers Switch room notifications."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.config = settings.deadlines_config

    def create_deadline(
        self,
        tender_id: str,
        deadline_type: str,
        title: str,
        deadline_date: datetime,
        timezone_name: str = "UTC",
        is_mandatory: bool = True,
        reminder_intervals_hours: Optional[List[int]] = None,
        notes: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> TenderDeadline:
        """Register a milestone deadline with associated reminder schedules."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tender = session.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        default_intervals = self.config.get("default_reminder_hours", [168, 72, 24, 2])
        intervals = reminder_intervals_hours if reminder_intervals_hours is not None else default_intervals

        # If deadline_date is timezone-naive, make it UTC
        if deadline_date.tzinfo is None:
            deadline_date_utc = deadline_date.replace(tzinfo=timezone.utc)
        else:
            deadline_date_utc = deadline_date.astimezone(timezone.utc)

        deadline = TenderDeadline(
            tender_id=tender_id,
            deadline_type=deadline_type,
            title=title,
            deadline_date=deadline_date_utc.replace(tzinfo=None),  # SQLite stores naive UTC
            timezone_name=timezone_name,
            is_mandatory=is_mandatory,
            reminder_intervals_hours=intervals,
            notes=notes,
            status="Upcoming",
        )
        session.add(deadline)
        session.commit()
        session.refresh(deadline)

        # Also update tender submission_deadline if this is the primary submission deadline
        if "submission" in deadline_type.lower():
            tender.submission_deadline = deadline_date_utc.replace(tzinfo=None)
            session.commit()

        return deadline

    def check_and_send_reminders(
        self,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """Scan upcoming deadlines and dispatch notifications for triggered reminder intervals."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        now_utc = datetime.now(timezone.utc)
        deadlines = session.query(TenderDeadline).filter(TenderDeadline.status.in_(["Upcoming", "Approaching"])).all()

        notifications_sent: List[Dict[str, Any]] = []
        bridge = get_switch_bridge()

        for dl in deadlines:
            dl_date = dl.deadline_date
            if dl_date.tzinfo is None:
                dl_date = dl_date.replace(tzinfo=timezone.utc)

            time_remaining = dl_date - now_utc
            hours_remaining = time_remaining.total_seconds() / 3600.0

            if hours_remaining <= 0:
                dl.status = "Missed"
                dl.updated_at = utcnow()
                continue

            if hours_remaining <= 48 and dl.status != "Approaching":
                dl.status = "Approaching"
                dl.updated_at = utcnow()

            # Check reminder intervals
            intervals = dl.reminder_intervals_hours or [72, 24, 2]
            for interval in sorted(intervals, reverse=True):
                # Trigger notification if within interval and not sent recently
                if hours_remaining <= interval:
                    msg = (
                        f"⏰ **DEADLINE REMINDER**: '{dl.title}' ({dl.deadline_type})\n"
                        f"- Remaining: approximately {int(hours_remaining)} hour(s)\n"
                        f"- Target Date: {dl.deadline_date.strftime('%Y-%m-%d %H:%M')} {dl.timezone_name}\n"
                        f"- Mandatory: {'YES' if dl.is_mandatory else 'NO'}"
                    )

                    # Post to Switch room if room exists
                    room = session.query(SwitchRoom).filter(SwitchRoom.tender_id == dl.tender_id).first()
                    channel_id = room.channel_id if room else None

                    if channel_id and bridge:
                        try:
                            bridge.post_message(
                                channel_id=channel_id,
                                sender_agent_id="DeadlineTracker",
                                text=msg,
                            )
                        except Exception as e:
                            logger.warning("Failed to post reminder to Switch room: %s", e)

                    dl.last_notification_sent_at = utcnow()
                    notifications_sent.append({
                        "deadline_id": dl.id,
                        "title": dl.title,
                        "hours_remaining": round(hours_remaining, 1),
                        "channel_id": channel_id,
                    })
                    break  # Trigger one interval notification per scan

        session.commit()
        return notifications_sent

    def list_deadlines(
        self,
        tender_id: str,
        db: Optional[Session] = None,
    ) -> List[TenderDeadline]:
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")
        return (
            session.query(TenderDeadline)
            .filter(TenderDeadline.tender_id == tender_id)
            .order_by(TenderDeadline.deadline_date.asc())
            .all()
        )
