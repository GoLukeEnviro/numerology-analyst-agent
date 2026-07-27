"""HTTP contract for the production DeepSeek adapter."""

from __future__ import annotations

import json
from typing import Any, cast

import httpx
import pytest

from numerology_agent.deepseek import DeepSeekProvider, DeepSeekSettings
from numerology_agent.provider import ProviderError


def _success_response(content: str = '{"summary":"ok"}') -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "deepseek-v4-pro",
            "system_fingerprint": "fp-1",
            "choices": [{"message": {"content": content}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        },
    )


@pytest.mark.anyio
async def test_deepseek_uses_thinking_mode_without_sampling_parameters() -> None:
    """The thinking mode renders temperature/top_p ineffective — they are omitted."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        assert request.headers["Authorization"] == "Bearer secret"
        return _success_response()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid"),
            client=client,
        )
        result = await provider.complete({"facts": {}}, {"type": "object"})

    assert captured["model"] == "deepseek-v4-pro"
    # Sampling parameters are deliberately ABSENT (thinking mode = provider-managed).
    assert "temperature" not in captured
    assert "top_p" not in captured
    assert captured["max_tokens"] == 8192
    assert captured["response_format"] == {"type": "json_object"}
    assert captured["thinking"] == {"type": "enabled"}
    assert captured["reasoning_effort"] == "high"
    messages = cast(list[dict[str, Any]], captured["messages"])
    assert isinstance(messages[1]["content"], str)
    assert result.provider_fingerprint == "fp-1"


@pytest.mark.anyio
async def test_reasoning_content_never_enters_provider_result() -> None:
    """Even if the API returns reasoning_content, it must not leak into ProviderResult."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-pro",
                "system_fingerprint": "fp-reasoning",
                "choices": [
                    {
                        "message": {
                            "content": '{"summary":"ok"}',
                            "reasoning_content": "SECRET THINKING TRACE",
                        }
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid"),
            client=client,
        )
        result = await provider.complete({"facts": {}}, {"type": "object"})

    serialised = result.model_dump_json()
    assert "reasoning_content" not in serialised
    assert "SECRET THINKING TRACE" not in serialised
    assert result.content == '{"summary":"ok"}'


@pytest.mark.anyio
async def test_transient_error_is_retried() -> None:
    """HTTP 503 is transient and should be retried."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 2:
            return httpx.Response(503, json={"error": "unavailable"})
        return _success_response()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid", max_retries=2),
            client=client,
            sleeper=lambda _delay: _noop(),
        )
        result = await provider.complete({"facts": {}}, {"type": "object"})

    assert calls == 2
    assert result.content == '{"summary":"ok"}'


@pytest.mark.anyio
async def test_rate_limit_429_is_retried() -> None:
    """HTTP 429 is transient and should be retried."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(429, json={"error": "rate limit"})
        return _success_response()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid", max_retries=3),
            client=client,
            sleeper=lambda _delay: _noop(),
        )
        result = await provider.complete({"facts": {}}, {"type": "object"})

    assert calls == 3
    assert result.content == '{"summary":"ok"}'


@pytest.mark.anyio
async def test_hard_failure_401_is_not_retried() -> None:
    """HTTP 401 is a hard failure — fail-closed immediately, no retry."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401, json={"error": "invalid api key"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="bad-key", base_url="https://provider.invalid", max_retries=3),
            client=client,
            sleeper=lambda _delay: _noop(),
        )
        with pytest.raises(ProviderError, match="hard failure"):
            await provider.complete({"facts": {}}, {"type": "object"})

    assert calls == 1


@pytest.mark.anyio
async def test_hard_failure_400_is_not_retried() -> None:
    """HTTP 400 is a hard failure — fail-closed immediately."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(400, json={"error": "bad request"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid", max_retries=3),
            client=client,
            sleeper=lambda _delay: _noop(),
        )
        with pytest.raises(ProviderError, match="hard failure"):
            await provider.complete({"facts": {}}, {"type": "object"})

    assert calls == 1


@pytest.mark.anyio
async def test_all_retries_exhausted_raises_provider_error() -> None:
    """When all retries are exhausted, a ProviderError is raised."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={"error": "unavailable"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid", max_retries=1),
            client=client,
            sleeper=lambda _delay: _noop(),
        )
        with pytest.raises(ProviderError, match="after retries"):
            await provider.complete({"facts": {}}, {"type": "object"})

    assert calls == 2  # initial + 1 retry


async def _noop() -> None:
    """No-op sleeper for deterministic retry tests."""
    pass
