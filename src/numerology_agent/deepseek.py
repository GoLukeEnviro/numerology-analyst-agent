"""Asynchronous DeepSeek chat-completion adapter.

DeepSeek is called with the thinking mode enabled (``reasoning_effort``
combined with ``thinking.type = "enabled"``). Sampling parameters
(``temperature`` / ``top_p``) are intentionally OMITTED because they are
ineffective under thinking mode — sampling is provider-managed and reported
as such in the provenance.

Retry strategy (provider-level, NOT schema-level):
- Transient errors (network, timeout, HTTP 429/502/503/504) are retried with
  exponential backoff + jitter up to ``max_retries`` attempts.
- Hard failures (HTTP 400/401/403, invalid key, unknown model) fail-closed
  immediately — no retry.
- Schema/JSON validation retries are handled one level up in the agent service
  (``AgentService`` allows at most ONE controlled regeneration).

``reasoning_content`` (the DeepSeek thinking trace) is deliberately NOT
extracted from the response and never enters :class:`ProviderResult`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from numerology_agent.models import ProviderResult
from numerology_agent.prompts import report_task_prompt, system_prompt
from numerology_agent.provider import ProviderError

_LOGGER = logging.getLogger("numerology_agent.deepseek")

#: HTTP status codes considered transient (safe to retry).
_TRANSIENT_STATUS: frozenset[int] = frozenset({429, 502, 503, 504})

#: HTTP status codes that are hard failures (never retried).
_HARD_STATUS: frozenset[int] = frozenset({400, 401, 403, 404, 422})


class DeepSeekSettings(BaseModel):
    """Immutable configuration for the DeepSeek provider.

    ``thinking_enabled`` and ``reasoning_effort`` activate the DeepSeek
    thinking mode. Because sampling is provider-managed in that mode,
    ``temperature`` and ``top_p`` are intentionally absent — they are reported
    as ``None`` in the provenance.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    api_key: SecretStr
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-pro"
    timeout_seconds: float = Field(default=90.0, gt=0, le=180)
    thinking_enabled: bool = True
    reasoning_effort: str = Field(default="high", pattern=r"^(high|medium|low)$")
    max_output_tokens: int = Field(default=8192, ge=256, le=32_768)
    max_retries: int = Field(default=3, ge=0, le=6)


class Sleeper(Protocol):
    """Awaitable sleep abstraction for deterministic tests."""

    async def __call__(self, delay: float) -> None: ...


class Jitter(Protocol):
    """Random jitter callable for backoff (``[0, factor)``)."""

    def __call__(self) -> float: ...


def _classify_error(exc: BaseException) -> str:
    """Classify an exception as 'transient', 'hard', or 'fatal'.

    Returns one of ``"transient"``, ``"hard"``, ``"fatal"``.
    - ``transient``: retryable (network, timeout, 429, 5xx transient).
    - ``hard``:     never retry (400/401/403, auth, model errors).
    - ``fatal``:    unexpected — propagate as ProviderError without retry.
    """
    if isinstance(exc, httpx.TimeoutException):
        return "transient"
    if isinstance(exc, httpx.ConnectError):
        return "transient"
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status in _TRANSIENT_STATUS:
            return "transient"
        return "hard"
    if isinstance(exc, KeyError | TypeError | ValueError):
        return "fatal"
    return "fatal"


class DeepSeekProvider:
    """Production DeepSeek adapter with retry and thinking-mode support."""

    def __init__(
        self,
        settings: DeepSeekSettings,
        *,
        client: httpx.AsyncClient | None = None,
        sleeper: Sleeper = asyncio.sleep,
        jitter: Jitter = random.random,
    ) -> None:
        self._settings = settings
        self._client = client
        self._sleeper = sleeper
        self._jitter = jitter

    def _build_request_body(
        self, payload: dict[str, Any], schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Construct the DeepSeek chat-completion request body.

        System and task prompts are loaded from versioned package data via
        ``numerology_agent.prompts``. Sampling parameters (``temperature`` /
        ``top_p``) are deliberately omitted: the thinking mode renders them
        ineffective.
        """
        body: dict[str, Any] = {
            "model": self._settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt(),
                },
                {
                    "role": "user",
                    "content": report_task_prompt()
                    + "\n\n"
                    + json.dumps(
                        {"context": payload, "output_schema": schema},
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                },
            ],
            "max_tokens": self._settings.max_output_tokens,
            "response_format": {"type": "json_object"},
        }
        if self._settings.thinking_enabled:
            body["thinking"] = {"type": "enabled"}
            body["reasoning_effort"] = self._settings.reasoning_effort
        return body

    async def _post(self, request_body: dict[str, Any]) -> httpx.Response:
        """Issue the HTTP POST, reusing an injected client or creating one."""
        url = f"{self._settings.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        timeout = self._settings.timeout_seconds
        if self._client is not None:
            return await self._client.post(url, json=request_body, headers=headers, timeout=timeout)
        async with httpx.AsyncClient() as client:
            return await client.post(url, json=request_body, headers=headers, timeout=timeout)

    async def complete(
        self,
        payload: dict[str, Any],
        schema: dict[str, Any],
    ) -> ProviderResult:
        """Call DeepSeek and return the completion content.

        Retries transient errors (network, timeout, 429, 502, 503, 504) with
        exponential backoff + jitter. Hard failures (400/401/403) fail-closed
        immediately.

        ``reasoning_content`` is NEVER extracted from the response.
        """
        request_body = self._build_request_body(payload, schema)
        last_exc: BaseException | None = None
        for attempt in range(self._settings.max_retries + 1):
            try:
                response = await self._post(request_body)
                response.raise_for_status()
                body = response.json()
                usage = body.get("usage", {})
                return ProviderResult(
                    content=str(body["choices"][0]["message"]["content"]),
                    model=str(body.get("model", self._settings.model)),
                    provider_fingerprint=body.get("system_fingerprint"),
                    prompt_tokens=int(usage.get("prompt_tokens", 0)),
                    completion_tokens=int(usage.get("completion_tokens", 0)),
                )
            except Exception as exc:
                classification = _classify_error(exc)
                last_exc = exc
                if classification == "hard":
                    raise ProviderError("LLM provider returned a hard failure") from exc
                if classification == "fatal":
                    raise ProviderError("LLM provider request failed") from exc
                # transient
                remaining = self._settings.max_retries - attempt
                if remaining <= 0:
                    break
                _LOGGER.debug("deepseek transient error (attempt %d), retrying", attempt + 1)
                delay = min(2.0**attempt, 30.0) * (0.5 + self._jitter() * 0.5)
                await self._sleeper(delay)
        raise ProviderError("LLM provider request failed after retries") from last_exc
