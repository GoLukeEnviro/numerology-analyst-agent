"""Strict models for versioned, source-linked numerology knowledge."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _KnowledgeModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class KnowledgeSource(_KnowledgeModel):
    id: str
    title: str
    source_type: str
    locator: str


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
