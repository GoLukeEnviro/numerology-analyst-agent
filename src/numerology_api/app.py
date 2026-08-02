"""FastAPI application factory for the stateless Numra calculation API.

This module only wires the application: settings resolution, dependency
creation, middleware registration, exception handlers and router mounting.
All route handlers live in :mod:`numerology_api.routes` and shared analysis
logic in :mod:`numerology_api.analysis_runtime`.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from numerology_agent.provider import LlmProvider
from numerology_agent.rate_limit import RateLimiter
from numerology_agent.resilience import CircuitBreaker
from numerology_api.dependencies import (
    ApiSettings as ApiSettings,
)
from numerology_api.dependencies import (
    package_version,
    production_dependencies,
    settings_from_environment,
)
from numerology_api.http_models import FieldError, ProblemDetails
from numerology_api.middleware import (
    AccessLogMiddleware,
    CorrelationIdMiddleware,
    OriginValidationMiddleware,
    RequestBodyLimitMiddleware,
    SecurityHeadersMiddleware,
)
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response
from numerology_api.routes import analyses, cycles, health, meta, profiles
from numerology_domain.exceptions import NumerologyError

_ERROR_LOGGER = logging.getLogger("numerology_api.error")


def create_app(
    settings: ApiSettings | None = None,
    *,
    provider: LlmProvider | None = None,
    rate_limiter: RateLimiter | None = None,
) -> FastAPI:
    """Build an independently testable FastAPI application instance."""
    resolved = settings or settings_from_environment()
    provider, rate_limiter = production_dependencies(resolved, provider, rate_limiter)
    circuit_breaker: CircuitBreaker | None = CircuitBreaker() if resolved.llm_enabled else None
    api = FastAPI(
        title="Numra API",
        version=package_version(),
        docs_url="/api/docs",
        redoc_url=None,
    )
    api.state.settings = resolved
    api.state.provider = provider
    api.state.rate_limiter = rate_limiter
    api.state.circuit_breaker = circuit_breaker
    api.add_middleware(
        OriginValidationMiddleware,
        allowed_origins=resolved.allowed_origins,
    )
    api.add_middleware(
        RequestBodyLimitMiddleware,
        max_bytes=resolved.max_request_body_bytes,
    )
    api.add_middleware(AccessLogMiddleware)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
        max_age=600,
    )
    api.add_middleware(
        SecurityHeadersMiddleware,
        production=resolved.environment == "production",
    )
    api.add_middleware(CorrelationIdMiddleware)

    @api.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        field_errors: list[FieldError] = []
        for error in exc.errors():
            parts = [str(part) for part in error["loc"] if part != "body"]
            message = str(error["msg"])
            if parts == ["person"] and "PERSON_BIRTH_DATE_IN_FUTURE" in message:
                parts.append("birth_date")
            field_errors.append(
                FieldError(
                    field=".".join(parts),
                    message=message,
                    code=str(error["type"]),
                )
            )
        return problem_response(
            ProblemDetails(
                type=f"{PROBLEM_BASE}/request-validation",
                title="Request validation failed",
                status=422,
                code="REQUEST_VALIDATION_FAILED",
                detail="The request body does not satisfy the API contract.",
                correlation_id=correlation_id(request),
                field_errors=tuple(field_errors),
            )
        )

    @api.exception_handler(NumerologyError)
    async def numerology_error_handler(
        request: Request,
        exc: NumerologyError,
    ) -> JSONResponse:
        return problem_response(
            ProblemDetails(
                type=f"{PROBLEM_BASE}/calculation",
                title="Calculation rejected",
                status=400,
                code="CALCULATION_REJECTED",
                detail=str(exc),
                correlation_id=correlation_id(request),
            )
        )

    @api.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        _ERROR_LOGGER.error(
            "unhandled_request_error method=%s path=%s correlation_id=%s error_type=%s",
            request.method,
            request.url.path,
            correlation_id(request),
            type(exc).__name__,
        )
        return problem_response(
            ProblemDetails(
                type=f"{PROBLEM_BASE}/internal",
                title="Internal server error",
                status=500,
                code="INTERNAL_SERVER_ERROR",
                detail="An unexpected error occurred.",
                correlation_id=correlation_id(request),
            )
        )

    api.include_router(health.router)
    api.include_router(meta.router)
    api.include_router(profiles.router)
    api.include_router(analyses.router)
    api.include_router(cycles.router)

    return api


app = create_app()

__all__ = ["ApiSettings", "app", "create_app"]
