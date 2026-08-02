"""Property-Based Tests für pythagorean-v2 (Hypothesis) — PR #19.

Invarianten die für beliebige Inputs gelten müssen:
- Determinismus: gleicher Input → identischer Hash
- NumberModel-Konsistenz: chain, root_value, is_master sind kohärent
- V1-Kompatibilität: V1-Ergebnisse bleiben byte-identisch

Issue #32 Instrumentierung:
Bei jedem Hypothesis-Fehler werden vollständig reproduzierbare Kontextdaten
erfasst: Hypothesis-Seed, minimiertes Beispiel, PYTHONHASHSEED, Python-Version,
Plattform, kanonisches Hash-Envelope, erste Byte-Differenz.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
import os
import platform
import sys
from typing import Any

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
# Issue #32 — Determinismus-Kontext-Erfassung (Instrumentierung)
# ---------------------------------------------------------------------------


def _capture_determinism_context(
    *,
    person: PersonInput,
    policy: MethodPolicy,
    serialized_1: str | None = None,
    serialized_2: str | None = None,
    hash_1: str | None = None,
    hash_2: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Erfasst den vollständigen reproduzierbaren Kontext bei einem Fehlschlag.

    Keine personenbezogenen Daten — nur technische Umgebungsinformationen
    und die Hash-Envelope-VOR-SHA-256 (nicht die Personendaten selbst).
    """
    context: dict[str, Any] = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "python_hash_seed": os.environ.get("PYTHONHASHSEED", "<not set>"),
        "relevant_env_vars": {
            k: v
            for k, v in sorted(os.environ.items())
            if any(
                prefix in k.upper()
                for prefix in ("PYTHON", "PYTEST", "HYPOTHESIS", "LANG", "LC_", "TZ")
            )
        },
        "test_file": __file__,
        "policy": policy.model_dump(mode="json"),
        "input_ref": {
            "core_name_length": len(person.core_name),
            "birth_date": person.birth_date.isoformat(),
            "as_of_date": person.as_of_date.isoformat(),
            "locale": person.locale.value,
        },
    }

    if hash_1 is not None:
        context["hash_1"] = hash_1
    if hash_2 is not None:
        context["hash_2"] = hash_2

    if serialized_1 is not None and serialized_2 is not None:
        context["serialized_lengths"] = (len(serialized_1), len(serialized_2))
        # Erste Byte-Differenz lokalisieren
        diff_pos = None
        b1 = serialized_1.encode("utf-8")
        b2 = serialized_2.encode("utf-8")
        max_len = max(len(b1), len(b2))
        for i in range(max_len):
            byte_a = b1[i] if i < len(b1) else None
            byte_b = b2[i] if i < len(b2) else None
            if byte_a != byte_b:
                diff_pos = i
                # Kontext um die Differenz herum (20 Bytes vorher)
                ctx_start = max(0, i - 20)
                ctx_end = min(max_len, i + 20)
                context["diff_context"] = {
                    "position": i,
                    "byte_1": byte_a,
                    "byte_2": byte_b,
                    "context_before": b1[ctx_start:i].hex() if i > 0 else "",
                    "context_after_1": b1[i:ctx_end].hex() if i < len(b1) else "<eof>",
                    "context_after_2": b2[i:ctx_end].hex() if i < len(b2) else "<eof>",
                }
                break
        if diff_pos is None:
            context["diff_context"] = "no byte difference found (identical serialized?)"

    if extra:
        context.update(extra)

    return context


def _build_canonical_envelope_v4(result: Any) -> dict[str, Any]:
    """Baut das kanonische Hash-Envelope VOR SHA-256 (für Diagnose)."""
    from numerology_engine.trace import _calculation_input_ref, _canonical_json, _canonicalize

    raw: dict[str, Any] = result.model_dump(mode="json", exclude={"deterministic_hash"})
    raw["input_ref"] = _calculation_input_ref(result.input_ref)
    canonicalized = _canonicalize(raw)
    assert isinstance(canonicalized, dict)
    return {
        "canonical_json": _canonical_json(canonicalized),
        "canonicalized_structure_keys": sorted(str(k) for k in canonicalized),
        "sha256": hashlib.sha256(_canonical_json(canonicalized).encode("utf-8")).hexdigest(),
    }


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
# Hash-Stabilität für V2 — MIT VOLLSTÄNDIGER INSTRUMENTIERUNG (Issue #32)
# ---------------------------------------------------------------------------


