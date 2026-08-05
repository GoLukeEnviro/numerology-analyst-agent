"""V3 dependency wiring — settings and factory interfaces (Welle 1).

Concrete implementations follow in Welle 3.  This module keeps the
``create_app`` signature type-checked and testable before the V3
provider and idempotency store exist.
"""

from __future__ import annotations

from typing import Protocol


class V3AnalysisSettings(Protocol):
    """Settings required by the V3 analysis stack.

    Implemented by extending ``ApiSettings`` with V3-specific fields
    in Welle 3 (e.g. ``v3_analysis_enabled``,
    ``idempotency_encryption_key``).
    """

    @property
    def v3_analysis_enabled(self) -> bool: ...

    @property
    def idempotency_encryption_key(self) -> str | None: ...

    @property
    def idempotency_ttl_seconds(self) -> int: ...
