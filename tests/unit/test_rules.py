"""Contracts for the interpretation composer rules."""

from __future__ import annotations

import pytest

from numerology_domain.models import MethodPolicy, PersonInput, ProfileCalculationResult
from numerology_engine.profile import calculate_profile
from numerology_interpretation.rules import compose_observations


def _profile() -> ProfileCalculationResult:
    return calculate_profile(
        PersonInput(
            core_name="Max Mustermann",
            active_name="Max Power",
            birth_date="1985-07-25",
            as_of_date="2026-07-26",
        ),
        MethodPolicy(),
    )


@pytest.mark.unit
def test_compose_observations_returns_list() -> None:
    profile = _profile()
    observations = compose_observations(profile)
    assert isinstance(observations, list)
    assert len(observations) > 0


@pytest.mark.unit
def test_all_observations_have_valid_relation() -> None:
    profile = _profile()
    observations = compose_observations(profile)
    for obs in observations:
        assert obs.relation in {"resonance", "tension"}
        assert obs.rule_id in {"reinforcement", "tension", "core_vs_active", "maturity_alignment"}


@pytest.mark.unit
def test_observations_are_non_judgmental() -> None:
    profile = _profile()
    observations = compose_observations(profile)
    forbidden = {"immer", "niemals", "garantiert", "zweifellos", "du bist", "du wirst"}
    for obs in observations:
        text_lower = obs.description.lower()
        for word in forbidden:
            assert word not in text_lower, f"observation contains '{word}': {obs.description}"


@pytest.mark.unit
def test_core_vs_active_rule_detects_difference() -> None:
    profile = _profile()
    observations = compose_observations(profile)
    core_active = [o for o in observations if o.rule_id == "core_vs_active"]
    assert len(core_active) >= 1
