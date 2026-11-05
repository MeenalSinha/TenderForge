"""
Tender Service: Manages tender registration, document linkage, and tender overview.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.exceptions import DocumentNotFoundError, TenderNotFoundError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    Document,
    Tender,
    TenderDocument,
    TenderRequirement,
)
from backend.app.services.document_service import ensure_default_workspace

logger = get_logger(__name__)


class TenderService:
    """Manages tender domain entities and relationships."""

    def create_tender(
        self,
        title: str,
        reference_number: Optional[str] = None,
        issuing_authority: Optional[str] = None,
        procurement_category: Optional[str] = None,
        estimated_value: Optional[float] = None,
        currency: str = "USD",
        submission_deadline: Optional[datetime] = None,
        workspace_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        db: Session = None,
    ) -> Tender:
        target_ws = ensure_default_workspace(db, workspace_id)

        tender = Tender(
            workspace_id=target_ws,
            title=title,
            reference_number=reference_number,
            issuing_authority=issuing_authority,
            procurement_category=procurement_category,
            estimated_value=estimated_value,
            currency=currency,
            submission_deadline=submission_deadline,
            status="draft",
        )
        db.add(tender)
        db.flush()

        # Link documents if provided
        if document_ids:
            for doc_id in document_ids:
                doc = db.query(Document).filter(Document.id == doc_id).first()
                if not doc:
                    raise DocumentNotFoundError(f"Cannot link non-existent document ID: {doc_id}")
                link = TenderDocument(
                    tender_id=tender.id,
                    document_id=doc.id,
                    relationship_type="primary_specification",
                )
                db.add(link)

        db.commit()
        db.refresh(tender)
        logger.info(f"Registered tender {tender.id} ({tender.title})")
        return tender

    def get_tender_by_id(self, tender_id: str, db: Session) -> Tender:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise TenderNotFoundError(f"Tender with ID '{tender_id}' not found.")
        return tender

    def get_tender(self, db: Session, tender_id: str) -> Tender:
        """Alias accepting db first."""
        return self.get_tender_by_id(tender_id, db)

    def list_requirements(
        self,
        db: Session,
        tender_id: str,
        category: Optional[str] = None,
        classification: Optional[str] = None,
    ) -> List[TenderRequirement]:
        q = db.query(TenderRequirement).filter(TenderRequirement.tender_id == tender_id)
        if category:
            q = q.filter(TenderRequirement.category == category)
        if classification:
            q = q.filter(TenderRequirement.classification == classification)
        return q.order_by(TenderRequirement.created_at.asc()).all()

    def list_tenders(
        self,
        db: Session,
        workspace_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Tender], int]:
        target_ws = ensure_default_workspace(db, workspace_id)
        query = db.query(Tender).filter(Tender.workspace_id == target_ws)
        total = query.count()
        tenders = query.order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()
        return tenders, total

    def link_document(
        self,
        tender_id: str,
        document_id: str,
        relationship_type: str = "primary_specification",
        db: Session = None,
    ) -> TenderDocument:
        tender = self.get_tender_by_id(tender_id, db)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise DocumentNotFoundError(f"Document with ID '{document_id}' not found.")

        # Check existing link
        existing = (
            db.query(TenderDocument)
            .filter(
                TenderDocument.tender_id == tender_id,
                TenderDocument.document_id == document_id,
            )
            .first()
        )
        if existing:
            return existing

        link = TenderDocument(
            tender_id=tender.id,
            document_id=doc.id,
            relationship_type=relationship_type,
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    def get_tender_requirements(self, tender_id: str, db: Session) -> Dict[str, Any]:
        tender = self.get_tender_by_id(tender_id, db)
        reqs = (
            db.query(TenderRequirement)
            .filter(TenderRequirement.tender_id == tender_id)
            .order_by(TenderRequirement.created_at.asc())
            .all()
        )

        by_cat: Dict[str, List[Dict[str, Any]]] = {}
        for r in reqs:
            by_cat.setdefault(r.category, []).append(
                {
                    "id": r.id,
                    "category": r.category,
                    "classification": r.classification,
                    "description": r.description,
                    "source_document_id": r.source_document_id,
                    "source_page": r.source_page,
                    "source_offset": r.source_offset,
                    "source_excerpt": r.source_excerpt,
                    "confidence_score": r.confidence_score,
                    "human_review_status": r.human_review_status,
                }
            )

        return {
            "tender_id": tender.id,
            "title": tender.title,
            "reference_number": tender.reference_number,
            "status": tender.status,
            "total_requirements": len(reqs),
            "requirements_by_category": by_cat,
        }

