"""End-to-end HTTP contracts for optional LLM analyses."""

from __future__ import annotations

from collections.abc import AsyncIterator
import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
import pytest

from numerology_agent.models import ProviderResult
from numerology_api.app import ApiSettings, create_app
from numerology_knowledge.loader import load_knowledge_bundle
from tests.integration.test_http_api import _request


def _life_path_knowledge_ref(number: int) -> str:
    """Return the stable_id for the life_path entry of the given number."""
    bundle = load_knowledge_bundle("de", "v2")
    entry = bundle.entry_for(number, context="life_path")
    return entry.stable_id


class ContractProvider:
    async def complete(self, payload: dict[str, Any], schema: dict[str, Any]) -> ProviderResult:
        facts = payload["facts"]
        assert isinstance(facts, list)
        life_path = next(fact for fact in facts if fact["calculation_ref"] == "life_path_a")
        knowledge_ref = _life_path_knowledge_ref(life_path["number"])
        content: dict[str, Any]
        if payload.get("prompt_version") == "numra-follow-up-de-v2":
            content = {
                "answer": "Diese Rückfrage kann als Reflexionsimpuls betrachtet werden.",
                "claims": [
                    {
                        "claim_type": "interpretive_hypothesis",
                        "text": "Möglicherweise zeigt sich Eigenständigkeit situationsabhängig.",
                        "calculation_ref": "life_path_a",
                        "knowledge_ref": knowledge_ref,
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
                                "knowledge_ref": knowledge_ref,
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
    def __init__(self, ready: bool = True) -> None:
        self.counts: dict[str, int] = {}
        self.keys: list[str] = []
        self.ready = ready

    async def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        self.keys.append(key)
        self.counts[key] = self.counts.get(key, 0) + 1
        return 3600 if self.counts[key] > limit else None

    async def is_ready(self) -> bool:
        return self.ready


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
    # Mock the runtime gate to always pass in tests
    with patch("numerology_api.app.verify_runtime_gates") as mock_gate:
        mock_gate.return_value = MagicMock(all_passed=True, platform_skipped=True)
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

    assert response.json()["provider"] == "configured"
    assert response.json()["redis"] == "ready"


@pytest.mark.anyio
async def test_ready_fails_when_the_rate_limit_store_is_unavailable() -> None:
    from unittest.mock import patch

    with patch("numerology_api.app.verify_runtime_gates") as mock_gates:
        mock_gates.return_value = None
        app = create_app(
            ApiSettings(
                environment="test",
                llm_enabled=True,
                rate_limit_hmac_secret=SecretStr("test-only-rate-limit-secret"),
            ),
            provider=ContractProvider(),
            rate_limiter=MemoryLimiter(ready=False),
        )
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="https://test",
        ) as client:
            response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["redis"] == "unavailable"


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
async def test_report_recalculates_a_legacy_v2_profile_as_canonical_v3(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state
    current_profile = await _profile(client)
    legacy_profile = json.loads(json.dumps(current_profile))
    legacy_profile["schema_version"] = "profile-calculation-result-v2"
    legacy_profile["core_name"].pop("maturity")
    legacy_profile["active_name"].pop("maturity")
    legacy_profile["birthday"]["reduced_value"] = 99
    legacy_profile["maturity"]["reduced_value"] = 99
    legacy_profile["deterministic_hash"] = "f" * 64

    response = await client.post(
        "/api/v1/analyses/report",
        json={
            "consent": True,
            "device_id": "device-legacy-v2-1234",
            "profile": legacy_profile,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["provenance"]["calculation_hash"] == current_profile["deterministic_hash"]
    )


@pytest.mark.anyio
async def test_report_rejects_an_unknown_profile_schema_before_consuming_quota(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, limiter = enabled_state
    profile = await _profile(client)
    profile["schema_version"] = "profile-calculation-result-v99"

    response = await client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": "device-unknown-v99-1234", "profile": profile},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "PROFILE_INTEGRITY_FAILED"
    assert limiter.keys == []


@pytest.mark.anyio
@pytest.mark.parametrize("field", ["deterministic_hash", "maturity"])
async def test_report_rejects_a_tampered_profile_before_consuming_quota(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
    field: str,
) -> None:
    client, limiter = enabled_state
    profile = await _profile(client)
    if field == "deterministic_hash":
        profile[field] = "f" * 64
    else:
        profile[field]["reduced_value"] = 99

    response = await client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": "device-contract-1234", "profile": profile},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "PROFILE_INTEGRITY_FAILED"
    assert limiter.keys == []


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
async def test_report_quota_is_per_device_day_not_per_profile(
    enabled_state: tuple[AsyncClient, MemoryLimiter],
) -> None:
    client, _ = enabled_state
    first_profile = await _profile(client)
    alternate_request = _request()
    alternate_person = cast(dict[str, Any], alternate_request["person"])
    alternate_person["core_name"] = "Anna Beispiel"
    alternate_person["active_name"] = None
    alternate_response = await client.post(
        "/api/v1/profiles/calculate",
        json=alternate_request,
    )
    alternate_profile = alternate_response.json()
    device_id = "device-daily-quota-1234"

    assert (
        await client.post(
            "/api/v1/analyses/report",
            json={"consent": True, "device_id": device_id, "profile": first_profile},
        )
    ).status_code == 200
    denied = await client.post(
        "/api/v1/analyses/report",
        json={"consent": True, "device_id": device_id, "profile": alternate_profile},
    )

    assert denied.status_code == 429
    assert denied.json()["code"] == "LLM_DEVICE_QUOTA_EXCEEDED"


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
