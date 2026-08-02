"""Input contracts — PersonInput and MethodPolicy (Master Contract §6.1/§6.2).

Private submodule of ``numerology_domain._models``.  The public surface is
the ``numerology_domain.models`` compatibility facade.
"""

from __future__ import annotations

from datetime import date

from pydantic import Field, field_validator, model_validator

from numerology_domain._models.base import _FrozenModel
from numerology_domain.enums import (
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

# Pythagorean method version tags (ADR set + Master Contract §3.2).
PYTHAGOREAN_V1_VERSION = "v1"
PYTHAGOREAN_V2_VERSION = "v2"
VALID_PYTHAGOREAN_VERSIONS: frozenset[str] = frozenset(
    {PYTHAGOREAN_V1_VERSION, PYTHAGOREAN_V2_VERSION}
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
        # pythagorean-v1 and pythagorean-v2 are the only implemented versions
        # (calculation-engineer contract §4: "Methodenversionen vermischen" is forbidden).
        if (
            self.system is MethodSystem.PYTHAGOREAN
            and self.version not in VALID_PYTHAGOREAN_VERSIONS
        ):
            raise ValueError(
                f"pythagorean system requires one of {sorted(VALID_PYTHAGOREAN_VERSIONS)!r}, "
                f"got {self.version!r}"
            )
        return self
