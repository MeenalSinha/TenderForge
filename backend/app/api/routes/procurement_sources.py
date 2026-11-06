"""
Procurement Sources API Routes.
Manages source configurations and on-demand synchronization runs.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rbac import Role, require_role, get_current_user_claims
from backend.app.infrastructure.database.models import ConnectorRun, ProcurementSource
from backend.app.infrastructure.database.session import get_db
from backend.app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/sources", tags=["Procurement Sources"])


class CreateSourceRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    connector_type: str = Field(default="mock_sandbox", description="mock_sandbox, manual_import, open_contracting, government_portal")
    endpoint_url: Optional[str] = None
    auth_type: str = "none"
    auth_config: Optional[Dict[str, Any]] = None
    polling_interval_minutes: int = 60
    organization_id: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_source(
    payload: CreateSourceRequest,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    org_id = payload.organization_id or claims.get("org_id") or settings.default_organization_id
    svc = OpportunityService()
    source = svc.get_or_create_source(
        db=db,
        organization_id=org_id,
        name=payload.name,
        connector_type=payload.connector_type,
        endpoint_url=payload.endpoint_url,
        auth_type=payload.auth_type,
        auth_config=payload.auth_config,
        polling_interval_minutes=payload.polling_interval_minutes,
    )
    return {
        "status": "success",
        "source": {
            "id": source.id,
            "name": source.name,
            "connector_type": source.connector_type,
            "endpoint_url": source.endpoint_url,
            "is_active": source.is_active,
            "polling_interval_minutes": source.polling_interval_minutes,
            "sync_status": source.sync_status,
            "created_at": source.created_at.isoformat(),
        },
    }


@router.get("")
def list_sources(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    org_id = organization_id or claims.get("org_id") or settings.default_organization_id
    sources = db.query(ProcurementSource).filter(ProcurementSource.organization_id == org_id).all()
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "connector_type": s.connector_type,
                "endpoint_url": s.endpoint_url,
                "is_active": s.is_active,
                "polling_interval_minutes": s.polling_interval_minutes,
                "last_synced_at": s.last_synced_at.isoformat() if s.last_synced_at else None,
                "sync_status": s.sync_status,
                "created_at": s.created_at.isoformat(),
            }
            for s in sources
        ],
    }


@router.post("/{source_id}/sync")
async def sync_source(
    source_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = OpportunityService()
    try:
        run, opportunities = await svc.sync_source(db=db, source_id=source_id, limit=limit)
        return {
            "status": "success",
            "run_id": run.id,
            "run_status": run.status,
            "items_discovered": run.items_discovered,
            "items_ingested": run.items_ingested,
            "errors": run.error_message,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{source_id}/runs")
def list_source_runs(
    source_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    runs = (
        db.query(ConnectorRun)
        .filter(ConnectorRun.source_id == source_id)
        .order_by(ConnectorRun.started_at.desc())
        .limit(20)
        .all()
    )
    return {
        "runs": [
            {
                "id": r.id,
                "status": r.status,
                "started_at": r.started_at.isoformat(),
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "items_discovered": r.items_discovered,
                "items_ingested": r.items_ingested,
                "error_message": r.error_message,
            }
            for r in runs
        ]
    }

