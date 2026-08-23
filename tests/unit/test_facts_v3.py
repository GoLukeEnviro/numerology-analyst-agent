"""V3 fact package tests — extraction completeness and provider minimisation.

Regression coverage for the post-PR56 finding B-6: ``build_analysis_fact_package_v3``
crashed on real V4 profiles because it accessed ``profile.maturity`` and
``profile.pinnacles``/``profile.challenges`` which live under
``core_name.maturity`` and ``cycles.*`` respectively.
"""

from __future__ import annotations

import json

from numerology_agent.facts_v3 import (
    build_analysis_fact_package_v3,
    derive_provider_fact_package_v3,
)
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
    ProfileCalculationResultV4,
)
from numerology_engine.profile_v2 import calculate_profile_v2

_EXPECTED_REFS = (
    "life_path_primary",
    "life_path_secondary",
    "birthday",
    "attitude",
    "expression",
    "soul_urge",
    "personality",
    "maturity",
    "personal_year",
    "personal_month",
    "personal_day",
    "pinnacle_1",
    "pinnacle_2",
    "pinnacle_3",
    "pinnacle_4",
    "challenge_1",
    "challenge_2",
    "challenge_3",
    "challenge_4",
)


def _profile() -> ProfileCalculationResultV4:
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date="1986-07-18",
        as_of_date="2026-07-28",
    )
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION, umlaut_policy="de-expanded-v1")
    return calculate_profile_v2(person, policy)


def test_fact_package_extracts_all_expected_entries() -> None:
    package = build_analysis_fact_package_v3(_profile())

    refs = [entry.calculation_ref for entry in package.entries]
    assert refs == list(_EXPECTED_REFS)
    assert package.calculation_hash == _profile().deterministic_hash
    assert package.method_version == "v2"


def test_fact_package_keeps_primary_secondary_life_paths_separate() -> None:
    package = build_analysis_fact_package_v3(_profile())
    by_ref = {entry.calculation_ref: entry for entry in package.entries}

    primary = by_ref["life_path_primary"]
    secondary = by_ref["life_path_secondary"]
    assert primary.role == "primary"
    assert secondary.role == "secondary"
    assert primary.display_notation == "40/4"
    assert secondary.display_notation == "22/4"
    assert secondary.held_master_value == 22
    assert secondary.is_master is True


def test_fact_package_marks_44_as_non_master() -> None:
    package = build_analysis_fact_package_v3(_profile())
    by_ref = {entry.calculation_ref: entry for entry in package.entries}

    personality = by_ref["personality"]
    assert personality.display_notation == "44/8"
    assert personality.is_master is False
    assert personality.held_master_value is None


def test_provider_package_contains_no_personal_data() -> None:
    package = build_analysis_fact_package_v3(_profile())
    provider = derive_provider_fact_package_v3(package)

    blob = json.dumps(provider.model_dump(mode="json"))
    assert "Lukas" not in blob
    assert "Springer" not in blob
    assert "1986" not in blob
    assert "07-18" not in blob
    # No letter chains, no raw totals, no reduction chains, no trace refs.
    assert "reduction_chain" not in blob
    assert "raw_total" not in blob
    assert "trace_ref" not in blob
    assert "components" not in blob


def test_provider_package_preserves_calculation_references() -> None:
    package = build_analysis_fact_package_v3(_profile())
    provider = derive_provider_fact_package_v3(package)

    refs = {entry["ref"] for entry in provider.entries}
    assert refs == set(_EXPECTED_REFS)
    assert provider.calculation_hash == package.calculation_hash
    assert provider.method_version == "v2"


def test_provider_package_entries_are_deterministic() -> None:
    package = build_analysis_fact_package_v3(_profile())
    first = derive_provider_fact_package_v3(package)
    second = derive_provider_fact_package_v3(package)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
