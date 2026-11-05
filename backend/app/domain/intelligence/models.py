"""
Pydantic Schemas for Structured Tender Intelligence.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TenderGeneralInfo(BaseModel):
    """General metadata identified in the tender document."""

    title: Optional[str] = Field(None, description="Official title of the tender or RFP")
    reference_number: Optional[str] = Field(None, description="Tender notice or reference ID")
    issuing_authority: Optional[str] = Field(None, description="Issuing government agency or corporation")
    procurement_category: Optional[str] = Field(None, description="Category (Goods, Services, Works, IT)")
    description: Optional[str] = Field(None, description="High-level description of scope")
    estimated_value: Optional[float] = Field(None, description="Estimated contract value if specified")
    currency: Optional[str] = Field("USD", description="Currency code (USD, EUR, INR, GBP, etc.)")
    submission_deadline: Optional[datetime] = Field(None, description="Final submission deadline")


class ExtractedRequirement(BaseModel):
    """An individual tender requirement grounded in source evidence."""

    category: str = Field(
        ...,
        description="Category: eligibility, technical, financial, submission, general",
    )
    classification: str = Field(
        "mandatory",
        description="Classification: mandatory, optional, desirable",
    )
    description: str = Field(..., description="Actionable statement of the requirement")
    source_page: Optional[int] = Field(None, description="Source page number where clause appears")
    source_offset: Optional[int] = Field(None, description="Character offset in source text")
    source_excerpt: str = Field(
        ...,
        description="Exact verbatim quotation from the tender text backing this requirement",
    )
    confidence_score: float = Field(
        1.0, ge=0.0, le=1.0, description="Model extraction confidence score"
    )
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class StructuredTenderIntelligence(BaseModel):
    """Complete validated extraction payload."""

    schema_version: str = "1.0.0"
    general_info: TenderGeneralInfo
    requirements: List[ExtractedRequirement] = Field(default_factory=list)

