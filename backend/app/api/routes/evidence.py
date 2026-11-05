"""
Evidence & Organization Profile API endpoints for TenderForge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status as http_status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.session import get_db
from backend.app.services.evidence_service import EvidenceService

router = APIRouter(tags=["Evidence & Profiles"])
evidence_service = EvidenceService()


class OrganizationProfileRequest(BaseModel):
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    headquarters_address: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    financial_metrics: Optional[Dict[str, Any]] = None
    core_capabilities: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class CompanyEvidenceCreateRequest(BaseModel):
    title: str
    evidence_type: str
    issuer: Optional[str] = None
    reference_number: Optional[str] = None
    summary: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


@router.post("/organizations/{organization_id}/profile", status_code=http_status.HTTP_200_OK)
def update_organization_profile(
    organization_id: str,
    payload: OrganizationProfileRequest,
    db: Session = Depends(get_db),
):
    profile = evidence_service.get_or_create_profile(
        db=db,
        organization_id=organization_id,
        profile_data=payload.model_dump(exclude_unset=True),
    )
    return {
        "status": "success",
        "data": {
            "id": profile.id,
            "organization_id": profile.organization_id,
            "legal_name": profile.legal_name,
            "registration_number": profile.registration_number,
            "tax_id": profile.tax_id,
            "financial_metrics": profile.financial_metrics,
            "certifications": profile.certifications,
            "capabilities": profile.core_capabilities,
        }
    }


@router.get("/organizations/{organization_id}/profile", status_code=http_status.HTTP_200_OK)
def get_organization_profile(
    organization_id: str,
    db: Session = Depends(get_db),
):
    profile = evidence_service.get_or_create_profile(db=db, organization_id=organization_id)
    return {
        "status": "success",
        "data": {
            "id": profile.id,
            "organization_id": profile.organization_id,
            "legal_name": profile.legal_name,
            "registration_number": profile.registration_number,
            "tax_id": profile.tax_id,
            "financial_metrics": profile.financial_metrics,
            "certifications": profile.certifications,
            "capabilities": profile.core_capabilities,
        }
    }


@router.post("/organizations/{organization_id}/evidence", status_code=http_status.HTTP_201_CREATED)
def register_evidence(
    organization_id: str,
    payload: CompanyEvidenceCreateRequest,
    db: Session = Depends(get_db),
):
    ev = evidence_service.register_evidence(
        db=db,
        organization_id=organization_id,
        title=payload.title,
        evidence_type=payload.evidence_type,
        issuer=payload.issuer,
        reference_number=payload.reference_number,
        summary=payload.summary,
        extracted_data=payload.extracted_data,
        tags=payload.tags,
    )
    return {
        "status": "success",
        "data": {
            "id": ev.id,
            "title": ev.title,
            "evidence_type": ev.evidence_type,
            "issuer": ev.issuer,
            "status": ev.status,
            "tags": ev.tags,
        }
    }


@router.get("/organizations/{organization_id}/evidence", status_code=http_status.HTTP_200_OK)
def search_evidence(
    organization_id: str,
    query: Optional[str] = Query(None),
    evidence_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    results = evidence_service.search_evidence(
        db=db,
        organization_id=organization_id,
        query=query,
        evidence_type=evidence_type,
    )
    return {
        "status": "success",
        "count": len(results),
        "data": [
            {
                "id": e.id,
                "title": e.title,
                "evidence_type": e.evidence_type,
                "issuer": e.issuer,
                "status": e.status,
                "summary": e.summary,
                "tags": e.tags,
            }
            for e in results
        ]
    }


@router.get("/evidence/{evidence_id}", status_code=http_status.HTTP_200_OK)
def get_evidence_details(
    evidence_id: str,
    db: Session = Depends(get_db),
):
    ev = evidence_service.get_evidence(db, evidence_id)
    if not ev:
        return {"status": "error", "message": f"Evidence '{evidence_id}' not found."}, 404
    return {
        "status": "success",
        "data": {
            "id": ev.id,
            "title": ev.title,
            "evidence_type": ev.evidence_type,
            "issuer": ev.issuer,
            "reference_number": ev.reference_number,
            "status": ev.status,
            "summary": ev.summary,
            "extracted_data": ev.extracted_data,
            "tags": ev.tags,
        }
    }
