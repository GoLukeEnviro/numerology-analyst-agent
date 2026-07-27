"""Load versioned prompt templates from the ``prompts/`` directory.

The prompts live in ``<repo-root>/prompts/`` (a sibling of ``src/``). They
contain ONLY linguistic instructions — never secrets, never calculation logic.
Loading is deterministic and cached per (kind, name, locale) tuple.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path


def _prompts_root() -> Path:
    """Resolve the ``prompts/`` directory relative to this package.

    Layout::

        src/numerology_agent/prompts.py   (this file)
        prompts/                          (target, two levels up)
    """
    here = Path(__file__).resolve()
    # src/numerology_agent/prompts.py -> src/ -> repo root
    return here.parent.parent.parent / "prompts"


@lru_cache(maxsize=32)
def load_prompt(category: str, name: str) -> str:
    """Load a prompt file ``prompts/<category>/<name>.md`` as UTF-8 text.

    ``category`` is one of ``system``, ``tasks``, ``eval``. The lookup is
    cached because prompts are immutable per process; tests that swap the
    directory should call :func:`reset_prompt_cache`.
    """
    root = _prompts_root()
    candidate = root / category / f"{name}.md"
    if not candidate.is_file():
        raise FileNotFoundError(f"prompt not found: {candidate}")
    return candidate.read_text(encoding="utf-8")


def reset_prompt_cache() -> None:
    """Clear the LRU cache (test hook for swapping prompt directories)."""
    load_prompt.cache_clear()


def system_prompt(locale: str = "de") -> str:
    """Return the system prompt for report generation (default: de-v2)."""
    return load_prompt("system", f"{locale}-report-system")


def report_task_prompt(locale: str = "de") -> str:
    """Return the task prompt for the report (default: de-v2)."""
    return load_prompt("tasks", f"{locale}-report-task")


def follow_up_task_prompt(locale: str = "de") -> str:
    """Return the task prompt for follow-up questions (default: de-v2)."""
    return load_prompt("tasks", f"{locale}-follow-up-task")


def eval_criteria(locale: str = "de") -> str:
    """Return the eval criteria (default: de-v2)."""
    return load_prompt("eval", f"{locale}-report-eval")


__all__ = [
    "eval_criteria",
    "follow_up_task_prompt",
    "load_prompt",
    "report_task_prompt",
    "reset_prompt_cache",
    "system_prompt",
]


# Defensive: ensure resource access via importlib.resources also works for
# callers that prefer the resources API. ``resources.files`` requires the
# target to be importable as a package; since ``prompts/`` is data-only we
# expose a stable accessor for parity with the file-based loader above.
def _resource_anchor() -> Traversable:
    """Anchor for ``importlib.resources``-style access (parity helper)."""
    return resources.files(__name__)
