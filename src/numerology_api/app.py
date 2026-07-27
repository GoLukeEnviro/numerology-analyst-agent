"""FastAPI application factory for the stateless Numra calculation API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from importlib.metadata import PackageNotFoundError, version
import logging
import os
import re
from time import perf_counter
from typing import cast
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

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
    AnalysisProfile,
    AnalysisReportRequest,
    FieldError,
    LegacyV2ProfileCalculationResult,
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
_ACCESS_LOGGER = logging.getLogger("numerology_api.access")
_ERROR_LOGGER = logging.getLogger("numerology_api.error")
_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


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
    max_request_body_bytes: int = Field(default=65_536, ge=256, le=1_048_576)


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
        max_request_body_bytes=int(os.getenv("NUMRA_MAX_REQUEST_BODY_BYTES", "65536")),
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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply browser hardening and disable intermediary storage of API data."""

    def __init__(self, app: ASGIApp, *, production: bool) -> None:
        super().__init__(app)
        self._production = production

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if self._production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Log bounded request metadata without query strings, bodies or responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = perf_counter()
        response = await call_next(request)
        duration_ms = (perf_counter() - started) * 1000
        _ACCESS_LOGGER.info(
            "request_completed method=%s path=%s status=%d correlation_id=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            _correlation_id(request),
            duration_ms,
        )
        return response


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """Reject browser state-changing requests from unconfigured origins."""

    def __init__(self, app: ASGIApp, *, allowed_origins: tuple[str, ...]) -> None:
        super().__init__(app)
        self._allowed_origins = frozenset(allowed_origins)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        origin = request.headers.get("Origin")
        if (
            request.method in _UNSAFE_METHODS
            and origin is not None
            and origin not in self._allowed_origins
        ):
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/origin",
                    title="Origin not allowed",
                    status=403,
                    code="ORIGIN_NOT_ALLOWED",
                    detail="The request origin is not allowed.",
                    correlation_id=_correlation_id(request),
                )
            )
        return await call_next(request)


class RequestBodyLimitMiddleware:
    """Bound request bodies before JSON parsing, including chunked requests."""

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self._app = app
        self._max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") not in _UNSAFE_METHODS:
            await self._app(scope, receive, send)
            return

        headers = {
            key.lower(): value
            for key, value in scope.get("headers", [])
            if isinstance(key, bytes) and isinstance(value, bytes)
        }
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                if int(content_length) > self._max_bytes:
                    await self._reject(scope, receive, send)
                    return
            except ValueError:
                await self._reject(scope, receive, send)
                return

        chunks: list[bytes] = []
        total = 0
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            total += len(chunk)
            if total > self._max_bytes:
                await self._reject(scope, receive, send)
                return
            chunks.append(chunk)
            more_body = bool(message.get("more_body", False))

        body = b"".join(chunks)
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if delivered:
                return {"type": "http.request", "body": b"", "more_body": False}
            delivered = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self._app(scope, replay, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive=receive)
        response = _problem_response(
            ProblemDetails(
                type=f"{_PROBLEM_BASE}/request-body-too-large",
                title="Request body too large",
                status=413,
                code="REQUEST_BODY_TOO_LARGE",
                detail="The request body exceeds the configured limit.",
                correlation_id=_correlation_id(request),
            )
        )
        await response(scope, receive, send)


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

    @api.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        _ERROR_LOGGER.error(
            "unhandled_request_error method=%s path=%s correlation_id=%s error_type=%s",
            request.method,
            request.url.path,
            _correlation_id(request),
            type(exc).__name__,
        )
        return _problem_response(
            ProblemDetails(
                type=f"{_PROBLEM_BASE}/internal",
                title="Internal server error",
                status=500,
                code="INTERNAL_SERVER_ERROR",
                detail="An unexpected error occurred.",
                correlation_id=_correlation_id(request),
            )
        )

    @api.get("/api/v1/health/live", response_model=LiveStatus, tags=["health"])
    async def live() -> LiveStatus:
        return LiveStatus()

    @api.get("/api/v1/health/ready", response_model=ReadyStatus, tags=["health"])
    async def ready() -> ReadyStatus | JSONResponse:
        if not resolved.llm_enabled:
            return ReadyStatus()
        limiter_ready = rate_limiter is not None and await rate_limiter.is_ready()
        status = ReadyStatus(
            status="ready" if limiter_ready else "unavailable",
            redis="ready" if limiter_ready else "unavailable",
            provider="configured" if provider is not None else "disabled",
        )
        if limiter_ready:
            return status
        return JSONResponse(status_code=503, content=status.model_dump(mode="json"))

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

    def canonical_analysis_profile(profile: AnalysisProfile) -> ProfileCalculationResult | None:
        canonical = calculate_profile(profile.input_ref, profile.policy)
        if isinstance(profile, LegacyV2ProfileCalculationResult):
            return canonical
        if (
            profile.schema_version != PROFILE_CALCULATION_RESULT_SCHEMA_VERSION
            or profile != canonical
        ):
            return None
        return canonical

    async def consume_analysis_limits(
        request: Request,
        *,
        device_id: str,
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
                device_id,
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
        canonical_profile = canonical_analysis_profile(body.profile)
        if canonical_profile is None:
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/profile-integrity",
                    title="Profile integrity validation failed",
                    status=422,
                    code="PROFILE_INTEGRITY_FAILED",
                    detail="Das übermittelte Profil stimmt nicht mit der kanonischen Berechnung überein.",
                    correlation_id=_correlation_id(request),
                )
            )
        limited = await consume_analysis_limits(
            request,
            device_id=body.device_id,
            device_limit=1,
            device_scope="device-report",
        )
        if limited is not None:
            return limited
        try:
            assert resolved.rate_limit_hmac_secret is not None
            return await AgentService(
                provider,
                context_secret=resolved.rate_limit_hmac_secret.get_secret_value().encode(),
            ).generate_report(canonical_profile)
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
        canonical_profile = canonical_analysis_profile(body.profile)
        if canonical_profile is None:
            return _problem_response(
                ProblemDetails(
                    type=f"{_PROBLEM_BASE}/profile-integrity",
                    title="Profile integrity validation failed",
                    status=422,
                    code="PROFILE_INTEGRITY_FAILED",
                    detail="Das übermittelte Profil stimmt nicht mit der kanonischen Berechnung überein.",
                    correlation_id=_correlation_id(request),
                )
            )
        limited = await consume_analysis_limits(
            request,
            device_id=body.device_id,
            device_limit=2,
            device_scope="device-follow-up",
        )
        if limited is not None:
            return limited
        try:
            assert resolved.rate_limit_hmac_secret is not None
            return await AgentService(
                provider,
                context_secret=resolved.rate_limit_hmac_secret.get_secret_value().encode(),
            ).generate_follow_up(
                canonical_profile,
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
