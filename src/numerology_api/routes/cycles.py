"""Cycle routes for the Numra API.

The current v1 contract exposes cycles only as part of the complete profile
(``/api/v1/profiles/calculate``). This router is intentionally empty and
reserved for future dedicated cycle endpoints; registering it keeps the
route namespace stable without changing the public API.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["cycles"])
