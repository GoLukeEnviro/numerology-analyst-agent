# ADR 0022 — finish_reason-Klassifikationsmatrix im V3-Provider-Stack

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Der bestehende `DeepSeekProvider` (V1) liest `finish_reason` nicht aus — ein abgeschnittener Bericht (`max_tokens` überschritten) würde unbemerkt als vollständig behandelt. Der neue V3-Provider muss alle `finish_reason`-Fälle explizit behandeln und darf nie unvollständige Berichte als vollständig ausliefern.
> **Betrifft:** Agent-Architektur, Fehlerbehandlung, Provider-Vertrag

---

## Entscheidung

### ProviderResultV3

```python
class ProviderResultV3:
    content: str
    model: str
    finish_reason: str               # Pflichtfeld, explizit ausgewertet
    provider_fingerprint: str | None
    prompt_tokens: int
    completion_tokens: int
```

### Verbindliche finish_reason-Matrix

| `finish_reason`                | Klassifikation     | Behandlung                                                                                                                                                                                                               |
| ------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `stop`                         | Normal             | Inhalt validieren, als vollständig behandeln                                                                                                                                                                             |
| `length`                       | Unvollständig      | Max. 1 Zusatzversuch mit erhöhtem `max_output_tokens` (innerhalb `NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS`). Bleibt es bei `length`: Kapitelorchestrierung oder Fail-Closed. **Nie** einen unvollständigen Bericht speichern. |
| `content_filter`               | Sicherheitsabbruch | Fail-Closed. Keine Teilantwort speichern.                                                                                                                                                                                |
| `tool_calls`                   | Vertragsverletzung | Fail-Closed. Keine Tools angeboten → Provider hat entgegen der Konfiguration Tools aufgerufen.                                                                                                                           |
| `insufficient_system_resource` | Transient          | Retry mit Backoff (wie 429/502/503/504)                                                                                                                                                                                  |
| leer / unbekannt               | Undefiniert        | Fail-Closed + Telemetrie                                                                                                                                                                                                 |

### Strategie bei length (detailliert)

1. Nicht als gültigen Bericht akzeptieren/speichern.
2. Maximal **ein** kontrollierter Zusatzversuch mit erhöhtem Budget.
3. Bleibt es bei `length`: entweder auf Kapitel-Orchestrierung wechseln oder Fail-Closed mit verständlicher Fehlermeldung — nie stillschweigend ausliefern.

### UX-Vertrag vs. Provider-Vertrag

Der UX-Vertrag lautet: **ein Nutzerauftrag = eine Berichtsversion**. Ob das Backend dafür einen einzigen Provider-Request oder bei wiederholtem `length` mehrere deterministisch orchestrierte Kapitel-Calls nutzt, wird nach der Evaluation (Welle 5A) entschieden und ändert den UI-Vertrag nicht.

## Konsequenzen

- **Positiv:** Keine stillen Teilberichte mehr — jeder gespeicherte Bericht ist vollständig.
- **Positiv:** Strukturierte Fehlerbehandlung für alle Provider-Zustände.
- **Neutral:** `DeepSeekProvider` (V1) bleibt unverändert (kein Backport des `finish_reason`-Handlings).

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `src/numerology_agent/deepseek.py` — bestehender V1-Provider (unverändert)
