# ==============================================================================
# TenderForge Backend - Production Multi-Stage Dockerfile
# ==============================================================================

# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime Environment
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime dependencies for PDF/document parsing and curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user & group
RUN groupadd -g 1001 tenderforge && \
    useradd -u 1001 -g tenderforge -s /bin/bash -m tenderforge

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/tenderforge/.local
ENV PATH=/home/tenderforge/.local/bin:$PATH

# Copy application code and configuration
COPY --chown=tenderforge:tenderforge backend/ ./backend/
COPY --chown=tenderforge:tenderforge config/ ./config/
COPY --chown=tenderforge:tenderforge scripts/ ./scripts/
COPY --chown=tenderforge:tenderforge frontend/dist/ ./frontend/dist/
COPY --chown=tenderforge:tenderforge alembic.ini .

# Create persistent storage directories with proper ownership
RUN mkdir -p /app/storage /app/temp_uploads && \
    chown -R tenderforge:tenderforge /app

USER tenderforge

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info"]

