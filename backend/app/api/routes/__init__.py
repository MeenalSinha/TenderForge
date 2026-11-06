"""API routes package for TenderForge."""
from backend.app.api.routes.compliance import router as compliance_router
from backend.app.api.routes.documents import router as documents_router
from backend.app.api.routes.evidence import router as evidence_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.prooflink import router as prooflink_router
from backend.app.api.routes.proposals import router as proposals_router
from backend.app.api.routes.switch import router as switch_router
from backend.app.api.routes.tenders import router as tenders_router
from backend.app.api.routes.workflow import router as workflow_router
from backend.app.api.routes.bid_decision import router as bid_decision_router
from backend.app.api.routes.financial import router as financial_router
from backend.app.api.routes.portfolio import router as portfolio_router
from backend.app.api.routes.risks import router as risks_router
from backend.app.api.routes.deadlines import router as deadlines_router
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.optimizations import router as optimizations_router
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.organizations import router as organizations_router
from backend.app.api.routes.procurement_sources import router as sources_router
from backend.app.api.routes.opportunities import router as opportunities_router
from backend.app.api.routes.monitoring import router as monitoring_router
from backend.app.api.routes.market import router as market_router
from backend.app.api.routes.bid_outcomes import router as bid_outcomes_router
from backend.app.api.routes.knowledge import router as knowledge_router

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
    "bid_decision_router",
    "financial_router",
    "portfolio_router",
    "risks_router",
    "deadlines_router",
    "analytics_router",
    "optimizations_router",
    "auth_router",
    "organizations_router",
    "sources_router",
    "opportunities_router",
    "monitoring_router",
    "market_router",
    "bid_outcomes_router",
    "knowledge_router",
]
