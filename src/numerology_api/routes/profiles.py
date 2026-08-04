"""Profile calculation routes for the Numra API."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_api.http_models import (
    ProblemDetails,
    ProfileCalculationRequest,
)
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response
from numerology_domain.models import PYTHAGOREAN_V1_VERSION, ProfileCalculationResult
from numerology_engine.profile import calculate_profile

router = APIRouter(tags=["profiles"])


def method_version_mismatch_response(request: Request, requested: str) -> JSONResponse:
    """Return the stable 422 ProblemDetails for a version this endpoint cannot serve.

    Without this guard the endpoint answered a ``v2`` request with 200 and a v1
    result carrying the v2 policy in its envelope — a mislabelling no client
    could detect.
    """
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/method-version-mismatch",
            title="Method version not supported by this endpoint",
            status=422,
            code="METHOD_VERSION_MISMATCH",
            detail=(
                f"Dieser Endpunkt rechnet ausschliesslich mit Methodenversion "
                f"{PYTHAGOREAN_V1_VERSION!r}; angefragt wurde {requested!r}."
            ),
            correlation_id=correlation_id(request),
        )
    )


@router.post(
    "/api/v1/profiles/calculate",
    response_model=ProfileCalculationResult,
    responses={
        400: {"model": ProblemDetails, "description": "Calculation rejected"},
        422: {"model": ProblemDetails, "description": "Request validation failed"},
    },
)
async def calculate(
    body: ProfileCalculationRequest,
    request: Request,
) -> ProfileCalculationResult | JSONResponse:
    if body.policy.version != PYTHAGOREAN_V1_VERSION:
        return method_version_mismatch_response(request, body.policy.version)
    return calculate_profile(body.person, body.policy)
