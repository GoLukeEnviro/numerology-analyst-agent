"""Domain models - the binding contracts of the Numerology Analyst Agent.

Implements Master Implementation Contract §6.1 (PersonInput), §6.2
(MethodPolicy) and §6.3 (CalculationResult), plus the audit-trace
primitives required by the deterministic core.

Design rules enforced here:
* All models are ``frozen`` (immutable) - determinism requires that an
  input cannot mutate after entering the core (Master Contract §2.4).
* ``extra='forbid'`` - no silent defaults sneak in (Master Contract §6.2).
* ``str_strip_whitespace=True`` on the models that carry free text, so
  ``"  Max  "`` and ``"Max"`` are treated identically.
* No ``Any`` types. No network. No time/randomness. Pure data.
"""

from __future__ import annotations

from datetime import date
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from numerology_domain.enums import (
    ClaimType,
    DateMethod,
    Locale,
    MethodSystem,
    NameBasis,
    UmlautPolicy,
    YMode,
)

# Master numbers (held, never reduced further) and karmic debt markers.
# Karmic debts are metadata only in 0.1.0 - they are flagged, never
# "evaluated" into an interpretation (Master Contract §3.2).
MASTER_NUMBERS: frozenset[int] = frozenset({11, 22, 33})
KARMIC_DEBTS: frozenset[int] = frozenset({13, 14, 16, 19})

# Pythagorean method version tag (ADR set + Master Contract §3.2).
PYTHAGOREAN_V1_VERSION = "v1"


class _FrozenModel(BaseModel):
    """Common config for every domain model: immutable + no extra fields."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class PersonInput(_FrozenModel):
    """Person input contract (Master Contract §6.1).

    The Walking Skeleton (0.1.0) only consumes ``core_name`` and
    ``birth_date`` for the Life Path calculation, but the full contract is
    modelled here so later name-based numbers (Expression, Soul Urge,
    Personality, Maturity - Phase 4+) can reuse the same input without a
    breaking migration.

    * ``core_name`` - full birth name (authoritative for the core profile,
      ADR 0004 §1). Required.
    * ``active_name`` - currently used name, optional. When present and
      different from ``core_name`` it triggers the supplementary profile
      (ADR 0004 §2). Never silently merged with ``core_name``.
    * ``birth_date`` - calendar date of birth. The Life Path A/B
      calculations operate exclusively on this field.
    * ``as_of_date`` - explicit evaluation date for deterministic tests.
      MUST be >= ``birth_date`` for a person profile (Korrektur 3); the
      domain core never calls ``date.today()`` - the CLI defaults this at
      its own boundary (Korrektur 2). General date analysis (later) will
      not carry this constraint.
    """

    core_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full birth name (authoritative).",
    )
    birth_date: date = Field(..., description="Calendar date of birth (YYYY-MM-DD).")
    as_of_date: date = Field(
        ...,
        description=(
            "Explicit evaluation date for deterministic tests. "
            "birth_date must be <= as_of_date for a person profile."
        ),
    )
    active_name: str | None = Field(
        default=None,
        max_length=200,
        description="Currently used name; optional supplementary profile basis.",
    )
    locale: Locale = Field(default=Locale.DE, description="Normalization locale selector.")
    consent_given: bool = Field(
        default=False,
        description="Whether the data subject consented to processing.",
    )

    @field_validator("core_name", "active_name")
    @classmethod
    def _non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.strip():
            raise ValueError("name must contain at least one non-whitespace character")
        # NFC-normalize the stored original so visually identical inputs are
        # byte-identical (ADR 0002 §2 - storage uses Unicode NFC).
        import unicodedata

        return unicodedata.normalize("NFC", v)

    @model_validator(mode="after")
    def _birth_date_not_in_future(self) -> PersonInput:
        # Korrektur 3: a person profile must not have a birth_date later than
        # the evaluation date. General date analysis is a separate command
        # (extension point, not modelled here).
        if self.birth_date > self.as_of_date:
            raise ValueError(
                "PERSON_BIRTH_DATE_IN_FUTURE: birth_date must be <= as_of_date "
                f"(birth_date={self.birth_date}, as_of_date={self.as_of_date})"
            )
        return self

    @model_validator(mode="after")
    def _active_differs_from_core_if_set(self) -> PersonInput:
        if self.active_name is not None and self.active_name == self.core_name:
            # An active name equal to the core name carries no information;
            # normalize to None so downstream code can rely on the invariant
            # "active_name is None IFF no name change".
            return self.model_copy(update={"active_name": None})
        return self


class MethodPolicy(_FrozenModel):
    """Explicit method configuration (Master Contract §6.2).

    No silent defaults: every policy dimension relevant to 0.1.0 is an
    explicit field with a documented canonical default. Mixing
    incompatible policies (e.g. two umlaut policies) is rejected.
    """

    system: MethodSystem = Field(default=MethodSystem.PYTHAGOREAN)
    version: str = Field(default=PYTHAGOREAN_V1_VERSION, description="Method version tag.")
    y_mode: YMode = Field(default=YMode.PHONETIC, description="Y classification (ADR 0001).")
    umlaut_policy: UmlautPolicy = Field(
        default=UmlautPolicy.DE_DIRECT_V1,
        description="Umlaut/accent normalization (ADR 0002).",
    )
    name_basis: NameBasis = Field(
        default=NameBasis.BOTH_SEPARATE,
        description="core_name vs active_name selection (ADR 0004).",
    )
    date_method: DateMethod = Field(
        default=DateMethod.BOTH,
        description="Life Path A/B selection (Master Contract §3.2).",
    )
    locale: Locale = Field(default=Locale.DE, description="Normalization locale.")
    master_numbers: frozenset[int] = Field(
        default=MASTER_NUMBERS,
        description="Numbers held as-is during reduction.",
    )

    @field_validator("version")
    @classmethod
    def _non_empty_version(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("version must be non-empty")
        return v

    @model_validator(mode="after")
    def _system_version_consistent(self) -> MethodPolicy:
        # pythagorean-v1 is the only implemented version (calculation-engineer
        # contract §4: "Methodenversionen vermischen" is forbidden). We do not
        # hard-fail on other version strings yet (other systems are documented
        # extension points), but we record the canonical pairing.
        if self.system is MethodSystem.PYTHAGOREAN and self.version != PYTHAGOREAN_V1_VERSION:
            raise ValueError(
                f"pythagorean system requires version {PYTHAGOREAN_V1_VERSION!r}, "
                f"got {self.version!r}"
            )
        return self


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


# Schema version for the CalculationResult contract (v0.1.3 contract integrity).
# Bumped when the JSON shape of CalculationResult changes in a way that
# affects the deterministic hash.
CALCULATION_RESULT_SCHEMA_VERSION = "calculation-result-v1"
PROFILE_CALCULATION_RESULT_SCHEMA_VERSION = "profile-calculation-result-v2"


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
    """Expression, Soul Urge and Personality values for one separately held name."""

    basis: str
    original_name: str
    normalized_name: str
    segments: tuple[NameSegmentResult, ...]
    expression: NumberResult
    soul_urge: NumberResult
    personality: NumberResult
    y_classifications: tuple[str, ...] = Field(default_factory=tuple)
    variants: tuple[NameNumberVariant, ...] = Field(default_factory=tuple)


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
    core_name: NameNumberSet
    active_name: NameNumberSet | None = None
    maturity: NumberResult
    cycles: CycleCalculationResult
    trace: AuditTrace
    deterministic_hash: str = ""
