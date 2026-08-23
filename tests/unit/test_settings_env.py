"""Regression tests for environment settings parsing.

Covers the CRLF/whitespace robustness fix (B-16): Docker Compose on Windows
injects ``\r`` into env values read from a CRLF ``.env`` file, so
``NUMRA_LLM_ENABLED`` arrives as ``"true\r"``.  The settings parser must
strip surrounding whitespace before boolean comparison.
"""

from __future__ import annotations

import os
from unittest.mock import patch

from numerology_api.dependencies import settings_from_environment


def test_llm_enabled_with_crlf_trailing_carriage_return() -> None:
    """``NUMRA_LLM_ENABLED=true\r`` must parse as enabled (CRLF .env)."""
    with patch.dict(
        os.environ,
        {"NUMRA_LLM_ENABLED": "true\r", "DEEPSEEK_API_KEY": "sk-test"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.llm_enabled is True


def test_llm_enabled_with_trailing_space() -> None:
    """``NUMRA_LLM_ENABLED=true `` must parse as enabled."""
    with patch.dict(
        os.environ,
        {"NUMRA_LLM_ENABLED": "true ", "DEEPSEEK_API_KEY": "sk-test"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.llm_enabled is True


def test_llm_enabled_with_leading_space() -> None:
    """``NUMRA_LLM_ENABLED= true`` must parse as enabled."""
    with patch.dict(
        os.environ,
        {"NUMRA_LLM_ENABLED": " true", "DEEPSEEK_API_KEY": "sk-test"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.llm_enabled is True


def test_llm_disabled_with_crlf() -> None:
    """``NUMRA_LLM_ENABLED=false\r`` must parse as disabled."""
    with patch.dict(
        os.environ,
        {"NUMRA_LLM_ENABLED": "false\r"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.llm_enabled is False


def test_llm_enabled_uppercase() -> None:
    """``NUMRA_LLM_ENABLED=TRUE`` must parse as enabled (case-insensitive)."""
    with patch.dict(
        os.environ,
        {"NUMRA_LLM_ENABLED": "TRUE", "DEEPSEEK_API_KEY": "sk-test"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.llm_enabled is True


def test_environment_strips_crlf() -> None:
    """``NUMRA_ENVIRONMENT=production\r`` must parse as ``production``."""
    with patch.dict(
        os.environ,
        {"NUMRA_ENVIRONMENT": "production\r"},
        clear=False,
    ):
        settings = settings_from_environment()
        assert settings.environment == "production"
