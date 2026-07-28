#!/usr/bin/env python3
"""Validate all knowledge bundles against their schema models.

Exit codes:
- 0: all bundles valid
- 1: validation error (printed to stderr)

Usage:
    uv run python scripts/validate_knowledge.py
    uv run python scripts/validate_knowledge.py --check   # CI mode (same as default)
"""

from __future__ import annotations

from pathlib import Path
import sys

from pydantic import BaseModel, ValidationError

from numerology_knowledge.models import KnowledgeBundle, KnowledgeBundleV2

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _REPO_ROOT / "src" / "numerology_knowledge" / "data"

_BUNDLES: list[tuple[str, type[BaseModel]]] = [
    ("de-v1.json", KnowledgeBundle),
    ("de-v2.json", KnowledgeBundleV2),
]


def validate_bundle(filename: str, model: type[BaseModel]) -> bool:
    """Validate a single bundle file. Returns True on success."""
    path = _DATA_DIR / filename
    if not path.is_file():
        print(f"ERROR: knowledge bundle not found: {path}", file=sys.stderr)
        return False
    try:
        raw = path.read_text(encoding="utf-8")
        model.model_validate_json(raw)
    except ValidationError as exc:
        print(f"ERROR: {filename} failed validation:", file=sys.stderr)
        print(exc, file=sys.stderr)
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
