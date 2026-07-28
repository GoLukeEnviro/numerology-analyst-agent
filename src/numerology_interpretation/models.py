"""Structured interpretation contracts with explicit statement classes."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from numerology_domain.enums import ClaimType


class _InterpretationModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class InterpretationClaim(_InterpretationModel):
    claim_type: ClaimType
    text: str
    calculation_ref: str
    knowledge_ref: str
    composer_rule_id: str | None = None
    uncertainty: str | None = None
    counter_hypothesis: str | None = None


class InterpretationSection(_InterpretationModel):
    subject: str
    number: int
    title: str
    claims: tuple[InterpretationClaim, ...]
    counter_hypotheses: tuple[str, ...]


class InterpretationResult(_InterpretationModel):
    schema_version: str = "interpretation-result-v1"
    knowledge_bundle: str
    calculation_hash: str
    scientific_position: str
    sections: tuple[InterpretationSection, ...]
