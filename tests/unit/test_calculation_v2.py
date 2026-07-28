"""Unit-Tests für pythagorean-v2 Berechnungsformeln (PR #19).

Jede Testfunktion prüft genau eine Formel oder Invariante.
"""

from __future__ import annotations

from datetime import date

import pytest

from numerology_domain.enums import UmlautPolicy
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    KarmicOccurrence,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.normalization import normalize_name
from numerology_engine.profile_v2 import (
    _full_chain_v2,
    _held_master_from_chain,
    _karmic_occurrences_from_chain,
    calculate_cycles_v2,
    create_number_model,
    life_path_primary_v2,
    life_path_secondary_v2,
)

_POLICY_V2 = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)
_POLICY_V2_EXPANDED = MethodPolicy(
    version=PYTHAGOREAN_V2_VERSION,
    umlaut_policy=UmlautPolicy.DE_EXPANDED_V1,
)


# ---------------------------------------------------------------------------
# _full_chain_v2
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_full_chain_single_digit():
    assert _full_chain_v2(4) == (4,)


@pytest.mark.unit
def test_full_chain_zero():
    assert _full_chain_v2(0) == (0,)


@pytest.mark.unit
def test_full_chain_master_continues_to_root():
    """22 → (22, 4): master number continues to root."""
    assert _full_chain_v2(22) == (22, 4)


@pytest.mark.unit
def test_full_chain_11_to_2():
    assert _full_chain_v2(11) == (11, 2)


@pytest.mark.unit
def test_full_chain_33_to_6():
    assert _full_chain_v2(33) == (33, 6)


@pytest.mark.unit
def test_full_chain_44_not_master():
    """44 is NOT a master number — reduces to 8 without being held."""
    assert _full_chain_v2(44) == (44, 8)


@pytest.mark.unit
def test_full_chain_29_through_master():
    assert _full_chain_v2(29) == (29, 11, 2)


@pytest.mark.unit
def test_full_chain_40():
    assert _full_chain_v2(40) == (40, 4)


@pytest.mark.unit
def test_full_chain_59_karmic_intermediate():
    assert _full_chain_v2(59) == (59, 14, 5)


@pytest.mark.unit
def test_full_chain_67_karmic_intermediate():
    assert _full_chain_v2(67) == (67, 13, 4)


# ---------------------------------------------------------------------------
# _held_master_from_chain
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_held_master_for_22():
    assert _held_master_from_chain((22, 4)) == 22


@pytest.mark.unit
def test_held_master_for_29():
    assert _held_master_from_chain((29, 11, 2)) == 11


@pytest.mark.unit
def test_held_master_none_for_44():
    assert _held_master_from_chain((44, 8)) is None


@pytest.mark.unit
def test_held_master_none_for_single():
    assert _held_master_from_chain((4,)) is None


# ---------------------------------------------------------------------------
# _karmic_occurrences_from_chain
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_karmic_direct_raw():
    occ = _karmic_occurrences_from_chain((16, 7))
    assert len(occ) == 1
    assert occ[0].value == 16
    assert occ[0].origin_type == "direct_raw"


@pytest.mark.unit
def test_karmic_intermediate():
    occ = _karmic_occurrences_from_chain((59, 14, 5))
    assert len(occ) == 1
    assert occ[0].value == 14
    assert occ[0].origin_type == "reduction_intermediate"


@pytest.mark.unit
def test_karmic_component_total():
    occ = _karmic_occurrences_from_chain((13, 4), raw_origin_type="component_total")
    assert len(occ) == 1
    assert occ[0].value == 13
    assert occ[0].origin_type == "component_total"


@pytest.mark.unit
def test_karmic_none_for_non_karmic():
    occ = _karmic_occurrences_from_chain((62, 8))
    assert len(occ) == 0


# ---------------------------------------------------------------------------
# create_number_model
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_create_number_model_22():
    n = create_number_model(22, policy=_POLICY_V2)
    assert n.display_notation == "22/4"
    assert n.root_value == 4
    assert n.is_master
    assert n.held_master_value == 22
    assert n.compound_classification == "master_number"


@pytest.mark.unit
def test_create_number_model_44_not_master():
    n = create_number_model(44, policy=_POLICY_V2)
    assert n.display_notation == "44/8"
    assert n.root_value == 8
    assert not n.is_master
    assert n.held_master_value is None


@pytest.mark.unit
def test_create_number_model_karmic_direct():
    n = create_number_model(16, policy=_POLICY_V2)
    assert n.display_notation == "16/7"
    assert len(n.karmic_occurrences) == 1
    assert n.karmic_occurrences[0].origin_type == "direct_raw"


