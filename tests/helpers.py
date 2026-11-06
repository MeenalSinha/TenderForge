"""
Synthetic Document Generators for Automated Tests.
"""

from __future__ import annotations

import io


def create_synthetic_pdf_bytes() -> bytes:
    """Generate in-memory PDF with 2 pages and realistic tender clauses."""
    import pymupdf

    doc = pymupdf.open()
    # Page 1
    p1 = doc.new_page()
    p1.insert_text(
        (50, 72),
        "SECTION 1: TENDER NOTICE\n"
        "Tender Ref: RFP-2026-001\n"
        "Clause 1.1: Minimum annual turnover of USD 2,000,000 required over the last 3 fiscal years.\n"
        "Clause 1.2: Bidder must have minimum 5 years of experience in enterprise systems.\n",
    )
    # Page 2
    p2 = doc.new_page()
    p2.insert_text(
        (50, 72),
        "SECTION 2: TECHNICAL SPECIFICATIONS & FINANCIAL TERMS\n"
        "Clause 2.1: The scope of work involves providing core high-availability servers and network switches.\n"
        "Clause 2.2: Earnest Money Deposit / EMD of USD 50,000 is mandatory.\n"
        "Clause 2.3: Valid ISO 9001 certification is mandatory.\n",
    )

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def create_synthetic_docx_bytes() -> bytes:
    """Generate in-memory DOCX with paragraphs and table."""
    import docx

    doc = docx.Document()
    doc.add_heading("Section 1: Scope of Work", level=1)
    doc.add_paragraph("The contractor shall implement enterprise networking infrastructure within 6 months.")
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Item"
    table.rows[0].cells[1].text = "Qty"
    table.rows[1].cells[0].text = "Core Switch"
    table.rows[1].cells[1].text = "4"

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def run_sync(coro):
    """
    Safely executes a coroutine synchronously without event loop deadlocks
    on Windows in Python 3.14.
    """
    try:
        return coro.send(None)
    except StopIteration as e:
        return e.value


