"""
Unit Tests: AI Provider Abstraction, Schema Validation, & Graceful Degradation.
"""

import asyncio
import pytest
from backend.app.core.exceptions import AIConfigurationRequiredError
from backend.app.domain.intelligence.models import (
    ExtractedRequirement,
    StructuredTenderIntelligence,
    TenderGeneralInfo,
)
from backend.app.infrastructure.ai.factory import MissingConfigProvider, get_ai_provider
from backend.app.infrastructure.ai.mock_adapter import MockAIProvider


def test_mock_ai_provider_extracts_real_clauses():
    async def _test():
        provider = MockAIProvider()
        doc_text = (
            "Request for Proposal: Tender No: RFP-2026-CLOUD-99\n"
            "Issued by: Department of Technology\n"
            "Clause 1: Minimum annual turnover of USD 5,000,000 required in the last 3 years.\n"
            "Clause 2: Bidder must have 7 years of experience in distributed cloud deployments.\n"
            "Clause 3: Bid Security / EMD deposit of USD 25,000 must accompany technical proposal.\n"
        )

        structured, meta = await provider.extract_intelligence(
            document_text=doc_text,
            prompt_template="{document_content}",
            parameters={},
        )

        assert isinstance(structured, StructuredTenderIntelligence)
        assert structured.general_info.reference_number == "RFP-2026-CLOUD-99"
        assert len(structured.requirements) >= 3

        # Check requirement provenance
        turnover_req = next((r for r in structured.requirements if "turnover" in r.source_excerpt.lower()), None)
        assert turnover_req is not None
        assert turnover_req.category == "eligibility"
        assert turnover_req.source_page == 1
        assert "5,000,000" in turnover_req.source_excerpt

    asyncio.run(_test())


def test_missing_config_provider_raises():
    async def _test():
        missing_provider = MissingConfigProvider()
        with pytest.raises(AIConfigurationRequiredError):
            await missing_provider.extract_intelligence("text", "tmpl", {})

    asyncio.run(_test())


def test_structured_intelligence_schema_validation():
    gen_info = TenderGeneralInfo(
        title="Smart City Infrastructure",
        reference_number="SC-2026-01",
        estimated_value=12500000.0,
    )
    req = ExtractedRequirement(
        category="eligibility",
        classification="mandatory",
        description="ISO 27001 Certification Required",
        source_page=3,
        source_excerpt="Bidder must submit copy of valid ISO 27001 certificate.",
        confidence_score=0.98,
    )
    payload = StructuredTenderIntelligence(general_info=gen_info, requirements=[req])
    assert payload.schema_version == "1.0.0"
    assert len(payload.requirements) == 1
    assert payload.requirements[0].confidence_score == 0.98
