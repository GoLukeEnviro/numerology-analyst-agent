"""FastAPI application factory for the stateless Numra calculation API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from importlib.metadata import PackageNotFoundError, version
import os
import re
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from numerology_api.http_models import (
    FieldError,
    LiveStatus,
    MetaResponse,
    ProblemDetails,
    ProfileCalculationRequest,
    ReadyStatus,
)
from numerology_domain.exceptions import NumerologyError
from numerology_domain.models import (
    PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
    ProfileCalculationResult,
)
from numerology_engine.profile import calculate_profile

_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_PROBLEM_BASE = "https://numra.app/problems"


class ApiSettings(BaseModel):
    """Small immutable settings surface; secrets never belong here."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str = "development"
    allowed_origins: tuple[str, ...] = Field(
        default=("http://localhost:5173", "http://127.0.0.1:5173")
    )
    llm_enabled: bool = False


def settings_from_environment() -> ApiSettings:
    """Read non-secret API settings from environment variables."""
    origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "NUMRA_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    return ApiSettings(
        environment=os.getenv("NUMRA_ENVIRONMENT", "development"),
        allowed_origins=origins,
        llm_enabled=os.getenv("NUMRA_LLM_ENABLED", "false").lower() == "true",
    )


def _package_version() -> str:
    try:
        return version("numerology-analyst-agent")
    except PackageNotFoundError:
        return "0.0.0+dev"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach one bounded correlation ID to every request and response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        supplied = request.headers.get("X-Correlation-ID", "")
        correlation_id = supplied if _CORRELATION_PATTERN.fullmatch(supplied) else str(uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


def _problem_response(problem: ProblemDetails) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json"),
        media_type="application/problem+json",
    )


def _correlation_id(request: Request) -> str:
    value = getattr(request.state, "correlation_id", "")
    return value if isinstance(value, str) and value else str(uuid4())


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    """Build an independently testable FastAPI application instance."""
    resolved = settings or settings_from_environment()
    api = FastAPI(
        title="Numra API",
        version=_package_version(),
        docs_url="/api/docs",
        redoc_url=None,
    )
    api.state.settings = resolved
    api.add_middleware(CorrelationIdMiddleware)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
        max_age=600,
    )

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
        return _problem_response(
            ProblemDetails(
                type=f"{_PROBLEM_BASE}/request-validation",
                title="Request validation failed",
                status=422,
                code="REQUEST_VALIDATION_FAILED",
                detail="The request body does not satisfy the API contract.",
                correlation_id=_correlation_id(request),
                field_errors=tuple(field_errors),
            )
        )

    @api.exception_handler(NumerologyError)
    async def numerology_error_handler(
        request: Request,
        exc: NumerologyError,
    ) -> JSONResponse:
        return _problem_response(
            ProblemDetails(
                type=f"{_PROBLEM_BASE}/calculation",
                title="Calculation rejected",
                status=400,
                code="CALCULATION_REJECTED",
                detail=str(exc),
                correlation_id=_correlation_id(request),
            )
        )

    @api.get("/api/v1/health/live", response_model=LiveStatus, tags=["health"])
    async def live() -> LiveStatus:
        return LiveStatus()

    @api.get("/api/v1/health/ready", response_model=ReadyStatus, tags=["health"])
    async def ready() -> ReadyStatus:
        return ReadyStatus()

    @api.get("/api/v1/meta", response_model=MetaResponse, tags=["meta"])
    async def meta() -> MetaResponse:
        return MetaResponse(
            package_version=_package_version(),
            profile_schema_version=PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
        )

    @api.post(
        "/api/v1/profiles/calculate",
        response_model=ProfileCalculationResult,
        responses={
            400: {"model": ProblemDetails, "description": "Calculation rejected"},
            422: {"model": ProblemDetails, "description": "Request validation failed"},
        },
        tags=["profiles"],
    )
    async def calculate(request: ProfileCalculationRequest) -> ProfileCalculationResult:
        return calculate_profile(request.person, request.policy)

    return api


app = create_app()
