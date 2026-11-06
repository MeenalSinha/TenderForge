"""
Market Intelligence & Competitor Tracking API Routes.
Provides verified public contract award ingestion, macro-procurement analytics, and competitor intelligence.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import AwardRecord, CompetitorRecord
from backend.app.infrastructure.database.session import get_db
from backend.app.services.market_intelligence_service import MarketIntelligenceService

router = APIRouter(prefix="/market", tags=["Market Intelligence & Competitors"])


class RecordAwardRequest(BaseModel):
    tender_reference: str = Field(..., min_length=2)
    buyer_name: str = Field(..., min_length=2)
    winning_bidder: str = Field(..., min_length=2)
    award_amount: float = Field(..., gt=0.0)
    currency: str = "USD"
    award_date: Optional[datetime] = None
    procurement_category: str = "general"
    source_provenance: str = "Verified Public Portal Feed"


class CompetitorProfileRequest(BaseModel):
    competitor_name: str = Field(..., min_length=2)
    domain: Optional[str] = None
    observed_tenders_count: int = Field(default=1, ge=0)
    estimated_win_rate: float = Field(default=50.0, ge=0.0, le=100.0)
    key_strengths: Optional[List[str]] = None
    known_weaknesses: Optional[List[str]] = None
    pricing_strategy_notes: Optional[str] = None


@router.post("/awards", status_code=status.HTTP_201_CREATED)
def record_award(
    payload: RecordAwardRequest,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = MarketIntelligenceService()
    award = svc.record_public_award(
        db=db,
        organization_id=org_id,
        tender_reference=payload.tender_reference,
        buyer_name=payload.buyer_name,
        winning_bidder=payload.winning_bidder,
        award_amount=payload.award_amount,
        currency=payload.currency,
        award_date=payload.award_date,
        procurement_category=payload.procurement_category,
        source_provenance=payload.source_provenance,
    )
    return {
        "status": "success",
        "award": {
            "id": award.id,
            "tender_reference": award.tender_reference,
            "buyer_name": award.buyer_name,
            "winning_bidder": award.winning_bidder,
            "award_amount": award.award_amount,
            "currency": award.currency,
            "award_date": award.award_date.isoformat(),
            "source_provenance": award.source_provenance,
        },
    }


@router.get("/awards")
def list_awards(
    organization_id: Optional[str] = None,
    category: Optional[str] = Query(None),
    buyer_name: Optional[str] = Query(None),
    winning_bidder: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or (claims.get("org_id") if isinstance(claims, dict) else None) or settings.default_organization_id
    cat = category if isinstance(category, str) else None
    buyer = buyer_name if isinstance(buyer_name, str) else None
    winner = winning_bidder if isinstance(winning_bidder, str) else None
    skp = skip if isinstance(skip, int) else 0
    lmt = limit if isinstance(limit, int) else 50

    svc = MarketIntelligenceService()
    results, total = svc.list_awards(
        db=db,
        organization_id=org_id,
        category=cat,
        buyer_name=buyer,
        winning_bidder=winner,
        skip=skp,
        limit=lmt,
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "awards": [
            {
                "id": a.id,
                "tender_reference": a.tender_reference,
                "buyer_name": a.buyer_name,
                "winning_bidder": a.winning_bidder,
                "award_amount": a.award_amount,
                "currency": a.currency,
                "award_date": a.award_date.isoformat(),
                "procurement_category": a.procurement_category,
                "source_provenance": a.source_provenance,
                "verification_status": a.verification_status,
            }
            for a in results
        ],
    }


@router.get("/trends")
def get_market_trends(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = MarketIntelligenceService()
    summary = svc.get_market_summary(db=db, organization_id=org_id)
    return summary


@router.post("/competitors")
def upsert_competitor(
    payload: CompetitorProfileRequest,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = MarketIntelligenceService()
    comp = svc.record_or_update_competitor(
        db=db,
        organization_id=org_id,
        competitor_name=payload.competitor_name,
        domain=payload.domain,
        observed_tenders_count=payload.observed_tenders_count,
        estimated_win_rate=payload.estimated_win_rate,
        key_strengths=payload.key_strengths,
        known_weaknesses=payload.known_weaknesses,
        pricing_strategy_notes=payload.pricing_strategy_notes,
    )
    return {
        "status": "success",
        "competitor": {
            "id": comp.id,
            "competitor_name": comp.competitor_name,
            "domain": comp.domain,
            "observed_tenders_count": comp.observed_tenders_count,
            "estimated_win_rate": comp.estimated_win_rate,
            "key_strengths": comp.key_strengths,
            "known_weaknesses": comp.known_weaknesses,
            "pricing_strategy_notes": comp.pricing_strategy_notes,
        },
    }


@router.get("/competitors")
def list_competitors(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    svc = MarketIntelligenceService()
    competitors = svc.list_competitors(db=db, organization_id=org_id)
    return {
        "count": len(competitors),
        "competitors": [
            {
                "id": c.id,
                "competitor_name": c.competitor_name,
                "domain": c.domain,
                "observed_tenders_count": c.observed_tenders_count,
                "estimated_win_rate": c.estimated_win_rate,
                "key_strengths": c.key_strengths,
                "known_weaknesses": c.known_weaknesses,
                "pricing_strategy_notes": c.pricing_strategy_notes,
                "updated_at": c.updated_at.isoformat(),
            }
            for c in competitors
        ],
    }
