"""Version and completeness contracts for the German V1 knowledge bundle."""

from __future__ import annotations

import pytest

from numerology_knowledge.loader import load_knowledge_bundle


@pytest.mark.unit
def test_german_v1_bundle_covers_every_supported_reduction() -> None:
    bundle = load_knowledge_bundle("de", "v1")

    assert bundle.bundle_id == "numra-knowledge-de-v1"
    assert bundle.scientific_position
    assert {entry.number for entry in bundle.entries} == {
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        11,
        22,
        33,
    }
    assert all(entry.counter_hypotheses for entry in bundle.entries)
    assert all(entry.source_refs for entry in bundle.entries)
    assert {reference for entry in bundle.entries for reference in entry.source_refs} <= {
        source.id for source in bundle.sources
    }


@pytest.mark.unit
def test_unknown_bundle_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported knowledge bundle"):
        load_knowledge_bundle("en", "v1")
