"""V2 analysis routes — stub (Welle 1).

Full implementation follows in Welle 3 when AgentServiceV3,
DeepSeekProviderV3 and the idempotency store are available.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["analyses-v2"])
