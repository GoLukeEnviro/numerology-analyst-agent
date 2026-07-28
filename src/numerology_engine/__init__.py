"""Deterministic pythagorean calculation core.

Public surface for the Walking Skeleton (0.1.0). The engine is pure: no
network, no LLM, no global mutable state.
"""

from __future__ import annotations

from numerology_engine.alphabet import PYTHAGOREAN_V1, VOWELS, letter_value
from numerology_engine.cycles import calculate_cycles
from numerology_engine.dates import (
    consistency_check,
    future_warning,
    life_path_a,
    life_path_b,
)
from numerology_engine.normalization import normalize_name
from numerology_engine.profile import calculate_profile
from numerology_engine.profile_v2 import calculate_profile_v2
from numerology_engine.reduction import (
    digit_sum,
    recognize_karmic,
    recognize_master,
    reduce_to_single_digit,
)
from numerology_engine.service import calculate_life_path
from numerology_engine.trace import _canonical_json, build_trace, deterministic_hash

__all__ = [
    "PYTHAGOREAN_V1",
    "VOWELS",
    "_canonical_json",
    "build_trace",
    "calculate_cycles",
    "calculate_life_path",
    "calculate_profile",
    "calculate_profile_v2",
    "consistency_check",
    "deterministic_hash",
    "digit_sum",
    "future_warning",
    "letter_value",
    "life_path_a",
    "life_path_b",
    "normalize_name",
    "recognize_karmic",
    "recognize_master",
    "reduce_to_single_digit",
]