@pytest.mark.unit
def test_create_number_model_zero_challenge():
    n = create_number_model(0, policy=_POLICY_V2)
    assert n.root_value == 0
    assert n.display_notation == "0"


# ---------------------------------------------------------------------------
# Life Path V2
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_life_path_primary_lukas():
    result = life_path_primary_v2(date(1986, 7, 18))
    assert result.display_notation == "40/4"
    assert result.root_value == 4
    assert not result.is_master


@pytest.mark.unit
def test_life_path_primary_stella():
    result = life_path_primary_v2(date(2011, 4, 18))
    assert result.display_notation == "17/8"


@pytest.mark.unit
def test_life_path_primary_antoney():
    result = life_path_primary_v2(date(1995, 10, 15))
    assert result.display_notation == "31/4"


@pytest.mark.unit
def test_life_path_secondary_lukas_master():
    result = life_path_secondary_v2(date(1986, 7, 18))
    assert result.display_notation == "22/4"
    assert result.is_master
    assert result.held_master_value == 22


@pytest.mark.unit
def test_life_path_secondary_antoney_karmic():
    result = life_path_secondary_v2(date(1995, 10, 15))
    assert result.display_notation == "13/4"
    assert len(result.karmic_occurrences) == 1
    assert result.karmic_occurrences[0].origin_type == "component_total"
    assert result.karmic_occurrences[0].value == 13


@pytest.mark.unit
def test_life_path_secondary_sina_holds_master_in_sum():
    """Sina day=11 (master held) contributes 11 to sum: 3+11+3=17→8."""
    result = life_path_secondary_v2(date(1992, 12, 11))
    assert result.display_notation == "17/8"


# ---------------------------------------------------------------------------
# Personal Year V2 formula
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_personal_year_v2_lukas_2026():
    """7 + 9 + reduce(digit_sum(2026)=10→1) = 17 → 8."""
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 28),
    )
    cycles = calculate_cycles_v2(person, _POLICY_V2)
    assert cycles.personal_year.display_notation == "17/8"


@pytest.mark.unit
def test_personal_year_v2_sina_2026_holds_birth_day_master():
    """Sina: birth_day=11 (master held) contributes 11 to personal year sum."""
    person = PersonInput(
        core_name="Sina Langner",
        birth_date=date(1992, 12, 11),
        as_of_date=date(2026, 7, 28),
    )
    cycles = calculate_cycles_v2(person, _POLICY_V2)
    assert cycles.personal_year.display_notation == "15/6"


# ---------------------------------------------------------------------------
# Challenge root reduction (master force-reduced)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_challenge_uses_root_not_master():
    """Birth day=11 → root=2 for challenge components."""
    # Person with day=29 (→ 11 master → root=2 for challenges)
    person = PersonInput(
        core_name="Test Master Day",
        birth_date=date(2000, 3, 29),  # day=29 → reduce→11 master → root=2
        as_of_date=date(2026, 7, 28),
    )
    cycles = calculate_cycles_v2(person, _POLICY_V2)
    # month=3, day.root=2, year.root=reduce(2)=2
    # C1=|2-3|=1, C2=|2-2|=0, C3=|1-0|=1, C4=|3-2|=1
    assert cycles.challenges[0].root_value == 1  # C1=|day.root-month.root|=|2-3|=1
    assert cycles.challenges[1].root_value == 0  # C2=|day.root-year.root|=|2-2|=0


