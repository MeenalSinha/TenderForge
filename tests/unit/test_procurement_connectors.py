"""
Unit tests for Procurement Connectors, SSRF validation, and Connector Registry.
"""

import pytest
from datetime import datetime, timezone
from backend.app.integrations.procurement.base_connector import BaseProcurementConnector, DiscoveredOpportunity
from backend.app.integrations.procurement.manual_connector import ManualImportConnector
from backend.app.integrations.procurement.open_tender_connector import OpenTenderApiConnector
from backend.app.integrations.procurement.mock_sandbox_connector import MockSandboxConnector
from backend.app.integrations.procurement.connector_registry import ConnectorRegistry


def test_ssrf_protection_blocks_internal_ips():
    """Verify that private IP ranges and loopback are blocked."""
    connector = OpenTenderApiConnector(
        source_id="src-test-01",
        config={"endpoint_url": "https://127.0.0.1/api"},
        security_config={"blocked_hostnames": ["127.0.0.1", "localhost"], "allow_insecure_http": False},
    )
    with pytest.raises(ValueError, match="SSRF Security Violation"):
        connector.validate_security("https://127.0.0.1/releases")


def test_ssrf_protection_blocks_insecure_http():
    """Verify that plain HTTP is blocked unless explicitly enabled."""
    connector = OpenTenderApiConnector(
        source_id="src-test-02",
        config={"endpoint_url": "http://api.example.com/notices"},
        security_config={"allow_insecure_http": False},
    )
    with pytest.raises(ValueError, match="Insecure HTTP connections are prohibited"):
        connector.validate_security("http://api.example.com/notices")


def test_manual_connector_json_parsing():
    """Verify manual connector parses structured JSON batch."""
    connector = ManualImportConnector(source_id="src-manual-01", config={})
    sample_json = '''
    [
        {
            "external_id": "TND-9901",
            "title": "Cloud Computing Strategy & Migration",
            "buyer_name": "Department of Energy",
            "procurement_category": "information_technology",
            "estimated_budget": 3500000.0,
            "currency": "USD"
        }
    ]
    '''
    opps = connector.parse_payload_data(sample_json, format_type="json")
    assert len(opps) == 1
    assert opps[0].external_id == "TND-9901"
    assert opps[0].title == "Cloud Computing Strategy & Migration"
    assert opps[0].estimated_budget == 3500000.0


def test_manual_connector_csv_parsing():
    """Verify manual connector parses CSV tables."""
    connector = ManualImportConnector(source_id="src-manual-02", config={})
    sample_csv = "external_id,title,buyer_name,estimated_budget\nTND-8822,Hospital Network Infrastructure,Health Dept,4200000"
    opps = connector.parse_payload_data(sample_csv, format_type="csv")
    assert len(opps) == 1
    assert opps[0].external_id == "TND-8822"
    assert opps[0].buyer_name == "Health Dept"
    assert opps[0].estimated_budget == 4200000.0


def test_mock_sandbox_connector_discover():
    """Verify mock sandbox connector generates deterministic opportunities."""
    from tests.helpers import run_sync
    connector = MockSandboxConnector(source_id="src-sandbox-01", config={})
    result = run_sync(connector.discover(limit=3))
    assert result.status == "completed"
    assert result.items_discovered == 3
    assert len(result.opportunities) == 3
    assert result.opportunities[0].external_id.startswith("TND-2026")


def test_connector_registry():
    """Verify connector factory registry looks up and instantiates connectors."""
    types = ConnectorRegistry.list_available_types()
    assert "manual_import" in types
    assert "open_contracting" in types
    assert "mock_sandbox" in types

    instance = ConnectorRegistry.get_connector("s1", "mock_sandbox", {})
    assert isinstance(instance, MockSandboxConnector)
