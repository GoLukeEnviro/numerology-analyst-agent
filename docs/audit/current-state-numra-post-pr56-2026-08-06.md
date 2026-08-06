# Numra — aktueller Quellstand (post-PR-56, 2026-08-06)

> **Stand:** 2026-08-06
> **Main-HEAD:** `ba4c9121866a8c05b1ccfea076e0c26db9c25758`
> **Paketversion:** `0.3.0rc1`
> **Unveränderlicher Tag:** `v0.3.0-rc.1` → `21ba56ed0d918cea7c60090bcc50937adc16269a`
> **Zweck:** Frische Repository-Wahrheit nach Merge von PR #56 (V2/V3-Stack
> inkl. Web-Welle 4) und nach der lokalen Recovery-Verifikation
> (`docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`).
> Ersetzt **nicht** die historische Bestandsaufnahme
> `docs/audit/current-state-numra-post-rc1-2026-08-02.md` — diese bleibt als
> historisches Artefakt lesbar.

---

## 1. Governance-Reconciliation (ADR 0028)

PR #56 hat den V2/V3-Stack nach `main` gebracht, obwohl ADR 0017 einen
V2-Merge solange untersagte, wie der RC2-Pfad offen ist. Der Widerspruch wird
nicht durch Umschreiben der Historie verborgen, sondern durch
**ADR 0028** (`docs/adr/0028-post-pr56-sequenz-und-rollout-reconciliation.md`)
kanonisiert:

- V2/V3 verbleibt auf `main` (kein Revert, kein Force-Push).
- `product_default_method_version=v1` bleibt verbindlich.
- `rollout_stage=disabled` bleibt verbindlich.
- V2/V3 ist nicht Bestandteil des RC2-Default-Scopes.
- Guided Masterplan bleibt bis nach Stable `v0.3.0` gesperrt.
- Neue Merge-/Release-Gates und ein klarer Rollbackpfad sind definiert.

## 2. Was abgeschlossen ist

| Thema | Evidenz |
|-------|---------|
| RC1 Integration Closure | Tag `v0.3.0-rc.1`, Release Notes |
| V2/V3-Stack auf `main` (PR #56) | Backend-Wellen 1–3, Web-Welle 4 |
| OpenAPI-Drift behoben | `openapi/numra-api.json` regeneriert; alle 4 V2-Pfade vorhanden; `--check` grün |
| V1-Contract unverändert | `openapi/contracts/v1-contract.json` semantisch identisch (kein Diff) |
| Web-Type-Drift behoben | `apps/web/src/api/schema.d.ts` regeneriert; `git diff --exit-code` grün |
| Knowledge V3-Validierung | `scripts/validate_knowledge.py` validiert de-v1/v2/v3 |
| V3-Ressourcen im Wheel | `de-v3.json`, `de-report-system-v3.md`, `de-report-task-v3.md`, `de-follow-up-task-v3.md` |
| V2-Analyse-Routen funktional | `analyses_v2.py` vollständig implementiert (fail-closed 503 bei LLM-off, 422 bei Profil-Integrität, 429 Rate-Limit) |
| Backend-Audit-Fixes | B-6 (Fact-Package-Pfade), B-7 (Interpretation-V3), B-8 (context_signature) |
| Python-Gates | Ruff, Mypy, pip-audit, Coverage (Engine 98,52 %, gesamt 89,57 %) grün |
| Web-Gates | Lint, Typecheck, Coverage (73 Tests), Build, Check-Build, E2E grün |
| Package-Smoke | Wheel in frischer Venv; CLI V1/V2; 8 Imports OK |
| Lokale Docker-Abnahme | Stack healthy; V1/V2 Golden-Werte; Fail-closed; Restart/Redis-Resilienz; Log-Hygiene |
| LLM-Staging fail-closed | Ohne Runtime-Marker startet der API-Container nicht (RuntimeError) |
| Rollback-Rehearsal | `800082aa… → ba4c9121… → 800082aa…`, Health PASS |
| Restore-Rehearsal | age-encrypt/decrypt, strukturelle Prüfung, Byte-Identität |

## 3. Was **nicht** bewiesen ist (reale Betriebsleistung)

| Thema | Status |
|-------|--------|
| Privates Staging auf bestätigtem Numra-Host | **BLOCKED_BY_APPROVED_HOST_MISSING** |
| Echter Provider-/LLM-Smoke (Legal/Transfer/Secret) | **BLOCKED** (Legal/Transfer-Approval + Runtime-Marker fehlen) |
| Provider-Evaluation Welle 5A | **BLOCKED** (gleiche externe Voraussetzungen) |
| Committee Release Review (post-Fixes) | **PENDING** (erneute Durchführung nach Merge) |
| Closed Beta | **NOT_STARTED** |
| Stable `v0.3.0` | **NOT_STARTED** |
| Öffentlicher Launch | **NO_GO** (`docs/operations/launch-checklist.md`) |

## 4. Versions- und Release-Pfad

```text
v0.3.0-rc.1 (immutable) → post-PR-56 main (0.3.0rc1, V2/V3 kontrolliert)
  → PR-CI grün → Merge → Main-CI grün
  → private staging + restore + rollback evidence (extern)
  → committee GO|GO_WITH_CONDITIONS
  → v0.3.0-rc.2 (prerelease)
  → closed beta (P0/P1 = 0)
  → v0.3.0 stable
  → public deploy GO|NO_GO (separat)
  → V2 opt-in (rollout_stage=opt_in) → canary → default (eigener PR)
```

## 5. V2/V3-Kontrollzustand

```text
PRODUCT_DEFAULT_METHOD_VERSION=v1
V2_STACK_PRESENT=YES
V2_DEFAULT=NO
ROLLOUT_STAGE=disabled
PUBLIC_DEPLOYMENT=NO
```

## 6. Dependency-Hinweis

- Python `pip-audit`: keine bekannten CVEs (Messung 2026-08-06).
- Node: `react-router` GHSA-qwww-vcr4-c8h2 (HIGH) — in CI mit
  `--ignore GHSA-qwww-vcr4-c8h2` geführt; Patch-Pfad ≥8.3.0 ist
  Major-Risiko und gehört in den RC2 Security-Stream.

## 7. Historische Dokumente (nicht als Live-Status lesen)

| Datei | Hinweis |
|-------|---------|
| `docs/audit/current-state-numra-post-rc1-2026-08-02.md` | Stand vor PR #56 — **historisch** |
| `docs/audit/current-state-numra-rc.md` | RC-Vorbereitung 28.07.2026 — **historisch** |
| `docs/audit/phase-0-gate-2026-08-02.md` / `phase-1-gate-2026-08-02.md` | Messung auf RC1-Tag — **historisch** |

## 8. Nächster einzelner Schritt

1. Vollständiger lokaler Gate-Lauf (Phase 12) mit Audit-Bericht
   `docs/audit/numra-post-pr56-full-verification-2026-08-06.md`.
2. Commit- und PR-Strategie (Phase 13), PR-CI grün (Phase 14), Merge.
3. Danach externe Gates: privates Staging, Committee-Review, RC2.
