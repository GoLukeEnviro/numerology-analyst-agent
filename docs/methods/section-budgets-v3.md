# Section-Längenbudgets V3

> Zeichenlimits für die 18 AnalysisSectionV3-Felder. Diese Budgets werden im Prompt als verbindliche Grenzen kommuniziert und im `_validate_draft_v3()`-Validator geprüft.
> Stand: 2026-08-05

## Globale Budgets

| Feld | Typ | Limit |
|---|---|---|
| `summary` (Standard) | Zeichen | max. 800 |
| `summary` (executive_overview, final_synthesis) | Zeichen | max. 1.400 |
| `claims` (applicable=true) | Anzahl | 1–4 |
| `claims` (applicable=false) | Anzahl | 0 |
| `supporting_calculation_refs` | Anzahl | 0–10 |
| `supporting_knowledge_refs` | Anzahl | 0–10 |
| `counter_hypotheses` | Anzahl | 0–2 |
| `reflection_questions` | Anzahl | 0–2 |
| `practical_options` | Anzahl | 0–2 |
| `limitations` | Anzahl | 0–1 |

## Pro Section

| # | Section-ID | summary_max | Besonderheit |
|---|---|---|---|
| 1 | `executive_overview` | 1.400 | Gesamtüberblick |
| 2 | `life_path_and_purpose` | 800 | primary + secondary getrennt |
| 3 | `birthday_and_attitude` | 800 | |
| 4 | `inner_motivation` | 800 | |
| 5 | `expression_and_external_persona` | 800 | |
| 6 | `maturity_and_development` | 800 | |
| 7 | `number_harmonies` | 800 | |
| 8 | `number_tensions` | 800 | |
| 9 | `repetitions_and_missing_values` | 800 | |
| 10 | `life_phases` | 800 | |
| 11 | `personal_cycles` | 800 | |
| 12 | `pinnacles` | 800 | |
| 13 | `challenges` | 800 | |
| 14 | `shadow_patterns` | 800 | |
| 15 | `development_opportunities` | 800 | |
| 16 | `practical_integration` | 800 | |
| 17 | `final_synthesis` | 1.400 | Gesamtsynthese |
| 18 | `method_and_calculation_notes` | 400 | Kurz — Rechenweg wird deterministisch gerendert |

## Validierung

Der `_validate_draft_v3()`-Validator prüft:
- Section-ID-Vollständigkeit (alle 18, keine doppelten, keine unbekannten)
- Reihenfolge (1→18)
- `applicable`-Konsistenz (Claims/Refs nur wenn applicable=true)
- Zeichenlimits für `summary`
- Anzahl-Limits für Claims, Hypothesen, Fragen, Optionen, Limitations

## MAX_CANONICAL_REPORT_BYTES

Wird in Welle 3 aus dem Zwei-Korpus-Test (Golden-Profile + Maximalfälle) abgeleitet. Formel:

```
MAX_CANONICAL_REPORT_BYTES = V2_FOLLOW_UP_REQUEST_LIMIT
    - MAX_SERIALIZED_V4_PROFILE_BYTES
    - MAX_SERIALIZED_QUESTION_BYTES
    - ENVELOPE_OVERHEAD_BYTES
    - SAFETY_MARGIN_BYTES
```
