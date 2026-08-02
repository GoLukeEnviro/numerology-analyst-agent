"""Private model submodules — fachliche Cluster der Domain-Modelle.

Dieses Paket ist bewusst privat (``_models``): Der stabile öffentliche
Einstiegspunkt ist ``numerology_domain.models`` (Compatibility Facade).
Direkte Imports aus ``numerology_domain._models`` sind für interne
Zwecke erlaubt, aber nicht Teil des öffentlichen Vertrags.
"""

from numerology_domain._models.calculation import (
    CALCULATION_RESULT_SCHEMA_VERSION,
    PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
    PROFILE_CALCULATION_RESULT_V4_SCHEMA_VERSION,
    AuditTrace,
    CalculationHashEnvelope,
    CalculationResult,
    CalculationStep,
    ConsistencyStatus,
    KarmicDebtInfo,
    KarmicOccurrence,
    LifePathResult,
    NameNumberSet,
    NameNumberSetV2,
    NameNumberVariant,
    NameSegmentResult,
    NormalizationStep,
    NumberModel,
    NumberResult,
    ReductionOutcome,
)
from numerology_domain._models.cycles import (
    CycleCalculationResult,
    CycleCalculationResultV2,
    CyclePhase,
)
from numerology_domain._models.input import (
    KARMIC_DEBTS,
    MASTER_NUMBERS,
    PYTHAGOREAN_V1_VERSION,
    PYTHAGOREAN_V2_VERSION,
    VALID_PYTHAGOREAN_VERSIONS,
    MethodPolicy,
    PersonInput,
)
from numerology_domain._models.profile import (
    ProfileCalculationResult,
    ProfileCalculationResultV4,
)

__all__ = [  # noqa: RUF022
    # Constants
    "CALCULATION_RESULT_SCHEMA_VERSION",
    "PROFILE_CALCULATION_RESULT_SCHEMA_VERSION",
    "PROFILE_CALCULATION_RESULT_V4_SCHEMA_VERSION",
    "KARMIC_DEBTS",
    "MASTER_NUMBERS",
    "PYTHAGOREAN_V1_VERSION",
    "PYTHAGOREAN_V2_VERSION",
    "VALID_PYTHAGOREAN_VERSIONS",
    # Models
    "AuditTrace",
    "CalculationHashEnvelope",
    "CalculationResult",
    "CalculationStep",
    "ConsistencyStatus",
    "CycleCalculationResult",
    "CycleCalculationResultV2",
    "CyclePhase",
    "KarmicDebtInfo",
    "KarmicOccurrence",
    "LifePathResult",
    "MethodPolicy",
    "NameNumberSet",
    "NameNumberSetV2",
    "NameNumberVariant",
    "NameSegmentResult",
    "NormalizationStep",
    "NumberModel",
    "NumberResult",
    "PersonInput",
    "ProfileCalculationResult",
    "ProfileCalculationResultV4",
    "ReductionOutcome",
]
