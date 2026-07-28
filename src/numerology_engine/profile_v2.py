"""Deterministic pythagorean-v2 profile calculations (PR #19).

V2 introduces:
* NumberModel — full chain including master roots, karmic origin typing
* Primary life path: sum_all_birth_date_digits  (role=primary)
* Secondary life path: component_then_sum       (role=secondary, never overrides primary)
* Corrected personal year: reduced_month + reduced_day + reduced_universal_year
* Pinnacles/Challenges: root values only (master numbers force-reduced)
* de-expanded-v1 umlaut support (Ä→AE, Ö→OE, Ü→UE)
* Per-occurrence Y classification with decision_source

Invariants:
- No network, no LLM, no global mutable state, no randomness.
- V1 code paths are NOT modified.
- pythagorean-v2 MUST be specified in MethodPolicy.version.
"""

from __future__ import annotations

from datetime import date
import re

from numerology_domain.enums import NameBasis, YMode
from numerology_domain.exceptions import NormalizationError, PolicyError
from numerology_domain.models import (
    KARMIC_DEBTS,
    MASTER_NUMBERS,
    PYTHAGOREAN_V2_VERSION,
    AuditTrace,
    CalculationStep,
    CycleCalculationResultV2,
    KarmicOccurrence,
    MethodPolicy,
    NameNumberSetV2,
    NormalizationStep,
    NumberModel,
    PersonInput,
    ProfileCalculationResultV4,
)
from numerology_engine.alphabet import VOWELS, letter_value
from numerology_engine.normalization import normalize_name
from numerology_engine.reduction import digit_sum, reduce_to_single_digit
from numerology_engine.trace import build_trace

_SEGMENT_PATTERN = re.compile(r"[A-Z]+")

# ---------------------------------------------------------------------------
# V2 primitive helpers
# ---------------------------------------------------------------------------


def _full_chain_v2(n: int) -> tuple[int, ...]:
    """Full reduction chain ending always at a single digit (0-9).

    Unlike V1 reduction_chain, master numbers are NOT held — the chain
    continues to the root digit.  This gives:
      22 → (22, 4)
      11 → (11, 2)
      29 → (29, 11, 2)
      59 → (59, 14, 5)
      40 → (40, 4)
       4 → (4,)
       0 → (0,)   # challenge=0 special case

    Used internally for NumberModel construction only.
    """
    if n < 0:
        raise ValueError("_full_chain_v2 requires a non-negative integer")
    if n == 0:
        return (0,)
    result = [n]
    current = n
    while current > 9:
        current = digit_sum(current)
        result.append(current)
    return tuple(result)


def _held_master_from_chain(chain: tuple[int, ...]) -> int | None:
    """Return the FIRST master number (11/22/33) in the chain, or None.

    The root value (last element) is excluded because it is always a
    single digit.  We search from the beginning, so 29→11→2 returns 11.
    """
    for value in chain[:-1]:
        if value in MASTER_NUMBERS:
            return value
    return None


def _karmic_occurrences_from_chain(
    chain: tuple[int, ...],
    *,
    raw_origin_type: str = "direct_raw",
) -> tuple[KarmicOccurrence, ...]:
    """Extract karmic occurrences from a reduction chain.

    * chain[0] (raw_total): origin = raw_origin_type  (direct_raw or component_total)
    * chain[1:-1] (intermediates): origin = reduction_intermediate
    * chain[-1] (root): ignored (single digits are never karmic)
    """
    result: list[KarmicOccurrence] = []
    for idx, value in enumerate(chain):
        if idx == len(chain) - 1:
            # Root digit — never karmic
            continue
        if value not in KARMIC_DEBTS:
            continue
        origin = raw_origin_type if idx == 0 else "reduction_intermediate"
        result.append(KarmicOccurrence(value=value, origin_type=origin))
    return tuple(result)


def _compound_classification(
    is_master: bool,
    karmic_occurrences: tuple[KarmicOccurrence, ...],
    raw_total: int,
) -> str | None:
    """Derive the compound classification string (priority: master > karmic > compound)."""
    if is_master:
        return "master_number"
    if karmic_occurrences:
        return "karmic_debt"
    if raw_total >= 10:
        return "compound"
    return None


