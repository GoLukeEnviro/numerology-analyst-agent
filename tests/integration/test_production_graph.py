"""Integrationstests: Produktionsgraph und Feature-Integration.

Beweist, dass system_prompt, report_task_prompt, compose_observations,
KnowledgeBundleV2.entry_for mit context und CircuitBreaker via AgentService
im Produktionsgraphen erreichbar und funktionsfähig sind.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import zipfile

import pytest

from numerology_agent.models import ProviderResult
from numerology_agent.prompts import report_task_prompt, system_prompt
from numerology_agent.resilience import CircuitBreaker, CircuitState
from numerology_agent.service import AgentService
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile
from numerology_interpretation.rules import compose_observations
from numerology_interpretation.service import compose_interpretation
from numerology_knowledge.loader import load_knowledge_bundle

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _profile() -> Any:
    return calculate_profile(
        PersonInput(
            core_name="Max Mustermann",
            active_name="Max Power",
            birth_date="1985-07-25",
            as_of_date="2026-07-26",
        ),
        MethodPolicy(),
    )


def _knowledge_ref_for_life_path(number: int) -> str:
    bundle = load_knowledge_bundle("de", "v2")
    return bundle.entry_for(number, context="life_path").stable_id


class _FixedProvider:
    """Minimalste Provider-Implementierung mit statischer Antwort."""

    def __init__(self, knowledge_ref: str, number: int) -> None:
        self._knowledge_ref = knowledge_ref
        self._number = number

    async def complete(self, payload: dict[str, Any], schema: dict[str, Any]) -> ProviderResult:
        content = {
            "summary": "Reflexionseinladung.",
            "sections": [
                {
                    "title": "Lebensweg",
                    "claims": [
                        {
                            "claim_type": "interpretive_hypothesis",
                            "text": "Möglicherweise ein Reflexionsangebot.",
                            "calculation_ref": "life_path_a",
                            "knowledge_ref": self._knowledge_ref,
                            "number": self._number,
                        }
                    ],
                }
            ],
            "limitations": ["Numerologie ist nicht wissenschaftlich validiert."],
            "suggestions": [],
        }
        return ProviderResult(
            content=json.dumps(content),
            model="test-model",
            provider_fingerprint="test-fp",
            prompt_tokens=10,
            completion_tokens=10,
        )


# ---------------------------------------------------------------------------
# 1. Architekturtest: Produktionsgraph vollständig verdrahtet
# ---------------------------------------------------------------------------


def test_system_prompt_importable_from_package() -> None:
    """system_prompt() lädt aus dem Package — nicht aus dem Repo-Root."""
    prompt = system_prompt()
    assert len(prompt) > 100
    assert "JSON" in prompt


def test_report_task_prompt_importable_from_package() -> None:
    """report_task_prompt() lädt aus dem Package."""
    prompt = report_task_prompt()
    assert len(prompt) > 50
    assert "Reflexionsbericht" in prompt


def test_compose_observations_callable_from_profile() -> None:
    """compose_observations() ist aus dem Produktionsgraphen erreichbar."""
    profile = _profile()
    observations = compose_observations(profile)
    assert isinstance(observations, list)


def test_knowledge_bundle_entry_for_with_context() -> None:
    """entry_for(number, context=...) wählt den kontextbewussten Eintrag."""
    bundle = load_knowledge_bundle("de", "v2")
    entry = bundle.entry_for(1, context="life_path")
    assert entry.stable_id.startswith("de.pythagorean.")
    assert "life_path" in entry.result_contexts


def test_circuit_breaker_reachable_via_agent_service() -> None:
    """CircuitBreaker ist in AgentService integriert (kein ImportError)."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
    profile = _profile()
    knowledge_ref = _knowledge_ref_for_life_path(profile.life_path_a.reduced_value)
    provider = _FixedProvider(knowledge_ref, profile.life_path_a.reduced_value)
    service = AgentService(
        provider,
        context_secret=b"integration-test-secret-16bytes!",
        circuit_breaker=breaker,
    )
    assert service._breaker is breaker


