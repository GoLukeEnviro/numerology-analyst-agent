"""Deterministic contracts for the LLM circuit breaker."""

from __future__ import annotations

import pytest

from numerology_agent.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)


def _breaker(now: list[float]) -> CircuitBreaker:
    """Create a breaker with an injectable clock (list as mutable counter)."""
    return CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30.0,
        clock=lambda: now[0],
    )


def test_breaker_starts_closed() -> None:
    breaker = CircuitBreaker()
    assert breaker.state == CircuitState.CLOSED


def test_breaker_opens_after_failure_threshold() -> None:
    now = [0.0]
    breaker = _breaker(now)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.record_failure()
    state_after: CircuitState = breaker.state
    assert state_after == CircuitState.OPEN


def test_open_breaker_rejects_calls() -> None:
    now = [0.0]
    breaker = _breaker(now)
    for _ in range(3):
        breaker.record_failure()
    with pytest.raises(CircuitOpenError):
        breaker.before_call()


def test_breaker_transitions_to_half_open_after_recovery_timeout() -> None:
    now = [0.0]
    breaker = _breaker(now)
    for _ in range(3):
        breaker.record_failure()
    assert breaker.state == CircuitState.OPEN

    now[0] = 31.0  # past recovery_timeout
    half_state: CircuitState = breaker.state
    assert half_state == CircuitState.HALF_OPEN


def test_half_open_success_closes_breaker() -> None:
    now = [0.0]
    breaker = _breaker(now)
    for _ in range(3):
        breaker.record_failure()
    now[0] = 31.0
    assert breaker.state == CircuitState.HALF_OPEN

    breaker.record_success()
    closed_state: CircuitState = breaker.state
    assert closed_state == CircuitState.CLOSED


def test_half_open_failure_reopens_breaker() -> None:
    now = [0.0]
    breaker = _breaker(now)
    for _ in range(3):
        breaker.record_failure()
    now[0] = 31.0
    assert breaker.state == CircuitState.HALF_OPEN

    breaker.record_failure()
    reopened_state: CircuitState = breaker.state
    assert reopened_state == CircuitState.OPEN


def test_success_resets_failure_count() -> None:
    now = [0.0]
    breaker = _breaker(now)
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_success()
    # Two more failures should NOT open (we are back to 0 failures after success).
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED


def test_invalid_constructor_args() -> None:
    with pytest.raises(ValueError, match="failure_threshold"):
        CircuitBreaker(failure_threshold=0)
    with pytest.raises(ValueError, match="recovery_timeout"):
        CircuitBreaker(recovery_timeout=0)
