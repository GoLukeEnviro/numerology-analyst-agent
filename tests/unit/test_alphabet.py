"""Unit tests for the pythagorean alphabet mapping (V1)."""

from __future__ import annotations

import pytest

from numerology_engine.alphabet import PYTHAGOREAN_V1, VOWELS, letter_value


class TestAlphabetTable:
    def test_table_has_26_letters(self) -> None:
        assert len(PYTHAGOREAN_V1) == 26
        assert set(PYTHAGOREAN_V1) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    @pytest.mark.parametrize(
        "letter,expected",
        [("A", 1), ("I", 9), ("J", 1), ("R", 9), ("S", 1), ("Z", 8), ("Y", 7)],
    )
    def test_known_values(self, letter: str, expected: int) -> None:
        assert PYTHAGOREAN_V1[letter] == expected

    def test_values_in_range_1_to_9(self) -> None:
        for v in PYTHAGOREAN_V1.values():
            assert 1 <= v <= 9


class TestLetterValue:
    @pytest.mark.parametrize("letter,expected", [("a", 1), ("A", 1), ("z", 8), ("Z", 8)])
    def test_case_insensitive(self, letter: str, expected: int) -> None:
        assert letter_value(letter) == expected

    def test_non_ascii_rejected(self) -> None:
        with pytest.raises(KeyError):
            letter_value("Ä")

    def test_multi_char_rejected(self) -> None:
        with pytest.raises(KeyError):
            letter_value("AB")


class TestVowels:
    def test_y_excluded(self) -> None:
        # Y classification is policy-driven (ADR 0001); it must NOT be a default vowel.
        assert "Y" not in VOWELS
        assert frozenset({"A", "E", "I", "O", "U"}) == VOWELS
