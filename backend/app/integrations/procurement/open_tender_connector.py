"""
Open Contracting Data Standard (OCDS) Procurement Connector.
Ingests normalized public procurement releases and contract notices from OCDS-compliant APIs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from backend.app.integrations.procurement.base_connector import (
    BaseProcurementConnector,
    ConnectorSyncResult,
    DiscoveredOpportunity,
)


class OpenTenderApiConnector(BaseProcurementConnector):
    """Connector for OCDS (Open Contracting Data Standard) procurement feeds."""

    def validate_configuration(self) -> bool:
        endpoint = self.config.get("endpoint_url")
        if not endpoint:
            raise ValueError("OCDS connector requires 'endpoint_url' in configuration.")
        self.validate_security(endpoint)
        return True

    def _normalize_ocds_release(self, release: Dict[str, Any]) -> Optional[DiscoveredOpportunity]:
        """Maps an OCDS release object into a DiscoveredOpportunity."""
        tender = release.get("tender") or {}
        if not tender:
            return None

        ext_id = str(tender.get("id") or release.get("ocid") or "")
        title = tender.get("title") or release.get("id") or "Untitled Tender"

        # Procuring entity
        procuring_entity = tender.get("procuringEntity") or {}
        buyer_name = procuring_entity.get("name") or release.get("buyer", {}).get("name") or "Public Contracting Authority"

        # Value
        val = tender.get("value") or {}
        budget = None
        if val.get("amount") is not None:
            try:
                budget = float(val["amount"])
            except Exception:
                budget = None
        currency = val.get("currency") or "USD"

        # Dates
        pub_date = None
        date_str = release.get("date")
        if date_str:
            try:
                pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except Exception:
                pass

        tender_period = tender.get("tenderPeriod") or {}
        deadline = None
        end_date_str = tender_period.get("endDate")
        if end_date_str:
            try:
                deadline = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except Exception:
                pass

        category = tender.get("mainProcurementCategory") or "general"
        status = tender.get("status") or "open"
        summary = tender.get("description")

        # Document links
        documents = tender.get("documents") or []
        doc_url = None
        if documents and isinstance(documents, list) and documents[0].get("url"):
            doc_url = documents[0]["url"]

        return DiscoveredOpportunity(
            external_id=ext_id,
            title=title,
            buyer_name=buyer_name,
            procurement_category=category,
            estimated_budget=budget,
            currency=currency,
            published_date=pub_date,
            submission_deadline=deadline,
            status=status,
            opportunity_url=doc_url or self.config.get("endpoint_url"),
            canonical_summary=summary,
            raw_payload=release,
        )

    async def discover(self, since: Optional[datetime] = None, limit: int = 50) -> ConnectorSyncResult:
        self.validate_configuration()
        endpoint = self.config.get("endpoint_url")
        headers = {"User-Agent": "TenderForge-OCDS-Client/1.0"}

        auth_type = self.config.get("auth_type", "none")
        auth_config = self.config.get("auth_config") or {}
        if auth_type == "api_key" and auth_config.get("api_key"):
            headers["X-API-Key"] = auth_config["api_key"]
        elif auth_type == "bearer" and auth_config.get("token"):
            headers["Authorization"] = f"Bearer {auth_config['token']}"

        result = ConnectorSyncResult(source_id=self.source_id, status="completed")
        params = {"limit": limit}
        if since:
            params["updated_since"] = since.isoformat()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(endpoint, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()

            releases = data.get("releases", [])
            for rel in releases[:limit]:
                opp = self._normalize_ocds_release(rel)
                if opp:
                    result.opportunities.append(opp)

            result.items_discovered = len(result.opportunities)
            result.items_ingested = len(result.opportunities)
            result.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            result.status = "failed"
            result.errors.append(f"HTTP fetch failed for {endpoint}: {str(exc)}")
            result.completed_at = datetime.now(timezone.utc)

        return result

    async def fetch_details(self, external_id: str) -> Optional[DiscoveredOpportunity]:
        self.validate_configuration()
        endpoint = f"{self.config.get('endpoint_url')}/{external_id}"
        self.validate_security(endpoint)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(endpoint)
                resp.raise_for_status()
                data = resp.json()
            return self._normalize_ocds_release(data)
        except Exception:
            return None

