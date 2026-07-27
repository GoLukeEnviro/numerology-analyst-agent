"""Contract tests for the complete deterministic profile (v0.1.4)."""

from __future__ import annotations

from datetime import date

import pytest

from numerology_domain.enums import NameBasis, YMode
from numerology_domain.exceptions import NormalizationError, PolicyError
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.numbers import create_number
from numerology_engine.profile import calculate_profile


@pytest.fixture
def person() -> PersonInput:
    return PersonInput(
        core_name="Max Mustermann",
        active_name="Max Power",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )


@pytest.mark.unit
def test_complete_reference_profile(person: PersonInput) -> None:
    result = calculate_profile(person, MethodPolicy())

    assert result.schema_version == "profile-calculation-result-v2"
    assert result.life_path_a.reduced_value == 1
    assert result.life_path_b.reduced_value == 1
    assert result.birthday.reduced_value == 7
    assert result.attitude.reduced_value == 5

    assert result.core_name.expression.raw_total == 50
    assert result.core_name.expression.reduced_value == 5
    assert result.core_name.soul_urge.raw_total == 10
    assert result.core_name.soul_urge.reduced_value == 1
    assert result.core_name.personality.raw_total == 40
    assert result.core_name.personality.reduced_value == 4
    assert [segment.text for segment in result.core_name.segments] == ["MAX", "MUSTERMANN"]
    assert [segment.raw_total for segment in result.core_name.segments] == [11, 39]

    assert result.active_name is not None
    assert result.active_name.expression.reduced_value == 7
    assert result.maturity.reduced_value == 6
    assert len(result.deterministic_hash) == 64


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "soul", "personality"),
    [
        ("Yoga", 7, 5),  # word-initial Y followed by a vowel: consonant
        ("Lydia", 8, 7),  # internal Y followed by a consonant: vowel
    ],
)
def test_phonetic_y_clear_cases(name: str, soul: int, personality: int) -> None:
    result = calculate_profile(
        PersonInput(
            core_name=name,
            birth_date=date(1990, 1, 1),
            as_of_date=date(2026, 7, 26),
        ),
        MethodPolicy(y_mode=YMode.PHONETIC),
    )

    assert result.core_name.soul_urge.reduced_value == soul
    assert result.core_name.personality.reduced_value == personality
    assert result.trace.disambiguation_required is False


@pytest.mark.unit
def test_ambiguous_y_emits_both_variants() -> None:
    result = calculate_profile(
        PersonInput(
            core_name="Maya",
            birth_date=date(1990, 1, 1),
            as_of_date=date(2026, 7, 26),
        ),
        MethodPolicy(y_mode=YMode.PHONETIC),
    )

    assert result.trace.disambiguation_required is True
    assert {variant.label for variant in result.core_name.variants} == {
        "y_as_consonant",
        "y_as_vowel",
    }
    assert {variant.expression.reduced_value for variant in result.core_name.variants} == {4}


@pytest.mark.unit
def test_profile_hash_is_deterministic_and_excludes_consent(person: PersonInput) -> None:
    without_consent = calculate_profile(person, MethodPolicy())
    with_consent = calculate_profile(
        person.model_copy(update={"consent_given": True}),
        MethodPolicy(),
    )

    assert without_consent.deterministic_hash == with_consent.deterministic_hash
    assert calculate_profile(person, MethodPolicy()).deterministic_hash == (
        without_consent.deterministic_hash
    )


@pytest.mark.unit
def test_unsupported_or_incomplete_policies_fail_closed() -> None:
    base = PersonInput(
        core_name="Y",
        birth_date=date(1990, 1, 1),
        as_of_date=date(2026, 7, 26),
    )
    with pytest.raises(PolicyError, match="user_fixed"):
        calculate_profile(base, MethodPolicy(y_mode=YMode.USER_FIXED))
    with pytest.raises(PolicyError, match="requires active_name"):
        calculate_profile(base, MethodPolicy(name_basis=NameBasis.ACTIVE_NAME_ONLY))


@pytest.mark.unit
def test_invalid_name_and_negative_number_fail_closed() -> None:
    with pytest.raises(NormalizationError, match="A-Z"):
        calculate_profile(
            PersonInput(
                core_name="---",
                birth_date=date(1990, 1, 1),
                as_of_date=date(2026, 7, 26),
            ),
            MethodPolicy(),
        )
    with pytest.raises(ValueError, match="must not be negative"):
        create_number("invalid", -1, policy=MethodPolicy())


@pytest.mark.unit
def test_isolated_y_is_reported_as_ambiguous() -> None:
    result = calculate_profile(
        PersonInput(
            core_name="Y",
            birth_date=date(1990, 1, 1),
            as_of_date=date(2026, 7, 26),
        ),
        MethodPolicy(),
    )
    assert result.trace.disambiguation_required is True
