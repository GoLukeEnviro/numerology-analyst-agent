"""Life Path date calculations (Master Contract §3.2, V1 minimal scope).

Two reduction methods are implemented and cross-checked:

* **Life Path A — ``sum_all_digits``**: add every digit of the ISO date
  (``YYYYMMDD``), then reduce. Example ``1985-07-25`` →
  ``1+9+8+5+0+7+2+5 = 37 → 10 → 1``.
* **Life Path B — ``component_then_sum``**: reduce month, day and year
  independently first, then sum the three reduced values and reduce again.
  Example ``1985-07-25`` → month ``7``, day ``7``, year ``23 → 5`` →
  ``7+7+5 = 19 → 10 → 1``.

When A ≠ B the result is still returned (both values are valid pythagorean
answers); a deterministic consistency warning is attached to the audit
trace. This is the documented V1 behavior (no silent picking of one side).
"""

from __future__ import annotations

from datetime import date

from numerology_domain.models import (
    MASTER_NUMBERS,
    CalculationStep,
    ConsistencyStatus,
    KarmicDebtInfo,
    LifePathResult,
)
from numerology_engine.reduction import (
    digit_sum,
    recognize_karmic,
    reduce_to_single_digit,
    reduction_chain,
)

# Upper bound used purely to validate that a date is not absurdly far in the
# future. The Walking Skeleton accepts future dates with a warning rather
# than rejecting them, because no contract pins the cutoff (see OFFEN note
# in the final report). 2200 is a generous, deterministic fence.
#
# NOTE (Korrektur 3): this fence only applies to the *general date analysis*
# extension point. Person profiles reject future birth_date at the
# PersonInput model boundary (birth_date <= as_of_date); this warning is a
# backstop for the date-analysis command that will reuse the engine later.
_FUTURE_FENCE_YEAR = 2200


def _all_digits(birth: date) -> tuple[int, ...]:
    """Return the eight digits of an ISO date ``YYYYMMDD`` in order.

    Leading zeros of month/day are preserved as explicit ``0`` digits so
    ``1985-07-05`` and ``1985-7-5`` produce the identical digit sequence
    ``1,9,8,5,0,7,0,5`` (determinism: calendar equality ⇒ digit equality).
    """
    return tuple(int(ch) for ch in f"{birth.year:04d}{birth.month:02d}{birth.day:02d}")


def _karmic_for(raw_total: int, origin: str) -> KarmicDebtInfo | None:
    """Attach a karmic marker iff the unreduced core value is a karmic debt.

    Per Korrektur 1 the marker lives ONLY on the methodically defined
    unreduced core value of a Life Path method - never on intermediate
    digit-sum steps. ``origin`` records which method component produced
    the value ('total_sum' for A, 'component_sum' for B).
    """
    if recognize_karmic(raw_total):
        return KarmicDebtInfo(number=raw_total, origin=origin)
    return None


def life_path_a(birth: date, *, master_numbers: frozenset[int] = MASTER_NUMBERS) -> LifePathResult:
    """Life Path A — sum every date digit, then reduce.

    The unreduced core value (``raw_total``) is the sum of all date digits
    (Korrektur 1). The karmic marker attaches to this raw_total with origin
    ``'total_sum'``.
    """
    digits = _all_digits(birth)
    raw = sum(digits)
    steps: list[CalculationStep] = [
        CalculationStep(
            label="sum_all_digits",
            inputs=digits,
            output=raw,
            note=f"{' + '.join(str(d) for d in digits)} = {raw}",
        )
    ]
    outcome = reduce_to_single_digit(raw, master_numbers=master_numbers)
    steps.extend(_reduction_steps(raw, outcome.value, master_numbers))
    chain = reduction_chain(raw, master_numbers=master_numbers)
    return LifePathResult(
        method="sum_all_digits",
        reduction=outcome,
        raw_total=raw,
        reduced_value=outcome.value,
        compound_notation=_compound_notation(chain),
        karmic_debt=_karmic_for(raw, "total_sum"),
        components={},
        steps=tuple(steps),
    )


