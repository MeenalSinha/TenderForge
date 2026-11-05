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

