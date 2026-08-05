"""V3 fact models — AnalysisFactEntryV3, AnalysisFactPackageV3, ProviderFactPackageV3.

These models exist in parallel to ``models.py`` (V1/V2 stack).  The internal
``AnalysisFactPackageV3`` is request-scoped, transient and never persisted.
The minimised ``ProviderFactPackageV3`` is the only structure sent to DeepSeek.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from numerology_domain.models import KarmicOccurrence


class _FactModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AnalysisFactEntryV3(_FactModel):
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


class AnalysisFactPackageV3(_FactModel):
    """Full, internal fact package — request-scoped, transient, never persisted."""

    calculation_hash: str
    profile_schema_version: str
    method_version: str
    entries: tuple[AnalysisFactEntryV3, ...]


class ProviderFactPackageV3(_FactModel):
    """Minimised, closed-book fact package sent to DeepSeek.

    Derived from ``AnalysisFactPackageV3`` via ``derive_provider_fact_package_v3()``.
    Contains no full names, letter chains, technical traces or audit metadata.
    """

    calculation_hash: str
    method_version: str = ""
    entries: tuple[dict[str, object], ...] = ()