def life_path_b(birth: date, *, master_numbers: frozenset[int] = MASTER_NUMBERS) -> LifePathResult:
    """Life Path B — reduce month/day/year, then sum and reduce.

    The unreduced core value (``raw_total``) is the sum of the *reduced*
    month/day/year components (Korrektur 1). The karmic marker attaches to
    this component sum with origin ``'component_sum'``.
    """
    month = birth.month
    day = birth.day
    year = birth.year

    month_red = reduce_to_single_digit(month, master_numbers=master_numbers)
    day_red = reduce_to_single_digit(day, master_numbers=master_numbers)
    year_red = reduce_to_single_digit(_year_digit_sum(year), master_numbers=master_numbers)

    components = {"month": month_red.value, "day": day_red.value, "year": year_red.value}
    summed = month_red.value + day_red.value + year_red.value

    steps: list[CalculationStep] = [
        CalculationStep(
            label="reduce_month",
            inputs=(month,),
            output=month_red.value,
            note=f"month {month} -> {month_red.value}",
        ),
        CalculationStep(
            label="reduce_day",
            inputs=(day,),
            output=day_red.value,
            note=f"day {day} -> {day_red.value}",
        ),
        CalculationStep(
            label="reduce_year",
            inputs=(_year_digit_sum(year),),
            output=year_red.value,
            note=f"year {year} digits -> {_year_digit_sum(year)} -> {year_red.value}",
        ),
        CalculationStep(
            label="sum_components",
            inputs=(month_red.value, day_red.value, year_red.value),
            output=summed,
            note=f"{month_red.value} + {day_red.value} + {year_red.value} = {summed}",
        ),
    ]
    outcome = reduce_to_single_digit(summed, master_numbers=master_numbers)
    steps.extend(_reduction_steps(summed, outcome.value, master_numbers))
    chain = reduction_chain(summed, master_numbers=master_numbers)
    return LifePathResult(
        method="component_then_sum",
        reduction=outcome,
        raw_total=summed,
        reduced_value=outcome.value,
        compound_notation=_compound_notation(chain),
        karmic_debt=_karmic_for(summed, "component_sum"),
        components=components,
        steps=tuple(steps),
    )


def _compound_notation(chain: list[int]) -> str:
    """Render a reduction chain as slash-notation, e.g. ``'37/10/1'`` (Korrektur 1)."""
    return "/".join(str(n) for n in chain)


def _year_digit_sum(year: int) -> int:
    return digit_sum(year)


def _reduction_steps(start: int, end: int, master_numbers: frozenset[int]) -> list[CalculationStep]:
    """Reconstruct the per-iteration digit-sum steps for the audit trail."""
    if start == end:
        # No reduction needed (already single digit / master held).
        return [
            CalculationStep(
                label="reduce",
                inputs=(start,),
                output=end,
                note="already reduced" if start <= 9 else "master number held",
            )
        ]
    out: list[CalculationStep] = []
    current = start
    # Guard: bounded by the digit-length of start, so always terminates.
    while current != end:
        nxt = digit_sum(current)
        out.append(
            CalculationStep(
                label="digit_sum",
                inputs=(current,),
                output=nxt,
                note=f"{current} -> {nxt}",
            )
        )
        current = nxt
        if current in master_numbers and current == end:
            break
    return out


def consistency_check(res_a: LifePathResult, res_b: LifePathResult) -> ConsistencyStatus:
    """Build the A-vs-B consistency report."""
    a_equals_b = res_a.reduction.value == res_b.reduction.value
    warning = (
        ""
        if a_equals_b
        else (
            f"Life Path A ({res_a.reduction.value}) differs from Life Path B "
            f"({res_b.reduction.value}); both values emitted, no automatic pick."
        )
    )
    return ConsistencyStatus(
        a_equals_b=a_equals_b,
        life_path_a=res_a.reduction.value,
        life_path_b=res_b.reduction.value,
        warning=warning,
    )


def future_warning(birth: date) -> str:
    """Return a deterministic warning if ``birth`` is implausibly far ahead.

    Empty string when the date is within the accepted fence. The Walking
    Skeleton deliberately *accepts* future dates (with a warning) instead of
    rejecting them, because the Master Contract does not pin a cutoff.

    Note (Korrektur 3): this is a backstop for the general date-analysis
    extension point. Person profiles reject a future ``birth_date`` at the
    ``PersonInput`` model boundary; this function is retained for future
    date-analysis work and remains unused on the person happy path.
    """
    if birth.year > _FUTURE_FENCE_YEAR:
        return (
            f"birth_date year {birth.year} exceeds {_FUTURE_FENCE_YEAR}; "
            "accepted with warning (general date analysis extension point)."
        )
    return ""
