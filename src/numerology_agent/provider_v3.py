"""V3 LLM provider protocol — interface layer (Welle 1).

The concrete ``DeepSeekProviderV3`` implementation follows in Welle 3.
This module exists so that ``create_app`` and the dependency wiring
can be typed and tested before the provider exists.
"""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ProviderResultV3(BaseModel):
    """Result returned by any V3 LLM provider implementation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    content: str
    model: str
    finish_reason: str
    provider_fingerprint: str | None = None
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)


class LlmProviderV3(Protocol):
    """V3 LLM provider protocol — implemented by ``DeepSeekProviderV3`` in Welle 3."""

    async def complete(
        self,
        payload: dict[str, Any],
        schema: dict[str, Any],
    ) -> ProviderResultV3: ...
