"""Unit tests for Life Path A/B date calculations (Master Contract §3.2)."""

from __future__ import annotations

from datetime import date

from numerology_engine.dates import (
    consistency_check,
    future_warning,
    life_path_a,
    life_path_b,
)


class TestLifePathA:
    def test_reference_date_1985_07_25(self) -> None:
        # 1+9+8+5+0+7+2+5 = 37 -> 10 -> 1
        res = life_path_a(date(1985, 7, 25))
        assert res.method == "sum_all_digits"
        assert res.reduction.value == 1
        assert res.reduction.intermediate == 37
        assert not res.reduction.is_master
        # Korrektur 1: raw_total + compound_notation + karmic on raw_total.
        assert res.raw_total == 37
        assert res.reduced_value == 1
        assert res.compound_notation == "37/10/1"
        # 37 is not a karmic debt number => None.
        assert res.karmic_debt is None

    def test_leading_zeros_preserved(self) -> None:
        # 1985-07-05 vs 1985-7-5 must yield identical digit sequences.
        a = life_path_a(date(1985, 7, 5))
        # digits 1,9,8,5,0,7,0,5 -> 35 -> 8
        assert a.reduction.intermediate == 35
        assert a.reduction.value == 8
        assert a.raw_total == 35
        assert a.compound_notation == "35/8"

    def test_steps_audited(self) -> None:
        res = life_path_a(date(1985, 7, 25))
        labels = [s.label for s in res.steps]
        assert labels[0] == "sum_all_digits"
        assert "digit_sum" in labels

    def test_karmic_debt_on_raw_total(self) -> None:
        # 2000-12-29: digits sum to 16 (karmic) -> 7. Marker on raw_total.
        res = life_path_a(date(2000, 12, 29))
        assert res.raw_total == 16
        assert res.compound_notation == "16/7"
        assert res.karmic_debt is not None
        assert res.karmic_debt.number == 16
        assert res.karmic_debt.origin == "total_sum"


class TestLifePathB:
    def test_reference_date_1985_07_25(self) -> None:
        # month 7, day 7, year 23->5 ; 7+7+5 = 19 -> 10 -> 1
        res = life_path_b(date(1985, 7, 25))
        assert res.method == "component_then_sum"
        assert res.components == {"month": 7, "day": 7, "year": 5}
        assert res.reduction.value == 1
        assert res.reduction.intermediate == 19
        assert not res.reduction.is_master
        # Korrektur 1: raw_total = component sum (19), karmic on it.
        assert res.raw_total == 19
        assert res.reduced_value == 1
        assert res.compound_notation == "19/10/1"
        assert res.karmic_debt is not None
        assert res.karmic_debt.number == 19
        assert res.karmic_debt.origin == "component_sum"

    def test_day_master_number_held(self) -> None:
        # day 29 -> 11 (master, held); 2000-12-29: month 3, day 11, year 2 -> 16 -> 7
        res = life_path_b(date(2000, 12, 29))
        assert res.components["day"] == 11

    def test_year_master_number_held(self) -> None:
        # year 1993 -> 1+9+9+3 = 22 (master); 1993-01-01: month 1, day 1, year 22 -> 24 -> 6
        res = life_path_b(date(1993, 1, 1))
        assert res.components["year"] == 22

    def test_karmic_debt_none_when_component_sum_not_karmic(self) -> None:
        # 1993-01-01: 1+1+22 = 24 (not karmic) => None.
        res = life_path_b(date(1993, 1, 1))
        assert res.raw_total == 24
        assert res.karmic_debt is None


class TestConsistency:
    def test_equal_paths_no_warning(self) -> None:
        a = life_path_a(date(1985, 7, 25))
        b = life_path_b(date(1985, 7, 25))
        status = consistency_check(a, b)
        assert status.a_equals_b
        assert status.warning == ""

    def test_diverging_paths_warned(self) -> None:
        # 1980-09-04: A reduces to 4, B holds 22 (master) -> A=4, B=22
        a = life_path_a(date(1980, 9, 4))
        b = life_path_b(date(1980, 9, 4))
        status = consistency_check(a, b)
        assert not status.a_equals_b
        assert status.life_path_a == 4
        assert status.life_path_b == 22
        assert "differs" in status.warning


class TestFutureWarning:
    def test_normal_date_no_warning(self) -> None:
        assert future_warning(date(1985, 7, 25)) == ""

    def test_far_future_date_warned(self) -> None:
        assert future_warning(date(2210, 6, 15)) != ""

    def test_boundary_year_no_warning(self) -> None:
        assert future_warning(date(2200, 1, 1)) == ""
