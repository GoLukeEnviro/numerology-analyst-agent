"""V3 fact and report models — parallel to ``models.py`` (V1/V2 stack).

Fact models (Welle 2): ``AnalysisFactEntryV3``, ``AnalysisFactPackageV3``, ``ProviderFactPackageV3``.
Report models (Welle 3): ``ClaimV3``, ``AnalysisSectionV3``, ``AnalysisReportV3``, etc.
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from numerology_domain.enums import ClaimType
from numerology_domain.models import KarmicOccurrence


class _AgentModelV3(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# Fact models (Welle 2)
# ---------------------------------------------------------------------------


class AnalysisFactEntryV3(_AgentModelV3):
    """A single deterministic calculation fact extracted from a V4 profile."""

    calculation_ref: str
    result_context: str
    role: Literal["primary", "secondary", "supporting"]
    raw_total: int
    reduction_chain: tuple[int, ...]
    root_value: int
    held_master_value: int | None = None
    display_notation: str
    is_master: bool = False
    compound_classification: str | None = None
    karmic_occurrences: tuple[KarmicOccurrence, ...] = ()
    calculation_method: str = ""
    method_version: str = ""
    components: tuple[int, ...] = ()
    trace_ref: str = ""


class AnalysisFactPackageV3(_AgentModelV3):
    """Full, internal fact package — request-scoped, transient, never persisted."""

    calculation_hash: str
    profile_schema_version: str
    method_version: str
    entries: tuple[AnalysisFactEntryV3, ...]


class ProviderFactPackageV3(_AgentModelV3):
    """Minimised, closed-book fact package sent to DeepSeek."""

    calculation_hash: str
    method_version: str = ""
    entries: tuple[dict[str, object], ...] = ()


# ---------------------------------------------------------------------------
# Report models (Welle 3)
# ---------------------------------------------------------------------------

#: The 18 fixed section IDs for analysis-report-v3.
VALID_SECTION_IDS: frozenset[str] = frozenset(
    {
        "executive_overview",
        "life_path_and_purpose",
        "birthday_and_attitude",
        "inner_motivation",
        "expression_and_external_persona",
        "maturity_and_development",
        "number_harmonies",
        "number_tensions",
        "repetitions_and_missing_values",
        "life_phases",
        "personal_cycles",
        "pinnacles",
        "challenges",
        "shadow_patterns",
        "development_opportunities",
        "practical_integration",
        "final_synthesis",
        "method_and_calculation_notes",
    }
)

SECTION_ORDER: tuple[str, ...] = (
    "executive_overview",
    "life_path_and_purpose",
    "birthday_and_attitude",
    "inner_motivation",
    "expression_and_external_persona",
    "maturity_and_development",
    "number_harmonies",
    "number_tensions",
    "repetitions_and_missing_values",
    "life_phases",
    "personal_cycles",
    "pinnacles",
    "challenges",
    "shadow_patterns",
    "development_opportunities",
    "practical_integration",
    "final_synthesis",
    "method_and_calculation_notes",
)


class ClaimV3(_AgentModelV3):
    claim_id: str
    claim_type: ClaimType = ClaimType.INTERPRETIVE_HYPOTHESIS
    text: str = Field(min_length=1, max_length=1200)
    calculation_refs: tuple[str, ...] = ()
    knowledge_refs: tuple[str, ...] = ()
    uncertainty: str | None = Field(default=None, max_length=600)
    composer_rule_id: str | None = None


class AnalysisSectionV3(_AgentModelV3):
    section_id: str
    applicable: bool = True
    model_heading: str | None = None
    summary: str = Field(min_length=1, max_length=2000)
    claims: tuple[ClaimV3, ...] = ()
    supporting_calculation_refs: tuple[str, ...] = ()
    supporting_knowledge_refs: tuple[str, ...] = ()
    counter_hypotheses: tuple[str, ...] = ()
    reflection_questions: tuple[str, ...] = ()
    practical_options: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_applicability(self) -> "AnalysisSectionV3":
        if self.applicable:
            if not 1 <= len(self.claims) <= 4:
                raise ValueError(
                    f"applicable section {self.section_id!r} requires 1-4 claims, "
                    f"got {len(self.claims)}"
                )
        else:
            if (
                self.claims
                or self.supporting_calculation_refs
                or self.supporting_knowledge_refs
            ):
                raise ValueError(
                    f"non-applicable section {self.section_id!r} must contain "
                    f"no claims or references"
                )
        return self


class AnalysisReportContentV3(_AgentModelV3):
    summary: str = Field(min_length=1, max_length=2000)
    sections: tuple[AnalysisSectionV3, ...]
    global_limitations: tuple[str, ...] = ()


class AnalysisProvenanceV3(_AgentModelV3):
    provider: str
    model: str
    thinking: str = "enabled"
    effective_sampling: Literal["provider_managed"] = "provider_managed"
    reasoning_effort: Literal["high"] = "high"
    prompt_version: str
    knowledge_bundle: str
    calculation_hash: str
    provider_fingerprint: str | None = None
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    context_signature: str = Field(min_length=64, max_length=64)


class AnalysisReportV3(_AgentModelV3):
    schema_version: Literal["analysis-report-v3"] = "analysis-report-v3"
    report_id: UUID
    content: AnalysisReportContentV3
    report_content_hash: str = Field(min_length=64, max_length=64)
    generation_context_hash: str = Field(min_length=64, max_length=64)
    provenance: AnalysisProvenanceV3
    context_signature: str = Field(min_length=64, max_length=64)


class AnalysisDraftV3(_AgentModelV3):
    content: AnalysisReportContentV3


class ProviderRequestV3(_AgentModelV3):
    prompt_version: Literal["numra-report-de-v3"] = "numra-report-de-v3"
    calculation_hash: str
    facts: tuple[dict[str, Any], ...]
    knowledge: tuple[dict[str, Any], ...]
    safety_rules: tuple[str, ...]
    section_plan: tuple[str, ...] = SECTION_ORDER


class FollowUpDraftV3(_AgentModelV3):
    answer: str = Field(min_length=1, max_length=3000)
    claims: tuple[ClaimV3, ...] = Field(min_length=1, max_length=8)
    limitations: tuple[str, ...] = Field(min_length=1, max_length=8)


class AnalysisFollowUpV3(_AgentModelV3):
    schema_version: Literal["analysis-follow-up-v3"] = "analysis-follow-up-v3"
    follow_up_id: UUID
    report_id: UUID
    answer: str
    claims: tuple[ClaimV3, ...]
    limitations: tuple[str, ...]
    provenance: AnalysisProvenanceV3
    context_signature: str = Field(min_length=64, max_length=64)


class FollowUpProviderRequestV3(_AgentModelV3):
    prompt_version: Literal["numra-follow-up-de-v3"] = "numra-follow-up-de-v3"
    calculation_hash: str
    report_summary: str
    question: str
    safety_rules: tuple[str, ...]
