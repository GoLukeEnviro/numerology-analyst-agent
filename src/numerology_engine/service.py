"""Service facade — the single entry point the CLI/API layers call.

The Walking Skeleton (0.1.0) computes only the Life Path (A and B). The
service:

1. normalizes the name (foundation for later name-based numbers; recorded
   in the audit trace even though Life Path does not consume it),
2. runs Life Path A and Life Path B on the birth date,
3. checks A-vs-B consistency,
4. assembles the :class:`CalculationResult` with a deterministic hash.

No LLM, no network, no global state — pure deterministic transformation.
"""

from __future__ import annotations

from numerology_domain.models import (
    AuditTrace,
    CalculationResult,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.dates import consistency_check, future_warning, life_path_a, life_path_b
from numerology_engine.normalization import normalize_name
from numerology_engine.trace import build_trace, deterministic_hash


def calculate_life_path(person: PersonInput, policy: MethodPolicy) -> CalculationResult:
    """Compute the Life Path (A + B) result for ``person`` under ``policy``.

    The result is fully self-describing: it carries the input reference,
    the policy, both methods, the consistency status, the audit trace and
    the deterministic hash.
    """
    # 1. Normalize the name as a reusable foundation. Life Path itself only
    #    depends on the birth date, but the calculation_name is recorded so
    #    later name-based numbers reuse the exact same audit trail.
    _calc_name, norm_steps = normalize_name(
        person.core_name,
        umlaut_policy=policy.umlaut_policy,
        locale=policy.locale,
    )

    # 2. Run both Life Path methods on the birth date.
    res_a = life_path_a(person.birth_date, master_numbers=policy.master_numbers)
    res_b = life_path_b(person.birth_date, master_numbers=policy.master_numbers)

    # 3. Consistency + optional future-date warning.
    consistency = consistency_check(res_a, res_b)
    warnings: list[str] = []
    if consistency.warning:
        warnings.append(consistency.warning)
    fw = future_warning(person.birth_date)
    if fw:
        warnings.append(fw)

    # 4. Assemble the trace from the per-method steps.
    calc_steps = (*res_a.steps, *res_b.steps)
    trace: AuditTrace = build_trace(
        normalization_steps=norm_steps,
        calculation_steps=calc_steps,
        warnings=tuple(warnings),
        disambiguation_required=False,
    )

    result = CalculationResult(
        input_ref=person,
        policy=policy,
        life_path_a=res_a,
        life_path_b=res_b,
        consistency=consistency,
        trace=trace,
    )

    # 5. Stamp the deterministic hash (computed over the full hash envelope,
    #    not just the trace — v0.1.3 contract integrity).
    return result.model_copy(update={"deterministic_hash": deterministic_hash(result)})
