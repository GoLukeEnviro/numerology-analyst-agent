"""Fail-closed language and claim-classification validation."""

from __future__ import annotations

import re

from numerology_domain.enums import ClaimType
from numerology_interpretation.models import InterpretationClaim

_FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "diagnostic_language",
        re.compile(
            r"\b(depressiv|bipolar|narzisst\w*|autistisch|traumatisiert|psychisch krank)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "absolute_language",
        re.compile(r"\b(definitiv|garantiert|zweifellos|immer|niemals)\b", re.IGNORECASE),
    ),
    ("identity_assertion", re.compile(r"\bdu bist\b", re.IGNORECASE)),
    ("prediction", re.compile(r"\bdu wirst\b", re.IGNORECASE)),
)


class SafetyError(ValueError):
    """Raised when text or claim metadata violates Numra's safety contract."""


def assert_text_safe(text: str) -> None:
    """Reject diagnostic, absolute, identity-defining and predictive language."""
    for code, pattern in _FORBIDDEN_PATTERNS:
        if pattern.search(text):
            raise SafetyError(f"{code}: unsafe language detected")


def assert_claims_safe(claims: tuple[InterpretationClaim, ...]) -> None:
    """Validate both statement class and language for interpretation-layer claims."""
    for claim in claims:
        if claim.claim_type is ClaimType.CALCULATION_FACT:
            raise SafetyError("calculation_fact is reserved for deterministic engine output")
        assert_text_safe(claim.text)
