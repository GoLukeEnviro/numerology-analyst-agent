"""Golden-case driver: load ``cases.yaml`` and assert the pinned expectations.

Golden cases are the regression backbone. If any pinned value drifts the
suite fails loudly - there is no "soft" tolerance. The driver computes the
Life Path via the real service path so the trace + hash are also exercised.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field
import pytest
from pytest import FixtureRequest
import yaml

from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.normalization import normalize_name
from numerology_engine.service import calculate_life_path

_CASES_PATH = Path(__file__).parent / "cases.yaml"


class _ExpectedMethod(BaseModel):
    """Pinned Life Path expectation for one reduction method (A or B)."""

    model_config = {"extra": "forbid"}

    value: int
    intermediate: int
    is_master: bool = False
    is_karmic_debt: bool = False
    components: dict[str, int] = Field(default_factory=dict)


class _Expected(BaseModel):
    """Pinned expectation block for a single golden case."""

    model_config = {"extra": "forbid"}

    life_path_a: _ExpectedMethod
    life_path_b: _ExpectedMethod
    a_equals_b: bool
    calculation_name: str | None = None
    future_warning: bool = False


class GoldenCase(BaseModel):
    """Type-safe view over one ``cases.yaml`` entry (no ``Any``)."""

    model_config = {"extra": "forbid"}

    id: str
    synthetic: bool = True
    core_name: str
    birth_date: str
    derivation: str = ""
    expected: _Expected


def _load_cases() -> list[GoldenCase]:
    raw = yaml.safe_load(_CASES_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    entries = raw.get("cases")
    assert isinstance(entries, list)
    return [GoldenCase.model_validate(entry) for entry in entries]


_CASES = _load_cases()


@pytest.fixture(params=_CASES, ids=[c.id for c in _CASES])
def golden_case(request: FixtureRequest) -> GoldenCase:
    return request.param  # type: ignore[no-any-return]


@pytest.mark.golden
def test_golden_life_path(golden_case: GoldenCase) -> None:
    person = PersonInput(
        core_name=golden_case.core_name,
        birth_date=date.fromisoformat(golden_case.birth_date),
    )
    policy = MethodPolicy()
    result = calculate_life_path(person, policy)
    expected = golden_case.expected

    # --- Life Path A ---
    exp_a = expected.life_path_a
    assert result.life_path_a.reduction.value == exp_a.value
    assert result.life_path_a.reduction.intermediate == exp_a.intermediate
    assert result.life_path_a.reduction.is_master == exp_a.is_master
    assert result.life_path_a.reduction.is_karmic_debt == exp_a.is_karmic_debt

    # --- Life Path B ---
    exp_b = expected.life_path_b
    assert result.life_path_b.reduction.value == exp_b.value
    assert result.life_path_b.reduction.intermediate == exp_b.intermediate
    assert result.life_path_b.reduction.is_master == exp_b.is_master
    assert result.life_path_b.reduction.is_karmic_debt == exp_b.is_karmic_debt
    assert dict(result.life_path_b.components) == dict(exp_b.components)

    # --- Consistency ---
    assert result.consistency.a_equals_b == expected.a_equals_b

    # --- Optional: pinned calculation_name (umlaut case) ---
    if expected.calculation_name is not None:
        calc_name, _ = normalize_name(
            person.core_name,
            umlaut_policy=policy.umlaut_policy,
            locale=policy.locale,
        )
        assert calc_name == expected.calculation_name

    # --- Optional: future warning expectation ---
    if expected.future_warning:
        assert any("exceeds" in w for w in result.trace.warnings)
    else:
        assert not any("exceeds" in w for w in result.trace.warnings)

    # --- Deterministic hash must be present and 64 hex chars (SHA-256). ---
    assert len(result.deterministic_hash) == 64
    assert all(c in "0123456789abcdef" for c in result.deterministic_hash)
