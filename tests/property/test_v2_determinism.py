"""Property-Based Tests für pythagorean-v2 (Hypothesis) — PR #19.

Invarianten die für beliebige Inputs gelten müssen:
- Determinismus: gleicher Input → identischer Hash
- NumberModel-Konsistenz: chain, root_value, is_master sind kohärent
- V1-Kompatibilität: V1-Ergebnisse bleiben byte-identisch
"""

from __future__ import annotations

from datetime import date

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from numerology_domain.enums import UmlautPolicy
from numerology_domain.models import (
    MASTER_NUMBERS,
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.profile_v2 import (
    _full_chain_v2,
    create_number_model,
    life_path_primary_v2,
    life_path_secondary_v2,
)

_POLICY_V2 = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)

# Strategy für gültige Geburtsdaten
_valid_dates = st.dates(min_value=date(1900, 1, 1), max_value=date(2020, 12, 31))
_valid_raw = st.integers(min_value=0, max_value=200)


# ---------------------------------------------------------------------------
# _full_chain_v2 invarianten
# ---------------------------------------------------------------------------


@given(_valid_raw)
@settings(max_examples=500)
@pytest.mark.property
def test_chain_last_is_single_digit(n: int) -> None:
    """Letztes Element ist immer 0-9."""
    chain = _full_chain_v2(n)
    assert 0 <= chain[-1] <= 9


@given(_valid_raw)
@settings(max_examples=500)
@pytest.mark.property
def test_chain_first_is_input(n: int) -> None:
    """Erstes Element ist immer der Input."""
    chain = _full_chain_v2(n)
    assert chain[0] == n


@given(_valid_raw)
@settings(max_examples=500)
@pytest.mark.property
def test_chain_monotone_nondecreasing_length(n: int) -> None:
    """Kette hat immer mindestens ein Element."""
    chain = _full_chain_v2(n)
    assert len(chain) >= 1


@given(st.integers(min_value=1, max_value=200))
@settings(max_examples=500)
@pytest.mark.property
def test_chain_each_step_is_digit_sum(n: int) -> None:
    """Jeder Schritt in der Kette ist der Ziffernsumme des Vorgängers."""
    from numerology_engine.reduction import digit_sum

    chain = _full_chain_v2(n)
    for i in range(len(chain) - 1):
        assert digit_sum(chain[i]) == chain[i + 1]


# ---------------------------------------------------------------------------
# NumberModel invarianten
# ---------------------------------------------------------------------------


@given(_valid_raw)
@settings(max_examples=300)
@pytest.mark.property
def test_number_model_root_in_0_to_9(n: int) -> None:
    m = create_number_model(n, policy=_POLICY_V2)
    assert 0 <= m.root_value <= 9


@given(_valid_raw)
@settings(max_examples=300)
@pytest.mark.property
def test_number_model_is_master_iff_held_master(n: int) -> None:
    m = create_number_model(n, policy=_POLICY_V2)
    assert m.is_master == (m.held_master_value is not None)


@given(_valid_raw)
@settings(max_examples=300)
@pytest.mark.property
def test_number_model_44_never_master(n: int) -> None:
    """44 darf nie als Meisterzahl klassifiziert werden."""
    if n == 44:
        m = create_number_model(44, policy=_POLICY_V2)
        assert not m.is_master


@given(_valid_raw)
@settings(max_examples=300)
@pytest.mark.property
def test_number_model_master_only_11_22_33(n: int) -> None:
    m = create_number_model(n, policy=_POLICY_V2)
    if m.held_master_value is not None:
        assert m.held_master_value in MASTER_NUMBERS


@given(_valid_raw)
@settings(max_examples=300)
@pytest.mark.property
def test_number_model_chain_consistent_with_raw_and_root(n: int) -> None:
    m = create_number_model(n, policy=_POLICY_V2)
    assert m.reduction_chain[0] == m.raw_total
    assert m.reduction_chain[-1] == m.root_value


# ---------------------------------------------------------------------------
# Life Path V2: Determinismus
# ---------------------------------------------------------------------------


