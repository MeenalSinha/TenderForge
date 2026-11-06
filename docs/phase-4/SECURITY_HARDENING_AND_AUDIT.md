# TenderForge Phase 4: Security Hardening & Audit

## 1. Executive Summary & Security Posture

TenderForge handles sensitive competitive intelligence, proprietary pricing models, and government procurement filings. Phase 4 implements enterprise defense-in-depth security hardening across network, application, database, and identity perimeters.

---

## 2. Hardening Measures Implemented

### 2.1 HTTP Security Headers Middleware
All responses emitted by FastAPI pass through `SecurityHeadersMiddleware`, injecting:
- `X-Content-Type-Options: nosniff` (Prevents MIME sniffing attacks).
- `X-Frame-Options: DENY` (Mitigates clickjacking in legacy frames).
- `X-XSS-Protection: 1; mode=block` (Enforces legacy browser reflective XSS filtering).
- `Referrer-Policy: strict-origin-when-cross-origin` (Prevents leaking query parameters to third parties).
- `Permissions-Policy: camera=(), microphone=(), geolocation=()` (Disables unnecessary device capabilities).

### 2.2 Strict CORS Policy
- Controlled via `settings.CORS_ORIGINS`. In development mode, wildcards are permitted; in production, strict origin validation is enforced for authorized domains.
- Credentials support enabled (`allow_credentials=True`) with explicit method whitelisting (`GET, POST, PUT, DELETE, OPTIONS`).

### 2.3 Authentication & Password Security
- Passwords hashed using `bcrypt` with adaptive salt cost.
- High-entropy single-use password reset tokens with SHA-256 hash storage.
- Rate limiting on authentication routes (30 requests per minute per IP address).

### 2.4 Nothing Hardcoded & Zero Leakage Policy
- All secrets (`JWT_SECRET_KEY`, `AI_API_KEY`, `DATABASE_URL`) are loaded from environment variables or `.env` files via Pydantic Settings.
- Logging utilities feature automatic masking: database passwords and API keys are redacted as `***REDACTED***` before writing to disk or stdout.
- Exception handlers intercept unhandled server errors and return sanitized generic envelopes to clients (`INTERNAL_ERROR`), preventing stack trace leakage.

---

## 3. Vulnerability Scanning & Code Audit Checklist

| Threat Category | Risk Description | TenderForge Safeguard |
| :--- | :--- | :--- |
| **SQL Injection** | Attacker injects arbitrary SQL syntax via input fields | 100% parameterized queries via SQLAlchemy ORM; zero string interpolation in queries. |
| **Broken Object Level Auth** | User accesses tender belonging to another organization | Tenant scoping enforced in queries: `WHERE organization_id = :org_id`. |
| **Cryptographic Failures** | Weak hashing or plain reset tokens | bcrypt password hashing; SHA-256 token hashing; HS256 JWT signatures. |
| **SSRF** | Server fetches malicious internal URLs | Document upload restricted to local multipart files or authorized object storage buckets. |
| **Path Traversal** | Malicious filename `../../etc/passwd` | Filenames sanitized via `Path(name).name`; relative storage paths resolved with strict jail check. |

