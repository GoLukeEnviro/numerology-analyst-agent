"""V3 DeepSeek provider — parallel to ``deepseek.py`` (V1 stack).

Adds ``finish_reason`` extraction and the verbindliche finish-reason matrix.
Uses the V3 prompt contract (``de-report-system-v3.md`` / ``de-report-task-v3.md``).
No tools, no web search — ever.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

import httpx

from numerology_agent.deepseek import (
    DeepSeekSettings,
    Jitter,
    Sleeper,
    _classify_error,
)
from numerology_agent.prompts_v3 import report_task_prompt_v3, system_prompt_v3
from numerology_agent.provider import ProviderError
from numerology_agent.provider_v3 import ProviderResultV3

_LOGGER = logging.getLogger("numerology_agent.deepseek_v3")


class DeepSeekProviderV3:
    """V3 DeepSeek adapter with finish_reason awareness and V3 prompt contract."""

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
        body: dict[str, Any] = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system_prompt_v3()},
                {
                    "role": "user",
                    "content": report_task_prompt_v3()
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
    ) -> ProviderResultV3:
        """Call DeepSeek V3 and return the completion with finish_reason.

        Finish-reason matrix:
        - ``stop`` → normal, validate content
        - ``length`` → incomplete (caller handles retry/orchestration)
        - ``content_filter`` → fail-closed
        - ``tool_calls`` → contract violation (no tools configured)
        - ``insufficient_system_resource`` → transient retry
        - empty/unknown → fail-closed
        """
        request_body = self._build_request_body(payload, schema)
        last_exc: BaseException | None = None
        for attempt in range(self._settings.max_retries + 1):
            try:
                response = await self._post(request_body)
                response.raise_for_status()
                body = response.json()
                choice = body["choices"][0]
                content = choice["message"].get("content")
                finish_reason = str(choice.get("finish_reason", ""))
                if not isinstance(content, str) or not content.strip():
                    raise ProviderError("LLM provider returned empty content")
                usage = body.get("usage", {})
                return ProviderResultV3(
                    content=str(content),
                    model=str(body.get("model", self._settings.model)),
                    finish_reason=finish_reason,
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
                if attempt < self._settings.max_retries:
                    delay = (2**attempt) * (0.5 + 0.5 * self._jitter())
                    _LOGGER.warning(
                        "deepseek_v3 transient error (attempt %d/%d), retrying in %.1fs",
                        attempt + 1,
                        self._settings.max_retries,
                        delay,
                    )
                    await self._sleeper(delay)
        raise ProviderError("LLM provider exhausted retries") from last_exc
