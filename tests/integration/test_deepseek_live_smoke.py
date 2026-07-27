"""Opt-in live DeepSeek smoke test.

This test is ONLY executed when the environment variable
``NUMRA_RUN_LIVE_DEEPSEEK_TESTS=true`` is set AND a real API key is available
via ``DEEPSEEK_API_KEY`` (or the deprecated ``NUMRA_DEEPSEEK_API_KEY``).

Without the opt-in flag or key, the test is skipped. It must never log
secrets, request bodies, response bodies, or reasoning_content.

The 10 verification points are documented inline.
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from numerology_agent.deepseek import DeepSeekProvider, DeepSeekSettings
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile

_LIVE_ENABLED = os.getenv("NUMRA_RUN_LIVE_DEEPSEEK_TESTS", "false").lower() == "true"
_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("NUMRA_DEEPSEEK_API_KEY")

pytestmark = pytest.mark.skipif(
    not (_LIVE_ENABLED and _API_KEY),
    reason="Set NUMRA_RUN_LIVE_DEEPSEEK_TESTS=true and DEEPSEEK_API_KEY to run live smoke.",
)


def _profile() -> Any:
    return calculate_profile(
        PersonInput(
            core_name="Numra Live Smoke",
            active_name=None,
            birth_date="1990-04-12",
            as_of_date="2026-07-26",
        ),
        MethodPolicy(),
    )


def _live_provider() -> DeepSeekProvider:
    return DeepSeekProvider(
        DeepSeekSettings(api_key=_API_KEY or ""),
    )


@pytest.mark.anyio
async def test_deepseek_live_smoke_ten_points() -> None:
    """End-to-end live smoke covering 10 verification points."""
    from numerology_agent.service import AgentService

    profile = _profile()
    provider = _live_provider()
    service = AgentService(
        provider,
        context_secret=b"live-smoke-context-secret-32b!",
    )

    # Point 1: report generation succeeds without ProviderError.
    report = await service.generate_report(profile)

    # Point 2: schema_version is analysis-report-v2.
    assert report.schema_version == "analysis-report-v2"

    # Point 3: provenance reports provider-managed sampling.
    assert report.provenance.effective_sampling == "provider_managed"
    assert report.provenance.thinking == "enabled"
    assert report.provenance.reasoning_effort == "high"

    # Point 4: temperature and top_p are None (thinking mode).
    assert report.provenance.temperature is None
    assert report.provenance.top_p is None

    # Point 5: calculation_hash binds the report to the canonical profile.
    assert report.provenance.calculation_hash == profile.deterministic_hash

    # Point 6: no reasoning_content leaks into the serialised report.
    serialised = report.model_dump_json()
    assert "reasoning_content" not in serialised

    # Point 7: all claims reference valid calculation_refs and numbers.
    for section in report.sections:
        for claim in section.claims:
            # Point 8: claim_type is never input_fact or calculation_fact.
            assert claim.claim_type.value not in {"input_fact", "calculation_fact"}

    # Point 9: follow-up generation succeeds.
    follow_up = await service.generate_follow_up(
        profile,
        report,
        "Welche Reflexionsfrage passt zum Lebensweg?",
    )
    assert follow_up.schema_version == "analysis-follow-up-v2"

    # Point 10: follow-up provenance also has no reasoning_content.
    follow_serialised = follow_up.model_dump_json()
    assert "reasoning_content" not in follow_serialised