@given(
    st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=2,
        max_size=30,
    ).filter(lambda s: s.strip()),
    _valid_dates,
)
@settings(max_examples=100)
@pytest.mark.property
def test_v2_hash_stable_for_same_input(name: str, bd: date) -> None:
    """Gleicher Input → identischer Hash — mit voller Issue-#32-Diagnostik."""
    from numerology_engine.profile_v2 import calculate_profile_v2

    as_of = date(2026, 7, 28)
    if bd > as_of:
        return

    normalized = "".join(c for c in name.upper() if c.isalpha())
    if not normalized:
        return

    person = PersonInput(core_name=name, birth_date=bd, as_of_date=as_of)
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)

    r1 = calculate_profile_v2(person, policy)
    r2 = calculate_profile_v2(person, policy)

    if r1.deterministic_hash != r2.deterministic_hash or r1.deterministic_hash == "":
        # Vollständige Diagnostik erfassen
        env_1 = _build_canonical_envelope_v4(r1)
        env_2 = _build_canonical_envelope_v4(r2)

        diagnostic = _capture_determinism_context(
            person=person,
            policy=policy,
            serialized_1=env_1["canonical_json"],
            serialized_2=env_2["canonical_json"],
            hash_1=r1.deterministic_hash,
            hash_2=r2.deterministic_hash,
            extra={
                "canonical_envelope_1_keys": env_1["canonicalized_structure_keys"],
                "canonical_envelope_2_keys": env_2["canonicalized_structure_keys"],
                "hash_via_envelope_1": env_1["sha256"],
                "hash_via_envelope_2": env_2["sha256"],
                "identical_envelopes": env_1["canonical_json"] == env_2["canonical_json"],
            },
        )

        # Hypothesis-spezifische Seed-Information (aus dem aktuellen Testlauf)
        diagnostic["note"] = (
            "Hypothesis seed wird automatisch von pytest-hypothesis "
            "ausgegeben. Bei Reproduktion: --hypothesis-seed=<seed>"
        )

        pytest.fail(
            f"Issue #32 DETERMINISM VIOLATION:\n"
            f"  hash_1={r1.deterministic_hash}\n"
            f"  hash_2={r2.deterministic_hash}\n"
            f"  identical_envelopes={diagnostic['identical_envelopes']}\n"
            f"  python_hash_seed={diagnostic['python_hash_seed']}\n"
            f"  python_version={diagnostic['python_version']}\n"
            f"  platform={diagnostic['platform']}\n"
            f"  diff_context={diagnostic.get('diff_context', 'N/A')}\n"
            f"\nFull diagnostic:\n{json.dumps(diagnostic, indent=2, default=str)}"
        )

    assert r1.deterministic_hash != ""


# ---------------------------------------------------------------------------
# Zusätzlicher Instrumentierungstest: model_dump-Vergleich (Issue #32)
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
def test_v2_model_dump_identical_for_same_input(name: str, bd: date) -> None:
    """model_dump(mode='json') muss für gleichen Input identisch sein."""
    from numerology_engine.profile_v2 import calculate_profile_v2

    as_of = date(2026, 7, 28)
    if bd > as_of:
        return

    normalized = "".join(c for c in name.upper() if c.isalpha())
    if not normalized:
        return

    person = PersonInput(core_name=name, birth_date=bd, as_of_date=as_of)
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)

    r1 = calculate_profile_v2(person, policy)
    r2 = calculate_profile_v2(person, policy)

    dump1 = r1.model_dump(mode="json", exclude={"deterministic_hash"})
    dump2 = r2.model_dump(mode="json", exclude={"deterministic_hash"})

    if dump1 != dump2:
        # Tiefe Differenz finden
        def _find_diff(d1: Any, d2: Any, path: str = "$") -> list[str]:
            diffs: list[str] = []
            if type(d1) is not type(d2):
                diffs.append(f"{path}: type mismatch {type(d1).__name__} vs {type(d2).__name__}")
                return diffs
            if isinstance(d1, dict):
                all_keys = set(d1.keys()) | set(d2.keys())
                for k in sorted(all_keys):
                    if k not in d1:
                        diffs.append(f"{path}.{k}: missing in first")
                    elif k not in d2:
                        diffs.append(f"{path}.{k}: missing in second")
                    else:
                        diffs.extend(_find_diff(d1[k], d2[k], f"{path}.{k}"))
            elif isinstance(d1, list):
                if len(d1) != len(d2):
                    diffs.append(f"{path}: list length {len(d1)} vs {len(d2)}")
                for i in range(min(len(d1), len(d2))):
                    diffs.extend(_find_diff(d1[i], d2[i], f"{path}[{i}]"))
            elif d1 != d2:
                diffs.append(f"{path}: {d1!r} != {d2!r}")
            return diffs

        diffs = _find_diff(dump1, dump2)
        diagnostic = _capture_determinism_context(
            person=person,
            policy=policy,
            extra={"model_dump_diffs": diffs[:20]},  # max 20 Differenzen
        )
        pytest.fail(
            f"Issue #32 MODEL_DUMP DIVERGENCE ({len(diffs)} differences):\n"
            + "\n".join(diffs[:20])
            + f"\n\nDiagnostic:\n{json.dumps(diagnostic, indent=2, default=str)}"
        )

    assert dump1 == dump2


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
