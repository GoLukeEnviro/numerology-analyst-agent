# ADR 0023 — API-Idempotenz mit vollständigem Kryptovertrag

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Berichtserzeugung und Follow-ups sind teure, nicht-deterministische Operationen (LLM-Call). Bei Netzwerk-Retry nach erfolgreicher Generierung würde ohne Idempotenz ein zweiter Bericht erzeugt und doppelt abgerechnet. `report_id` (UUID) allein verhindert das nicht — der Client weiß nach verlorener HTTP-Response nicht, ob der Server den Bericht bereits erzeugt hat.
> **Betrifft:** API-Design, Privacy, Infrastruktur

---

## Entscheidung

### Request-Idempotenz-Schlüssel

Jeder V2-Analyserequest trägt eine vom Client erzeugte stabile `request_id` (UUID):

```python
class AnalysisReportRequestV2:
    request_id: UUID                  # Idempotenz-Key

class AnalysisFollowUpRequestV2:
    request_id: UUID                  # Idempotenz-Key
```

Der vollständige Idempotenzschlüssel: `pseudonymous_device_key + operation_type + request_id`

### IdempotencyStoreV3

```python
class IdempotencyStoreV3(Protocol):
    async def acquire(*, key, request_context_hash, operation, ttl_seconds) -> AcquireResultV3
    async def complete(*, key, owner_token, response_type, encrypted_response) -> None
    async def fail(*, key, owner_token, error_code, retryable) -> None
```

- **Zustände:** `PENDING`, `COMPLETED`, `FAILED`
- **TTL:** 1–6 Stunden, keine Verlängerung durch Reads
- **Atomar:** via Redis `SET NX` / Lua-Skript
- **409 bei Konflikt:** gleicher Key, anderer `request_context_hash` → `409 IDEMPOTENCY_KEY_CONFLICT`

### Request-Context-Hash

**Berichte:** `operation_type + calculation_hash + generation_context_hash + report_schema_version`
**Follow-ups:** `operation_type + calculation_hash + report_id + report_content_hash + normalisierte Frage + follow_up_prompt_version`

### Prüf-Reihenfolge (Idempotenz VOR Rate-Limit)

```
1. Request validieren
2. Kanonisches Profil prüfen
3. Idempotenz prüfen (existierende Response?)
4. Laufende Generierung erkennen (→ 202)
5. Atomaren Lock erwerben
6. Erst jetzt: Rate-Limit verbrauchen
7. Provider aufrufen
8. Verschlüsselte Response speichern
9. Lock auf COMPLETED setzen
```

### 202-Vertrag (laufende Generierung)

```
HTTP 202
Retry-After: <Sekunden>
Content-Type: application/problem+json
code: ANALYSIS_GENERATION_IN_PROGRESS
request_id: <UUID>
```

### Vollständiger Kryptovertrag

```
NUMRA_IDEMPOTENCY_ENCRYPTION_KEY (Umgebungsvariable)

- Separater Schlüssel — NIEMALS NUMRA_RATE_LIMIT_HMAC_SECRET wiederverwenden
- Authentifizierte Verschlüsselung: AES-GCM-256
- Zufälliger 96-Bit-Nonce pro Cache-Eintrag
- operation_type, request_context_hash und Key-ID als AAD (Additional Authenticated Data)
- Ciphertext, Nonce und Key-ID im Redis-Value
- KEINE Klartext-Response im Redis
- V3-Analyse-Start schlägt fail-fast fehl, wenn der Schlüssel fehlt
- V1-Startup bleibt davon unbeeinflusst
- Schlüsselrotation muss mindestens die maximale TTL überlappen
```

## Konsequenzen

- **Positiv:** Deterministische Idempotenz — keine doppelten Provider-Calls.
- **Positiv:** Privacy — verschlüsselte Cache-Ablage, keine Klartext-Inhalte in Redis.
- **Positiv:** Fail-Fast — fehlender Schlüssel blockiert V3, nicht V1.
- **Neutral:** Zusätzliche Infrastruktur-Abhängigkeit (Redis für Idempotenz).

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `src/numerology_api/rate_limit.py` — bestehender Rate-Limiter (nicht für Idempotenz zweckentfremden)
