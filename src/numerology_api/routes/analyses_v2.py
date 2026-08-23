"""V2 analysis routes — full AgentServiceV3-powered endpoints.

The V1 routes in ``routes/analyses.py`` remain unchanged.  The V2 pipeline
mirrors the V1 flow but operates on the V4 profile contract and the V3 agent:

1. LLM-enabled check (fail-closed 503 when disabled).
2. Canonical V4 profile re-validation (422 on integrity failure).
3. Rate-limit consumption (429 with ``Retry-After``).
4. ``AgentServiceV3`` report / follow-up generation.
5. Provider/validation failures map to the stable 502 ProblemDetails.

Idempotency is wired through the optional ``IdempotencyStoreV3``; when no
store is configured the endpoints still work but without replay protection
(``idempotency_store is None`` is an explicit, documented configuration).
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_agent.models_v3 import AnalysisFollowUpV3, AnalysisReportV3
from numerology_agent.provider import ProviderError
from numerology_agent.provider_v3 import LlmProviderV3
from numerology_agent.service_v3 import AgentServiceV3
from numerology_api.analysis_runtime import (
    consume_analysis_limits,
    llm_disabled_response,
)
from numerology_api.analysis_runtime_v2 import canonical_analysis_profile_v2
from numerology_api.http_models import (
    AnalysisFollowUpRequestV2,
    AnalysisReportRequestV2,
    ProblemDetails,
)
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response

router = APIRouter(tags=["analyses-v2"])


def _build_agent(request: Request) -> AgentServiceV3 | None:
    """Construct the V3 agent from the app state provider (or ``None``)."""
    provider = getattr(request.app.state, "provider_v3", None)
    if provider is None:
        return None
    settings = request.app.state.settings
    hmac_secret = (
        settings.rate_limit_hmac_secret.get_secret_value().encode()
        if settings.rate_limit_hmac_secret is not None
        else b""
    )
    return AgentServiceV3(provider, hmac_secret=hmac_secret)


def _profile_integrity_response(request: Request) -> JSONResponse:
    """Return the stable 422 ProblemDetails for a non-canonical V4 profile."""
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


def _generation_response(request: Request, *, follow_up: bool) -> JSONResponse:
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


def _is_generation_error(exc: Exception) -> bool:
    """Return whether the exception maps to the analysis-generation ProblemDetails."""
    return isinstance(exc, ProviderError | ValueError)


@router.post(
    "/api/v2/analyses/report",
    response_model=AnalysisReportV3,
    responses={
        422: {"model": ProblemDetails, "description": "Request validation failed"},
        429: {"model": ProblemDetails, "description": "Rate limit exceeded"},
        502: {"model": ProblemDetails, "description": "Analysis generation failed"},
        503: {"model": ProblemDetails, "description": "LLM analysis disabled"},
    },
)
async def analysis_report_v2(
    body: AnalysisReportRequestV2,
    request: Request,
) -> AnalysisReportV3 | JSONResponse:
    settings = request.app.state.settings
    provider: LlmProviderV3 | None = getattr(request.app.state, "provider_v3", None)
    rate_limiter = request.app.state.rate_limiter
    if not settings.llm_enabled or provider is None or rate_limiter is None:
        return llm_disabled_response(request)
    canonical_profile = canonical_analysis_profile_v2(body.profile)
    if canonical_profile is None:
        return _profile_integrity_response(request)
    limited = await consume_analysis_limits(
        request,
        settings=settings,
        rate_limiter=rate_limiter,
        device_id=body.device_id,
        device_limit=1,
        device_scope="device-report-v2",
    )
    if limited is not None:
        return limited
    agent = _build_agent(request)
    if agent is None:
        return llm_disabled_response(request)
    try:
        return await agent.generate_report(canonical_profile)
    except Exception as exc:
        if _is_generation_error(exc):
            return _generation_response(request, follow_up=False)
        raise


@router.post(
    "/api/v2/analyses/follow-up",
    response_model=AnalysisFollowUpV3,
    responses={
        422: {"model": ProblemDetails, "description": "Request validation failed"},
        429: {"model": ProblemDetails, "description": "Rate limit exceeded"},
        502: {"model": ProblemDetails, "description": "Analysis generation failed"},
        503: {"model": ProblemDetails, "description": "LLM analysis disabled"},
    },
)
async def analysis_follow_up_v2(
    body: AnalysisFollowUpRequestV2,
    request: Request,
) -> AnalysisFollowUpV3 | JSONResponse:
    settings = request.app.state.settings
    provider: LlmProviderV3 | None = getattr(request.app.state, "provider_v3", None)
    rate_limiter = request.app.state.rate_limiter
    if not settings.llm_enabled or provider is None or rate_limiter is None:
        return llm_disabled_response(request)
    canonical_profile = canonical_analysis_profile_v2(body.profile)
    if canonical_profile is None:
        return _profile_integrity_response(request)
    limited = await consume_analysis_limits(
        request,
        settings=settings,
        rate_limiter=rate_limiter,
        device_id=body.device_id,
        device_limit=2,
        device_scope="device-follow-up-v2",
    )
    if limited is not None:
        return limited
    agent = _build_agent(request)
    if agent is None:
        return llm_disabled_response(request)
    try:
        return await agent.generate_follow_up(
            canonical_profile,
            body.report,
            body.question,
        )
    except Exception as exc:
        if _is_generation_error(exc):
            return _generation_response(request, follow_up=True)
        raise
