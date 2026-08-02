"""Calculation contracts — reduction, trace and result models.

Private submodule of ``numerology_domain._models``.  The public surface is
the ``numerology_domain.models`` compatibility facade.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field, model_validator

from numerology_domain._models.base import _FrozenModel
from numerology_domain._models.input import (
    KARMIC_DEBTS,
    MASTER_NUMBERS,
    MethodPolicy,
    PersonInput,
)
from numerology_domain.enums import ClaimType

# Schema version for the CalculationResult contract (v0.1.3 contract integrity).
# Bumped when the JSON shape of CalculationResult changes in a way that
# affects the deterministic hash.
CALCULATION_RESULT_SCHEMA_VERSION = "calculation-result-v1"
PROFILE_CALCULATION_RESULT_SCHEMA_VERSION = "profile-calculation-result-v3"


class CalculationStep(_FrozenModel):
    """A single auditable step in a calculation (Master Contract §6.3).

    The deterministic hash of a result is computed over the sorted JSON of
    its steps, so every step must carry exactly the fields that influence
    the outcome - nothing more, nothing less.
    """

    label: str = Field(..., description="Human-readable step identifier (stable).")
    inputs: tuple[int, ...] = Field(
        default_factory=tuple,
        description="Numeric inputs consumed by this step, in order.",
    )
    output: int = Field(..., description="Numeric output produced by this step.")
    note: str = Field(default="", description="Optional deterministic note (no free text logic).")


class NormalizationStep(_FrozenModel):
    """A single normalization transformation (ADR 0002 §6)."""

    step: str = Field(..., description="Stable step identifier (e.g. 'unicode_nfc').")
    input: str = Field(..., description="Input string before the transformation.")
    output: str = Field(..., description="Output string after the transformation.")
    note: str = Field(default="", description="Optional deterministic note.")


class ReductionOutcome(_FrozenModel):
    """A reduced numeric result with master-number metadata.

    ``value`` is always in ``1..9`` or one of the configured master numbers.
    ``intermediate`` is the pre-reduction sum (useful for the audit trace).

    Karmic-debt detection moved OFF this primitive (Korrektur 1): the marker
    is only meaningful on the *methodically defined unreduced core value*
    of a Life Path method, not on arbitrary intermediate sums. The karmic
    info therefore lives on :class:`LifePathResult` (``karmic_debt``), not
    here. This primitive stays focused on numeric reduction + master-flag.
    """

    value: int = Field(..., description="Reduced value (1..9 or a master number).")
    intermediate: int = Field(..., description="Sum fed into the reduction.")
    is_master: bool = Field(default=False, description="True iff value is a master number.")

    @model_validator(mode="after")
    def _check_range(self) -> ReductionOutcome:
        if self.is_master and self.value not in MASTER_NUMBERS:
            raise ValueError(f"is_master=True but value {self.value} is not a master number")
        if not self.is_master and not (1 <= self.value <= 9):
            raise ValueError(f"non-master value {self.value} out of range 1..9")
        return self


class KarmicDebtInfo(_FrozenModel):
    """Methodically defined karmic debt number with its origin (Korrektur 1).

    The marker is attached ONLY when the *unreduced core value* of a Life
    Path method (the raw total before the first reduction step) is one of
    {13, 14, 16, 19}. Random intermediate sums are NOT karmic markers.
    ``origin`` records which methodical component produced the value, e.g.
    ``'total_sum'`` (Life Path A) or ``'component_sum'`` (Life Path B).
    """

    number: int = Field(..., description="Karmic debt number (13, 14, 16 or 19).")
    origin: str = Field(
        ...,
        description="Methodical component that produced the value (e.g. 'total_sum').",
    )

    @model_validator(mode="after")
    def _check_karmic_range(self) -> KarmicDebtInfo:
        if self.number not in KARMIC_DEBTS:
            raise ValueError(
                f"karmic number must be one of {sorted(KARMIC_DEBTS)}, got {self.number}"
            )
        if not self.origin.strip():
            raise ValueError("origin must be non-empty")
        return self


class LifePathResult(_FrozenModel):
    """Life Path result for one reduction method (A or B).

    Carries the *methodically defined unreduced core value* (``raw_total``)
    alongside the final reduced value, the slash-notation reduction path
    (``compound_notation``) and an optional karmic-debt marker attached to
    that raw total (Korrektur 1).
    """

    method: str = Field(..., description="'sum_all_digits' (A) or 'component_then_sum' (B).")
    reduction: ReductionOutcome
    raw_total: int = Field(
        ...,
        description="Methodically defined unreduced core value before the first reduction.",
    )
    reduced_value: int = Field(
        ...,
        description="Final reduced value (1-9 or a master number); mirrors reduction.value.",
    )
    compound_notation: str = Field(
        ...,
        description="Reduction path as slash-notation, e.g. '19/10/1' or '37/10/1'.",
    )
    karmic_debt: KarmicDebtInfo | None = Field(
        default=None,
        description="Karmic debt info iff raw_total is a karmic debt number, else None.",
    )
    components: dict[str, int] = Field(
        default_factory=dict,
        description="Per-component reductions (only for method B).",
    )
    steps: tuple[CalculationStep, ...] = Field(
        default_factory=tuple,
        description="Ordered audit steps for this method.",
    )

    @model_validator(mode="after")
    def _reduced_value_consistent(self) -> LifePathResult:
        if self.reduced_value != self.reduction.value:
            raise ValueError(
                f"reduced_value {self.reduced_value} must equal reduction.value {self.reduction.value}"
            )
        return self


class ConsistencyStatus(_FrozenModel):
    """A-vs-B consistency report (Master Contract §3.2)."""

    a_equals_b: bool
    life_path_a: int
    life_path_b: int
    warning: str = Field(default="", description="Empty when A == B.")


class AuditTrace(_FrozenModel):
    """Deterministic audit trail attached to every calculation result.

    The trace is one component of the CalculationHashEnvelope.
    The calculation hash also covers the schema version, relevant input
    fields, MethodPolicy and calculated results — not the trace alone.
    """

    normalization_steps: tuple[NormalizationStep, ...] = Field(default_factory=tuple)
    calculation_steps: tuple[CalculationStep, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    disambiguation_required: bool = Field(
        default=False,
        description="True iff an ambiguous Y (ADR 0001) or other ambiguity was hit.",
    )


class CalculationHashEnvelope(_FrozenModel):
    """Hash input contract (v0.1.3 contract integrity).

    The deterministic hash is computed over this envelope — NOT over the
    AuditTrace alone. This guarantees that input_ref, policy, schema_version,
    and results all contribute to the hash. The hash field itself is excluded.
    """

    schema_version: str = Field(
        default=CALCULATION_RESULT_SCHEMA_VERSION,
        description="Schema version of the CalculationResult shape.",
    )
    input_ref: PersonInput
    policy: MethodPolicy
    results: dict[str, object] = Field(
        default_factory=dict,
        description="Calculation results keyed by name (e.g. life_path_a, life_path_b).",
    )
    trace: AuditTrace


class CalculationResult(_FrozenModel):
    """Full calculation result (Master Contract §6.3).

    Carries the input reference, the policy used, the Life Path A/B
    outcomes, the consistency status and the audit trace. Everything
    needed to reproduce the result byte-for-byte is present.
    """

    # No claim_type default here: 0.1.0 only emits calculation_fact, but we
    # keep the field so later layers can attach traditional_claim etc.
    claim_type: ClaimType = Field(
        default=ClaimType.CALCULATION_FACT,
        description="Statement class (Master Contract §2.2).",
    )
    name: str = Field(default="life_path", description="Name of the calculated number.")
    schema_version: str = Field(
        default=CALCULATION_RESULT_SCHEMA_VERSION,
        description="Schema version of this result shape (v0.1.3 contract integrity).",
    )
    input_ref: PersonInput
    policy: MethodPolicy
    life_path_a: LifePathResult
    life_path_b: LifePathResult
    consistency: ConsistencyStatus
    trace: AuditTrace
    deterministic_hash: str = Field(
        default="",
        description="SHA-256 over the CalculationHashEnvelope; empty until computed.",
    )

    #: Stable marker so serialization layers never lose the statement class.
    CLAIM: ClassVar[ClaimType] = ClaimType.CALCULATION_FACT


class NumberResult(_FrozenModel):
    """One deterministic numerological value with a reproducible reduction path."""

    name: str
    raw_total: int = Field(..., ge=0)
    reduced_value: int = Field(..., ge=0)
    compound_notation: str
    is_master: bool = False
    components: dict[str, int] = Field(default_factory=dict)
    steps: tuple[CalculationStep, ...] = Field(default_factory=tuple)


class NameSegmentResult(_FrozenModel):
    """Auditable subtotal for one whitespace- or hyphen-delimited name segment."""

    text: str
    raw_total: int = Field(..., ge=1)
    reduced_value: int
    compound_notation: str


class NameNumberVariant(_FrozenModel):
    """A complete vowel/consonant result for one explicit Y interpretation."""

    label: str
    expression: NumberResult
    soul_urge: NumberResult
    personality: NumberResult


class NameNumberSet(_FrozenModel):
    """All name-derived values for one explicitly separated name profile."""

    basis: str
    original_name: str
    normalized_name: str
    segments: tuple[NameSegmentResult, ...]
    expression: NumberResult
    soul_urge: NumberResult
    personality: NumberResult
    maturity: NumberResult
    y_classifications: tuple[str, ...] = Field(default_factory=tuple)
    variants: tuple[NameNumberVariant, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# V2 schema additions — pythagorean-v2 contract
# ---------------------------------------------------------------------------

PROFILE_CALCULATION_RESULT_V4_SCHEMA_VERSION = "profile-calculation-result-v4"

_KARMIC_DEBT_ORIGIN_TYPES: frozenset[str] = frozenset(
    {"direct_raw", "reduction_intermediate", "component_total"}
)


class KarmicOccurrence(_FrozenModel):
    """A karmic debt value found during reduction with its precise origin type.

    origin_type distinguishes three cases (PR #19):
    * ``direct_raw`` — the methodically defined raw total itself is karmic
      (e.g. birthday=16).
    * ``reduction_intermediate`` — a karmic number appears as an intermediate
      step in the chain (e.g. expression 59→14→5).
    * ``component_total`` — the sum of reduced components is karmic
      (e.g. Life Path B component sum = 13).
    """

    value: int = Field(..., description="Karmic debt number (13, 14, 16 or 19).")
    origin_type: str = Field(
        ...,
        description="direct_raw | reduction_intermediate | component_total",
    )

    @model_validator(mode="after")
    def _validate(self) -> KarmicOccurrence:
        if self.value not in KARMIC_DEBTS:
            raise ValueError(f"value must be one of {sorted(KARMIC_DEBTS)}, got {self.value}")
        if self.origin_type not in _KARMIC_DEBT_ORIGIN_TYPES:
            raise ValueError(
                f"origin_type must be one of {sorted(_KARMIC_DEBT_ORIGIN_TYPES)}, "
                f"got {self.origin_type!r}"
            )
        return self


class NumberModel(_FrozenModel):
    """Rich V2 numeric model (PR #19) with full reduction chain, karmic origin
    differentiation, and master-number / compound classification.

    Replaces ``NumberResult`` for pythagorean-v2 code paths.  The two models
    coexist; pythagorean-v1 still uses ``NumberResult``.

    Key invariants:
    * ``root_value`` is ALWAYS in 1..9 (the final single-digit result).
    * ``held_master_value`` is ``None`` unless the chain passes through 11/22/33.
    * ``is_master`` is ``True`` iff ``held_master_value is not None``.
    * 44 is NOT a master number (``is_master=False`` for raw_total=44).
    * ``reduction_chain`` always ends at ``root_value`` (including past masters).
    * ``display_notation`` renders the chain as slash-notation.
    """

    raw_total: int = Field(..., ge=0)
    reduction_chain: tuple[int, ...] = Field(
        ...,
        description="Full chain from raw_total to root_value, e.g. (29,11,2).",
    )
    root_value: int = Field(
        ..., ge=0, le=9, description="Final 0-9 result (0 only for challenge=0)."
    )
    held_master_value: int | None = Field(
        default=None,
        description="Master number in chain (11/22/33) or None.",
    )
    display_notation: str = Field(
        ...,
        description="Slash notation, e.g. '29/11/2', '40/4', '22/4'.",
    )
    is_master: bool = Field(
        default=False,
        description="True only when held_master_value is not None (11/22/33; NOT 44).",
    )
    compound_classification: str | None = Field(
        default=None,
        description="master_number | karmic_debt | compound | None.",
    )
    karmic_occurrences: tuple[KarmicOccurrence, ...] = Field(
        default_factory=tuple,
        description="Karmic debt hits in this reduction, with origin context.",
    )
    components: tuple[int, ...] = Field(
        default_factory=tuple,
        description="Original summation components before the raw_total.",
    )
    steps: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Human-readable calculation steps for the audit trail.",
    )

    @model_validator(mode="after")
    def _check_invariants(self) -> NumberModel:
        if self.is_master and self.held_master_value is None:
            raise ValueError("is_master=True requires held_master_value to be set")
        if not self.is_master and self.held_master_value is not None:
            raise ValueError("is_master=False requires held_master_value to be None")
        if self.held_master_value is not None and self.held_master_value not in MASTER_NUMBERS:
            raise ValueError(
                f"held_master_value {self.held_master_value} is not in {sorted(MASTER_NUMBERS)}"
            )
        if not self.reduction_chain:
            raise ValueError("reduction_chain must not be empty")
        if self.reduction_chain[-1] != self.root_value:
            raise ValueError(
                f"reduction_chain last element {self.reduction_chain[-1]} "
                f"must equal root_value {self.root_value}"
            )
        if self.reduction_chain[0] != self.raw_total:
            raise ValueError(
                f"reduction_chain first element {self.reduction_chain[0]} "
                f"must equal raw_total {self.raw_total}"
            )
        return self


class NameNumberSetV2(_FrozenModel):
    """Name-derived numbers using the V2 NumberModel (pythagorean-v2)."""

    basis: str
    original_name: str
    normalized_name: str
    expression: NumberModel
    soul_urge: NumberModel
    personality: NumberModel
    maturity: NumberModel
    y_classifications: tuple[str, ...] = Field(default_factory=tuple)
