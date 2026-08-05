# ADR 0021 — Trennung AnalysisFactPackageV3 (transient) vs. ProviderFactPackageV3 (Closed-Book)

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Für die Berichtserzeugung muss ein strukturiertes Faktenpaket aus dem `ProfileCalculationResultV4` abgeleitet werden. Dieses enthält potenziell PII-relevante Informationen (Namen, Buchstabenketten, vollständige Traces). DeepSeek als externer Provider darf nur ein minimiertes, Closed-Book-Paket erhalten.
> **Betrifft:** Privacy, Agent-Architektur, Datenminimierung

---

## Entscheidung

### Zwei getrennte, request-scoped Verträge

1. **`AnalysisFactPackageV3` (intern, vollständig, transient):**
   - Enthält alle 15 Felder pro `AnalysisFactEntryV3`
   - Lebt nur für die Dauer des Requests
   - Wird **nicht** geloggt
   - Wird **nicht** standardmäßig serverseitig persistiert
   - Wird **nicht** in `AnalysisProvenance` gespeichert

2. **`ProviderFactPackageV3` (an DeepSeek gesendet, Closed-Book-minimiert):**
   - Abgeleitet via `derive_provider_fact_package_v3()`
   - **Keine** vollständigen Namen
   - **Keine** Buchstabenketten
   - **Keine** technischen Traces
   - `trace_ref` nur als opake Kennung
   - Keine überschüssigen Geburtsdatumskomponenten
   - Keine Audit-Metadaten

### Provenance

In `AnalysisProvenanceV3` werden nur gespeichert:

- `calculation_hash`
- Versionskennungen (`method_version`, `prompt_version`, `knowledge_bundle`, `report_schema_version`)
- Tatsächlich verwendete Referenz-IDs (`calculation_ref` / `knowledge_ref` je Claim)

Das reicht für vollständige Nachvollziehbarkeit/Audit, ohne die serverseitige Datenhaltung personenbezogener Ableitungen unnötig auszuweiten.

### Fact-Package-Builder

Der Builder lebt in einer eigenen Datei, getrennt vom `AgentServiceV3`:

```
src/numerology_agent/facts_v3.py     ← build_analysis_fact_package_v3()
                                        derive_provider_fact_package_v3()
src/numerology_agent/service_v3.py   ← ausschließlich AgentServiceV3
```

## Konsequenzen

- **Positiv:** Privacy by Design — DeepSeek sieht nie personenbezogene Rohdaten.
- **Positiv:** Audit-Trail bleibt vollständig über Referenz-IDs ohne Inhaltslogging.
- **Negativ:** Zwei separate Strukturen zu pflegen (explizit in Kauf genommen).

## Verweise

- ADR 0018 — V2-Stack-Isolation
- Prompt §8 (Privacy-Prinzipien): „Keine Berichtsinhalte oder vollständigen Fact Packages in Logs"
