"""
ProofLink Evidence Traceability Engine.
Connects tender requirements and proposal claims to verifiable company evidence.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError
from backend.app.core.logging import get_logger
from backend.app.infrastructure.database.models import (
    CompanyEvidence,
    EvidenceRequirementLink,
    Organization,
    OrganizationProfile,
    Tender,
    TenderRequirement,
)

logger = get_logger("prooflink_service")


class ProofLinkStatus:
    VERIFIED = "Verified"
    HUMAN_CONFIRMED = "Human Confirmed"
    PENDING = "Pending"
    UNSUPPORTED = "Unsupported"
    CONTRADICTED = "Contradicted"


class ProofLinkService:
    """Matches tender requirements against company evidence with traceable proof links."""

    def match_requirement_to_evidence(
        self,
        db: Session,
        requirement: TenderRequirement,
        organization_id: str,
    ) -> List[EvidenceRequirementLink]:
        """Analyze a requirement against company evidence and generate traceable links."""
        # Retrieve all evidence for the organization
        evidence_list = db.query(CompanyEvidence).filter(
            CompanyEvidence.organization_id == organization_id
        ).all()

        profile = db.query(OrganizationProfile).filter(
            OrganizationProfile.organization_id == organization_id
        ).first()

        req_text = (requirement.description + " " + requirement.source_excerpt).lower()
        matched_links: List[EvidenceRequirementLink] = []

        # 1. Turnover / Financial Matching
        if "turnover" in req_text or "revenue" in req_text or "financial" in req_text:
            # Check financial audits in evidence
            financial_ev = [e for e in evidence_list if e.evidence_type == "financial_audit"]
            extracted_num = self._extract_amount(req_text)
            
            if financial_ev:
                best_ev = financial_ev[0]
                ev_amount = best_ev.extracted_data.get("average_turnover") or best_ev.extracted_data.get("annual_turnover")
                
                if extracted_num and ev_amount:
                    if float(ev_amount) >= float(extracted_num):
                        status = ProofLinkStatus.VERIFIED
                        notes = f"Audited turnover (${ev_amount:,.2f}) meets or exceeds requirement (${extracted_num:,.2f})."
                    else:
                        status = ProofLinkStatus.CONTRADICTED
                        notes = f"Audited turnover (${ev_amount:,.2f}) is below mandatory threshold (${extracted_num:,.2f})."
                else:
                    status = ProofLinkStatus.VERIFIED if best_ev.status == "valid" else ProofLinkStatus.PENDING
                    notes = f"Financial audit report on file: {best_ev.title}"

                link = EvidenceRequirementLink(
                    requirement_id=requirement.id,
                    evidence_id=best_ev.id,
                    match_status=status,
                    confidence_score=0.95,
                    source_excerpt=best_ev.summary or best_ev.title,
                    notes=notes,
                )
                matched_links.append(link)

        # 2. Certification Matching (e.g. ISO 9001, ISO 27001)
        iso_match = re.search(r"iso\s*(\d{4,5})", req_text)
        if iso_match:
            iso_code = f"iso {iso_match.group(1)}"
            cert_ev = [
                e for e in evidence_list 
                if e.evidence_type == "certification" and (iso_code in e.title.lower() or (e.tags and any(iso_code in str(t).lower() for t in e.tags)))
            ]
            if cert_ev:
                for ce in cert_ev:
                    is_expired = ce.status == "expired"
                    if ce.expiry_date:
                        exp = ce.expiry_date if ce.expiry_date.tzinfo else ce.expiry_date.replace(tzinfo=timezone.utc)
                        if exp < datetime.now(timezone.utc):
                            is_expired = True
                    status = ProofLinkStatus.CONTRADICTED if is_expired else ProofLinkStatus.VERIFIED
                    notes = "Certificate expired; renewal needed." if is_expired else f"Valid certificate verified from {ce.issuer}."
                    matched_links.append(
                        EvidenceRequirementLink(
                            requirement_id=requirement.id,
                            evidence_id=ce.id,
                            match_status=status,
                            confidence_score=0.98,
                            source_excerpt=ce.summary or ce.title,
                            notes=notes,
                        )
                    )

        # 3. Experience / Past Projects Matching
        if "experience" in req_text or "track record" in req_text or "prior project" in req_text:
            years_req = self._extract_years(req_text)
            project_ev = [e for e in evidence_list if e.evidence_type in ("past_project", "statutory_registration")]
            
            # Check company incorporation/experience years from profile
            if profile and profile.incorporation_date and years_req:
                inc_date = profile.incorporation_date if profile.incorporation_date.tzinfo else profile.incorporation_date.replace(tzinfo=timezone.utc)
                years_in_business = (datetime.now(timezone.utc) - inc_date).days // 365
                if years_in_business >= years_req:
                    status = ProofLinkStatus.VERIFIED
                    notes = f"Organization has {years_in_business} years active in business (required: {years_req} years)."
                else:
                    status = ProofLinkStatus.CONTRADICTED
                    notes = f"Organization in business for {years_in_business} years, failing requirement of {years_req} years."
            else:
                status = ProofLinkStatus.VERIFIED if project_ev else ProofLinkStatus.UNSUPPORTED
                notes = f"Found {len(project_ev)} past project completion records." if project_ev else "No project records found."

            if project_ev:
                for pe in project_ev[:2]:
                    matched_links.append(
                        EvidenceRequirementLink(
                            requirement_id=requirement.id,
                            evidence_id=pe.id,
                            match_status=status,
                            confidence_score=0.90,
                            source_excerpt=pe.summary or pe.title,
                            notes=notes,
                        )
                    )

        # 4. Bid Security / Financial Deposit
        if "bid security" in req_text or "earnest money" in req_text or "emd" in req_text:
            sec_ev = [e for e in evidence_list if "bank" in e.title.lower() or "guarantee" in e.title.lower() or "solvency" in e.title.lower()]
            if sec_ev:
                matched_links.append(
                    EvidenceRequirementLink(
                        requirement_id=requirement.id,
                        evidence_id=sec_ev[0].id,
                        match_status=ProofLinkStatus.VERIFIED,
                        confidence_score=0.92,
                        source_excerpt=sec_ev[0].summary or sec_ev[0].title,
                        notes="Solvency certificate / bank line available for bid bond issuance.",
                    )
                )

        # 5. General fallback keyword search
        if not matched_links:
            candidates = []
            for ev in evidence_list:
                ev_text = (ev.title + " " + (ev.summary or "")).lower()
                # Check overlapping terms
                tokens = set(req_text.split())
                ev_tokens = set(ev_text.split())
                overlap = tokens.intersection(ev_tokens)
                if len(overlap) >= 3:
                    candidates.append((ev, len(overlap)))
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            for ev, score in candidates[:1]:
                matched_links.append(
                    EvidenceRequirementLink(
                        requirement_id=requirement.id,
                        evidence_id=ev.id,
                        match_status=ProofLinkStatus.PENDING,
                        confidence_score=0.65,
                        source_excerpt=ev.summary or ev.title,
                        notes="Candidate evidence match identified via keyword correlation; human confirmation recommended.",
                    )
                )

        # If still no matches found, create an UNSUPPORTED indicator link (linked to a generic or placeholder evidence or logged)
        if not matched_links and evidence_list:
            # Link to first evidence with UNSUPPORTED status
            matched_links.append(
                EvidenceRequirementLink(
                    requirement_id=requirement.id,
                    evidence_id=evidence_list[0].id,
                    match_status=ProofLinkStatus.UNSUPPORTED,
                    confidence_score=0.0,
                    source_excerpt=None,
                    notes="No supporting corporate records found in repository for this mandatory requirement.",
                )
            )

        # Persist links
        for link in matched_links:
            # Check if link already exists
            existing = db.query(EvidenceRequirementLink).filter(
                EvidenceRequirementLink.requirement_id == link.requirement_id,
                EvidenceRequirementLink.evidence_id == link.evidence_id,
            ).first()
            if not existing:
                db.add(link)
        db.commit()
        return matched_links

    def match_all_tender_requirements(
        self,
        db: Session,
        tender_id: str,
        organization_id: str,
    ) -> List[EvidenceRequirementLink]:
        """Run ProofLink matching for all requirements of a tender."""
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise EntityNotFoundError(f"Tender '{tender_id}' not found.")

        requirements = db.query(TenderRequirement).filter(
            TenderRequirement.tender_id == tender_id
        ).all()

        all_links = []
        for req in requirements:
            links = self.match_requirement_to_evidence(db, req, organization_id)
            all_links.extend(links)

        logger.info(f"Generated {len(all_links)} ProofLink links for tender {tender_id}.")
        return all_links

    def confirm_evidence_link(
        self,
        db: Session,
        link_id: str,
        user_id: str,
        status: str = ProofLinkStatus.HUMAN_CONFIRMED,
        notes: Optional[str] = None,
    ) -> EvidenceRequirementLink:
        """Allow an authorized human to confirm, reject, or adjust an evidence link."""
        link = db.query(EvidenceRequirementLink).filter(EvidenceRequirementLink.id == link_id).first()
        if not link:
            raise EntityNotFoundError(f"Evidence link '{link_id}' not found.")

        link.match_status = status
        link.verified_by_user_id = user_id
        link.verified_at = datetime.now(timezone.utc)
        if notes:
            link.notes = (link.notes or "") + f" [User Note: {notes}]"

        db.commit()
        db.refresh(link)
        logger.info(f"Human confirmation recorded on ProofLink {link_id} by {user_id}: {status}")
        return link

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract currency amount from text (e.g., '$2,000,000' or 'USD 2,000,000')."""
        match = re.search(r"(?:usd|\$)\s*([\d,]+(?:\.\d+)?)", text)
        if match:
            clean = match.group(1).replace(",", "")
            try:
                return float(clean)
            except ValueError:
                return None
        return None

    def _extract_years(self, text: str) -> Optional[int]:
        """Extract number of years from text (e.g. '5 years')."""
        match = re.search(r"(\d+)\s*(?:years|year|yrs)", text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
