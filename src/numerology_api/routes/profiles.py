"""Profile calculation routes for the Numra API."""

from __future__ import annotations

from fastapi import APIRouter

from numerology_api.http_models import (
    ProblemDetails,
    ProfileCalculationRequest,
)
from numerology_domain.models import ProfileCalculationResult
from numerology_engine.profile import calculate_profile

router = APIRouter(tags=["profiles"])


@router.post(
    "/api/v1/profiles/calculate",
    response_model=ProfileCalculationResult,
    responses={
        400: {"model": ProblemDetails, "description": "Calculation rejected"},
        422: {"model": ProblemDetails, "description": "Request validation failed"},
    },
)
async def calculate(request: ProfileCalculationRequest) -> ProfileCalculationResult:
    return calculate_profile(request.person, request.policy)
