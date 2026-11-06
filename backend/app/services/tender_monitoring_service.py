"""
Tender Monitoring & Snapshot Service.
Maintains continuous monitor subscriptions, captures periodic snapshots,
computes cryptographic hashes, and triggers amendment analysis.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    ProcurementSource,
    Tender,
    TenderAmendment,
    TenderMonitorSubscription,
    TenderSnapshot,
)
from backend.app.services.amendment_service import AmendmentService

logger = get_logger(__name__)


class TenderMonitoringService:
    """Manages active monitoring subscriptions, periodic polling, and snapshot comparisons."""

    def __init__(self, amendment_service: Optional[AmendmentService] = None):
        self.amendment_service = amendment_service or AmendmentService()

    @staticmethod
    def compute_content_hash(text_content: str, metadata: Dict[str, Any]) -> str:
        canonical_str = f"{text_content.strip()}|{json.dumps(metadata, sort_keys=True)}"
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def create_subscription(
        self,
        db: Session,
        tender_id: str,
        organization_id: str,
        source_id: Optional[str] = None,
        check_frequency_minutes: int = 60,
        notify_channels: Optional[List[str]] = None,
    ) -> TenderMonitorSubscription:
        existing = (
            db.query(TenderMonitorSubscription)
            .filter(
                TenderMonitorSubscription.tender_id == tender_id,
                TenderMonitorSubscription.organization_id == organization_id,
            )
            .first()
        )
        if existing:
            existing.is_active = True
            existing.check_frequency_minutes = check_frequency_minutes
            if notify_channels:
                existing.notify_channels = notify_channels
            db.commit()
            db.refresh(existing)
            return existing

        sub = TenderMonitorSubscription(
            tender_id=tender_id,
            organization_id=organization_id,
            source_id=source_id,
            is_active=True,
            check_frequency_minutes=check_frequency_minutes,
            notify_channels=notify_channels or ["email", "in_app"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub

    def capture_snapshot(
        self,
        db: Session,
        subscription_id: str,
        content_text: str,
        metadata: Dict[str, Any],
        amendment_notice_title: Optional[str] = None,
    ) -> Tuple[TenderSnapshot, Optional[TenderAmendment]]:
        """
        Captures a new point-in-time snapshot. If the content hash differs from previous snapshot,
        triggers amendment classification and downstream impact propagation.
        """
        sub = db.query(TenderMonitorSubscription).filter(TenderMonitorSubscription.id == subscription_id).first()
        if not sub:
            raise ValueError(f"Subscription '{subscription_id}' not found.")

        current_hash = self.compute_content_hash(content_text, metadata)
        sub.last_checked_at = datetime.now(timezone.utc)

        # Get latest snapshot
        last_snapshot = (
            db.query(TenderSnapshot)
            .filter(TenderSnapshot.subscription_id == sub.id)
            .order_by(TenderSnapshot.snapshot_version.desc())
            .first()
        )

        next_version = (last_snapshot.snapshot_version + 1) if last_snapshot else 1

        new_snapshot = TenderSnapshot(
            subscription_id=sub.id,
            tender_id=sub.tender_id,
            snapshot_version=next_version,
            content_hash=current_hash,
            raw_content=content_text,
            metadata_payload=metadata,
            captured_at=datetime.now(timezone.utc),
        )
        db.add(new_snapshot)

        detected_amendment: Optional[TenderAmendment] = None

        # Check for change
        if last_snapshot and last_snapshot.content_hash != current_hash:
            # Hash mismatch detected - analyze differences
            old_meta = last_snapshot.metadata_payload or {}
            new_meta = metadata or {}

            deadline_changed = old_meta.get("submission_deadline") != new_meta.get("submission_deadline")
            budget_changed = old_meta.get("estimated_value") != new_meta.get("estimated_value")

            diff_summary = f"Content hash updated from {last_snapshot.content_hash[:12]} to {current_hash[:12]}."
            affected_clauses = [
                {"clause": "Document Content", "description": "Modifications detected in official tender text specifications."}
            ]
            if deadline_changed:
                diff_summary += f" Submission deadline revised to {new_meta.get('submission_deadline')}."
                affected_clauses.append({
                    "clause": "Submission Schedule",
                    "description": f"Deadline updated: was {old_meta.get('submission_deadline')}, now {new_meta.get('submission_deadline')}.",
                })

            amendment_num = f"CORR-{next_version:02d}"
            amendment_title = amendment_notice_title or f"Corrigendum / Addendum {amendment_num}"

            detected_amendment = self.amendment_service.record_amendment(
                db=db,
                tender_id=sub.tender_id,
                amendment_number=amendment_num,
                title=amendment_title,
                diff_summary=diff_summary,
                affected_clauses=affected_clauses,
                deadline_changed=deadline_changed,
                budget_changed=budget_changed,
            )

        sub.last_snapshot_hash = current_hash
        db.commit()
        db.refresh(new_snapshot)
        return new_snapshot, detected_amendment

    def list_subscriptions(self, db: Session, organization_id: str) -> List[TenderMonitorSubscription]:
        return (
            db.query(TenderMonitorSubscription)
            .filter(TenderMonitorSubscription.organization_id == organization_id)
            .order_by(TenderMonitorSubscription.created_at.desc())
            .all()
        )

    def list_snapshots(self, db: Session, tender_id: str) -> List[TenderSnapshot]:
        return (
            db.query(TenderSnapshot)
            .filter(TenderSnapshot.tender_id == tender_id)
            .order_by(TenderSnapshot.snapshot_version.desc())
            .all()
        )

