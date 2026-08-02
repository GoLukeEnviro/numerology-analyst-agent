"""Settings resolution and production dependency wiring for the Numra API."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import logging
import os
from typing import cast

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from numerology_agent.deepseek import DeepSeekProvider, DeepSeekSettings
from numerology_agent.provider import LlmProvider
from numerology_agent.rate_limit import (
    RateLimiter,
    RedisEvalClient,
    RedisRateLimiter,
)

_DEPRECATION_LOGGER = logging.getLogger("numerology_api.deprecation")


class ApiSettings(BaseModel):
    """Immutable runtime settings; secret values are redacted by Pydantic."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str = "development"
    allowed_origins: tuple[str, ...] = Field(
        default=("http://localhost:5173", "http://127.0.0.1:5173")
    )
    llm_enabled: bool = False
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-pro"
    deepseek_thinking_enabled: bool = True
    deepseek_reasoning_effort: str = "high"
    deepseek_max_output_tokens: int = 8192
    deepseek_max_retries: int = 3
    redis_url: SecretStr = SecretStr("redis://redis:6379/0")
    rate_limit_hmac_secret: SecretStr | None = None
    max_request_body_bytes: int = Field(default=65_536, ge=256, le=1_048_576)


def _env_with_deepseek_fallback(new_key: str, legacy_key: str) -> str | None:
    """Read ``DEEPSEEK_*`` (preferred) with ``NUMRA_DEEPSEEK_*`` fallback.

    If only the legacy ``NUMRA_DEEPSEEK_*`` variable is set, a deprecation
    warning is logged. The warning contains NO secret value.
    """
    new_val = os.getenv(new_key)
    if new_val is not None:
        return new_val
    legacy_val = os.getenv(legacy_key)
    if legacy_val is not None:
        _DEPRECATION_LOGGER.warning(
            "Environment variable %s is deprecated; use %s instead. The value is not logged.",
            legacy_key,
            new_key,
        )
    return legacy_val


def settings_from_environment() -> ApiSettings:
    """Read non-secret API settings from environment variables.

    DeepSeek variables use the ``DEEPSEEK_*`` prefix (preferred), with a
    fallback to the legacy ``NUMRA_DEEPSEEK_*`` prefix (deprecated, warns).
    Operational variables (``NUMRA_LLM_ENABLED``, ``NUMRA_REDIS_URL``, etc.)
    remain under the ``NUMRA_`` prefix.
    """
    origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "NUMRA_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    api_key = _env_with_deepseek_fallback("DEEPSEEK_API_KEY", "NUMRA_DEEPSEEK_API_KEY")
    rate_secret = os.getenv("NUMRA_RATE_LIMIT_HMAC_SECRET")
    return ApiSettings(
        environment=os.getenv("NUMRA_ENVIRONMENT", "development"),
        allowed_origins=origins,
        llm_enabled=os.getenv("NUMRA_LLM_ENABLED", "false").lower() == "true",
        deepseek_api_key=SecretStr(api_key) if api_key else None,
        deepseek_base_url=_env_with_deepseek_fallback(
            "DEEPSEEK_BASE_URL", "NUMRA_DEEPSEEK_BASE_URL"
        )
        or "https://api.deepseek.com",
        deepseek_model=_env_with_deepseek_fallback("DEEPSEEK_MODEL", "NUMRA_DEEPSEEK_MODEL")
        or "deepseek-v4-pro",
        deepseek_thinking_enabled=(
            _env_with_deepseek_fallback(
                "DEEPSEEK_THINKING_ENABLED", "NUMRA_DEEPSEEK_THINKING_ENABLED"
            )
            or "true"
        ).lower()
        == "true",
        deepseek_reasoning_effort=_env_with_deepseek_fallback(
            "DEEPSEEK_REASONING_EFFORT", "NUMRA_DEEPSEEK_REASONING_EFFORT"
        )
        or "high",
        deepseek_max_output_tokens=int(
            _env_with_deepseek_fallback(
                "DEEPSEEK_MAX_OUTPUT_TOKENS", "NUMRA_DEEPSEEK_MAX_OUTPUT_TOKENS"
            )
            or "8192"
        ),
        deepseek_max_retries=int(
            _env_with_deepseek_fallback("DEEPSEEK_MAX_RETRIES", "NUMRA_DEEPSEEK_MAX_RETRIES") or "3"
        ),
        redis_url=SecretStr(os.getenv("NUMRA_REDIS_URL", "redis://redis:6379/0")),
        rate_limit_hmac_secret=SecretStr(rate_secret) if rate_secret else None,
        max_request_body_bytes=int(os.getenv("NUMRA_MAX_REQUEST_BODY_BYTES", "65536")),
    )


def package_version() -> str:
    """Return the installed package version, falling back to a dev marker."""
    try:
        return version("numerology-analyst-agent")
    except PackageNotFoundError:
        return "0.0.0+dev"


def production_dependencies(
    settings: ApiSettings,
    provider: LlmProvider | None,
    rate_limiter: RateLimiter | None,
) -> tuple[LlmProvider | None, RateLimiter | None]:
    """Resolve production-grade LLM provider and rate limiter when enabled.

    When ``llm_enabled`` is false the injected (or ``None``) dependencies are
    returned unchanged. When enabled, runtime gates are verified and missing
    secrets raise a :class:`RuntimeError` so misconfiguration fails fast.
    """
    if not settings.llm_enabled:
        return provider, rate_limiter
    # Lazy import: numerology_safety's package init pulls in the
    # interpretation chain, which itself imports numerology_safety.validation.
    # By the time production_dependencies runs, that chain is fully loaded,
    # so importing here avoids the module-level circular import.
    from numerology_safety.runtime_gate import verify_runtime_gates

    verify_runtime_gates()
    if provider is None:
        if settings.deepseek_api_key is None:
            raise RuntimeError("DEEPSEEK_API_KEY is required when LLM is enabled")
        provider = DeepSeekProvider(
            DeepSeekSettings(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                model=settings.deepseek_model,
                thinking_enabled=settings.deepseek_thinking_enabled,
                reasoning_effort=settings.deepseek_reasoning_effort,
                max_output_tokens=settings.deepseek_max_output_tokens,
                max_retries=settings.deepseek_max_retries,
            )
        )
    if rate_limiter is None:
        from redis.asyncio import Redis

        client = Redis.from_url(settings.redis_url.get_secret_value(), decode_responses=True)
        rate_limiter = RedisRateLimiter(cast(RedisEvalClient, client))
    if settings.rate_limit_hmac_secret is None:
        raise RuntimeError("NUMRA_RATE_LIMIT_HMAC_SECRET is required when LLM is enabled")
    return provider, rate_limiter
