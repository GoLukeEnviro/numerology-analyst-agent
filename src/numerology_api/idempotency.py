"""API idempotency contracts — interface layer (Welle 1).

The concrete ``RedisIdempotencyStoreV3`` follows in Welle 3.
This module provides the protocol, result types and status enums
so that ``create_app`` can accept an idempotency store without
a concrete implementation.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Protocol


class IdempotencyStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AcquireResultV3:
    """Result of an ``IdempotencyStoreV3.acquire()`` call."""

    __slots__ = ("status", "owner_token", "existing_response", "conflict_detail")

    def __init__(
        self,
        status: IdempotencyStatus,
        owner_token: str | None = None,
        existing_response: bytes | None = None,
        conflict_detail: str | None = None,
    ) -> None:
        self.status = status
        self.owner_token = owner_token
        self.existing_response = existing_response
        self.conflict_detail = conflict_detail


class IdempotencyStoreV3(Protocol):
    """Protocol for the V3 idempotency store — implemented in Welle 3.

    TTL: 1–6 hours (no extension on reads).
    Storage: encrypted (AES-GCM-256), never plaintext in Redis.
    """

    async def acquire(
        self,
        *,
        key: str,
        request_context_hash: str,
        operation: Literal["report", "follow_up"],
        ttl_seconds: int,
    ) -> AcquireResultV3: ...

    async def complete(
        self,
        *,
        key: str,
        owner_token: str,
        response_type: Literal["report", "follow_up"],
        encrypted_response: bytes,
    ) -> None: ...

    async def fail(
        self,
        *,
        key: str,
        owner_token: str,
        error_code: str,
        retryable: bool,
    ) -> None: ...