def create_number_model(
    raw_total: int,
    *,
    policy: MethodPolicy,
    components: tuple[int, ...] = (),
    step_description: str = "",
    raw_origin_type: str = "direct_raw",
) -> NumberModel:
    """Build a V2 NumberModel from a raw total.

    ``raw_origin_type`` distinguishes:
    * ``direct_raw``     — the raw_total itself (default for most numbers)
    * ``component_total`` — the raw_total is a sum of reduced components
                            (Life Path B / component_then_sum)
    """
    chain = _full_chain_v2(raw_total)
    root_value = chain[-1]
    held_master = _held_master_from_chain(chain)
    is_master = held_master is not None
    karmic = _karmic_occurrences_from_chain(chain, raw_origin_type=raw_origin_type)
    classification = _compound_classification(is_master, karmic, raw_total)
    display = "/".join(str(v) for v in chain)
    steps: tuple[str, ...] = (step_description,) if step_description else ()
    return NumberModel(
        raw_total=raw_total,
        reduction_chain=chain,
        root_value=root_value,
        held_master_value=held_master,
        display_notation=display,
        is_master=is_master,
        compound_classification=classification,
        karmic_occurrences=karmic,
        components=components,
        steps=steps,
    )


# ---------------------------------------------------------------------------
# Life Path V2
# ---------------------------------------------------------------------------


def life_path_primary_v2(
    birth: date,
    *,
    master_numbers: frozenset[int] = MASTER_NUMBERS,
) -> NumberModel:
    """Life Path primary — sum_all_birth_date_digits (role=primary).

    Adds every digit of the ISO YYYYMMDD date string, then reduces.
    Lukas 18.07.1986: 1+8+0+7+1+9+8+6 = 40 → 4  (notation: 40/4)
    """
    digits = tuple(int(ch) for ch in f"{birth.year:04d}{birth.month:02d}{birth.day:02d}")
    raw = sum(digits)
    step = f"{' + '.join(str(d) for d in digits)} = {raw} (sum_all_birth_date_digits)"
    return create_number_model(
        raw,
        policy=MethodPolicy(version=PYTHAGOREAN_V2_VERSION),
        components=digits,
        step_description=step,
        raw_origin_type="direct_raw",
    )


def life_path_secondary_v2(
    birth: date,
    *,
    master_numbers: frozenset[int] = MASTER_NUMBERS,
) -> NumberModel:
    """Life Path secondary — component_then_sum (role=secondary).

    Reduces month, day, year independently (holding masters), then sums
    the three reduced values and reduces.
    Lukas 18.07.1986: 7 + 9 + 6 = 22 → 22/4

    This result NEVER overrides the primary.
    """
    month_out = reduce_to_single_digit(birth.month, master_numbers=master_numbers)
    day_out = reduce_to_single_digit(birth.day, master_numbers=master_numbers)
    year_sum = digit_sum(birth.year)
    year_out = reduce_to_single_digit(year_sum, master_numbers=master_numbers)
    components_reduced = (month_out.value, day_out.value, year_out.value)
    raw = sum(components_reduced)
    step = (
        f"month={birth.month}→{month_out.value}  "
        f"day={birth.day}→{day_out.value}  "
        f"year={birth.year}→{year_sum}→{year_out.value}  "
        f"sum={month_out.value}+{day_out.value}+{year_out.value}={raw} "
        f"(component_then_sum)"
    )
    return create_number_model(
        raw,
        policy=MethodPolicy(version=PYTHAGOREAN_V2_VERSION),
        components=components_reduced,
        step_description=step,
        raw_origin_type="component_total",
    )


# ---------------------------------------------------------------------------
# Cycle V2 — corrected personal year formula
# ---------------------------------------------------------------------------


def _root_value(n: int) -> int:
    """Reduce n to 1-9 without holding master numbers (for cycle components)."""
    chain = _full_chain_v2(n)
    return chain[-1]


