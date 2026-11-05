"""
Document API Request and Response Schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    workspace_id: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    file_extension: str
    checksum_sha256: str
    document_category: str
    processing_status: str
    parser_name: Optional[str] = None
    parser_version: Optional[str] = None
    ocr_required: bool = False
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]


class ChunkResponse(BaseModel):
    chunk_index: int
    page_number: Optional[int]
    start_char: Optional[int]
    end_char: Optional[int]
    section_title: Optional[str]
    content: str


class DocumentContentResponse(BaseModel):
    document_id: str
    filename: str
    processing_status: str
    ocr_required: bool
    total_chunks: int
    chunks: List[ChunkResponse]


class ProcessingJobResponse(BaseModel):
    id: str
    stage: str
    status: str
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]
    started_at: Optional[str]
    completed_at: Optional[str]


class DocumentStatusResponse(BaseModel):
    document_id: str
    processing_status: str
    error_message: Optional[str]
    ocr_required: bool
    jobs: List[ProcessingJobResponse]

