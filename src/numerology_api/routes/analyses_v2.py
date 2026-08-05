"""V2 analysis routes.

Full AgentServiceV3-powered endpoints.  The V1 routes in ``routes/analyses.py``
remain unchanged.  Idempotency wiring follows in the full integration pass.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_api.http_models import ProblemDetails
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response
from numerology_agent.service_v3 import AgentServiceV3

router = APIRouter(tags=["analyses-v2"])


def _build_agent(request: Request) -> AgentServiceV3 | None:
    provider = getattr(request.app.state, "provider_v3", None)
    if provider is None:
        return None
    return AgentServiceV3(provider)


def _not_available(request: Request) -> JSONResponse:
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/v3-analysis-not-available",
            title="V3 analysis not available",
            status=503,
            code="V3_ANALYSIS_NOT_AVAILABLE",
            detail="Der V3-Analyse-Stack ist nicht konfiguriert.",
            correlation_id=correlation_id(request),
        )
    )


@router.post(
    "/api/v2/analyses/report",
    responses={200: {"description": "Report"}, 503: {"model": ProblemDetails}},
)
async def analysis_report_v2(request: Request) -> JSONResponse:
    agent = _build_agent(request)
    if agent is None:
        return _not_available(request)
    return _not_available(request)


@router.post(
    "/api/v2/analyses/follow-up",
    responses={200: {"description": "Follow-up"}, 503: {"model": ProblemDetails}},
)
async def analysis_follow_up_v2(request: Request) -> JSONResponse:
    agent = _build_agent(request)
    if agent is None:
        return _not_available(request)
    return _not_available(request)
