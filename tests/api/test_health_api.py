"""
API Tests: Health, Readiness and Diagnostic Endpoints.
"""

from sqlalchemy.orm import Session
from backend.app.api.routes.health import health_check, readiness_check, system_diagnostics


def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert data["app_name"] == "TenderForge"
    assert "version" in data
    assert "timestamp" in data


def test_ready_endpoint(db_session: Session):
    resp = readiness_check(db=db_session)
    assert resp.status_code == 200
    import json
    data = json.loads(resp.body.decode())
    assert data["status"] == "ready"
    assert data["checks"]["database"] == "connected"
    assert "healthy" in data["checks"]["storage"]


def test_diagnostics_endpoint(db_session: Session):
    data = system_diagnostics(db=db_session)
    assert data["system"]["app_name"] == "TenderForge"
    assert data["database"]["status"] == "connected"
    assert "storage" in data
    assert "security" in data
    assert "integrations" in data

