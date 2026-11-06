"""
TenderForge Main Application Factory & ASGI Entrypoint.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import (
    compliance_router,
    documents_router,
    evidence_router,
    health_router,
    prooflink_router,
    proposals_router,
    switch_router,
    tenders_router,
    workflow_router,
    bid_decision_router,
    financial_router,
    portfolio_router,
    risks_router,
    deadlines_router,
    analytics_router,
    optimizations_router,
    auth_router,
    organizations_router,
    sources_router,
    opportunities_router,
    monitoring_router,
    market_router,
    bid_outcomes_router,
    knowledge_router,
)
from backend.app.api.schemas.common import ErrorDetail, ResponseEnvelope
from backend.app.core.config import settings
from backend.app.core.exceptions import TenderForgeException
from backend.app.core.logging import correlation_id_ctx, get_logger, setup_logging

# Configure logging at boot
setup_logging(settings.LOG_LEVEL)
logger = get_logger("tenderforge.app")


class CorrelationIdMiddleware:
    """Pure ASGI middleware injecting an X-Correlation-ID header without buffering multipart streams."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            corr_id = str(uuid.uuid4())
            for header_name, header_val in scope.get("headers", []):
                if header_name.lower() == b"x-correlation-id":
                    corr_id = header_val.decode("latin1")
                    break

            token = correlation_id_ctx.set(corr_id)

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-correlation-id", corr_id.encode("latin1")))
                    message["headers"] = headers
                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)
            finally:
                correlation_id_ctx.reset(token)
        else:
            await self.app(scope, receive, send)


class SecurityHeadersMiddleware:
    """ASGI middleware applying enterprise defense-in-depth HTTP security headers."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"x-xss-protection", b"1; mode=block"),
                        (b"referrer-policy", b"strict-origin-when-cross-origin"),
                        (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    ])
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def create_app() -> FastAPI:
    """Application factory configuring routes, middleware, and exception handlers."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-Powered Collaborative Tender Intelligence & Proposal Preparation Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # 1. Middlewares
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Centralized Exception Handlers
    @app.exception_handler(TenderForgeException)
    async def handle_domain_exception(request: Request, exc: TenderForgeException) -> JSONResponse:
        logger.warning(f"Domain exception [{exc.code}]: {exc.message}")
        envelope = ResponseEnvelope[None](
            success=False,
            status_code=exc.status_code,
            message=exc.message,
            data=None,
            errors=[ErrorDetail(code=exc.code, detail=exc.message)],
            correlation_id=correlation_id_ctx.get(),
            timestamp=datetime.now(timezone.utc),
        )
        return JSONResponse(status_code=exc.status_code, content=envelope.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            ErrorDetail(
                code="REQUEST_VALIDATION_ERROR",
                detail=f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}",
            )
        for err in exc.errors()
        ]
        envelope = ResponseEnvelope[None](
            success=False,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed.",
            data=None,
            errors=errors,
            correlation_id=correlation_id_ctx.get(),
            timestamp=datetime.now(timezone.utc),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=envelope.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled server error: {str(exc)}", exc_info=True)
        envelope = ResponseEnvelope[None](
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An internal server error occurred.",
            data=None,
            errors=[ErrorDetail(code="INTERNAL_ERROR", detail="An unexpected error occurred.")],
            correlation_id=correlation_id_ctx.get(),
            timestamp=datetime.now(timezone.utc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=envelope.model_dump(mode="json"),
        )

    # 3. Mount REST API Routers
    app.include_router(health_router)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(organizations_router, prefix=settings.API_V1_PREFIX)
    app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
    app.include_router(tenders_router, prefix=settings.API_V1_PREFIX)
    app.include_router(evidence_router, prefix=settings.API_V1_PREFIX)
    app.include_router(prooflink_router, prefix=settings.API_V1_PREFIX)
    app.include_router(compliance_router, prefix=settings.API_V1_PREFIX)
    app.include_router(proposals_router, prefix=settings.API_V1_PREFIX)
    app.include_router(switch_router, prefix=settings.API_V1_PREFIX)
    app.include_router(workflow_router, prefix=settings.API_V1_PREFIX)
    app.include_router(bid_decision_router, prefix=settings.API_V1_PREFIX)
    app.include_router(financial_router, prefix=settings.API_V1_PREFIX)
    app.include_router(portfolio_router, prefix=settings.API_V1_PREFIX)
    app.include_router(risks_router, prefix=settings.API_V1_PREFIX)
    app.include_router(deadlines_router, prefix=settings.API_V1_PREFIX)
    app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
    app.include_router(optimizations_router, prefix=settings.API_V1_PREFIX)
    app.include_router(sources_router, prefix=settings.API_V1_PREFIX)
    app.include_router(opportunities_router, prefix=settings.API_V1_PREFIX)
    app.include_router(monitoring_router, prefix=settings.API_V1_PREFIX)
    app.include_router(market_router, prefix=settings.API_V1_PREFIX)
    app.include_router(bid_outcomes_router, prefix=settings.API_V1_PREFIX)
    app.include_router(knowledge_router, prefix=settings.API_V1_PREFIX)

    # 4. Optional Static Assets & SPA Routing for Enterprise Frontend
    dist_dir = Path("frontend/dist")
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
            file_path = dist_dir / full_path
            if file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(dist_dir / "index.html")

    return app


app = create_app()
