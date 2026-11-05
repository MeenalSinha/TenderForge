# TenderForge Phase 4: Authentication & User Management

## 1. Overview & Objectives

In Phase 4, TenderForge transitions from an anonymous local workspace model to an enterprise-grade multi-tenant identity and access management system. The authentication framework is engineered according to OWASP guidelines, ensuring zero credentials leakage, secure password hashing, tamper-proof JSON Web Tokens (JWT), session revocation, and automated self-service password reset workflows.

---

## 2. Cryptographic Foundation & Policies

### 2.1 Password Hashing via bcrypt
- Passwords are never stored in plaintext or reversible formats.
- Hashed using the industry-standard `bcrypt` algorithm with salt rounds governed by `settings.BCRYPT_ROUNDS` (configurable from 4 in automated test harnesses to 12 in production environments).
- Passwords must satisfy complexity constraints: minimum 8 characters, maximum 128 characters, containing uppercase, lowercase, numeric, and special characters.

### 2.2 JWT Token Generation & Verification
- **Algorithm**: HMAC-SHA256 (`HS256`), signing secret governed by `settings.JWT_SECRET_KEY`.
- **Payload Claims**:
  - `sub`: User UUID
  - `email`: User email address
  - `full_name`: User's display name
  - `default_org_id`: Active primary organization UUID
  - `role`: System-level or active organizational role
  - `exp`: Expiration epoch (default 1440 minutes / 24 hours)
  - `iat`: Issue epoch
- **Token Validation**: Automatically verified via `get_current_user_claims` dependency in `backend/app/core/rbac.py`. Backwards compatibility with developer header-based auth (`X-User-Role`, `X-User-Id`) is preserved for headless test automation.

---

## 3. Database Schema

### 3.1 `users` Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(50),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
CREATE INDEX ix_users_email ON users(email);
```

### 3.2 `password_reset_tokens` Table
```sql
CREATE TABLE password_reset_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL
);
CREATE INDEX ix_reset_tokens_hash ON password_reset_tokens(token_hash);
```

### 3.3 `user_sessions` Table
```sql
CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(64) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    expires_at DATETIME NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL
);
CREATE INDEX ix_user_sessions_jti ON user_sessions(token_jti);
```

---

## 4. REST API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account and provision personal workspace | Public |
| `POST` | `/api/v1/auth/login` | Authenticate with email/password; returns JWT access token | Public |
| `POST` | `/api/v1/auth/logout` | Revoke active user session | Bearer Token |
| `GET` | `/api/v1/auth/me` | Fetch active user profile and organizational memberships | Bearer Token |
| `POST` | `/api/v1/auth/password-reset/request` | Request single-use password reset token | Public |
| `POST` | `/api/v1/auth/password-reset/confirm` | Confirm password reset using single-use token and update password | Public |
| `POST` | `/api/v1/auth/change-password` | Update password for currently authenticated user | Bearer Token |

---

## 5. Security & Defense in Depth
1. **Timing Attack Protection**: Password comparison uses `bcrypt.checkpw()` which runs in constant time.
2. **Token Hash Storage**: Password reset tokens are generated as high-entropy 32-byte URL-safe strings; only the SHA-256 digest is stored in the database.
3. **Automatic Single-Use Invalidation**: Reset tokens are marked `is_used = True` upon successful password modification.
4. **Rate Limiting**: Configured to restrict authentication endpoints to 30 requests per minute per IP address.
