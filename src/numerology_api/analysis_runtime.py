"""Shared runtime for LLM analysis endpoints (report and follow-up).

Both ``/api/v1/analyses/report`` and ``/api/v1/analyses/follow-up`` follow the
same pipeline: LLM-enabled check, canonical profile validation, rate-limit
preparation, context-secret derivation and provider/validation error mapping.
This module centralizes that shared flow without hiding the report- and
follow-up-specific semantics of the individual handlers.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from numerology_agent.provider import LlmProvider, ProviderError
from numerology_agent.rate_limit import RateLimiter, pseudonymous_key
from numerology_agent.resilience import CircuitBreaker
from numerology_agent.service import AgentService, AgentValidationError
from numerology_api.dependencies import ApiSettings
from numerology_api.http_models import (
    AnalysisProfile,
    LegacyV2ProfileCalculationResult,
    ProblemDetails,
)
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response
from numerology_domain.models import (
    PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
    ProfileCalculationResult,
)
from numerology_engine.profile import calculate_profile


def llm_disabled_response(request: Request) -> JSONResponse:
    """Return the stable 503 ProblemDetails when the LLM feature is disabled."""
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/llm-disabled",
            title="LLM analysis disabled",
            status=503,
            code="LLM_FEATURE_DISABLED",
            detail="Die optionale LLM-Analyse ist derzeit deaktiviert.",
            correlation_id=correlation_id(request),
        )
    )


def canonical_analysis_profile(profile: AnalysisProfile) -> ProfileCalculationResult | None:
    """Recalculate the canonical profile and verify the submitted one matches.

    Legacy V2 profiles are accepted and recalculated server-side. Current V3
    profiles must match the canonical calculation byte-for-byte; otherwise
    ``None`` is returned and the caller rejects the request before any quota
    is consumed.
    """
    canonical = calculate_profile(profile.input_ref, profile.policy)
    if isinstance(profile, LegacyV2ProfileCalculationResult):
        return canonical
    if profile.schema_version != PROFILE_CALCULATION_RESULT_SCHEMA_VERSION or profile != canonical:
        return None
    return canonical


def profile_integrity_response(request: Request) -> JSONResponse:
    """Return the stable 422 ProblemDetails for a non-canonical profile."""
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/profile-integrity",
            title="Profile integrity validation failed",
            status=422,
            code="PROFILE_INTEGRITY_FAILED",
            detail="Das übermittelte Profil stimmt nicht mit der kanonischen Berechnung überein.",
            correlation_id=correlation_id(request),
        )
    )


async def consume_analysis_limits(
    request: Request,
    *,
    settings: ApiSettings,
    rate_limiter: RateLimiter,
    device_id: str,
    device_limit: int,
    device_scope: str,
) -> JSONResponse | None:
    """Consume the daily IP and device quotas for an analysis request.

    Returns ``None`` when the request may proceed, otherwise a 429
    ProblemDetails response carrying the ``Retry-After`` header.
    """
    assert settings.rate_limit_hmac_secret is not None
    secret = settings.rate_limit_hmac_secret.get_secret_value().encode()
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
    response = problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/rate-limit",
            title="Analysis rate limit exceeded",
            status=429,
            code=code,
            detail="Das kurzlebige Analyse-Kontingent ist ausgeschöpft.",
            correlation_id=correlation_id(request),
        )
    )
    response.headers["Retry-After"] = str(retry_after)
    return response


def analysis_generation_response(request: Request, *, follow_up: bool) -> JSONResponse:
    """Map provider/validation failures to the stable 502 ProblemDetails."""
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/analysis-generation",
            title="Analysis generation failed",
            status=502,
            code="ANALYSIS_GENERATION_FAILED",
            detail=(
                "Die Rückfrage konnte nicht sicher beantwortet werden."
                if follow_up
                else "Der Bericht konnte nicht sicher erzeugt werden."
            ),
            correlation_id=correlation_id(request),
        )
    )


def build_agent_service(
    provider: LlmProvider,
    *,
    settings: ApiSettings,
    circuit_breaker: CircuitBreaker | None,
) -> AgentService:
    """Construct the :class:`AgentService` with the shared context secret."""
    assert settings.rate_limit_hmac_secret is not None
    return AgentService(
        provider,
        context_secret=settings.rate_limit_hmac_secret.get_secret_value().encode(),
        circuit_breaker=circuit_breaker,
    )


def is_analysis_generation_error(exc: Exception) -> bool:
    """Return whether the exception maps to the analysis-generation ProblemDetails."""
    return isinstance(exc, AgentValidationError | ProviderError)
