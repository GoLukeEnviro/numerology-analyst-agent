# GOAL: Numra Full Analysis Experience — Wellen 4–5C fortsetzen

> **Goal-Typ:** Fortsetzung nach Wellen 0–3
> **Repository:** `GoLukeEnviro/numerology-analyst-agent`
> **Branch:** `feat/v2-full-analysis-welle-0` (HEAD: `039ca9c`)
> **Basis-Branch:** `main` (`9cc7e44`)
> **Erstellt:** 2026-08-05
> **Sprache:** Deutsch

---

## Ausgangszustand

### Git-Status

```
Branch: feat/v2-full-analysis-welle-0 (4 Commits vor main)
main  : 9cc7e44 docs: clarify ADR supersession and reconciliation scope

039ca9c feat: Welle 3 — Berichtserzeugung V3 (Provider, Service, Prompts, Routen)
2db4138 feat: Welle 2 — Fact Package V3, Knowledge V3, Interpretation V3
32a80a3 feat: Welle 1 — API-Grundlage für /api/v2 Stack
5a5fac7 docs: Welle 0 — Architekturentscheidungen, Capability-Matrix, Golden-E2E, Mobile-Strategie
```

### Bereits abgeschlossen (Wellen 0–3)

| Welle | Status | Inhalt                                                                                                                                                                                                                                                                                                                                                                 |
| ----- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0** | ✅     | 10 ADRs (0018–0027), Capability-Matrix, Section-Budgets, Golden-E2E, Mobile-Strategie, Execution Plan                                                                                                                                                                                                                                                                  |
| **1** | ✅     | `/api/v2/profiles/calculate`, `/api/v2/meta` (MetaResponseV2), V2-Analyse-Runtime, Dependency-Wiring-Interfaces, OpenAPI (`numra-api.json` + `v1-contract.json`), CLI `--method-version`                                                                                                                                                                               |
| **2** | ✅     | `AnalysisFactEntryV3`/`AnalysisFactPackageV3`/`ProviderFactPackageV3`, Fact-Builder (`facts_v3.py`), `KnowledgeEntryV3`/`KnowledgeBundleV3`, `de-v3.json` (16 Einträge), `loader_v3.py`, `compose_interpretation_for_profile_v4()`                                                                                                                                     |
| **3** | ✅     | `ClaimV3`, `AnalysisSectionV3` (18 feste IDs + Validator), `AnalysisReportV3`, `AnalysisReportContentV3`, V3-Prompts (`de-report-system-v3.md`, `de-report-task-v3.md`, `de-follow-up-task-v3.md`), `DeepSeekProviderV3` (finish_reason-Matrix), `AgentServiceV3` (Hash-Kanonisierung, Draft-Validierung), `/api/v2/analyses/*`-Routen (Gerüst), Wheel-Smoke erweitert |

### V2/V3-Stack — 31 neue Dateien

```
src/numerology_agent/
  models_v3.py          ← Fact- + Report-Modelle
  facts_v3.py           ← Fact-Package-Builder
  prompts_v3.py         ← V3-Prompt-Loader
  provider_v3.py        ← LlmProviderV3 Protocol
  deepseek_v3.py        ← DeepSeekProviderV3
  service_v3.py         ← AgentServiceV3
  prompt_templates/
    system/de-report-system-v3.md
    tasks/de-report-task-v3.md
    tasks/de-follow-up-task-v3.md

src/numerology_knowledge/
  models_v3.py          ← KnowledgeEntryV3, KnowledgeBundleV3
  loader_v3.py          ← load_knowledge_bundle_v3()
  data/de-v3.json       ← 16 entries (1-9, master 11/22/33, karmic 13/14/16/19)

src/numerology_interpretation/
  service_v3.py         ← compose_interpretation_for_profile_v4()

src/numerology_api/
  routes/profiles_v2.py ← POST /api/v2/profiles/calculate
  routes/meta_v2.py     ← GET /api/v2/meta (MetaResponseV2)
  routes/analyses_v2.py ← POST /api/v2/analyses/report + follow-up (Gerüst)
  analysis_runtime_v2.py ← canonical_analysis_profile_v2()
  idempotency.py        ← IdempotencyStoreV3 Protocol
  dependencies_v3.py    ← V3AnalysisSettings Protocol

docs/
  adr/0018–0027         ← 10 Architekturentscheidungen
  methods/              ← capability-matrix-v3, section-budgets-v3,
                          golden-e2e-lukas-springer-v3, mobile-strategy-9-tabs
  plans/                ← numra-full-analysis-execution-plan.md (Quelle der Wahrheit)
```

---

## Verbindliche Constraints

### SEQUENCING_GATE (ADR 0017)

