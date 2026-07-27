"""Provider protocol used by production and contract-test adapters."""

from __future__ import annotations

from typing import Any, Protocol

from numerology_agent.models import ProviderResult


class LlmProvider(Protocol):
    async def complete(
        self,
        payload: dict[str, Any],
        schema: dict[str, Any],
    ) -> ProviderResult: ...


class ProviderError(RuntimeError):
    """Sanitized provider failure safe to handle above the adapter."""
