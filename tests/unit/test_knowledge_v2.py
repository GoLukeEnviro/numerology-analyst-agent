"""Contracts for the V2 knowledge bundle and context-sensitive resolver."""

from __future__ import annotations

import pytest

from numerology_knowledge.loader import load_knowledge_bundle
from numerology_knowledge.models import KnowledgeBundleV2


@pytest.mark.unit
def test_v2_bundle_loads_with_correct_metadata() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    assert isinstance(bundle, KnowledgeBundleV2)
    assert bundle.bundle_id == "numra-knowledge-de-v2"
    assert bundle.version == "v2"
    assert bundle.locale == "de"


@pytest.mark.unit
def test_v2_bundle_covers_all_required_classifications() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    classifications = {e.classification for e in bundle.entries}
    assert classifications == {"single", "master", "compound", "karmic_debt"}


@pytest.mark.unit
def test_v2_bundle_has_required_coverage() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    singles = {e.number for e in bundle.entries if e.classification == "single"}
    masters = {e.number for e in bundle.entries if e.classification == "master"}
    assert singles == {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert masters == {11, 22, 33}


@pytest.mark.unit
def test_v2_compounds_have_compound_notation() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    compounds = [e for e in bundle.entries if e.classification == "compound"]
    assert len(compounds) >= 20
    for entry in compounds:
        assert entry.compound is not None
        assert entry.compound.raw_value != entry.compound.reduced_value
        assert "/" in entry.compound.compound_notation


@pytest.mark.unit
def test_v2_karmic_debt_entries() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    karmic = [e for e in bundle.entries if e.classification == "karmic_debt"]
    notations = {e.compound.compound_notation for e in karmic if e.compound is not None}
    assert {"13/4", "14/5", "16/7", "19/1"} <= notations


@pytest.mark.unit
def test_context_sensitive_resolver_single() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    entry = bundle.entry_for(4, classification="single")
    assert entry.classification == "single"
    assert entry.number == 4


@pytest.mark.unit
def test_context_sensitive_resolver_compound_vs_karmic() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    compound = bundle.entry_for(4, classification="compound")
    assert compound.classification == "compound"
    karmic = bundle.entry_for(4, classification="karmic_debt")
    assert karmic.classification == "karmic_debt"
    assert karmic.compound is not None
    assert karmic.compound.compound_notation == "13/4"


@pytest.mark.unit
def test_context_sensitive_resolver_master() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    entry = bundle.entry_for(22, classification="master")
    assert entry.classification == "master"
    assert entry.number == 22


@pytest.mark.unit
def test_context_sensitive_resolver_with_context_filter() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    entry = bundle.entry_for(1, classification="single", context="life_path")
    assert "life_path" in entry.result_contexts


@pytest.mark.unit
def test_stable_ids_are_unique() -> None:
    bundle = load_knowledge_bundle("de", "v2")
    stable_ids = [e.stable_id for e in bundle.entries]
    assert len(stable_ids) == len(set(stable_ids))


@pytest.mark.unit
def test_v1_bundle_still_loadable() -> None:
    bundle = load_knowledge_bundle("de", "v1")
    assert bundle.bundle_id == "numra-knowledge-de-v1"
    assert bundle.version == "v1"
