"""Typer CLI for the Numerology Analyst Agent (Walking Skeleton 0.1.0).

Single command ``profile``:

    numerology profile --name "Max Mustermann" --birth 1985-07-25

Output is canonical, key-sorted JSON on stdout (determinism contract:
identical input ⇒ byte-identical output). Errors go to stderr with a
non-zero exit code.
"""

from __future__ import annotations

from datetime import date

import typer

from numerology_api.contracts import dump_result_as_json
from numerology_domain.exceptions import NumerologyError
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.service import calculate_life_path

app = typer.Typer(
    add_completion=False,
    help="Numerology Analyst Agent - deterministic pythagorean core (0.1.0).",
)


@app.callback()
def _main() -> None:
    """Numerology Analyst Agent - deterministic pythagorean core (0.1.0).

    A no-op root callback so that ``profile`` is exposed as a real subcommand
    (``numerology profile ...``) rather than collapsed onto the root entry.
    """


def _parse_birth(raw: str) -> date:
    """Parse an ISO ``YYYY-MM-DD`` string into a :class:`datetime.date`.

    Typer/Python's ``date.fromisoformat`` rejects ``1985-7-5`` (non-zero-
    padded), which is the determinism-correct behavior — the CLI demands
    canonical ISO dates.
    """
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise typer.BadParameter(f"--birth must be an ISO date YYYY-MM-DD (got {raw!r})") from exc


@app.command()
def profile(
    name: str = typer.Option(..., "--name", "-n", help="Full birth name (core_name)."),
    birth: str = typer.Option(..., "--birth", "-b", help="Birth date as YYYY-MM-DD."),
    active_name: str | None = typer.Option(
        None, "--active-name", help="Currently used name (optional)."
    ),
) -> None:
    """Compute the Life Path (A + B) profile and emit canonical JSON."""
    try:
        person = PersonInput(
            core_name=name,
            birth_date=_parse_birth(birth),
            active_name=active_name,
        )
        policy = MethodPolicy()  # canonical pythagorean-v1 defaults
        result = calculate_life_path(person, policy)
    except NumerologyError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(dump_result_as_json(result))


if __name__ == "__main__":
    app()
