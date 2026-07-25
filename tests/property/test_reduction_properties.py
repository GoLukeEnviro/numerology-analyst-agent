"""Property-based tests for the reduction core (hypothesis).

These encode the *invariants* every valid reduction must satisfy, not
specific values. They are the long tail of the Phase-4 determinism gate.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from numerology_domain.models import MASTER_NUMBERS
from numerology_engine.reduction import digit_sum, reduce_to_single_digit


@given(st.integers(min_value=1, max_value=10_000_000))
def test_reduction_returns_single_digit_or_master(n: int) -> None:
    outcome = reduce_to_single_digit(n)
    assert outcome.is_master or 1 <= outcome.value <= 9


@given(st.integers(min_value=1, max_value=10_000_000))
def test_master_value_is_actually_a_master_number(n: int) -> None:
    outcome = reduce_to_single_digit(n)
    if outcome.is_master:
        assert outcome.value in MASTER_NUMBERS


@given(st.integers(min_value=1, max_value=10_000_000))
def test_intermediate_is_the_input(n: int) -> None:
    outcome = reduce_to_single_digit(n)
    assert outcome.intermediate == n


@given(st.integers(min_value=0, max_value=10_000_000))
def test_digit_sum_non_negative_and_bounded(n: int) -> None:
    s = digit_sum(n)
    assert s >= 0
    # The digit sum of an n-digit number is at most 9*n.
    upper = 9 * max(1, len(str(n)))
    assert s <= upper


@given(st.integers(min_value=1, max_value=10_000_000))
def test_reduction_is_idempotent(n: int) -> None:
    """Reducing an already-reduced value must be a no-op on the value."""
    once = reduce_to_single_digit(n)
    twice = reduce_to_single_digit(once.value)
    assert once.value == twice.value


@pytest.mark.property
@given(st.integers(min_value=1, max_value=10_000_000))
@settings(max_examples=500)
def test_determinism_same_input_same_output(n: int) -> None:
    a = reduce_to_single_digit(n)
    b = reduce_to_single_digit(n)
    assert a.value == b.value
    assert a.is_master == b.is_master
    # Korrektur 1: karmic detection moved off the primitive; only master flag + value matter.
