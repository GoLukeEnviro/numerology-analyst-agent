"""Export JSON Schemas for the v0.1.3 contract models.

Generates versioned JSON Schema files from the Pydantic models so that
consumers can validate inputs and outputs without importing Python.

Usage:
    uv run python scripts/export_schemas.py          # write schemas
    uv run python scripts/export_schemas.py --check  # verify schemas are up-to-date

Schemas are written to:
    src/numerology_api/schemas/
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

from pydantic import TypeAdapter

from numerology_domain.models import (
    CalculationResult,
    MethodPolicy,
    PersonInput,
    ProfileCalculationResult,
)
from numerology_interpretation.models import InterpretationResult
from numerology_knowledge.models import KnowledgeBundle, KnowledgeBundleV2

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "src" / "numerology_api" / "schemas"

SCHEMA_SPECS: list[tuple[str, type, str]] = [
    ("person-input-v1.schema.json", PersonInput, "PersonInput"),
    ("method-policy-v1.schema.json", MethodPolicy, "MethodPolicy"),
    ("calculation-result-v1.schema.json", CalculationResult, "CalculationResult"),
    (
        "profile-calculation-result-v3.schema.json",
        ProfileCalculationResult,
        "ProfileCalculationResult",
    ),
    ("knowledge-bundle-v1.schema.json", KnowledgeBundle, "KnowledgeBundle"),
    ("knowledge-bundle-v2.schema.json", KnowledgeBundleV2, "KnowledgeBundleV2"),
    ("interpretation-result-v1.schema.json", InterpretationResult, "InterpretationResult"),
]


def _generate_schema(model: type) -> dict[str, object]:
    """Generate a JSON Schema (draft 2020-12) from a Pydantic model."""
    adapter: TypeAdapter[object] = TypeAdapter(model)
    schema = adapter.json_schema()
    # Ensure it's a dict (TypeAdapter may return a ref in some cases).
    assert isinstance(schema, dict)
    return schema


def _write_schema(path: Path, schema: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _schemas_match(path: Path, schema: dict[str, object]) -> bool:
    if not path.exists():
        return False
    existing: object = json.loads(path.read_text(encoding="utf-8"))
    return existing == schema


def main() -> None:
    check_mode = "--check" in sys.argv

    all_ok = True
    for filename, model, _name in SCHEMA_SPECS:
        schema = _generate_schema(model)
        path = SCHEMAS_DIR / filename

        if check_mode:
            if not _schemas_match(path, schema):
                print(f"MISMATCH: {filename} is out of date. Run without --check to regenerate.")
                all_ok = False
        else:
            _write_schema(path, schema)
            print(f"Wrote {path}")

    if check_mode:
        if all_ok:
            print("All schemas up-to-date.")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
