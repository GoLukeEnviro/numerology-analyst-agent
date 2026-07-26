"""Versionierter deterministic_hash Golden Case (Korrektur 4, v0.1.3).

Garantiert:
1. Gleiche kanonische Eingabe + Methodenversion + Schema-Version ⇒ gleicher Hash.
2. JSON-Feldreihenfolge beeinflusst Hash nicht.
3. Metadaten (Laufzeit, Request-ID) fließen nicht ein (der Core hat keine).

Eine bewusste Änderung braucht: Methodenversion ODER Schema-Version Bump +
aktualisierten Golden Case + dokumentierte Begründung.

Der Hash wird über das CalculationHashEnvelope gebildet (v0.1.3 contract
integrity): input_ref + policy + schema_version + results + trace.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json

import pytest

from numerology_api.contracts import result_to_payload
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.service import calculate_life_path
from numerology_engine.trace import _canonical_json

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
        # v0.1.3: hash covers CalculationHashEnvelope (input_ref minus consent,
        # full MethodPolicy, schema_version, results, trace). Frozensets are
        # canonicalized to sorted lists. Independently verified via manual
        # SHA-256 over the canonical JSON.
        "expected_hash": "5ec8117ea20995b8eb9aaa7f539bf2e125844860272de851d684ca777e985258",
    },
]


def _canonical_hash_of(json_str: str) -> str:
    """SHA-256 über das sortierte, neu serialisierte JSON (externer Vergleich)."""
    canonical = json.dumps(json.loads(json_str), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@pytest.mark.golden
@pytest.mark.parametrize("case", HASH_CASES, ids=[c["case_id"] for c in HASH_CASES])
def test_deterministic_hash_stable(case: dict[str, object]) -> None:
    """Hash muss stabil bleiben für identische Eingabe + Versionen.

    v0.1.3: vergleicht result.deterministic_hash (intern) gegen den
    erwarteten Golden-Case-Wert, nicht einen extern neu berechneten Hash.
    """
    person = PersonInput(
        core_name=str(case["core_name"]),
        birth_date=date.fromisoformat(str(case["birth_date"])),
        as_of_date=date.fromisoformat(str(case["as_of_date"])),
    )
    result = calculate_life_path(person, MethodPolicy())
    actual_hash = result.deterministic_hash

    assert actual_hash == case["expected_hash"], (
        f"Hash changed for {case['case_id']}! "
        f"If this is intentional: document why, bump method/schema version, "
        f"and update expected_hash. New hash: {actual_hash}"
    )


@pytest.mark.golden
def test_hash_independent_of_key_order() -> None:
    """JSON-Feldreihenfolge darf den Hash nicht beeinflussen (v0.1.3 korrigiert).

    Baut einen Payload mit tatsächlich umgekehrter Schlüsselreihenfolge und
    prüft, dass _canonical_json beide normalisiert.
    """
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    result = calculate_life_path(person, MethodPolicy())
    payload = result_to_payload(result)

    # Build a payload with reversed top-level key order.
    reordered: dict[str, object] = {}
    for key in reversed(tuple(payload.keys())):
        reordered[key] = payload[key]

    h_normal = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    h_reordered = hashlib.sha256(_canonical_json(reordered).encode("utf-8")).hexdigest()

    assert h_normal == h_reordered


@pytest.mark.golden
def test_hash_same_across_two_runs() -> None:
    """Zwei unabhängige Berechnungen gleicher Eingabe ⇒ gleicher Hash (v0.1.3)."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    h1 = calculate_life_path(person, MethodPolicy()).deterministic_hash
    h2 = calculate_life_path(person, MethodPolicy()).deterministic_hash
    assert h1 == h2
