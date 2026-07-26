"""Complete, deterministic pythagorean profile calculations.

This module contains no interpretation, persistence, network or clock access.
Every result is derived exclusively from ``PersonInput`` and ``MethodPolicy``.
"""

from __future__ import annotations

import re

from numerology_domain.enums import NameBasis, YMode
from numerology_domain.exceptions import NormalizationError, PolicyError
from numerology_domain.models import (
    AuditTrace,
    MethodPolicy,
    NameNumberSet,
    NameNumberVariant,
    NameSegmentResult,
    NormalizationStep,
    PersonInput,
    ProfileCalculationResult,
)
from numerology_engine.alphabet import VOWELS, letter_value
from numerology_engine.cycles import calculate_cycles
from numerology_engine.dates import consistency_check, life_path_a, life_path_b
from numerology_engine.normalization import normalize_name
from numerology_engine.numbers import create_number
from numerology_engine.reduction import reduce_to_single_digit, reduction_chain
from numerology_engine.trace import build_trace, deterministic_profile_hash

_SEGMENT_PATTERN = re.compile(r"[A-Z]+")


def _classify_y(
    letters: str,
    index: int,
    mode: YMode,
) -> tuple[str, bool]:
    if mode is YMode.ALWAYS_VOWEL:
        return "vowel", False
    if mode is YMode.ALWAYS_CONSONANT:
        return "consonant", False
    if mode is YMode.USER_FIXED:
        raise PolicyError("y_mode 'user_fixed' requires per-occurrence input not available in v1")

    previous = letters[index - 1] if index > 0 else None
    following = letters[index + 1] if index + 1 < len(letters) else None
    if index == 0 and following in VOWELS:
        return "consonant", False
    if previous in VOWELS and following in VOWELS:
        return "consonant", True
    if index > 0 and (following is None or following not in VOWELS):
        return "vowel", False
    return "consonant", True


def _partition_name(
    letters: str,
    *,
    policy: MethodPolicy,
    ambiguous_as_vowel: bool,
) -> tuple[int, int, tuple[str, ...], bool]:
    vowel_total = 0
    consonant_total = 0
    decisions: list[str] = []
    ambiguous_found = False
    for index, letter in enumerate(letters):
        value = letter_value(letter)
        if letter != "Y":
            if letter in VOWELS:
                vowel_total += value
            else:
                consonant_total += value
            continue
        classification, ambiguous = _classify_y(letters, index, policy.y_mode)
        ambiguous_found = ambiguous_found or ambiguous
        if ambiguous:
            classification = "vowel" if ambiguous_as_vowel else "consonant"
        decisions.append(f"Y@{index}:{classification}{':ambiguous' if ambiguous else ''}")
        if classification == "vowel":
            vowel_total += value
        else:
            consonant_total += value
    return vowel_total, consonant_total, tuple(decisions), ambiguous_found


