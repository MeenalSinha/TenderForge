"""
Tender Deadlines & Notification Intelligence API Routes for TenderForge.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.deadline_service import DeadlineService

router = APIRouter(tags=["Deadlines"])


class CreateDeadlineRequest(BaseModel):
    deadline_type: str = "Technical Bid Submission"
    title: str
    deadline_date: datetime
    timezone_name: str = "UTC"
    is_mandatory: bool = True
    reminder_intervals_hours: Optional[List[int]] = None
    notes: Optional[str] = None


@router.get("/tenders/{tender_id}/deadlines")
def list_deadlines(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> List[Dict[str, Any]]:
    svc = DeadlineService(db)
    items = svc.list_deadlines(tender_id)
    return [
        {
            "id": d.id,
            "deadline_type": d.deadline_type,
            "title": d.title,
            "deadline_date": d.deadline_date.isoformat(),
            "timezone_name": d.timezone_name,
            "is_mandatory": d.is_mandatory,
            "status": d.status,
            "notes": d.notes,
            "last_notification_sent_at": d.last_notification_sent_at.isoformat() if d.last_notification_sent_at else None,
        }
        for d in items
    ]


@router.post("/tenders/{tender_id}/deadlines", status_code=status.HTTP_201_CREATED)
def create_deadline(
    tender_id: str,
    payload: CreateDeadlineRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = DeadlineService(db)
    try:
        dl = svc.create_deadline(
            tender_id=tender_id,
            deadline_type=payload.deadline_type,
            title=payload.title,
            deadline_date=payload.deadline_date,
            timezone_name=payload.timezone_name,
            is_mandatory=payload.is_mandatory,
            reminder_intervals_hours=payload.reminder_intervals_hours,
            notes=payload.notes,
        )
        return {
            "id": dl.id,
            "title": dl.title,
            "deadline_type": dl.deadline_type,
            "deadline_date": dl.deadline_date.isoformat(),
            "status": dl.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deadlines/check-reminders")
def check_reminders(
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> List[Dict[str, Any]]:
    svc = DeadlineService(db)
    return svc.check_and_send_reminders()
