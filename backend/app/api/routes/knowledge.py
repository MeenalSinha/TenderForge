"""
Knowledge Library API Routes.
Manages reusable proposal narratives, boilerplate, CVs, and methodology assets.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import KnowledgeAsset
from backend.app.infrastructure.database.session import get_db
from backend.app.services.knowledge_library_service import KnowledgeLibraryService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Library"])


class CreateAssetRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=512)
    content: str = Field(..., min_length=1)
    category: str = Field(default="technical_approach")
    asset_type: str = Field(default="text")
    keywords: Optional[List[str]] = Field(default_factory=list)
    auto_approve: bool = False


class UpdateAssetRequest(BaseModel):
    content: str = Field(..., min_length=1)
    title: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None
    change_summary: Optional[str] = None


class ReuseAssetRequest(BaseModel):
    proposal_section_id: Optional[str] = None


@router.post("/assets", status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: CreateAssetRequest,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    user_id = claims.get("sub")
    svc = KnowledgeLibraryService()
    asset = svc.create_asset(
        db=db,
        organization_id=org_id,
        title=payload.title,
        content=payload.content,
        category=payload.category,
        asset_type=payload.asset_type,
        keywords=payload.keywords,
        author_user_id=user_id,
        auto_approve=payload.auto_approve,
    )
    return {
        "status": "success",
        "asset": {
            "id": asset.id,
            "title": asset.title,
            "category": asset.category,
            "review_status": asset.review_status,
            "times_reused": asset.times_reused,
            "created_at": asset.created_at.isoformat(),
        },
    }


@router.get("/assets")
def list_assets(
    organization_id: Optional[str] = None,
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or (claims.get("org_id") if isinstance(claims, dict) else None) or settings.default_organization_id
    cat = category if isinstance(category, str) else None
    stat = review_status if isinstance(review_status, str) else None
    srch = search if isinstance(search, str) else None
    skp = skip if isinstance(skip, int) else 0
    lmt = limit if isinstance(limit, int) else 50

    svc = KnowledgeLibraryService()
    results, total = svc.list_assets(
        db=db,
        organization_id=org_id,
        category=cat,
        review_status=stat,
        search=srch,
        skip=skp,
        limit=lmt,
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "assets": [
            {
                "id": a.id,
                "title": a.title,
                "category": a.category,
                "review_status": a.review_status,
                "keywords": a.keywords,
                "plain_text": a.plain_text,
                "times_reused": a.times_reused,
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
            }
            for a in results
        ],
    }


@router.get("/assets/{asset_id}")
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = KnowledgeLibraryService()
    asset = svc.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")

    return {
        "id": asset.id,
        "title": asset.title,
        "category": asset.category,
        "asset_type": asset.asset_type,
        "content": asset.content,
        "keywords": asset.keywords,
        "review_status": asset.review_status,
        "times_reused": asset.times_reused,
        "created_at": asset.created_at.isoformat(),
        "updated_at": asset.updated_at.isoformat(),
        "versions": [
            {
                "version_number": v.version_number,
                "change_summary": v.change_summary,
                "created_at": v.created_at.isoformat(),
            }
            for v in asset.versions
        ],
    }


@router.put("/assets/{asset_id}")
def update_asset(
    asset_id: str,
    payload: UpdateAssetRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    user_id = claims.get("sub")
    svc = KnowledgeLibraryService()
    try:
        updated = svc.update_asset(
            db=db,
            asset_id=asset_id,
            content=payload.content,
            title=payload.title,
            category=payload.category,
            keywords=payload.keywords,
            change_summary=payload.change_summary,
            modified_by_user_id=user_id,
        )
        return {
            "status": "success",
            "asset": {
                "id": updated.id,
                "title": updated.title,
                "category": updated.category,
                "updated_at": updated.updated_at.isoformat(),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/assets/{asset_id}/approve")
def approve_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> Dict[str, Any]:
    user_id = claims.get("sub") or "reviewer"
    svc = KnowledgeLibraryService()
    try:
        approved = svc.approve_asset(db, asset_id, user_id)
        return {
            "status": "success",
            "message": "Asset approved for proposal reuse.",
            "asset_id": approved.id,
            "review_status": approved.review_status,
            "approved_at": approved.approved_at.isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/assets/{asset_id}/reuse")
def reuse_asset(
    asset_id: str,
    payload: ReuseAssetRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = KnowledgeLibraryService()
    try:
        result = svc.use_asset(
            db=db,
            asset_id=asset_id,
            proposal_section_id=payload.proposal_section_id,
        )
        return {
            "status": "success",
            "result": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
