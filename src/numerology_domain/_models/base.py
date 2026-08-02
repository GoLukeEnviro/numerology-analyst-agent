"""Shared base configuration for every domain model.

Kept separate from the fachliche clusters so that ``input``, ``calculation``,
``cycles`` and ``profile`` can all import the same frozen base without
creating an import cycle.  This module is private (``_models``) — the public
surface is the ``numerology_domain.models`` compatibility facade.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _FrozenModel(BaseModel):
    """Common config for every domain model: immutable + no extra fields."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
