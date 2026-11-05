"""API routes package."""
from backend.app.api.routes.compliance import router as compliance_router
from backend.app.api.routes.documents import router as documents_router
from backend.app.api.routes.evidence import router as evidence_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.prooflink import router as prooflink_router
from backend.app.api.routes.proposals import router as proposals_router
from backend.app.api.routes.switch import router as switch_router
from backend.app.api.routes.tenders import router as tenders_router
from backend.app.api.routes.workflow import router as workflow_router

__all__ = [
    "health_router",
    "documents_router",
    "tenders_router",
    "evidence_router",
    "prooflink_router",
    "compliance_router",
    "proposals_router",
    "switch_router",
    "workflow_router",
]
