"""Rate limiter key and expiration contracts."""

from __future__ import annotations

import pytest

from numerology_agent.rate_limit import RedisRateLimiter, pseudonymous_key


def test_pseudonymous_key_never_contains_source_value() -> None:
    key = pseudonymous_key("ip", "203.0.113.42", b"secret")

    assert key.startswith("numra:rate:ip:")
    assert "203.0.113.42" not in key


class FakeRedis:
    def __init__(self, result: list[int]) -> None:
        self.result = result
        self.calls: list[tuple[str, int, str, int, int]] = []

    async def eval(
        self,
        script: str,
        number_of_keys: int,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> list[int]:
        self.calls.append((script, number_of_keys, key, limit, window_seconds))
        return self.result


@pytest.mark.anyio
async def test_redis_limiter_returns_ttl_only_when_limit_is_exceeded() -> None:
    allowed_redis = FakeRedis([1, 0])
    denied_redis = FakeRedis([0, 713])

    assert await RedisRateLimiter(allowed_redis).consume("key", 20, 86400) is None
    assert await RedisRateLimiter(denied_redis).consume("key", 20, 86400) == 713
    assert "EXPIRE" in denied_redis.calls[0][0]
