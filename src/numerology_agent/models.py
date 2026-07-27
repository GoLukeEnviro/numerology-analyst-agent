"""Strict contracts crossing the LLM boundary.

Schema-versioning policy (PR B, DeepSeek-Live-Aktivierung):
- ``*-v1`` models are READ structures for migration/import of legacy data;
  they remain importable and validatable.
- ``*-v2`` models are the only structures NEWLY PRODUCED by the agent service.
- ``AnalysisProvenance`` carries nullable ``temperature``/``top_p`` because the
  DeepSeek thinking mode (``reasoning_effort="high"``) makes sampling
  parameters ineffective — they are reported as ``None`` and sampling is
  ``provider_managed``. Legacy v1 data (with concrete floats) remains valid
  against this nullable superset, so v1 imports keep working.
- ``reasoning_content`` (DeepSeek thinking trace) is NEVER modelled as a field.
  It must not appear in ``ProviderResult``, ``AnalysisReport``/``-FollowUp``,
  exports, logs or API responses (see ``test_reasoning_content_hygiene``).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from numerology_domain.enums import ClaimType


class _AgentModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProviderResult(_AgentModel):
    """Provider response.

    Deliberately carries NO ``reasoning_content`` field: the DeepSeek thinking
    trace must not cross the provider boundary into provenance, reports,
    exports, logs or API responses.
    """

    content: str
    model: str
    provider_fingerprint: str | None = None
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)


class AnalysisClaim(_AgentModel):
    claim_type: ClaimType
    text: str = Field(min_length=1, max_length=1200)
    calculation_ref: str = Field(min_length=1, max_length=100)
    knowledge_ref: str = Field(min_length=1, max_length=160)
    number: int = Field(ge=0, le=99)
    uncertainty: str | None = Field(default=None, max_length=600)
    counter_hypothesis: str | None = Field(default=None, max_length=600)
    composer_rule_id: str | None = Field(default=None, max_length=120)


class AnalysisSection(_AgentModel):
    title: str = Field(min_length=1, max_length=160)
    claims: tuple[AnalysisClaim, ...] = Field(min_length=1, max_length=12)


class AnalysisDraft(_AgentModel):
    summary: str = Field(min_length=1, max_length=3000)
    sections: tuple[AnalysisSection, ...] = Field(min_length=1, max_length=16)
    limitations: tuple[str, ...] = Field(min_length=1, max_length=12)
    suggestions: tuple[str, ...] = Field(max_length=12)


class AnalysisProvenance(_AgentModel):
    """Provenance shared by v1 (read) and v2 (write) reports.

    ``temperature``/``top_p`` are nullable because the DeepSeek thinking mode
    renders them ineffective (provider-managed sampling). Legacy v1 data with
    concrete floats validates unchanged against this superset.
    """

    provider: str
    model: str
    temperature: float | None = None
    top_p: float | None = None
    thinking: str
    effective_sampling: Literal["provider_managed"] = "provider_managed"
    reasoning_effort: Literal["high"] = "high"
    prompt_version: str
    knowledge_bundle: str
    calculation_hash: str
    provider_fingerprint: str | None
    prompt_tokens: int
    completion_tokens: int
    context_signature: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


class AnalysisReportV1(_AgentModel):
    """Legacy v1 read structure (migration/import only)."""

    schema_version: Literal["analysis-report-v1"] = "analysis-report-v1"
    summary: str
    sections: tuple[AnalysisSection, ...]
    limitations: tuple[str, ...]
    suggestions: tuple[str, ...]
    provenance: AnalysisProvenance


class AnalysisReport(_AgentModel):
    """Canonical v2 report — the only structure newly produced by the agent."""

    schema_version: Literal["analysis-report-v2"] = "analysis-report-v2"
    summary: str
    sections: tuple[AnalysisSection, ...]
    limitations: tuple[str, ...]
    suggestions: tuple[str, ...]
    provenance: AnalysisProvenance


class FollowUpDraft(_AgentModel):
    answer: str = Field(min_length=1, max_length=3000)
    claims: tuple[AnalysisClaim, ...] = Field(min_length=1, max_length=8)
    limitations: tuple[str, ...] = Field(min_length=1, max_length=8)


class AnalysisFollowUpV1(_AgentModel):
    """Legacy v1 follow-up read structure (migration/import only)."""

    schema_version: Literal["analysis-follow-up-v1"] = "analysis-follow-up-v1"
    answer: str
    claims: tuple[AnalysisClaim, ...]
    limitations: tuple[str, ...]
    provenance: AnalysisProvenance


class AnalysisFollowUp(_AgentModel):
    """Canonical v2 follow-up — the only structure newly produced by the agent."""

    schema_version: Literal["analysis-follow-up-v2"] = "analysis-follow-up-v2"
    answer: str
    claims: tuple[AnalysisClaim, ...]
    limitations: tuple[str, ...]
    provenance: AnalysisProvenance


class ProviderRequestV1(_AgentModel):
    """Legacy v1 provider request (migration/import only)."""

    prompt_version: Literal["numra-report-de-v1"] = "numra-report-de-v1"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    knowledge: tuple[dict[str, Any], ...]
    safety_rules: tuple[str, ...]


class ProviderRequest(_AgentModel):
    """Canonical v2 provider request."""

    prompt_version: Literal["numra-report-de-v2"] = "numra-report-de-v2"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    knowledge: tuple[dict[str, Any], ...]
    safety_rules: tuple[str, ...]


class FollowUpProviderRequestV1(_AgentModel):
    """Legacy v1 follow-up provider request (migration/import only)."""

    prompt_version: Literal["numra-follow-up-de-v1"] = "numra-follow-up-de-v1"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    report: dict[str, Any]
    question: str
    safety_rules: tuple[str, ...]


class FollowUpProviderRequest(_AgentModel):
    """Canonical v2 follow-up provider request."""

    prompt_version: Literal["numra-follow-up-de-v2"] = "numra-follow-up-de-v2"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    report: dict[str, Any]
    question: str
    safety_rules: tuple[str, ...]