```
Solange der RC2-Releasepfad gemäß ADR 0017 offen ist,
dürfen V2/V3-Wellen auf einem isolierten Branch entwickelt werden,
aber nicht nach main gemergt werden.

Welle 4 (Web) beginnt erst nach dem RC2-Schnitt.

Eine abweichende Reihenfolge benötigt zuerst eine neue ADR,
die ADR 0017 ausdrücklich ersetzt oder ergänzt.
```

### Architekturregeln

1. **Keine geteilten versionierten HTTP-/Report-Modelle** zwischen `/api/v1` und `/api/v2`. Stabile Domainprimitiven (`PersonInput`, `MethodPolicy`, `KarmicOccurrence`, `ProblemDetails` etc.) dürfen wiederverwendet werden.
2. **V1-Stack in allen dokumentierten Erfolgsfällen rückwärtskompatibel.** Einzige bewusste Änderung: V1-Guard (`version != "v1"` → 422) — bereits implementiert.
3. **Determinismus vor LLM.** Alle Berechnungen funktionieren ohne Sprachmodell. LLM nur für Erklärungen.
4. **14 nicht verhandelbare Prinzipien** aus dem Execution Plan §"Nicht verhandelbare Prinzipien".

### Golden-Werte (Lukas Springer)

```
life_path_primary  = 40/4 (root=4)
life_path_secondary = 22/4 (root=4, held_master_value=22, is_master=true)
personality        = 44/8 (KEINE Meisterzahl, is_master=false)
expression         = 62/8
birthday           = 18/9
attitude           = 25/7
soul_urge          = 18/9
maturity           = 12/3
personal_year_2026 = 17/8
pinnacles          = 16/7, 15/6, 13/4, 13/4
challenges         = 2, 3, 1, 1
```

---

## Noch zu implementieren

### Welle 4 — Web-Migration (BEGINNT ERST NACH RC2-SCHNITT gemäß ADR 0017)

**Ziel:** 9 Reiter, Berichtshistorie, Offline, Print/PDF.

**9 Schritte:**

| #   | Schritt                     | Datei                                                                                                     | Typ        |
| --- | --------------------------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| 1   | Präsentationsmodell-Adapter | `apps/web/src/features/profile/presentation.ts`                                                           | NEU        |
| 2   | API-Client V2-Endpunkte     | `apps/web/src/api/client.ts`, `apps/web/src/api/schema.d.ts`                                              | ÄNDERN     |
| 3   | Section-Mapping (18→9)      | `apps/web/src/features/report/sectionMapping.ts`                                                          | NEU        |
| 4   | ResultsTabs (WAI-ARIA)      | `apps/web/src/features/report/ResultsTabs.tsx`                                                            | NEU        |
| 5   | ReportExperience umbauen    | `apps/web/src/features/report/ReportExperience.tsx`                                                       | ÄNDERN     |
| 6   | Druckansicht + PDF          | `apps/web/src/features/report/PrintView.tsx` (NEU), `apps/web/src/features/export/profilePdf.ts` (ÄNDERN) | NEU/ÄNDERN |
| 7   | Storage Schema v4           | `apps/web/src/storage/database.ts`, `apps/web/src/storage/repository.ts`                                  | ÄNDERN     |
| 8   | Offline-Status              | `apps/web/src/pwa/offlineState.ts`                                                                        | NEU        |
| 9   | AnalysisWizard v1/v2        | `apps/web/src/features/analysis/AnalysisWizard.tsx`                                                       | ÄNDERN     |

**UI-Reiter (18→9-Mapping):**

| Reiter                   | Sections                                                                |
| ------------------------ | ----------------------------------------------------------------------- |
| Überblick                | `executive_overview`                                                    |
| Lebensweg                | `life_path_and_purpose`, `birthday_and_attitude`                        |
| Inneres Profil           | `inner_motivation`, `maturity_and_development`                          |
| Ausdruck und Wirkung     | `expression_and_external_persona`                                       |
| Muster und Spannungen    | `number_harmonies`, `number_tensions`, `repetitions_and_missing_values` |
| Lebensphasen             | `life_phases`, `personal_cycles`, `pinnacles`, `challenges`             |
| Schatten und Entwicklung | `shadow_patterns`, `development_opportunities`                          |
| Integration              | `practical_integration`, `final_synthesis`                              |
| Rechenweg                | `method_and_calculation_notes`                                          |

**Storage Schema v4 (Dexie):**

- `reports`-Tabelle: `reportId` (UUID-PK), `profileId`, `reportContentHash`, `generationContextHash`, `methodVersion`, `reportSchemaVersion`, `calculationHash`, `createdAt`, `payload`
- Mehrere Berichte pro Profil (keine Exception mehr)
- `threads`/`notes` erhalten zusätzlich `reportId`

