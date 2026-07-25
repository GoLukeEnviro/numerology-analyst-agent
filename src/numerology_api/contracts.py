"""Thin serialization adapter between the domain core and JSON consumers.

This is *not* FastAPI — the Walking Skeleton (0.1.0) deliberately ships no
HTTP layer (Master Contract §4.1 lists FastAPI for later phases). The
adapter only provides deterministic JSON dumping so the CLI and (later)
the API share one canonical serializer.

Determinism contract: ``dump_result_as_json`` always emits sorted keys and
stable UTF-8, so identical input + policy ⇒ byte-identical JSON.
"""

from __future__ import annotations

import json
from typing import Any

from numerology_domain.models import CalculationResult, LifePathResult


def result_to_payload(result: CalculationResult) -> dict[str, Any]:
    """Convert a :class:`CalculationResult` to a JSON-native dict.

    The shape matches the Walking Skeleton CLI contract (sorted, stable):
    ``audit_trace``, ``consistency``, ``input``, ``method``, ``results``,
    plus ``claim_type``, ``name`` and ``deterministic_hash``.
    """
    payload: dict[str, Any] = {
        "claim_type": result.claim_type.value,
        "name": result.name,
        "deterministic_hash": result.deterministic_hash,
        "input": {
            "core_name": result.input_ref.core_name,
            "active_name": result.input_ref.active_name,
            "birth_date": result.input_ref.birth_date.isoformat(),
            "locale": result.input_ref.locale.value,
        },
        "method": {
            "system": result.policy.system.value,
            "version": result.policy.version,
            "y_mode": result.policy.y_mode.value,
            "umlaut_policy": result.policy.umlaut_policy.value,
            "name_basis": result.policy.name_basis.value,
            "date_method": result.policy.date_method.value,
            "locale": result.policy.locale.value,
            "master_numbers": sorted(result.policy.master_numbers),
        },
        "results": {
            "life_path_a": _life_path_payload(result.life_path_a),
            "life_path_b": _life_path_payload(result.life_path_b),
        },
        "consistency": {
            "a_equals_b": result.consistency.a_equals_b,
            "life_path_a": result.consistency.life_path_a,
            "life_path_b": result.consistency.life_path_b,
            "warning": result.consistency.warning,
        },
        "audit_trace": {
            "normalization_steps": [
                s.model_dump(mode="json") for s in result.trace.normalization_steps
            ],
            "calculation_steps": [
                s.model_dump(mode="json") for s in result.trace.calculation_steps
            ],
            "warnings": list(result.trace.warnings),
            "disambiguation_required": result.trace.disambiguation_required,
        },
    }
    return payload


def _life_path_payload(lp: LifePathResult) -> dict[str, Any]:
    """Project a :class:`LifePathResult` into a JSON-native dict."""
    return {
        "method": lp.method,
        "value": lp.reduction.value,
        "intermediate": lp.reduction.intermediate,
        "is_master": lp.reduction.is_master,
        "is_karmic_debt": lp.reduction.is_karmic_debt,
        "components": dict(lp.components),
        "steps": [s.model_dump(mode="json") for s in lp.steps],
    }


def dump_result_as_json(result: CalculationResult, *, indent: int = 2) -> str:
    """Serialize a result to canonical, key-sorted JSON text.

    ``sort_keys=True`` + ``ensure_ascii=False`` guarantees byte-stability
    for identical inputs (Master Contract §2.4, Phase-4 Gate).
    """
    return json.dumps(
        result_to_payload(result),
        sort_keys=True,
        ensure_ascii=False,
        indent=indent,
    )
