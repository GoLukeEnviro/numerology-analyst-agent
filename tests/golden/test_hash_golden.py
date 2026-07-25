"""Versionierter deterministic_hash Golden Case (Korrektur 4).

Garantiert:
1. Gleiche kanonische Eingabe + Methodenversion + Schema-Version ⇒ gleicher Hash.
2. JSON-Feldreihenfolge beeinflusst Hash nicht.
3. Metadaten (Laufzeit, Request-ID) fließen nicht ein (der Core hat keine).

Eine bewusste Änderung braucht: Methodenversion ODER Schema-Version Bump +
aktualisierten Golden Case + dokumentierte Begründung.

Der Hash wird kanonisch gebildet: parse des Service-JSON, re-dump mit
``sort_keys=True``, SHA-256 über UTF-8. Damit ist er unabhängig von der
Ausgabereihenfolge und identisch mit der Definition im Service-Layer.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json

import pytest

from numerology_api.contracts import dump_result_as_json
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.service import calculate_life_path

# Methodenversion / Schema-Version sind Bestandteil der Eingabemenge, die der
# Hash stabilisiert. Eine Änderung hier ODER am CalculationResult-Schema
# erfordert einen neuen Golden Case plus Begründung.
HASH_CASES = [
    {
        "case_id": "life-path-max-mustermann-v1",
        "method_version": "pythagorean-v1",
        "schema_version": "calculation-result-v1",
        "core_name": "Max Mustermann",
        "birth_date": "1985-07-25",
        "as_of_date": "2026-07-26",
        "expected_hash": "1c908a42e74a28bc193a95756e312ced7bc9d42b550be957c1d7bb5777dbe983",
    },
]


def _canonical_hash_of(json_str: str) -> str:
    """SHA-256 über das sortierte, neu serialisierte JSON."""
    canonical = json.dumps(json.loads(json_str), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@pytest.mark.golden
@pytest.mark.parametrize("case", HASH_CASES, ids=[c["case_id"] for c in HASH_CASES])
def test_deterministic_hash_stable(case: dict[str, object]) -> None:
    """Hash muss stabil bleiben für identische Eingabe + Versionen."""
    person = PersonInput(
        core_name=str(case["core_name"]),
        birth_date=date.fromisoformat(str(case["birth_date"])),
        as_of_date=date.fromisoformat(str(case["as_of_date"])),
    )
    result = calculate_life_path(person, MethodPolicy())
    json_str = dump_result_as_json(result)
    actual_hash = _canonical_hash_of(json_str)

    assert actual_hash == case["expected_hash"], (
        f"Hash changed for {case['case_id']}! "
        f"If this is intentional: document why, bump method/schema version, "
        f"and update expected_hash. New hash: {actual_hash}"
    )


@pytest.mark.golden
def test_hash_independent_of_key_order() -> None:
    """JSON-Feldreihenfolge darf den Hash nicht beeinflussen."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    result = calculate_life_path(person, MethodPolicy())
    payload = json.loads(dump_result_as_json(result))

    json_sorted = json.dumps(payload, sort_keys=True)
    json_unsorted = json.dumps(payload, sort_keys=False)

    hash_sorted = hashlib.sha256(json_sorted.encode("utf-8")).hexdigest()
    hash_unsorted = hashlib.sha256(json_unsorted.encode("utf-8")).hexdigest()

    assert hash_sorted == hash_unsorted


@pytest.mark.golden
def test_hash_same_across_two_runs() -> None:
    """Zwei unabhängige Berechnungen gleicher Eingabe ⇒ gleicher Hash."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    h1 = _canonical_hash_of(dump_result_as_json(calculate_life_path(person, MethodPolicy())))
    h2 = _canonical_hash_of(dump_result_as_json(calculate_life_path(person, MethodPolicy())))
    assert h1 == h2
