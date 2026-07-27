"""Pinned complete-profile values for the versioned 0.1.4 method contract."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel
import pytest
import yaml

from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile

_CASES_PATH = Path(__file__).with_name("profile_cases.yaml")


class _Expected(BaseModel):
    birthday: int
    attitude: int
    expression: int
    soul_urge: int
    personality: int
    maturity: int
    active_expression: int | None
    personal_year: int
    personal_month: int
    personal_day: int
    pinnacles: list[int]
    challenges: list[int]


class _Case(BaseModel):
    id: str
    core_name: str
    active_name: str | None = None
    birth_date: date
    as_of_date: date
    expected: _Expected


def _cases() -> list[_Case]:
    raw = yaml.safe_load(_CASES_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    cases = raw["cases"]
    assert isinstance(cases, list)
    return [_Case.model_validate(case) for case in cases]


@pytest.mark.golden
@pytest.mark.parametrize("case", _cases(), ids=lambda case: case.id)
def test_complete_profile_golden(case: _Case) -> None:
    result = calculate_profile(
        PersonInput(
            core_name=case.core_name,
            active_name=case.active_name,
            birth_date=case.birth_date,
            as_of_date=case.as_of_date,
        ),
        MethodPolicy(),
    )

    assert result.birthday.reduced_value == case.expected.birthday
    assert result.attitude.reduced_value == case.expected.attitude
    assert result.core_name.expression.reduced_value == case.expected.expression
    assert result.core_name.soul_urge.reduced_value == case.expected.soul_urge
    assert result.core_name.personality.reduced_value == case.expected.personality
    assert result.maturity.reduced_value == case.expected.maturity
    active_expression = (
        None if result.active_name is None else result.active_name.expression.reduced_value
    )
    assert active_expression == case.expected.active_expression
    assert result.cycles.personal_year.reduced_value == case.expected.personal_year
    assert result.cycles.personal_month.reduced_value == case.expected.personal_month
    assert result.cycles.personal_day.reduced_value == case.expected.personal_day
    assert [phase.number.reduced_value for phase in result.cycles.pinnacles] == (
        case.expected.pinnacles
    )
    assert [phase.number.reduced_value for phase in result.cycles.challenges] == (
        case.expected.challenges
    )
