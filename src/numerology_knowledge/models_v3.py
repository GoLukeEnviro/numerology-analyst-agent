"""V3 knowledge models — parallel to ``models.py`` (V1/V2 stack).

Adds ``life_path_primary`` / ``life_path_secondary`` as separate
``ResultContextV3`` values and uses ``method_system = "pythagorean-v2"``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from numerology_knowledge.models import (
    AuthoringProvenance,
    ClaimClass,
    CompoundNotation,
    EntryClassification,
    KnowledgeSource,
    _KnowledgeModel,
)

# ---------------------------------------------------------------------------
# V3 result contexts (adds life_path_primary / life_path_secondary)
# ---------------------------------------------------------------------------

ResultContextV3 = Literal[
    "life_path_primary",
    "life_path_secondary",
    "birthday",
    "attitude",
    "expression",
    "soul_urge",
    "personality",
    "maturity",
    "personal_year",
    "personal_month",
    "personal_day",
    "pinnacle",
    "challenge",
]


# ---------------------------------------------------------------------------
# V3 knowledge entry
# ---------------------------------------------------------------------------


class KnowledgeEntryV3(_KnowledgeModel):
    """Canonical V3 knowledge entry for the pythagorean-v2 method system."""

    stable_id: str = Field(min_length=1, max_length=160)
    method_system: Literal["pythagorean-v2"] = "pythagorean-v2"
    classification: EntryClassification
    number: int = Field(ge=0, le=99)
    compound: CompoundNotation | None = None
    title: str = Field(min_length=1, max_length=200)
    claim_class: ClaimClass = "traditional_claim"
    constructive_expression: str = Field(min_length=1, max_length=800)
    shadow_expression: str = Field(min_length=1, max_length=800)
    development_theme: str = Field(min_length=1, max_length=400)
    traditional_claims: tuple[str, ...] = Field(min_length=1)
    reflection_prompts: tuple[str, ...] = Field(min_length=1)
    practical_suggestions: tuple[str, ...] = Field(min_length=1)
    counter_hypotheses: tuple[str, ...] = Field(min_length=1)
    uncertainty: str | None = Field(default=None, max_length=600)
    result_contexts: tuple[ResultContextV3, ...] = Field(min_length=1)
    source_refs: tuple[str, ...] = Field(min_length=1)
    authoring_provenance: AuthoringProvenance


# ---------------------------------------------------------------------------
# V3 knowledge bundle
# ---------------------------------------------------------------------------


class KnowledgeBundleV3(_KnowledgeModel):
    """Canonical V3 knowledge bundle for pythagorean-v2 profiles."""

    bundle_id: str
    locale: str
    version: Literal["v3"] = "v3"
    scientific_position: str
    sources: tuple[KnowledgeSource, ...]
    entries: tuple[KnowledgeEntryV3, ...]

    def entry_by_stable_id(self, stable_id: str) -> KnowledgeEntryV3:
        for entry in self.entries:
            if entry.stable_id == stable_id:
                return entry
        raise ValueError(f"knowledge bundle has no entry with stable_id {stable_id!r}")

    def entry_for(
        self,
        number: int,
        *,
        classification: EntryClassification | None = None,
        context: ResultContextV3 | None = None,
    ) -> KnowledgeEntryV3:
        """Context-sensitive resolver — fail-closed on ambiguity.

        Raises ``ValueError`` for zero matches or multiple equally-ranked
        matches (never silently returns ``candidates[0]`` on ambiguity).
        """
        candidates = [e for e in self.entries if e.number == number]
        if classification is not None:
            candidates = [e for e in candidates if e.classification == classification]
        if context is not None:
            ctx_matches = [e for e in candidates if context in e.result_contexts]
            if ctx_matches:
                candidates = ctx_matches
        if not candidates:
            raise ValueError(
                f"knowledge bundle has no V3 entry for number={number}"
                f" classification={classification!r} context={context!r}"
            )
        # Fail-closed: if multiple equally-ranked entries remain after all
        # filters, refuse to pick one arbitrarily.
        if len(candidates) > 1:
            ids = [c.stable_id for c in candidates]
            raise ValueError(
                f"ambiguous V3 knowledge lookup for number={number}: "
                f"multiple candidates remain ({', '.join(ids)})"
            )
        return candidates[0]
