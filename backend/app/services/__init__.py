"""Services package for TenderForge."""
from backend.app.services.document_service import DocumentService, ensure_default_workspace
from backend.app.services.document_processing_service import DocumentProcessingService
from backend.app.services.tender_service import TenderService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.prooflink_service import ProofLinkService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.proposal_service import ProposalService
from backend.app.services.audit_service import AuditService
from backend.app.services.approval_service import ApprovalService
from backend.app.services.export_service import ExportService
from backend.app.services.workflow_orchestrator import WorkflowOrchestrator
from backend.app.services.bid_decision_service import BidDecisionService
from backend.app.services.advanced_prooflink_service import AdvancedProofLinkService
from backend.app.services.evaluation_criteria_service import EvaluationCriteriaService
from backend.app.services.proposal_optimization_service import ProposalOptimizationService
from backend.app.services.financial_service import FinancialService
from backend.app.services.risk_service import RiskService
from backend.app.services.proposal_revision_service import ProposalRevisionService
from backend.app.services.portfolio_service import PortfolioService
from backend.app.services.deadline_service import DeadlineService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.opportunity_service import OpportunityService
from backend.app.services.opportunity_matching_service import OpportunityMatchingService
from backend.app.services.tender_monitoring_service import TenderMonitoringService
from backend.app.services.amendment_service import AmendmentService
from backend.app.services.market_intelligence_service import MarketIntelligenceService
from backend.app.services.bid_outcome_service import BidOutcomeService
from backend.app.services.knowledge_library_service import KnowledgeLibraryService

__all__ = [
    "DocumentService",
    "ensure_default_workspace",
    "DocumentProcessingService",
    "TenderService",
    "TenderIntelligenceService",
    "EvidenceService",
    "ProofLinkService",
    "ComplianceService",
    "ProposalService",
    "AuditService",
    "ApprovalService",
    "ExportService",
    "WorkflowOrchestrator",
    "BidDecisionService",
    "AdvancedProofLinkService",
    "EvaluationCriteriaService",
    "ProposalOptimizationService",
    "FinancialService",
    "RiskService",
    "ProposalRevisionService",
    "PortfolioService",
    "DeadlineService",
    "AnalyticsService",
    "OpportunityService",
    "OpportunityMatchingService",
    "TenderMonitoringService",
    "AmendmentService",
    "MarketIntelligenceService",
    "BidOutcomeService",
    "KnowledgeLibraryService",
]


