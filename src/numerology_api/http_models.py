"""Versioned HTTP-boundary models for the Numra API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from numerology_domain.models import MethodPolicy, PersonInput


class _HttpModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileCalculationRequest(_HttpModel):
    """Explicit person and method policy submitted to the deterministic core."""

    person: PersonInput
    policy: MethodPolicy


class FieldError(_HttpModel):
    field: str
    message: str
    code: str


class ProblemDetails(_HttpModel):
    """RFC-9457-style API error with a stable machine-readable code."""

    type: str
    title: str
    status: int
    code: str
    detail: str
    correlation_id: str
    field_errors: tuple[FieldError, ...] = ()


class LiveStatus(_HttpModel):
    status: Literal["ok"] = "ok"


class ReadyStatus(_HttpModel):
    status: Literal["ready"] = "ready"
    engine: Literal["ready"] = "ready"
    redis: Literal["not_configured"] = "not_configured"
    provider: Literal["disabled"] = "disabled"


class LlmMeta(_HttpModel):
    enabled: bool = False
    provider: str | None = None


class MetaResponse(_HttpModel):
    api_version: Literal["v1"] = "v1"
    package_version: str
    method_system: Literal["pythagorean"] = "pythagorean"
    method_version: Literal["v1"] = "v1"
    profile_schema_version: str
    knowledge_bundle: str
    llm: LlmMeta = Field(default_factory=LlmMeta)
