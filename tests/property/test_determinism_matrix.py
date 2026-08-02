"""Mehrdimensionale Determinismus-Testmatrix — Issue #32.

Testet die vollständige Determinismus-Garantie des V2-Profils über:
* Gleicher Prozess (Wiederholungsaufrufe)
* Frische Subprozesse (via subprocess)
* Unterschiedliche PYTHONHASHSEED-Werte
* Unterschiedliche Testreihenfolgen
* model_dump-Vergleich, kanonisches JSON, SHA-256
* Canonicalization-Härtung (heterogene unordered collections)

Keine personenbezogenen Daten in den Fixtures.
"""

from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from typing import Any

import pytest

from numerology_domain.enums import UmlautPolicy
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.profile_v2 import calculate_profile_v2
from numerology_engine.trace import (
    _calculation_input_ref,
    _canonical_json,
    _canonicalize,
)

# ---------------------------------------------------------------------------
# Gemeinsame Test-Fixtures (keine personenbezogenen Daten)
# ---------------------------------------------------------------------------

# Kanonische Test-Personen (synthetische Namen)
_TEST_PERSON_A = PersonInput(
    core_name="Anna Test",
    birth_date=date(1990, 5, 15),
    as_of_date=date(2026, 8, 1),
)

_TEST_PERSON_B = PersonInput(
    core_name="Bruno Beispiel",
    birth_date=date(1982, 11, 3),
    as_of_date=date(2026, 8, 1),
)

_TEST_POLICY_DEFAULT = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)
_TEST_POLICY_DIRECT = MethodPolicy(
    version=PYTHAGOREAN_V2_VERSION, umlaut_policy=UmlautPolicy.DE_DIRECT_V1
)
_TEST_POLICY_EXPANDED = MethodPolicy(
    version=PYTHAGOREAN_V2_VERSION, umlaut_policy=UmlautPolicy.DE_EXPANDED_V1
)

# Alle Test-Konfigurationen
_TEST_CONFIGS: list[tuple[str, PersonInput, MethodPolicy]] = [
    ("anna_default", _TEST_PERSON_A, _TEST_POLICY_DEFAULT),
    ("anna_direct", _TEST_PERSON_A, _TEST_POLICY_DIRECT),
    ("anna_expanded", _TEST_PERSON_A, _TEST_POLICY_EXPANDED),
    ("bruno_default", _TEST_PERSON_B, _TEST_POLICY_DEFAULT),
    ("bruno_direct", _TEST_PERSON_B, _TEST_POLICY_DIRECT),
    ("bruno_expanded", _TEST_PERSON_B, _TEST_POLICY_EXPANDED),
]


# ---------------------------------------------------------------------------
# 3.2.1 — Gleicher Prozess: Wiederholungsaufrufe
# ---------------------------------------------------------------------------


