"""Typer CLI for the Numerology Analyst Agent.

Single command ``profile``:

    numerology profile --name "Max Mustermann" --birth 1985-07-25

Output is canonical, key-sorted JSON on stdout (determinism contract:
identical input ⇒ byte-identical output). Errors go to stderr with a
non-zero exit code.

The CLI version is read dynamically from the installed package metadata to
avoid hardcoded version drift (Luke's P1 review 2026-07-26).
"""

from __future__ import annotations

from datetime import date
from importlib.metadata import PackageNotFoundError, version

from pydantic import ValidationError
import typer

from numerology_api.contracts import dump_profile_as_json
from numerology_domain.exceptions import NumerologyError
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile


def _package_version() -> str:
    """Read the installed package version dynamically.

    Falls back to ``"0.0.0+dev"`` if the package is not installed (e.g., running
    directly from a source checkout without installation). This eliminates
    hardcoded version strings in the CLI (Luke's P1 review 2026-07-26).
    """
    try:
        return version("numerology-analyst-agent")
    except PackageNotFoundError:
        return "0.0.0+dev"


PACKAGE_VERSION = _package_version()

app = typer.Typer(
    add_completion=False,
    help=f"Numerology Analyst Agent - deterministic pythagorean core ({PACKAGE_VERSION}).",
)


@app.callback()
def _main() -> None:
    """Numerology Analyst Agent - deterministic pythagorean core.

    A no-op root callback so that ``profile`` is exposed as a real subcommand
    (``numerology profile ...``) rather than collapsed onto the root entry.
    The version is read dynamically from the installed package metadata.
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
    as_of: str = typer.Option(
        ...,
        "--as-of-date",
        help="Required evaluation date as YYYY-MM-DD. birth must be <= as_of.",
    ),
) -> None:
    """Compute the complete deterministic profile and emit canonical JSON."""
    # as_of_date is mandatory (v0.1.3 contract integrity): the CLI must be
    # fully reproducible; date.today() would break determinism.
    try:
        as_of_date = _parse_birth(as_of)
        person = PersonInput(
            core_name=name,
            birth_date=_parse_birth(birth),
            active_name=active_name,
            as_of_date=as_of_date,
        )
        policy = MethodPolicy()  # canonical pythagorean-v1 defaults
        result = calculate_profile(person, policy)
    except NumerologyError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except ValidationError as exc:
        # Korrektur 3: surface the first validation failure deterministically.
        # pydantic raises ValidationError (not ValueError) at the model boundary;
        # we extract the human-readable message (e.g. PERSON_BIRTH_DATE_IN_FUTURE).
        first = exc.errors()[0]
        msg = " ".join(str(part) for part in (first.get("msg"), first.get("type"))).strip()
        typer.echo(f"error: {msg}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(dump_profile_as_json(result))


@app.command(name="version")
def version_cmd() -> None:
    """Print the installed package version and exit."""
    typer.echo(PACKAGE_VERSION)


if __name__ == "__main__":
    app()
