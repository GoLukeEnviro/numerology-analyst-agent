"""V3 prompt loader — loads ``de-report-system-v3.md`` and ``de-report-task-v3.md``.

Parallel to ``prompts.py`` (V1/V2 stack).  Uses the same ``load_prompt`` helper
internally but loads the V3 prompt files explicitly.
"""

from __future__ import annotations

from numerology_agent.prompts import load_prompt


def system_prompt_v3(locale: str = "de") -> str:
    return load_prompt("system", f"{locale}-report-system-v3")


def report_task_prompt_v3(locale: str = "de") -> str:
    return load_prompt("tasks", f"{locale}-report-task-v3")


def follow_up_task_prompt_v3(locale: str = "de") -> str:
    return load_prompt("tasks", f"{locale}-follow-up-task-v3")
