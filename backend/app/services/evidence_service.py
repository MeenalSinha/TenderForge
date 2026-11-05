"""
Service for managing Organization Profiles and the Company Evidence Repository.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, InvalidFileError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    Document,
    Organization,
    OrganizationProfile,
)
from backend.app.services.document_processing_service import DocumentProcessingService
from backend.app.services.document_service import DocumentService

logger = get_logger("evidence_service")


class EvidenceService:
    """Manages company profiles, corporate credentials, past performance, and verifiable evidence."""

    def __init__(
        self,
        document_service: Optional[DocumentService] = None,
        processing_service: Optional[DocumentProcessingService] = None,
    ):
        self.doc_service = document_service or DocumentService()
        self.proc_service = processing_service or DocumentProcessingService()

    def get_or_create_profile(
        self,
        db: Session,
        organization_id: str,
        profile_data: Optional[Dict[str, Any]] = None,
    ) -> OrganizationProfile:
        """Retrieve existing profile or create a default one for the organization."""
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise EntityNotFoundError(f"Organization '{organization_id}' not found.")

        profile = db.query(OrganizationProfile).filter(
            OrganizationProfile.organization_id == organization_id
        ).first()

        if profile:
            if profile_data:
                for k, v in profile_data.items():
                    if hasattr(profile, k) and v is not None:
                        setattr(profile, k, v)
                db.commit()
                db.refresh(profile)
            return profile

        data = profile_data or {}
        new_profile = OrganizationProfile(
            organization_id=organization_id,
            legal_name=data.get("legal_name", org.name),
            trade_name=data.get("trade_name", org.name),
            registration_number=data.get("registration_number", "REG-PENDING"),
            tax_id=data.get("tax_id", "TAX-PENDING"),
            jurisdiction=data.get("jurisdiction", "United States"),
            incorporation_date=data.get("incorporation_date"),
            headquarters_address=data.get("headquarters_address"),
            primary_contact_name=data.get("primary_contact_name"),
            primary_contact_email=data.get("primary_contact_email"),
            financial_metrics=data.get("financial_metrics", {}),
            core_capabilities=data.get("core_capabilities", []),
            certifications=data.get("certifications", []),
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        logger.info(f"Created organization profile for '{org.name}' ({organization_id})")
        return new_profile

    def register_evidence(
        self,
        db: Session,
        organization_id: str,
        title: str,
        evidence_type: str,
        issuer: Optional[str] = None,
        issue_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        reference_number: Optional[str] = None,
        status: str = "valid",
        summary: Optional[str] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        document_id: Optional[str] = None,
    ) -> CompanyEvidence:
        """Register a new evidence record directly in the repository."""
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise EntityNotFoundError(f"Organization '{organization_id}' not found.")

        evidence = CompanyEvidence(
            organization_id=organization_id,
            document_id=document_id,
            evidence_type=evidence_type,
            title=title,
            issuer=issuer,
            issue_date=issue_date,
            expiry_date=expiry_date,
            reference_number=reference_number,
            status=status,
            summary=summary,
            extracted_data=extracted_data or {},
            tags=tags or [],
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        logger.info(f"Registered company evidence '{title}' ({evidence.id}) for org {organization_id}")
        return evidence

    def upload_and_ingest_evidence_file(
        self,
        db: Session,
        organization_id: str,
        workspace_id: str,
        filename: str,
        content: bytes,
        evidence_type: str,
        title: str,
        issuer: Optional[str] = None,
        issue_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        reference_number: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> CompanyEvidence:
        """Ingest a physical evidence document using Phase 1 document parsers and register it."""
        # 1. Store and parse document via Phase 1 document pipeline
        doc = self.doc_service.register_document(
            db=db,
            workspace_id=workspace_id,
            filename=filename,
            content=content,
            document_category="company_evidence",
        )

        # 2. Extract text summary from chunks
        chunks = self.doc_service.get_extracted_content(db=db, document_id=doc.id)
        combined_text = "\n".join(c.content for c in chunks[:5])
        summary = combined_text[:500] if combined_text else "Evidence document uploaded."

        # 3. Create evidence record linked to document
        return self.register_evidence(
            db=db,
            organization_id=organization_id,
            title=title,
            evidence_type=evidence_type,
            issuer=issuer,
            issue_date=issue_date,
            expiry_date=expiry_date,
            reference_number=reference_number,
            status="valid",
            summary=summary,
            extracted_data={"file_size": len(content), "chunks_count": len(chunks)},
            tags=tags or [evidence_type],
            document_id=doc.id,
        )

    def search_evidence(
        self,
        db: Session,
        organization_id: str,
        query: Optional[str] = None,
        evidence_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[CompanyEvidence]:
        """Search company evidence repository with filtering and keyword matching."""
        q = db.query(CompanyEvidence).filter(CompanyEvidence.organization_id == organization_id)
        if evidence_type:
            q = q.filter(CompanyEvidence.evidence_type == evidence_type)

        results = q.all()

        if query:
            q_lower = query.lower()
            filtered = []
            for ev in results:
                title_match = q_lower in ev.title.lower()
                summary_match = ev.summary and q_lower in ev.summary.lower()
                issuer_match = ev.issuer and q_lower in ev.issuer.lower()
                tag_match = ev.tags and any(q_lower in str(t).lower() for t in ev.tags)
                if title_match or summary_match or issuer_match or tag_match:
                    filtered.append(ev)
            return filtered

        return results

    def get_evidence(self, db: Session, evidence_id: str) -> Optional[CompanyEvidence]:
        return db.query(CompanyEvidence).filter(CompanyEvidence.id == evidence_id).first()
