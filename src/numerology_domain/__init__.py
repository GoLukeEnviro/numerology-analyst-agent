"""Numerology domain — types, policies and contracts.

Public surface for the Walking Skeleton (0.1.0). Importing from submodules
is allowed, but the names below are the stable API the engine and CLI
depend on.
"""

from __future__ import annotations

from numerology_domain.enums import (
    ClaimType,
    DateMethod,
    EvidenceLevel,
    Locale,
    MethodSystem,
    NameBasis,
    UmlautPolicy,
    YMode,
)
from numerology_domain.exceptions import (
    CalculationError,
    DisambiguationRequired,
    NormalizationError,
    NumerologyError,
    PolicyError,
    ValidationError,
)
from numerology_domain.models import (
    CALCULATION_RESULT_SCHEMA_VERSION,
    KARMIC_DEBTS,
    MASTER_NUMBERS,
    PYTHAGOREAN_V1_VERSION,
    AuditTrace,
    CalculationHashEnvelope,
    CalculationResult,
    CalculationStep,
    ConsistencyStatus,
    KarmicDebtInfo,
    LifePathResult,
    MethodPolicy,
    NormalizationStep,
    PersonInput,
    ReductionOutcome,
)

# __all__ is grouped thematically (Enums/Exceptions/Constants/Models) for
# readability; the grouping is intentionally documentative, hence RUF022 is
# suppressed on the assignment line below.
__all__ = [  # noqa: RUF022
    # Enums
    "ClaimType",
    "DateMethod",
    "EvidenceLevel",
    "Locale",
    "MethodSystem",
    "NameBasis",
    "UmlautPolicy",
    "YMode",
    # Exceptions
    "CalculationError",
    "DisambiguationRequired",
    "NormalizationError",
    "NumerologyError",
    "PolicyError",
    "ValidationError",
    # Constants
    "CALCULATION_RESULT_SCHEMA_VERSION",
    "KARMIC_DEBTS",
    "MASTER_NUMBERS",
    "PYTHAGOREAN_V1_VERSION",
    # Models
    "AuditTrace",
    "CalculationHashEnvelope",
    "CalculationResult",
    "CalculationStep",
    "ConsistencyStatus",
    "KarmicDebtInfo",
    "LifePathResult",
    "MethodPolicy",
    "NormalizationStep",
    "PersonInput",
    "ReductionOutcome",
]
