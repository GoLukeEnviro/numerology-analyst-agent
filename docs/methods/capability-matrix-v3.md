# Capability-Matrix V3 — 18 Sections

> Welche Section braucht welche deterministischen Daten? Welche Sections sind immer anwendbar, welche nur bei bestimmten Profilkonstellationen?
> Stand: 2026-08-05

## Immer anwendbar (applicable=true für alle Profile)

| Section-ID                        | Benötigte Daten                                   | Berechnungsquelle                           |
| --------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `executive_overview`              | Alle Kernzahlen                                   | Gesamtes `ProfileCalculationResultV4`       |
| `life_path_and_purpose`           | `life_path_primary`, `life_path_secondary`        | `profile.life_path.*`                       |
| `birthday_and_attitude`           | `birthday`, `attitude`                            | `profile.birthday`, `profile.attitude`      |
| `inner_motivation`                | `soul_urge`                                       | `profile.soul_urge`                         |
| `expression_and_external_persona` | `expression`, `personality`                       | `profile.expression`, `profile.personality` |
| `maturity_and_development`        | `maturity`                                        | `profile.maturity`                          |
| `personal_cycles`                 | `personal_year`, `personal_month`, `personal_day` | `profile.personal_year/month/day`           |
| `pinnacles`                       | `pinnacle_1..4`                                   | `profile.pinnacles`                         |
| `challenges`                      | `challenge_1..4`                                  | `profile.challenges`                        |
| `final_synthesis`                 | Alle Sections                                     | Gesamter Bericht                            |
| `method_and_calculation_notes`    | Trace, Berechnungsmethode                         | `profile`-Metadaten, Trace                  |

## Bedingt anwendbar (applicable abhängig von Profil)

| Section-ID                       | Bedingung für applicable=true                                                    | Benötigte Daten                                    |
| -------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| `number_harmonies`               | ≥2 gleiche Zahlen in unterschiedlichen Kontexten                                 | `result_context`-Vergleich über alle `NumberModel` |
| `number_tensions`                | Bekannte Kontrastpaare vorhanden (1-2, 4-5, 3-4, 7-3, 8-9)                       | Kontext-Paar-Analyse                               |
| `repetitions_and_missing_values` | Wiederholungen (≥3× gleiche Zahl) ODER fehlende Ziffern 1–9                      | Frequenzanalyse aller Zahlen                       |
| `life_phases`                    | Alter ≥ erste Pinnacle-Periode                                                   | `birth_date`, aktuelle Pinnacle-Periode            |
| `shadow_patterns`                | Karmic-Debt-Vorkommen (13, 14, 16, 19) ODER compound_classification Abweichungen | `karmic_occurrences`, `compound_classification`    |
| `development_opportunities`      | Immer applicable=true (Gegenstück zu shadow_patterns)                            | Gleiche Daten wie `shadow_patterns`                |
| `practical_integration`          | Immer applicable=true                                                            | Alle Sections, practical_options                   |

## Capability-Hinweise für den Prompt

Pro Section liefert das Backend vor dem Prompt-Bau eine Capability-Angabe:

```json
{
  "section_id": "number_harmonies",
  "supported": true,
  "reason_code": "harmonies_detected",
  "data_hint": "Zahl 4 erscheint in life_path_primary, life_path_secondary und personality"
}
```

```json
{
  "section_id": "shadow_patterns",
  "supported": false,
  "reason_code": "no_karmic_occurrences",
  "data_hint": null
}
```

Ist eine Section nicht supported (`supported=false`), MUSS `applicable=false` gesetzt sein — DeepSeek darf sie nicht selbst erraten oder nachberechnen.

## Nicht von DeepSeek zu berechnende Daten

Diese Werte werden deterministisch berechnet und als Fakten an DeepSeek übergeben — das LLM darf sie NICHT selbst berechnen:

- Alle `display_notation`-Werte
- `root_value`, `held_master_value`, `is_master`
- `reduction_chain`
- `karmic_occurrences`
- `compound_classification`
- Pinnacle-/Challenge-Perioden
