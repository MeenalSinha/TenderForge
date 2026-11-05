"""
Proposal Optimization, Evaluation Criteria, Quality Check, and Revisions API Routes.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.rbac import Role, require_role
from backend.app.infrastructure.database.session import get_db
from backend.app.services.evaluation_criteria_service import EvaluationCriteriaService
from backend.app.services.proposal_optimization_service import ProposalOptimizationService
from backend.app.services.proposal_revision_service import ProposalRevisionService

router = APIRouter(tags=["Proposal Optimizations & Quality"])


class UpdateSectionRequest(BaseModel):
    new_content: str
    author_id: str
    author_type: str = "human"
    change_summary: str = "Updated section text"


class CreateCriterionRequest(BaseModel):
    criterion_code: str
    title: str
    category: str
    weight_percentage: float
    max_marks: float
    description: str
    scoring_rules: Optional[Dict[str, Any]] = None
    mandatory: bool = False


# Criteria Endpoints
@router.get("/tenders/{tender_id}/criteria")
def list_criteria(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> List[Dict[str, Any]]:
    svc = EvaluationCriteriaService(db)
    items = svc.list_criteria(tender_id)
    return [
        {
            "id": c.id,
            "criterion_code": c.criterion_code,
            "title": c.title,
            "category": c.category,
            "weight_percentage": c.weight_percentage,
            "max_marks": c.max_marks,
            "description": c.description,
            "mandatory": c.mandatory,
            "scoring_rules": c.scoring_rules,
        }
        for c in items
    ]


@router.post("/tenders/{tender_id}/criteria/extract")
def extract_criteria(
    tender_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> List[Dict[str, Any]]:
    svc = EvaluationCriteriaService(db)
    try:
        items = svc.extract_evaluation_criteria(tender_id)
        return [
            {
                "id": c.id,
                "criterion_code": c.criterion_code,
                "title": c.title,
                "category": c.category,
                "weight_percentage": c.weight_percentage,
                "max_marks": c.max_marks,
            }
            for c in items
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Optimization Endpoints
@router.post("/proposals/{proposal_id}/optimize")
def analyze_and_optimize(
    proposal_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> List[Dict[str, Any]]:
    svc = ProposalOptimizationService(db)
    try:
        opts = svc.analyze_and_optimize(proposal_id)
        return [
            {
                "id": o.id,
                "section_number": o.section_number,
                "coverage_status": o.coverage_status,
                "gap_analysis": o.gap_analysis,
                "current_score_estimate": o.current_score_estimate,
                "potential_score_estimate": o.potential_score_estimate,
                "before_text": o.before_text,
                "after_text": o.after_text,
                "improvement_rationale": o.improvement_rationale,
                "status": o.status,
            }
            for o in opts
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals/{proposal_id}/optimizations")
def list_optimizations(
    proposal_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> List[Dict[str, Any]]:
    svc = ProposalOptimizationService(db)
    opts = svc.list_optimizations(proposal_id)
    return [
        {
            "id": o.id,
            "section_number": o.section_number,
            "coverage_status": o.coverage_status,
            "gap_analysis": o.gap_analysis,
            "current_score_estimate": o.current_score_estimate,
            "potential_score_estimate": o.potential_score_estimate,
            "before_text": o.before_text,
            "after_text": o.after_text,
            "improvement_rationale": o.improvement_rationale,
            "status": o.status,
        }
        for o in opts
    ]


@router.post("/optimizations/{optimization_id}/apply")
def apply_optimization(
    optimization_id: str,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = ProposalOptimizationService(db)
    try:
        o = svc.apply_optimization(optimization_id)
        return {
            "id": o.id,
            "proposal_id": o.proposal_id,
            "section_number": o.section_number,
            "status": o.status,
            "applied_at": o.applied_at.isoformat() if o.applied_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Revisions & Quality Endpoints
@router.post("/proposals/{proposal_id}/sections/{section_number}")
def update_section(
    proposal_id: str,
    section_number: str,
    payload: UpdateSectionRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.AUTHOR)),
) -> Dict[str, Any]:
    svc = ProposalRevisionService(db)
    try:
        sec, invalidated = svc.update_section_with_invalidation(
            proposal_id=proposal_id,
            section_number=section_number,
            new_content=payload.new_content,
            author_id=payload.author_id,
            author_type=payload.author_type,
            change_summary=payload.change_summary,
        )
        return {
            "proposal_id": proposal_id,
            "section_number": sec.section_number,
            "approval_invalidated": invalidated,
            "updated_at": sec.updated_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals/{proposal_id}/diff")
def diff_revisions(
    proposal_id: str,
    v_old: int = Query(..., description="Earlier version number"),
    v_new: int = Query(..., description="Later version number"),
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.VIEWER)),
) -> Dict[str, Any]:
    svc = ProposalRevisionService(db)
    try:
        return svc.compare_revisions(proposal_id, v_old, v_new)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/proposals/{proposal_id}/quality-check")
def validate_proposal_quality(
    proposal_id: str,
    checked_by: str = "QualityAuditor",
    db: Session = Depends(get_db),
    _role: str = Depends(require_role(Role.REVIEWER)),
) -> Dict[str, Any]:
    svc = ProposalRevisionService(db)
    try:
        qc = svc.validate_proposal_quality(proposal_id, checked_by=checked_by)
        return {
            "id": qc.id,
            "formatting_score": qc.formatting_score,
            "passed": qc.passed,
            "word_count": qc.word_count,
            "page_count_estimate": qc.page_count_estimate,
            "placeholder_count": qc.placeholder_count,
            "placeholders_found": qc.placeholders_found,
            "citations_verified_count": qc.citations_verified_count,
            "citations_missing_count": qc.citations_missing_count,
            "issues": qc.issues,
            "created_at": qc.created_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
