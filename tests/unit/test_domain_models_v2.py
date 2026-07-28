"""Tests für V2-Domainmodell-Invarianten und Trace-Hilfsfunktionen.

Deckt Validierungsfehler-Pfade in NumberModel, KarmicOccurrence,
ReductionOutcome, KarmicDebtInfo, LifePathResult und PersonInput ab.
Deckt außerdem den Tuple-Pfad in _canonicalize und build_trace/
deterministic_profile_hash_v4 ab.
"""

from __future__ import annotations

from datetime import date

from pydantic import ValidationError
import pytest

from numerology_domain.models import (
    KarmicDebtInfo,
    KarmicOccurrence,
    LifePathResult,
    MethodPolicy,
    NumberModel,
    PersonInput,
    ReductionOutcome,
)
from numerology_engine.profile_v2 import calculate_profile_v2
from numerology_engine.trace import (
    _canonicalize,
    build_trace,
    deterministic_profile_hash_v4,
)

_POLICY_V2 = MethodPolicy(version="v2")

# ---------------------------------------------------------------------------
# _canonicalize — Tuple-Pfad (trace.py line 59)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_canonicalize_tuple_converted_to_list() -> None:
    result = _canonicalize((1, 2, 3))
    assert result == [1, 2, 3]


@pytest.mark.unit
def test_canonicalize_nested_tuple() -> None:
    result = _canonicalize(({"b": 2, "a": 1},))
    assert result == [{"a": 1, "b": 2}]


@pytest.mark.unit
def test_canonicalize_frozenset_sorted() -> None:
    result = _canonicalize(frozenset({3, 1, 2}))
    assert result == [1, 2, 3]


@pytest.mark.unit
def test_canonicalize_set_sorted() -> None:
    result = _canonicalize({3, 1, 2})
    assert result == [1, 2, 3]


# ---------------------------------------------------------------------------
# build_trace — AuditTrace-Builder
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_build_trace_empty_defaults() -> None:
    trace = build_trace()
    assert trace.normalization_steps == ()
    assert trace.calculation_steps == ()
    assert trace.warnings == ()
    assert not trace.disambiguation_required


@pytest.mark.unit
def test_build_trace_with_warnings() -> None:
    trace = build_trace(warnings=("W1", "W2"), disambiguation_required=True)
    assert trace.warnings == ("W1", "W2")
    assert trace.disambiguation_required


# ---------------------------------------------------------------------------
# deterministic_profile_hash_v4
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_profile_hash_v4_is_hex_64() -> None:
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 28),
    )
    result = calculate_profile_v2(person, _POLICY_V2)
    h = deterministic_profile_hash_v4(result)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


@pytest.mark.unit
def test_profile_hash_v4_deterministic() -> None:
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 28),
    )
    r1 = calculate_profile_v2(person, _POLICY_V2)
    r2 = calculate_profile_v2(person, _POLICY_V2)
    assert deterministic_profile_hash_v4(r1) == deterministic_profile_hash_v4(r2)


@pytest.mark.unit
def test_profile_hash_v4_changes_with_input() -> None:
    p1 = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 28),
    )
    p2 = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 29),
    )
    h1 = deterministic_profile_hash_v4(calculate_profile_v2(p1, _POLICY_V2))
    h2 = deterministic_profile_hash_v4(calculate_profile_v2(p2, _POLICY_V2))
    assert h1 != h2


# ---------------------------------------------------------------------------
# NumberModel — Invarianten-Verletzungen (models.py lines 587-602)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_number_model_is_master_without_held_value_raises() -> None:
    with pytest.raises(ValidationError, match="held_master_value"):
        NumberModel(
            raw_total=22,
            reduction_chain=(22, 4),
            root_value=4,
            display_notation="22/4",
            is_master=True,
            held_master_value=None,
        )


@pytest.mark.unit
def test_number_model_not_master_with_held_value_raises() -> None:
    with pytest.raises(ValidationError, match="held_master_value"):
        NumberModel(
            raw_total=22,
            reduction_chain=(22, 4),
            root_value=4,
            display_notation="22/4",
            is_master=False,
            held_master_value=22,
        )


@pytest.mark.unit
def test_number_model_held_master_not_in_classic_set_raises() -> None:
    with pytest.raises(ValidationError, match="held_master_value"):
        NumberModel(
            raw_total=44,
            reduction_chain=(44, 8),
            root_value=8,
            display_notation="44/8",
            is_master=True,
            held_master_value=44,
        )


