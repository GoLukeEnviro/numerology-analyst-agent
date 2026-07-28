"""Tests für numerology_agent.prompts — Prompt-Template-Laden.

Stellt sicher, dass alle öffentlichen Funktionen korrekt funktionieren
und Fehler explizit geworfen werden.
"""

from __future__ import annotations

import pytest

from numerology_agent.prompts import (
    _prompts_root,
    _resource_anchor,
    eval_criteria,
    follow_up_task_prompt,
    load_prompt,
    report_task_prompt,
    reset_prompt_cache,
    system_prompt,
)


@pytest.mark.unit
def test_prompts_root_exists() -> None:
    """_prompts_root() zeigt auf ein existierendes Verzeichnis."""
    root = _prompts_root()
    assert root.is_dir(), f"Prompts-Verzeichnis nicht gefunden: {root}"


@pytest.mark.unit
def test_prompts_root_contains_expected_subdirs() -> None:
    root = _prompts_root()
    assert (root / "system").is_dir()
    assert (root / "tasks").is_dir()
    assert (root / "eval").is_dir()


@pytest.mark.unit
def test_load_prompt_system_de() -> None:
    text = load_prompt("system", "de-report-system")
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.unit
def test_load_prompt_task_report() -> None:
    text = load_prompt("tasks", "de-report-task")
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.unit
def test_load_prompt_task_follow_up() -> None:
    text = load_prompt("tasks", "de-follow-up-task")
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.unit
def test_load_prompt_eval_criteria() -> None:
    text = load_prompt("eval", "de-report-eval")
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.unit
def test_load_prompt_missing_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError, match="prompt not found"):
        load_prompt("system", "nonexistent-prompt-xyz")


@pytest.mark.unit
def test_load_prompt_missing_category_raises() -> None:
    with pytest.raises(FileNotFoundError, match="prompt not found"):
        load_prompt("nonexistent-category", "de-report-system")


@pytest.mark.unit
def test_load_prompt_caching_returns_same_content() -> None:
    """Zweifacher Aufruf liefert gleichen String-Inhalt."""
    reset_prompt_cache()
    t1 = load_prompt("system", "de-report-system")
    t2 = load_prompt("system", "de-report-system")
    assert t1 == t2


@pytest.mark.unit
def test_load_prompt_cache_hit_after_first_call() -> None:
    """Nach dem ersten Aufruf enthält der Cache mindestens einen Eintrag."""
    reset_prompt_cache()
    load_prompt("system", "de-report-system")
    info = load_prompt.cache_info()
    assert info.currsize >= 1


@pytest.mark.unit
def test_reset_prompt_cache_clears_entries() -> None:
    load_prompt("system", "de-report-system")
    reset_prompt_cache()
    info = load_prompt.cache_info()
    assert info.currsize == 0


@pytest.mark.unit
def test_system_prompt_returns_non_empty_string() -> None:
    text = system_prompt()
    assert isinstance(text, str)
    assert len(text) > 10


@pytest.mark.unit
def test_system_prompt_default_locale_de() -> None:
    """system_prompt() und system_prompt('de') liefern identischen Inhalt."""
    assert system_prompt() == system_prompt("de")


@pytest.mark.unit
def test_report_task_prompt_returns_non_empty_string() -> None:
    text = report_task_prompt()
    assert isinstance(text, str)
    assert len(text) > 10


@pytest.mark.unit
def test_report_task_prompt_default_locale_de() -> None:
    assert report_task_prompt() == report_task_prompt("de")


@pytest.mark.unit
def test_follow_up_task_prompt_returns_non_empty_string() -> None:
    text = follow_up_task_prompt()
    assert isinstance(text, str)
    assert len(text) > 10


@pytest.mark.unit
def test_follow_up_task_prompt_default_locale_de() -> None:
    assert follow_up_task_prompt() == follow_up_task_prompt("de")


@pytest.mark.unit
def test_eval_criteria_returns_non_empty_string() -> None:
    text = eval_criteria()
    assert isinstance(text, str)
    assert len(text) > 10


@pytest.mark.unit
def test_eval_criteria_default_locale_de() -> None:
    assert eval_criteria() == eval_criteria("de")


@pytest.mark.unit
def test_resource_anchor_is_traversable() -> None:
    from importlib.resources.abc import Traversable

    anchor = _resource_anchor()
    assert isinstance(anchor, Traversable)
