"""Health and readiness routes for the Numra API."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_agent.provider import LlmProvider
from numerology_agent.rate_limit import RateLimiter
from numerology_api.http_models import LiveStatus, ReadyStatus

router = APIRouter(tags=["health"])


@router.get("/api/v1/health/live", response_model=LiveStatus)
async def live() -> LiveStatus:
    return LiveStatus()


@router.get("/api/v1/health/ready", response_model=ReadyStatus)
async def ready(
    request: Request,
) -> ReadyStatus | JSONResponse:
    settings = request.app.state.settings
    provider: LlmProvider | None = request.app.state.provider
    rate_limiter: RateLimiter | None = request.app.state.rate_limiter
    if not settings.llm_enabled:
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
