"""RFC-9457-style ProblemDetails helpers shared across the API layer."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from numerology_api.http_models import ProblemDetails

PROBLEM_BASE = "https://numra.app/problems"


def problem_response(problem: ProblemDetails) -> JSONResponse:
    """Render a :class:`ProblemDetails` as an ``application/problem+json`` response."""
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json"),
        media_type="application/problem+json",
    )


def correlation_id(request: Request) -> str:
    """Return the bounded correlation ID attached by the correlation middleware.

    Falls back to a fresh UUID when the middleware did not run (e.g. in
    middleware that executes before the correlation middleware).
    """
    value = getattr(request.state, "correlation_id", "")
    return value if isinstance(value, str) and value else str(uuid4())
