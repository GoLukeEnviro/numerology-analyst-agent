"""ASGI middleware for the Numra API: correlation, security, access and limits."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from numerology_api.http_models import ProblemDetails
from numerology_api.problem_details import PROBLEM_BASE, correlation_id, problem_response

_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_ACCESS_LOGGER = logging.getLogger("numerology_api.access")
_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach one bounded correlation ID to every request and response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        supplied = request.headers.get("X-Correlation-ID", "")
        correlation_id_value = (
            supplied if _CORRELATION_PATTERN.fullmatch(supplied) else str(uuid4())
        )
        request.state.correlation_id = correlation_id_value
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id_value
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
            correlation_id(request),
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
            return problem_response(
                ProblemDetails(
                    type=f"{PROBLEM_BASE}/origin",
                    title="Origin not allowed",
                    status=403,
                    code="ORIGIN_NOT_ALLOWED",
                    detail="The request origin is not allowed.",
                    correlation_id=correlation_id(request),
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
        response: JSONResponse = problem_response(
            ProblemDetails(
                type=f"{PROBLEM_BASE}/request-body-too-large",
                title="Request body too large",
                status=413,
                code="REQUEST_BODY_TOO_LARGE",
                detail="The request body exceeds the configured limit.",
                correlation_id=correlation_id(request),
            )
        )
        await response(scope, receive, send)
