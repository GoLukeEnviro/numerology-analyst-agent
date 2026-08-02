"""Audit-trace builder and deterministic hash (calculation-engineer contract §6).

The deterministic hash is the byte-stability proof required by Master
Contract §2.4 and Phase-4 Gate: identical input + policy MUST yield an
identical hash. We achieve this by:

* building a ``CalculationHashEnvelope`` that includes ONLY
  calculation-relevant fields (schema_version, core_name, active_name,
  birth_date, as_of_date, locale, full MethodPolicy, results, trace),
* EXCLUDING non-calculation fields: consent_given, deterministic_hash,
  request metadata, timestamps, logging fields,
* canonicalizing all unordered collections (frozenset, set) to sorted
  lists before serialization,
* serializing with ``sort_keys=True`` (dict order is irrelevant),
* serializing with ``ensure_ascii=False`` + UTF-8 (locale-stable),
* hashing the resulting bytes with SHA-256.

No time, no random, no dict-order dependency, no consent leakage.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from numerology_domain.models import (
    AuditTrace,
    CalculationHashEnvelope,
    CalculationResult,
    PersonInput,
    ProfileCalculationResult,
    ProfileCalculationResultV4,
)


def _canonicalize(value: object) -> object:
    """Recursively canonicalize a value for deterministic hashing.

    * dict keys are sorted by their string representation.
    * frozenset and set are converted to sorted lists.
    * lists and tuples are recursively canonicalized element-wise.
    * All other values pass through unchanged.

    Unordered collections (set/frozenset) are sorted by their canonical
    JSON representation, NOT by direct Python comparison.  Direct
    ``sorted()`` on heterogeneous elements (e.g. ``{1, 'a', 2.5}``) raises
    ``TypeError: '<' not supported between instances of 'str' and 'float'``
    (reproducible counter-evidence, Issue #32).  Sorting by canonical JSON
    is total, deterministic and type-agnostic.

    This guarantees that two semantically identical payloads produce
    byte-identical JSON regardless of Python's hash seed or insertion
    order of unordered collections.
    """
    if isinstance(value, dict):
        return {
            str(key): _canonicalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, set | frozenset):
        # Härtung (Issue #32): erst kanonisches JSON je Element, dann sortieren.
        # Vermeidet TypeError bei heterogenen Elementen (int/str/float/...).
        canonical_items = [_canonicalize(item) for item in value]
        return sorted(
            canonical_items,
            key=lambda item: _canonical_json(item)
            if isinstance(item, dict)
            else json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
        )
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    return value


def _canonical_json(payload: dict[str, Any]) -> str:
    """Serialize a dict to canonical, sorted JSON (deterministic byte form)."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _calculation_input_ref(person: PersonInput) -> dict[str, object]:
    """Project only calculation-relevant fields from PersonInput.

    consent_given is explicitly excluded — it is a transport/legal
    metadata field, not a calculation input. Changing consent must not
    change the calculation hash.
    """
    return {
        "core_name": person.core_name,
        "active_name": person.active_name,
        "birth_date": person.birth_date.isoformat(),
        "as_of_date": person.as_of_date.isoformat(),
        "locale": person.locale.value,
    }


def deterministic_hash(result: CalculationResult) -> str:
    """SHA-256 hex digest over the :class:`CalculationHashEnvelope`.

    v0.1.3 contract integrity: the hash covers ONLY calculation-relevant
    fields — schema_version, input_ref (minus consent), full MethodPolicy,
    results, and trace. The ``deterministic_hash`` field itself and
    consent_given are excluded.

    Hash contract (v0.1.3):
    * same input + same policy + same schema → same hash
    * different as_of_date → different hash
    * different MethodPolicy → different hash
    * different input → different hash
    * different schema_version → different hash
    * consent_given change → same hash (excluded)
    * dict/frozenset order → same hash (canonicalized)
    """
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
    raw: dict[str, Any] = envelope.model_dump(mode="json")
    # Replace the full PersonInput with only calculation-relevant fields.
    raw["input_ref"] = _calculation_input_ref(result.input_ref)
    canonicalized = _canonicalize(raw)
    assert isinstance(canonicalized, dict)
    return hashlib.sha256(_canonical_json(canonicalized).encode("utf-8")).hexdigest()


def deterministic_profile_hash(result: ProfileCalculationResult) -> str:
    """Hash every calculation-relevant field of a complete profile result."""
    raw: dict[str, Any] = result.model_dump(mode="json", exclude={"deterministic_hash"})
    raw["input_ref"] = _calculation_input_ref(result.input_ref)
    canonicalized = _canonicalize(raw)
    assert isinstance(canonicalized, dict)
    return hashlib.sha256(_canonical_json(canonicalized).encode("utf-8")).hexdigest()


def deterministic_profile_hash_v4(result: ProfileCalculationResultV4) -> str:
    """Hash every calculation-relevant field of a V4 profile result (PR #19)."""
    raw: dict[str, Any] = result.model_dump(mode="json", exclude={"deterministic_hash"})
    raw["input_ref"] = _calculation_input_ref(result.input_ref)
    canonicalized = _canonicalize(raw)
    assert isinstance(canonicalized, dict)
    return hashlib.sha256(_canonical_json(canonicalized).encode("utf-8")).hexdigest()


def build_trace(
    *,
    normalization_steps: tuple[Any, ...] = (),
    calculation_steps: tuple[Any, ...] = (),
    warnings: tuple[str, ...] = (),
    disambiguation_required: bool = False,
) -> AuditTrace:
    """Construct an :class:`AuditTrace` from already-audited pieces."""
    return AuditTrace(
        normalization_steps=tuple(normalization_steps),
        calculation_steps=tuple(calculation_steps),
        warnings=tuple(warnings),
        disambiguation_required=disambiguation_required,
    )
