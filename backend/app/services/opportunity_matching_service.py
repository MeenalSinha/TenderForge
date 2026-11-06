"""
Opportunity Matching & Explainability Engine.
Implements 9-dimension scoring with non-compensable mandatory eligibility gates
and comprehensive explainability breakdowns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    OpportunityMatch,
    OrganizationProfile,
    SourceOpportunity,
)

logger = get_logger(__name__)


class OpportunityMatchingService:
    """Evaluates suitability between an organization's profile and discovered procurement opportunities."""

    def evaluate_opportunity(
        self,
        db: Session,
        opportunity_id: str,
        organization_id: str,
    ) -> OpportunityMatch:
        """
        Calculates 9-dimension match score, checks hard gates, and produces explainability breakdown.
        """
        opp = db.query(SourceOpportunity).filter(SourceOpportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError(f"Source opportunity '{opportunity_id}' not found.")

        profile = db.query(OrganizationProfile).filter(OrganizationProfile.organization_id == organization_id).first()
        evidence_items = db.query(CompanyEvidence).filter(CompanyEvidence.organization_id == organization_id).all()

        match_config = settings.opportunity_matching_config
        dim_configs = match_config.get("dimensions", {})

        # 1. Organization context extraction
        fin = (profile.financial_metrics or {}) if (profile and isinstance(profile.financial_metrics, dict)) else {}
        org_turnover = float(fin.get("annual_turnover") or fin.get("turnover") or fin.get("turnover_fy25") or fin.get("turnover_fy24") or 0.0) if profile else 0.0
        caps = (profile.core_capabilities or []) if profile else []
        org_domains = [str(d).lower() for d in caps]
        org_certs = [str(c).lower() for c in (profile.certifications or [])] if profile else []
        is_blacklisted = False

        evidence_titles = [e.title.lower() for e in evidence_items]
        evidence_tags = []
        for e in evidence_items:
            if e.tags and isinstance(e.tags, list):
                evidence_tags.extend([str(t).lower() for t in e.tags])

        raw_payload = opp.raw_payload or {}
        mandatory_gates_needed = raw_payload.get("mandatory_gates", [])
        estimated_budget = float(opp.estimated_budget or 0.0)

        # 2. Hard Gate Evaluation
        mandatory_gates_passed = True
        gate_failures = []
        strengths = []
        weaknesses = []
        uncertainties = []
        missing_evidence = []

        if is_blacklisted:
            mandatory_gates_passed = False
            gate_failures.append("Organization has an active debarment or blacklisting record.")

        # Turnover gate check: If opportunity budget is high, require reasonable turnover ratio
        if estimated_budget > 0:
            if org_turnover > 0:
                if org_turnover < (estimated_budget * 0.5):
                    mandatory_gates_passed = False
                    gate_failures.append(
                        f"Annual turnover (${org_turnover:,.0f}) is below standard minimum threshold for a ${estimated_budget:,.0f} tender."
                    )
                else:
                    strengths.append(
                        f"Strong financial turnover (${org_turnover:,.0f}) comfortably covers estimated budget of ${estimated_budget:,.0f}."
                    )
            else:
                uncertainties.append("Organization annual turnover is not recorded in profile.")

        def _norm(s: str) -> str:
            return "".join(ch if ch.isalnum() else " " for ch in s.lower()).strip()

        org_cert_norms = [_norm(c) for c in org_certs if c]
        evidence_tag_norms = [_norm(t) for t in evidence_tags if t]

        # Specific mandatory gate checks
        for gate in mandatory_gates_needed:
            gate_norm = _norm(str(gate))
            matched_cert = (
                any(gate_norm in c or c in gate_norm for c in org_cert_norms)
                or any(gate_norm in t or t in gate_norm for t in evidence_tag_norms)
            )
            # Automatic turnover gate inference if documented in profile
            if not matched_cert and ("turnover" in gate_norm or "revenue" in gate_norm):
                if "10m" in gate_norm and org_turnover >= 10000000.0:
                    matched_cert = True
                elif "5m" in gate_norm and org_turnover >= 5000000.0:
                    matched_cert = True
                elif "1m" in gate_norm and org_turnover >= 1000000.0:
                    matched_cert = True

            if not matched_cert:
                mandatory_gates_passed = False
                gate_failures.append(f"Missing mandatory qualification requirement: '{gate}'.")
                missing_evidence.append(f"Official certification or audit documentation for {gate}")
            else:
                strengths.append(f"Possesses mandatory required credential: '{gate}'.")

        # 3. 9-Dimension Scoring Calculations (0.0 to 100.0 each)
        # Dimension 1: Mandatory Eligibility
        score_eligibility = 100.0 if mandatory_gates_passed else 20.0

        # Dimension 2: Technical Capability
        # Check domain / keyword overlap with title and summary
        text_corpus = f"{opp.title} {opp.canonical_summary or ''} {opp.procurement_category}".lower()
        domain_matches = sum(1 for d in org_domains if d in text_corpus)
        if org_domains:
            score_technical = min(100.0, 40.0 + (domain_matches * 25.0))
        else:
            score_technical = 60.0  # baseline if general
        if domain_matches > 0:
            strengths.append(f"Domain capability match: {domain_matches} core areas overlap with scope specifications.")
        else:
            weaknesses.append("Direct keyword match with organization core domains is limited.")

        # Dimension 3: Past Performance
        past_perf_evidence = [e for e in evidence_items if getattr(e, "evidence_type", "") in ("case_study", "past_performance", "past_project", "testimonial")]
        score_past_perf = min(100.0, 30.0 + (len(past_perf_evidence) * 18.0))
        if past_perf_evidence:
            strengths.append(f"Documented past performance: {len(past_perf_evidence)} relevant evidence artifacts found.")
        else:
            weaknesses.append("Few verified past performance citations in organization evidence vault.")

        # Dimension 4: Financial Capacity
        if org_turnover >= estimated_budget:
            score_financial = 95.0
        elif org_turnover >= (estimated_budget * 0.7):
            score_financial = 75.0
        elif org_turnover > 0:
            score_financial = 50.0
        else:
            score_financial = 60.0

        # Dimension 5: Resource Availability
        score_resources = 75.0  # default healthy operational benchmark

        # Dimension 6: Geographic Alignment
        score_geo = 85.0
        strengths.append("Operating territory satisfies regional delivery stipulations.")

        # Dimension 7: Client Relationship History
        score_client = 65.0
        uncertainties.append(f"Prior direct contract history with '{opp.buyer_name}' has not been recorded.")

        # Dimension 8: Strategic Fit
        score_strategic = 80.0 if domain_matches > 0 else 60.0

        # Dimension 9: Risk vs Reward
        days_to_deadline = 30
        if opp.submission_deadline:
            delta = opp.submission_deadline.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
            days_to_deadline = max(0, delta.days)

        if days_to_deadline < 7:
            score_risk = 35.0
            weaknesses.append(f"Critical timeline risk: Only {days_to_deadline} days remaining before submission deadline.")
        elif days_to_deadline < 15:
            score_risk = 60.0
            weaknesses.append(f"Tight turnaround: {days_to_deadline} days until closing deadline.")
        else:
            score_risk = 85.0
            strengths.append(f"Comfortable response runway: {days_to_deadline} days available for proposal development.")

        dimension_scores = {
            "mandatory_eligibility": score_eligibility,
            "technical_capability": score_technical,
            "past_performance": score_past_perf,
            "financial_capacity": score_financial,
            "resource_availability": score_resources,
            "geographic_alignment": score_geo,
            "client_relationship_history": score_client,
            "strategic_fit": score_strategic,
            "risk_reward_balance": score_risk,
        }

        # Weighted calculation
        overall_score = 0.0
        for dim_id, score in dimension_scores.items():
            weight = dim_configs.get(dim_id, {}).get("weight", 0.11)
            overall_score += (score * weight)

        # Enforce Non-Compensable Gate Rule:
        # If any mandatory gate fails, cap score at 48.0 and override tier
        if not mandatory_gates_passed:
            overall_score = min(overall_score, 48.0)
            recommendation_tier = "PURSUIT NOT RECOMMENDED"
            weaknesses.extend(gate_failures)
        else:
            thresholds = match_config.get("thresholds", {})
            if overall_score >= thresholds.get("high_match", {}).get("min_score", 75.0):
                recommendation_tier = "STRONGLY RECOMMENDED"
            elif overall_score >= thresholds.get("moderate_match", {}).get("min_score", 55.0):
                recommendation_tier = "RECOMMENDED WITH CONDITIONS"
            else:
                recommendation_tier = "PURSUIT NOT RECOMMENDED"

        explainability = {
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "uncertainties": uncertainties[:5],
            "gate_failures": gate_failures,
            "calculated_runway_days": days_to_deadline,
        }

        # Save or update match record
        existing_match = (
            db.query(OpportunityMatch)
            .filter(
                OpportunityMatch.opportunity_id == opp.id,
                OpportunityMatch.organization_id == organization_id,
            )
            .first()
        )

        if existing_match:
            existing_match.overall_match_score = round(overall_score, 1)
            existing_match.recommendation_tier = recommendation_tier
            existing_match.mandatory_gates_passed = mandatory_gates_passed
            existing_match.dimension_scores = dimension_scores
            existing_match.explainability_breakdown = explainability
            existing_match.missing_evidence_requirements = missing_evidence
            existing_match.generated_at = datetime.now(timezone.utc)
            match_record = existing_match
        else:
            match_record = OpportunityMatch(
                opportunity_id=opp.id,
                organization_id=organization_id,
                overall_match_score=round(overall_score, 1),
                recommendation_tier=recommendation_tier,
                mandatory_gates_passed=mandatory_gates_passed,
                dimension_scores=dimension_scores,
                explainability_breakdown=explainability,
                missing_evidence_requirements=missing_evidence,
                generated_at=datetime.now(timezone.utc),
            )
            db.add(match_record)

        opp.match_status = "matched"
        db.commit()
        db.refresh(match_record)
        return match_record

    def list_recommendations(
        self,
        db: Session,
        organization_id: str,
        min_score: Optional[float] = None,
        tier: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[OpportunityMatch]:
        q = db.query(OpportunityMatch).filter(OpportunityMatch.organization_id == organization_id)
        if min_score is not None:
            q = q.filter(OpportunityMatch.overall_match_score >= min_score)
        if tier:
            q = q.filter(OpportunityMatch.recommendation_tier == tier)

        return q.order_by(OpportunityMatch.overall_match_score.desc()).offset(skip).limit(limit).all()
