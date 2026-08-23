"""V2/V3 HTTP contract tests — /api/v2 endpoint family.

Covers the four V2 endpoints:
- GET  /api/v2/meta
- POST /api/v2/profiles/calculate
- POST /api/v2/analyses/report
- POST /api/v2/analyses/follow-up

Fail-closed behaviour is verified for the LLM-disabled configuration using
canonical, server-validated payloads (the Pydantic body validation runs
before the handler's LLM-enabled check, so the payloads must be valid).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest

from numerology_agent.models_v3 import (
    AnalysisProvenanceV3,
    AnalysisReportContentV3,
    AnalysisReportV3,
    AnalysisSectionV3,
    ClaimV3,
)
from numerology_api.app import ApiSettings, create_app
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    PersonInput,
    ProfileCalculationResultV4,
)
from numerology_engine.profile_v2 import calculate_profile_v2

_HEX64 = "a" * 64


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app(
        ApiSettings(
            environment="test",
            allowed_origins=("https://numra.example",),
        )
    )
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://testserver",
    ) as http_client:
        yield http_client


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _v2_request() -> dict[str, object]:
    return {
        "person": {
            "core_name": "Lukas Springer",
            "birth_date": "1986-07-18",
            "as_of_date": "2026-07-28",
            "locale": "de",
            "consent_given": False,
        },
        "policy": {
            "system": "pythagorean",
            "version": PYTHAGOREAN_V2_VERSION,
            "y_mode": "phonetic",
            "umlaut_policy": "de-expanded-v1",
            "name_basis": "both_separate",
            "date_method": "both",
            "locale": "de",
            "master_numbers": [11, 22, 33],
        },
    }


def _canonical_v4_profile() -> ProfileCalculationResultV4:
    request = _v2_request()
    person = PersonInput.model_validate(request["person"])
    policy = request["policy"]
    from numerology_domain.models import MethodPolicy

    return calculate_profile_v2(person, MethodPolicy.model_validate(policy))


def _valid_report_v3(profile: ProfileCalculationResultV4) -> AnalysisReportV3:
    """Build a minimal schema-valid AnalysisReportV3 for follow-up requests."""
    claim = ClaimV3(claim_id="c-1", text="Ein deterministischer Test-Claim.")
    section = AnalysisSectionV3(
        section_id="executive_overview",
        summary="Zusammenfassung des Testberichts.",
        claims=(claim,),
    )
    return AnalysisReportV3(
        report_id=uuid4(),
        content=AnalysisReportContentV3(
            summary="Testbericht.",
            sections=(section,),
        ),
        report_content_hash=_HEX64,
        generation_context_hash=_HEX64,
        provenance=AnalysisProvenanceV3(
            provider="test",
            model="test-model",
            prompt_version="numra-report-de-v3",
            knowledge_bundle="numra-knowledge-de-v3",
            calculation_hash=profile.deterministic_hash,
            prompt_tokens=10,
            completion_tokens=10,
            context_signature=_HEX64,
        ),
        context_signature=_HEX64,
    )


@pytest.mark.integration
@pytest.mark.anyio
async def test_v2_meta_reports_capability_contract(client: AsyncClient) -> None:
    response = await client.get("/api/v2/meta")

    assert response.status_code == 200
    payload = response.json()
    assert payload["api_version"] == "v2"
    assert payload["endpoint_method_version"] == "v2"
    assert payload["product_default_method_version"] == "v1"
    assert payload["rollout_stage"] == "disabled"
    assert payload["supported_method_versions"] == ["v2"]
    assert payload["supported_profile_schema_versions"] == ["profile-calculation-result-v4"]
    assert payload["supported_report_schema_versions"] == ["analysis-report-v3"]
    assert payload["supported_knowledge_bundles"] == ["numra-knowledge-de-v3"]
    assert payload["llm"]["enabled"] is False


@pytest.mark.integration
@pytest.mark.anyio
async def test_v2_profile_calculate_returns_v4_golden_values(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v2/profiles/calculate",
        json=_v2_request(),
        headers={"X-Correlation-ID": "v2-golden"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "profile-calculation-result-v4"
    assert payload["life_path_primary"]["display_notation"] == "40/4"
    assert payload["life_path_primary"]["root_value"] == 4
    assert payload["life_path_secondary"]["display_notation"] == "22/4"
    assert payload["life_path_secondary"]["held_master_value"] == 22
    assert payload["life_path_secondary"]["is_master"] is True
    assert payload["birthday"]["display_notation"] == "18/9"
    assert payload["attitude"]["display_notation"] == "25/7"
    assert payload["core_name"]["expression"]["display_notation"] == "62/8"
    assert payload["core_name"]["soul_urge"]["display_notation"] == "18/9"
    assert payload["core_name"]["personality"]["display_notation"] == "44/8"
    assert payload["core_name"]["personality"]["is_master"] is False
    assert payload["core_name"]["maturity"]["display_notation"] == "12/3"
    assert payload["cycles"]["personal_year"]["display_notation"] == "17/8"
    pinnacles = [p["display_notation"] for p in payload["cycles"]["pinnacles"]]
    assert pinnacles == ["16/7", "15/6", "13/4", "13/4"]
    challenges = [c["display_notation"] for c in payload["cycles"]["challenges"]]
    assert challenges == ["2", "3", "1", "1"]
    assert len(payload["deterministic_hash"]) == 64


@pytest.mark.integration
@pytest.mark.anyio
async def test_v2_profile_rejects_foreign_method_version(client: AsyncClient) -> None:
    request = _v2_request()
    policy = request["policy"]
    assert isinstance(policy, dict)
    policy["version"] = "v1"

    response = await client.post(
        "/api/v2/profiles/calculate",
        json=request,
        headers={"X-Correlation-ID": "v2-method-version"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "METHOD_VERSION_MISMATCH"


@pytest.mark.integration
@pytest.mark.anyio
async def test_v2_analysis_report_fails_closed_when_llm_disabled(client: AsyncClient) -> None:
    profile = _canonical_v4_profile()
    response = await client.post(
        "/api/v2/analyses/report",
        json={
            "consent": True,
            "device_id": "device-1234567890abcdef",
            "profile": profile.model_dump(mode="json"),
        },
        headers={"X-Correlation-ID": "v2-report-disabled"},
    )

    # LLM disabled → 503 fail-closed (after body validation, before provider).
    assert response.status_code == 503
    assert response.json()["code"] == "LLM_FEATURE_DISABLED"


@pytest.mark.integration
@pytest.mark.anyio
async def test_v2_analysis_follow_up_fails_closed_when_llm_disabled(client: AsyncClient) -> None:
    profile = _canonical_v4_profile()
    report = _valid_report_v3(profile)
    response = await client.post(
        "/api/v2/analyses/follow-up",
        json={
            "consent": True,
            "device_id": "device-1234567890abcdef",
            "profile": profile.model_dump(mode="json"),
            "report": report.model_dump(mode="json"),
            "question": "Was bedeutet das?",
        },
        headers={"X-Correlation-ID": "v2-followup-disabled"},
    )

    assert response.status_code == 503
    assert response.json()["code"] == "LLM_FEATURE_DISABLED"


@pytest.mark.integration
@pytest.mark.anyio
async def test_openapi_contains_all_four_v2_paths(client: AsyncClient) -> None:
    schema = (await client.get("/openapi.json")).json()

    assert "/api/v2/meta" in schema["paths"]
    assert "/api/v2/profiles/calculate" in schema["paths"]
    assert "/api/v2/analyses/report" in schema["paths"]
    assert "/api/v2/analyses/follow-up" in schema["paths"]
    # The V2 analysis responses must carry real schemas, not empty stubs.
    report_200 = schema["paths"]["/api/v2/analyses/report"]["post"]["responses"]["200"]
    assert "content" in report_200
    assert "$ref" in report_200["content"]["application/json"]["schema"]
    follow_up_200 = schema["paths"]["/api/v2/analyses/follow-up"]["post"]["responses"]["200"]
    assert "content" in follow_up_200
    assert "$ref" in follow_up_200["content"]["application/json"]["schema"]
