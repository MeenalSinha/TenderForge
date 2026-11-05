"""
Mock / Deterministic AI Provider for Local Development, Testing, and Demos.
Extracts structured intelligence strictly from real clauses identified in the document text.
Includes adversarial prompt injection filtering.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from backend.app.domain.intelligence.models import (
    ExtractedRequirement,
    StructuredTenderIntelligence,
    TenderGeneralInfo,
)
from backend.app.infrastructure.ai.base import BaseAIProvider

INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"disregard\s+(?:all\s+)?prior",
    r"output\s+that\s+this",
    r"you\s+are\s+now",
    r"pre-approved\s+for",
    r"system\s+prompt",
]


def is_adversarial_injection(text: str) -> bool:
    """Detect if clause attempts to manipulate the AI system."""
    lower = text.lower()
    return any(re.search(pat, lower) is not None for pat in INJECTION_PATTERNS)


class MockAIProvider(BaseAIProvider):
    """Deterministic intelligence extractor parsing real clauses directly from document text."""

    provider_id: str = "mock"
    model_id: str = "deterministic-tender-extractor-v1"

    async def extract_intelligence(
        self,
        document_text: str,
        prompt_template: str,
        parameters: Dict[str, Any],
    ) -> Tuple[StructuredTenderIntelligence, Dict[str, Any]]:
        clean_text = document_text or ""
        lines = [ln.strip() for ln in clean_text.splitlines() if ln.strip()]

        # Filter out obvious injection lines before metadata extraction
        safe_lines = [ln for ln in lines if not is_adversarial_injection(ln)]

        # 1. Extract General Info
        title: Optional[str] = None
        ref_num: Optional[str] = None
        authority: Optional[str] = None
        est_val: Optional[float] = None

        for line in safe_lines[:10]:
            if any(k in line.lower() for k in ["tender", "rfp", "request for proposal", "bidding document", "procurement"]):
                title = line
                break
        if not title and safe_lines:
            title = safe_lines[0]

        ref_match = re.search(r"(?:Tender\s*(?:No|Ref|Notice)?|RFP\s*(?:No|Ref)?|NIT\s*(?:No)?)[.:\s]+([A-Za-z0-9\-_/]+)", clean_text, re.IGNORECASE)
        if ref_match and not is_adversarial_injection(ref_match.group(0)):
            ref_num = ref_match.group(1).strip()

        auth_match = re.search(r"(?:Issued\s+by|Authority|Client|Employer|Department)[.:\s]+([^\n\r]+)", clean_text, re.IGNORECASE)
        if auth_match and not is_adversarial_injection(auth_match.group(0)):
            authority = auth_match.group(1).strip()[:150]

        val_match = re.search(r"(?:Estimated\s+(?:Cost|Value)|Budget|Contract\s+Value)[.:\s]+(?:USD|INR|EUR|\$)?\s*([0-9,]+(?:\.[0-9]+)?)", clean_text, re.IGNORECASE)
        if val_match and not is_adversarial_injection(val_match.group(0)):
            try:
                est_val = float(val_match.group(1).replace(",", ""))
            except ValueError:
                est_val = None

        general_info = TenderGeneralInfo(
            title=title,
            reference_number=ref_num,
            issuing_authority=authority,
            procurement_category="Procurement & Services",
            description=safe_lines[1][:250] if len(safe_lines) > 1 else None,
            estimated_value=est_val,
            currency="USD",
            submission_deadline=None,
        )

        # 2. Extract Requirements strictly based on real clauses in document
        requirements: List[ExtractedRequirement] = []

        patterns = [
            (
                "eligibility",
                "mandatory",
                r"([^.\n]*?(?:turnover|financial\s+capacity|annual\s+revenue)[^.\n]*?\.)",
                "Annual Financial Turnover Requirement",
            ),
            (
                "eligibility",
                "mandatory",
                r"([^.\n]*?(?:years\s+of\s+experience|past\s+experience|prior\s+work|track\s+record)[^.\n]*?\.)",
                "Minimum Prior Experience Requirement",
            ),
            (
                "eligibility",
                "mandatory",
                r"([^.\n]*?(?:iso\s*\d+|certification|accreditation|licensed)[^.\n]*?\.)",
                "Mandatory Certification / Quality Standard",
            ),
            (
                "financial",
                "mandatory",
                r"([^.\n]*?(?:earnest\s+money|emd|bid\s+security|performance\s+guarantee|security\s+deposit)[^.\n]*?\.)",
                "Bid Security / EMD Deposit Requirement",
            ),
            (
                "financial",
                "mandatory",
                r"([^.\n]*?(?:payment\s+terms|milestone\s+payment|invoicing)[^.\n]*?\.)",
                "Contract Payment & Invoicing Terms",
            ),
            (
                "technical",
                "mandatory",
                r"([^.\n]*?(?:scope\s+of\s+work|technical\s+specification|deliverable|sla|service\s+level)[^.\n]*?\.)",
                "Technical Scope & Deliverables",
            ),
            (
                "submission",
                "mandatory",
                r"([^.\n]*?(?:submission\s+deadline|two-envelope|sealed\s+cover|mandatory\s+documents|tender\s+fee)[^.\n]*?\.)",
                "Tender Submission Guidelines",
            ),
        ]

        seen_excerpts = set()
        for cat, classification, regex, desc_prefix in patterns:
            matches = re.finditer(regex, clean_text, re.IGNORECASE)
            for m in matches:
                excerpt = m.group(1).strip()
                if excerpt and len(excerpt) > 20 and excerpt not in seen_excerpts:
                    if is_adversarial_injection(excerpt):
                        continue
                    seen_excerpts.add(excerpt)
                    offset = m.start()
                    requirements.append(
                        ExtractedRequirement(
                            category=cat,
                            classification=classification,
                            description=f"{desc_prefix}: {excerpt[:120]}...",
                            source_page=1,
                            source_offset=offset,
                            source_excerpt=excerpt,
                            confidence_score=0.92,
                        )
                    )

        # Fallback to substantial safe paragraph if nothing matched
        if not requirements and safe_lines:
            for p in safe_lines:
                if len(p) > 50 and not is_adversarial_injection(p):
                    requirements.append(
                        ExtractedRequirement(
                            category="general",
                            classification="mandatory",
                            description="General Tender Scope Requirement",
                            source_page=1,
                            source_offset=clean_text.find(p),
                            source_excerpt=p,
                            confidence_score=0.85,
                        )
                    )
                    break

        structured = StructuredTenderIntelligence(
            schema_version="1.0.0",
            general_info=general_info,
            requirements=requirements,
        )

        metadata = {
            "provider": self.provider_id,
            "model": self.model_id,
            "requirements_extracted": len(requirements),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return structured, metadata
