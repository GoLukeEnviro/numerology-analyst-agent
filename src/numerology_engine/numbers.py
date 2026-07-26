"""Shared construction of auditable reduced numerological numbers."""

from __future__ import annotations

from numerology_domain.models import CalculationStep, MethodPolicy, NumberResult
from numerology_engine.reduction import reduce_to_single_digit, reduction_chain


def create_number(
    name: str,
    raw_total: int,
    *,
    policy: MethodPolicy,
    components: dict[str, int] | None = None,
) -> NumberResult:
    """Reduce a non-negative raw total and retain its complete calculation path."""
    if raw_total < 0:
        raise ValueError("raw_total must not be negative")
    if raw_total == 0:
        reduced_value = 0
        is_master = False
        chain = [0]
    else:
        outcome = reduce_to_single_digit(raw_total, master_numbers=policy.master_numbers)
        reduced_value = outcome.value
        is_master = outcome.is_master
        chain = reduction_chain(raw_total, master_numbers=policy.master_numbers)
    return NumberResult(
        name=name,
        raw_total=raw_total,
        reduced_value=reduced_value,
        compound_notation="/".join(str(value) for value in chain),
        is_master=is_master,
        components={} if components is None else components,
        steps=(
            CalculationStep(
                label=name,
                inputs=(raw_total,),
                output=reduced_value,
                note=" -> ".join(str(value) for value in chain),
            ),
        ),
    )
