"""Numerology API adapter layer.

In 0.1.0 this is a thin serialization adapter only — no FastAPI, no HTTP.
The HTTP routes (Master Contract §4.1, Phase 9) are added in a later
release on top of the same domain contracts.
"""

from __future__ import annotations

from numerology_api.contracts import dump_result_as_json, result_to_payload

__all__ = ["dump_result_as_json", "result_to_payload"]
