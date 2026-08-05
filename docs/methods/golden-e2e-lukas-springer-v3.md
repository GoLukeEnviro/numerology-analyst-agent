# Golden-End-to-End-Testfall: Lukas Springer — V2/V3-Gesamtgraph

> **Abnahmekriterium für Wellen 1–5C**
> Stand: 2026-08-05

## Referenzprofil

```
Name:              Lukas Springer
Geburtsdatum:      18.07.1986
Methodenversion:   pythagorean-v2
As-of-Date:        2026-07-26 (Testdatum)
```

## Erwartete Berechnungsergebnisse

| Kernzahl | display_notation | root_value | held_master_value | is_master |
|---|---|---|---|---|
| Life Path Primary | `40/4` | 4 | — | false |
| Life Path Secondary | `22/4` | 4 | 22 | true |
| Geburtstag | `18/9` | 9 | — | false |
| Einstellung | `25/7` | 7 | — | false |
| Ausdruck | `62/8` | 8 | — | false |
| Seelenstreben | `18/9` | 9 | — | false |
| Persönlichkeit | `44/8` | 8 | — | false |
| Reife | `12/3` | 3 | — | false |
| Persönliches Jahr 2026 | `17/8` | 8 | — | false |
| Pinnacle 1 | `16/7` | 7 | — | false |
| Pinnacle 2 | `15/6` | 6 | — | false |
| Pinnacle 3 | `13/4` | 4 | — | false |
| Pinnacle 4 | `13/4` | 4 | — | false |
| Challenge 1 | 2 | — | — | — |
| Challenge 2 | 3 | — | — | — |
| Challenge 3 | 1 | — | — | — |
| Challenge 4 | 1 | — | — | — |

## E2E-Test-Szenario

### 1. Profilberechnung (Welle 1)

```python
POST /api/v2/profiles/calculate
{
  "person": {"core_name": "Lukas Springer", "birth_date": "1986-07-18"},
  "policy": {"version": "v2", "method_system": "pythagorean", "y_mode": "phonetic",
             "umlaut_policy": "de-direct-v1", "master_numbers": [11, 22, 33]},
  "as_of_date": "2026-07-26"
}
→ 200 ProfileCalculationResultV4
→ life_path_primary.display_notation == "40/4"
→ life_path_secondary.held_master_value == 22
→ personality.display_notation == "44/8"
→ personality.is_master == false
```

### 2. Berichtserzeugung (Welle 3)

```python
POST /api/v2/analyses/report
{
  "request_id": "<stabile-test-uuid>",
  "consent": true,
  "device_id": "test-device-golden-e2e",
  "profile": <ProfileCalculationResultV4 aus Schritt 1>
}
→ 200 AnalysisReportV3
→ 18 Sections mit korrekten section_ids
→ Keine Section mit unbekannter/doppelter ID
→ life_path_primary 40/4 im provider_fact_package
→ life_path_secondary 22/4 mit held_master_value=22 im provider_fact_package
→ personality als compound/non-master klassifiziert
```

### 3. Idempotenz (Welle 3)

```
Gleicher request_id → gleicher report_id, gleicher report_content_hash
Anderer calculation_hash → 409 IDEMPOTENCY_KEY_CONFLICT
```

### 4. Follow-up (Welle 3)

```python
POST /api/v2/analyses/follow-up
{
  "request_id": "<stabile-test-uuid-2>",
  "consent": true,
  "device_id": "test-device-golden-e2e",
  "profile": <ProfileCalculationResultV4>,
  "report": <AnalysisReportV3 aus Schritt 2>,
  "question": "Was bedeutet die 22/4 als sekundärer Lebensweg?"
}
→ 200 AnalysisFollowUpV3
```

## Invarianten (niemals verletzen)

1. `life_path_primary.display_notation == "40/4"` — primärer Lebensweg nie durch sekundären überschrieben
2. `life_path_secondary.held_master_value == 22` — Meisterzahl nie auf root abgeflacht
3. `personality.is_master == false` — 44/8 ist keine klassische Meisterzahl
4. `personality.compound_classification != "master_number"` — korrekte compound-Klassifikation
5. `report.sections[0].section_id == "executive_overview"` — Reihenfolge eingehalten
6. `report.sections[-1].section_id == "method_and_calculation_notes"` — letzte Section korrekt