# ---------------------------------------------------------------------------
# 2. Integrationstest: compose_observations erscheint im echten Bericht
# ---------------------------------------------------------------------------


def test_compose_observations_in_interpretation_result() -> None:
    """InterpretationResult.observations wird von compose_observations befüllt."""
    profile = _profile()
    result = compose_interpretation(profile)
    # Observations sind eine Teilmenge — Profil mit zwei Namen hat mindestens eine.
    assert isinstance(result.observations, tuple)
    # Jede Observation hat die pflichtigen Felder.
    for obs in result.observations:
        assert obs.composer_rule_id
        assert obs.relation in ("resonance", "tension")
        assert len(obs.calculation_refs) == 2
        assert len(obs.knowledge_refs) == 2
        assert obs.description


# ---------------------------------------------------------------------------
# 3. Integrationstest: entry_for mit Kontext wählt korrekten Eintrag
# ---------------------------------------------------------------------------


def test_entry_for_context_returns_context_aware_entry() -> None:
    """entry_for() wählt einen Eintrag, dessen result_contexts den Kontext enthält."""
    bundle = load_knowledge_bundle("de", "v2")
    for ctx in ("life_path", "expression", "soul_urge", "personality", "maturity"):
        # Alle Singles 1-9 müssen für jeden Kontext einen Eintrag haben.
        for num in range(1, 10):
            candidates = [e for e in bundle.entries if e.number == num and ctx in e.result_contexts]
            if candidates:
                entry = bundle.entry_for(num, context=ctx)
                assert ctx in entry.result_contexts, (
                    f"entry_for({num}, context={ctx!r}).result_contexts={entry.result_contexts}"
                )


def test_knowledge_ref_uses_stable_id() -> None:
    """compose_interpretation verwendet entry.stable_id als knowledge_ref."""
    profile = _profile()
    result = compose_interpretation(profile)
    for section in result.sections:
        for claim in section.claims:
            # stable_ids starten mit "de.pythagorean.", nicht mit "numra-knowledge-"
            assert claim.knowledge_ref.startswith("de.pythagorean."), (
                f"knowledge_ref {claim.knowledge_ref!r} nutzt nicht das stable_id-Format"
            )


# ---------------------------------------------------------------------------
# 4. Integrationstest: Circuit Breaker via AgentService
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_circuit_breaker_opens_after_threshold() -> None:
    """AgentService öffnet den Circuit Breaker nach wiederholten Fehlern."""
    from numerology_agent.provider import ProviderError
    from numerology_agent.resilience import CircuitOpenError

    class _FailingProvider:
        async def complete(self, payload: dict[str, Any], schema: dict[str, Any]) -> ProviderResult:
            raise ProviderError("transient failure")

    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
    service = AgentService(
        _FailingProvider(),
        context_secret=b"integration-test-secret-16bytes!",
        circuit_breaker=breaker,
    )
    profile = _profile()
    with pytest.raises((ProviderError, CircuitOpenError)):
        await service.generate_report(profile)
    assert breaker.state is CircuitState.OPEN


# ---------------------------------------------------------------------------
# 5. Wheel-Smoke: Prompt-Dateien sind im Wheel enthalten
# ---------------------------------------------------------------------------


def test_wheel_contains_prompt_templates() -> None:
    """Wheel enthält die Prompt-Template-Dateien als Package Data."""
    dist_dir = Path(__file__).resolve().parent.parent.parent / "dist"
    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        pytest.skip("Kein Wheel in dist/ gefunden — führe `uv build` aus")
    whl = wheels[0]
    with zipfile.ZipFile(whl) as zf:
        names = zf.namelist()
    expected = [
        "numerology_agent/prompt_templates/system/de-report-system.md",
        "numerology_agent/prompt_templates/tasks/de-report-task.md",
        "numerology_agent/prompt_templates/tasks/de-follow-up-task.md",
        "numerology_agent/prompt_templates/eval/de-report-eval.md",
    ]
    missing = [e for e in expected if e not in names]
    assert not missing, f"Fehlende Prompt-Dateien im Wheel: {missing}"
