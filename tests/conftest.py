"""Shared pytest fixtures and path setup for the test suite.

The ``src`` layout is added to ``sys.path`` so tests can import the domain
and engine packages both under ``uv run pytest`` (which installs the
package) and under a bare interpreter.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import pytest

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from numerology_domain.models import MethodPolicy, PersonInput  # noqa: E402


@pytest.fixture
def default_policy() -> MethodPolicy:
    """Canonical pythagorean-v1 policy (y_mode=phonetic, de-direct-v1, both A/B)."""
    return MethodPolicy()


@pytest.fixture
def standard_person() -> PersonInput:
    """The canonical reference person used across golden + unit tests.

    Korrektur 2: as_of_date is an explicit, fixed value (never date.today())
    so tests stay fully deterministic. 2026-07-26 is comfortably after the
    canonical birth date 1985-07-25.
    """
    return PersonInput(
        core_name="Max Mustermann",
        birth_date=date(1985, 7, 25),
        as_of_date=date(2026, 7, 26),
    )
