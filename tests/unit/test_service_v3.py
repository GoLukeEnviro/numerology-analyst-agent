"""AgentServiceV3 fail-closed tests — /api/v2/analyses/* provider pipeline.

Covers the finish-reason matrix, draft validation (unknown/duplicate/out-of-order
sections), invalid JSON, and the fact-package pipeline.  The service must fail
closed: no partially validated analysis may be returned as success.
"""

from __future__ import annotations

import json

import pytest

from numerology_agent.models_v3 import (
    SECTION_ORDER,
    AnalysisDraftV3,
    AnalysisReportContentV3,
    AnalysisSectionV3,
    ClaimV3,
)
from numerology_agent.provider import ProviderError
from numerology_agent.provider_v3 import LlmProviderV3, ProviderResultV3
from numerology_agent.service_v3 import AgentServiceV3
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
    ProfileCalculationResultV4,
)
from numerology_engine.profile_v2 import calculate_profile_v2


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class _StubProvider:
    """Provider stub returning a fixed sequence of ProviderResultV3."""

    def __init__(self, results: list[ProviderResultV3]) -> None:
        self._results = list(results)
        self.calls: list[tuple[dict[str, object], dict[str, object]]] = []

    async def complete(
        self,
        payload: dict[str, object],
        schema: dict[str, object],
    ) -> ProviderResultV3:
        self.calls.append((payload, schema))
        if not self._results:
            raise ProviderError("no more stub results")
        return self._results.pop(0)


def _profile() -> ProfileCalculationResultV4:
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date="1986-07-18",
        as_of_date="2026-07-28",
    )
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION, umlaut_policy="de-expanded-v1")
    return calculate_profile_v2(person, policy)


def _valid_draft_json() -> str:
    sections = [
        AnalysisSectionV3(
            section_id=sid,
            summary=f"Zusammenfassung {sid}.",
            claims=(ClaimV3(claim_id=f"c-{sid}", text=f"Claim {sid}."),),
        )
        for sid in SECTION_ORDER
    ]
    draft = AnalysisDraftV3(
        content=AnalysisReportContentV3(
            summary="Testbericht.",
            sections=tuple(sections),
        )
    )
    return draft.model_dump_json()


def _result(content: str, *, finish_reason: str = "stop") -> ProviderResultV3:
    return ProviderResultV3(
        content=content,
        model="test-model",
        finish_reason=finish_reason,
        prompt_tokens=10,
        completion_tokens=10,
    )


def _service(provider: LlmProviderV3) -> AgentServiceV3:
    return AgentServiceV3(provider, hmac_secret=b"test-secret")


@pytest.mark.anyio
async def test_generate_report_success_with_valid_draft() -> None:
    provider = _StubProvider([_result(_valid_draft_json())])
    report = await _service(provider).generate_report(_profile())

    assert report.schema_version == "analysis-report-v3"
    assert len(report.report_content_hash) == 64
    assert len(report.generation_context_hash) == 64
    assert len(report.context_signature) == 64
    assert len(report.provenance.context_signature) == 64
    assert report.provenance.calculation_hash == _profile().deterministic_hash


@pytest.mark.anyio
async def test_generate_report_fails_closed_on_invalid_json() -> None:
    provider = _StubProvider([_result("{not-json")])
    with pytest.raises(ValueError):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_generate_report_fails_closed_on_unknown_section() -> None:
    draft = json.loads(_valid_draft_json())
    draft["content"]["sections"][0]["section_id"] = "unknown_section"
    provider = _StubProvider([_result(json.dumps(draft))])
    with pytest.raises(ValueError, match="unknown section_id"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_generate_report_fails_closed_on_duplicate_section() -> None:
    draft = json.loads(_valid_draft_json())
    draft["content"]["sections"][1]["section_id"] = draft["content"]["sections"][0]["section_id"]
    provider = _StubProvider([_result(json.dumps(draft))])
    with pytest.raises(ValueError, match="duplicate section_id"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_generate_report_fails_closed_on_out_of_order_section() -> None:
    draft = json.loads(_valid_draft_json())
    first, second = draft["content"]["sections"][0], draft["content"]["sections"][1]
    draft["content"]["sections"][0], draft["content"]["sections"][1] = second, first
    provider = _StubProvider([_result(json.dumps(draft))])
    with pytest.raises(ValueError, match="expected"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_generate_report_fails_closed_on_missing_section() -> None:
    draft = json.loads(_valid_draft_json())
    draft["content"]["sections"] = draft["content"]["sections"][:-1]
    provider = _StubProvider([_result(json.dumps(draft))])
    with pytest.raises(ValueError, match="expected 18 sections"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_finish_reason_length_fails_closed() -> None:
    provider = _StubProvider([_result(_valid_draft_json(), finish_reason="length")])
    with pytest.raises(ProviderError, match="truncated"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_finish_reason_content_filter_fails_closed() -> None:
    provider = _StubProvider([_result(_valid_draft_json(), finish_reason="content_filter")])
    with pytest.raises(ProviderError, match="fail-closed"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_finish_reason_empty_fails_closed() -> None:
    provider = _StubProvider([_result(_valid_draft_json(), finish_reason="")])
    with pytest.raises(ProviderError, match="empty finish_reason"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_finish_reason_unknown_fails_closed() -> None:
    provider = _StubProvider([_result(_valid_draft_json(), finish_reason="mystery")])
    with pytest.raises(ProviderError, match="unknown finish_reason"):
        await _service(provider).generate_report(_profile())


@pytest.mark.anyio
async def test_provider_payload_contains_no_personal_data() -> None:
    provider = _StubProvider([_result(_valid_draft_json())])
    await _service(provider).generate_report(_profile())

    payload = provider.calls[0][0]
    blob = json.dumps(payload)
    assert "Lukas" not in blob
    assert "Springer" not in blob
    assert "1986" not in blob
    assert "07-18" not in blob
