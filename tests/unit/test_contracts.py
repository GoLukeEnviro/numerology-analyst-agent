"""Unit tests for the JSON serialization adapter (numerology_api.contracts).

These guard the CLI determinism contract: identical input + policy must
yield byte-identical, key-sorted JSON. This is the single most important
property of the Walking Skeleton output (Master Contract §2.4).
"""

from __future__ import annotations

from datetime import date
from json import loads

import pytest

from numerology_api.contracts import dump_result_as_json, result_to_payload
from numerology_domain.models import CalculationResult, MethodPolicy, PersonInput
from numerology_engine.service import calculate_life_path


@pytest.fixture
def sample_result() -> CalculationResult:
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    return calculate_life_path(person, MethodPolicy())


class TestPayload:
    def test_payload_has_required_top_level_keys(self, sample_result: CalculationResult) -> None:
        payload = result_to_payload(sample_result)
        for key in (
            "claim_type",
            "name",
            "deterministic_hash",
            "input",
            "method",
            "results",
            "consistency",
            "audit_trace",
        ):
            assert key in payload

    def test_payload_carries_life_path_a_and_b(self, sample_result: CalculationResult) -> None:
        payload = result_to_payload(sample_result)
        assert "life_path_a" in payload["results"]
        assert "life_path_b" in payload["results"]
        assert payload["results"]["life_path_a"]["value"] == 1
        assert payload["results"]["life_path_b"]["components"] == {"month": 7, "day": 7, "year": 5}
        # Korrektur 1: karmic_debt as object + compound_notation; as_of_date in input.
        assert payload["results"]["life_path_a"]["compound_notation"] == "37/10/1"
        assert payload["results"]["life_path_b"]["compound_notation"] == "19/10/1"
        assert payload["results"]["life_path_a"]["karmic_debt"] is None
        assert payload["results"]["life_path_b"]["karmic_debt"] == {
            "number": 19,
            "origin": "component_sum",
        }
        assert payload["input"]["as_of_date"] == "2026-07-26"


class TestJsonDeterminism:
    def test_dump_is_valid_json(self, sample_result: CalculationResult) -> None:
        text = dump_result_as_json(sample_result)
        parsed = loads(text)
        assert parsed["results"]["life_path_a"]["value"] == 1

    def test_keys_are_sorted(self, sample_result: CalculationResult) -> None:
        text = dump_result_as_json(sample_result)
        # Sorted keys => 'audit_trace' appears before 'claim_type' before 'consistency'.
        assert text.index('"audit_trace"') < text.index('"claim_type"')
        assert text.index('"claim_type"') < text.index('"consistency"')

    def test_byte_stability_identical_input(self) -> None:
        """Two computations from identical input must produce byte-identical JSON."""
        person = PersonInput(
            core_name="Müller-Lüdenscheidt",
            birth_date=date(1993, 1, 1),
            as_of_date=date(2026, 7, 26),
        )
        a = dump_result_as_json(calculate_life_path(person, MethodPolicy()))
        b = dump_result_as_json(calculate_life_path(person, MethodPolicy()))
        assert a == b

    def test_hash_present_and_stable(self) -> None:
        person = PersonInput(
            core_name="Test",
            birth_date=date(2000, 12, 29),
            as_of_date=date(2026, 7, 26),
        )
        h1 = calculate_life_path(person, MethodPolicy()).deterministic_hash
        h2 = calculate_life_path(person, MethodPolicy()).deterministic_hash
        assert h1 == h2 and len(h1) == 64
