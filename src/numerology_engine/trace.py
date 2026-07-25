"""Audit-trace builder and deterministic hash (calculation-engineer contract §6).

The deterministic hash is the byte-stability proof required by Master
Contract §2.4 and Phase-4 Gate: identical input + policy MUST yield an
identical hash. We achieve this by:

* serializing with ``sort_keys=True`` (dict order is irrelevant),
* serializing with ``ensure_ascii=False`` + UTF-8 (locale-stable),
* hashing the resulting bytes with SHA-256.

No time, no random, no dict-order dependency.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from numerology_domain.models import AuditTrace


def trace_to_sorted_json(trace: AuditTrace) -> str:
    """Serialize an :class:`AuditTrace` to canonical, sorted JSON.

    Pydantic ``model_dump(mode='json')`` gives JSON-native primitives; we
    then re-dump with ``sort_keys=True`` so key order never affects the
    hash. Tuples become lists in JSON, which is order-stable by position.
    """
    payload: dict[str, Any] = trace.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def deterministic_hash(trace: AuditTrace) -> str:
    """SHA-256 hex digest of the canonical trace JSON."""
    return hashlib.sha256(trace_to_sorted_json(trace).encode("utf-8")).hexdigest()


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
