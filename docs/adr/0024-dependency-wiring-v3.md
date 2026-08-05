# ADR 0024 — Dependency-Wiring des parallelen V3-Stacks

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Der bestehende App-Container (`src/numerology_api/app.py`) kennt nur `provider`, `rate_limiter`, `circuit_breaker`. Der neue V3-Stack braucht zusätzliche Abhängigkeiten (`provider_v3`, `idempotency_store`). Diese müssen typisiert und testbar sein, ohne dass die konkreten Implementierungen bereits vorliegen.
> **Betrifft:** API-Architektur, Dependency Injection, Testbarkeit

---

## Entscheidung

### Interfaces in Welle 1, Implementierungen in Welle 3

**Welle 1** liefert die reinen Interfaces/Settings:

```
src/numerology_agent/provider_v3.py    ← LlmProviderV3 Protocol, ProviderResultV3
src/numerology_api/idempotency.py      ← IdempotencyStoreV3 Protocol, AcquireResultV3, Status-Enums
src/numerology_api/dependencies_v3.py  ← V3-Settings und Factory-Schnittstellen
```

**Welle 3** liefert die konkreten Implementierungen:

```
DeepSeekProviderV3
RedisIdempotencyStoreV3
AgentServiceV3
/api/v2/analyses/*
```

### create_app-Signatur

```python
def create_app(
    settings: ApiSettings | None = None,
    *,
    provider: LlmProvider | None = None,
    provider_v3: LlmProviderV3 | None = None,       # NEU
    rate_limiter: RateLimiter | None = None,
    idempotency_store: IdempotencyStoreV3 | None = None,  # NEU
) -> FastAPI:
```

### App-State

```
api.state.provider              (bestehend)
api.state.provider_v3           (NEU)
api.state.circuit_breaker       (bestehend)
api.state.circuit_breaker_v3    (NEU)
api.state.rate_limiter          (bestehend)
api.state.idempotency_store     (NEU)
```

### Rollback

Der `/api/v2/analyses/*`-Router kann unabhängig deaktiviert werden, ohne `AgentService` oder den V1-Pfad zu berühren. Keine verzweigte Logik innerhalb des produktiven `AgentService`.

## Konsequenzen

- **Positiv:** Typisiert erweiterbar — `create_app` kann vor Implementierung getestet werden.
- **Positiv:** Rollback durch Router-Deaktivierung, kein Code-Revert nötig.
- **Neutral:** Zusätzliche optionale Parameter in `create_app`.

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `src/numerology_api/app.py` — `create_app()`, `production_dependencies()`
