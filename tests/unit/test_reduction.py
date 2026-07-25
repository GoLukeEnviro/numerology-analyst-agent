"""Unit tests for numeric reduction (Master Contract §3.2)."""

from __future__ import annotations

import pytest

from numerology_engine.reduction import (
    digit_sum,
    recognize_karmic,
    recognize_master,
    reduce_to_single_digit,
)


class TestDigitSum:
    @pytest.mark.parametrize("n,expected", [(0, 0), (7, 7), (37, 10), (1985, 23), (99, 18)])
    def test_known_values(self, n: int, expected: int) -> None:
        assert digit_sum(n) == expected

    def test_negative_rejected(self) -> None:
        with pytest.raises(ValueError):
            digit_sum(-1)


class TestReduceToSingleDigit:
    @pytest.mark.parametrize("n,expected", [(1, 1), (37, 1), (10, 1), (29, 11), (1985, 5)])
    def test_basic_reduction(self, n: int, expected: int) -> None:
        outcome = reduce_to_single_digit(n)
        assert outcome.value == expected
        assert not outcome.is_master or outcome.value in (11, 22, 33)
        # Non-master results land in 1..9.
        if not outcome.is_master:
            assert 1 <= outcome.value <= 9

    @pytest.mark.parametrize("n", [11, 22, 33])
    def test_master_numbers_held(self, n: int) -> None:
        outcome = reduce_to_single_digit(n)
        assert outcome.value == n
        assert outcome.is_master

    def test_master_emerges_from_reduction(self) -> None:
        # 29 -> 11, which is a master number and must be held.
        outcome = reduce_to_single_digit(29)
        assert outcome.value == 11
        assert outcome.is_master

    @pytest.mark.parametrize("n", [13, 14, 16, 19])
    def test_karmic_debts_flagged_not_master(self, n: int) -> None:
        outcome = reduce_to_single_digit(n)
        assert outcome.is_karmic_debt
        assert not outcome.is_master
        # Karmic debts reduce to 4, 5, 7, 1 respectively.
        assert outcome.value in {4, 5, 7, 1}

    def test_outcome_records_intermediate(self) -> None:
        outcome = reduce_to_single_digit(1985)
        assert outcome.intermediate == 1985


class TestRecognizers:
    @pytest.mark.parametrize(
        "n,expected", [(11, True), (22, True), (33, True), (44, False), (5, False)]
    )
    def test_recognize_master(self, n: int, expected: bool) -> None:
        assert recognize_master(n) is expected

    @pytest.mark.parametrize(
        "n,expected", [(13, True), (14, True), (16, True), (19, True), (12, False)]
    )
    def test_recognize_karmic(self, n: int, expected: bool) -> None:
        assert recognize_karmic(n) is expected
