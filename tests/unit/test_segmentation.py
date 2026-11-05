"""
Unit Tests: Text Normalizer & Intelligent Segmentation.
"""

from backend.app.domain.documents.segmentation import (
    DocumentSegment,
    IntelligentSegmenter,
    TextNormalizer,
)
from backend.app.infrastructure.parsers.base import ParsedBlock, ParsedDocument


def test_text_normalizer():
    dirty = "Line 1   \r\n\r\n\r\n\r\nLine 2 \t\r\nLine 3"
    clean = TextNormalizer.normalize(dirty)
    assert "\r" not in clean
    assert "\n\n\n" not in clean
    assert clean.startswith("Line 1")
    assert clean.endswith("Line 3")


def test_intelligent_segmenter_preserves_page_and_offsets():
    blocks = [
        ParsedBlock(
            page_number=1,
            block_type="paragraph",
            text="Clause 1.1: The bidder must provide audited financial statements for the past 3 fiscal years.",
            section_title="Financial Qualification",
            char_offset=0,
        ),
        ParsedBlock(
            page_number=2,
            block_type="paragraph",
            text="Clause 2.1: Performance Security of 10% contract value is mandatory.",
            section_title="Security Deposit",
            char_offset=200,
        ),
    ]

    doc = ParsedDocument(
        filename="test.pdf",
        parser_name="TestParser",
        parser_version="1.0",
        total_pages=2,
        blocks=blocks,
        full_text="...",
    )

    segmenter = IntelligentSegmenter(chunk_size=150, chunk_overlap=30, min_chunk_size=20)
    segments = segmenter.segment_parsed_document(doc)

    assert len(segments) >= 2
    assert segments[0].page_number == 1
    assert segments[0].section_title == "Financial Qualification"
    assert "audited financial statements" in segments[0].content
    assert segments[1].page_number == 2
    assert segments[1].section_title == "Security Deposit"

