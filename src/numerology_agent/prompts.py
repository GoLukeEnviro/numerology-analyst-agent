"""Load versioned prompt templates from the ``prompt_templates/`` package data.

Templates live in ``src/numerology_agent/prompt_templates/`` and are bundled
as package data in the wheel.  They contain ONLY linguistic instructions —
never secrets, never calculation logic.  Loading is deterministic and cached
per (category, name) pair.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files as _pkg_files


@lru_cache(maxsize=32)
def load_prompt(category: str, name: str) -> str:
    """Load a prompt file from ``numerology_agent/prompt_templates/<category>/<name>.md``.

    ``category`` is one of ``system``, ``tasks``, ``eval``. The lookup is
    cached because prompts are immutable per process; tests that need to reset
    the cache should call :func:`reset_prompt_cache`.
    """
    pkg = _pkg_files("numerology_agent.prompt_templates")
    candidate = pkg / category / f"{name}.md"
    try:
        return candidate.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError) as exc:
        raise FileNotFoundError(f"prompt not found: prompt_templates/{category}/{name}.md") from exc


def reset_prompt_cache() -> None:
    """Clear the LRU cache (test hook)."""
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
