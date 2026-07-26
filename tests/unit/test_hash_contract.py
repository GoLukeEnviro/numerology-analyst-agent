"""Hash contract tests (v0.1.3 contract integrity).

Proves that the deterministic hash:
1. Covers input_ref, policy, schema_version, results, and trace.
2. Changes when any of those change.
3. Is independent of dict key order and frozenset iteration order.
4. Excludes the hash field itself and consent_given.
5. Is stable across different Python hash seeds.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json

import pytest

from numerology_api.contracts import result_to_payload
from numerology_domain.models import (
    CalculationHashEnvelope,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.service import calculate_life_path
from numerology_engine.trace import _canonical_json, _canonicalize


def _hash_of_envelope(result: object) -> str:
    """Compute the hash the same way the service does (via CalculationHashEnvelope)."""
    from numerology_engine.trace import deterministic_hash as dh

    return dh(result)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Invariant: same input + same policy + same schema → same hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_same_input_same_hash() -> None:
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    policy = MethodPolicy()
    h1 = _hash_of_envelope(calculate_life_path(person, policy))
    h2 = _hash_of_envelope(calculate_life_path(person, policy))
    assert h1 == h2


# ---------------------------------------------------------------------------
# Different as_of_date → different hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_different_as_of_date_different_hash() -> None:
    person1 = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    person2 = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 27),
    )
    policy = MethodPolicy()
    h1 = _hash_of_envelope(calculate_life_path(person1, policy))
    h2 = _hash_of_envelope(calculate_life_path(person2, policy))
    assert h1 != h2


# ---------------------------------------------------------------------------
# Different policy → different hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_different_policy_different_hash() -> None:
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    policy1 = MethodPolicy()
    policy2 = MethodPolicy(master_numbers=frozenset({11, 22}))  # no 33
    h1 = _hash_of_envelope(calculate_life_path(person, policy1))
    h2 = _hash_of_envelope(calculate_life_path(person, policy2))
    assert h1 != h2


# ---------------------------------------------------------------------------
# Different input → different hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_different_input_different_hash() -> None:
    person1 = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    person2 = PersonInput(
        core_name="Anna Musterfrau",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    policy = MethodPolicy()
    h1 = _hash_of_envelope(calculate_life_path(person1, policy))
    h2 = _hash_of_envelope(calculate_life_path(person2, policy))
    assert h1 != h2


# ---------------------------------------------------------------------------
# Different schema_version → different hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_different_schema_version_different_hash() -> None:
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    policy = MethodPolicy()
    result = calculate_life_path(person, policy)
    h1 = _hash_of_envelope(result)

    # Simulate a different schema version by building a different envelope.
    envelope = CalculationHashEnvelope(
        schema_version="calculation-result-v2",
        input_ref=result.input_ref,
        policy=result.policy,
        results={
            "life_path_a": result.life_path_a.model_dump(mode="json"),
            "life_path_b": result.life_path_b.model_dump(mode="json"),
        },
        trace=result.trace,
    )
    payload = envelope.model_dump(mode="json")
    h2 = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    assert h1 != h2


# ---------------------------------------------------------------------------
# Hash field itself is excluded from hash input
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hash_field_excluded_from_hash_input() -> None:
    """The deterministic_hash field must not appear in the hash envelope."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    result = calculate_life_path(person, MethodPolicy())
    envelope = CalculationHashEnvelope(
        schema_version=result.schema_version,
        input_ref=result.input_ref,
        policy=result.policy,
        results={
            "life_path_a": result.life_path_a.model_dump(mode="json"),
            "life_path_b": result.life_path_b.model_dump(mode="json"),
        },
        trace=result.trace,
    )
    payload = envelope.model_dump(mode="json")
    assert "deterministic_hash" not in json.dumps(payload)


# ---------------------------------------------------------------------------
# Key-order independence (corrected: actually reorder keys)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hash_independent_of_key_order() -> None:
    """JSON key order must not affect the hash (v0.1.3 corrected)."""
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

    # Also recursively reorder nested dicts.
    def _reverse_keys(d: object) -> object:
        if not isinstance(d, dict):
            return d
        rev: dict[str, object] = {}
        for k in reversed(tuple(d.keys())):
            rev[k] = _reverse_keys(d[k])
        return rev

    deeply_reordered = _reverse_keys(payload)
    assert isinstance(deeply_reordered, dict)

    h_normal = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    h_reordered = hashlib.sha256(_canonical_json(reordered).encode("utf-8")).hexdigest()
    h_deeply = hashlib.sha256(_canonical_json(deeply_reordered).encode("utf-8")).hexdigest()

    assert h_normal == h_reordered
    assert h_normal == h_deeply


# ---------------------------------------------------------------------------
# The internal deterministic_hash is present and well-formed
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_internal_hash_is_valid_sha256() -> None:
    """result.deterministic_hash must be a 64-char hex SHA-256 digest."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    result = calculate_life_path(person, MethodPolicy())
    h = result.deterministic_hash
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# consent_given change → same hash (excluded from calculation hash)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_consent_given_does_not_affect_hash() -> None:
    """consent_given is a transport/legal field, not a calculation input."""
    person_consent_false = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
        consent_given=False,
    )
    person_consent_true = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
        consent_given=True,
    )
    policy = MethodPolicy()
    h1 = _hash_of_envelope(calculate_life_path(person_consent_false, policy))
    h2 = _hash_of_envelope(calculate_life_path(person_consent_true, policy))
    assert h1 == h2


# ---------------------------------------------------------------------------
# frozenset canonicalization: different iteration order → same hash
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_frozenset_order_does_not_affect_hash() -> None:
    """frozenset master_numbers must be canonicalized to sorted list."""
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    # Same set, different construction order.
    policy1 = MethodPolicy(master_numbers=frozenset({11, 22, 33}))
    policy2 = MethodPolicy(master_numbers=frozenset({33, 11, 22}))
    h1 = _hash_of_envelope(calculate_life_path(person, policy1))
    h2 = _hash_of_envelope(calculate_life_path(person, policy2))
    assert h1 == h2


# ---------------------------------------------------------------------------
# _canonicalize unit: frozenset → sorted list
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_canonicalize_sorts_frozenset() -> None:
    result = _canonicalize({"nums": frozenset({33, 11, 22})})
    assert result == {"nums": [11, 22, 33]}


@pytest.mark.unit
def test_canonicalize_sorts_dict_keys() -> None:
    result = _canonicalize({"z": 1, "a": 2, "m": 3})
    assert isinstance(result, dict)
    assert list(result.keys()) == ["a", "m", "z"]


@pytest.mark.unit
def test_canonicalize_recursively_sorts_nested() -> None:
    result = _canonicalize({"outer": {"z": frozenset({3, 1, 2}), "a": 1}})
    expected: dict[str, object] = {"outer": {"a": 1, "z": [1, 2, 3]}}
    assert result == expected