# ---------------------------------------------------------------------------
# de-expanded-v1 normalization
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_de_expanded_ae():
    normalized, _ = normalize_name("Ärger", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
    assert normalized.startswith("AE")


@pytest.mark.unit
def test_de_expanded_oe():
    normalized, _ = normalize_name("Öl", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
    assert normalized.startswith("OE")


@pytest.mark.unit
def test_de_expanded_ue():
    normalized, _ = normalize_name("Müller", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
    assert "UE" in normalized


@pytest.mark.unit
def test_de_expanded_ss():
    normalized, _ = normalize_name("Straße", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
    assert "SS" in normalized


@pytest.mark.unit
def test_de_direct_ae():
    normalized, _ = normalize_name("Ärger", umlaut_policy=UmlautPolicy.DE_DIRECT_V1)
    assert normalized.startswith("A")
    assert "AE" not in normalized


@pytest.mark.unit
def test_de_expanded_lower():
    """Lowercase umlauts are also expanded."""
    normalized, _ = normalize_name("müller", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
    assert "UE" in normalized


# ---------------------------------------------------------------------------
# Master number boundary
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_44_not_master_in_number_model():
    n = create_number_model(44, policy=_POLICY_V2)
    assert not n.is_master
    assert n.held_master_value is None
    assert n.compound_classification == "compound"


@pytest.mark.unit
def test_11_is_master():
    n = create_number_model(11, policy=_POLICY_V2)
    assert n.is_master
    assert n.held_master_value == 11
    assert n.root_value == 2


@pytest.mark.unit
def test_22_is_master():
    n = create_number_model(22, policy=_POLICY_V2)
    assert n.is_master
    assert n.held_master_value == 22
    assert n.root_value == 4


@pytest.mark.unit
def test_33_is_master():
    n = create_number_model(33, policy=_POLICY_V2)
    assert n.is_master
    assert n.held_master_value == 33
    assert n.root_value == 6


# ---------------------------------------------------------------------------
# Method Policy V2 validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_method_policy_v2_accepted():
    p = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)
    assert p.version == "v2"


@pytest.mark.unit
def test_method_policy_v1_still_accepted():
    from numerology_domain.models import PYTHAGOREAN_V1_VERSION

    p = MethodPolicy(version=PYTHAGOREAN_V1_VERSION)
    assert p.version == "v1"


@pytest.mark.unit
def test_method_policy_invalid_version_rejected():
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        MethodPolicy(version="v3")


# ---------------------------------------------------------------------------
# Leap-day test
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_leap_day_29_feb():
    """29.02.2000 — leap day must not crash."""
    result = life_path_primary_v2(date(2000, 2, 29))
    assert result.root_value in range(1, 10)  # valid 1-9


# ---------------------------------------------------------------------------
# KarmicOccurrence model validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_karmic_occurrence_invalid_value():
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        KarmicOccurrence(value=15, origin_type="direct_raw")


@pytest.mark.unit
def test_karmic_occurrence_invalid_origin():
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        KarmicOccurrence(value=13, origin_type="unknown_origin")


@pytest.mark.unit
def test_karmic_occurrence_valid():
    k = KarmicOccurrence(value=14, origin_type="reduction_intermediate")
    assert k.value == 14
    assert k.origin_type == "reduction_intermediate"


# ---------------------------------------------------------------------------
# Coverage gap: uncovered edge paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_full_chain_negative_raises():
    from numerology_engine.profile_v2 import _full_chain_v2

    with pytest.raises(ValueError, match="non-negative"):
        _full_chain_v2(-1)


@pytest.mark.unit
def test_classify_y_always_consonant():
    from numerology_domain.enums import YMode
    from numerology_engine.profile_v2 import _classify_y_v2

    classification, source, ambiguous = _classify_y_v2("AY", 1, YMode.ALWAYS_CONSONANT)
    assert classification == "consonant"
    assert source == "always_consonant"
    assert ambiguous is False


@pytest.mark.unit
def test_classify_y_always_vowel():
    from numerology_domain.enums import YMode
    from numerology_engine.profile_v2 import _classify_y_v2

    classification, source, ambiguous = _classify_y_v2("YA", 0, YMode.ALWAYS_VOWEL)
    assert classification == "vowel"
    assert source == "always_vowel"
    assert ambiguous is False


@pytest.mark.unit
def test_classify_y_user_fixed_raises():
    from numerology_domain.enums import YMode
    from numerology_domain.exceptions import PolicyError
    from numerology_engine.profile_v2 import _classify_y_v2

    with pytest.raises(PolicyError):
        _classify_y_v2("AY", 1, YMode.USER_FIXED)


@pytest.mark.unit
def test_classify_y_between_two_vowels_ambiguous():
    """Y surrounded by vowels → consonant, ambiguous (phonetic rule line 386-387)."""
    from numerology_domain.enums import YMode
    from numerology_engine.profile_v2 import _classify_y_v2

    # A-Y-A: index=1, previous='A' (vowel), following='A' (vowel)
    classification, source, ambiguous = _classify_y_v2("AYA", 1, YMode.PHONETIC)
    assert classification == "consonant"
    assert source == "phonetic_rule"
    assert ambiguous is True


@pytest.mark.unit
def test_classify_y_at_start_with_consonant_following():
    """Y at index 0 with consonant following → consonant, ambiguous (fallthrough line 391)."""
    from numerology_domain.enums import YMode
    from numerology_engine.profile_v2 import _classify_y_v2

    # Y-B: index=0, following='B' (not vowel) → not caught by line 385, falls to line 391
    classification, source, ambiguous = _classify_y_v2("YB", 0, YMode.PHONETIC)
    assert classification == "consonant"
    assert source == "phonetic_rule"


@pytest.mark.unit
def test_classify_y_at_start_with_vowel_following():
    """Y at index 0 with vowel following → consonant, not ambiguous (phonetic rule line 385-386)."""
    from numerology_domain.enums import YMode
    from numerology_engine.profile_v2 import _classify_y_v2

    # Y-A: index=0, following='A' (vowel) → hits line 385 condition
    classification, source, ambiguous = _classify_y_v2("YA", 0, YMode.PHONETIC)
    assert classification == "consonant"
    assert source == "phonetic_rule"
    assert ambiguous is False


@pytest.mark.unit
def test_name_with_no_letters_after_normalization():
    """A name that reduces to no A-Z letters raises NormalizationError."""
    from numerology_domain.exceptions import NormalizationError
    from numerology_engine.profile_v2 import calculate_profile_v2

    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)
    person = PersonInput(
        core_name="123-456",
        birth_date=date(1990, 3, 15),
        as_of_date=date(2026, 7, 28),
    )
    with pytest.raises(NormalizationError):
        calculate_profile_v2(person, policy)


@pytest.mark.unit
def test_calculate_profile_v2_active_name_only_without_active_raises():
    from numerology_domain.enums import NameBasis
    from numerology_domain.exceptions import PolicyError
    from numerology_engine.profile_v2 import calculate_profile_v2

    policy = MethodPolicy(
        version=PYTHAGOREAN_V2_VERSION,
        name_basis=NameBasis.ACTIVE_NAME_ONLY,
    )
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1990, 3, 15),
        as_of_date=date(2026, 7, 28),
        # active_name=None
    )
    with pytest.raises(PolicyError):
        calculate_profile_v2(person, policy)


@pytest.mark.unit
def test_calculate_profile_v2_wrong_version_raises():
    """calculate_profile_v2 with v1 policy raises PolicyError (line 511 coverage)."""
    from numerology_domain.exceptions import PolicyError
    from numerology_engine.profile_v2 import calculate_profile_v2

    policy_v1 = MethodPolicy(version="v1")
    person = PersonInput(
        core_name="Test",
        birth_date=date(1990, 3, 15),
        as_of_date=date(2026, 7, 28),
    )
    with pytest.raises(PolicyError, match="policy.version='v2'"):
        calculate_profile_v2(person, policy_v1)


@pytest.mark.unit
def test_calculate_profile_v2_active_name_only_with_active():
    """ACTIVE_NAME_ONLY policy with active_name set: skips core, calculates active (branch 545->552)."""
    from numerology_domain.enums import NameBasis
    from numerology_engine.profile_v2 import calculate_profile_v2

    policy = MethodPolicy(
        version=PYTHAGOREAN_V2_VERSION,
        name_basis=NameBasis.ACTIVE_NAME_ONLY,
    )
    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1990, 3, 15),
        as_of_date=date(2026, 7, 28),
        active_name="Luka",
    )
    result = calculate_profile_v2(person, policy)
    assert result.core_name is None
    assert result.active_name is not None
    assert result.active_name.original_name == "Luka"


