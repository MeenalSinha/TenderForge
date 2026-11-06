"""
Procurement Connector Registry and Factory.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type
from backend.app.integrations.procurement.base_connector import BaseProcurementConnector
from backend.app.integrations.procurement.manual_connector import ManualImportConnector
from backend.app.integrations.procurement.open_tender_connector import OpenTenderApiConnector
from backend.app.integrations.procurement.mock_sandbox_connector import MockSandboxConnector


class ConnectorRegistry:
    """Registry maintaining available connector classes and constructing instances."""

    _connectors: Dict[str, Type[BaseProcurementConnector]] = {
        "manual_import": ManualImportConnector,
        "open_contracting": OpenTenderApiConnector,
        "government_portal": OpenTenderApiConnector,
        "mock_sandbox": MockSandboxConnector,
    }

    @classmethod
    def register(cls, connector_type: str, connector_cls: Type[BaseProcurementConnector]) -> None:
        cls._connectors[connector_type] = connector_cls

    @classmethod
    def get_connector(
        cls,
        source_id: str,
        connector_type: str,
        config: Dict[str, Any],
        security_config: Optional[Dict[str, Any]] = None,
    ) -> BaseProcurementConnector:
        connector_cls = cls._connectors.get(connector_type)
        if not connector_cls:
            # Fallback to mock_sandbox if unrecognized or for offline testing
            connector_cls = MockSandboxConnector
        return connector_cls(source_id=source_id, config=config, security_config=security_config)

    @classmethod
    def list_available_types(cls) -> list[str]:
        return list(cls._connectors.keys())