**Offline-Zustände:**

```
PROFILE_CALCULATION_REQUIRES_NETWORK
REPORT_GENERATION_REQUIRES_NETWORK
SAVED_PROFILE_AVAILABLE_OFFLINE
SAVED_REPORT_AVAILABLE_OFFLINE
```

**Verifikation Welle 4:**

```bash
pnpm web:typecheck
pnpm web:test
pnpm web:e2e    # Playwright + @axe-core/playwright
```

---

### Welle 5A — Provider-Evaluation (kein Default-Wechsel)

- `scripts/eval_deepseek_config.py` (NEU)
- 5 Golden-Profile × 3 Läufe × 2 Varianten (Thinking vs. Non-Thinking)
- Metriken: Zahlenkorrektheit, Kapitelabdeckung, Schema-Treue, Varianz, Trunkierung, Kosten, Latenz
- `max_output_tokens` kalibrieren (≤ `NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS` = 32768)
- `MAX_CANONICAL_REPORT_BYTES` festlegen
- **Kein Default-Wechsel nach Evaluation**

### Welle 5B — Opt-in-Beta

- `rollout_stage = "opt_in"`
- V2 im Wizard manuell auswählbar, V1 bleibt Default
- Telemetrie nur Metriken, keine Inhalte

### Welle 5C — Default-Wechsel

Nur bei ALLEN grünen Gates:

```
reference_integrity = 100%
Lukas 40/4 = PASS, Lukas 22/4 held_master_value=22 = PASS
unknown_references = 0, truncated_reports = 0, PII_leakage = 0
V1_contract_snapshot = PASS
schema_success_rate >= Grenzwert
provider_error_rate <= Budget
P95_latency <= Budget
cost_per_report <= Budget
rollback_test = PASS, A11y = PASS
Export/Import = PASS, Offline-Reopen = PASS
```

---

## Verifikation (nach jeder Welle)

```bash
# Backend
uv run pytest --cov=src/numerology_engine --cov-fail-under=95
uv run pytest --cov=src --cov-fail-under=85
uv run python scripts/export_openapi.py --check

# Web (ab Welle 4)
pnpm web:typecheck
pnpm web:test
pnpm web:e2e

# Build
uv build
```

---

## Schlüsseldokumente

| Dokument           | Pfad                                               | Rolle                                            |
| ------------------ | -------------------------------------------------- | ------------------------------------------------ |
| **Execution Plan** | `docs/plans/numra-full-analysis-execution-plan.md` | Operative Quelle der Wahrheit                    |
| Architekturquelle  | `docs/plans/numra-full-analysis-v2-v3.md`          | Kanonische Architekturdefinition                 |
| Sequenz-Governance | `docs/adr/0017-v2-parallel-anbindung-sequenz.md`   | RC2-Sequenz, Merge-Regeln                        |
| Stack-Isolation    | `docs/adr/0018-v2-stack-isolation.md`              | Geteilte-Modelle-Regel                           |
| Idempotenz+Krypto  | `docs/adr/0023-api-idempotency-crypto.md`          | Vollständiger Kryptovertrag                      |
| Hash-Kanonisierung | `docs/adr/0027-hash-canonization.md`               | `generation_context_hash`, `report_content_hash` |
| Golden-E2E         | `docs/methods/golden-e2e-lukas-springer-v3.md`     | Abnahmekriterium                                 |
| Mobile-Strategie   | `docs/methods/mobile-strategy-9-tabs.md`           | Scrollbare Tab-Leiste                            |
| Capability-Matrix  | `docs/methods/capability-matrix-v3.md`             | 18 Sections mit Datenabhängigkeiten              |
| Section-Budgets    | `docs/methods/section-budgets-v3.md`               | Zeichen- und Anzahl-Limits                       |

---

## Rollback-Strategie

- `/api/v2/analyses/*`-Router aus `src/numerology_api/app.py` deaktivieren → V1 unberührt
- `rollout_stage = "disabled"` in `MetaResponseV2` → Web-App zeigt kein V2
- `product_default_method_version = "v1"` → Wizard-Default bleibt V1
- Branch `feat/v2-full-analysis-welle-0` löschen → alle V2-Änderungen entfernt

---

## Abschlussbericht (nach jeder Welle liefern)

- Geänderte Dateien
- Erfüllte Gates
- Fehlgeschlagene Gates
- Migrationsauswirkungen
- OpenAPI-Auswirkungen
- Privacy-Auswirkungen
- Rollback-Punkt
- Testresultate
- Commit-SHA
- Nächster zulässiger Schritt
