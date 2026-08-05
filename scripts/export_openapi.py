"""Export the FastAPI OpenAPI document and fail CI when it drifts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from numerology_api.app import ApiSettings, create_app

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "openapi" / "numra-api.json"
V1_CONTRACT = REPO_ROOT / "openapi" / "contracts" / "v1-contract.json"


def rendered_schema() -> str:
    app = create_app(ApiSettings(environment="schema", allowed_origins=()))
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = rendered_schema()
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected:
            print("OpenAPI drift detected. Run: uv run python scripts/export_openapi.py")
            return 1
        print(f"OpenAPI up-to-date: {TARGET}")
        return 0
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(expected, encoding="utf-8")
    print(f"Wrote {TARGET}")
    _write_v1_contract(expected)
    return 0


def _write_v1_contract(full_schema: str) -> None:
    """Extract V1-only paths + recursive schema closure into v1-contract.json."""
    import copy

    doc = json.loads(full_schema)
    v1_paths: dict[str, object] = {}
    for path, methods in doc.get("paths", {}).items():
        if path.startswith("/api/v1/"):
            v1_paths[path] = methods
    if not v1_paths:
        return
    v1_refs: set[str] = set()
    _collect_refs(v1_paths, v1_refs)
    schemas = doc.get("components", {}).get("schemas", {})
    closure: dict[str, object] = {}
    for ref in sorted(v1_refs):
        name = ref.split("/")[-1]
        if name in schemas:
            closure[name] = schemas[name]
    contract: dict[str, object] = {
        "openapi": doc["openapi"],
        "info": {"title": "Numra API V1 Contract Snapshot", "version": "1.0"},
        "paths": v1_paths,
    }
    if closure:
        contract.setdefault("components", {})["schemas"] = closure  # type: ignore[index]
    V1_CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    V1_CONTRACT.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {V1_CONTRACT}")


def _collect_refs(obj: object, refs: set[str]) -> None:
    """Recursively collect all $ref values from a JSON-like structure."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                refs.add(value)
            else:
                _collect_refs(value, refs)
    elif isinstance(obj, list):
        for item in obj:
            _collect_refs(item, refs)


if __name__ == "__main__":
    raise SystemExit(main())