class TestSameProcessDeterminism:
    """Determinismus innerhalb eines einzelnen Python-Prozesses."""

    @pytest.mark.parametrize("label,person,policy", _TEST_CONFIGS)
    def test_model_dump_identical(
        self, label: str, person: PersonInput, policy: MethodPolicy
    ) -> None:
        """model_dump(mode='json') muss für gleichen Input identisch sein."""
        r1 = calculate_profile_v2(person, policy)
        r2 = calculate_profile_v2(person, policy)

        dump1 = r1.model_dump(mode="json", exclude={"deterministic_hash"})
        dump2 = r2.model_dump(mode="json", exclude={"deterministic_hash"})

        assert dump1 == dump2, (
            f"[{label}] model_dump divergence detected\n"
            f"Keys in dump1: {sorted(dump1.keys())}\n"
            f"Keys in dump2: {sorted(dump2.keys())}"
        )

    @pytest.mark.parametrize("label,person,policy", _TEST_CONFIGS)
    def test_canonical_json_identical(
        self, label: str, person: PersonInput, policy: MethodPolicy
    ) -> None:
        """Kanonisches JSON muss identisch sein."""
        r1 = calculate_profile_v2(person, policy)
        r2 = calculate_profile_v2(person, policy)

        raw1 = r1.model_dump(mode="json", exclude={"deterministic_hash"})
        raw1["input_ref"] = _calculation_input_ref(r1.input_ref)
        c1 = _canonical_json(_canonicalize(raw1))  # type: ignore[arg-type]

        raw2 = r2.model_dump(mode="json", exclude={"deterministic_hash"})
        raw2["input_ref"] = _calculation_input_ref(r2.input_ref)
        c2 = _canonical_json(_canonicalize(raw2))  # type: ignore[arg-type]

        assert c1 == c2, f"[{label}] canonical JSON divergence (len1={len(c1)}, len2={len(c2)})"

    @pytest.mark.parametrize("label,person,policy", _TEST_CONFIGS)
    def test_sha256_identical(self, label: str, person: PersonInput, policy: MethodPolicy) -> None:
        """SHA-256 Hash muss identisch sein."""
        r1 = calculate_profile_v2(person, policy)
        r2 = calculate_profile_v2(person, policy)

        assert r1.deterministic_hash == r2.deterministic_hash, (
            f"[{label}] SHA-256 divergence: {r1.deterministic_hash} vs {r2.deterministic_hash}"
        )
        assert len(r1.deterministic_hash) == 64  # SHA-256 = 64 hex chars
        assert r1.deterministic_hash != ""

    @pytest.mark.parametrize("label,person,policy", _TEST_CONFIGS)
    def test_hash_envelope_identical(
        self, label: str, person: PersonInput, policy: MethodPolicy
    ) -> None:
        """Das kanonische Hash-Envelope muss identisch sein."""
        from numerology_engine.trace import deterministic_profile_hash_v4 as hash_fn

        r1 = calculate_profile_v2(person, policy)
        r2 = calculate_profile_v2(person, policy)

        h1 = hash_fn(r1)
        h2 = hash_fn(r2)

        assert h1 == h2, f"[{label}] hash_fn divergence: {h1} vs {h2}"
        assert h1 == r1.deterministic_hash
        assert h2 == r2.deterministic_hash

    def test_ten_iterations_same_result(self) -> None:
        """10 Wiederholungen mit derselben Person — alle identisch."""
        person = _TEST_PERSON_A
        policy = _TEST_POLICY_DEFAULT

        results = [calculate_profile_v2(person, policy) for _ in range(10)]
        first_hash = results[0].deterministic_hash

        for i, r in enumerate(results[1:], start=2):
            assert r.deterministic_hash == first_hash, (
                f"Iteration {i} divergiert von Iteration 1: {r.deterministic_hash} vs {first_hash}"
            )


# ---------------------------------------------------------------------------
# 3.2.2 — Frische Subprozesse (via subprocess)
# ---------------------------------------------------------------------------


_SUBPROCESS_SCRIPT = r"""
import json, os, sys
from datetime import date

# Path-Setup wie in conftest.py
_src = r"{src_path}"
if _src not in sys.path:
    sys.path.insert(0, _src)

from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile_v2 import calculate_profile_v2

person = PersonInput(
    core_name={core_name!r},
    birth_date=date({y}, {m}, {d}),
    as_of_date=date(2026, 8, 1),
)
policy = MethodPolicy(version="v2", umlaut_policy={umlaut!r})

result = calculate_profile_v2(person, policy)
dump = result.model_dump(mode="json", exclude={{"deterministic_hash"}})
canonical_json = json.dumps(dump, sort_keys=True, ensure_ascii=False)

output = {{
    "hash": result.deterministic_hash,
    "python_hash_seed": os.environ.get("PYTHONHASHSEED", "<not set>"),
    "canonical_json_sha256": __import__("hashlib").sha256(
        canonical_json.encode("utf-8")
    ).hexdigest(),
}}

print("SUBPROCESS_RESULT:" + json.dumps(output))
"""


