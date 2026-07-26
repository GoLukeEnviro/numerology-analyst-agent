"""Domain enums for the Numerology Analyst Agent.

These enums are the vocabulary shared across the calculation core, the
audit trace and the (later) interpretation layer. They implement the
separation of statement classes required by the Master Implementation
Contract §2.2 (Trennung der Aussagearten).
"""

from __future__ import annotations

from enum import Enum


class ClaimType(str, Enum):
    """Statement classes (Master Contract §2.2).

    Every artifact in the system is tagged with exactly one claim type so
    that symbolic tradition, deterministic calculation, interpretive
    hypothesis and empirical evidence can never be silently conflated.
    """

    INPUT_FACT = "input_fact"
    CALCULATION_FACT = "calculation_fact"
    TRADITIONAL_CLAIM = "traditional_claim"
    INTERPRETIVE_HYPOTHESIS = "interpretive_hypothesis"
    EMPIRICAL_EVIDENCE = "empirical_evidence"
    PRACTICAL_SUGGESTION = "practical_suggestion"


class MethodSystem(str, Enum):
    """Numerological method systems.

    V1 implements only ``PYTHAGOREAN``. Other systems are documented
    extension points (Master Contract §3.1) and must never be silently
    mixed (calculation-engineer agent contract §4).
    """

    PYTHAGOREAN = "pythagorean"
    CHALDEAN = "chaldean"
    KABBALISTIC = "kabbalistic"


class YMode(str, Enum):
    """Y classification policy (ADR 0001).

    ``PHONETIC`` is the V1 canonical default for ``pythagorean-v1``.
    """

    PHONETIC = "phonetic"
    ALWAYS_VOWEL = "always_vowel"
    ALWAYS_CONSONANT = "always_consonant"
    USER_FIXED = "user_fixed"


class UmlautPolicy(str, Enum):
    """German umlaut / semantic normalization policy (ADR 0002).

    ``DE_DIRECT_V1`` is the V1 default for ``locale=de``. The two policies
    must never be mixed within a single calculation (ADR 0002 §7).
    """

    DE_DIRECT_V1 = "de-direct-v1"
    DE_EXPANDED_V1 = "de-expanded-v1"


class NameBasis(str, Enum):
    """Two-level name model selector (ADR 0004).

    There is intentionally no ``MIXED`` or ``WEIGHTED`` value: silently
    fusing ``core_name`` and ``active_name`` would violate the statement
    class separation (Master Contract §2.2).
    """

    CORE_NAME_ONLY = "core_name_only"
    ACTIVE_NAME_ONLY = "active_name_only"
    BOTH_SEPARATE = "both_separate"


class DateMethod(str, Enum):
    """Life Path reduction strategy.

    ``BOTH`` runs A and B and emits a consistency warning when they
    diverge (Master Contract §3.2, V1 minimal scope).
    """

    SUM_ALL_DIGITS = "sum_all_digits"
    COMPONENT_THEN_SUM = "component_then_sum"
    BOTH = "both"


class Locale(str, Enum):
    """Locale for normalization policy selection.

    V1 ships only ``DE``; other locales are extension points.
    """

    DE = "de"
    EN = "en"


class EvidenceLevel(str, Enum):
    """Evidence grading for claims (Master Contract §3.4, research layer).

    Used as metadata on interpretive/traditional claims; pure calculation
    facts are always ``CALCULATION_FACT`` and carry no evidence grade of
    their own.
    """

    NONE = "none"
    ANECDOTAL = "anecdotal"
    EXPLORATORY = "exploratory"
    CONFIRMATORY = "confirmatory"
    CONTRADICTED = "contradicted"
