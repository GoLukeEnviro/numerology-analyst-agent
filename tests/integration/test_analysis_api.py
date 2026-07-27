"""End-to-end HTTP contracts for optional LLM analyses."""

from __future__ import annotations

from collections.abc import AsyncIterator
import json
from typing import Any, cast

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
import pytest

from numerology_agent.models import ProviderResult
from numerology_api.app import ApiSettings, create_app
from tests.integration.test_http_api import _request


class ContractProvider:
    async def complete(self, payload: dict[str, Any], schema: dict[str, Any]) -> ProviderResult:
        facts = payload["facts"]
        assert isinstance(facts, list)
        life_path = next(fact for fact in facts if fact["calculation_ref"] == "life_path_a")
        content: dict[str, Any]
        if payload.get("prompt_version") == "numra-follow-up-de-v1":
            content = {
                "answer": "Diese Rückfrage kann als Reflexionsimpuls betrachtet werden.",
                "claims": [
                    {
                        "claim_type": "interpretive_hypothesis",
                        "text": "Möglicherweise zeigt sich Eigenständigkeit situationsabhängig.",
                        "calculation_ref": "life_path_a",
                        "knowledge_ref": f"numra-knowledge-de-v1:number:{life_path['number']}",
                        "number": life_path["number"],
                    }
                ],
                "limitations": ["Die Antwort ist keine wissenschaftliche Diagnose."],
            }
        else:
            content = {
                "summary": "Eine strukturierte Einladung zur Reflexion.",
                "sections": [
                    {
                        "title": "Lebensweg",
                        "claims": [
                            {
                                "claim_type": "interpretive_hypothesis",
                                "text": "Möglicherweise lohnt sich ein Blick auf Eigenständigkeit.",
                                "calculation_ref": "life_path_a",
                                "knowledge_ref": (
                                    f"numra-knowledge-de-v1:number:{life_path['number']}"
                                ),
                                "number": life_path["number"],
                            }
                        ],
                    }
                ],
                "limitations": ["Numerologie ist keine wissenschaftliche Diagnostik."],
                "suggestions": ["Prüfe diese Anregung anhand eigener Erfahrungen."],
            }
        return ProviderResult(
            content=json.dumps(content),
            model="contract-model",
            provider_fingerprint="contract-fp",
            prompt_tokens=40,
            completion_tokens=20,
        )


class MemoryLimiter:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.keys: list[str] = []

    async def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        self.keys.append(key)
        self.counts[key] = self.counts.get(key, 0) + 1
        return 3600 if self.counts[key] > limit else None


async def _profile(client: AsyncClient) -> dict[str, Any]:
    response = await client.post("/api/v1/profiles/calculate", json=_request())
    assert response.status_code == 200
    return cast(dict[str, Any], response.json())


@pytest.fixture
async def disabled_client() -> AsyncIterator[AsyncClient]:
    app = create_app(ApiSettings(environment="test"))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        yield client


@pytest.fixture
async def enabled_state() -> AsyncIterator[tuple[AsyncClient, MemoryLimiter]]:
    limiter = MemoryLimiter()
    app = create_app(
        ApiSettings(
            environment="test",
            llm_enabled=True,
            rate_limit_hmac_secret=SecretStr("test-only-rate-limit-secret"),
        ),
        provider=ContractProvider(),
        rate_limiter=limiter,
    )
    async with AsyncClient(
        transport=ASGITransport(app=app, client=("203.0.113.42", 1234)),
        base_url="https://test",
    ) as client:
        yield client, limiter


@pytest.mark.anyio
async def test_llm_is_disabled_by_default(disabled_client: AsyncClient) -> None:
    profile = await _profile(disabled_client)
    response = await disabled_client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": "device-contract-1234", "profile": profile},
    )

    assert response.status_code == 503
    assert response.json()["code"] == "LLM_FEATURE_DISABLED"


@pytest.mark.anyio
async def test_report_requires_explicit_consent(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state
    profile = await _profile(client)
    response = await client.post(
        "/api/v1/analyses/report",
        json={"consent": False, "device_id": "device-contract-1234", "profile": profile},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_ready_reports_configured_llm_dependencies(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state

    response = await client.get("/api/v1/health/ready")

    assert response.json()["provider"] == "ready"
    assert response.json()["redis"] == "ready"


@pytest.mark.anyio
async def test_report_is_generated_without_raw_ip_in_rate_limit_keys(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, limiter = enabled_state
    profile = await _profile(client)
    response = await client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": "device-contract-1234", "profile": profile},
    )

    assert response.status_code == 200
    assert response.json()["provenance"]["provider"] == "deepseek"
    assert all("203.0.113.42" not in key for key in limiter.keys)


@pytest.mark.anyio
async def test_second_report_returns_problem_details_with_retry_after(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state
    profile = await _profile(client)
    payload = {"consent": True, "device_id": "device-contract-1234", "profile": profile}
    assert (await client.post("/api/v1/analyses/report", json=payload)).status_code == 200

    response = await client.post("/api/v1/analyses/report", json=payload)

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "3600"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "LLM_DEVICE_QUOTA_EXCEEDED"


@pytest.mark.anyio
async def test_only_two_follow_ups_are_allowed(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state
    profile = await _profile(client)
    report_response = await client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": "device-followup-1234", "profile": profile},
    )
    report = report_response.json()
    payload = {
        "consent": True,
        "device_id": "device-followup-1234",
        "profile": profile,
        "report": report,
        "question": "Welche Reflexionsfrage passt zum Lebensweg?",
    }

    assert (await client.post("/api/v1/analyses/follow-up", json=payload)).status_code == 200
    assert (await client.post("/api/v1/analyses/follow-up", json=payload)).status_code == 200
    denied = await client.post("/api/v1/analyses/follow-up", json=payload)
    assert denied.status_code == 429
    assert denied.headers["Retry-After"] == "3600"
