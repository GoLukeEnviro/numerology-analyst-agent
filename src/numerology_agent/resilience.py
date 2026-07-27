"""Deterministic, dependency-free circuit breaker for the LLM boundary.

The breaker protects the agent service from cascading provider failures:
after ``failure_threshold`` consecutive errors it opens for
``recovery_timeout`` seconds. A single probe is allowed in ``HALF_OPEN``; on
success the breaker closes again, on failure it re-opens.

Design goals:
- Deterministic and testable via an injectable ``clock`` callable.
- No external dependencies (pure stdlib).
- ``mypy strict`` conformant.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from time import time as _real_time


class CircuitState(str, Enum):
    """Stable, machine-readable breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    """Raised when a call is attempted while the breaker is OPEN.

    Sanitized: carries no provider payload, secrets or response bodies.
    """


Clock = Callable[[], float]


class CircuitBreaker:
    """A minimal, deterministic circuit breaker.

    The breaker is intentionally simple and side-effect free apart from the
    injected clock. It does NOT perform the guarded call itself; callers wrap
    their operation and report success/failure via :meth:`record_success` /
    :meth:`record_failure`, or use :meth:`before_call` to fail fast.
    """

    __slots__ = (
        "_clock",
        "_failure_threshold",
        "_failures",
        "_opened_at",
        "_recovery_timeout",
        "_state",
    )

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        clock: Clock = _real_time,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._clock = clock
        self._state: CircuitState = CircuitState.CLOSED
        self._failures: int = 0
        self._opened_at: float = 0.0

    @property
    def state(self) -> CircuitState:
        """Current effective state (auto-transitions OPEN -> HALF_OPEN)."""
        if self._state is CircuitState.OPEN and self._has_recovered():
            self._state = CircuitState.HALF_OPEN
        return self._state

    @property
    def failure_threshold(self) -> int:
        return self._failure_threshold

    @property
    def recovery_timeout(self) -> float:
        return self._recovery_timeout

    def before_call(self) -> None:
        """Fail fast with :class:`CircuitOpenError` when the breaker is OPEN.

        Auto-transitions to ``HALF_OPEN`` once the recovery timeout elapses,
        allowing exactly one probe through.
        """
        current = self.state
        if current is CircuitState.OPEN:
            raise CircuitOpenError("circuit breaker is open")

    def record_success(self) -> None:
        """Mark the last guarded call as successful (closes the breaker)."""
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = 0.0

    def record_failure(self) -> None:
        """Mark the last guarded call as failed.

        In ``HALF_OPEN`` a single failure re-opens the breaker immediately.
        In ``CLOSED`` consecutive failures are counted; once the threshold is
        reached the breaker opens.
        """
        if self._state is CircuitState.HALF_OPEN:
            self._open()
            return
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._open()

    def reset(self) -> None:
        """Force the breaker back to its initial CLOSED state (test/admin hook)."""
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = 0.0

    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()

    def _has_recovered(self) -> bool:
        return (self._clock() - self._opened_at) >= self._recovery_timeout


__all__ = ["CircuitBreaker", "CircuitOpenError", "CircuitState", "Clock"]
