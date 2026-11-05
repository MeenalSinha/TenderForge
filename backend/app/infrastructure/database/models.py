"""
SQLAlchemy 2.0 Declarative Models for TenderForge.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.infrastructure.database.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")
    profile = relationship("OrganizationProfile", uselist=False, back_populates="organization", cascade="all, delete-orphan")
    evidence = relationship("CompanyEvidence", back_populates="organization", cascade="all, delete-orphan")
    contradictions = relationship("EvidenceContradiction", back_populates="organization", cascade="all, delete-orphan")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="workspaces")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    tenders = relationship("Tender", back_populates="workspace", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="workspace", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)
    mime_type = Column(String(128), nullable=False)
    file_extension = Column(String(16), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False, index=True)
    document_category = Column(String(64), default="tender_notice", nullable=False)
    processing_status = Column(String(32), default="pending", nullable=False)  # pending, parsed, failed
    parser_name = Column(String(64), nullable=True)
    parser_version = Column(String(32), nullable=True)
    ocr_required = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")
    extracted_contents = relationship("ExtractedContent", back_populates="document", cascade="all, delete-orphan")
    tender_links = relationship("TenderDocument", back_populates="document", cascade="all, delete-orphan")
    requirements = relationship("TenderRequirement", back_populates="source_document")
    evidence_records = relationship("CompanyEvidence", back_populates="document")

    __table_args__ = (
        Index("ix_documents_workspace_status", "workspace_id", "processing_status"),
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    storage_path = Column(String(512), nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    document = relationship("Document", back_populates="versions")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(64), nullable=False)  # validation, parsing, normalization, segmentation, ai_extraction
    status = Column(String(32), default="queued", nullable=False)  # queued, in_progress, completed, failed
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="processing_jobs")


class ExtractedContent(Base):
    __tablename__ = "extracted_contents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    document = relationship("Document", back_populates="extracted_contents")

    __table_args__ = (
        Index("ix_extracted_chunk_order", "document_id", "chunk_index"),
    )


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    reference_number = Column(String(128), nullable=True, index=True)
    title = Column(String(512), nullable=False)
    issuing_authority = Column(String(255), nullable=True)
    procurement_category = Column(String(128), nullable=True)
    estimated_value = Column(Float, nullable=True)
    currency = Column(String(8), default="USD", nullable=False)
    submission_deadline = Column(DateTime, nullable=True)
    status = Column(String(32), default="draft", nullable=False)  # draft, analyzing, analyzed, in_review
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="tenders")
    document_links = relationship("TenderDocument", back_populates="tender", cascade="all, delete-orphan")
    requirements = relationship("TenderRequirement", back_populates="tender", cascade="all, delete-orphan")
    extraction_results = relationship("ExtractionResult", back_populates="tender", cascade="all, delete-orphan")
    compliance_matrices = relationship("ComplianceMatrix", back_populates="tender", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="tender", cascade="all, delete-orphan")
    bid_audits = relationship("BidAudit", back_populates="tender", cascade="all, delete-orphan")
    human_approvals = relationship("HumanApproval", back_populates="tender", cascade="all, delete-orphan")
    switch_rooms = relationship("SwitchRoom", back_populates="tender", cascade="all, delete-orphan")
    workflow_state = relationship("WorkflowState", uselist=False, back_populates="tender", cascade="all, delete-orphan")
    bid_evaluations = relationship("BidEvaluation", back_populates="tender", cascade="all, delete-orphan")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="tender", cascade="all, delete-orphan")
    financial_proposals = relationship("FinancialProposal", back_populates="tender", cascade="all, delete-orphan")
    bid_risks = relationship("BidRisk", back_populates="tender", cascade="all, delete-orphan")
    deadlines = relationship("TenderDeadline", back_populates="tender", cascade="all, delete-orphan")
    claim_lineages = relationship("ClaimLineage", back_populates="tender", cascade="all, delete-orphan")


class TenderDocument(Base):
    __tablename__ = "tender_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(64), default="primary_specification", nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="document_links")
    document = relationship("Document", back_populates="tender_links")


class TenderRequirement(Base):
    __tablename__ = "tender_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    source_document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(64), nullable=False)  # eligibility, technical, financial, submission, general
    classification = Column(String(32), default="mandatory", nullable=False)  # mandatory, optional, desirable
    description = Column(Text, nullable=False)
    source_page = Column(Integer, nullable=True)
    source_offset = Column(Integer, nullable=True)
    source_excerpt = Column(Text, nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    human_review_status = Column(String(32), default="unreviewed", nullable=False)  # unreviewed, confirmed, rejected
    extra_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="requirements")
    source_document = relationship("Document", back_populates="requirements")
    evidence_links = relationship("EvidenceRequirementLink", back_populates="requirement", cascade="all, delete-orphan")
    claim_lineages = relationship("ClaimLineage", back_populates="requirement")

    __table_args__ = (
        Index("ix_requirements_tender_cat", "tender_id", "category"),
    )


class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(String(64), nullable=False)
    model_id = Column(String(128), nullable=False)
    prompt_version = Column(String(32), nullable=False)
    raw_response = Column(JSON, nullable=True)
    structured_data = Column(JSON, nullable=True)
    validation_status = Column(String(32), nullable=False)  # valid, invalid, fallback_used, ai_configuration_required
    error_message = Column(Text, nullable=True)
    execution_timestamp = Column(DateTime, default=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="extraction_results")


# ---------------------------------------------------------------------------
# Phase 2 Models: Organization Evidence, ProofLink, Compliance, Proposals,
# Audits, Human Approvals, Switch Rooms, and Workflow State
# ---------------------------------------------------------------------------

class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False)
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    registration_number = Column(String(128), nullable=False)
    tax_id = Column(String(128), nullable=False)
    jurisdiction = Column(String(128), default="United States", nullable=False)
    incorporation_date = Column(DateTime, nullable=True)
    headquarters_address = Column(String(512), nullable=True)
    primary_contact_name = Column(String(255), nullable=True)
    primary_contact_email = Column(String(255), nullable=True)
    financial_metrics = Column(JSON, nullable=True)  # e.g. {"turnover_fy23": 2500000, "turnover_fy24": 3100000, "turnover_fy25": 4200000}
    core_capabilities = Column(JSON, nullable=True)  # list of strings
    certifications = Column(JSON, nullable=True)  # list of strings e.g. ["ISO 9001:2015", "ISO 27001"]
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="profile")


class CompanyEvidence(Base):
    __tablename__ = "company_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    evidence_type = Column(String(64), nullable=False)  # financial_audit, certification, past_project, statutory_registration, policy, cv_personnel, other
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    reference_number = Column(String(128), nullable=True)
    status = Column(String(32), default="valid", nullable=False)  # valid, expired, pending_verification, revoked
    summary = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="evidence")
    document = relationship("Document", back_populates="evidence_records")
    requirement_links = relationship("EvidenceRequirementLink", back_populates="evidence", cascade="all, delete-orphan")
    claim_lineages = relationship("ClaimLineage", back_populates="evidence")

    __table_args__ = (
        Index("ix_company_evidence_org_type", "organization_id", "evidence_type"),
    )


class EvidenceRequirementLink(Base):
    __tablename__ = "evidence_requirement_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    requirement_id = Column(String(36), ForeignKey("tender_requirements.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("company_evidence.id", ondelete="CASCADE"), nullable=False)
    match_status = Column(String(32), default="Pending", nullable=False)  # Verified, Human Confirmed, Pending, Unsupported, Contradicted
    confidence_score = Column(Float, default=1.0, nullable=False)
    source_excerpt = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    verified_by_user_id = Column(String(128), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    requirement = relationship("TenderRequirement", back_populates="evidence_links")
    evidence = relationship("CompanyEvidence", back_populates="requirement_links")

    __table_args__ = (
        Index("ix_evidence_req_link", "requirement_id", "evidence_id"),
    )


class ComplianceMatrix(Base):
    __tablename__ = "compliance_matrices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    overall_status = Column(String(32), default="Pending", nullable=False)  # Compliant, Partially Compliant, Non-Compliant, Clarification Required
    overall_risk_level = Column(String(32), default="Medium", nullable=False)  # Low, Medium, High, Critical
    evaluated_by_agent = Column(String(128), default="ComplianceOfficer", nullable=False)
    summary = Column(Text, nullable=False)
    items = Column(JSON, nullable=False)  # list of evaluated requirements with status, risk, notes
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="compliance_matrices")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(512), nullable=False)
    current_version = Column(Integer, default=1, nullable=False)
    status = Column(String(32), default="drafting", nullable=False)  # drafting, auditing, pending_human_review, approved, rejected
    executive_summary = Column(Text, nullable=True)
    docx_file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="proposals")
    sections = relationship("ProposalSection", back_populates="proposal", cascade="all, delete-orphan")
    revisions = relationship("ProposalRevision", back_populates="proposal", cascade="all, delete-orphan")
    audits = relationship("BidAudit", back_populates="proposal", cascade="all, delete-orphan")
    optimizations = relationship("ProposalOptimization", back_populates="proposal", cascade="all, delete-orphan")
    quality_checks = relationship("ProposalQualityCheck", back_populates="proposal", cascade="all, delete-orphan")
    claim_lineages = relationship("ClaimLineage", back_populates="proposal", cascade="all, delete-orphan")
    financial_proposals = relationship("FinancialProposal", back_populates="proposal")


class ProposalSection(Base):
    __tablename__ = "proposal_sections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    section_number = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    claims = Column(JSON, nullable=True)  # list of factual claims with text, status, prooflink_citation
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    proposal = relationship("Proposal", back_populates="sections")


class ProposalRevision(Base):
    __tablename__ = "proposal_revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    author_type = Column(String(32), default="agent", nullable=False)  # agent, human
    author_id = Column(String(128), nullable=False)
    change_summary = Column(String(512), nullable=False)
    snapshot = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    proposal = relationship("Proposal", back_populates="revisions")


class BidAudit(Base):
    __tablename__ = "bid_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    auditor_type = Column(String(32), default="agent", nullable=False)  # agent, human
    auditor_id = Column(String(128), default="BidAuditor", nullable=False)
    readiness_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    verdict = Column(String(64), nullable=False)  # Ready for Submission, Conditional Approval Required, Submission Blocked - High Risk
    total_claims = Column(Integer, default=0, nullable=False)
    verified_claims = Column(Integer, default=0, nullable=False)
    unsupported_claims = Column(Integer, default=0, nullable=False)
    contradicted_claims = Column(Integer, default=0, nullable=False)
    findings = Column(JSON, nullable=False)  # list of findings with severity, category, description, recommendation
    created_at = Column(DateTime, default=utcnow, nullable=False)

    proposal = relationship("Proposal", back_populates="audits")
    tender = relationship("Tender", back_populates="bid_audits")


class HumanApproval(Base):
    __tablename__ = "human_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=True)
    audit_id = Column(String(36), ForeignKey("bid_audits.id", ondelete="CASCADE"), nullable=True)
    decision = Column(String(32), nullable=False)  # Approved, Rejected, Changes Requested
    user_id = Column(String(128), nullable=False)
    user_name = Column(String(255), nullable=False)
    user_role = Column(String(128), nullable=False)
    comments = Column(Text, nullable=False)
    signature_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="human_approvals")


class SwitchRoom(Base):
    __tablename__ = "switch_rooms"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    room_name = Column(String(255), nullable=False)
    channel_id = Column(String(128), nullable=False)
    channel_type = Column(String(32), default="mattermost", nullable=False)  # mattermost, slack, teams, web_mock
    status = Column(String(32), default="active", nullable=False)  # active, archived
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="switch_rooms")


class WorkflowState(Base):
    __tablename__ = "workflow_states"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_stage = Column(String(64), default="WORKSPACE_INITIALIZED", nullable=False)
    stage_history = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="workflow_state")


# ---------------------------------------------------------------------------
# Phase 3 Models: Bid Intelligence, Advanced ProofLink, Financial Workspace,
# Evaluation Criteria, Proposal Optimization, Bid Risks, Deadlines, and RBAC
# ---------------------------------------------------------------------------

class BidEvaluation(Base):
    __tablename__ = "bid_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    evaluator_type = Column(String(32), default="agent", nullable=False)  # agent, human
    evaluator_id = Column(String(128), default="BidIntelligenceEngine", nullable=False)
    dimensions = Column(JSON, nullable=False)  # dimension scores, weights, reasonings
    overall_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    eligibility_gates_passed = Column(Boolean, default=True, nullable=False)
    failed_gates = Column(JSON, default=list, nullable=False)
    recommendation = Column(String(64), nullable=False)  # BID, BID WITH CONDITIONS, NO-BID RECOMMENDED
    conditions = Column(JSON, default=list, nullable=False)
    executive_summary = Column(Text, nullable=False)
    human_decision = Column(String(32), default="PENDING", nullable=False)  # PENDING, APPROVED_BID, APPROVED_NO_BID, OVERRIDDEN
    human_decision_by = Column(String(128), nullable=True)
    human_decision_rationale = Column(Text, nullable=True)
    human_decision_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="bid_evaluations")


class EvidenceContradiction(Base):
    __tablename__ = "evidence_contradictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    evidence_id_1 = Column(String(36), ForeignKey("company_evidence.id", ondelete="CASCADE"), nullable=False)
    evidence_id_2 = Column(String(36), ForeignKey("company_evidence.id", ondelete="SET NULL"), nullable=True)
    claim_field = Column(String(128), nullable=False)
    value_1 = Column(Text, nullable=False)
    value_2 = Column(Text, nullable=False)
    contradiction_severity = Column(String(32), default="High", nullable=False)  # Critical, High, Medium, Low
    status = Column(String(32), default="Open", nullable=False)  # Open, Investigating, Resolved, Dismissed
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(128), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="contradictions")
    evidence_1 = relationship("CompanyEvidence", foreign_keys=[evidence_id_1])
    evidence_2 = relationship("CompanyEvidence", foreign_keys=[evidence_id_2])


class ClaimLineage(Base):
    __tablename__ = "claim_lineages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=True)
    requirement_id = Column(String(36), ForeignKey("tender_requirements.id", ondelete="SET NULL"), nullable=True)
    evidence_id = Column(String(36), ForeignKey("company_evidence.id", ondelete="SET NULL"), nullable=True)
    section_number = Column(String(32), nullable=True)
    claim_text = Column(Text, nullable=False)
    evidence_extract = Column(Text, nullable=False)
    review_status = Column(String(32), default="unreviewed", nullable=False)  # unreviewed, audited, verified, rejected
    auditor_verdict = Column(String(64), nullable=True)
    approval_status = Column(String(32), default="pending", nullable=False)  # pending, approved, invalidated
    lineage_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="claim_lineages")
    proposal = relationship("Proposal", back_populates="claim_lineages")
    requirement = relationship("TenderRequirement", back_populates="claim_lineages")
    evidence = relationship("CompanyEvidence", back_populates="claim_lineages")

    __table_args__ = (
        Index("ix_claim_lineage_tender_req", "tender_id", "requirement_id"),
    )


class EvaluationCriteria(Base):
    __tablename__ = "evaluation_criteria"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    criterion_code = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False)  # Technical, Financial, Past Performance, Management, Compliance
    weight_percentage = Column(Float, default=0.0, nullable=False)
    max_marks = Column(Float, default=100.0, nullable=False)
    description = Column(Text, nullable=False)
    scoring_rules = Column(JSON, default=dict, nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="evaluation_criteria")
    optimizations = relationship("ProposalOptimization", back_populates="criterion", cascade="all, delete-orphan")


class ProposalOptimization(Base):
    __tablename__ = "proposal_optimizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(String(36), ForeignKey("evaluation_criteria.id", ondelete="SET NULL"), nullable=True)
    section_number = Column(String(32), nullable=True)
    coverage_status = Column(String(32), default="Partial", nullable=False)  # Complete, Partial, Missing, Weak
    gap_analysis = Column(Text, nullable=False)
    current_score_estimate = Column(Float, default=0.0, nullable=False)
    potential_score_estimate = Column(Float, default=0.0, nullable=False)
    before_text = Column(Text, nullable=True)
    after_text = Column(Text, nullable=True)
    improvement_rationale = Column(Text, nullable=False)
    status = Column(String(32), default="Proposed", nullable=False)  # Proposed, Accepted, Rejected, Applied
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    proposal = relationship("Proposal", back_populates="optimizations")
    criterion = relationship("EvaluationCriteria", back_populates="optimizations")


class FinancialProposal(Base):
    __tablename__ = "financial_proposals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), default="Pricing Schedule", nullable=False)
    currency = Column(String(8), default="USD", nullable=False)
    subtotal = Column(String(32), default="0.00", nullable=False)
    tax_rate_percent = Column(String(16), default="0.00", nullable=False)
    tax_amount = Column(String(32), default="0.00", nullable=False)
    contingency_rate_percent = Column(String(16), default="0.00", nullable=False)
    contingency_amount = Column(String(32), default="0.00", nullable=False)
    overhead_rate_percent = Column(String(16), default="0.00", nullable=False)
    overhead_amount = Column(String(32), default="0.00", nullable=False)
    margin_rate_percent = Column(String(16), default="0.00", nullable=False)
    margin_amount = Column(String(32), default="0.00", nullable=False)
    total_price = Column(String(32), default="0.00", nullable=False)
    status = Column(String(32), default="Draft", nullable=False)  # Draft, In_Review, Approved, Locked
    validation_errors = Column(JSON, default=list, nullable=True)
    assumptions = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="financial_proposals")
    proposal = relationship("Proposal", back_populates="financial_proposals")
    line_items = relationship("FinancialLineItem", back_populates="financial_proposal", cascade="all, delete-orphan")
    scenarios = relationship("FinancialScenario", back_populates="financial_proposal", cascade="all, delete-orphan")


class FinancialLineItem(Base):
    __tablename__ = "financial_line_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    financial_proposal_id = Column(String(36), ForeignKey("financial_proposals.id", ondelete="CASCADE"), nullable=False)
    item_code = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), default="Services", nullable=False)  # Labor, Hardware, Software, Services, Travel, Contingency
    unit = Column(String(32), default="each", nullable=False)
    quantity = Column(String(32), default="1.00", nullable=False)
    unit_rate = Column(String(32), default="0.00", nullable=False)
    tax_percent = Column(String(16), default="0.00", nullable=False)
    line_total = Column(String(32), default="0.00", nullable=False)
    notes = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    financial_proposal = relationship("FinancialProposal", back_populates="line_items")


class FinancialScenario(Base):
    __tablename__ = "financial_scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    financial_proposal_id = Column(String(36), ForeignKey("financial_proposals.id", ondelete="CASCADE"), nullable=False)
    scenario_name = Column(String(64), nullable=False)  # Base Case, Conservative, Aggressive
    margin_rate_percent = Column(String(16), nullable=False)
    contingency_rate_percent = Column(String(16), nullable=False)
    discount_percent = Column(String(16), default="0.00", nullable=False)
    calculated_total = Column(String(32), nullable=False)
    summary_metrics = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    financial_proposal = relationship("FinancialProposal", back_populates="scenarios")


class BidRisk(Base):
    __tablename__ = "bid_risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False)  # Compliance, Evidence, Financial, Timeline, Legal_Commercial, Technical
    likelihood = Column(Integer, default=1, nullable=False)  # 1 to 5
    impact = Column(Integer, default=1, nullable=False)      # 1 to 5
    severity_score = Column(Integer, default=1, nullable=False)  # 1 to 25
    risk_level = Column(String(32), default="Low", nullable=False)  # Low, Medium, High
    description = Column(Text, nullable=False)
    consequences = Column(Text, nullable=True)
    mitigation_strategy = Column(Text, nullable=False)
    contingency_plan = Column(Text, nullable=True)
    owner = Column(String(128), default="Bid Manager", nullable=False)
    status = Column(String(32), default="Open", nullable=False)  # Open, In_Progress, Mitigated, Accepted
    source_module = Column(String(64), default="compliance", nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="bid_risks")

    __table_args__ = (
        Index("ix_bid_risks_tender_sev", "tender_id", "severity_score"),
    )


class ProposalQualityCheck(Base):
    __tablename__ = "proposal_quality_checks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    checked_by = Column(String(128), default="QualityAuditor", nullable=False)
    formatting_score = Column(Float, default=100.0, nullable=False)
    placeholder_count = Column(Integer, default=0, nullable=False)
    placeholders_found = Column(JSON, default=list, nullable=False)
    broken_references_count = Column(Integer, default=0, nullable=False)
    citations_verified_count = Column(Integer, default=0, nullable=False)
    citations_missing_count = Column(Integer, default=0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    page_count_estimate = Column(Integer, default=0, nullable=False)
    issues = Column(JSON, default=list, nullable=False)
    passed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    proposal = relationship("Proposal", back_populates="quality_checks")


class TenderDeadline(Base):
    __tablename__ = "tender_deadlines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    deadline_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    deadline_date = Column(DateTime, nullable=False)
    timezone_name = Column(String(64), default="UTC", nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    status = Column(String(32), default="Upcoming", nullable=False)  # Upcoming, Approaching, Completed, Missed
    reminder_intervals_hours = Column(JSON, default=list, nullable=False)
    last_notification_sent_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    tender = relationship("Tender", back_populates="deadlines")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(128), nullable=False)
    user_name = Column(String(255), nullable=False)
    role = Column(String(64), default="Viewer", nullable=False)  # Viewer, Author, Reviewer, Approver, Admin
    created_at = Column(DateTime, default=utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="user_roles")

    __table_args__ = (
        Index("ix_user_roles_ws_user", "workspace_id", "user_id"),
    )



