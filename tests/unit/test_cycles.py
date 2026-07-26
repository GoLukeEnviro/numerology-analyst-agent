"""Deterministic personal-cycle, Pinnacle and Challenge contract tests."""

from __future__ import annotations

from datetime import date

import pytest

from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.cycles import calculate_cycles
from numerology_engine.profile import calculate_profile


@pytest.fixture
def person() -> PersonInput:
    return PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )


@pytest.mark.unit
def test_reference_personal_cycles(person: PersonInput) -> None:
    cycles = calculate_cycles(person, MethodPolicy())

    assert cycles.as_of_date == date(2026, 7, 26)
    assert cycles.personal_year.raw_total == 42
    assert cycles.personal_year.reduced_value == 6
    assert cycles.personal_month.raw_total == 13
    assert cycles.personal_month.reduced_value == 4
    assert cycles.personal_day.raw_total == 30
    assert cycles.personal_day.reduced_value == 3


@pytest.mark.unit
def test_reference_pinnacles_and_challenges(person: PersonInput) -> None:
    cycles = calculate_cycles(person, MethodPolicy())

    assert [phase.number.reduced_value for phase in cycles.pinnacles] == [5, 3, 8, 3]
    assert [phase.number.reduced_value for phase in cycles.challenges] == [0, 2, 2, 2]
    assert [(phase.start_age, phase.end_age) for phase in cycles.pinnacles] == [
        (0, 35),
        (36, 44),
        (45, 53),
        (54, None),
    ]


@pytest.mark.unit
def test_profile_contains_cycles_and_as_of_date_changes_hash(person: PersonInput) -> None:
    first = calculate_profile(person, MethodPolicy())
    second = calculate_profile(
        person.model_copy(update={"as_of_date": date(2026, 7, 27)}),
        MethodPolicy(),
    )

    assert first.cycles.personal_day.reduced_value == 3
    assert second.cycles.personal_day.reduced_value == 4
    assert first.deterministic_hash != second.deterministic_hash
