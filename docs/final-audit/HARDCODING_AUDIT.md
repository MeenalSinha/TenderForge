# TenderForge — Hardcoding, Configuration & Secrets Audit Report

**Project Identity:** TenderForge — *From Tender to Trustworthy Proposal*  
**Scope:** Static Analysis & Grep Audit for Hardcoded Credentials, URLs, and Mock Bypasses  
**Audit Date:** November 2026  
**Status:** FULLY COMPLIANT (ZERO HARDCODED SECRETS OR MOCK SHORTCUTS)  

---

## 1. Executive Summary

A full-codebase static audit was conducted to identify any hardcoded API keys, JWT secrets, database connection strings, absolute local paths, or mock bypass shortcuts in production code. 

**Audit Conclusion**:
- Zero hardcoded plain-text passwords or secret keys exist in production application code.
- All secrets and runtime parameters are sourced through `backend/app/core/config.py` using Pydantic Settings with environment variable overrides.
- Development and demo shortcuts (such as synthetic fallback admin profiles and hardcoded client role headers) have been permanently removed.

---

## 2. Configuration & Secrets Management Audit

### 2.1 Centralized Settings Architecture (`backend/app/core/config.py`)
All system configurations adhere to Twelve-Factor App principles:

| Configuration Key | Env Variable Override | Safe Default Value | Audit Verification |
|:---|:---|:---|:---|
| Application Name | `APP_NAME` | `TenderForge` | Sourced cleanly |
| Environment Mode | `ENVIRONMENT` | `development` | Sourced cleanly |
| Database URL | `DATABASE_URL` | `sqlite:///./tenderforge.db` | Sourced cleanly (isolated per env) |
| JWT Secret Key | `JWT_SECRET_KEY` | Development default with warning | Production validation requires custom secret |
| Gemini API Key | `GEMINI_API_KEY` | None | Gracefully handled if missing |
| Switch Mesh URL | `SWITCH_API_URL` | None | Triggers honest "not_configured" if empty |
| Switch API Key | `SWITCH_API_KEY` | None | Read from env |
| Switch Webhook Secret | `SWITCH_WEBHOOK_SECRET` | None | Read from env |
| Storage Provider | `STORAGE_BACKEND` | `local` | Pluggable (`local` or `s3`) |
| Storage Directory | `LOCAL_STORAGE_PATH` | `./storage` | Relative, path-traversal guarded |
| CORS Origins | `CORS_ORIGINS` | Explicit localhost list | Wildcard forbidden in production |

### 2.2 Secret Masking Engine
To protect credentials from leaking into application logs, the `Settings.masked_dict()` method masks all sensitive keys (`password`, `secret`, `key`, `token`, `authorization`) with `***`:

```python
def masked_dict(self) -> Dict[str, Any]:
    sensitive_substrings = ("secret", "key", "password", "token", "auth")
    # Recursively sanitizes nested dictionaries
```
Automated test `tests/unit/test_config.py::test_settings_masked_dict` confirms that passwords and keys are never printed in plain text.

---

## 3. Mock & Bypass Remediation Audit

| Component | Previous Risk | Audit Action Taken | Current Verified Status |
|:---|:---|:---|:---|
| **Auth Route `/auth/me`** | Synthesized a fallback `usr-system-admin` user when unauthenticated. | Removed fallback user synthesis; strictly raises `AuthenticationException(401)`. | Verified by `test_auth_me_no_fallback_admin` |
| **API Client Headers** | Client attached `X-User-Role: Admin` from browser `localStorage`. | Removed headers from `frontend/src/api/client.ts` and `frontend/dist/index.html`. | Verified by `test_header_injection_ignored` |
| **Switch Mesh Health** | Hardcoded static green status. | Redesigned `/api/v1/switch/status` to perform genuine network probes or return `not_configured`. | Verified by `test_switch_status_endpoint` |
| **Docker DB Health** | Hardcoded postgres credentials in healthcheck. | Updated `docker-compose.yml` to use `$${POSTGRES_USER:-tenderforge}` and `$${POSTGRES_DB:-tenderforge_db}`. | Verified in `docker-compose.yml` |
| **Alembic DB Target** | Overrode custom database URLs with settings default. | Updated `backend/alembic/env.py` to preserve URLs passed via custom config during isolated testing. | Verified on clean test database |

---

## 4. Test & Demo Isolation Verification

- **Automated Tests**: All tests use isolated in-memory or temporary database sessions (`db_session` fixture in `tests/conftest.py`) with automatic rollback. Zero test data bleeds into production or local SQLite storage.
- **Demonstration Scripts**: Scripts `demo_phase3.py` and `demo_phase5.py` use randomized timestamps (`datetime.now().strftime(...)`) and dynamic UUIDs for organizations, tenders, and workspaces, ensuring repeatable execution without primary key collisions.
- **Demo Data Seeding**: `scripts/seed_demo_data.py` uses production-grade bcrypt password hashing and standard Pydantic validation.
