# TenderForge — Phase 1: Configuration Guide

## 1. Centralized Configuration Hierarchy

TenderForge strictly enforces the **Nothing Hardcoded** rule. System parameters, thresholds, paths, model names, and categories are decoupled into a centralized configuration architecture.

Precedence order:
1. **Explicit Runtime Arguments**
2. **Environment Variables**
3. **`.env` File**
4. **YAML Configuration Files** (`config/application.yaml`, `config/document_processing.yaml`)
5. **Pydantic Model Defaults**

---

## 2. Environment Variables Reference (`.env`)

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Deployment environment (`development`, `testing`, `production`) |
| `APP_NAME` | `TenderForge` | Application display name |
| `APP_VERSION` | `1.0.0` | Application semver string |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `API_V1_PREFIX` | `/api/v1` | URL routing prefix for API v1 |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins as a JSON list |
| `DATABASE_URL` | `sqlite:///./tenderforge.db` | SQLAlchemy connection string |
| `DB_ECHO` | `false` | Log raw SQL statements to console |
| `STORAGE_PROVIDER`| `local` | Binary storage adapter (`local`, `s3`, `gcs`) |
| `STORAGE_ROOT` | `./storage` | Directory where uploaded files are persisted |
| `TEMP_STORAGE_ROOT`| `./temp_uploads` | Temporary processing directory |
| `MAX_UPLOAD_SIZE_BYTES` | `52428800` | Upload limit in bytes (default 50 MB) |
| `AI_PROVIDER` | `mock` | Active provider: `mock`, `openai`, `gemini`, `anthropic`, `ollama`, or `none` |
| `AI_MODEL_NAME` | `gpt-4o` | Target LLM model name |
| `AI_API_KEY` | *(empty)* | API key for remote LLM provider |
| `AI_API_BASE_URL` | *(empty)* | Optional base URL override (e.g. for Ollama or Azure) |
| `AI_TEMPERATURE` | `0.1` | Sampling temperature for AI extraction |
| `AI_MAX_TOKENS` | `4096` | Max completion tokens |
| `AI_TIMEOUT_SECONDS` | `60.0` | Network timeout for AI API requests |
| `AI_MAX_RETRIES` | `2` | Max automatic retries on provider failure |

---

## 3. YAML Configuration Files

### 3.1 `config/application.yaml`
Governs enterprise workspaces, rate limiting, and log redaction masks:
```yaml
application:
  name: "TenderForge"
  version: "1.0.0"

workspaces:
  default_id: "ws-default-0000-0000-000000000000"
  default_organization_id: "org-default-0000-0000-000000000000"

security:
  enforce_file_signatures: true
  rate_limit_per_minute: 120

logging:
  mask_keys:
    - "api_key"
    - "password"
    - "token"
    - "secret"
    - "authorization"
```

### 3.2 `config/document_processing.yaml`
Governs document formats, parser parameters, and chunking:
```yaml
formats:
  allowed_extensions: [".pdf", ".docx", ".txt", ".csv", ".xlsx"]

parsers:
  pdf:
    min_page_char_threshold: 40
    enable_ocr_detection: true

segmentation:
  chunk_size_chars: 1200
  chunk_overlap_chars: 200
  min_chunk_size_chars: 100

intelligence:
  categories: ["eligibility", "technical", "financial", "submission", "general"]
  classifications: ["mandatory", "optional", "desirable"]
```

---

## 4. Switching AI Providers

### Option A: Local Deterministic Development (Default)
```env
AI_PROVIDER=mock
```
Uses `MockAIProvider` to extract real clauses directly from uploaded documents with zero network dependency or API costs.

### Option B: Remote OpenAI / Gemini
```env
AI_PROVIDER=openai
AI_MODEL_NAME=gpt-4o
AI_API_KEY=sk-your-actual-api-key-here
```
For Google Gemini via OpenAI-compatibility endpoint:
```env
AI_PROVIDER=gemini
AI_MODEL_NAME=gemini-1.5-pro
AI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_API_KEY=your-gemini-key
```

### Option C: Testing Missing Configuration Behavior
```env
AI_PROVIDER=none
```
Document ingestion, storage, parsing, normalization, and segmentation will continue to run completely. The `/analyze` endpoint will cleanly report `ai_configuration_required` without fabricating false claims.

