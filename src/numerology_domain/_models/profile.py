"""Profile contracts — complete deterministic profile results (V1/V3/V4).

Private submodule of ``numerology_domain._models``.  The public surface is
the ``numerology_domain.models`` compatibility facade.
"""

from __future__ import annotations

from pydantic import Field

from numerology_domain._models.base import _FrozenModel
from numerology_domain._models.calculation import (
    PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
    PROFILE_CALCULATION_RESULT_V4_SCHEMA_VERSION,
    AuditTrace,
    ConsistencyStatus,
    LifePathResult,
    NameNumberSet,
    NameNumberSetV2,
    NumberModel,
    NumberResult,
)
from numerology_domain._models.cycles import (
    CycleCalculationResult,
    CycleCalculationResultV2,
)
from numerology_domain._models.input import MethodPolicy, PersonInput
from numerology_domain.enums import ClaimType


class ProfileCalculationResult(_FrozenModel):
    """Complete deterministic profile contract introduced for release 0.1.4."""

    claim_type: ClaimType = ClaimType.CALCULATION_FACT
    name: str = "complete_profile"
    schema_version: str = PROFILE_CALCULATION_RESULT_SCHEMA_VERSION
    input_ref: PersonInput
    policy: MethodPolicy
    life_path_a: LifePathResult
    life_path_b: LifePathResult
    consistency: ConsistencyStatus
    birthday: NumberResult
    attitude: NumberResult
    core_name: NameNumberSet | None = None
    active_name: NameNumberSet | None = None
    maturity: NumberResult
    cycles: CycleCalculationResult
    trace: AuditTrace
    deterministic_hash: str = ""


class ProfileCalculationResultV4(_FrozenModel):
    """Complete deterministic V2 profile contract (profile-calculation-result-v4, PR #19).

    Uses ``NumberModel`` throughout, has explicit primary/secondary life path
    roles and full MethodPolicy versioning.  Additive — does not alter V1/V3.
    """

    claim_type: ClaimType = ClaimType.CALCULATION_FACT
    name: str = "complete_profile_v4"
    schema_version: str = PROFILE_CALCULATION_RESULT_V4_SCHEMA_VERSION
    input_ref: PersonInput
    policy: MethodPolicy
    life_path_primary: NumberModel = Field(
        ..., description="sum_all_birth_date_digits (role=primary)."
    )
    life_path_secondary: NumberModel = Field(
        ..., description="component_then_sum (role=secondary)."
    )
    birthday: NumberModel
    attitude: NumberModel
    core_name: NameNumberSetV2 | None = None
    active_name: NameNumberSetV2 | None = None
    cycles: CycleCalculationResultV2
    trace: AuditTrace
    deterministic_hash: str = ""
