# TENDERFORGE — EVIDENCE REPOSITORY & PROFILE GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Business Problem

Responding to competitive tenders requires assembling dozens of corporate credentials, past project records, financial audits, quality certifications, and statutory filings. In most enterprises, these documents are scattered across departments, outdated, or difficult to correlate against specific tender requirements.

The **Evidence Repository** provides a centralized, structured database of verified company artifacts, directly connected to the ProofLink Evidence Traceability Engine.

---

## 2. Organization Profile Architecture

The `OrganizationProfile` model stores core corporate baseline data:
- **Legal Entity Information:** `legal_name`, `trade_name`, `registration_number`, `tax_id`, `jurisdiction`, `headquarters_address`.
- **Financial Metrics:** Annual turnover per fiscal year, 3-year average turnover, net worth, credit ratings.
- **Accreditations & Certifications:** Active quality and security certifications (ISO 9001, ISO 27001, CMMI, SOC 2).
- **Core Capabilities:** Primary technology domains and delivery capabilities.

---

## 3. Evidence Classification Taxonomy

Company evidence records are categorized into 7 standardized types:

| Evidence Type | Examples | Key Extracted Metrics |
| :--- | :--- | :--- |
| `financial_audit` | Annual reports, P&L statements, CPA audit reports | `annual_turnover`, `average_turnover`, `net_profit_margin`, `net_worth` |
| `certification` | ISO 9001, ISO 27001, CMMI Level 3, SOC 2 | `issuer`, `reference_number`, `issue_date`, `expiry_date`, `accreditation_scope` |
| `past_project` | Client completion certificates, reference letters | `client_name`, `contract_value`, `start_date`, `completion_date`, `deliverables` |
| `statutory_registration` | Certificate of incorporation, tax clearance | `registration_number`, `tax_id`, `jurisdiction`, `good_standing_status` |
| `policy` | Information security policy, environmental policy | `policy_scope`, `version`, `effective_date`, `approval_authority` |
| `cv_personnel` | Key personnel resumes, professional licenses | `name`, `role`, `years_experience`, `certifications` (PMP, CISSP) |
| `other` | Solvency letters, bank guarantees, awards | `bank_name`, `credit_line_amount`, `expiry_date` |

---

## 4. Evidence Ingestion Pipeline

Evidence documents (PDF, DOCX, XLSX, TXT) are ingested using Phase 1 document parsers:
1. **Document Registration:** Computes SHA-256 hash to eliminate duplicate files; validates MIME signature.
2. **Text Parsing & Segmentation:** PyMuPDF, python-docx, or openpyxl extracts text and tables.
3. **Fact Extraction:** Identifies key values (revenue numbers, validity dates, certificate numbers).
4. **Metadata Tagging:** Attaches searchable tags (e.g. `iso 9001`, `financial`, `defense`) for retrieval.

---

## 5. API Endpoints

- `POST /api/v1/organizations/{id}/profile`: Create or update organization profile.
- `GET /api/v1/organizations/{id}/profile`: Retrieve current profile.
- `POST /api/v1/organizations/{id}/evidence`: Ingest new evidence record or upload evidence document.
- `GET /api/v1/organizations/{id}/evidence`: Search evidence by query string, type, or tags.
- `GET /api/v1/evidence/{id}`: Retrieve detailed evidence record.
