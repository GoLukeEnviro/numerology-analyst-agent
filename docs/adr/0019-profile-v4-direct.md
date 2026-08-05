# ADR 0019 — ProfileCalculationResultV4 direkt in /api/v2/analyses/\*

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** `/api/v2/analyses/*` soll Berichte auf Basis von `pythagorean-v2`-Profilen (`ProfileCalculationResultV4`) erzeugen. Der bestehende V1-Pfad `/api/v1/analyses/*` verwendet eine `AnalysisProfile`-Union (`ProfileCalculationResult | LegacyV2ProfileCalculationResult`). Eine entsprechende Union für V2 würde `/api/v1/analyses/*` potenziell für V4-Payloads öffnen.
> **Betrifft:** API-Design, HTTP-Verträge, OpenAPI

---

## Entscheidung

`/api/v2/analyses/*` akzeptiert `ProfileCalculationResultV4` **direkt, ohne Union**:

```python
class AnalysisReportRequestV2:
    request_id: UUID
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4        # direkt, keine Union
```

### Was NICHT gemacht wird

- **Keine** `Literal`-Verschärfung der bestehenden `schema_version`-Felder in den Domainmodellen. Diese sind aktuell `str` und bleiben `str` — eine Änderung auf `Literal` würde das generierte JSON-Schema der bestehenden V1-Requestmodelle verändern und `/api/v1/analyses/*` im OpenAPI-Vertrag nicht mehr byte-identisch halten.
- **Keine** neue `AnalysisProfileV2`-Union. Solange `/api/v2/analyses/*` ausschließlich V4-Profile akzeptiert, ist keine diskriminierte Union erforderlich.
- **Keine** Änderung der bestehenden `AnalysisProfile`-Union — sie bleibt unverändert und wird ausschließlich von `/api/v1/analyses/*` verwendet.

### Zukünftige Erweiterung

Eine diskriminierte Union (bzw. ein HTTP-spezifischer diskriminierter Wrapper) wird **erst dann** eingeführt, wenn im V2-API-Vertrag tatsächlich mehrere Profilvarianten existieren.

## Konsequenzen

- **Positiv:** `/api/v1/analyses/*` OpenAPI-Vertrag bleibt byte-identisch.
- **Positiv:** Keine `Literal`-Migration der Domainmodelle nötig — kein Risiko für bestehende Serialisierung.
- **Neutral:** Der Request-Typ ist fest an `ProfileCalculationResultV4` gebunden — ausreichend für den aktuellen Scope.

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `src/numerology_domain/_models/profile.py` — `schema_version`-Felder
- `src/numerology_api/http_models.py` — `AnalysisProfile`-Union