def calculate_cycles_v2(person: PersonInput, policy: MethodPolicy) -> CycleCalculationResultV2:
    """Personal cycles for V2: corrected personal year + root-based components.

    Personal Year: reduced_birth_month + reduced_birth_day + reduced_universal_year
    Personal Month: personal_year.root_value + reduced_calendar_month
    Personal Day: personal_month.root_value + reduced_calendar_day

    Pinnacles/Challenges: use ROOT values (master numbers force-reduced).
    Lukas 2026 personal year: 7 + 9 + 1 = 17 → 8 (notation: 17/8)
    """
    birth = person.birth_date
    as_of = person.as_of_date

    # Birth date components — reduced holding masters (for personal year)
    month_red = reduce_to_single_digit(birth.month, master_numbers=policy.master_numbers)
    day_red = reduce_to_single_digit(birth.day, master_numbers=policy.master_numbers)

    # Universal year: digit_sum of current year → reduce (holding 11/22/33)
    universal_year_sum = digit_sum(as_of.year)
    universal_year_red = reduce_to_single_digit(
        universal_year_sum, master_numbers=policy.master_numbers
    )

    py_raw = month_red.value + day_red.value + universal_year_red.value
    py_step = (
        f"birth_month={birth.month}→{month_red.value}  "
        f"birth_day={birth.day}→{day_red.value}  "
        f"universal_year={as_of.year}→{universal_year_sum}→{universal_year_red.value}  "
        f"sum={py_raw}"
    )
    personal_year = create_number_model(
        py_raw,
        policy=policy,
        components=(month_red.value, day_red.value, universal_year_red.value),
        step_description=py_step,
    )

    cal_month_red = reduce_to_single_digit(as_of.month, master_numbers=policy.master_numbers)
    pm_raw = personal_year.root_value + cal_month_red.value
    personal_month = create_number_model(
        pm_raw,
        policy=policy,
        components=(personal_year.root_value, cal_month_red.value),
        step_description=f"personal_year.root={personal_year.root_value} + month={as_of.month}→{cal_month_red.value}",
    )

    cal_day_red = reduce_to_single_digit(as_of.day, master_numbers=policy.master_numbers)
    pd_raw = personal_month.root_value + cal_day_red.value
    personal_day = create_number_model(
        pd_raw,
        policy=policy,
        components=(personal_month.root_value, cal_day_red.value),
        step_description=f"personal_month.root={personal_month.root_value} + day={as_of.day}→{cal_day_red.value}",
    )

    # Pinnacle/Challenge components use ROOT values (master force-reduced)
    m_root = _root_value(birth.month)
    d_root = _root_value(birth.day)
    y_root = _root_value(digit_sum(birth.year))

    p1 = create_number_model(
        m_root + d_root,
        policy=policy,
        components=(m_root, d_root),
        step_description="P1=month.root+day.root",
    )
    p2 = create_number_model(
        d_root + y_root,
        policy=policy,
        components=(d_root, y_root),
        step_description="P2=day.root+year.root",
    )
    p3 = create_number_model(
        p1.root_value + p2.root_value,
        policy=policy,
        components=(p1.root_value, p2.root_value),
        step_description="P3=P1.root+P2.root",
    )
    p4 = create_number_model(
        m_root + y_root,
        policy=policy,
        components=(m_root, y_root),
        step_description="P4=month.root+year.root",
    )

    c1 = create_number_model(
        abs(d_root - m_root),
        policy=policy,
        components=(d_root, m_root),
        step_description=f"C1=|day.root({d_root})-month.root({m_root})|",
    )
    c2 = create_number_model(
        abs(d_root - y_root),
        policy=policy,
        components=(d_root, y_root),
        step_description=f"C2=|day.root({d_root})-year.root({y_root})|",
    )
    c3 = create_number_model(
        abs(c1.root_value - c2.root_value),
        policy=policy,
        components=(c1.root_value, c2.root_value),
        step_description=f"C3=|C1.root({c1.root_value})-C2.root({c2.root_value})|",
    )
    c4 = create_number_model(
        abs(m_root - y_root),
        policy=policy,
        components=(m_root, y_root),
        step_description=f"C4=|month.root({m_root})-year.root({y_root})|",
    )

    return CycleCalculationResultV2(
        as_of_date=as_of,
        personal_year=personal_year,
        personal_month=personal_month,
        personal_day=personal_day,
        pinnacles=(p1, p2, p3, p4),
        challenges=(c1, c2, c3, c4),
    )


