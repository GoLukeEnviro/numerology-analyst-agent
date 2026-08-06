# Numra V3 Task Prompt — 18-Section-Bericht

Erstelle einen vollständigen Analysebericht im JSON-Format mit exakt 18 Sections.
Jede Section hat eine feste `section_id` aus der folgenden Liste.

## Section-Plan (verbindliche Reihenfolge)

| section_id                        | UI-Label                   | Immer anwendbar? |
| --------------------------------- | -------------------------- | ---------------- |
| `executive_overview`              | Überblick                  | Ja               |
| `life_path_and_purpose`           | Lebensweg                  | Ja               |
| `birthday_and_attitude`           | Geburtstag & Einstellung   | Ja               |
| `inner_motivation`                | Innere Motivation          | Ja               |
| `expression_and_external_persona` | Ausdruck & Wirkung         | Ja               |
| `maturity_and_development`        | Reife & Entwicklung        | Ja               |
| `number_harmonies`                | Zahlenharmonien            | Bedingt          |
| `number_tensions`                 | Zahlenspannungen           | Bedingt          |
| `repetitions_and_missing_values`  | Wiederholungen & Fehlendes | Bedingt          |
| `life_phases`                     | Lebensphasen               | Bedingt          |
| `personal_cycles`                 | Persönliche Zyklen         | Ja               |
| `pinnacles`                       | Pinnacles                  | Ja               |
| `challenges`                      | Challenges                 | Ja               |
| `shadow_patterns`                 | Schattenmuster             | Bedingt          |
| `development_opportunities`       | Entwicklungsmöglichkeiten  | Ja               |
| `practical_integration`           | Praktische Integration     | Ja               |
| `final_synthesis`                 | Abschliessende Synthese    | Ja               |
| `method_and_calculation_notes`    | Rechenweg                  | Ja               |

## JSON-Schema (verbindlich)

```json
{
  "content": {
    "summary": "string (max. 1400 Zeichen)",
    "sections": [
      {
        "section_id": "string (eine der 18 IDs)",
        "applicable": true,
        "model_heading": "string | null",
        "summary": "string (max. 800 Zeichen, 1400 für executive_overview/final_synthesis)",
        "claims": [
          {
            "claim_id": "string",
            "claim_type": "traditional_claim | interpretive_hypothesis | practical_suggestion",
            "text": "string (max. 1200 Zeichen)",
            "calculation_refs": ["string"],
            "knowledge_refs": ["string"],
            "uncertainty": "string | null",
            "composer_rule_id": null
          }
        ],
        "supporting_calculation_refs": ["string"],
        "supporting_knowledge_refs": ["string"],
        "counter_hypotheses": ["string"],
        "reflection_questions": ["string"],
        "practical_options": ["string"],
        "limitations": ["string"]
      }
    ],
    "global_limitations": ["string"]
  }
}
```

## Längenbudgets

- `summary`: max. 800 Zeichen (1400 für executive_overview und final_synthesis)
- `claims`: 1–4 wenn applicable=true, 0 wenn applicable=false
- `counter_hypotheses`: 0–2
- `reflection_questions`: 0–2
- `practical_options`: 0–2
- `limitations`: 0–1 pro Section

## Capability-Hinweise

Das Backend liefert für jede Section einen Capability-Hinweis. Ist eine Section als `supported: false` markiert, MUSS `applicable: false` gesetzt sein.

## Method & Calculation Notes

Der Rechenweg wird deterministisch vom Backend gerendert. Beschreibe ihn NICHT in Prosa nach, sondern verweise nur kurz auf die verwendete Methode (pythagorean-v2).
