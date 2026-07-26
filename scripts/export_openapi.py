"""Export the FastAPI OpenAPI document and fail CI when it drifts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from numerology_api.app import ApiSettings, create_app

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "openapi" / "numra-v1.json"


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
