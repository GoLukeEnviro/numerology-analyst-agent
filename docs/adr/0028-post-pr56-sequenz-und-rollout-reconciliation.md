# ADR 0028: Post-PR-56 Sequenz- und Rollout-Reconciliation

> **Status:** ACCEPTED
> **Datum:** 2026-08-06
> **Kontext:** PR #56 hat den V2/V3-Stack einschließlich Web-Welle 4 nach `main`
> gebracht, obwohl ADR 0017 (ACCEPTED, 2026-08-04) einen V2-Merge nach `main`
> solange untersagte, wie der RC2-Pfad (Strang A) offen ist. Dieser Merge ist
> Fakt und wird nicht rückwirkend umgeschrieben. Diese ADR kanonisiert den
> tatsächlichen Zustand, benennt den Widerspruch ausdrücklich und definiert
> die weitere Sequenz.

---

## 1. Ausgangslage und Widerspruch

- ADR 0017 (2026-08-04) legte fest: „Solange Strang A offen ist, kein V2-Merge
  nach `main`; Welle 4 (Web) erst nach dem RC2-Schnitt."
- PR #56 wurde dennoch gemergt und hat den V2/V3-Stack (Backend-Wellen 1–3,
  Web-Welle 4) auf `main` (HEAD `ba4c9121866a8c05b1ccfea076e0c26db9c25758`)
  gebracht.
- **Widerspruch:** Der Merge verletzt die Sequenzregel von ADR 0017. Die
  Historie wird nicht umgeschrieben; der Widerspruch wird hier ausdrücklich
  dokumentiert.

## 2. Kanonisierung des Ist-Zustands

- V2/V3 verbleibt auf `main` (kein Revert, kein Force-Push, keine
  Historie-Umschreibung).
- `product_default_method_version=v1` bleibt verbindlich.
- `rollout_stage=disabled` bleibt verbindlich.
- V2/V3 ist **nicht** Bestandteil des RC2-Default-Scopes, solange es nicht
  vollständig abgenommen ist.
- Der Guided Masterplan (Strang C) bleibt bis nach Stable `v0.3.0` gesperrt.

## 3. Neue Merge- und Release-Gates

1. OpenAPI- und TypeScript-Codegen-Drift = 0 (CI-Gate).
2. V1-Contract semantisch unverändert (V1-Unverletzlichkeit).
3. Knowledge V3 wird durch `scripts/validate_knowledge.py` validiert.
4. Alle V3-Ressourcen sind im Wheel enthalten.
5. Python-Gates (Ruff, Mypy, pip-audit, Coverage ≥95 % Engine / ≥85 % gesamt).
6. Web-Gates (Lint, Typecheck, Coverage, Build, PWA/Budget, E2E).
7. Package-Smoke in frischer Umgebung.
8. Container-Smoke und lokale Docker-Abnahme.
9. Log-Hygiene (keine Secrets, keine PII).
10. Lokaler Restore- und Rollback-Nachweis.
11. Governance-Dokumentation entspricht der Repository-Realität.
12. Externe Staging-Gates bleiben verbindlich (privater Staging-Host,
    Backup/Restore/Rollback auf dem Host, Committee-Entscheidung).

## 4. Rollout-Pfad

- Nach Stable `v0.3.0` darf V2 zunächst nur als Opt-in aktiviert werden
  (`rollout_stage=opt_in`).
- Vor `canary` sind Provider-Evaluation, Zahlenintegrität, Schema-Treue,
  Telemetrie-Datenschutz und getesteter Rollback erforderlich.
- Der Default-Wechsel (`product_default_method_version=v2`,
  `rollout_stage=default`) ist ein eigener PR, eine eigene Entscheidung und
  ein eigener Rollbackpunkt.

## 5. Rollback-Pfad

- Rollback auf den letzten grünen `main`-Merge-SHA per
  `deploy/scripts/rollback.sh` (Image-Swap per SHA-Tag, Health-Verifikation).
- Konfigurations-Restore per `deploy/scripts/restore-config.sh` (age-verschlüsselt,
  strukturell geprüft, atomarer `mv`).
- V2-Rollout-Rollback: `rollout_stage` zurück auf `disabled` und
  `product_default_method_version` zurück auf `v1`.

## 6. Verweise

- ADR 0017 — V2-Parallel-Entwicklung — Sequenzielle Anbindung (ACCEPTED;
  wird durch diese ADR nicht rückwirkend verändert, nur in der Sequenzwirkung
  überlagert)
- ADR 0016 — V2 User-Owned Masterplan Boundary (ACCEPTED)
- ADR 0018 — V2-Stack-Isolation (ACCEPTED)
- ADR 0025 — OpenAPI-Artifact-Strategie (ACCEPTED)
- `docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`
- `docs/audit/numra-post-pr56-full-verification-2026-08-06.md`
