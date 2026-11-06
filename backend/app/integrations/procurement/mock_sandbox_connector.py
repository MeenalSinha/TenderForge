"""
Mock Sandbox Procurement Connector.
Generates rich, realistic, deterministic public procurement opportunities for sandbox and offline testing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from backend.app.integrations.procurement.base_connector import (
    BaseProcurementConnector,
    ConnectorSyncResult,
    DiscoveredOpportunity,
)


class MockSandboxConnector(BaseProcurementConnector):
    """Generates realistic simulated public tender notices across industries."""

    def validate_configuration(self) -> bool:
        return True

    def _generate_seed_opportunities(self) -> List[DiscoveredOpportunity]:
        now = datetime.now(timezone.utc)
        seeds = [
            {
                "external_id": "TND-2026-CLOUD-901",
                "title": "Enterprise Hybrid Cloud Migration & Kubernetes Orchestration",
                "buyer_name": "State Department of Administrative Services",
                "procurement_category": "information_technology",
                "estimated_budget": 4850000.0,
                "currency": "USD",
                "published_date": now - timedelta(days=5),
                "submission_deadline": now + timedelta(days=25),
                "status": "open",
                "opportunity_url": "https://procure.example.gov/tenders/TND-2026-CLOUD-901",
                "canonical_summary": (
                    "Modernization of legacy mainframe applications to sovereign cloud microservices. "
                    "Mandatory requirements include SOC2 Type II, ISO 27001, active secret clearance for leads, "
                    "minimum annual revenue of $10M, and 3 previous public sector cloud migrations."
                ),
                "raw_payload": {
                    "sector": "Public Administration",
                    "evaluation_method": "Quality and Cost Based Selection (QCBS 80/20)",
                    "mandatory_gates": ["iso_27001", "minimum_turnover_10m", "past_experience_3_contracts"],
                },
            },
            {
                "external_id": "TND-2026-MED-442",
                "title": "Next-Generation Interoperable Electronic Health Records (EHR) Platform",
                "buyer_name": "Regional Health Authority & University Hospital Network",
                "procurement_category": "healthcare",
                "estimated_budget": 12500000.0,
                "currency": "USD",
                "published_date": now - timedelta(days=2),
                "submission_deadline": now + timedelta(days=40),
                "status": "open",
                "opportunity_url": "https://health-procure.example.org/notices/MED-442",
                "canonical_summary": (
                    "Turnkey rollout of FHIR-compliant electronic health records across 14 acute care hospitals. "
                    "Requires HIPAA certification, FedRAMP High equivalent, 99.999% uptime SLA, and local disaster recovery."
                ),
                "raw_payload": {
                    "sector": "Healthcare",
                    "evaluation_method": "Best Value with Technical Demonstration",
                    "mandatory_gates": ["hipaa_compliance", "fedramp_high", "24_7_sla"],
                },
            },
            {
                "external_id": "TND-2026-INFRA-108",
                "title": "Smart City Intelligent Traffic Management System (ITMS) Sensors",
                "buyer_name": "Metropolitan Transportation Commission",
                "procurement_category": "infrastructure",
                "estimated_budget": 7200000.0,
                "currency": "USD",
                "published_date": now - timedelta(days=8),
                "submission_deadline": now + timedelta(days=14),
                "status": "open",
                "opportunity_url": "https://transit.example.gov/bids/ITMS-108",
                "canonical_summary": (
                    "Deployment of 850 edge AI computer vision sensors, adaptive signal controllers, and central traffic analytics. "
                    "Requires hardware warranty for 5 years, ISO 9001, and bonded performance guarantee of 10% contract value."
                ),
                "raw_payload": {
                    "sector": "Smart Cities",
                    "evaluation_method": "Lowest Compliant Bidder",
                    "mandatory_gates": ["iso_9001", "bank_guarantee_10_percent"],
                },
            },
            {
                "external_id": "TND-2026-SEC-770",
                "title": "Autonomous Security Operations Center (SOC) Managed Detection & Response",
                "buyer_name": "National Defense Logistics Agency",
                "procurement_category": "cybersecurity",
                "estimated_budget": 8900000.0,
                "currency": "USD",
                "published_date": now - timedelta(days=1),
                "submission_deadline": now + timedelta(days=18),
                "status": "open",
                "opportunity_url": "https://defense-procure.example.mil/rfp/SEC-770",
                "canonical_summary": (
                    "Continuous 24/7/365 managed threat detection, containment, and reverse engineering. "
                    "Facility Security Clearance (FCL) Top Secret required. Strict US citizen on-soil requirement."
                ),
                "raw_payload": {
                    "sector": "Defense & Security",
                    "evaluation_method": "Highest Technical Score within Target Budget",
                    "mandatory_gates": ["top_secret_fcl", "us_on_soil_mandate"],
                },
            },
        ]

        return [DiscoveredOpportunity(**seed) for seed in seeds]

    async def discover(self, since: Optional[datetime] = None, limit: int = 50) -> ConnectorSyncResult:
        all_seeds = self._generate_seed_opportunities()
        selected = all_seeds[:limit]
        return ConnectorSyncResult(
            source_id=self.source_id,
            status="completed",
            items_discovered=len(selected),
            items_ingested=len(selected),
            opportunities=selected,
            completed_at=datetime.now(timezone.utc),
        )

    async def fetch_details(self, external_id: str) -> Optional[DiscoveredOpportunity]:
        for opp in self._generate_seed_opportunities():
            if opp.external_id == external_id:
                return opp
        return None

