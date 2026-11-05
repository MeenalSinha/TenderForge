"""
Proposal Generation, Audit & Human Approval API endpoints for TenderForge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status as http_status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.session import get_db
from backend.app.services.approval_service import ApprovalService
from backend.app.services.audit_service import AuditService
from backend.app.services.export_service import ExportService
from backend.app.services.proposal_service import ProposalService

router = APIRouter(tags=["Proposals & Governance"])
proposal_service = ProposalService()
audit_service = AuditService()
approval_service = ApprovalService()
export_service = ExportService()


class CreateProposalRequest(BaseModel):
    title: Optional[str] = None
    author_id: str = "ProposalArchitect"


class HumanApprovalRequest(BaseModel):
    tender_id: str
    user_id: str
    user_name: str
    user_role: str
    decision: str  # Approved, Rejected, Changes Requested
    comments: str


class ExportPackageRequest(BaseModel):
    tender_id: str
    require_human_approval: bool = True


@router.post("/tenders/{tender_id}/proposals", status_code=http_status.HTTP_201_CREATED)
def create_proposal(
    tender_id: str,
    payload: CreateProposalRequest,
    db: Session = Depends(get_db),
):
    proposal = proposal_service.create_proposal_draft(
        db=db,
        tender_id=tender_id,
        title=payload.title,
        author_id=payload.author_id,
    )
    return {
        "status": "success",
        "data": {
            "id": proposal.id,
            "tender_id": proposal.tender_id,
            "title": proposal.title,
            "version": proposal.current_version,
            "status": proposal.status,
            "docx_path": proposal.docx_file_path,
        }
    }


@router.get("/proposals/{proposal_id}", status_code=http_status.HTTP_200_OK)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
):
    proposal = proposal_service.get_proposal(db, proposal_id)
    if not proposal:
        return {"status": "error", "message": f"Proposal '{proposal_id}' not found."}, 404

    return {
        "status": "success",
        "data": {
            "id": proposal.id,
            "tender_id": proposal.tender_id,
            "title": proposal.title,
            "version": proposal.current_version,
            "status": proposal.status,
            "docx_path": proposal.docx_file_path,
            "sections": [
                {
                    "number": s.section_number,
                    "title": s.title,
                    "content": s.content,
                    "claims": s.claims,
                }
                for s in proposal.sections
            ]
        }
    }


@router.post("/proposals/{proposal_id}/audit", status_code=http_status.HTTP_200_OK)
def audit_proposal(
    proposal_id: str,
    auditor: str = "BidAuditor",
    db: Session = Depends(get_db),
):
    audit = audit_service.audit_proposal(
        db=db,
        proposal_id=proposal_id,
        auditor_id=auditor,
    )
    return {
        "status": "success",
        "data": {
            "audit_id": audit.id,
            "proposal_id": audit.proposal_id,
            "auditor_id": audit.auditor_id,
            "readiness_score": audit.readiness_score,
            "verdict": audit.verdict,
            "total_claims": audit.total_claims,
            "verified_claims": audit.verified_claims,
            "unsupported_claims": audit.unsupported_claims,
            "contradicted_claims": audit.contradicted_claims,
            "findings_count": len(audit.findings),
            "findings": audit.findings,
        }
    }


@router.get("/proposals/{proposal_id}/audit", status_code=http_status.HTTP_200_OK)
def get_latest_audit(
    proposal_id: str,
    db: Session = Depends(get_db),
):
    audit = audit_service.get_latest_audit(db, proposal_id)
    if not audit:
        return {"status": "error", "message": f"No audit found for proposal '{proposal_id}'."}, 404

    return {
        "status": "success",
        "data": {
            "audit_id": audit.id,
            "proposal_id": audit.proposal_id,
            "readiness_score": audit.readiness_score,
            "verdict": audit.verdict,
            "total_claims": audit.total_claims,
            "verified_claims": audit.verified_claims,
            "unsupported_claims": audit.unsupported_claims,
            "contradicted_claims": audit.contradicted_claims,
            "findings": audit.findings,
        }
    }


@router.post("/proposals/{proposal_id}/approve", status_code=http_status.HTTP_200_OK)
def record_human_approval(
    proposal_id: str,
    payload: HumanApprovalRequest,
    db: Session = Depends(get_db),
):
    approval = approval_service.record_decision(
        db=db,
        tender_id=payload.tender_id,
        proposal_id=proposal_id,
        user_id=payload.user_id,
        user_name=payload.user_name,
        user_role=payload.user_role,
        decision=payload.decision,
        comments=payload.comments,
    )
    return {
        "status": "success",
        "data": {
            "approval_id": approval.id,
            "decision": approval.decision,
            "user_name": approval.user_name,
            "user_role": approval.user_role,
            "signature_hash": approval.signature_hash,
            "timestamp": approval.created_at.isoformat(),
        }
    }


@router.post("/proposals/{proposal_id}/export", status_code=http_status.HTTP_200_OK)
def export_bid_package(
    proposal_id: str,
    payload: ExportPackageRequest,
    db: Session = Depends(get_db),
):
    zip_path = export_service.export_bid_package(
        db=db,
        tender_id=payload.tender_id,
        proposal_id=proposal_id,
        require_human_approval=payload.require_human_approval,
    )
    return {
        "status": "success",
        "data": {
            "package_path": zip_path,
            "filename": str(zip_path).split("\\")[-1].split("/")[-1],
        }
    }