@pytest.mark.unit
def test_calculate_profile_v2_with_active_name():
    from numerology_engine.profile_v2 import calculate_profile_v2

    policy = _POLICY_V2
    person = PersonInput(
        core_name="Anna Mueller",
        birth_date=date(1990, 5, 5),
        as_of_date=date(2026, 7, 28),
        active_name="Anna",
    )
    result = calculate_profile_v2(person, policy)
    assert result.active_name is not None
    assert result.active_name.original_name == "Anna"


@pytest.mark.unit
def test_life_path_divergence_warning():
    """A birth date where primary ≠ secondary root triggers a divergence warning."""
    from unittest.mock import patch

    from numerology_engine.profile_v2 import calculate_profile_v2

    # Force the divergence by patching life_path_secondary_v2 to return a different root.
    # This tests line 562 (the warning generation branch) that can't be reached
    # naturally because digital-root algebra preserves the mod-9 class.
    policy = _POLICY_V2
    person = PersonInput(
        core_name="Test",
        birth_date=date(2001, 1, 1),
        as_of_date=date(2026, 7, 28),
    )

    # Compute real primary to know its root
    from numerology_engine.profile_v2 import create_number_model, life_path_secondary_v2

    real_secondary = life_path_secondary_v2(person.birth_date)
    # Build a fake secondary with a different root_value to trigger the warning
    different_root = (real_secondary.root_value % 9) + 1  # always different
    fake_secondary = create_number_model(different_root, policy=policy, step_description="fake")

    with patch("numerology_engine.profile_v2.life_path_secondary_v2", return_value=fake_secondary):
        result = calculate_profile_v2(person, policy)

    assert len(result.trace.warnings) > 0
    assert "V2_LIFE_PATH_DIVERGENCE" in result.trace.warnings[0]
