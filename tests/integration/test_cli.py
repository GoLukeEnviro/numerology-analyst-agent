"""CLI integration tests via Typer's CliRunner.

These exercise the real ``profile`` command end-to-end (parse → validate →
calculate → serialize) without spawning a subprocess, and prove the
determinism contract of the CLI output (byte-identical for identical input).
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from apps.cli.main import app

runner = CliRunner()


def _run(name: str, birth: str) -> str:
    result = runner.invoke(app, ["profile", "--name", name, "--birth", birth])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    return result.output


class TestProfileCommand:
    def test_reference_date_emits_life_path_one(self) -> None:
        out = _run("Max Mustermann", "1985-07-25")
        payload = json.loads(out)
        assert payload["results"]["life_path_a"]["value"] == 1
        assert payload["results"]["life_path_b"]["value"] == 1
        assert payload["consistency"]["a_equals_b"] is True
        assert payload["input"]["birth_date"] == "1985-07-25"

    def test_invalid_date_exits_nonzero(self) -> None:
        result = runner.invoke(app, ["profile", "--name", "X", "--birth", "not-a-date"])
        assert result.exit_code != 0

    def test_keys_sorted_in_output(self) -> None:
        out = _run("Max Mustermann", "1985-07-25")
        assert out.index('"audit_trace"') < out.index('"input"')
        assert out.index('"input"') < out.index('"results"')


@pytest.mark.property
class TestCliDeterminism:
    def test_two_runs_byte_identical(self) -> None:
        """Identical input must produce byte-identical stdout (Master Contract §2.4)."""
        first = _run("Müller-Lüdenscheidt", "1993-01-01")
        second = _run("Müller-Lüdenscheidt", "1993-01-01")
        assert first == second

    def test_hash_stable_across_runs(self) -> None:
        a = json.loads(_run("Anna", "2000-12-29"))["deterministic_hash"]
        b = json.loads(_run("Anna", "2000-12-29"))["deterministic_hash"]
        assert a == b
