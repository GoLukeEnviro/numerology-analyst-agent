"""CLI integration tests via Typer's CliRunner.

These exercise the real ``profile`` command end-to-end (parse → validate →
calculate → serialize) without spawning a subprocess, and prove the
determinism contract of the CLI output (byte-identical for identical input).
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from numerology_cli.main import app

runner = CliRunner()


def _run(name: str, birth: str, as_of: str) -> str:
    args = ["profile", "--name", name, "--birth", birth, "--as-of-date", as_of]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    return result.output


class TestProfileCommand:
    def test_reference_date_emits_life_path_one(self) -> None:
        out = _run("Max Mustermann", "1985-07-25", as_of="2026-07-26")
        payload = json.loads(out)
        assert payload["results"]["life_path_a"]["value"] == 1
        assert payload["results"]["life_path_b"]["value"] == 1
        assert payload["consistency"]["a_equals_b"] is True
        assert payload["input"]["birth_date"] == "1985-07-25"
        assert payload["input"]["as_of_date"] == "2026-07-26"

    def test_invalid_date_exits_nonzero(self) -> None:
        result = runner.invoke(
            app, ["profile", "--name", "X", "--birth", "not-a-date", "--as-of-date", "2026-07-26"]
        )
        assert result.exit_code != 0

    def test_missing_as_of_date_exits_nonzero(self) -> None:
        """v0.1.3: --as-of-date is mandatory for reproducibility."""
        result = runner.invoke(app, ["profile", "--name", "X", "--birth", "1985-07-25"])
        assert result.exit_code != 0

    def test_keys_sorted_in_output(self) -> None:
        out = _run("Max Mustermann", "1985-07-25", as_of="2026-07-26")
        # v0.1.3: schema_version appears between name and deterministic_hash.
        assert out.index('"audit_trace"') < out.index('"input"')
        assert out.index('"input"') < out.index('"results"')
        assert '"schema_version"' in out

    def test_karmic_debt_and_compound_notation_exposed(self) -> None:
        # Korrektur 1: B's component sum (19) is karmic; notation is exposed.
        out = _run("Max Mustermann", "1985-07-25", as_of="2026-07-26")
        payload = json.loads(out)
        b = payload["results"]["life_path_b"]
        a = payload["results"]["life_path_a"]
        assert a["compound_notation"] == "37/10/1"
        assert a["karmic_debt"] is None
        assert b["compound_notation"] == "19/10/1"
        assert b["karmic_debt"] == {"number": 19, "origin": "component_sum"}

    def test_future_birth_date_rejected(self) -> None:
        # Korrektur 3: birth_date later than as_of_date must be rejected.
        result = runner.invoke(
            app,
            ["profile", "--name", "Test", "--birth", "2030-01-01", "--as-of-date", "2026-07-26"],
        )
        assert result.exit_code != 0
        assert "PERSON_BIRTH_DATE_IN_FUTURE" in result.output


@pytest.mark.property
class TestCliDeterminism:
    def test_two_runs_byte_identical(self) -> None:
        """Identical input must produce byte-identical stdout (Master Contract §2.4)."""
        first = _run("Müller-Lüdenscheidt", "1993-01-01", as_of="2026-07-26")
        second = _run("Müller-Lüdenscheidt", "1993-01-01", as_of="2026-07-26")
        assert first == second

    def test_hash_stable_across_runs(self) -> None:
        a = json.loads(_run("Anna", "2000-12-29", as_of="2026-07-26"))["deterministic_hash"]
        b = json.loads(_run("Anna", "2000-12-29", as_of="2026-07-26"))["deterministic_hash"]
        assert a == b
