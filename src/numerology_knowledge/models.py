"""Strict models for versioned, source-linked numerology knowledge.

V1 models (``KnowledgeEntry``, ``KnowledgeBundle``) remain as read structures
for migration/import. V2 models (``CompoundNotation``, ``KnowledgeEntryV2``,
``KnowledgeBundleV2``) are the canonical structures newly loaded and produced.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _KnowledgeModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class KnowledgeSource(_KnowledgeModel):
    id: str
    title: str
    source_type: str
    locator: str


# ---------------------------------------------------------------------------
# V1 models (read-only / migration / import)
# ---------------------------------------------------------------------------


class KnowledgeEntry(_KnowledgeModel):
    number: int
    title: str
    traditional_claims: tuple[str, ...]
    reflection_prompts: tuple[str, ...]
    practical_suggestions: tuple[str, ...]
    counter_hypotheses: tuple[str, ...]
    source_refs: tuple[str, ...]


class KnowledgeBundle(_KnowledgeModel):
    bundle_id: str
    locale: str
    version: str
    scientific_position: str
    sources: tuple[KnowledgeSource, ...]
    entries: tuple[KnowledgeEntry, ...]

    def entry_for(self, number: int) -> KnowledgeEntry:
        for entry in self.entries:
            if entry.number == number:
                return entry
        raise ValueError(f"knowledge bundle has no entry for number {number}")


# ---------------------------------------------------------------------------
# V2 models (canonical / newly produced)
# ---------------------------------------------------------------------------

#: Classification of a knowledge entry's numeric structure.
EntryClassification = Literal[
    "single",  # 0-9 (reduced single digit)
    "master",  # 11, 22, 33 (master number)
    "compound",  # 10/1, 12/3, 15/6, … (two-digit reduced to single)
    "karmic_debt",  # 13/4, 14/5, 16/7, 19/1
]

#: The context in which a number appears in a profile.
ResultContext = Literal[
    "life_path",
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
    "name_cycle",
]

#: Claim class for the six-statement-class taxonomy.
ClaimClass = Literal[
    "input_fact",
    "calculation_fact",
    "traditional_claim",
    "interpretive_hypothesis",
    "empirical_evidence",
    "practical_suggestion",
]


class CompoundNotation(_KnowledgeModel):
    """Compound structure replacing ``number: int`` for compound entries.

    For a compound like 13/4:
    - ``raw_value`` = 13 (the unreduced two-digit number)
    - ``reduced_value`` = 4 (the pythagorean reduction)
    - ``compound_notation`` = "13/4"

    Compounds reducing to a master number (e.g. 29/11, 38/11) carry the
    master number as ``reduced_value``.
    """

    raw_value: int = Field(ge=10, le=99)
    reduced_value: int = Field(ge=1, le=33)
    compound_notation: str = Field(min_length=3, max_length=5, pattern=r"^\d{2}/\d{1,2}$")


class AuthoringProvenance(_KnowledgeModel):
    """Provenance for the authoring of a knowledge entry."""

    authored_at: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    author: str = Field(min_length=1, max_length=80)
    review_status: Literal["draft", "reviewed", "approved"] = "draft"


class KnowledgeEntryV2(_KnowledgeModel):
    """Canonical V2 knowledge entry with compound support and rich metadata.

    For single/master/karmic entries ``compound`` is ``None`` and ``number``
    holds the integer. For compound entries ``compound`` carries the
    ``CompoundNotation`` and ``number`` holds the ``reduced_value``.
    """

    stable_id: str = Field(min_length=1, max_length=160)
    method_system: Literal["pythagorean-v1"] = "pythagorean-v1"
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
    result_contexts: tuple[ResultContext, ...] = Field(min_length=1)
    source_refs: tuple[str, ...] = Field(min_length=1)
    authoring_provenance: AuthoringProvenance


class KnowledgeBundleV2(_KnowledgeModel):
    """Canonical V2 knowledge bundle."""

    bundle_id: str
    locale: str
    version: Literal["v2"] = "v2"
    scientific_position: str
    sources: tuple[KnowledgeSource, ...]
    entries: tuple[KnowledgeEntryV2, ...]

    def entry_by_stable_id(self, stable_id: str) -> KnowledgeEntryV2:
        for entry in self.entries:
            if entry.stable_id == stable_id:
                return entry
        raise ValueError(f"knowledge bundle has no entry with stable_id {stable_id!r}")

    def entry_for(
        self,
        number: int,
        *,
        classification: EntryClassification | None = None,
        context: ResultContext | None = None,
    ) -> KnowledgeEntryV2:
        """Context-sensitive resolver.

        - ``number=4, classification=None`` → first entry with number=4.
        - ``number=4, classification="compound"`` → compound 13/4 (or 31/4 etc.).
        - ``number=22, classification="master"`` → master 22.
        - ``context="life_path"`` narrows to entries where ``result_contexts``
          includes the given context.
        """
        candidates = [e for e in self.entries if e.number == number]
        if classification is not None:
            candidates = [e for e in candidates if e.classification == classification]
        if context is not None:
            candidates = [e for e in candidates if context in e.result_contexts]
        if not candidates:
            raise ValueError(
                f"knowledge bundle has no V2 entry for number={number}"
                f" classification={classification!r} context={context!r}"
            )
        return candidates[0]
