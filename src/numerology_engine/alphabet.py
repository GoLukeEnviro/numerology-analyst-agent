"""Pythagorean alphabet mapping V1 (Master Contract §3.2, calculation-engineer
contract §4).

Only the canonical pythagorean letter→digit table is defined here. Chaldäische
or other system values must never leak into this module - that would be a
method-version contamination.
"""

from __future__ import annotations

from typing import Final

# Pythagoreisches Alphabet (V1). Each base letter A-Z maps to 1..9 in the
# classic 3-row layout. Verified against the Master Implementation Contract
# §3 spec (1-9, 1-9, 1-8 pattern) and the V1 minimal scope.
PYTHAGOREAN_V1: Final[dict[str, int]] = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "I": 9,
    "J": 1,
    "K": 2,
    "L": 3,
    "M": 4,
    "N": 5,
    "O": 6,
    "P": 7,
    "Q": 8,
    "R": 9,
    "S": 1,
    "T": 2,
    "U": 3,
    "V": 4,
    "W": 5,
    "X": 6,
    "Y": 7,
    "Z": 8,
}

# Vowels per the pythagorean convention. Y is intentionally NOT in this set:
# its classification is policy-driven (ADR 0001). The Walking Skeleton does
# not yet compute vowel/consonant sums (those are name-based numbers, Phase
# 4+), but the set is defined here so the engine has a single source of truth.
VOWELS: Final[frozenset[str]] = frozenset({"A", "E", "I", "O", "U"})


def letter_value(letter: str) -> int:
    """Return the pythagorean V1 value of a single ASCII letter.

    Raises :class:`KeyError` for non-letters. Callers must normalize first
    (see :mod:`numerology_engine.normalization`) so that only A-Z reach
    this function.
    """
    if len(letter) != 1 or not letter.isascii():
        raise KeyError(f"letter_value expects a single ASCII letter, got {letter!r}")
    return PYTHAGOREAN_V1[letter.upper()]
