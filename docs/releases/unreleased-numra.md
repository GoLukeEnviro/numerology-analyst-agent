# Numra — unreleased / post-RC1 Arbeitspfad

> **Stand:** 2026-08-02  
> **Aktueller `main`:** `5976ae2299059451461f634cb89f525151fda8b2`  
> **Paketversion auf main:** `0.3.0rc1`  
> **Letzter immutable Tag:** `v0.3.0-rc.1` → `21ba56ed0d918cea7c60090bcc50937adc16269a`

## Was bereits getaggt ist

- **`v0.3.0-rc.1`** — Integration Closure (siehe `docs/releases/v0.3.0-rc.1.md`).
  Tag wird **nicht** bewegt.

## Was seit RC1 auf main liegt (noch kein neuer Tag)

- PR **#34** — Ship-Hygiene: Issue #32 Determinismus-Fix, API-/Domain-Modularisierung,
  Frontend-Coverage-CI-Gate, README/Release-Truth.
- PR **#35** — Konsolidierung von Audit-, Governance- und OpenAPI-Artefakten.

Diese Commits gehören zur **RC2-Vorbereitung**, nicht zu einer stillen
RC1-Tag-Verschiebung.

## Nächste geplante Code-Releases

1. **`v0.3.0-rc.2`** — erst nach frischem Gate, privatem Staging, Restore,
   Rollback und Committee `GO` / `GO_WITH_CONDITIONS`.
2. **`v0.3.0`** (stable) — erst nach Closed Beta mit P0/P1 = 0.

## Explizit unreleased / blockiert

| Thema | Status |
|-------|--------|
| Privates Staging (bestätigter Host) | NOT_EXECUTED |
| Backup create + structural validate + restore + re-smoke | NOT_EXECUTED |
| Rollback-Rehearsal | NOT_EXECUTED |
| Committee Review | COMPLETE (`docs/committee/rc2-*.md`); Entscheidung NO_GO; Betriebsabnahme BLOCKED_BY_STAGING |
| Closed Beta | NOT_STARTED |
| Öffentlicher Launch | NO_GO |
| Research Preview (historisch „0.4.0“) | NOT_STARTED |
| V2 Guided Masterplan Implementierung | DEFERRED (ADR 0016) |

## Hinweis zur alten „unreleased“-Erzählung

Frühere Fassungen dieses Dokuments beschrieben den Stand nach PR #10 mit
formal `0.1.5` und ohne RC1-Tag. Das ist durch ADR 0015 und den Tag
`v0.3.0-rc.1` **ersetzt**. Nicht als aktuellen main-Status zitieren.
