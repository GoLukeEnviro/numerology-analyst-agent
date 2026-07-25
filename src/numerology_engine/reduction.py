"""Numeric reduction primitives (Master Contract §3.2, ADR set).

The reduction is the heart of pythagorean numerology: reduce any positive
integer to ``1..9`` *or* hold a master number (11/22/33). Karmic debts
(13/14/16/19) are recognized and flagged as **metadata only** — never
interpreted in 0.1.0.

All functions here are pure and deterministic: same input ⇒ same output,
no global state, no time, no randomness.
"""

from __future__ import annotations

from numerology_domain.models import KARMIC_DEBTS, MASTER_NUMBERS, ReductionOutcome


def digit_sum(n: int) -> int:
    """Sum the base-10 digits of a non-negative integer.

    ``digit_sum(0) == 0``; for ``n > 0`` the result is in ``1..`` (a sum of
    digits is never zero for a positive number).
    """
    if n < 0:
        raise ValueError("digit_sum is defined for non-negative integers only")
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


def recognize_master(n: int, master_numbers: frozenset[int] = MASTER_NUMBERS) -> bool:
    """True iff ``n`` is a configured master number."""
    return n in master_numbers


def recognize_karmic(n: int) -> bool:
    """True iff ``n`` is a karmic debt intermediate (13/14/16/19).

    Per the Master Contract these are flagged, not evaluated.
    """
    return n in KARMIC_DEBTS


def reduce_to_single_digit(
    n: int,
    *,
    master_numbers: frozenset[int] = MASTER_NUMBERS,
) -> ReductionOutcome:
    """Reduce ``n`` to ``1..9`` or hold at a master number.

    Algorithm:
      * ``0`` reduces to ``0`` (only reachable from degenerate input; the
        date validators forbid all-zero dates, but the function stays total).
      * While ``n > 9`` and ``n`` is not a master number: replace ``n`` by
        its digit sum.
      * Stop as soon as ``n`` is a master number or ``n <= 9``.

    The per-iteration audit steps are reconstructed separately by the date
    layer (which owns the :class:`CalculationStep` trail); this primitive
    stays focused on the numeric outcome.
    """
    if n < 0:
        raise ValueError("reduce_to_single_digit requires a non-negative integer")

    current = n

    # Master numbers are held immediately, even if they appear as the input.
    # A karmic debt (13/14/16/19) can never coincide with a master number, so
    # the early-return case is never karmic.
    if recognize_master(current, master_numbers):
        return ReductionOutcome(
            value=current,
            intermediate=n,
            is_master=True,
            is_karmic_debt=False,
        )

    while current > 9 and not recognize_master(current, master_numbers):
        current = digit_sum(current)

    # ``current`` is now <= 9 or a master number.
    is_master = recognize_master(current, master_numbers)
    is_karmic = recognize_karmic(n) and not is_master

    return ReductionOutcome(
        value=current,
        intermediate=n,
        is_master=is_master,
        is_karmic_debt=is_karmic,
    )
