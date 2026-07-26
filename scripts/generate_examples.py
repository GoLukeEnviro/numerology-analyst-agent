"""Beispieldateien aus echten Service-Ausgaben erzeugen (Korrektur 5).

Usage::

    uv run python scripts/generate_examples.py           # neu erzeugen
    uv run python scripts/generate_examples.py --check    # CI-Modus: Drift => Exit 1

Beispieldateien werden NIE von Hand gepflegt. Sie sind 1:1 vom Service
abgeleitet. Die CI ruft ``--check`` auf; jeder Drift schlägt rot an.

Designentscheidung (documented): Das Skript schreibt den *reinen* Service-
Output ohne hand-editierten ``_comment``-Header. Ein Hand-Kommentar wäre
genau die Drift-Quelle, die dieses Skript verhindern soll. Wer den Kontext
einer Beispieldatei braucht, konsultiert dieses Skript (den Generator).
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from numerology_api.contracts import dump_result_as_json
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.service import calculate_life_path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def _basic_life_path_payload() -> str:
    """Erzeuge ``examples/basic-life-path.json`` aus einem echten Service-Aufruf.

    Die Eingabe ist absichtlich die kanonische Referenz (Max Mustermann,
    1985-07-25, as_of_date 2026-07-26) - dieselbe, die auch im Hash-Golden-
    Case (tests/golden/test_hash_golden.py) gepinnt ist.
    """
    person = PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
    result = calculate_life_path(person, MethodPolicy())
    return dump_result_as_json(result)


def regenerate() -> None:
    """Alle Beispieldateien neu erzeugen."""
    EXAMPLES_DIR.mkdir(exist_ok=True)
    (EXAMPLES_DIR / "basic-life-path.json").write_text(_basic_life_path_payload(), encoding="utf-8")
    print(f"Regenerated examples in {EXAMPLES_DIR}")


def check() -> int:
    """0 wenn Beispiele aktuell sind, 1 bei Drift."""
    expected = _basic_life_path_payload()
    target = EXAMPLES_DIR / "basic-life-path.json"
    if not target.exists():
        print(f"ERROR: {target} fehlt. Aufruf: uv run python scripts/generate_examples.py")
        return 1
    actual = target.read_text(encoding="utf-8")
    if actual != expected:
        print(f"DRIFT in {target} erkannt. Aufruf: uv run python scripts/generate_examples.py")
        return 1
    print(f"OK: {target} stimmt mit der Service-Ausgabe ueberein")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="CI-Drift-Pruefmodus")
    args = parser.parse_args()
    if args.check:
        return check()
    regenerate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