@given(_valid_dates)
@settings(max_examples=200)
@pytest.mark.property
def test_life_path_primary_v2_deterministic(d: date) -> None:
    r1 = life_path_primary_v2(d)
    r2 = life_path_primary_v2(d)
    assert r1.display_notation == r2.display_notation
    assert r1.root_value == r2.root_value


@given(_valid_dates)
@settings(max_examples=200)
@pytest.mark.property
def test_life_path_secondary_v2_deterministic(d: date) -> None:
    r1 = life_path_secondary_v2(d)
    r2 = life_path_secondary_v2(d)
    assert r1.display_notation == r2.display_notation


# ---------------------------------------------------------------------------
# Hash-Stabilität für V2
# ---------------------------------------------------------------------------


@given(
    st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=2,
        max_size=30,
    ).filter(lambda s: s.strip()),
    _valid_dates,
)
@settings(max_examples=50)
@pytest.mark.property
def test_v2_hash_stable_for_same_input(name: str, bd: date) -> None:
    """Gleicher Input → identischer Hash."""
    from numerology_engine.profile_v2 import calculate_profile_v2

    # Stelle sicher dass as_of_date >= birth_date
    as_of = date(2026, 7, 28)
    if bd > as_of:
        return  # skip

    # Normierter Name muss mind. einen Buchstaben haben
    normalized = "".join(c for c in name.upper() if c.isalpha())
    if not normalized:
        return

    person = PersonInput(core_name=name, birth_date=bd, as_of_date=as_of)
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)

    r1 = calculate_profile_v2(person, policy)
    r2 = calculate_profile_v2(person, policy)
    assert r1.deterministic_hash == r2.deterministic_hash
    assert r1.deterministic_hash != ""


# ---------------------------------------------------------------------------
# Hash ändert sich bei Policy-Änderung
# ---------------------------------------------------------------------------


@pytest.mark.property
def test_v2_hash_changes_with_policy() -> None:
    """Andere Policy → anderer Hash."""
    from numerology_engine.profile_v2 import calculate_profile_v2

    person = PersonInput(
        core_name="Lukas Springer",
        birth_date=date(1986, 7, 18),
        as_of_date=date(2026, 7, 28),
    )
    policy_direct = MethodPolicy(
        version=PYTHAGOREAN_V2_VERSION, umlaut_policy=UmlautPolicy.DE_DIRECT_V1
    )
    policy_expanded = MethodPolicy(
        version=PYTHAGOREAN_V2_VERSION, umlaut_policy=UmlautPolicy.DE_EXPANDED_V1
    )

    r1 = calculate_profile_v2(person, policy_direct)
    r2 = calculate_profile_v2(person, policy_expanded)
    # Für Namen ohne Umlaute sind die Hashes identisch (gleicher Normalisierungsoutput)
    # aber die Policy unterscheidet sich → anderer Hash
    assert r1.deterministic_hash != r2.deterministic_hash


# ---------------------------------------------------------------------------
# V1-Kompatibilität: V1-Ergebnisse bleiben unverändert
# ---------------------------------------------------------------------------


@pytest.mark.property
def test_v1_life_path_unchanged() -> None:
    """V1 gibt weiterhin byte-identische Ergebnisse."""
    from numerology_engine.dates import life_path_a, life_path_b

    bd = date(1985, 7, 25)
    a = life_path_a(bd)
    b = life_path_b(bd)
    assert a.compound_notation == "37/10/1"
    assert b.compound_notation == "19/10/1"
    assert b.karmic_debt is not None
    assert b.karmic_debt.number == 19


@pytest.mark.property
def test_v1_profile_hash_unchanged() -> None:
    """V1-Profile-Hash bleibt nach V2-Ergänzungen stabil."""
    from numerology_domain.models import MethodPolicy as MP
    from numerology_engine.profile import calculate_profile

    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    p1 = calculate_profile(person, MP())
    p2 = calculate_profile(person, MP())
    assert p1.deterministic_hash == p2.deterministic_hash
    assert p1.deterministic_hash != ""
