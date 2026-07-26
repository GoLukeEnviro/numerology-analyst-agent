"""Exception hierarchy for the numerology domain.

All engine/validation failures raise a subclass of :class:`NumerologyError`.
This keeps the boundary clean: callers catch ``NumerologyError``, the
deterministic core never leaks unexpected runtime types.
"""

from __future__ import annotations


class NumerologyError(Exception):
    """Base class for every domain error."""


class ValidationError(NumerologyError):
    """Raised when ``PersonInput`` or ``MethodPolicy`` is invalid."""


class NormalizationError(NumerologyError):
    """Raised when a name cannot be normalized deterministically."""


class CalculationError(NumerologyError):
    """Raised when a calculation cannot be completed deterministically."""


class PolicyError(NumerologyError):
    """Raised when a policy combination is unsupported or contradictory.

    Example: requesting ``DE_EXPANDED_V1`` mixing with ``DE_DIRECT_V1``
    in one calculation (ADR 0002 §7), or an unknown ``y_mode``.
    """


class PersonBirthDateInFutureError(ValidationError):
    """Raised when a person profile's birth_date is later than as_of_date.

    Korrektur 3: person profiles forbid a birth date in the future relative
    to the explicit evaluation date. General date analysis (later command)
    is a separate use case and remains permitted for future dates.
    """


class DisambiguationRequired(NumerologyError):
    """Raised (optionally) when a Y classification is ambiguous (ADR 0001).

    The Walking Skeleton does not raise this from the happy path; the
    phonetic policy instead marks ``disambiguation_required`` in the trace
    and emits both variants when ambiguous (ADR 0001 Option B, recommended
    in the V1 minimal scope). This exception exists for callers that opt
    into the strict (Option A) behavior.
    """
