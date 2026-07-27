"""Property tests for the complete deterministic name profile."""

from __future__ import annotations

from datetime import date

from hypothesis import given
from hypothesis import strategies as st
import pytest

from numerology_domain.enums import YMode
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile

_NAMES = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=40)
_VALID_REDUCTIONS = frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33})


@pytest.mark.property
@given(name=_NAMES)
def test_expression_partition_and_reduction_range(name: str) -> None:
    result = calculate_profile(
        PersonInput(
            core_name=name,
            birth_date=date(1990, 1, 1),
            as_of_date=date(2026, 7, 26),
        ),
        MethodPolicy(y_mode=YMode.ALWAYS_CONSONANT),
    )
    numbers = result.core_name

    assert numbers.expression.raw_total == (
        numbers.soul_urge.raw_total + numbers.personality.raw_total
    )
    assert numbers.expression.reduced_value in _VALID_REDUCTIONS
    assert numbers.soul_urge.reduced_value in _VALID_REDUCTIONS
    assert numbers.personality.reduced_value in _VALID_REDUCTIONS


@pytest.mark.property
@given(name=_NAMES)
def test_same_profile_input_is_byte_stable(name: str) -> None:
    person = PersonInput(
        core_name=name,
        birth_date=date(1990, 1, 1),
        as_of_date=date(2026, 7, 26),
    )
    policy = MethodPolicy(y_mode=YMode.ALWAYS_VOWEL)

    assert calculate_profile(person, policy).deterministic_hash == (
        calculate_profile(person, policy).deterministic_hash
    )


@pytest.mark.property
@given(as_of=st.dates(min_value=date(2020, 1, 1), max_value=date(2035, 12, 31)))
def test_cycle_shape_and_ranges_are_stable(as_of: date) -> None:
    result = calculate_profile(
        PersonInput(
            core_name="Cycle Test",
            birth_date=date(1990, 1, 1),
            as_of_date=as_of,
        ),
        MethodPolicy(),
    )

    assert len(result.cycles.pinnacles) == 4
    assert len(result.cycles.challenges) == 4
    assert result.cycles.pinnacles[-1].end_age is None
    assert result.cycles.personal_year.reduced_value in _VALID_REDUCTIONS
    assert result.cycles.personal_month.reduced_value in _VALID_REDUCTIONS
    assert result.cycles.personal_day.reduced_value in _VALID_REDUCTIONS