def _run_subprocess(
    person: PersonInput,
    policy: MethodPolicy,
    *,
    python_hash_seed: str | None = None,
) -> dict[str, Any]:
    """Führt calculate_profile_v2 in einem frischen Subprozess aus."""
    src_path = Path(__file__).resolve().parent.parent.parent / "src"

    script = _SUBPROCESS_SCRIPT.format(
        src_path=str(src_path),
        core_name=person.core_name,
        y=person.birth_date.year,
        m=person.birth_date.month,
        d=person.birth_date.day,
        umlaut=policy.umlaut_policy.value,
    )

    env = os.environ.copy()
    if python_hash_seed is not None:
        env["PYTHONHASHSEED"] = python_hash_seed
    else:
        env.pop("PYTHONHASHSEED", None)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(script)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
            cwd=str(src_path.parent),
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"Subprocess failed (rc={proc.returncode}):\n"
                f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
            )

        for line in proc.stdout.splitlines():
            if line.startswith("SUBPROCESS_RESULT:"):
                payload = json.loads(line[len("SUBPROCESS_RESULT:") :])
                if not isinstance(payload, dict):
                    raise RuntimeError(f"Unexpected SUBPROCESS_RESULT type: {type(payload)!r}")
                return payload

        raise RuntimeError(f"No SUBPROCESS_RESULT in output:\n{proc.stdout}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


class TestSubprocessDeterminism:
    """Determinismus über separate Python-Prozesse hinweg."""

    @pytest.mark.slow
    def test_subprocess_same_result_as_main_process(self) -> None:
        """Subprozess-Ergebnis muss mit Hauptprozess übereinstimmen."""
        person = _TEST_PERSON_A
        policy = _TEST_POLICY_DEFAULT

        main_result = calculate_profile_v2(person, policy)
        sub_result = _run_subprocess(person, policy)

        assert main_result.deterministic_hash == sub_result["hash"], (
            f"Subprocess hash divergence:\n"
            f"  main: {main_result.deterministic_hash}\n"
            f"  sub:  {sub_result['hash']}\n"
            f"  sub PYTHONHASHSEED: {sub_result['python_hash_seed']}"
        )

    @pytest.mark.slow
    def test_two_subprocesses_same_result(self) -> None:
        """Zwei unabhängige Subprozesse — gleiches Ergebnis."""
        person = _TEST_PERSON_B
        policy = _TEST_POLICY_EXPANDED

        r1 = _run_subprocess(person, policy)
        r2 = _run_subprocess(person, policy)

        assert r1["hash"] == r2["hash"], f"Two subprocesses diverged: {r1['hash']} vs {r2['hash']}"
        assert r1["canonical_json_sha256"] == r2["canonical_json_sha256"]


# ---------------------------------------------------------------------------
# 3.2.3 — Unterschiedliche PYTHONHASHSEED-Werte
# ---------------------------------------------------------------------------


# Hash-Seeds zum Testen
_HASH_SEEDS = ["0", "1", "42", "123", "999", "random"]


class TestHashSeedDeterminism:
    """Determinismus bei unterschiedlichen PYTHONHASHSEED-Werten."""

    @pytest.mark.parametrize("hash_seed", _HASH_SEEDS)
    @pytest.mark.slow
    def test_hash_seed_no_effect_on_result(self, hash_seed: str) -> None:
        """PYTHONHASHSEED darf keinen Einfluss auf den Ergebnis-Hash haben."""
        person = _TEST_PERSON_A
        policy = _TEST_POLICY_DEFAULT

        # Hauptprozess-Referenz (ohne gesetzten PYTHONHASHSEED)
        main_result = calculate_profile_v2(person, policy)
        ref_hash = main_result.deterministic_hash

        # Subprozess mit spezifischem PYTHONHASHSEED
        sub_result = _run_subprocess(person, policy, python_hash_seed=hash_seed)

        assert sub_result["hash"] == ref_hash, (
            f"PYTHONHASHSEED={hash_seed} caused divergence:\n"
            f"  ref (unset):  {ref_hash}\n"
            f"  sub (seed={hash_seed}): {sub_result['hash']}"
        )

    def test_all_seeds_produce_same_hash_in_process(self) -> None:
        """Alle PYTHONHASHSEED-Werte im gleichen Prozess testen.

        Da der Seed nur beim Interpreter-Start wirkt, prüfen wir hier nur
        die Wiederholbarkeit innerhalb des laufenden Prozesses.
        """
        person = _TEST_PERSON_A
        policy = _TEST_POLICY_DEFAULT

        hashes = []
        for _ in range(20):
            r = calculate_profile_v2(person, policy)
            hashes.append(r.deterministic_hash)

        assert len(set(hashes)) == 1, (
            f"Hash divergence within same process across 20 iterations: "
            f"unique hashes: {sorted(set(hashes))}"
        )


# ---------------------------------------------------------------------------
# 3.2.4 — Unterschiedliche Testreihenfolgen (Collection Order)
# ---------------------------------------------------------------------------


class TestOrderingIndependence:
    """Der Hash ist unabhängig von der Testreihenfolge."""

    def test_reverse_order_same_result(self) -> None:
        """Umgekehrte Aufrufreihenfolge ändert nichts am Ergebnis."""
        # Erst B, dann A
        r_b1 = calculate_profile_v2(_TEST_PERSON_B, _TEST_POLICY_DEFAULT)
        r_a1 = calculate_profile_v2(_TEST_PERSON_A, _TEST_POLICY_DEFAULT)

        # Dann A, dann B (umgekehrte Reihenfolge)
        r_a2 = calculate_profile_v2(_TEST_PERSON_A, _TEST_POLICY_DEFAULT)
        r_b2 = calculate_profile_v2(_TEST_PERSON_B, _TEST_POLICY_DEFAULT)

        assert r_a1.deterministic_hash == r_a2.deterministic_hash
        assert r_b1.deterministic_hash == r_b2.deterministic_hash

    def test_interleaved_order_same_result(self) -> None:
        """Verschränkte Aufrufreihenfolge ändert nichts."""
        hashes_a: list[str] = []
        hashes_b: list[str] = []

        # Interleaved: A, B, B, A, A, B, A, B
        for _i in range(4):
            r_a = calculate_profile_v2(_TEST_PERSON_A, _TEST_POLICY_DEFAULT)
            hashes_a.append(r_a.deterministic_hash)
            r_b = calculate_profile_v2(_TEST_PERSON_B, _TEST_POLICY_EXPANDED)
            hashes_b.append(r_b.deterministic_hash)

        assert len(set(hashes_a)) == 1, f"Person A hashes diverged: {hashes_a}"
        assert len(set(hashes_b)) == 1, f"Person B hashes diverged: {hashes_b}"

    def test_many_random_order_calls(self) -> None:
        """50 zufällig durchmischte Aufrufe — alle konsistent."""
        import random

        rng = random.Random(42)  # Fester Seed für Reproduzierbarkeit
        persons = [_TEST_PERSON_A, _TEST_PERSON_B]
        policies = [_TEST_POLICY_DEFAULT, _TEST_POLICY_DIRECT, _TEST_POLICY_EXPANDED]

        ref_hashes: dict[tuple[str, str], str] = {}
        for _ in range(50):
            person = rng.choice(persons)
            policy = rng.choice(policies)
            key = (person.core_name, policy.umlaut_policy.value)

            r = calculate_profile_v2(person, policy)
            if key not in ref_hashes:
                ref_hashes[key] = r.deterministic_hash
            else:
                assert r.deterministic_hash == ref_hashes[key], (
                    f"Hash divergence for {key}: {r.deterministic_hash} vs ref {ref_hashes[key]}"
                )


# ---------------------------------------------------------------------------
# 3.2.5 — Sonderfälle: Umlaute, Leerzeichen, Sonderzeichen
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Determinismus bei Edge-Case-Namen."""

    @pytest.mark.parametrize(
        "core_name,description",
        [
            ("Jürgen Müller", "Umlaute im Namen"),
            ("René Élise", "Französische Akzente"),
            ("Anna Maria", "Doppelname mit Leerzeichen"),
            ("ABC", "Minimalname (3 Buchstaben)"),
            ("Z", "Einbuchstabiger Name"),
            ("X Y Z", "Nur Initialen"),
        ],
    )
    def test_special_names_deterministic(self, core_name: str, description: str) -> None:
        """Spezielle Namen müssen deterministisch sein."""
        person = PersonInput(
            core_name=core_name,
            birth_date=date(1985, 7, 25),
            as_of_date=date(2026, 8, 1),
        )
        policy = _TEST_POLICY_EXPANDED  # expanded für Umlaut-Test

        r1 = calculate_profile_v2(person, policy)
        r2 = calculate_profile_v2(person, policy)

        assert r1.deterministic_hash == r2.deterministic_hash, (
            f"[{description}] Hash divergence for '{core_name}'"
        )


# ---------------------------------------------------------------------------
# 3.2.6 — Canonicalization-Härtung (Issue #32, reproduzierbarer Gegenbeweis)
# ---------------------------------------------------------------------------


class TestCanonicalizationHardening:
    """Heterogene unordered collections dürfen die Canonicalization nicht crashen.

    Reproduzierbarer Gegenbeweis (konstruiert am 2026-08-02):
    ``sorted({1, 'a', 2.5})`` wirft ``TypeError: '<' not supported between
    instances of 'str' and 'float'``. Die Härtung überführt jedes Element
    zuerst in kanonisches JSON und sortiert dann nach der JSON-Repräsentation.
    """

    def test_heterogeneous_set_does_not_crash(self) -> None:
        """Heterogenes Set (int/str/float) darf keinen TypeError werfen."""
        result = _canonicalize({1, "a", 2.5})
        assert isinstance(result, list)
        assert len(result) == 3
        # Sortierung nach kanonischer JSON-Repräsentation (lexikographisch):
        # '"a"' (0x22) < '1' (0x31) < '2.5' (0x32)
        assert result == ["a", 1, 2.5]

    def test_heterogeneous_frozenset_does_not_crash(self) -> None:
        """Heterogenes frozenset (bool/str/int) darf keinen TypeError werfen."""
        result = _canonicalize(frozenset({True, "x", 3}))
        assert isinstance(result, list)
        assert len(result) == 3
        # JSON-Repräsentationen: '"x"' < '3' < 'true' → sortiert: "x", 3, True
        assert result == ["x", 3, True]

    def test_nested_heterogeneous_set_in_dict(self) -> None:
        """Verschachteltes heterogenes Set in einem dict darf nicht crashen."""
        payload = {"values": {1, "b", 3.5}, "name": "test"}
        result = _canonicalize(payload)
        assert isinstance(result, dict)
        # '"b"' < '1' < '3.5' → sortiert: "b", 1, 3.5
        assert result["values"] == ["b", 1, 3.5]
        assert result["name"] == "test"

    def test_homogeneous_set_still_sorted(self) -> None:
        """Homogene Sets bleiben korrekt sortiert (keine Regression)."""
        result = _canonicalize({3, 1, 2})
        assert result == [1, 2, 3]

    def test_set_of_tuples_sorted_by_json(self) -> None:
        """Sets aus Tupeln werden nach kanonischer JSON-Repräsentation sortiert."""
        result = _canonicalize({(2, "b"), (1, "a")})
        assert isinstance(result, list)
        # JSON-Repräsentationen: "[1,\"a\"]" < "[2,\"b\"]"
        assert result == [[1, "a"], [2, "b"]]

    def test_canonical_json_stable_for_heterogeneous_sets(self) -> None:
        """Kanonisches JSON ist für heterogene Sets deterministisch."""
        c1 = _canonical_json(_canonicalize({1, "a", 2.5}))  # type: ignore[arg-type]
        c2 = _canonical_json(_canonicalize({"a", 2.5, 1}))  # type: ignore[arg-type]
        assert c1 == c2


# ---------------------------------------------------------------------------
# 3.2.7 — Environment Context Capture (für Diagnose)
# ---------------------------------------------------------------------------


def test_environment_snapshot() -> None:
    """Erfasst die aktuelle Umgebung als Referenz für die Untersuchung."""
    snapshot = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "python_hash_seed": os.environ.get("PYTHONHASHSEED", "<not set>"),
        "test_file": __file__,
        "timestamp_utc": date.today().isoformat(),
    }

    # Validiere, dass die Snapshot-Struktur konsistent ist
    assert "python_version" in snapshot
    assert "platform" in snapshot
    assert "python_hash_seed" in snapshot

    # Schreibe Snapshot nur wenn explizit per CLI gewünscht
    if os.environ.get("DETERMINISM_WRITE_SNAPSHOT") == "1":
        snapshot_path = Path(__file__).parent / "determinism_snapshot.json"
        snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
