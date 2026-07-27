"""Strict contracts crossing the LLM boundary."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from numerology_domain.enums import ClaimType


class _AgentModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProviderResult(_AgentModel):
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


class AnalysisSection(_AgentModel):
    title: str = Field(min_length=1, max_length=160)
    claims: tuple[AnalysisClaim, ...] = Field(min_length=1, max_length=12)


class AnalysisDraft(_AgentModel):
    summary: str = Field(min_length=1, max_length=3000)
    sections: tuple[AnalysisSection, ...] = Field(min_length=1, max_length=16)
    limitations: tuple[str, ...] = Field(min_length=1, max_length=12)
    suggestions: tuple[str, ...] = Field(max_length=12)


class AnalysisProvenance(_AgentModel):
    provider: str
    model: str
    temperature: float
    top_p: float
    thinking: str
    effective_sampling: Literal["provider_managed"] = "provider_managed"
    reasoning_effort: Literal["high"] = "high"
    prompt_version: str
    knowledge_bundle: str
    calculation_hash: str
    provider_fingerprint: str | None
    prompt_tokens: int
    completion_tokens: int


class AnalysisReport(_AgentModel):
    schema_version: Literal["analysis-report-v1"] = "analysis-report-v1"
    summary: str
    sections: tuple[AnalysisSection, ...]
    limitations: tuple[str, ...]
    suggestions: tuple[str, ...]
    provenance: AnalysisProvenance


class FollowUpDraft(_AgentModel):
    answer: str = Field(min_length=1, max_length=3000)
    claims: tuple[AnalysisClaim, ...] = Field(min_length=1, max_length=8)
    limitations: tuple[str, ...] = Field(min_length=1, max_length=8)


class AnalysisFollowUp(_AgentModel):
    schema_version: Literal["analysis-follow-up-v1"] = "analysis-follow-up-v1"
    answer: str
    claims: tuple[AnalysisClaim, ...]
    limitations: tuple[str, ...]
    provenance: AnalysisProvenance


class ProviderRequest(_AgentModel):
    prompt_version: Literal["numra-report-de-v1"] = "numra-report-de-v1"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    knowledge: tuple[dict[str, Any], ...]
    safety_rules: tuple[str, ...]


class FollowUpProviderRequest(_AgentModel):
    prompt_version: Literal["numra-follow-up-de-v1"] = "numra-follow-up-de-v1"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    report: dict[str, Any]
    question: str
    safety_rules: tuple[str, ...]
