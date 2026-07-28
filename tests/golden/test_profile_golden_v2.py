"""Golden-Case-Tests gegen reference_profiles_v2.yaml (PR #19).

Jede Assertion hier prüft einen pinned Referenzwert, der aus dem manuell
verifizierten Referenzkorpus stammt. Änderungen an diesen Werten sind
Vertragsbrüche, keine Refactorings.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from numerology_domain.enums import UmlautPolicy
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.profile_v2 import calculate_profile_v2

_CORPUS_PATH = Path(__file__).parent / "reference_profiles_v2.yaml"


def _load_corpus() -> list[dict[str, Any]]:
    data: dict[str, Any] = yaml.safe_load(_CORPUS_PATH.read_text(encoding="utf-8"))
    return list(data["profiles"])


_PROFILES = _load_corpus()


def _profile_by_id(pid: str) -> dict[str, Any]:
    for p in _PROFILES:
        if p["id"] == pid:
            return p
    raise KeyError(f"profile {pid!r} not found in corpus")


def _compute(core_name: str, birth_date: str, as_of_date: str) -> Any:
    policy = MethodPolicy(
        version=PYTHAGOREAN_V2_VERSION,
        umlaut_policy=UmlautPolicy.DE_EXPANDED_V1,
    )
    person = PersonInput(
        core_name=core_name,
        birth_date=date.fromisoformat(birth_date),
        as_of_date=date.fromisoformat(as_of_date),
    )
    return calculate_profile_v2(person, policy)


# ---------------------------------------------------------------------------
# Lukas Springer
# ---------------------------------------------------------------------------


@pytest.mark.golden
def test_lukas_springer_life_path_primary():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.life_path_primary.display_notation == "40/4"
    assert p.life_path_primary.root_value == 4
    assert not p.life_path_primary.is_master


@pytest.mark.golden
def test_lukas_springer_life_path_secondary():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.life_path_secondary.display_notation == "22/4"
    assert p.life_path_secondary.root_value == 4
    assert p.life_path_secondary.is_master
    assert p.life_path_secondary.held_master_value == 22


@pytest.mark.golden
def test_lukas_springer_birthday():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.birthday.display_notation == "18/9"
    assert p.birthday.root_value == 9


@pytest.mark.golden
def test_lukas_springer_attitude():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.attitude.display_notation == "25/7"


@pytest.mark.golden
def test_lukas_springer_expression():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.expression.display_notation == "62/8"
    assert not p.core_name.expression.is_master


@pytest.mark.golden
def test_lukas_springer_personality_not_master():
    """44/8 must NOT be classified as a master number."""
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.personality.display_notation == "44/8"
    assert not p.core_name.personality.is_master
    assert p.core_name.personality.held_master_value is None


@pytest.mark.golden
def test_lukas_springer_soul_urge():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.soul_urge.display_notation == "18/9"


@pytest.mark.golden
def test_lukas_springer_maturity():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.maturity.display_notation == "12/3"


@pytest.mark.golden
def test_lukas_springer_personal_year_2026():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    assert p.cycles.personal_year.display_notation == "17/8"


@pytest.mark.golden
def test_lukas_springer_pinnacles():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    notations = [pp.display_notation for pp in p.cycles.pinnacles]
    assert notations == ["16/7", "15/6", "13/4", "13/4"]


@pytest.mark.golden
def test_lukas_springer_challenges():
    p = _compute("Lukas Springer", "1986-07-18", "2026-07-28")
    roots = [c.root_value for c in p.cycles.challenges]
    assert roots == [2, 3, 1, 1]


# ---------------------------------------------------------------------------
# Stella Jane Witt
# ---------------------------------------------------------------------------


@pytest.mark.golden
def test_stella_witt_life_path():
    p = _compute("Stella Jane Witt", "2011-04-18", "2026-07-28")
    assert p.life_path_primary.display_notation == "17/8"
    assert p.life_path_secondary.display_notation == "17/8"


@pytest.mark.golden
def test_stella_witt_attitude_master():
    p = _compute("Stella Jane Witt", "2011-04-18", "2026-07-28")
    assert p.attitude.display_notation == "22/4"
    assert p.attitude.is_master
    assert p.attitude.held_master_value == 22


@pytest.mark.golden
def test_stella_witt_expression():
    p = _compute("Stella Jane Witt", "2011-04-18", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.expression.display_notation == "45/9"
    assert p.core_name.soul_urge.display_notation == "21/3"
    assert p.core_name.personality.display_notation == "24/6"
    assert p.core_name.maturity.display_notation == "17/8"


@pytest.mark.golden
def test_stella_witt_personal_year():
    p = _compute("Stella Jane Witt", "2011-04-18", "2026-07-28")
    assert p.cycles.personal_year.display_notation == "14/5"


# ---------------------------------------------------------------------------
# Antoney Newton — Y=Vokal via phonetische Regel
# ---------------------------------------------------------------------------


@pytest.mark.golden
def test_antoney_newton_life_path_primary():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.life_path_primary.display_notation == "31/4"
    assert not p.life_path_primary.is_master


@pytest.mark.golden
def test_antoney_newton_life_path_secondary_karmic():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.life_path_secondary.display_notation == "13/4"
    karmic = p.life_path_secondary.karmic_occurrences
    assert len(karmic) == 1
    assert karmic[0].value == 13
    assert karmic[0].origin_type == "component_total"


@pytest.mark.golden
def test_antoney_newton_expression_karmic_intermediate():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.expression.display_notation == "59/14/5"
    karmic = p.core_name.expression.karmic_occurrences
    assert len(karmic) == 1
    assert karmic[0].value == 14
    assert karmic[0].origin_type == "reduction_intermediate"


@pytest.mark.golden
def test_antoney_newton_soul_y_as_vowel():
    """Y at end of ANTONEY is classified vowel by phonetic rule."""
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.soul_urge.display_notation == "30/3"


@pytest.mark.golden
def test_antoney_newton_personality_master():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.personality.display_notation == "29/11/2"
    assert p.core_name.personality.is_master
    assert p.core_name.personality.held_master_value == 11


@pytest.mark.golden
def test_antoney_newton_maturity():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.maturity.display_notation == "9"
    assert p.core_name.maturity.root_value == 9


@pytest.mark.golden
def test_antoney_newton_personal_year():
    p = _compute("Antoney Newton", "1995-10-15", "2026-07-28")
    assert p.cycles.personal_year.display_notation == "8"


# ---------------------------------------------------------------------------
# Sina Langner — Geburtstag 11 = Meisterzahl
# ---------------------------------------------------------------------------


@pytest.mark.golden
def test_sina_langner_life_paths():
    p = _compute("Sina Langner", "1992-12-11", "2026-07-28")
    assert p.life_path_primary.display_notation == "26/8"
    assert p.life_path_secondary.display_notation == "17/8"


@pytest.mark.golden
def test_sina_langner_birthday_master():
    p = _compute("Sina Langner", "1992-12-11", "2026-07-28")
    assert p.birthday.display_notation == "11/2"
    assert p.birthday.is_master
    assert p.birthday.held_master_value == 11


@pytest.mark.golden
def test_sina_langner_name_numbers():
    p = _compute("Sina Langner", "1992-12-11", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.expression.display_notation == "51/6"
    assert p.core_name.soul_urge.display_notation == "16/7"
    assert p.core_name.personality.display_notation == "35/8"
    assert p.core_name.maturity.display_notation == "14/5"


@pytest.mark.golden
def test_sina_langner_personal_year():
    p = _compute("Sina Langner", "1992-12-11", "2026-07-28")
    assert p.cycles.personal_year.display_notation == "15/6"


# ---------------------------------------------------------------------------
# Stefanie Scheulen — karmische Geburtstag, karmisches Ausdruck, Seele=Master
# ---------------------------------------------------------------------------


@pytest.mark.golden
def test_stefanie_scheulen_life_paths():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.life_path_primary.display_notation == "30/3"
    assert p.life_path_secondary.display_notation == "12/3"


@pytest.mark.golden
def test_stefanie_scheulen_birthday_karmic():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.birthday.display_notation == "16/7"
    karmic = p.birthday.karmic_occurrences
    assert len(karmic) == 1
    assert karmic[0].value == 16
    assert karmic[0].origin_type == "direct_raw"


@pytest.mark.golden
def test_stefanie_scheulen_expression_karmic():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.expression.display_notation == "67/13/4"
    karmic = p.core_name.expression.karmic_occurrences
    assert len(karmic) == 1
    assert karmic[0].value == 13
    assert karmic[0].origin_type == "reduction_intermediate"


@pytest.mark.golden
def test_stefanie_scheulen_soul_master():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.soul_urge.display_notation == "33/6"
    assert p.core_name.soul_urge.is_master
    assert p.core_name.soul_urge.held_master_value == 33


@pytest.mark.golden
def test_stefanie_scheulen_maturity():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.core_name is not None
    assert p.core_name.maturity.display_notation == "7"


@pytest.mark.golden
def test_stefanie_scheulen_personal_year():
    p = _compute("Stefanie Scheulen", "1981-04-16", "2026-07-28")
    assert p.cycles.personal_year.display_notation == "12/3"
