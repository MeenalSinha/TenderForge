"""
Procurement Opportunities & Matching Engine API Routes.
Provides opportunity discovery search, 9-dimension explainable matching, and workspace promotion.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import OpportunityMatch, SourceOpportunity
from backend.app.infrastructure.database.session import get_db
from backend.app.services.opportunity_service import OpportunityService
from backend.app.services.opportunity_matching_service import OpportunityMatchingService

router = APIRouter(prefix="/opportunities", tags=["Procurement Opportunities"])


class PromoteOpportunityRequest(BaseModel):
    workspace_id: Optional[str] = None
    custom_title: Optional[str] = None


@router.get("")
def list_opportunities(
    organization_id: Optional[str] = None,
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    min_budget: Optional[float] = Query(None),
    max_budget: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or (claims.get("org_id") if isinstance(claims, dict) else None) or settings.default_organization_id
    cat = category if isinstance(category, str) else None
    stat = status_filter if isinstance(status_filter, str) else None
    min_b = min_budget if isinstance(min_budget, (int, float)) else None
    max_b = max_budget if isinstance(max_budget, (int, float)) else None
    srch = search if isinstance(search, str) else None
    skp = skip if isinstance(skip, int) else 0
    lmt = limit if isinstance(limit, int) else 50

    svc = OpportunityService()
    results, total = svc.list_opportunities(
        db=db,
        organization_id=org_id,
        category=cat,
        status=stat,
        min_budget=min_b,
        max_budget=max_b,
        search=srch,
        skip=skp,
        limit=lmt,
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "opportunities": [
            {
                "id": o.id,
                "external_id": o.external_id,
                "title": o.title,
                "buyer_name": o.buyer_name,
                "procurement_category": o.procurement_category,
                "estimated_budget": o.estimated_budget,
                "currency": o.currency,
                "published_date": o.published_date.isoformat() if o.published_date else None,
                "submission_deadline": o.submission_deadline.isoformat() if o.submission_deadline else None,
                "status": o.status,
                "opportunity_url": o.opportunity_url,
                "canonical_summary": o.canonical_summary,
                "match_status": o.match_status,
                "created_at": o.created_at.isoformat(),
            }
            for o in results
        ],
    }


@router.get("/recommendations")
def list_recommendations(
    organization_id: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    tier: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or (claims.get("org_id") if isinstance(claims, dict) else None) or settings.default_organization_id
    ms = min_score if isinstance(min_score, (int, float)) else None
    tr = tier if isinstance(tier, str) else None
    skp = skip if isinstance(skip, int) else 0
    lmt = limit if isinstance(limit, int) else 20

    svc = OpportunityMatchingService()
    matches = svc.list_recommendations(
        db=db,
        organization_id=org_id,
        min_score=ms,
        tier=tr,
        skip=skp,
        limit=lmt,
    )
    return {
        "count": len(matches),
        "recommendations": [
            {
                "id": m.id,
                "opportunity_id": m.opportunity_id,
                "opportunity_title": m.opportunity.title if m.opportunity else "",
                "buyer_name": m.opportunity.buyer_name if m.opportunity else "",
                "overall_match_score": m.overall_match_score,
                "recommendation_tier": m.recommendation_tier,
                "mandatory_gates_passed": m.mandatory_gates_passed,
                "dimension_scores": m.dimension_scores,
                "explainability": m.explainability_breakdown,
                "missing_evidence": m.missing_evidence_requirements,
                "generated_at": m.generated_at.isoformat(),
            }
            for m in matches
        ],
    }


@router.get("/{opportunity_id}")
def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = OpportunityService()
    opp = svc.get_opportunity(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")

    latest_match = (
        db.query(OpportunityMatch)
        .filter(OpportunityMatch.opportunity_id == opp.id)
        .order_by(OpportunityMatch.generated_at.desc())
        .first()
    )

    return {
        "id": opp.id,
        "external_id": opp.external_id,
        "title": opp.title,
        "buyer_name": opp.buyer_name,
        "procurement_category": opp.procurement_category,
        "estimated_budget": opp.estimated_budget,
        "currency": opp.currency,
        "published_date": opp.published_date.isoformat() if opp.published_date else None,
        "submission_deadline": opp.submission_deadline.isoformat() if opp.submission_deadline else None,
        "status": opp.status,
        "opportunity_url": opp.opportunity_url,
        "canonical_summary": opp.canonical_summary,
        "raw_payload": opp.raw_payload,
        "match_status": opp.match_status,
        "latest_match": {
            "overall_match_score": latest_match.overall_match_score,
            "recommendation_tier": latest_match.recommendation_tier,
            "mandatory_gates_passed": latest_match.mandatory_gates_passed,
            "dimension_scores": latest_match.dimension_scores,
            "explainability": latest_match.explainability_breakdown,
            "missing_evidence": latest_match.missing_evidence_requirements,
        } if latest_match else None,
        "created_at": opp.created_at.isoformat(),
    }


@router.post("/{opportunity_id}/match")
def evaluate_opportunity_match(
    opportunity_id: str,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = OpportunityMatchingService()
    try:
        match_record = svc.evaluate_opportunity(
            db=db,
            opportunity_id=opportunity_id,
            organization_id=org_id,
        )
        return {
            "status": "success",
            "match": {
                "id": match_record.id,
                "opportunity_id": match_record.opportunity_id,
                "overall_match_score": match_record.overall_match_score,
                "recommendation_tier": match_record.recommendation_tier,
                "mandatory_gates_passed": match_record.mandatory_gates_passed,
                "dimension_scores": match_record.dimension_scores,
                "explainability": match_record.explainability_breakdown,
                "missing_evidence": match_record.missing_evidence_requirements,
                "generated_at": match_record.generated_at.isoformat(),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/{opportunity_id}/promote")
def promote_opportunity(
    opportunity_id: str,
    payload: PromoteOpportunityRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = OpportunityService()
    try:
        tender = svc.promote_opportunity_to_tender(
            db=db,
            opportunity_id=opportunity_id,
            workspace_id=payload.workspace_id,
            custom_title=payload.custom_title,
        )
        return {
            "status": "success",
            "message": "Opportunity successfully promoted to active tender workspace.",
            "tender": {
                "id": tender.id,
                "workspace_id": tender.workspace_id,
                "title": tender.title,
                "reference_number": tender.reference_number,
                "issuing_authority": tender.issuing_authority,
                "estimated_value": tender.estimated_value,
                "submission_deadline": tender.submission_deadline.isoformat() if tender.submission_deadline else None,
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
