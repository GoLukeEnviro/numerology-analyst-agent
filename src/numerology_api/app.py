"""FastAPI application factory for the stateless Numra calculation API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from importlib.metadata import PackageNotFoundError, version
import os
import re
from typing import cast
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from numerology_agent.deepseek import DeepSeekProvider, DeepSeekSettings
from numerology_agent.models import AnalysisFollowUp, AnalysisReport
from numerology_agent.provider import LlmProvider, ProviderError
from numerology_agent.rate_limit import (
    RateLimiter,
    RedisEvalClient,
    RedisRateLimiter,
    pseudonymous_key,
)
from numerology_agent.service import AgentService, AgentValidationError
from numerology_api.http_models import (
    AnalysisFollowUpRequest,
    AnalysisReportRequest,
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
from numerology_knowledge.loader import load_knowledge_bundle

_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_PROBLEM_BASE = "https://numra.app/problems"


class ApiSettings(BaseModel):
    """Immutable runtime settings; secret values are redacted by Pydantic."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str = "development"
    allowed_origins: tuple[str, ...] = Field(
        default=("http://localhost:5173", "http://127.0.0.1:5173")
    )
    llm_enabled: bool = False
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-pro"
    redis_url: SecretStr = SecretStr("redis://redis:6379/0")
    rate_limit_hmac_secret: SecretStr | None = None


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
    api_key = os.getenv("NUMRA_DEEPSEEK_API_KEY")
    rate_secret = os.getenv("NUMRA_RATE_LIMIT_HMAC_SECRET")
    return ApiSettings(
        environment=os.getenv("NUMRA_ENVIRONMENT", "development"),
        allowed_origins=origins,
        llm_enabled=os.getenv("NUMRA_LLM_ENABLED", "false").lower() == "true",
        deepseek_api_key=SecretStr(api_key) if api_key else None,
        deepseek_base_url=os.getenv("NUMRA_DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("NUMRA_DEEPSEEK_MODEL", "deepseek-v4-pro"),
        redis_url=SecretStr(os.getenv("NUMRA_REDIS_URL", "redis://redis:6379/0")),
        rate_limit_hmac_secret=SecretStr(rate_secret) if rate_secret else None,
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


def _production_dependencies(
    settings: ApiSettings,
    provider: LlmProvider | None,
    rate_limiter: RateLimiter | None,
) -> tuple[LlmProvider | None, RateLimiter | None]:
    if not settings.llm_enabled:
        return provider, rate_limiter
    if provider is None:
        if settings.deepseek_api_key is None:
            raise RuntimeError("NUMRA_DEEPSEEK_API_KEY is required when LLM is enabled")
        provider = DeepSeekProvider(
            DeepSeekSettings(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                model=settings.deepseek_model,
            )
        )
    if rate_limiter is None:
        from redis.asyncio import Redis

        client = Redis.from_url(settings.redis_url.get_secret_value(), decode_responses=True)
        rate_limiter = RedisRateLimiter(cast(RedisEvalClient, client))
    if settings.rate_limit_hmac_secret is None:
        raise RuntimeError("NUMRA_RATE_LIMIT_HMAC_SECRET is required when LLM is enabled")
    return provider, rate_limiter


def create_app(
    settings: ApiSettings | None = None,
    *,
    provider: LlmProvider | None = None,
    rate_limiter: RateLimiter | None = None,
) -> FastAPI:
    """Build an independently testable FastAPI application instance."""
    resolved = settings or settings_from_environment()
    provider, rate_limiter = _production_dependencies(resolved, provider, rate_limiter)
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
        return ReadyStatus(
            redis="ready"
            if resolved.llm_enabled and rate_limiter is not None
            else "not_configured",
            provider="ready" if resolved.llm_enabled and provider is not None else "disabled",
        )

    @api.get("/api/v1/meta", response_model=MetaResponse, tags=["meta"])
    async def meta() -> MetaResponse:
        return MetaResponse(
            package_version=_package_version(),
            profile_schema_version=PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
            knowledge_bundle=load_knowledge_bundle().bundle_id,
            llm={
                "enabled": resolved.llm_enabled,
                "provider": "deepseek" if resolved.llm_enabled else None,
            },
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

    async def consume_analysis_limits(
        request: Request,
        *,
        device_id: str,
        calculation_hash: str,
        device_limit: int,
        device_scope: str,
    ) -> JSONResponse | None:
        assert rate_limiter is not None
        assert resolved.rate_limit_hmac_secret is not None
        secret = resolved.rate_limit_hmac_secret.get_secret_value().encode()
        client_ip = request.client.host if request.client is not None else "unknown"
        ip_retry = await rate_limiter.consume(
            pseudonymous_key("ip-day", client_ip, secret),
            20,
            86_400,
        )
        device_retry = await rate_limiter.consume(
            pseudonymous_key(
                device_scope,
                f"{device_id}:{calculation_hash}",
                secret,
            ),
            device_limit,
            86_400,
        )
        retry_after = ip_retry or device_retry
        if retry_after is None:
            return None
        code = "LLM_IP_QUOTA_EXCEEDED" if ip_retry is not None else "LLM_DEVICE_QUOTA_EXCEEDED"
        response = _problem_response(
            ProblemDetails(
                type=f"{_PROBLEM_BASE}/rate-limit",
                title="Analysis rate limit exceeded",
                status=429,
                code=code,
                detail="Das kurzlebige Analyse-Kontingent ist ausgeschöpft.",
                correlation_id=_correlation_id(request),
            )
        )
        response.headers["Retry-After"] = str(retry_after)
        return response

    @api.post(
        "/api/v1/analyses/report",
        response_model=AnalysisReport,
        responses={
            422: {"model": ProblemDetails},
            429: {"model": ProblemDetails},
            503: {"model": ProblemDetails},
        },
        tags=["analyses"],
    )
    async def analysis_report(
        body: AnalysisReportRequest,
        request: Request,
    ) -> AnalysisReport | JSONResponse:
        if not resolved.llm_enabled or provider is None or rate_limiter is None:
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/llm-disabled",
                    title="LLM analysis disabled",
                    status=503,
                    code="LLM_FEATURE_DISABLED",
                    detail="Die optionale LLM-Analyse ist derzeit deaktiviert.",
                    correlation_id=_correlation_id(request),
                )
            )
        limited = await consume_analysis_limits(
            request,
            device_id=body.device_id,
            calculation_hash=body.profile.deterministic_hash,
            device_limit=1,
            device_scope="device-report",
        )
        if limited is not None:
            return limited
        try:
            return await AgentService(provider).generate_report(body.profile)
        except (AgentValidationError, ProviderError):
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/analysis-generation",
                    title="Analysis generation failed",
                    status=502,
                    code="ANALYSIS_GENERATION_FAILED",
                    detail="Der Bericht konnte nicht sicher erzeugt werden.",
                    correlation_id=_correlation_id(request),
                )
            )

    @api.post(
        "/api/v1/analyses/follow-up",
        response_model=AnalysisFollowUp,
        responses={
            422: {"model": ProblemDetails},
            429: {"model": ProblemDetails},
            503: {"model": ProblemDetails},
        },
        tags=["analyses"],
    )
    async def analysis_follow_up(
        body: AnalysisFollowUpRequest,
        request: Request,
    ) -> AnalysisFollowUp | JSONResponse:
        if not resolved.llm_enabled or provider is None or rate_limiter is None:
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/llm-disabled",
                    title="LLM analysis disabled",
                    status=503,
                    code="LLM_FEATURE_DISABLED",
                    detail="Die optionale LLM-Analyse ist derzeit deaktiviert.",
                    correlation_id=_correlation_id(request),
                )
            )
        limited = await consume_analysis_limits(
            request,
            device_id=body.device_id,
            calculation_hash=body.profile.deterministic_hash,
            device_limit=2,
            device_scope="device-follow-up",
        )
        if limited is not None:
            return limited
        try:
            return await AgentService(provider).generate_follow_up(
                body.profile,
                body.report,
                body.question,
            )
        except (AgentValidationError, ProviderError):
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/analysis-generation",
                    title="Follow-up generation failed",
                    status=502,
                    code="ANALYSIS_GENERATION_FAILED",
                    detail="Die Rückfrage konnte nicht sicher beantwortet werden.",
                    correlation_id=_correlation_id(request),
                )
            )

    return api


app = create_app()
