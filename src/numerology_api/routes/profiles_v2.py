"""V2 profile calculation routes for the Numra API.

Uses the existing ``calculate_profile_v2`` engine which produces
``ProfileCalculationResultV4`` — the only profile schema accepted
by the ``/api/v2/analyses/*`` family.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from numerology_api.http_models import (
    ProblemDetails,
    ProfileCalculationRequestV2,
)
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response
from numerology_domain.models import PYTHAGOREAN_V2_VERSION, ProfileCalculationResultV4
from numerology_engine.profile_v2 import calculate_profile_v2

router = APIRouter(tags=["profiles-v2"])


def _method_version_mismatch(request: Request, requested: str) -> JSONResponse:
    return problem_response(
        ProblemDetails(
            type=f"{PROBLEM_BASE}/method-version-mismatch",
            title="Method version not supported by this endpoint",
            status=422,
            code="METHOD_VERSION_MISMATCH",
            detail=(
                f"Dieser Endpunkt rechnet ausschliesslich mit Methodenversion "
                f"{PYTHAGOREAN_V2_VERSION!r}; angefragt wurde {requested!r}."
            ),
            correlation_id=correlation_id(request),
        )
    )


@router.post(
    "/api/v2/profiles/calculate",
    response_model=ProfileCalculationResultV4,
    responses={
        400: {"model": ProblemDetails, "description": "Calculation rejected"},
        422: {"model": ProblemDetails, "description": "Request validation failed"},
    },
)
async def calculate_v2(
    body: ProfileCalculationRequestV2,
    request: Request,
) -> ProfileCalculationResultV4 | JSONResponse:
    if body.policy.version != PYTHAGOREAN_V2_VERSION:
        return _method_version_mismatch(request, body.policy.version)
    return calculate_profile_v2(body.person, body.policy)
