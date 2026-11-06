"""
Base Procurement Connector Interface and Security Guardrails.
Provides SSRF protection, canonical opportunity models, and abstract connector contract.
"""

from __future__ import annotations

import abc
import ipaddress
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field


class DiscoveredOpportunity(BaseModel):
    """Canonical representation of an opportunity discovered from an external or manual source."""
    external_id: Optional[str] = Field(default=None, description="External reference number or contract ID")
    title: str = Field(..., description="Official title or procurement scope")
    buyer_name: str = Field(..., description="Procuring authority or contracting body")
    procurement_category: str = Field(default="general", description="Category e.g., IT, Construction, Consulting")
    estimated_budget: Optional[float] = Field(default=None, description="Estimated contract value")
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")
    published_date: Optional[datetime] = Field(default=None, description="Official publication timestamp")
    submission_deadline: Optional[datetime] = Field(default=None, description="Closing deadline timestamp")
    status: str = Field(default="open", description="Procurement status (open, closing_soon, closed, awarded)")
    opportunity_url: Optional[str] = Field(default=None, description="Direct portal URL to the notice")
    canonical_summary: Optional[str] = Field(default=None, description="Brief scope summary or abstract")
    raw_payload: Dict[str, Any] = Field(default_factory=dict, description="Raw original source payload")


class ConnectorSyncResult(BaseModel):
    """Result summary of a connector synchronization cycle."""
    source_id: str
    status: str  # completed, failed
    items_discovered: int = 0
    items_ingested: int = 0
    opportunities: List[DiscoveredOpportunity] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class BaseProcurementConnector(abc.ABC):
    """Abstract Base Class for all TenderForge procurement source connectors."""

    def __init__(self, source_id: str, config: Dict[str, Any], security_config: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        self.config = config or {}
        self.security_config = security_config or {}

    def validate_security(self, url: Optional[str] = None) -> None:
        """Enforces SSRF prevention, host blocklists, and protocol constraints."""
        target_url = url or self.config.get("endpoint_url")
        if not target_url:
            return

        parsed = urlparse(target_url)
        scheme = parsed.scheme.lower()
        if scheme not in ("https", "http"):
            raise ValueError(f"Insecure or invalid URL scheme '{scheme}'. Only HTTPS is permitted.")

        # Unless insecure HTTP is explicitly allowed in dev/sandbox, require HTTPS
        allow_insecure = self.security_config.get("allow_insecure_http", False)
        if scheme == "http" and not allow_insecure:
            raise ValueError("Insecure HTTP connections are prohibited. Use HTTPS.")

        hostname = (parsed.hostname or "").lower()
        blocked_hosts = self.security_config.get(
            "blocked_hostnames",
            ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "metadata.google.internal"]
        )

        if hostname in blocked_hosts:
            raise ValueError(f"SSRF Security Violation: Target hostname '{hostname}' is blocked.")

        # Check for private IPv4 / IPv6 addresses
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                raise ValueError(f"SSRF Security Violation: Direct private/internal IP '{hostname}' is forbidden.")
        except ValueError:
            # Hostname is a domain name, not an IP literal
            pass

    @abc.abstractmethod
    def validate_configuration(self) -> bool:
        """Validate that all required parameters, credentials, and endpoints are present and valid."""
        pass

    @abc.abstractmethod
    async def discover(self, since: Optional[datetime] = None, limit: int = 50) -> ConnectorSyncResult:
        """Discover opportunities published since the given timestamp up to limit."""
        pass

    @abc.abstractmethod
    async def fetch_details(self, external_id: str) -> Optional[DiscoveredOpportunity]:
        """Fetch deep details and document metadata for a single opportunity."""
        pass

