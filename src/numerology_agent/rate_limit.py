"""Privacy-preserving distributed rate limiting."""

from __future__ import annotations

from hashlib import sha256
import hmac
from typing import Protocol, cast


def pseudonymous_key(scope: str, source: str, secret: bytes) -> str:
    digest = hmac.new(secret, source.encode("utf-8"), sha256).hexdigest()
    return f"numra:rate:{scope}:{digest}"


class RateLimiter(Protocol):
    async def consume(self, key: str, limit: int, window_seconds: int) -> int | None: ...


class RedisEvalClient(Protocol):
    async def eval(
        self,
        script: str,
        number_of_keys: int,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> object: ...


_CONSUME_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[2])
end
local ttl = redis.call('TTL', KEYS[1])
if count > tonumber(ARGV[1]) then
  return {0, ttl}
end
return {1, ttl}
""".strip()


class RedisRateLimiter:
    def __init__(self, client: RedisEvalClient) -> None:
        self._client = client

    async def consume(self, key: str, limit: int, window_seconds: int) -> int | None:
        raw = await self._client.eval(_CONSUME_SCRIPT, 1, key, limit, window_seconds)
        result = cast(list[int], raw)
        return None if result[0] == 1 else max(result[1], 1)
