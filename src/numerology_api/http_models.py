"""Versioned HTTP-boundary models for the Numra API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from numerology_agent.models import AnalysisReport
from numerology_domain.enums import ClaimType
from numerology_domain.models import (
    AuditTrace,
    ConsistencyStatus,
    CycleCalculationResult,
    LifePathResult,
    MethodPolicy,
    NameNumberVariant,
    NameSegmentResult,
    NumberResult,
    PersonInput,
    ProfileCalculationResult,
)


class _HttpModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileCalculationRequest(_HttpModel):
    """Explicit person and method policy submitted to the deterministic core."""

    person: PersonInput
    policy: MethodPolicy


class LegacyV2NameNumberSet(_HttpModel):
    """Historical V2 name contract, accepted only for server-side recalculation."""

    basis: str
    original_name: str
    normalized_name: str
    segments: tuple[NameSegmentResult, ...]
    expression: NumberResult
    soul_urge: NumberResult
    personality: NumberResult
    y_classifications: tuple[str, ...] = ()
    variants: tuple[NameNumberVariant, ...] = ()


class LegacyV2ProfileCalculationResult(_HttpModel):
    """Read-only V2 envelope; calculated fields are never trusted by the API."""

    claim_type: ClaimType = ClaimType.CALCULATION_FACT
    name: str = "complete_profile"
    schema_version: Literal["profile-calculation-result-v2"]
    input_ref: PersonInput
    policy: MethodPolicy
    life_path_a: LifePathResult
    life_path_b: LifePathResult
    consistency: ConsistencyStatus
    birthday: NumberResult
    attitude: NumberResult
    core_name: LegacyV2NameNumberSet | None = None
    active_name: LegacyV2NameNumberSet | None = None
    maturity: NumberResult
    cycles: CycleCalculationResult
    trace: AuditTrace
    deterministic_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


AnalysisProfile = ProfileCalculationResult | LegacyV2ProfileCalculationResult


class AnalysisReportRequest(_HttpModel):
    consent: Literal[True]
    device_id: str = Field(min_length=16, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    profile: AnalysisProfile


class AnalysisFollowUpRequest(_HttpModel):
    consent: Literal[True]
    device_id: str = Field(min_length=16, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    profile: AnalysisProfile
    report: AnalysisReport
    question: str = Field(min_length=1, max_length=500)


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
    status: Literal["ready", "unavailable"] = "ready"
    engine: Literal["ready"] = "ready"
    redis: Literal["not_configured", "ready", "unavailable"] = "not_configured"
    provider: Literal["disabled", "configured"] = "disabled"


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
