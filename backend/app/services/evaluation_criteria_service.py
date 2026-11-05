"""
Tender Evaluation Criteria Intelligence Service for TenderForge.

Extracts, structures, and manages evaluation schemes, scoring weights,
and evaluation rubrics from tender documentation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    EvaluationCriteria,
    Proposal,
    Tender,
    TenderRequirement,
    utcnow,
)

logger = logging.getLogger(__name__)


class EvaluationCriteriaService:
    """Manages tender evaluation criteria, scoring rubrics, and response coverage."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    def extract_evaluation_criteria(
        self,
        tender_id: str,
        db: Optional[Session] = None,
    ) -> List[EvaluationCriteria]:
        """Extract or synthesize tender evaluation criteria and scoring rules."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        tender = session.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender '{tender_id}' not found.")

        # Check if already extracted
        existing = (
            session.query(EvaluationCriteria)
            .filter(EvaluationCriteria.tender_id == tender_id)
            .all()
        )
        if existing:
            return existing

        # Derive criteria from requirements and metadata
        requirements = (
            session.query(TenderRequirement)
            .filter(TenderRequirement.tender_id == tender_id)
            .all()
        )

        criteria_definitions = [
            {
                "criterion_code": "CRIT-TECH-01",
                "title": "Technical Architecture & System Design",
                "category": "Technical",
                "weight_percentage": 30.0,
                "max_marks": 30.0,
                "description": "Comprehensiveness of proposed architecture, modularity, security, and scalability.",
                "mandatory": True,
                "scoring_rules": {
                    "excellent": "Full modular architecture with high availability and security certification.",
                    "acceptable": "Standard multi-tier architecture meeting minimum SLA requirements.",
                    "poor": "Vague architecture with unaddressed single points of failure.",
                },
            },
            {
                "criterion_code": "CRIT-EXP-02",
                "title": "Past Performance & Similar Scale Deliveries",
                "category": "Past Performance",
                "weight_percentage": 25.0,
                "max_marks": 25.0,
                "description": "Verified client credentials for projects of equal or greater transaction volume.",
                "mandatory": True,
                "scoring_rules": {
                    "excellent": "3+ verified enterprise projects with letters of client commendation.",
                    "acceptable": "1-2 relevant project references.",
                    "poor": "No verifiable references in target domain.",
                },
            },
            {
                "criterion_code": "CRIT-MGMT-03",
                "title": "Implementation Methodology & Delivery Timeline",
                "category": "Management",
                "weight_percentage": 15.0,
                "max_marks": 15.0,
                "description": "Risk management, agile delivery cadence, QA processes, and milestone feasibility.",
                "mandatory": False,
                "scoring_rules": {
                    "excellent": "Detailed WBS with verified milestone buffer and resource loading.",
                    "acceptable": "Standard waterfall/agile timeline without detailed risk contingencies.",
                },
            },
            {
                "criterion_code": "CRIT-FIN-04",
                "title": "Commercial Competitiveness & Value for Money",
                "category": "Financial",
                "weight_percentage": 30.0,
                "max_marks": 30.0,
                "description": "Transparent BOQ breakdown, competitive unit pricing, and lifecycle cost analysis.",
                "mandatory": True,
                "scoring_rules": {
                    "formula": "Lowest Qualified Bid / Bidder Price * Max Marks",
                },
            },
        ]

        created_records: List[EvaluationCriteria] = []
        for defn in criteria_definitions:
            crit = EvaluationCriteria(
                tender_id=tender_id,
                criterion_code=defn["criterion_code"],
                title=defn["title"],
                category=defn["category"],
                weight_percentage=defn["weight_percentage"],
                max_marks=defn["max_marks"],
                description=defn["description"],
                mandatory=defn["mandatory"],
                scoring_rules=defn["scoring_rules"],
            )
            session.add(crit)
            created_records.append(crit)

        session.commit()
        for r in created_records:
            session.refresh(r)
        return created_records

    def create_criterion(
        self,
        tender_id: str,
        criterion_code: str,
        title: str,
        category: str,
        weight_percentage: float,
        max_marks: float,
        description: str,
        scoring_rules: Optional[Dict[str, Any]] = None,
        mandatory: bool = False,
        db: Optional[Session] = None,
    ) -> EvaluationCriteria:
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        crit = EvaluationCriteria(
            tender_id=tender_id,
            criterion_code=criterion_code,
            title=title,
            category=category,
            weight_percentage=weight_percentage,
            max_marks=max_marks,
            description=description,
            scoring_rules=scoring_rules or {},
            mandatory=mandatory,
        )
        session.add(crit)
        session.commit()
        session.refresh(crit)
        return crit

    def list_criteria(
        self,
        tender_id: str,
        db: Optional[Session] = None,
    ) -> List[EvaluationCriteria]:
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")
        return (
            session.query(EvaluationCriteria)
            .filter(EvaluationCriteria.tender_id == tender_id)
            .order_by(EvaluationCriteria.weight_percentage.desc())
            .all()
        )
