"""
Tool execution handlers with Role-Based Access Control for TenderForge Switch Agents.
"""

from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, SecurityError
from backend.app.core.logging import get_logger
from backend.app.domain.agents.registry import agent_registry
from backend.app.infrastructure.database.models import (
    BidAudit,
    ComplianceMatrix,
    Document,
    HumanApproval,
    Organization,
    OrganizationProfile,
    Proposal,
    ProposalSection,
    Tender,
    TenderRequirement,
    Workspace,
)
from backend.app.services.approval_service import ApprovalService
from backend.app.services.audit_service import AuditService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.document_service import DocumentService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.export_service import ExportService
from backend.app.services.prooflink_service import ProofLinkService
from backend.app.services.proposal_service import ProposalService
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService

logger = get_logger("tool_handlers")


class ToolDispatcher:
    """Dispatches tool calls with strict agent role permission checks."""

    def __init__(self):
        self.doc_service = DocumentService()
        self.tender_service = TenderService()
        self.intel_service = TenderIntelligenceService()
        self.evidence_service = EvidenceService()
        self.prooflink_service = ProofLinkService()
        self.compliance_service = ComplianceService()
        self.proposal_service = ProposalService()
        self.audit_service = AuditService()
        self.approval_service = ApprovalService()
        self.export_service = ExportService()

    def execute(
        self,
        db: Session,
        tool_name: str,
        arguments: Dict[str, Any],
        caller_id: str,
        caller_type: str = "agent",
    ) -> Dict[str, Any]:
        """Validate permissions and execute the requested tool."""
        logger.info(f"Dispatching tool '{tool_name}' by {caller_type} '{caller_id}'")

        # 1. RBAC Guardrail check for agents
        if caller_type == "agent":
            # Human-only tools cannot be invoked by agents
            if tool_name in ("record_human_decision",):
                raise SecurityError(f"Agent '{caller_id}' is strictly forbidden from executing human governance tool '{tool_name}'.")

            if not agent_registry.is_tool_permitted(caller_id, tool_name):
                raise SecurityError(f"Permission denied: Agent '{caller_id}' is not authorized to invoke tool '{tool_name}'.")

        # 2. Tool routing
        handler_method = getattr(self, f"_tool_{tool_name}", None)
        if not handler_method:
            raise NotImplementedError(f"Tool '{tool_name}' is not recognized.")

        return handler_method(db, arguments, caller_id)

    # -----------------------------------------------------------------------
    # Tool Implementations
    # -----------------------------------------------------------------------

    def _tool_create_tender_workspace(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        ws = Workspace(
            name=args["name"],
            organization_id=args["organization_id"],
            description=args.get("description"),
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)
        return {"status": "success", "workspace_id": ws.id, "name": ws.name}

    def _tool_upload_tender_document(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        content_raw = args["content_base64"]
        try:
            content_bytes = base64.b64decode(content_raw)
        except Exception:
            content_bytes = content_raw.encode("utf-8")

        doc = self.doc_service.register_document(
            db=db,
            workspace_id=args["workspace_id"],
            filename=args["filename"],
            content=content_bytes,
            document_category=args.get("category", "tender_notice"),
        )
        return {"status": "success", "document_id": doc.id, "filename": doc.original_filename, "size": len(content_bytes)}

    def _tool_upload_company_evidence(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        content_raw = args["content_base64"]
        try:
            content_bytes = base64.b64decode(content_raw)
        except Exception:
            content_bytes = content_raw.encode("utf-8")

        ev = self.evidence_service.upload_and_ingest_evidence_file(
            db=db,
            organization_id=args["organization_id"],
            workspace_id=args["workspace_id"],
            filename=args["filename"],
            content=content_bytes,
            evidence_type=args["evidence_type"],
            title=args["title"],
            issuer=args.get("issuer"),
            reference_number=args.get("reference_number"),
            tags=args.get("tags"),
        )
        return {"status": "success", "evidence_id": ev.id, "title": ev.title, "evidence_type": ev.evidence_type}

    def _tool_get_tender_overview(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        tender = self.tender_service.get_tender(db, args["tender_id"])
        docs = [d.original_filename for d in tender.documents] if hasattr(tender, "documents") else []
        return {
            "status": "success",
            "tender_id": tender.id,
            "title": tender.title,
            "reference_number": tender.reference_number,
            "issuing_authority": tender.issuing_authority,
            "tender_status": tender.status,
            "documents": docs,
        }

    def _tool_analyze_tender(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        result = self.intel_service.analyze_tender_sync(args["tender_id"], db)
        return {"status": "success", "result": result}

    def _tool_get_tender_requirements(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        reqs = self.tender_service.list_requirements(
            db=db,
            tender_id=args["tender_id"],
            category=args.get("category"),
            classification=args.get("classification"),
        )
        return {
            "status": "success",
            "count": len(reqs),
            "requirements": [
                {
                    "id": r.id,
                    "category": r.category,
                    "classification": r.classification,
                    "description": r.description,
                    "source_page": r.source_page,
                    "source_excerpt": r.source_excerpt,
                    "confidence": r.confidence_score,
                }
                for r in reqs
            ]
        }

    def _tool_search_company_evidence(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        results = self.evidence_service.search_evidence(
            db=db,
            organization_id=args["organization_id"],
            query=args.get("query"),
            evidence_type=args.get("evidence_type"),
        )
        return {
            "status": "success",
            "count": len(results),
            "evidence": [
                {
                    "id": e.id,
                    "title": e.title,
                    "evidence_type": e.evidence_type,
                    "issuer": e.issuer,
                    "status": e.status,
                    "summary": e.summary,
                    "tags": e.tags,
                }
                for e in results
            ]
        }

    def _tool_get_evidence_details(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        ev = self.evidence_service.get_evidence(db, args["evidence_id"])
        if not ev:
            raise EntityNotFoundError(f"Evidence '{args['evidence_id']}' not found.")
        return {
            "status": "success",
            "evidence_id": ev.id,
            "title": ev.title,
            "evidence_type": ev.evidence_type,
            "issuer": ev.issuer,
            "reference_number": ev.reference_number,
            "status": ev.status,
            "summary": ev.summary,
            "extracted_data": ev.extracted_data,
        }

    def _tool_evaluate_compliance(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        matrix = self.compliance_service.evaluate_tender_compliance(
            db=db,
            tender_id=args["tender_id"],
            evaluator_agent=caller_id,
        )
        return {
            "status": "success",
            "matrix_id": matrix.id,
            "overall_status": matrix.overall_status,
            "overall_risk_level": matrix.overall_risk_level,
            "summary": matrix.summary,
            "items_count": len(matrix.items),
        }

    def _tool_get_compliance_matrix(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        matrix = self.compliance_service.get_latest_matrix(db, args["tender_id"])
        if not matrix:
            raise EntityNotFoundError(f"No compliance matrix found for tender '{args['tender_id']}'.")
        return {
            "status": "success",
            "matrix_id": matrix.id,
            "overall_status": matrix.overall_status,
            "overall_risk_level": matrix.overall_risk_level,
            "summary": matrix.summary,
            "items": matrix.items,
        }

    def _tool_create_proposal_draft(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        proposal = self.proposal_service.create_proposal_draft(
            db=db,
            tender_id=args["tender_id"],
            title=args.get("title"),
            author_id=caller_id,
        )
        return {
            "status": "success",
            "proposal_id": proposal.id,
            "title": proposal.title,
            "version": proposal.current_version,
            "status": proposal.status,
            "docx_path": proposal.docx_file_path,
        }

    def _tool_get_proposal_revision(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        proposal = self.proposal_service.get_proposal(db, args["proposal_id"])
        if not proposal:
            raise EntityNotFoundError(f"Proposal '{args['proposal_id']}' not found.")
        sections = [
            {"number": s.section_number, "title": s.title, "content": s.content, "claims": s.claims}
            for s in proposal.sections
        ]
        return {
            "status": "success",
            "proposal_id": proposal.id,
            "version": proposal.current_version,
            "status": proposal.status,
            "sections": sections,
        }

    def _tool_audit_proposal(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        audit = self.audit_service.audit_proposal(
            db=db,
            proposal_id=args["proposal_id"],
            auditor_id=caller_id,
        )
        return {
            "status": "success",
            "audit_id": audit.id,
            "readiness_score": audit.readiness_score,
            "verdict": audit.verdict,
            "findings_count": len(audit.findings),
            "findings": audit.findings,
        }

    def _tool_get_audit_report(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        audit = self.audit_service.get_latest_audit(db, args["proposal_id"])
        if not audit:
            raise EntityNotFoundError(f"No audit found for proposal '{args['proposal_id']}'.")
        return {
            "status": "success",
            "audit_id": audit.id,
            "readiness_score": audit.readiness_score,
            "verdict": audit.verdict,
            "total_claims": audit.total_claims,
            "verified_claims": audit.verified_claims,
            "unsupported_claims": audit.unsupported_claims,
            "contradicted_claims": audit.contradicted_claims,
            "findings": audit.findings,
        }

    def _tool_request_human_review(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        # Formulate review request
        return {
            "status": "success",
            "tender_id": args["tender_id"],
            "requested_by": caller_id,
            "reason": args["reason"],
            "severity": args.get("severity", "Major"),
            "action": "Human review request broadcasted to Tender War Room.",
        }

    def _tool_record_human_decision(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        approval = self.approval_service.record_decision(
            db=db,
            tender_id=args["tender_id"],
            proposal_id=args["proposal_id"],
            user_id=args["user_id"],
            user_name=args["user_name"],
            user_role=args["user_role"],
            decision=args["decision"],
            comments=args["comments"],
        )
        return {
            "status": "success",
            "approval_id": approval.id,
            "decision": approval.decision,
            "signature_hash": approval.signature_hash,
            "timestamp": approval.created_at.isoformat(),
        }

    def _tool_export_bid_package(self, db: Session, args: Dict[str, Any], caller_id: str) -> Dict[str, Any]:
        zip_path = self.export_service.export_bid_package(
            db=db,
            tender_id=args["tender_id"],
            proposal_id=args["proposal_id"],
            require_human_approval=args.get("require_human_approval", True),
        )
        return {
            "status": "success",
            "package_path": zip_path,
            "filename": str(zip_path).split("\\")[-1].split("/")[-1],
        }


# Global tool dispatcher
tool_dispatcher = ToolDispatcher()
