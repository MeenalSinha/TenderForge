"""
ProofLink Evidence Traceability API endpoints for TenderForge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status as http_status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import EvidenceRequirementLink, TenderRequirement
from backend.app.infrastructure.database.session import get_db
from backend.app.services.prooflink_service import ProofLinkService, ProofLinkStatus

router = APIRouter(tags=["ProofLink Traceability"])
prooflink_service = ProofLinkService()


class ProofLinkConfirmRequest(BaseModel):
    user_id: str
    status: str = ProofLinkStatus.HUMAN_CONFIRMED
    notes: Optional[str] = None


@router.post("/tenders/{tender_id}/prooflink/match", status_code=http_status.HTTP_200_OK)
def match_tender_evidence(
    tender_id: str,
    organization_id: str = Query(...),
    db: Session = Depends(get_db),
):
    links = prooflink_service.match_all_tender_requirements(
        db=db,
        tender_id=tender_id,
        organization_id=organization_id,
    )
    return {
        "status": "success",
        "matched_count": len(links),
        "data": [
            {
                "id": l.id,
                "requirement_id": l.requirement_id,
                "evidence_id": l.evidence_id,
                "match_status": l.match_status,
                "confidence_score": l.confidence_score,
                "notes": l.notes,
            }
            for l in links
        ]
    }


@router.get("/tenders/{tender_id}/prooflink", status_code=http_status.HTTP_200_OK)
def list_tender_prooflinks(
    tender_id: str,
    db: Session = Depends(get_db),
):
    requirements = db.query(TenderRequirement).filter(TenderRequirement.tender_id == tender_id).all()
    req_ids = [r.id for r in requirements]

    links = db.query(EvidenceRequirementLink).filter(EvidenceRequirementLink.requirement_id.in_(req_ids)).all() if req_ids else []

    return {
        "status": "success",
        "count": len(links),
        "data": [
            {
                "id": l.id,
                "requirement_id": l.requirement_id,
                "evidence_id": l.evidence_id,
                "match_status": l.match_status,
                "confidence_score": l.confidence_score,
                "source_excerpt": l.source_excerpt,
                "notes": l.notes,
                "verified_by_user_id": l.verified_by_user_id,
                "verified_at": l.verified_at.isoformat() if l.verified_at else None,
            }
            for l in links
        ]
    }


@router.post("/prooflink/{link_id}/confirm", status_code=http_status.HTTP_200_OK)
def confirm_prooflink(
    link_id: str,
    payload: ProofLinkConfirmRequest,
    db: Session = Depends(get_db),
):
    link = prooflink_service.confirm_evidence_link(
        db=db,
        link_id=link_id,
        user_id=payload.user_id,
        status=payload.status,
        notes=payload.notes,
    )
    return {
        "status": "success",
        "data": {
            "id": link.id,
            "match_status": link.match_status,
            "verified_by_user_id": link.verified_by_user_id,
            "verified_at": link.verified_at.isoformat() if link.verified_at else None,
            "notes": link.notes,
        }
    }
