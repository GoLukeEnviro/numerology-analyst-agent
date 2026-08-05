# ADR 0018 — Strikt paralleler V2/V3-Stack: Keine geteilten versionierten Modelle

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Der V1-Stack (`/api/v1/*`, `AgentService`, `AnalysisReport` v2, `de-v2.json`) ist produktiv und rückwärtskompatibel. Der V2/V3-Stack (`/api/v2/*`, `AgentServiceV3`, `AnalysisReportV3`, `de-v3.json`) soll parallel entstehen, ohne V1-Verträge zu verändern. Ein dreifacher Code-Audit bestätigte die vollständige Isolation der bestehenden `pythagorean-v2`-Berechnung von der Produktionsoberfläche.
> **Betrifft:** Architektur, API-Design, Paketstruktur

---

## Entscheidung

Der V2/V3-Stack entsteht als **vollständig paralleler, neuer Stack** mit folgenden
Isolationsregeln:

### Getrennt (dürfen NICHT geteilt werden)

- **Versionierte HTTP-Request-/Response-Modelle** zwischen `/api/v1` und `/api/v2`
- **Reportmodelle** (`AnalysisReport` v2 vs. `AnalysisReportV3`)
- **Providerresultate** (`ProviderResult` vs. `ProviderResultV3`)
- **Zustandsbehaftete Services** (`AgentService` vs. `AgentServiceV3`)
- **Prompt-Dateien** (`de-report-system.md` vs. `de-report-system-v3.md`)
- **Wissens-Bundles** (`de-v2.json` vs. `de-v3.json`)

### Erlaubte Wiederverwendung

Stabile, unveränderte Domainprimitiven und technische Low-Level-Infrastruktur dürfen
wiederverwendet werden, **sofern dadurch kein V1-Vertrag verändert wird**:

- `PersonInput`, `MethodPolicy`
- `ProfileCalculationResultV4` (Rechenkern-Output, bereits vorhanden)
- `KarmicOccurrence`, `NumberModel`
- `ProblemDetails` (RFC 9457)
- Rate-Limit- und Circuit-Breaker-Primitiven
- Kanonische Hash-Helfer

### Dateistruktur

Pro V3-Art eine eigene Datei — bestehende Dateien bleiben **vollständig unverändert**:

```
src/numerology_agent/models.py          unverändert
src/numerology_agent/models_v3.py       neu
src/numerology_agent/provider.py        unverändert
src/numerology_agent/provider_v3.py     neu
src/numerology_agent/deepseek.py        unverändert
src/numerology_agent/deepseek_v3.py     neu
src/numerology_agent/prompts.py         unverändert
src/numerology_agent/prompts_v3.py      neu
src/numerology_agent/service.py         unverändert
src/numerology_agent/service_v3.py      neu
src/numerology_agent/facts_v3.py        neu (Fact-Package-Builder)
```

Gleiches Muster für `numerology_knowledge`, `numerology_interpretation` und
`numerology_api/routes`.

### API-Pfade

```
/api/v1/*   → V1-Stack (unverändert, außer dokumentiertem Guard-Fix)
/api/v2/*   → V2/V3-Stack (vollständig neu)
```

Keine gemeinsamen Unions, keine diskriminierten Typen über API-Versionen hinweg.

## Konsequenzen

- **Positiv:** Kein Regressionsrisiko für V1. Rollback durch Router-Deaktivierung.
- **Positiv:** V1-OpenAPI-Vertrag bleibt byte-identisch.
- **Negativ:** Etwas mehr Code-Duplizierung (explizit in Kauf genommen für V1-Sicherheit).
- **Negativ:** `schema_version`-Felder bleiben `str` (keine `Literal`-Verschärfung, da dies das generierte JSON-Schema der V1-Requestmodelle verändern würde).

## Verweise

- ADR 0017 — V2-Parallel-Entwicklung Sequenz
- `docs/plans/numra-full-analysis-execution-plan.md` — Execution Plan
- `docs/plans/numra-full-analysis-v2-v3.md` — Architekturquelle
