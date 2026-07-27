"""HTTP contract for the production DeepSeek adapter."""

from __future__ import annotations

import json
from typing import Any, cast

import httpx
import pytest

from numerology_agent.deepseek import DeepSeekProvider, DeepSeekSettings


@pytest.mark.anyio
async def test_deepseek_uses_v4_pro_structured_thinking_contract() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(
            200,
            json={
                "model": "deepseek-reasoner",
                "system_fingerprint": "fp-1",
                "choices": [{"message": {"content": '{"summary":"ok"}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = DeepSeekProvider(
            DeepSeekSettings(api_key="secret", base_url="https://provider.invalid"),
            client=client,
        )
        result = await provider.complete({"facts": {}}, {"type": "object"})

    assert captured["model"] == "deepseek-reasoner"
    assert captured["temperature"] == 0.2
    assert captured["top_p"] == 1
    assert captured["max_tokens"] == 8192
    assert captured["response_format"] == {"type": "json_object"}
    assert captured["thinking"] == {"type": "enabled"}
    assert captured["reasoning_effort"] == "high"
    messages = cast(list[dict[str, Any]], captured["messages"])
    assert isinstance(messages[1]["content"], str)
    assert result.provider_fingerprint == "fp-1"
