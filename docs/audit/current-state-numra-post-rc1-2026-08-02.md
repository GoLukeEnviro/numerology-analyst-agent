# Numra — aktueller Quellstand (post-RC1, 2026-08-04)

> **Stand:** 2026-08-04  
> **Code-Baseline-SHA (Gates):** `a3f168ef99823fa2fd1c3f3b6536ea7523def451`  
> **Docs-Merge post-Reconciliation:** `7f9795c807f06c721a8c67c32823e8897de7f359` (`origin/main` nach PR #36)  
> **Paketversion:** `0.3.0rc1`  
> **Unveränderlicher Tag:** `v0.3.0-rc.1` → `21ba56ed0d918cea7c60090bcc50937adc16269a`  
> **Zweck:** Frische Repository-Wahrheit nach Merge von PR #34 und #35.  
> Ersetzt **nicht** die historische Bestandsaufnahme  
> `docs/audit/current-state-numra-rc.md` (RC-Vorbereitung 2026-07-28) — diese
> bleibt als historisches Artefakt lesbar und ist unten als historisch markiert.

---

## 1. Was abgeschlossen ist

| Thema | Evidenz |
|-------|---------|
| RC1 Integration Closure | Tag `v0.3.0-rc.1`, Release Notes |
| Issue #32 Determinismus-Flake | PR #34 (geschlossen) |
| API-Modularisierung | PR #34 |
| Domain-Modularisierung | PR #34 |
| Frontend-Coverage-Gate in CI | PR #34, CI-Job „Unit tests with coverage“ + check-build |
| README / Release-Truth | PR #34 |
| Audit-/OpenAPI-Konsolidierung | PR #35 → Merge-SHA = aktueller main |
| Frische Quality Gates auf main | 2026-08-02: ruff, mypy, pytest, Determinismus-Matrix (6 Seeds), web lint/typecheck/coverage/build/e2e, container health + profile smoke, Remote CI + CodeQL **PASS** |

## 2. Was **nicht** bewiesen ist (reale Betriebsleistung)

| Thema | Status |
|-------|--------|
| Privates Staging auf bestätigtem Numra-Host | **NOT_EXECUTED** |
| Echter Provider-/LLM-Smoke (Legal/Transfer/Secret) | **BLOCKED** / optional |
| Verschlüsseltes Konfig-Backup + Restore | **PASS (lokal)** (`docs/operations/rollback-rehearsal-local-2026-08-04.md`) |
| Rollback-Rehearsal | **PASS (lokal)** (`docs/operations/rollback-rehearsal-local-2026-08-04.md`) |
| Committee Release Review | **COMPLETE** (`docs/committee/rc2-*.md`), Entscheidung **NO_GO**, Betriebsabnahme **BLOCKED_BY_STAGING** |
| Closed Beta | **NOT_STARTED** |
| Stable `v0.3.0` | **NOT_STARTED** |
| Öffentlicher Launch | **NO_GO** (`docs/operations/launch-checklist.md`) |

## 3. Versions- und Release-Pfad

```text
v0.3.0-rc.1 (immutable) → post-RC1 main (0.3.0rc1)
  → private staging + restore + rollback evidence
  → committee GO|GO_WITH_CONDITIONS
  → v0.3.0-rc.2 (prerelease)
  → closed beta (P0/P1 = 0)
  → v0.3.0 stable
  → public deploy GO|NO_GO (separat)
  → ADR post-0.3 sequencing (V2 nur danach)
```

**V2 Guided Masterplan** (`docs/product/numra-v2-guided-masterplan.md`, ADR 0016)
ist eine Produktspezifikation, **keine** laufende Implementierung.

**Paralleler V2-Strang** (`pythagorean-v2` + Full Analysis V2/V3) gemäß ADR 0017
darf parallel entwickelt werden, jedoch ausschließlich unter `/api/v2`, hinter
Feature Flag, V1 unverändert, kein Default-Wechsel, und nicht zwingend Bestandteil
des RC2-Tags. Kein V2-Merge nach `main` solange Strang A offen ist.

## 4. Dependency-Hinweis

- Python `pip-audit`: keine bekannten CVEs (Messung 2026-08-02 auf main).
- Node: `react-router` GHSA-qwww-vcr4-c8h2 (HIGH) — in CI mit
  `--ignore GHSA-qwww-vcr4-c8h2` geführt; Patch-Pfad ≥8.3.0 ist
  Major-Risiko und gehört in den RC2 Security-Stream, nicht in stille
  Major-Upgrades ohne E2E.

## 5. Historische Dokumente (nicht als Live-Status lesen)

| Datei | Hinweis |
|-------|---------|
| `docs/audit/current-state-numra-rc.md` | RC-Vorbereitung 28.07.2026; SHA `8faba1b…` — **historisch** |
| `docs/audit/phase-0-gate-2026-08-02.md` / `phase-1-gate-2026-08-02.md` | Messung auf RC1-Tag / älterem Mess-HEAD — **historisch** |
| `docs/audit/numra-post-implementation-verification-2026-08-02.md` | Lokaler Tip vor Merge #34; NO-GO war damalige Messung — **historisch** |
| `docs/audit/gap-analysis.md` (Abschnitte V1.2) | Foundation-Stand nach v0.1.3 — **historische Baseline** |

## 6. Nächster einzelner Schritt

**Private Staging-Abnahme** auf einem vom Betreiber bestätigten Numra-Host
(kein ungeprüftes Shared-Hermes/Trading-Hosting) mit `NUMRA_LLM_ENABLED=false`,
anschließend Backup/Restore und Rollback-Rehearsal mit dokumentierten SHAs/Digests.
