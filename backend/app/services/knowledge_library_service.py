"""
Organizational Reusable Proposal Knowledge Library Service.
Manages verified corporate boilerplate, technical narratives, CVs, and methodology assets
with full versioning, approval workflows, and reuse tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    KnowledgeAsset,
    KnowledgeAssetVersion,
    ProposalSection,
    generate_uuid,
)

logger = get_logger(__name__)


class KnowledgeLibraryService:
    """Manages reusable proposal knowledge assets, editorial governance, and provenance."""

    def create_asset(
        self,
        db: Session,
        organization_id: str,
        title: str,
        content: str,
        category: str = "technical_approach",
        asset_type: str = "text",
        keywords: Optional[List[str]] = None,
        author_user_id: Optional[str] = None,
        auto_approve: bool = False,
    ) -> KnowledgeAsset:
        now = datetime.now(timezone.utc)
        asset = KnowledgeAsset(
            organization_id=organization_id,
            title=title,
            category=category,
            asset_type=asset_type,
            content=content,
            plain_text=content[:500],
            keywords=keywords or [],
            author_user_id=author_user_id,
            review_status="approved" if auto_approve else "draft",
            approved_by_user_id=author_user_id if auto_approve else None,
            approved_at=now if auto_approve else None,
            times_reused=0,
            created_at=now,
            updated_at=now,
        )
        db.add(asset)
        db.flush()

        # Create version 1
        v1 = KnowledgeAssetVersion(
            asset_id=asset.id,
            version_number=1,
            content=content,
            change_summary="Initial creation of knowledge asset.",
            modified_by_user_id=author_user_id,
            created_at=now,
        )
        db.add(v1)
        db.commit()
        db.refresh(asset)
        return asset

    def update_asset(
        self,
        db: Session,
        asset_id: str,
        content: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        change_summary: Optional[str] = None,
        modified_by_user_id: Optional[str] = None,
    ) -> KnowledgeAsset:
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Knowledge asset '{asset_id}' not found.")

        now = datetime.now(timezone.utc)
        if title:
            asset.title = title
        if category:
            asset.category = category
        if keywords is not None:
            asset.keywords = keywords

        asset.content = content
        asset.plain_text = content[:500]
        asset.updated_at = now

        # Get latest version number
        latest_ver = (
            db.query(KnowledgeAssetVersion)
            .filter(KnowledgeAssetVersion.asset_id == asset.id)
            .order_by(KnowledgeAssetVersion.version_number.desc())
            .first()
        )
        next_ver = (latest_ver.version_number + 1) if latest_ver else 1

        new_version = KnowledgeAssetVersion(
            asset_id=asset.id,
            version_number=next_ver,
            content=content,
            change_summary=change_summary or f"Updated to version {next_ver}.",
            modified_by_user_id=modified_by_user_id,
            created_at=now,
        )
        db.add(new_version)
        db.commit()
        db.refresh(asset)
        return asset

    def approve_asset(
        self,
        db: Session,
        asset_id: str,
        approver_user_id: str,
    ) -> KnowledgeAsset:
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Knowledge asset '{asset_id}' not found.")

        asset.review_status = "approved"
        asset.approved_by_user_id = approver_user_id
        asset.approved_at = datetime.now(timezone.utc)
        asset.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(asset)
        return asset

    def use_asset(
        self,
        db: Session,
        asset_id: str,
        proposal_section_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Marks asset as reused in a proposal, increments reusability metric, and optionally
        attaches content to the targeted proposal section.
        """
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Knowledge asset '{asset_id}' not found.")

        asset.times_reused += 1
        asset.updated_at = datetime.now(timezone.utc)

        section_updated = False
        if proposal_section_id:
            sec = db.query(ProposalSection).filter(ProposalSection.id == proposal_section_id).first()
            if sec:
                if sec.content:
                    sec.content = f"{sec.content}\n\n{asset.content}"
                else:
                    sec.content = asset.content
                section_updated = True

        db.commit()
        db.refresh(asset)

        return {
            "asset_id": asset.id,
            "title": asset.title,
            "category": asset.category,
            "content": asset.content,
            "times_reused": asset.times_reused,
            "section_updated": section_updated,
        }

    def list_assets(
        self,
        db: Session,
        organization_id: str,
        category: Optional[str] = None,
        review_status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[KnowledgeAsset], int]:
        q = db.query(KnowledgeAsset).filter(KnowledgeAsset.organization_id == organization_id)
        if category:
            q = q.filter(KnowledgeAsset.category == category)
        if review_status:
            q = q.filter(KnowledgeAsset.review_status == review_status)
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    KnowledgeAsset.title.ilike(term),
                    KnowledgeAsset.content.ilike(term),
                )
            )

        total = q.count()
        results = q.order_by(desc(KnowledgeAsset.times_reused), desc(KnowledgeAsset.created_at)).offset(skip).limit(limit).all()
        return results, total

    def get_asset(self, db: Session, asset_id: str) -> Optional[KnowledgeAsset]:
        return db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()

