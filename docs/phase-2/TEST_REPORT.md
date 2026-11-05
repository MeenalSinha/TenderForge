# TENDERFORGE — PHASE 2 TEST REPORT

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  
**Test Status:** **100% PASS (46 / 46 TESTS PASSED) | 82% CODE COVERAGE**

---

## 1. Executive Summary

Phase 2 implementation includes a comprehensive automated test suite spanning unit, integration, API, and security domains.

All 46 test cases passed in under 4 seconds with 82% code coverage across 3,136 statements.

---

## 2. Test Execution Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-8.2.2, pluggy-1.6.0
rootdir: C:\Users\Meenal Sinha\Downloads\TenderForge
configfile: pytest.ini
plugins: anyio-4.12.0, asyncio-0.23.7, cov-7.1.0, mock-3.16.0
asyncio: mode=Mode.AUTO
collected 46 items

tests/api/test_documents_api.py::test_document_api_flow PASSED           [  2%]
tests/api/test_documents_api.py::test_document_upload_invalid_extension PASSED [  4%]
tests/api/test_health_api.py::test_health_endpoint PASSED                [  6%]
tests/api/test_health_api.py::test_ready_endpoint PASSED                 [  8%]
tests/api/test_missing_ai_config.py::test_graceful_handling_when_ai_not_configured PASSED [ 10%]
tests/api/test_phase2_api.py::test_phase2_api_endpoints_flow PASSED      [ 13%]
tests/api/test_tenders_api.py::test_tender_api_flow PASSED               [ 15%]
tests/integration/test_document_pipeline.py::test_document_full_ingestion_pipeline PASSED [ 17%]
tests/integration/test_document_pipeline.py::test_document_duplicate_rejection PASSED [ 19%]
tests/integration/test_phase2_workflow.py::test_complete_phase2_multi_agent_workflow PASSED [ 21%]
tests/integration/test_tender_pipeline.py::test_tender_pipeline_with_mock_ai PASSED [ 23%]
tests/security/test_security_attacks.py::test_path_traversal_attack PASSED [ 26%]
tests/security/test_security_attacks.py::test_mime_spoofing_attack PASSED [ 28%]
tests/security/test_security_attacks.py::test_oversized_upload_attack PASSED [ 30%]
tests/security/test_security_attacks.py::test_prompt_injection_in_document PASSED [ 32%]
tests/unit/test_agent_tools.py::test_mcp_tools_definitions_count PASSED  [ 34%]
tests/unit/test_agent_tools.py::test_agent_rbac_tool_execution PASSED    [ 36%]
tests/unit/test_ai_provider.py::test_mock_ai_provider_extracts_real_clauses PASSED [ 39%]
tests/unit/test_ai_provider.py::test_missing_config_provider_raises PASSED [ 41%]
tests/unit/test_ai_provider.py::test_structured_intelligence_schema_validation PASSED [ 43%]
tests/unit/test_approval_service.py::test_human_approval_lifecycle_and_signature_hash PASSED [ 45%]
tests/unit/test_approval_service.py::test_human_approval_requires_substantive_comments PASSED [ 47%]
tests/unit/test_audit_service.py::test_audit_proposal_with_contradicted_and_verified_claims PASSED [ 50%]
tests/unit/test_audit_service.py::test_audit_proposal_all_verified PASSED [ 52%]
tests/unit/test_compliance_service.py::test_compliance_matrix_evaluation PASSED [ 54%]
tests/unit/test_config.py::test_settings_load_defaults PASSED            [ 56%]
tests/unit/test_config.py::test_settings_masked_dict PASSED              [ 58%]
tests/unit/test_config.py::test_yaml_config_accessors PASSED             [ 60%]
tests/unit/test_evidence_service.py::test_organization_profile_lifecycle PASSED [ 63%]
tests/unit/test_evidence_service.py::test_company_evidence_registration_and_search PASSED [ 65%]
tests/unit/test_parsers.py::test_pdf_parser_success PASSED               [ 67%]
tests/unit/test_parsers.py::test_pdf_parser_empty_error PASSED           [ 69%]
tests/unit/test_parsers.py::test_docx_parser_success PASSED              [ 71%]
tests/unit/test_parsers.py::test_docx_parser_corrupted PASSED            [ 73%]
tests/unit/test_parsers.py::test_txt_parser_success PASSED               [ 76%]
tests/unit/test_parsers.py::test_csv_spreadsheet_parser PASSED           [ 78%]
tests/unit/test_prooflink_service.py::test_prooflink_turnover_matching PASSED [ 80%]
tests/unit/test_prooflink_service.py::test_prooflink_iso_certification_expiration PASSED [ 82%]
tests/unit/test_prooflink_service.py::test_prooflink_human_confirmation PASSED [ 84%]
tests/unit/test_proposal_service.py::test_proposal_drafting_and_docx_generation PASSED [ 86%]
tests/unit/test_security.py::test_sanitize_filename_path_traversal PASSED [ 89%]
tests/unit/test_security.py::test_sanitize_filename_special_chars PASSED [ 91%]
tests/unit/test_security.py::test_compute_sha256 PASSED                  [ 93%]
tests/unit/test_verify_file_signature PASSED           [ 95%]
tests/unit/test_segmentation.py::test_text_normalizer PASSED             [ 97%]
tests/unit/test_segmentation.py::test_intelligent_segmenter_preserves_page_and_offsets PASSED [100%]

============================= 46 passed in 3.99s ==============================
```

---

## 3. Code Coverage Highlights

- Total Statements Analyzed: 3,136
- Statement Coverage: **82%**
- Key Modules Tested:
  - `backend/app/services/proposal_service.py`: 97%
  - `backend/app/services/document_service.py`: 95%
  - `backend/app/services/export_service.py`: 94%
  - `backend/app/services/audit_service.py`: 85%
  - `backend/app/services/prooflink_service.py`: 83%
  - `backend/app/services/compliance_service.py`: 81%
  - `backend/app/domain/agents/registry.py`: 77%
