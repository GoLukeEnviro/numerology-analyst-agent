"""Cycle contracts — personal date cycles and Pinnacle/Challenge phases.

Private submodule of ``numerology_domain._models``.  The public surface is
the ``numerology_domain.models`` compatibility facade.
"""

from __future__ import annotations

from datetime import date

from pydantic import Field

from numerology_domain._models.base import _FrozenModel
from numerology_domain._models.calculation import NumberModel, NumberResult


class CyclePhase(_FrozenModel):
    """One numbered Pinnacle or Challenge phase with inclusive age boundaries."""

    ordinal: int = Field(..., ge=1, le=4)
    start_age: int = Field(..., ge=0)
    end_age: int | None = Field(default=None, ge=0)
    number: NumberResult


class CycleCalculationResult(_FrozenModel):
    """Personal date cycles and the four lifetime Pinnacle/Challenge phases."""

    as_of_date: date
    personal_year: NumberResult
    personal_month: NumberResult
    personal_day: NumberResult
    pinnacles: tuple[CyclePhase, ...] = Field(..., min_length=4, max_length=4)
    challenges: tuple[CyclePhase, ...] = Field(..., min_length=4, max_length=4)


class CycleCalculationResultV2(_FrozenModel):
    """Personal date cycles using V2 NumberModel and corrected formulas (PR #19)."""

    as_of_date: date
    personal_year: NumberModel
    personal_month: NumberModel
    personal_day: NumberModel
    pinnacles: tuple[NumberModel, ...] = Field(..., min_length=4, max_length=4)
    challenges: tuple[NumberModel, ...] = Field(..., min_length=4, max_length=4)
