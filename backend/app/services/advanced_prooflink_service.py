"""
Advanced ProofLink Intelligence Service for TenderForge.

Capabilities:
1. Extended Evidence Metadata & Freshness Tracking (expiry windows, stale alerts).
2. Cross-Document Contradiction Detection (conflicting metrics, dates, credentials).
3. End-to-End Claim Lineage Recording:
   Requirement -> Evidence -> Extract -> Claim -> Review -> Approved Section.
4. Evidence Change Impact Invalidation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.infrastructure.database.models import (
    ClaimLineage,
    CompanyEvidence,
    EvidenceContradiction,
    EvidenceRequirementLink,
    Organization,
    OrganizationProfile,
    Proposal,
    Tender,
    TenderRequirement,
    utcnow,
)

logger = logging.getLogger(__name__)


class AdvancedProofLinkService:
    """Provides high-integrity evidence traceability, freshness audits, and contradiction detection."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    def audit_evidence_freshness(
        self,
        organization_id: str,
        target_date: Optional[datetime] = None,
        warning_window_days: int = 90,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Audit all evidence records for expiration and approaching obsolescence."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        ref_date = target_date or datetime.now(timezone.utc)
        if ref_date.tzinfo is None:
            ref_date = ref_date.replace(tzinfo=timezone.utc)

        warning_threshold = ref_date + timedelta(days=warning_window_days)

        evidence_items = (
            session.query(CompanyEvidence)
            .filter(CompanyEvidence.organization_id == organization_id)
            .all()
        )

        expired_items: List[Dict[str, Any]] = []
        expiring_soon_items: List[Dict[str, Any]] = []
        valid_items: List[Dict[str, Any]] = []

        for ev in evidence_items:
            exp_date = ev.expiry_date
            if exp_date:
                if exp_date.tzinfo is None:
                    exp_date = exp_date.replace(tzinfo=timezone.utc)

                item_info = {
                    "id": ev.id,
                    "title": ev.title,
                    "evidence_type": ev.evidence_type,
                    "expiry_date": exp_date.isoformat(),
                    "issuer": ev.issuer,
                    "reference_number": ev.reference_number,
                }

                if exp_date < ref_date:
                    item_info["status"] = "EXPIRED"
                    expired_items.append(item_info)
                    # Automatically update status in DB if not already flagged
                    if ev.status != "expired":
                        ev.status = "expired"
                elif exp_date <= warning_threshold:
                    days_remaining = (exp_date - ref_date).days
                    item_info["status"] = "EXPIRING_SOON"
                    item_info["days_remaining"] = days_remaining
                    expiring_soon_items.append(item_info)
                else:
                    item_info["status"] = "VALID"
                    valid_items.append(item_info)
            else:
                valid_items.append({
                    "id": ev.id,
                    "title": ev.title,
                    "evidence_type": ev.evidence_type,
                    "expiry_date": None,
                    "status": "VALID_PERMANENT",
                })

        session.commit()

        return {
            "organization_id": organization_id,
            "total_evidence_audited": len(evidence_items),
            "expired_count": len(expired_items),
            "expiring_soon_count": len(expiring_soon_items),
            "valid_count": len(valid_items),
            "expired": expired_items,
            "expiring_soon": expiring_soon_items,
            "valid": valid_items,
        }

    def detect_evidence_contradictions(
        self,
        organization_id: str,
        db: Optional[Session] = None,
    ) -> List[EvidenceContradiction]:
        """Analyze company evidence records and profile to detect conflicting factual claims."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        profile = (
            session.query(OrganizationProfile)
            .filter(OrganizationProfile.organization_id == organization_id)
            .first()
        )
        evidence_items = (
            session.query(CompanyEvidence)
            .filter(CompanyEvidence.organization_id == organization_id)
            .all()
        )

        contradictions: List[EvidenceContradiction] = []

        # 1. Compare financial metric values between evidence items
        financial_ev = [
            e for e in evidence_items
            if e.evidence_type in ("financial_audit", "annual_report") and e.extracted_data
        ]

        if len(financial_ev) >= 2:
            for i in range(len(financial_ev)):
                for j in range(i + 1, len(financial_ev)):
                    e1 = financial_ev[i]
                    e2 = financial_ev[j]
                    d1 = e1.extracted_data or {}
                    d2 = e2.extracted_data or {}

                    for key in ["turnover", "revenue", "net_profit", "turnover_fy23", "turnover_fy24"]:
                        v1 = d1.get(key)
                        v2 = d2.get(key)
                        if v1 is not None and v2 is not None and str(v1).strip() != str(v2).strip():
                            # Contradiction found!
                            existing = (
                                session.query(EvidenceContradiction)
                                .filter(
                                    EvidenceContradiction.organization_id == organization_id,
                                    EvidenceContradiction.evidence_id_1 == e1.id,
                                    EvidenceContradiction.evidence_id_2 == e2.id,
                                    EvidenceContradiction.claim_field == key,
                                )
                                .first()
                            )
                            if not existing:
                                contra = EvidenceContradiction(
                                    organization_id=organization_id,
                                    evidence_id_1=e1.id,
                                    evidence_id_2=e2.id,
                                    claim_field=key,
                                    value_1=str(v1),
                                    value_2=str(v2),
                                    contradiction_severity="Critical",
                                    status="Open",
                                    resolution_notes="Discrepancy in reported financial metrics across audit documents.",
                                )
                                session.add(contra)
                                contradictions.append(contra)

        # 2. Check profile vs evidence certifications
        if profile and profile.certifications:
            cert_ev = [
                e for e in evidence_items
                if e.evidence_type == "certification"
            ]
            for cert_name in profile.certifications:
                matching_ev = [
                    e for e in cert_ev
                    if cert_name.lower() in e.title.lower() or (e.extracted_data and cert_name.lower() in str(e.extracted_data).lower())
                ]
                for m in matching_ev:
                    if m.status == "expired" and m.expiry_date:
                        # Profile claims active certification, but evidence is expired
                        existing = (
                            session.query(EvidenceContradiction)
                            .filter(
                                EvidenceContradiction.organization_id == organization_id,
                                EvidenceContradiction.evidence_id_1 == m.id,
                                EvidenceContradiction.claim_field == f"cert_status_{cert_name}",
                            )
                            .first()
                        )
                        if not existing:
                            contra = EvidenceContradiction(
                                organization_id=organization_id,
                                evidence_id_1=m.id,
                                evidence_id_2=None,
                                claim_field=f"cert_status_{cert_name}",
                                value_1=f"Profile claims active: {cert_name}",
                                value_2=f"Certificate expired on {m.expiry_date.strftime('%Y-%m-%d')}",
                                contradiction_severity="High",
                                status="Open",
                                resolution_notes="Organization profile claims active certification but repository evidence shows expired status.",
                            )
                            session.add(contra)
                            contradictions.append(contra)

        session.commit()
        for c in contradictions:
            session.refresh(c)
        return contradictions

    def resolve_contradiction(
        self,
        contradiction_id: str,
        resolution_notes: str,
        resolved_by: str,
        status: str = "Resolved",
        db: Optional[Session] = None,
    ) -> EvidenceContradiction:
        """Record formal human resolution or explanation for an identified evidence contradiction."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        record = session.query(EvidenceContradiction).filter(EvidenceContradiction.id == contradiction_id).first()
        if not record:
            raise ValueError(f"EvidenceContradiction '{contradiction_id}' not found.")

        record.status = status
        record.resolution_notes = resolution_notes
        record.resolved_by = resolved_by
        record.resolved_at = utcnow()
        record.updated_at = utcnow()

        session.commit()
        session.refresh(record)
        logger.info("Evidence contradiction %s resolved by %s with status %s", contradiction_id, resolved_by, status)
        return record

    def record_claim_lineage(
        self,
        tender_id: str,
        claim_text: str,
        evidence_extract: str,
        proposal_id: Optional[str] = None,
        requirement_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        section_number: Optional[str] = None,
        review_status: str = "verified",
        auditor_verdict: Optional[str] = "Ready for Submission",
        approval_status: str = "pending",
        db: Optional[Session] = None,
    ) -> ClaimLineage:
        """Create end-to-end cryptographic proof link lineage:
        Requirement -> Evidence -> Extract -> Claim -> Review -> Approved Section.
        """
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        # Compute deterministic SHA-256 lineage hash
        payload = (
            f"{tender_id}|{proposal_id or ''}|{requirement_id or ''}|"
            f"{evidence_id or ''}|{section_number or ''}|{claim_text.strip()}|{evidence_extract.strip()}"
        )
        lineage_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        # Check if identical lineage exists
        existing = (
            session.query(ClaimLineage)
            .filter(ClaimLineage.lineage_hash == lineage_hash)
            .first()
        )
        if existing:
            existing.review_status = review_status
            existing.auditor_verdict = auditor_verdict
            existing.approval_status = approval_status
            existing.updated_at = utcnow()
            session.commit()
            session.refresh(existing)
            return existing

        lineage = ClaimLineage(
            tender_id=tender_id,
            proposal_id=proposal_id,
            requirement_id=requirement_id,
            evidence_id=evidence_id,
            section_number=section_number,
            claim_text=claim_text,
            evidence_extract=evidence_extract,
            review_status=review_status,
            auditor_verdict=auditor_verdict,
            approval_status=approval_status,
            lineage_hash=lineage_hash,
        )
        session.add(lineage)
        session.commit()
        session.refresh(lineage)
        return lineage

    def get_lineage_chain(
        self,
        tender_id: str,
        proposal_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve complete structured lineage graph for all claims in a tender/proposal."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        query = session.query(ClaimLineage).filter(ClaimLineage.tender_id == tender_id)
        if proposal_id:
            query = query.filter(ClaimLineage.proposal_id == proposal_id)

        lineages = query.all()
        chain: List[Dict[str, Any]] = []

        for item in lineages:
            req_info = None
            if item.requirement:
                req_info = {
                    "id": item.requirement.id,
                    "category": item.requirement.category,
                    "classification": item.requirement.classification,
                    "description": item.requirement.description,
                }

            ev_info = None
            if item.evidence:
                ev_info = {
                    "id": item.evidence.id,
                    "title": item.evidence.title,
                    "evidence_type": item.evidence.evidence_type,
                    "issuer": item.evidence.issuer,
                    "reference_number": item.evidence.reference_number,
                    "status": item.evidence.status,
                }

            chain.append({
                "lineage_id": item.id,
                "lineage_hash": item.lineage_hash,
                "section_number": item.section_number,
                "claim_text": item.claim_text,
                "evidence_extract": item.evidence_extract,
                "review_status": item.review_status,
                "auditor_verdict": item.auditor_verdict,
                "approval_status": item.approval_status,
                "requirement": req_info,
                "evidence": ev_info,
                "created_at": item.created_at.isoformat(),
            })

        return chain

    def invalidate_on_evidence_change(
        self,
        evidence_id: str,
        reason: str = "Evidence document status modified or revoked.",
        db: Optional[Session] = None,
    ) -> int:
        """Find all active proposal claims tied to an updated/revoked evidence record and invalidate their approval."""
        session = db or self.db
        if not session:
            raise ValueError("Database session required.")

        affected_lineages = (
            session.query(ClaimLineage)
            .filter(
                ClaimLineage.evidence_id == evidence_id,
                ClaimLineage.approval_status != "invalidated",
            )
            .all()
        )

        invalidated_count = len(affected_lineages)
        for lin in affected_lineages:
            lin.approval_status = "invalidated"
            lin.review_status = "unreviewed"
            lin.updated_at = utcnow()

        session.commit()
        logger.warning(
            "Invalidated %d claim lineages tied to evidence %s. Reason: %s",
            invalidated_count,
            evidence_id,
            reason,
        )
        return invalidated_count
