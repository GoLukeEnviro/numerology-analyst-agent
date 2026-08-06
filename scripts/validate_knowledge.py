#!/usr/bin/env python3
"""Validate all knowledge bundles against their schema models.

Exit codes:
- 0: all bundles valid
- 1: validation error (printed to stderr)

Usage:
    uv run python scripts/validate_knowledge.py
    uv run python scripts/validate_knowledge.py --check   # CI mode (same as default)

Hard validation rules (fail-closed):
- unknown version
- wrong bundle id
- duplicate stable_id
- missing context (result_contexts empty)
- invalid master number (classification=master but number not in 11/22/33)
- invalid karmic number (classification=karmic_debt but number not in 13/14/16/19)
- empty interpretation (constructive/shadow/development empty)
- multiple matches where uniqueness is required (V3 entry_for ambiguity)
- missing required values (schema-level)
- unsupported locale
"""

from __future__ import annotations

from pathlib import Path
import sys

from pydantic import BaseModel, ValidationError

from numerology_knowledge.models import KnowledgeBundle, KnowledgeBundleV2
from numerology_knowledge.models_v3 import KnowledgeBundleV3

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _REPO_ROOT / "src" / "numerology_knowledge" / "data"

_MASTER_NUMBERS: frozenset[int] = frozenset({11, 22, 33})
_KARMIC_DEBTS: frozenset[int] = frozenset({13, 14, 16, 19})
_SUPPORTED_LOCALES: frozenset[str] = frozenset({"de"})

_BUNDLES: list[tuple[str, type[BaseModel]]] = [
    ("de-v1.json", KnowledgeBundle),
    ("de-v2.json", KnowledgeBundleV2),
    ("de-v3.json", KnowledgeBundleV3),
]


def _validate_semantics(bundle: BaseModel, filename: str) -> list[str]:
    """Run cross-entry semantic checks. Returns a list of error messages."""
    errors: list[str] = []
    locale = getattr(bundle, "locale", None)
    if locale not in _SUPPORTED_LOCALES:
        errors.append(f"{filename}: unsupported locale {locale!r}")

    entries = list(getattr(bundle, "entries", ()))
    seen_ids: set[str] = set()
    for entry in entries:
        stable_id = getattr(entry, "stable_id", None)
        if stable_id is not None:
            if stable_id in seen_ids:
                errors.append(f"{filename}: duplicate stable_id {stable_id!r}")
            seen_ids.add(stable_id)

        classification = getattr(entry, "classification", None)
        number = getattr(entry, "number", None)
        compound = getattr(entry, "compound", None)
        if classification == "master" and number not in _MASTER_NUMBERS:
            errors.append(
                f"{filename}: entry {stable_id!r} classified as master but number={number} "
                f"is not in {sorted(_MASTER_NUMBERS)}"
            )
        if classification == "karmic_debt":
            # Karmic entries store the reduced value in ``number`` and the
            # karmic raw value in ``compound.raw_value`` (e.g. 13/4).  The
            # karmic number must be present in one of the two fields.
            raw_value = getattr(compound, "raw_value", None) if compound is not None else None
            karmic_hit = number in _KARMIC_DEBTS or raw_value in _KARMIC_DEBTS
            if not karmic_hit:
                errors.append(
                    f"{filename}: entry {stable_id!r} classified as karmic_debt but neither "
                    f"number={number} nor compound.raw_value={raw_value} is in "
                    f"{sorted(_KARMIC_DEBTS)}"
                )

        for field in ("constructive_expression", "shadow_expression", "development_theme"):
            value = getattr(entry, field, None)
            if value is not None and not str(value).strip():
                errors.append(f"{filename}: entry {stable_id!r} has empty {field}")

        contexts = getattr(entry, "result_contexts", None)
        if contexts is not None and len(contexts) == 0:
            errors.append(f"{filename}: entry {stable_id!r} has empty result_contexts")

    # V3: fail-closed on ambiguous lookups for every (number, classification, context)
    # combination that the resolver could be asked for. We only check the actual
    # entries present: for each entry, resolving by its own number+classification
    # must be unambiguous.
    if isinstance(bundle, KnowledgeBundleV3):
        for entry in bundle.entries:
            candidates = [
                e
                for e in bundle.entries
                if e.number == entry.number and e.classification == entry.classification
            ]
            if len(candidates) > 1:
                ids = [c.stable_id for c in candidates]
                errors.append(
                    f"{filename}: ambiguous V3 lookup for number={entry.number} "
                    f"classification={entry.classification!r}: {ids}"
                )
    return errors


def validate_bundle(filename: str, model: type[BaseModel]) -> bool:
    """Validate a single bundle file. Returns True on success."""
    path = _DATA_DIR / filename
    if not path.is_file():
        print(f"ERROR: knowledge bundle not found: {path}", file=sys.stderr)
        return False
    try:
        raw = path.read_text(encoding="utf-8")
        bundle = model.model_validate_json(raw)
    except ValidationError as exc:
        print(f"ERROR: {filename} failed validation:", file=sys.stderr)
        print(exc, file=sys.stderr)
        return False
    semantic_errors = _validate_semantics(bundle, filename)
    if semantic_errors:
        print(f"ERROR: {filename} failed semantic validation:", file=sys.stderr)
        for error in semantic_errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    print(f"OK: {filename} is valid against {model.__name__}")
    return True


def main() -> int:
    """Validate all knowledge bundles. Returns process exit code."""
    all_valid = True
    for filename, model in _BUNDLES:
        if not validate_bundle(filename, model):
            all_valid = False
    if all_valid:
        print(f"\nAll {len(_BUNDLES)} knowledge bundles valid.")
        return 0
    print("\nSome knowledge bundles failed validation.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