# ---------------------------------------------------------------------------
# Name numbers V2
# ---------------------------------------------------------------------------


def _classify_y_v2(
    letters: str,
    index: int,
    mode: YMode,
) -> tuple[str, str, bool]:
    """Classify a Y at position ``index`` in ``letters``.

    Returns (classification, decision_source, ambiguous).
    decision_source ∈ {phonetic_rule, always_vowel, always_consonant, user_fixed}
    """
    if mode is YMode.ALWAYS_VOWEL:
        return "vowel", "always_vowel", False
    if mode is YMode.ALWAYS_CONSONANT:
        return "consonant", "always_consonant", False
    if mode is YMode.USER_FIXED:
        raise PolicyError("y_mode 'user_fixed' requires per-occurrence input not available in v2")

    # PHONETIC rule (ADR 0001)
    previous = letters[index - 1] if index > 0 else None
    following = letters[index + 1] if index + 1 < len(letters) else None

    if index == 0 and following in VOWELS:
        return "consonant", "phonetic_rule", False
    if previous in VOWELS and following in VOWELS:
        return "consonant", "phonetic_rule", True  # ambiguous: surrounded by vowels
    if index > 0 and (following is None or following not in VOWELS):
        return "vowel", "phonetic_rule", False
    return "consonant", "phonetic_rule", True


def _partition_name_v2(
    letters: str,
    *,
    policy: MethodPolicy,
) -> tuple[int, int, tuple[str, ...], bool]:
    """Partition letters into vowel/consonant totals.

    Returns (vowel_total, consonant_total, y_classification_records, ambiguous_found).
    """
    vowel_total = 0
    consonant_total = 0
    y_records: list[str] = []
    ambiguous_found = False

    for index, letter in enumerate(letters):
        value = letter_value(letter)
        if letter != "Y":
            if letter in VOWELS:
                vowel_total += value
            else:
                consonant_total += value
            continue

        classification, decision_source, ambiguous = _classify_y_v2(letters, index, policy.y_mode)
        ambiguous_found = ambiguous_found or ambiguous

        # When ambiguous, default to consonant unless policy forces vowel
        if ambiguous and policy.y_mode is YMode.PHONETIC:
            classification = "consonant"

        y_records.append(
            f"Y@{index}:{classification}:{decision_source}{'::ambiguous' if ambiguous else ''}"
        )

        if classification == "vowel":
            vowel_total += value
        else:
            consonant_total += value

    return vowel_total, consonant_total, tuple(y_records), ambiguous_found


def _name_numbers_v2(
    original_name: str,
    *,
    basis: str,
    policy: MethodPolicy,
    life_path_root: int,
) -> tuple[NameNumberSetV2, tuple[NormalizationStep, ...], bool]:
    """Compute V2 name numbers for one name."""
    normalized, norm_steps = normalize_name(
        original_name,
        umlaut_policy=policy.umlaut_policy,
        locale=policy.locale,
    )
    segment_texts = tuple(_SEGMENT_PATTERN.findall(normalized))
    if not segment_texts:
        raise NormalizationError("name must contain at least one A-Z letter after normalization")
    letters = "".join(segment_texts)

    expression_raw = sum(letter_value(letter) for letter in letters)
    expression = create_number_model(
        expression_raw,
        policy=policy,
        components=tuple(letter_value(letter) for letter in letters),
        step_description=f"expression: {' + '.join(str(letter_value(letter)) for letter in letters)} = {expression_raw}",
    )

    soul_raw, personality_raw, y_classifications, ambiguous = _partition_name_v2(
        letters, policy=policy
    )
    soul = create_number_model(
        soul_raw,
        policy=policy,
        step_description=f"soul_urge raw={soul_raw} (vowels only)",
    )
    personality = create_number_model(
        personality_raw,
        policy=policy,
        step_description=f"personality raw={personality_raw} (consonants only)",
    )

    maturity_raw = life_path_root + expression.root_value
    maturity = create_number_model(
        maturity_raw,
        policy=policy,
        components=(life_path_root, expression.root_value),
        step_description=f"maturity: lw.root({life_path_root}) + expression.root({expression.root_value}) = {maturity_raw}",
    )

    return (
        NameNumberSetV2(
            basis=basis,
            original_name=original_name,
            normalized_name=normalized,
            expression=expression,
            soul_urge=soul,
            personality=personality,
            maturity=maturity,
            y_classifications=y_classifications,
        ),
        tuple(norm_steps),
        ambiguous,
    )


