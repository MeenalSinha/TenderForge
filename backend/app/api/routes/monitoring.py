"""
Tender Monitoring & Corrigendum Intelligence API Routes.
Enables continuous monitoring, version snapshots, amendment impact detection, and human acknowledgement.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import (
    TenderAmendment,
    TenderMonitorSubscription,
    TenderSnapshot,
)
from backend.app.infrastructure.database.session import get_db
from backend.app.services.amendment_service import AmendmentService
from backend.app.services.tender_monitoring_service import TenderMonitoringService

router = APIRouter(tags=["Tender Monitoring & Amendments"])


class SubscribeMonitoringRequest(BaseModel):
    check_frequency_minutes: int = Field(default=60, ge=5, le=1440)
    source_id: Optional[str] = None
    notify_channels: Optional[List[str]] = Field(default_factory=lambda: ["email", "in_app"])


class CaptureSnapshotRequest(BaseModel):
    content_text: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    amendment_notice_title: Optional[str] = None


class AcknowledgeAmendmentRequest(BaseModel):
    notes: Optional[str] = None


@router.post("/tenders/{tender_id}/monitor", status_code=status.HTTP_201_CREATED)
def subscribe_tender_monitoring(
    tender_id: str,
    payload: SubscribeMonitoringRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = claims.get("org_id") or settings.default_organization_id
    svc = TenderMonitoringService()
    sub = svc.create_subscription(
        db=db,
        tender_id=tender_id,
        organization_id=org_id,
        source_id=payload.source_id,
        check_frequency_minutes=payload.check_frequency_minutes,
        notify_channels=payload.notify_channels,
    )
    return {
        "status": "success",
        "subscription": {
            "id": sub.id,
            "tender_id": sub.tender_id,
            "is_active": sub.is_active,
            "check_frequency_minutes": sub.check_frequency_minutes,
            "notify_channels": sub.notify_channels,
            "last_checked_at": sub.last_checked_at.isoformat() if sub.last_checked_at else None,
        },
    }


@router.get("/tenders/{tender_id}/snapshots")
def list_snapshots(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = TenderMonitoringService()
    snapshots = svc.list_snapshots(db, tender_id)
    return {
        "count": len(snapshots),
        "snapshots": [
            {
                "id": s.id,
                "version": s.snapshot_version,
                "content_hash": s.content_hash,
                "metadata": s.metadata_payload,
                "captured_at": s.captured_at.isoformat(),
            }
            for s in snapshots
        ],
    }


@router.post("/tenders/{tender_id}/snapshots", status_code=status.HTTP_201_CREATED)
def capture_snapshot(
    tender_id: str,
    payload: CaptureSnapshotRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = claims.get("org_id") or settings.default_organization_id
    svc = TenderMonitoringService()

    # Ensure subscription exists
    sub = (
        db.query(TenderMonitorSubscription)
        .filter(
            TenderMonitorSubscription.tender_id == tender_id,
            TenderMonitorSubscription.organization_id == org_id,
        )
        .first()
    )
    if not sub:
        sub = svc.create_subscription(db, tender_id, org_id)

    snapshot, amendment = svc.capture_snapshot(
        db=db,
        subscription_id=sub.id,
        content_text=payload.content_text,
        metadata=payload.metadata or {},
        amendment_notice_title=payload.amendment_notice_title,
    )

    return {
        "status": "success",
        "snapshot": {
            "id": snapshot.id,
            "version": snapshot.snapshot_version,
            "content_hash": snapshot.content_hash,
            "captured_at": snapshot.captured_at.isoformat(),
        },
        "detected_amendment": {
            "id": amendment.id,
            "amendment_number": amendment.amendment_number,
            "title": amendment.title,
            "materiality": amendment.materiality,
            "diff_summary": amendment.diff_summary,
            "downstream_impact": amendment.downstream_impact,
            "approval_invalidated": amendment.approval_invalidated,
        } if amendment else None,
    }


@router.get("/tenders/{tender_id}/amendments")
def list_amendments(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = AmendmentService()
    amendments = svc.list_amendments(db, tender_id)
    return {
        "count": len(amendments),
        "amendments": [
            {
                "id": a.id,
                "amendment_number": a.amendment_number,
                "title": a.title,
                "materiality": a.materiality,
                "diff_summary": a.diff_summary,
                "affected_clauses": a.affected_clauses,
                "downstream_impact": a.downstream_impact,
                "approval_invalidated": a.approval_invalidated,
                "publication_date": a.publication_date.isoformat(),
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            }
            for a in amendments
        ],
    }


@router.post("/amendments/{amendment_id}/acknowledge")
def acknowledge_amendment(
    amendment_id: str,
    payload: AcknowledgeAmendmentRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    user_id = claims.get("sub") or "user-anon"
    svc = AmendmentService()
    try:
        amendment = svc.acknowledge_amendment(
            db=db,
            amendment_id=amendment_id,
            user_id=user_id,
            notes=payload.notes,
        )
        return {
            "status": "success",
            "message": "Amendment acknowledged.",
            "amendment_id": amendment.id,
            "acknowledged_at": amendment.acknowledged_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

