"""LLM analysis routes (report and follow-up) for the Numra API."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_agent.models import AnalysisFollowUp, AnalysisReport
from numerology_api.analysis_runtime import (
    analysis_generation_response,
    build_agent_service,
    canonical_analysis_profile,
    consume_analysis_limits,
    is_analysis_generation_error,
    llm_disabled_response,
    profile_integrity_response,
)
from numerology_api.http_models import (
    AnalysisFollowUpRequest,
    AnalysisReportRequest,
    ProblemDetails,
)

router = APIRouter(tags=["analyses"])


@router.post(
    "/api/v1/analyses/report",
    response_model=AnalysisReport,
    responses={
        422: {"model": ProblemDetails},
        429: {"model": ProblemDetails},
        503: {"model": ProblemDetails},
    },
)
async def analysis_report(
    body: AnalysisReportRequest,
    request: Request,
) -> AnalysisReport | JSONResponse:
    settings = request.app.state.settings
    provider = request.app.state.provider
    rate_limiter = request.app.state.rate_limiter
    circuit_breaker = request.app.state.circuit_breaker
    if not settings.llm_enabled or provider is None or rate_limiter is None:
        return llm_disabled_response(request)
    canonical_profile = canonical_analysis_profile(body.profile)
    if canonical_profile is None:
        return profile_integrity_response(request)
    limited = await consume_analysis_limits(
        request,
        settings=settings,
        rate_limiter=rate_limiter,
        device_id=body.device_id,
        device_limit=1,
        device_scope="device-report",
    )
    if limited is not None:
        return limited
    try:
        service = build_agent_service(
            provider,
            settings=settings,
            circuit_breaker=circuit_breaker,
        )
        return await service.generate_report(canonical_profile)
    except Exception as exc:
        if is_analysis_generation_error(exc):
            return analysis_generation_response(request, follow_up=False)
        raise


@router.post(
    "/api/v1/analyses/follow-up",
    response_model=AnalysisFollowUp,
    responses={
        422: {"model": ProblemDetails},
        429: {"model": ProblemDetails},
        503: {"model": ProblemDetails},
    },
)
async def analysis_follow_up(
    body: AnalysisFollowUpRequest,
    request: Request,
) -> AnalysisFollowUp | JSONResponse:
    settings = request.app.state.settings
    provider = request.app.state.provider
    rate_limiter = request.app.state.rate_limiter
    circuit_breaker = request.app.state.circuit_breaker
    if not settings.llm_enabled or provider is None or rate_limiter is None:
        return llm_disabled_response(request)
    canonical_profile = canonical_analysis_profile(body.profile)
    if canonical_profile is None:
        return profile_integrity_response(request)
    limited = await consume_analysis_limits(
        request,
        settings=settings,
        rate_limiter=rate_limiter,
        device_id=body.device_id,
        device_limit=2,
        device_scope="device-follow-up",
    )
    if limited is not None:
        return limited
    try:
        service = build_agent_service(
            provider,
            settings=settings,
            circuit_breaker=circuit_breaker,
        )
        return await service.generate_follow_up(
            canonical_profile,
            body.report,
            body.question,
        )
    except Exception as exc:
        if is_analysis_generation_error(exc):
            return analysis_generation_response(request, follow_up=True)
        raise
