"""
Human-in-the-Loop Governance & Digital Approval Service for TenderForge.
Enforces immutable human sign-off gates, audit trails, and cryptographic signature hashes.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, SecurityError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    BidAudit,
    HumanApproval,
    Proposal,
    Tender,
)

logger = get_logger("approval_service")


class ApprovalDecision:
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CHANGES_REQUESTED = "Changes Requested"


class ApprovalService:
    """Enforces human-in-the-loop review, sign-off verification, and immutable decision logging."""

    def record_decision(
        self,
        db: Session,
        tender_id: str,
        user_id: str,
        user_name: str,
        user_role: str,
        decision: str,
        comments: str,
        proposal_id: Optional[str] = None,
        audit_id: Optional[str] = None,
    ) -> HumanApproval:
        """Record an immutable human approval or rejection decision."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        if not comments or len(comments.strip()) < 5:
            raise ValueError("Substantive comments and rationale (minimum 5 characters) are required for human sign-off.")

        valid_decisions = (ApprovalDecision.APPROVED, ApprovalDecision.REJECTED, ApprovalDecision.CHANGES_REQUESTED)
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision '{decision}'. Must be one of {valid_decisions}")

        now = datetime.now(timezone.utc)
        
        # Compute cryptographic digital signature hash
        hash_payload = f"{tender_id}:{proposal_id or ''}:{audit_id or ''}:{decision}:{user_id}:{user_role}:{now.isoformat()}:{comments}"
        signature_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        approval = HumanApproval(
            tender_id=tender_id,
            proposal_id=proposal_id,
            audit_id=audit_id,
            decision=decision,
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            comments=comments,
            signature_hash=signature_hash,
            created_at=now,
        )
        db.add(approval)

        # Update proposal status accordingly
        if proposal_id:
            proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
            if proposal:
                if decision == ApprovalDecision.APPROVED:
                    proposal.status = "approved"
                    tender.status = "approved"
                elif decision == ApprovalDecision.CHANGES_REQUESTED:
                    proposal.status = "drafting"
                elif decision == ApprovalDecision.REJECTED:
                    proposal.status = "rejected"
                    tender.status = "rejected"

        db.commit()
        db.refresh(approval)
        logger.info(f"Human decision recorded for tender {tender_id}: {decision} by {user_name} ({user_role}). Hash: {signature_hash[:16]}...")
        return approval

    def is_proposal_approved_by_human(self, db: Session, proposal_id: str) -> bool:
        """Verify whether a proposal has an immutable 'Approved' human decision."""
        approval = db.query(HumanApproval).filter(
            HumanApproval.proposal_id == proposal_id,
            HumanApproval.decision == ApprovalDecision.APPROVED,
        ).first()
        return approval is not None

    def get_approval_history(self, db: Session, tender_id: str) -> List[HumanApproval]:
        return db.query(HumanApproval).filter(
            HumanApproval.tender_id == tender_id
        ).order_by(HumanApproval.created_at.desc()).all()
