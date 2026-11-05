"""
Multi-Agent Workflow Orchestrator for TenderForge.
Manages the finite state machine coordinating specialized AI agents and human gates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, WorkflowError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    Tender,
    WorkflowState,
)
from backend.app.services.approval_service import ApprovalService
from backend.app.services.audit_service import AuditService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.prooflink_service import ProofLinkService
from backend.app.services.proposal_service import ProposalService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService

logger = get_logger("workflow_orchestrator")


class WorkflowStage:
    WORKSPACE_INITIALIZED = "WORKSPACE_INITIALIZED"
    TENDER_ANALYZED = "TENDER_ANALYZED"
    EVIDENCE_MAPPED = "EVIDENCE_MAPPED"
    COMPLIANCE_EVALUATED = "COMPLIANCE_EVALUATED"
    PROPOSAL_DRAFTED = "PROPOSAL_DRAFTED"
    PROPOSAL_AUDITED = "PROPOSAL_AUDITED"
    HUMAN_REVIEW_PENDING = "HUMAN_REVIEW_PENDING"
    BID_APPROVED = "BID_APPROVED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


VALID_TRANSITIONS = {
    WorkflowStage.WORKSPACE_INITIALIZED: [WorkflowStage.TENDER_ANALYZED],
    WorkflowStage.TENDER_ANALYZED: [WorkflowStage.EVIDENCE_MAPPED],
    WorkflowStage.EVIDENCE_MAPPED: [WorkflowStage.COMPLIANCE_EVALUATED],
    WorkflowStage.COMPLIANCE_EVALUATED: [WorkflowStage.PROPOSAL_DRAFTED],
    WorkflowStage.PROPOSAL_DRAFTED: [WorkflowStage.PROPOSAL_AUDITED],
    WorkflowStage.PROPOSAL_AUDITED: [WorkflowStage.HUMAN_REVIEW_PENDING, WorkflowStage.REVISION_REQUIRED],
    WorkflowStage.HUMAN_REVIEW_PENDING: [WorkflowStage.BID_APPROVED, WorkflowStage.REVISION_REQUIRED],
    WorkflowStage.REVISION_REQUIRED: [WorkflowStage.PROPOSAL_DRAFTED],
    WorkflowStage.BID_APPROVED: [],  # Terminal state
}


class WorkflowOrchestrator:
    """Coordinates lifecycle stages, transitions, and agent invocations."""

    def __init__(
        self,
        intelligence_service: Optional[TenderIntelligenceService] = None,
        prooflink_service: Optional[ProofLinkService] = None,
        compliance_service: Optional[ComplianceService] = None,
        proposal_service: Optional[ProposalService] = None,
        audit_service: Optional[AuditService] = None,
        approval_service: Optional[ApprovalService] = None,
    ):
        self.intel_service = intelligence_service or TenderIntelligenceService()
        self.prooflink_service = prooflink_service or ProofLinkService()
        self.compliance_service = compliance_service or ComplianceService()
        self.proposal_service = proposal_service or ProposalService()
        self.audit_service = audit_service or AuditService()
        self.approval_service = approval_service or ApprovalService()

    def get_or_create_workflow(self, db: Session, tender_id: str) -> WorkflowState:
        """Fetch or initialize workflow state for a tender."""
        state = db.query(WorkflowState).filter(WorkflowState.tender_id == tender_id).first()
        if not state:
            state = WorkflowState(
                tender_id=tender_id,
                current_stage=WorkflowStage.WORKSPACE_INITIALIZED,
                stage_history=[{
                    "stage": WorkflowStage.WORKSPACE_INITIALIZED,
                    "actor": "system",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "notes": "Workflow initialized.",
                }],
            )
            db.add(state)
            db.commit()
            db.refresh(state)
        return state

    def transition_to(
        self,
        db: Session,
        tender_id: str,
        target_stage: str,
        actor: str,
        notes: Optional[str] = None,
    ) -> WorkflowState:
        """Transition workflow to a new stage if permitted by the transition graph."""
        state = self.get_or_create_workflow(db, tender_id)
        current = state.current_stage

        allowed = VALID_TRANSITIONS.get(current, [])
        if target_stage not in allowed:
            raise WorkflowError(
                f"Invalid workflow transition from '{current}' to '{target_stage}'. Permitted: {allowed}"
            )

        history = list(state.stage_history or [])
        history.append({
            "from_stage": current,
            "to_stage": target_stage,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": notes or f"Transitioned to {target_stage}",
        })

        state.current_stage = target_stage
        state.stage_history = history
        db.commit()
        db.refresh(state)
        logger.info(f"Workflow for tender {tender_id} transitioned: {current} -> {target_stage} by {actor}")
        return state

    def execute_next_stage(
        self,
        db: Session,
        tender_id: str,
        organization_id: str,
    ) -> Dict[str, Any]:
        """Execute the next logical pipeline step automatically."""
        state = self.get_or_create_workflow(db, tender_id)
        current = state.current_stage

        if current == WorkflowStage.WORKSPACE_INITIALIZED:
            # Run Tender Analyst
            result = self.intel_service.analyze_tender_sync(tender_id, db)
            self.transition_to(db, tender_id, WorkflowStage.TENDER_ANALYZED, "TenderAnalyst", "Tender analyzed.")
            return {"stage": WorkflowStage.TENDER_ANALYZED, "result": result}

        elif current == WorkflowStage.TENDER_ANALYZED:
            # Run Evidence Researcher & ProofLink
            links = self.prooflink_service.match_all_tender_requirements(db, tender_id, organization_id)
            self.transition_to(db, tender_id, WorkflowStage.EVIDENCE_MAPPED, "EvidenceResearcher", f"Mapped {len(links)} evidence links.")
            return {"stage": WorkflowStage.EVIDENCE_MAPPED, "links_count": len(links)}

        elif current == WorkflowStage.EVIDENCE_MAPPED:
            # Run Compliance Officer
            matrix = self.compliance_service.evaluate_tender_compliance(db, tender_id)
            self.transition_to(db, tender_id, WorkflowStage.COMPLIANCE_EVALUATED, "ComplianceOfficer", f"Compliance evaluated: {matrix.overall_status}")
            return {"stage": WorkflowStage.COMPLIANCE_EVALUATED, "matrix_id": matrix.id, "status": matrix.overall_status}

        elif current in (WorkflowStage.COMPLIANCE_EVALUATED, WorkflowStage.REVISION_REQUIRED):
            # Run Proposal Architect
            proposal = self.proposal_service.create_proposal_draft(db, tender_id)
            self.transition_to(db, tender_id, WorkflowStage.PROPOSAL_DRAFTED, "ProposalArchitect", f"Draft proposal v{proposal.current_version} created.")
            return {"stage": WorkflowStage.PROPOSAL_DRAFTED, "proposal_id": proposal.id}

        elif current == WorkflowStage.PROPOSAL_DRAFTED:
            # Run Bid Auditor
            proposal = self.proposal_service.get_latest_proposal(db, tender_id)
            if not proposal:
                raise EntityNotFoundError(f"No proposal found for tender {tender_id}")
            audit = self.audit_service.audit_proposal(db, proposal.id)
            target = WorkflowStage.HUMAN_REVIEW_PENDING if audit.verdict != "Submission Blocked - High Risk" else WorkflowStage.REVISION_REQUIRED
            self.transition_to(db, tender_id, target, "BidAuditor", f"Audit verdict: {audit.verdict} (Score: {audit.readiness_score}%)")
            return {"stage": target, "audit_id": audit.id, "readiness_score": audit.readiness_score, "verdict": audit.verdict}

        elif current == WorkflowStage.HUMAN_REVIEW_PENDING:
            return {"stage": WorkflowStage.HUMAN_REVIEW_PENDING, "message": "Awaiting authorized human review and sign-off."}

        elif current == WorkflowStage.BID_APPROVED:
            return {"stage": WorkflowStage.BID_APPROVED, "message": "Bid approved and ready for package export."}

        return {"stage": current, "message": "No automatic action available for current stage."}