# ---------------------------------------------------------------------------
# Full V4 profile
# ---------------------------------------------------------------------------


def calculate_profile_v2(person: PersonInput, policy: MethodPolicy) -> ProfileCalculationResultV4:
    """Calculate a complete V2 profile and return a ProfileCalculationResultV4.

    Requires ``policy.version == 'v2'``.  V1 code paths are not touched.
    """
    if policy.version != PYTHAGOREAN_V2_VERSION:
        raise PolicyError(
            f"calculate_profile_v2 requires policy.version='v2', got {policy.version!r}"
        )

    life_primary = life_path_primary_v2(person.birth_date, master_numbers=policy.master_numbers)
    life_secondary = life_path_secondary_v2(person.birth_date, master_numbers=policy.master_numbers)

    birthday = create_number_model(
        person.birth_date.day,
        policy=policy,
        step_description=f"birthday={person.birth_date.day}",
    )
    attitude = create_number_model(
        person.birth_date.month + person.birth_date.day,
        policy=policy,
        components=(person.birth_date.month, person.birth_date.day),
        step_description=(
            f"attitude: month({person.birth_date.month}) + day({person.birth_date.day}) "
            f"= {person.birth_date.month + person.birth_date.day}"
        ),
    )

    cycles = calculate_cycles_v2(person, policy)

    core: NameNumberSetV2 | None = None
    core_normalization: tuple[NormalizationStep, ...] = ()
    core_ambiguous = False
    active: NameNumberSetV2 | None = None
    active_normalization: tuple[NormalizationStep, ...] = ()
    active_ambiguous = False

    if policy.name_basis is NameBasis.ACTIVE_NAME_ONLY and person.active_name is None:
        raise PolicyError("name_basis 'active_name_only' requires active_name")

    if policy.name_basis is not NameBasis.ACTIVE_NAME_ONLY:
        core, core_normalization, core_ambiguous = _name_numbers_v2(
            person.core_name,
            basis="core_name",
            policy=policy,
            life_path_root=life_primary.root_value,
        )
    if person.active_name is not None and policy.name_basis is not NameBasis.CORE_NAME_ONLY:
        active, active_normalization, active_ambiguous = _name_numbers_v2(
            person.active_name,
            basis="active_name",
            policy=policy,
            life_path_root=life_primary.root_value,
        )

    warnings: tuple[str, ...] = ()
    if life_primary.root_value != life_secondary.root_value:
        warnings = (
            f"V2_LIFE_PATH_DIVERGENCE: primary_root={life_primary.root_value} "
            f"secondary_root={life_secondary.root_value}",
        )

    all_calc_steps: tuple[CalculationStep, ...] = ()

    trace: AuditTrace = build_trace(
        normalization_steps=(*core_normalization, *active_normalization),
        calculation_steps=all_calc_steps,
        warnings=warnings,
        disambiguation_required=core_ambiguous or active_ambiguous,
    )

    result = ProfileCalculationResultV4(
        input_ref=person,
        policy=policy,
        life_path_primary=life_primary,
        life_path_secondary=life_secondary,
        birthday=birthday,
        attitude=attitude,
        core_name=core,
        active_name=active,
        cycles=cycles,
        trace=trace,
    )

    # Compute deterministic hash using the same infrastructure as V1
    from numerology_engine.trace import deterministic_profile_hash_v4

    return result.model_copy(update={"deterministic_hash": deterministic_profile_hash_v4(result)})
