# Numra — unreleased / post-PR-56 Arbeitspfad

> **Stand:** 2026-08-06
> **Aktueller `main`:** `ba4c9121866a8c05b1ccfea076e0c26db9c25758`
> **Paketversion auf main:** `0.3.0rc1`
> **Letzter immutable Tag:** `v0.3.0-rc.1` → `21ba56ed0d918cea7c60090bcc50937adc16269a`

## Was bereits getaggt ist

- **`v0.3.0-rc.1`** — Integration Closure (siehe `docs/releases/v0.3.0-rc.1.md`).
  Tag wird **nicht** bewegt.

## Was seit RC1 auf main liegt (noch kein neuer Tag)

- PR **#34** — Ship-Hygiene: Issue #32 Determinismus-Fix, API-/Domain-Modularisierung,
  Frontend-Coverage-CI-Gate, README/Release-Truth.
- PR **#35** — Konsolidierung von Audit-, Governance- und OpenAPI-Artefakten.
- PR **#55** — Restore-Skript (OPS-001), Deploy-by-Digest (OPS-002), Rollback-Rehearsal lokal,
  Committee-Status-Korrektur, CQ-001.
- PR **#56** — V2/V3-Stack (Backend-Wellen 1–3, Web-Welle 4) auf `main`
  (`ba4c9121…`), kontrolliert gemäß ADR 0028 (`product_default_method_version=v1`,
  `rollout_stage=disabled`).

Diese Commits gehören zur **RC2-Vorbereitung**, nicht zu einer stillen
RC1-Tag-Verschiebung.

## Lokale Recovery-Verifikation (2026-08-06)

- OpenAPI-Drift behoben (alle 4 V2-Pfade; V1-Contract unverändert).
- Web-Type-Drift behoben (`apps/web/src/api/schema.d.ts` regeneriert).
- Knowledge V3-Validierung aktiv (`de-v1/v2/v3`).
- V2-Analyse-Routen funktional (fail-closed 503/422/429).
- Backend-Audit-Fixes B-6/B-7/B-8; CRLF-Env-Fix B-16.
- Python-Gates grün (Engine 98,52 %, gesamt 89,57 %); Web-Gates grün (73 Tests);
  lokale Docker-Abnahme grün; Rollback-/Restore-Rehearsal grün.
- Details: `docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`,
  `docs/audit/current-state-numra-post-pr56-2026-08-06.md`.

## Nächste geplante Code-Releases

1. **`v0.3.0-rc.2`** — erst nach frischem Gate, privatem Staging, Restore,
   Rollback und Committee `GO` / `GO_WITH_CONDITIONS`.
2. **`v0.3.0`** (stable) — erst nach Closed Beta mit P0/P1 = 0.

## Explizit unreleased / blockiert

| Thema | Status |
|-------|--------|
| Privates Staging (bestätigter Host) | **BLOCKED_BY_APPROVED_HOST_MISSING** |
| Backup create + structural validate + restore + re-smoke | **PASS** (lokal, `docs/operations/rollback-rehearsal-local-2026-08-04.md`) |
| Rollback-Rehearsal | **PASS** (lokal, `docs/operations/rollback-rehearsal-local-2026-08-04.md`) |
| Host-Staging Restore + Rollback | **NOT_EXECUTED** |
| Provider-Evaluation Welle 5A | **BLOCKED** (Legal/Transfer-Approval + Runtime-Marker fehlen) |
| Committee Review (post-Fixes) | **PENDING** (erneute Durchführung nach Merge) |
| Closed Beta | NOT_STARTED |
| Öffentlicher Launch | NO_GO |
| Research Preview (historisch „0.4.0“) | NOT_STARTED |
| V2 Guided Masterplan Implementierung | DEFERRED (ADR 0016, ADR 0028) |

## Hinweis zur alten „unreleased“-Erzählung

Frühere Fassungen dieses Dokuments beschrieben den Stand nach PR #10 mit
formal `0.1.5` und ohne RC1-Tag. Das ist durch ADR 0015 und den Tag
`v0.3.0-rc.1` **ersetzt**. Nicht als aktuellen main-Status zitieren.
