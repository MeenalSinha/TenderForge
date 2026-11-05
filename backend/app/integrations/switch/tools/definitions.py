"""
TenderForge Tool Definitions for Switch Agents & Model Context Protocol (MCP).
"""

from __future__ import annotations

from typing import Any, Dict, List

# Standard MCP / Switch tool schema representations
TOOLS_REGISTRY: List[Dict[str, Any]] = [
    {
        "name": "create_tender_workspace",
        "description": "Create a dedicated workspace for a tender response.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Workspace name"},
                "organization_id": {"type": "string", "description": "Organization ID"},
                "description": {"type": "string", "description": "Optional description"},
            },
            "required": ["name", "organization_id"],
        },
    },
    {
        "name": "upload_tender_document",
        "description": "Upload and parse a tender document (PDF, DOCX, TXT, XLSX).",
        "parameters": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Workspace ID"},
                "filename": {"type": "string", "description": "Filename with extension"},
                "content_base64": {"type": "string", "description": "Base64 encoded file content or text content"},
                "category": {"type": "string", "description": "Category e.g. tender_notice, technical_spec"},
            },
            "required": ["workspace_id", "filename", "content_base64"],
        },
    },
    {
        "name": "upload_company_evidence",
        "description": "Upload and register an organizational proof document (audit, ISO certificate, past project, policy).",
        "parameters": {
            "type": "object",
            "properties": {
                "organization_id": {"type": "string", "description": "Organization ID"},
                "workspace_id": {"type": "string", "description": "Workspace ID"},
                "title": {"type": "string", "description": "Evidence title"},
                "evidence_type": {"type": "string", "description": "certification, financial_audit, past_project, statutory_registration, policy"},
                "filename": {"type": "string", "description": "Document filename"},
                "content_base64": {"type": "string", "description": "Base64 encoded file content"},
                "issuer": {"type": "string", "description": "Issuing authority"},
                "reference_number": {"type": "string", "description": "Certificate or registration number"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Searchable tags"},
            },
            "required": ["organization_id", "workspace_id", "title", "evidence_type", "filename", "content_base64"],
        },
    },
    {
        "name": "get_tender_overview",
        "description": "Retrieve comprehensive tender metadata, dates, authority, documents, and current status.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "analyze_tender",
        "description": "Trigger the Tender Analyst to extract structured requirements with exact page and character coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "get_tender_requirements",
        "description": "Retrieve extracted requirements filtered by category or classification.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
                "category": {"type": "string", "description": "Optional category filter: eligibility, technical, financial"},
                "classification": {"type": "string", "description": "Optional classification: mandatory, optional"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "search_company_evidence",
        "description": "Search the company repository for verifiable proof records.",
        "parameters": {
            "type": "object",
            "properties": {
                "organization_id": {"type": "string", "description": "Organization ID"},
                "query": {"type": "string", "description": "Search keyword or requirement description"},
                "evidence_type": {"type": "string", "description": "Optional type filter: certification, past_project, financial_audit"},
            },
            "required": ["organization_id"],
        },
    },
    {
        "name": "get_evidence_details",
        "description": "Fetch detailed information, metrics, and document links for a specific evidence item.",
        "parameters": {
            "type": "object",
            "properties": {
                "evidence_id": {"type": "string", "description": "Evidence ID"},
            },
            "required": ["evidence_id"],
        },
    },
    {
        "name": "evaluate_compliance",
        "description": "Evaluate all tender requirements against company evidence, computing the compliance matrix.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "get_compliance_matrix",
        "description": "Retrieve the latest compliance matrix, status, risk levels, and remedial action items.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "create_proposal_draft",
        "description": "Generate an evidence-backed proposal draft with embedded ProofLink citations.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
                "title": {"type": "string", "description": "Optional proposal title"},
            },
            "required": ["tender_id"],
        },
    },
    {
        "name": "get_proposal_revision",
        "description": "Retrieve proposal content, claims, and ProofLink citations by version number.",
        "parameters": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string", "description": "Proposal ID"},
                "version": {"type": "integer", "description": "Optional version number (defaults to latest)"},
            },
            "required": ["proposal_id"],
        },
    },
    {
        "name": "audit_proposal",
        "description": "Trigger the independent Bid Auditor to inspect veracity, unsupported claims, and readiness score.",
        "parameters": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string", "description": "Proposal ID"},
            },
            "required": ["proposal_id"],
        },
    },
    {
        "name": "get_audit_report",
        "description": "Retrieve the latest audit findings, claim statistics, and submission verdict.",
        "parameters": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string", "description": "Proposal ID"},
            },
            "required": ["proposal_id"],
        },
    },
    {
        "name": "request_human_review",
        "description": "Post a high-priority review request to the Tender War Room for human decision or clarification.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
                "reason": {"type": "string", "description": "Reason for human review"},
                "severity": {"type": "string", "description": "Critical, Major, Minor"},
                "proposal_id": {"type": "string", "description": "Optional Proposal ID"},
            },
            "required": ["tender_id", "reason"],
        },
    },
    {
        "name": "record_human_decision",
        "description": "Record an immutable human approval or rejection decision with cryptographic signature hash.",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
                "proposal_id": {"type": "string", "description": "Proposal ID"},
                "user_id": {"type": "string", "description": "Human user ID"},
                "user_name": {"type": "string", "description": "Human user display name"},
                "user_role": {"type": "string", "description": "User authority role (e.g. Bid Director)"},
                "decision": {"type": "string", "description": "Approved, Rejected, Changes Requested"},
                "comments": {"type": "string", "description": "Justification and review notes"},
            },
            "required": ["tender_id", "proposal_id", "user_id", "user_name", "user_role", "decision", "comments"],
        },
    },
    {
        "name": "export_bid_package",
        "description": "Export the complete submission-ready ZIP bundle (DOCX, XLSX matrix, audit, and human certificate).",
        "parameters": {
            "type": "object",
            "properties": {
                "tender_id": {"type": "string", "description": "Tender ID"},
                "proposal_id": {"type": "string", "description": "Proposal ID"},
                "require_human_approval": {"type": "boolean", "description": "Whether to enforce human sign-off (default True)"},
            },
            "required": ["tender_id", "proposal_id"],
        },
    },
]


def get_mcp_tools() -> List[Dict[str, Any]]:
    """Return tool schemas formatted for Model Context Protocol (MCP)."""
    return TOOLS_REGISTRY