@pytest.mark.unit
def test_number_model_empty_reduction_chain_raises() -> None:
    with pytest.raises(ValidationError, match="reduction_chain must not be empty"):
        NumberModel(
            raw_total=4,
            reduction_chain=(),
            root_value=4,
            display_notation="4",
        )


@pytest.mark.unit
def test_number_model_chain_last_ne_root_value_raises() -> None:
    with pytest.raises(ValidationError, match="must equal root_value"):
        NumberModel(
            raw_total=22,
            reduction_chain=(22, 5),
            root_value=4,
            display_notation="22/4",
        )


@pytest.mark.unit
def test_number_model_chain_first_ne_raw_total_raises() -> None:
    with pytest.raises(ValidationError, match="must equal raw_total"):
        NumberModel(
            raw_total=22,
            reduction_chain=(11, 2),
            root_value=2,
            display_notation="22/2",
        )


# ---------------------------------------------------------------------------
# KarmicOccurrence — Validierungsfehler (models.py)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_karmic_occurrence_invalid_value_raises() -> None:
    with pytest.raises(ValidationError, match="must be one of"):
        KarmicOccurrence(value=15, origin_type="direct_raw")


@pytest.mark.unit
def test_karmic_occurrence_invalid_origin_type_raises() -> None:
    with pytest.raises(ValidationError, match="origin_type must be one of"):
        KarmicOccurrence(value=13, origin_type="unknown_origin")


@pytest.mark.unit
def test_karmic_occurrence_valid() -> None:
    occ = KarmicOccurrence(value=13, origin_type="component_total")
    assert occ.value == 13
    assert occ.origin_type == "component_total"


# ---------------------------------------------------------------------------
# ReductionOutcome — Validierungsfehler (models.py lines 238, 240)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_reduction_outcome_is_master_not_in_set_raises() -> None:
    with pytest.raises(ValidationError, match="is_master=True but value"):
        ReductionOutcome(value=5, intermediate=5, is_master=True)


@pytest.mark.unit
def test_reduction_outcome_non_master_out_of_range_raises() -> None:
    with pytest.raises(ValidationError, match="out of range"):
        ReductionOutcome(value=0, intermediate=0, is_master=False)


@pytest.mark.unit
def test_reduction_outcome_non_master_out_of_range_high_raises() -> None:
    with pytest.raises(ValidationError, match="out of range"):
        ReductionOutcome(value=10, intermediate=10, is_master=False)


# ---------------------------------------------------------------------------
# KarmicDebtInfo — Validierungsfehler (models.py lines 263, 267)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_karmic_debt_info_invalid_number_raises() -> None:
    with pytest.raises(ValidationError, match="karmic number must be one of"):
        KarmicDebtInfo(number=15, origin="total_sum")


@pytest.mark.unit
def test_karmic_debt_info_empty_origin_raises() -> None:
    with pytest.raises(ValidationError, match="origin must be non-empty"):
        KarmicDebtInfo(number=13, origin="   ")


# ---------------------------------------------------------------------------
# LifePathResult — Validierungsfehler (models.py line 310)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_life_path_result_inconsistent_reduced_value_raises() -> None:
    reduction = ReductionOutcome(value=4, intermediate=40)
    with pytest.raises(ValidationError, match="reduced_value.*must equal reduction.value"):
        LifePathResult(
            method="sum_all_digits",
            reduction=reduction,
            raw_total=40,
            reduced_value=5,  # inkonsistent mit reduction.value=4
            compound_notation="40/4",
        )


# ---------------------------------------------------------------------------
# PersonInput — Validierungsfehler (models.py lines 137, 174)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_person_input_birth_date_after_as_of_date_raises() -> None:
    with pytest.raises(ValidationError, match="PERSON_BIRTH_DATE_IN_FUTURE"):
        PersonInput(
            core_name="Test",
            birth_date=date(2030, 1, 1),
            as_of_date=date(2026, 7, 28),
        )


@pytest.mark.unit
def test_person_input_active_name_equal_core_name_no_crash() -> None:
    """PersonInput mit active_name == core_name darf nicht crashen.

    Der Validator-Pfad _active_differs_from_core_if_set wird durchlaufen.
    """
    p = PersonInput(
        core_name="Max",
        birth_date=date(1990, 1, 1),
        as_of_date=date(2026, 7, 28),
        active_name="Max",
    )
    assert p.core_name == "Max"


@pytest.mark.unit
def test_person_input_active_name_different_from_core_preserved() -> None:
    """Wenn active_name != core_name, bleibt active_name erhalten."""
    p = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1990, 1, 1),
        as_of_date=date(2026, 7, 28),
        active_name="Max",
    )
    assert p.active_name == "Max"
