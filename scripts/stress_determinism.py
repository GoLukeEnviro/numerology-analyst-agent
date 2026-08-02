"""Belastungsnachweis für Issue #32 (3.6) — NICHT Teil der Test-Suite.

Führt durch:
* 100 isolierte Wiederholungen des Property-Tests (test_v2_determinism.py)
* 20 vollständige Suite-Läufe (ohne slow-Marker)
* Hash-Seed-Matrix (0, 1, 42, 123, 999, random)

Dokumentiert alle Ergebnisse als JSON für das Audit.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import TypedDict

_ROOT = Path(__file__).resolve().parent.parent
_PYTHON = str(_ROOT / ".venv" / "Scripts" / "python.exe")
_PROPERTY_TEST = "tests/property/test_v2_determinism.py"
_SUITE = "tests/"

_HASH_SEEDS = ["0", "1", "42", "123", "999", "random"]


class _FailureDetail(TypedDict):
    run: int
    output: str


class _RunSummary(TypedDict):
    runs: int
    passes: int
    failures: int
    failure_details: list[_FailureDetail]


class _SeedResult(TypedDict):
    returncode: int
    passed: bool
    output_tail: str


def _run_pytest(args: list[str], *, env: dict[str, str] | None = None) -> tuple[int, str]:
    """Führt pytest aus und liefert (returncode, output)."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [_PYTHON, "-m", "pytest", *args],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(_ROOT),
        timeout=600,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    results: dict[str, object] = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }

    # --- 1. 100 isolierte Wiederholungen des Property-Tests -----------------
    isolated: _RunSummary = {
        "runs": 0,
        "passes": 0,
        "failures": 0,
        "failure_details": [],
    }
    for i in range(1, 101):
        rc, out = _run_pytest([_PROPERTY_TEST, "-x", "-q"])
        isolated["runs"] += 1
        if rc == 0:
            isolated["passes"] += 1
        else:
            isolated["failures"] += 1
            isolated["failure_details"].append({"run": i, "output": out[-2000:]})
            print(f"FAIL at isolated run {i}")
    results["isolated_runs"] = isolated
    print(f"ISOLATED_RUNS: {isolated['passes']} pass / {isolated['failures']} fail")

    # --- 2. 20 vollständige Suite-Läufe -------------------------------------
    suite: _RunSummary = {
        "runs": 0,
        "passes": 0,
        "failures": 0,
        "failure_details": [],
    }
    for i in range(1, 21):
        rc, out = _run_pytest([_SUITE, "-q", "-m", "not slow"])
        suite["runs"] += 1
        if rc == 0:
            suite["passes"] += 1
        else:
            suite["failures"] += 1
            suite["failure_details"].append({"run": i, "output": out[-2000:]})
            print(f"FAIL at suite run {i}")
    results["full_suite_runs"] = suite
    print(f"FULL_SUITE_RUNS: {suite['passes']} pass / {suite['failures']} fail")

    # --- 3. Hash-Seed-Matrix ------------------------------------------------
    seed_matrix: dict[str, _SeedResult] = {}
    for seed in _HASH_SEEDS:
        rc, out = _run_pytest(
            [_PROPERTY_TEST, "-q"],
            env={"PYTHONHASHSEED": seed},
        )
        seed_matrix[seed] = {
            "returncode": rc,
            "passed": rc == 0,
            "output_tail": out[-500:],
        }
        print(f"HASH_SEED {seed}: {'PASS' if rc == 0 else 'FAIL'}")
    results["hash_seed_matrix"] = seed_matrix

    # --- Ausgabe -------------------------------------------------------------
    out_path = _ROOT / "docs" / "audit" / "determinism-stress-results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults written to {out_path}")

    # Exit-Code: 0 nur wenn alles bestanden
    ok = (
        isolated["failures"] == 0
        and suite["failures"] == 0
        and all(v["passed"] for v in seed_matrix.values())
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
