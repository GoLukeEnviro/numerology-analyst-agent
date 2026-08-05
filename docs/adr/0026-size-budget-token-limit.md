# ADR 0026 — Gesamtgrößenbudget und projektinterne Token-Grenze

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Ein V3-Follow-up-Request enthält das vollständige V4-Profil, den vollständigen Bericht (18 Sections, Claims, Referenzen, Gegenhypothesen, Fragen, Optionen, Provenienz, Signaturen) und eine Nutzerfrage — und kann das bestehende HTTP-Request-Limit (65.536 Bytes) überschreiten. Gleichzeitig muss die maximale Berichtsgröße so bemessen sein, dass ein Follow-up noch in das Limit passt.
> **Betrifft:** API-Design, Performance, Kostenkontrolle

---

## Entscheidung

### Berichtslimit als abgeleitete Größe

```text
MAX_CANONICAL_REPORT_BYTES
=
MAX_FOLLOW_UP_REQUEST_BYTES
- MAX_SERIALIZED_V4_PROFILE_BYTES
- MAX_SERIALIZED_QUESTION_BYTES
- ENVELOPE_OVERHEAD_BYTES
- SAFETY_MARGIN_BYTES
```

Das wird mit **zwei Korpora** getestet:

1. **Golden-Referenzprofile** (alle 5 aus `tests/golden/reference_profiles_v2.yaml`)
2. **Maximalfälle:** lange Namen, aktive Namen, maximale Traces, maximal erlaubte Sections, maximale Frage

Erst nach den Tests wird entschieden:

- den Bericht kleiner halten, **oder**
- ausschließlich für `/api/v2/analyses/follow-up` ein höheres, geprüftes, pfadspezifisches Limit einführen.

Ein **globales** Hochsetzen verändert die Sicherheitsgrenze aller Endpunkte und wird vermieden.

### Projektinterne Token-Grenze

```text
NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS = 32768
```

**Dies ist eine anfängliche projektinterne Kosten-, Latenz- und Validierungsgrenze — NICHT das technische Maximum des Providers.** DeepSeek dokumentiert für `deepseek-v4-pro` eine maximale Ausgabe von bis zu 384K Tokens.

Die Evaluation (Welle 5A) darf eine andere projektinterne Grenze empfehlen, sofern Größenbudget, Kostenbudget, Latenz, Validierung und Idempotenzspeicherung nachweislich bestanden sind.

### Längenbudgets pro Section

```
summary:               max. 800 Zeichen (1400 für executive_overview/final_synthesis)
claims:                1–4 bei applicable=true, 0 bei false
counter_hypotheses:    0–2
reflection_questions:  0–2
practical_options:     0–2
limitations:           0–1
method_and_calculation_notes: kurz — Rechenweg wird deterministisch gerendert
```

## Konsequenzen

- **Positiv:** Nachweisbare Größenkontrolle — kein stilles Überschreiten des Request-Limits.
- **Positiv:** Klare Trennung zwischen projektinterner und Provider-Grenze.
- **Neutral:** Konkreter `MAX_CANONICAL_REPORT_BYTES`-Wert wird erst nach Zwei-Korpus-Test in Welle 3 festgelegt.

## Verweise

- `tests/golden/reference_profiles_v2.yaml` — Golden-Referenzprofile
- `src/numerology_api/middleware.py` — `RequestBodyLimitMiddleware`
