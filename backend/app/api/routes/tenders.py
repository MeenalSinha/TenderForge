"""
Tender Management & Intelligence REST Endpoints.
"""

from __future__ import annotations

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.dependencies import (
    get_db,
    get_intelligence_service,
    get_tndr_service,
)
from backend.app.api.schemas.common import ResponseEnvelope
from backend.app.api.schemas.tender import (
    TenderAnalysisRequest,
    TenderAnalysisResponse,
    TenderCreateRequest,
    TenderListResponse,
    TenderRequirementsGroupedResponse,
    TenderResponse,
)
from backend.app.core.logging import correlation_id_ctx
from backend.app.services.tender_intelligence_service import TenderIntelligenceService
from backend.app.services.tender_service import TenderService

router = APIRouter(prefix="/tenders", tags=["Tenders"])


@router.post(
    "",
    response_model=ResponseEnvelope[TenderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a tender opportunity and optionally link documents",
)
def create_tender(
    payload: TenderCreateRequest,
    db: Session = Depends(get_db),
    service: TenderService = Depends(get_tndr_service),
) -> ResponseEnvelope[TenderResponse]:
    tender = service.create_tender(
        title=payload.title,
        reference_number=payload.reference_number,
        issuing_authority=payload.issuing_authority,
        procurement_category=payload.procurement_category,
        estimated_value=payload.estimated_value,
        currency=payload.currency,
        submission_deadline=payload.submission_deadline,
        workspace_id=payload.workspace_id,
        document_ids=payload.document_ids,
        db=db,
    )

    return ResponseEnvelope[TenderResponse](
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="Tender registered successfully.",
        data=TenderResponse.model_validate(tender),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "",
    response_model=ResponseEnvelope[TenderListResponse],
    summary="List tenders with pagination",
)
def list_tenders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workspace_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    service: TenderService = Depends(get_tndr_service),
) -> ResponseEnvelope[TenderListResponse]:
    tenders, total = service.list_tenders(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
    )

    return ResponseEnvelope[TenderListResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Tenders retrieved successfully.",
        data=TenderListResponse(
            total=total,
            items=[TenderResponse.model_validate(t) for t in tenders],
        ),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{tender_id}",
    response_model=ResponseEnvelope[TenderResponse],
    summary="Retrieve single tender details",
)
def get_tender(
    tender_id: str,
    db: Session = Depends(get_db),
    service: TenderService = Depends(get_tndr_service),
) -> ResponseEnvelope[TenderResponse]:
    tender = service.get_tender_by_id(tender_id, db)
    return ResponseEnvelope[TenderResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Tender retrieved successfully.",
        data=TenderResponse.model_validate(tender),
        correlation_id=correlation_id_ctx.get(),
    )


@router.post(
    "/{tender_id}/analyze",
    response_model=ResponseEnvelope[TenderAnalysisResponse],
    summary="Initiate AI-assisted intelligence extraction over linked tender documents",
)
def analyze_tender(
    tender_id: str,
    payload: Optional[TenderAnalysisRequest] = None,
    db: Session = Depends(get_db),
    intel_service: TenderIntelligenceService = Depends(get_intelligence_service),
) -> ResponseEnvelope[TenderAnalysisResponse]:
    force = payload.force_reanalysis if payload else False
    result_data = asyncio.run(
        intel_service.analyze_tender(
            tender_id=tender_id,
            db=db,
            force_reanalysis=force,
        )
    )

    is_ai_req = result_data.get("analysis_status") == "ai_configuration_required"
    msg = (
        "AI provider is not configured. Document parsed and segmented without AI extraction."
        if is_ai_req
        else "Tender intelligence extraction completed successfully."
    )

    return ResponseEnvelope[TenderAnalysisResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message=msg,
        data=TenderAnalysisResponse.model_validate(result_data),
        correlation_id=correlation_id_ctx.get(),
    )


@router.get(
    "/{tender_id}/analysis",
    response_model=ResponseEnvelope[TenderRequirementsGroupedResponse],
    summary="Retrieve structured tender requirements grouped by category with source references",
)
def get_tender_analysis(
    tender_id: str,
    db: Session = Depends(get_db),
    service: TenderService = Depends(get_tndr_service),
) -> ResponseEnvelope[TenderRequirementsGroupedResponse]:
    grouped_data = service.get_tender_requirements(tender_id, db)
    return ResponseEnvelope[TenderRequirementsGroupedResponse](
        success=True,
        status_code=status.HTTP_200_OK,
        message="Tender requirements retrieved successfully.",
        data=TenderRequirementsGroupedResponse.model_validate(grouped_data),
        correlation_id=correlation_id_ctx.get(),
    )
