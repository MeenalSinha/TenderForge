"""
Opportunity Service: Manages procurement sources, external opportunity ingestion,
multi-factor deduplication, and workspace promotion.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    ConnectorRun,
    ProcurementSource,
    SourceOpportunity,
    Tender,
    Workspace,
    generate_uuid,
)
from backend.app.integrations.procurement.connector_registry import ConnectorRegistry
from backend.app.integrations.procurement.base_connector import DiscoveredOpportunity

logger = get_logger(__name__)


class OpportunityService:
    """Handles external procurement opportunity ingestion, deduplication, and lifecycle."""

    @staticmethod
    def compute_deduplication_hash(title: str, buyer_name: str, external_id: Optional[str] = None) -> str:
        """
        Computes a deterministic hash for deduplicating tender opportunities across sources.
        Normalizes whitespace, casing, and punctuation.
        """
        def clean(s: Optional[str]) -> str:
            if not s:
                return ""
            return re.sub(r"[^a-z0-9]", "", s.lower())

        c_title = clean(title)[:80]
        c_buyer = clean(buyer_name)[:50]
        c_ext = clean(external_id)[:40]

        raw = f"{c_title}|{c_buyer}|{c_ext}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_or_create_source(
        self,
        db: Session,
        organization_id: str,
        name: str,
        connector_type: str = "mock_sandbox",
        endpoint_url: Optional[str] = None,
        auth_type: str = "none",
        auth_config: Optional[Dict[str, Any]] = None,
        polling_interval_minutes: int = 60,
    ) -> ProcurementSource:
        source = (
            db.query(ProcurementSource)
            .filter(
                ProcurementSource.organization_id == organization_id,
                ProcurementSource.name == name,
            )
            .first()
        )
        if not source:
            source = ProcurementSource(
                organization_id=organization_id,
                name=name,
                connector_type=connector_type,
                endpoint_url=endpoint_url,
                auth_type=auth_type,
                auth_config=auth_config or {},
                polling_interval_minutes=polling_interval_minutes,
                is_active=True,
                sync_status="idle",
            )
            db.add(source)
            db.commit()
            db.refresh(source)
        return source

    async def sync_source(
        self,
        db: Session,
        source_id: str,
        limit: int = 50,
    ) -> Tuple[ConnectorRun, List[SourceOpportunity]]:
        """Executes a synchronization cycle for the given source and stores discovered opportunities."""
        source = db.query(ProcurementSource).filter(ProcurementSource.id == source_id).first()
        if not source:
            raise ValueError(f"Procurement source with id '{source_id}' not found.")

        # Create connector run record
        run = ConnectorRun(
            source_id=source.id,
            status="running",
            started_at=datetime.now(timezone.utc),
            items_discovered=0,
            items_ingested=0,
            run_log=[],
        )
        db.add(run)
        source.sync_status = "syncing"
        db.commit()
        db.refresh(run)

        security_conf = settings.procurement_sources_config.get("security", {})
        connector_config = {
            "endpoint_url": source.endpoint_url,
            "auth_type": source.auth_type,
            "auth_config": source.auth_config,
        }

        try:
            connector = ConnectorRegistry.get_connector(
                source_id=source.id,
                connector_type=source.connector_type,
                config=connector_config,
                security_config=security_conf,
            )
            result = await connector.discover(since=source.last_synced_at, limit=limit)

            ingested_opportunities: List[SourceOpportunity] = []
            for disc in result.opportunities:
                dedup_hash = self.compute_deduplication_hash(
                    title=disc.title,
                    buyer_name=disc.buyer_name,
                    external_id=disc.external_id,
                )

                # Deduplication check
                existing = (
                    db.query(SourceOpportunity)
                    .filter(
                        SourceOpportunity.organization_id == source.organization_id,
                        SourceOpportunity.deduplication_hash == dedup_hash,
                    )
                    .first()
                )

                if existing:
                    # Update metadata or deadline if changed
                    existing.submission_deadline = disc.submission_deadline or existing.submission_deadline
                    existing.status = disc.status or existing.status
                    existing.updated_at = datetime.now(timezone.utc)
                    ingested_opportunities.append(existing)
                else:
                    new_opp = SourceOpportunity(
                        source_id=source.id,
                        organization_id=source.organization_id,
                        external_id=disc.external_id,
                        title=disc.title,
                        buyer_name=disc.buyer_name,
                        procurement_category=disc.procurement_category,
                        estimated_budget=disc.estimated_budget,
                        currency=disc.currency,
                        published_date=disc.published_date,
                        submission_deadline=disc.submission_deadline,
                        status=disc.status,
                        opportunity_url=disc.opportunity_url,
                        canonical_summary=disc.canonical_summary,
                        raw_payload=disc.raw_payload,
                        deduplication_hash=dedup_hash,
                        match_status="unmatched",
                    )
                    db.add(new_opp)
                    ingested_opportunities.append(new_opp)

            db.commit()

            run.status = "completed" if result.status == "completed" else "failed"
            run.completed_at = datetime.now(timezone.utc)
            run.items_discovered = result.items_discovered
            run.items_ingested = len(ingested_opportunities)
            run.error_message = "\n".join(result.errors) if result.errors else None
            run.run_log = [{"discovered": result.items_discovered, "errors": result.errors}]

            source.sync_status = "success" if run.status == "completed" else "failed"
            source.last_synced_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(run)

            return run, ingested_opportunities

        except Exception as exc:
            db.rollback()
            run.status = "failed"
            run.completed_at = datetime.now(timezone.utc)
            run.error_message = str(exc)
            source.sync_status = "failed"
            db.commit()
            logger.error("Failed to sync procurement source %s: %s", source_id, exc)
            raise

    def list_opportunities(
        self,
        db: Session,
        organization_id: str,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[SourceOpportunity], int]:
        q = db.query(SourceOpportunity).filter(SourceOpportunity.organization_id == organization_id)

        if category:
            q = q.filter(SourceOpportunity.procurement_category.ilike(f"%{category}%"))
        if status:
            q = q.filter(SourceOpportunity.status == status)
        if min_budget is not None:
            q = q.filter(SourceOpportunity.estimated_budget >= min_budget)
        if max_budget is not None:
            q = q.filter(SourceOpportunity.estimated_budget <= max_budget)
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    SourceOpportunity.title.ilike(term),
                    SourceOpportunity.buyer_name.ilike(term),
                    SourceOpportunity.canonical_summary.ilike(term),
                    SourceOpportunity.external_id.ilike(term),
                )
            )

        total = q.count()
        results = q.order_by(desc(SourceOpportunity.created_at)).offset(skip).limit(limit).all()
        return results, total

    def get_opportunity(self, db: Session, opportunity_id: str) -> Optional[SourceOpportunity]:
        return db.query(SourceOpportunity).filter(SourceOpportunity.id == opportunity_id).first()

    def promote_opportunity_to_tender(
        self,
        db: Session,
        opportunity_id: str,
        workspace_id: Optional[str] = None,
        custom_title: Optional[str] = None,
    ) -> Tender:
        """Promotes a discovered opportunity into a full workspace and Tender entity for proposal development."""
        opp = self.get_opportunity(db, opportunity_id)
        if not opp:
            raise ValueError(f"Source opportunity '{opportunity_id}' not found.")

        # Ensure a valid workspace exists for the organization
        if not workspace_id:
            ws = db.query(Workspace).filter(Workspace.organization_id == opp.organization_id).first()
            if not ws:
                ws = Workspace(
                    organization_id=opp.organization_id,
                    name=f"Workspace - {opp.buyer_name[:40]}",
                    description=f"Auto-created workspace for opportunity {opp.external_id or opp.title[:30]}",
                )
                db.add(ws)
                db.flush()
            target_ws_id = ws.id
        else:
            target_ws_id = workspace_id

        # Create Tender
        tender = Tender(
            workspace_id=target_ws_id,
            title=custom_title or opp.title,
            reference_number=opp.external_id or f"OPP-{opp.id[:8].upper()}",
            issuing_authority=opp.buyer_name,
            procurement_category=opp.procurement_category,
            estimated_value=opp.estimated_budget,
            currency=opp.currency,
            submission_deadline=opp.submission_deadline,
            status="draft",
        )
        db.add(tender)

        opp.match_status = "promoted_to_workspace"
        db.commit()
        db.refresh(tender)
        return tender

