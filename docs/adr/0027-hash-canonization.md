# ADR 0027 — Hash- und Signaturkanonisierung für V3-Berichte

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** `AnalysisReportV3` benötigt zwei getrennte Hash-Konzepte: einen für die Generierungskonfiguration (zur Idempotenz- und Reproduzierbarkeitsprüfung) und einen für den konkreten Berichtinhalt (zur Inhaltsidentifikation). Ein einzelner „Fingerprint" würde Konfigurations- und Inhaltsidentität vermischen.
> **Betrifft:** Kryptografie, Auditierbarkeit, Idempotenz

---

## Entscheidung

### Zwei getrennte Hashes

1. **`generation_context_hash`** — identifiziert die **Konfiguration** eines Laufs:

   ```
   calculation_hash
   profile_schema_version
   method_version
   provider_fact_package_hash
   capability_matrix_version
   prompt_version
   prompt_content_hash
   knowledge_bundle_id
   knowledge_content_hash
   report_schema_version
   model
   thinking_mode
   reasoning_effort
   orchestration_version
   ```

   Zwei Läufe mit derselben Konfiguration können unterschiedliche Texte erzeugen (LLM nicht-deterministisch).

2. **`report_content_hash`** — identifiziert den **konkreten Inhalt** eines Berichts:
   ```
   schema_version
   content.summary
   content.sections
   content.global_limitations
   ```
   **Nicht enthalten:** `report_id`, `report_content_hash` selbst, `context_signature`, Zeitstempel, Tokenzahlen, Provider-Fingerprint.

### Envelope-Reihenfolge

```
1. Reportinhalt validieren (Schema, Sections, Längenbudgets)
2. report_content_hash berechnen (über validierte Inhalte)
3. generation_context_hash einsetzen (über Konfiguration)
4. report_id erzeugen (UUID)
5. Finale AnalysisReportV3-Envelope bilden
6. context_signature berechnen (HMAC über Envelope ohne context_signature)
```

### Kanonische JSON-Serialisierung

```python
json.dumps(
    projection,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

SHA-256 über die canonical UTF-8 bytes.

### Stabilitätstests

Explizite Tests, dass identische Inputs identische Hashes erzeugen — auch über Prozessgrenzen hinweg.

## Konsequenzen

- **Positiv:** Auditierbare Trennung von Konfigurations- und Inhaltsidentität.
- **Positiv:** Deterministische, sprachübergreifend prüfbare Serialisierung.
- **Positiv:** `context_signature` (HMAC) bleibt in bestehender Funktion erhalten.

## Verweise

- ADR 0023 — API-Idempotenz
- `src/numerology_agent/service.py:80-95` — bestehende `context_signature`-Implementierung