def _name_numbers(
    original_name: str,
    *,
    basis: str,
    policy: MethodPolicy,
) -> tuple[NameNumberSet, tuple[NormalizationStep, ...], bool]:
    normalized, normalization_steps = normalize_name(
        original_name,
        umlaut_policy=policy.umlaut_policy,
        locale=policy.locale,
    )
    segment_texts = tuple(_SEGMENT_PATTERN.findall(normalized))
    if not segment_texts:
        raise NormalizationError("name must contain at least one A-Z letter after normalization")
    letters = "".join(segment_texts)
    segment_raw = tuple(
        sum(letter_value(letter) for letter in segment) for segment in segment_texts
    )
    segments = tuple(
        NameSegmentResult(
            text=segment,
            raw_total=raw,
            reduced_value=reduce_to_single_digit(raw, master_numbers=policy.master_numbers).value,
            compound_notation="/".join(
                str(value) for value in reduction_chain(raw, master_numbers=policy.master_numbers)
            ),
        )
        for segment, raw in zip(segment_texts, segment_raw, strict=True)
    )
    expression_raw = sum(letter_value(letter) for letter in letters)
    expression = create_number(
        f"{basis}_expression",
        expression_raw,
        policy=policy,
        components={
            f"segment_{index + 1}": segment.raw_total for index, segment in enumerate(segments)
        },
    )
    soul_raw, personality_raw, decisions, ambiguous = _partition_name(
        letters,
        policy=policy,
        ambiguous_as_vowel=False,
    )
    soul = create_number(f"{basis}_soul_urge", soul_raw, policy=policy)
    personality = create_number(f"{basis}_personality", personality_raw, policy=policy)

    variants: tuple[NameNumberVariant, ...] = ()
    if ambiguous:
        vowel_soul_raw, vowel_personality_raw, _, _ = _partition_name(
            letters,
            policy=policy,
            ambiguous_as_vowel=True,
        )
        variants = (
            NameNumberVariant(
                label="y_as_consonant",
                expression=expression,
                soul_urge=soul,
                personality=personality,
            ),
            NameNumberVariant(
                label="y_as_vowel",
                expression=expression,
                soul_urge=create_number(
                    f"{basis}_soul_urge_y_as_vowel",
                    vowel_soul_raw,
                    policy=policy,
                ),
                personality=create_number(
                    f"{basis}_personality_y_as_vowel",
                    vowel_personality_raw,
                    policy=policy,
                ),
            ),
        )

    return (
        NameNumberSet(
            basis=basis,
            original_name=original_name,
            normalized_name=normalized,
            segments=segments,
            expression=expression,
            soul_urge=soul,
            personality=personality,
            y_classifications=decisions,
            variants=variants,
        ),
        tuple(normalization_steps),
        ambiguous,
    )


def calculate_profile(person: PersonInput, policy: MethodPolicy) -> ProfileCalculationResult:
    """Calculate all V1 core values and return a versioned, hashed result."""
    life_a = life_path_a(person.birth_date, master_numbers=policy.master_numbers)
    life_b = life_path_b(person.birth_date, master_numbers=policy.master_numbers)
    consistency = consistency_check(life_a, life_b)
    birthday = create_number("birthday", person.birth_date.day, policy=policy)
    attitude = create_number(
        "attitude",
        person.birth_date.month + person.birth_date.day,
        policy=policy,
        components={"month": person.birth_date.month, "day": person.birth_date.day},
    )
    core, core_normalization, core_ambiguous = _name_numbers(
        person.core_name,
        basis="core_name",
        policy=policy,
    )

    active: NameNumberSet | None = None
    active_normalization: tuple[NormalizationStep, ...] = ()
    active_ambiguous = False
    if policy.name_basis is NameBasis.ACTIVE_NAME_ONLY and person.active_name is None:
        raise PolicyError("name_basis 'active_name_only' requires active_name")
    if person.active_name is not None and policy.name_basis is not NameBasis.CORE_NAME_ONLY:
        active, active_normalization, active_ambiguous = _name_numbers(
            person.active_name,
            basis="active_name",
            policy=policy,
        )

    maturity = create_number(
        "maturity",
        life_a.reduced_value + core.expression.reduced_value,
        policy=policy,
        components={
            "life_path": life_a.reduced_value,
            "expression": core.expression.reduced_value,
        },
    )
    warnings = (consistency.warning,) if consistency.warning else ()
    cycles = calculate_cycles(person, policy)
    calculation_steps = (
        *life_a.steps,
        *life_b.steps,
        *birthday.steps,
        *attitude.steps,
        *core.expression.steps,
        *core.soul_urge.steps,
        *core.personality.steps,
        *maturity.steps,
        *cycles.personal_year.steps,
        *cycles.personal_month.steps,
        *cycles.personal_day.steps,
        *(step for phase in cycles.pinnacles for step in phase.number.steps),
        *(step for phase in cycles.challenges for step in phase.number.steps),
    )
    trace: AuditTrace = build_trace(
        normalization_steps=(*core_normalization, *active_normalization),
        calculation_steps=calculation_steps,
        warnings=warnings,
        disambiguation_required=core_ambiguous or active_ambiguous,
    )
    result = ProfileCalculationResult(
        input_ref=person,
        policy=policy,
        life_path_a=life_a,
        life_path_b=life_b,
        consistency=consistency,
        birthday=birthday,
        attitude=attitude,
        core_name=core,
        active_name=active,
        maturity=maturity,
        cycles=cycles,
        trace=trace,
    )
    return result.model_copy(update={"deterministic_hash": deterministic_profile_hash(result)})
