"""Deterministic personal cycles, Pinnacles and Challenges."""

from __future__ import annotations

from numerology_domain.models import (
    CycleCalculationResult,
    CyclePhase,
    MethodPolicy,
    PersonInput,
)
from numerology_engine.dates import life_path_a
from numerology_engine.numbers import create_number
from numerology_engine.reduction import digit_sum, reduce_to_single_digit


def calculate_cycles(person: PersonInput, policy: MethodPolicy) -> CycleCalculationResult:
    """Calculate all date-dependent V1 cycles using the explicit ``as_of_date``."""
    birth = person.birth_date
    as_of = person.as_of_date
    year_digits = digit_sum(as_of.year)
    personal_year = create_number(
        "personal_year",
        birth.month + birth.day + year_digits,
        policy=policy,
        components={"birth_month": birth.month, "birth_day": birth.day, "year": year_digits},
    )
    personal_month = create_number(
        "personal_month",
        personal_year.reduced_value + as_of.month,
        policy=policy,
        components={"personal_year": personal_year.reduced_value, "month": as_of.month},
    )
    personal_day = create_number(
        "personal_day",
        personal_month.reduced_value + as_of.day,
        policy=policy,
        components={"personal_month": personal_month.reduced_value, "day": as_of.day},
    )

    month = reduce_to_single_digit(birth.month, master_numbers=policy.master_numbers).value
    day = reduce_to_single_digit(birth.day, master_numbers=policy.master_numbers).value
    year = reduce_to_single_digit(digit_sum(birth.year), master_numbers=policy.master_numbers).value
    first_pinnacle = create_number("pinnacle_1", month + day, policy=policy)
    second_pinnacle = create_number("pinnacle_2", day + year, policy=policy)
    pinnacle_numbers = (
        first_pinnacle,
        second_pinnacle,
        create_number(
            "pinnacle_3",
            first_pinnacle.reduced_value + second_pinnacle.reduced_value,
            policy=policy,
        ),
        create_number("pinnacle_4", month + year, policy=policy),
    )
    first_challenge = create_number("challenge_1", abs(month - day), policy=policy)
    second_challenge = create_number("challenge_2", abs(day - year), policy=policy)
    challenge_numbers = (
        first_challenge,
        second_challenge,
        create_number(
            "challenge_3",
            abs(first_challenge.reduced_value - second_challenge.reduced_value),
            policy=policy,
        ),
        create_number("challenge_4", abs(month - year), policy=policy),
    )

    life_path = life_path_a(birth, master_numbers=policy.master_numbers).reduced_value
    first_end = 36 - life_path
    ranges: tuple[tuple[int, int | None], ...] = (
        (0, first_end),
        (first_end + 1, first_end + 9),
        (first_end + 10, first_end + 18),
        (first_end + 19, None),
    )
    pinnacles = tuple(
        CyclePhase(
            ordinal=index,
            start_age=start,
            end_age=end,
            number=number.model_copy(
                update={"components": {"month": month, "day": day, "year": year}}
            ),
        )
        for index, (number, (start, end)) in enumerate(
            zip(pinnacle_numbers, ranges, strict=True), start=1
        )
    )
    challenges = tuple(
        CyclePhase(
            ordinal=index,
            start_age=start,
            end_age=end,
            number=number.model_copy(
                update={"components": {"month": month, "day": day, "year": year}}
            ),
        )
        for index, (number, (start, end)) in enumerate(
            zip(challenge_numbers, ranges, strict=True), start=1
        )
    )
    return CycleCalculationResult(
        as_of_date=as_of,
        personal_year=personal_year,
        personal_month=personal_month,
        personal_day=personal_day,
        pinnacles=pinnacles,
        challenges=challenges,
    )
