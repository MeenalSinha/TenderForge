"""
Tender API Request and Response Schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TenderCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=512, description="Tender or RFP Title")
    reference_number: Optional[str] = Field(None, max_length=128, description="Official Tender Reference")
    issuing_authority: Optional[str] = Field(None, max_length=255, description="Procuring Entity")
    procurement_category: Optional[str] = Field(None, max_length=128, description="E.g. IT, Works, Goods")
    estimated_value: Optional[float] = Field(None, ge=0.0, description="Estimated contract budget")
    currency: str = Field("USD", max_length=8, description="Currency ISO code")
    submission_deadline: Optional[datetime] = Field(None, description="Proposal submission deadline")
    workspace_id: Optional[str] = Field(None, description="Owning workspace ID")
    document_ids: Optional[List[str]] = Field(default_factory=list, description="IDs of documents to link")


class TenderResponse(BaseModel):
    id: str
    workspace_id: str
    reference_number: Optional[str] = None
    title: str
    issuing_authority: Optional[str] = None
    procurement_category: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: str
    submission_deadline: Optional[datetime] = None
    status: str
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenderListResponse(BaseModel):
    total: int
    items: List[TenderResponse]


class TenderAnalysisRequest(BaseModel):
    force_reanalysis: bool = Field(False, description="Re-run extraction even if previously analyzed")
    categories: Optional[List[str]] = Field(None, description="Optional category filters")


class RequirementItemResponse(BaseModel):
    id: str
    category: str
    classification: str
    description: str
    source_page: Optional[int]
    source_offset: Optional[int]
    source_excerpt: str
    confidence_score: float
    human_review_status: str


class TenderAnalysisResponse(BaseModel):
    tender_id: str
    analysis_status: str
    provider: Optional[str] = None
    model: Optional[str] = None
    message: Optional[str] = None
    total_requirements: int
    requirements: List[RequirementItemResponse] = Field(default_factory=list)


class TenderRequirementsGroupedResponse(BaseModel):
    tender_id: str
    title: str
    reference_number: Optional[str]
    status: str
    total_requirements: int
    requirements_by_category: Dict[str, List[RequirementItemResponse]]

