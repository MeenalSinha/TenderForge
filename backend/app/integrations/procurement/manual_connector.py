"""
Manual Import Procurement Connector.
Supports ingesting structured CSV, JSON batches, or manual opportunity submissions.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.app.integrations.procurement.base_connector import (
    BaseProcurementConnector,
    ConnectorSyncResult,
    DiscoveredOpportunity,
)


class ManualImportConnector(BaseProcurementConnector):
    """Connector for manually imported tender packages, spreadsheets, and payloads."""

    def validate_configuration(self) -> bool:
        # Manual connector does not require remote endpoints
        return True

    def parse_payload_data(self, data_content: str, format_type: str = "json") -> List[DiscoveredOpportunity]:
        """Parses batch JSON or CSV content into DiscoveredOpportunity records."""
        opportunities: List[DiscoveredOpportunity] = []
        if not data_content or not data_content.strip():
            return opportunities

        if format_type == "json":
            parsed = json.loads(data_content)
            items = parsed if isinstance(parsed, list) else [parsed]
            for item in items:
                pub_date = None
                if item.get("published_date"):
                    try:
                        pub_date = datetime.fromisoformat(item["published_date"].replace("Z", "+00:00"))
                    except Exception:
                        pub_date = None

                deadline = None
                if item.get("submission_deadline"):
                    try:
                        deadline = datetime.fromisoformat(item["submission_deadline"].replace("Z", "+00:00"))
                    except Exception:
                        deadline = None

                budget = None
                if item.get("estimated_budget") is not None:
                    try:
                        budget = float(item["estimated_budget"])
                    except Exception:
                        budget = None

                opp = DiscoveredOpportunity(
                    external_id=str(item.get("external_id") or item.get("reference_number") or ""),
                    title=item.get("title") or "Untitled Tender",
                    buyer_name=item.get("buyer_name") or item.get("authority") or "Unknown Buyer",
                    procurement_category=item.get("procurement_category") or item.get("category") or "general",
                    estimated_budget=budget,
                    currency=item.get("currency") or "USD",
                    published_date=pub_date,
                    submission_deadline=deadline,
                    status=item.get("status") or "open",
                    opportunity_url=item.get("opportunity_url"),
                    canonical_summary=item.get("canonical_summary") or item.get("description"),
                    raw_payload=item,
                )
                opportunities.append(opp)

        elif format_type == "csv":
            reader = csv.DictReader(io.StringIO(data_content))
            for row in reader:
                budget = None
                try:
                    if row.get("estimated_budget"):
                        budget = float(row["estimated_budget"])
                except Exception:
                    budget = None

                opp = DiscoveredOpportunity(
                    external_id=row.get("external_id") or row.get("reference_number"),
                    title=row.get("title") or "Untitled Tender",
                    buyer_name=row.get("buyer_name") or "Unknown Buyer",
                    procurement_category=row.get("procurement_category") or "general",
                    estimated_budget=budget,
                    currency=row.get("currency") or "USD",
                    status=row.get("status") or "open",
                    opportunity_url=row.get("opportunity_url"),
                    canonical_summary=row.get("canonical_summary") or row.get("description"),
                    raw_payload=dict(row),
                )
                opportunities.append(opp)

        return opportunities

    async def discover(self, since: Optional[datetime] = None, limit: int = 50) -> ConnectorSyncResult:
        """Manual connector discovers records buffered in its configuration or import store."""
        raw_items = self.config.get("import_items", [])
        opportunities: List[DiscoveredOpportunity] = []
        for item in raw_items[:limit]:
            if isinstance(item, dict):
                opp = DiscoveredOpportunity(
                    external_id=item.get("external_id"),
                    title=item.get("title", "Imported Opportunity"),
                    buyer_name=item.get("buyer_name", "Procuring Agency"),
                    procurement_category=item.get("procurement_category", "general"),
                    estimated_budget=float(item.get("estimated_budget", 0.0)) if item.get("estimated_budget") else None,
                    currency=item.get("currency", "USD"),
                    status=item.get("status", "open"),
                    opportunity_url=item.get("opportunity_url"),
                    canonical_summary=item.get("canonical_summary"),
                    raw_payload=item,
                )
                opportunities.append(opp)

        return ConnectorSyncResult(
            source_id=self.source_id,
            status="completed",
            items_discovered=len(opportunities),
            items_ingested=len(opportunities),
            opportunities=opportunities,
            completed_at=datetime.now(timezone.utc),
        )

    async def fetch_details(self, external_id: str) -> Optional[DiscoveredOpportunity]:
        items = self.config.get("import_items", [])
        for item in items:
            if item.get("external_id") == external_id:
                return DiscoveredOpportunity(
                    external_id=external_id,
                    title=item.get("title", ""),
                    buyer_name=item.get("buyer_name", ""),
                    procurement_category=item.get("procurement_category", "general"),
                    raw_payload=item,
                )
        return None

