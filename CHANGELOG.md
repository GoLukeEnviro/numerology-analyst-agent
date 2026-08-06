# Changelog

> **Hinweis:** Dieser Changelog ist ein schlanker Index. Die ausführlichen
> Release Notes liegen in [`docs/releases/`](docs/releases/) und sind die
> **Single Source of Truth** für Release-Beschreibungen. Dieser Changelog
> erzeugt keine zweite, widersprüchliche Beschreibung.

## Unreleased — post-PR-56 main (0.3.0rc1, Richtung v0.3.0-rc.2)

Seit PR #56 liegt der V2/V3-Stack (Backend-Wellen 1–3, Web-Welle 4) auf `main`
(`ba4c9121866a8c05b1ccfea076e0c26db9c25758`), kontrolliert gemäß ADR 0028
(`product_default_method_version=v1`, `rollout_stage=disabled`). Die lokale
Recovery-Verifikation hat OpenAPI-/Web-Type-Drift behoben, Knowledge V3
validiert, V2-Analyse-Routen funktional gemacht (fail-closed) und die
Backend-Audit-Fixes B-6/B-7/B-8 sowie den CRLF-Env-Fix (B-16) eingebracht.

- **Details:** `docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`,
  `docs/audit/current-state-numra-post-pr56-2026-08-06.md`
- **Governance:** ADR 0028 (post-PR-56 Sequenz- und Rollout-Reconciliation)

## v0.3.0-rc.1 — Release Candidate 1 (2026-07-28, Closure 2026-07-29)

Erster Release Candidate der kumulativen Normalisierungsrunde (ADR 0015).
Enthält die vollständige Integration Closure (Backend, Frontend, API,
Container), das V2-Wissensmodell, den kanonischen pythagoreischen
Berechnungsvertrag V2, die produktive Prompt-/Knowledge-/Composer-Verdrahtung,
die Behebung des Abort-/Resubmit-Race im Web-Client sowie den ausführbaren
LLM-Staging-Vertrag.

- **Tag:** `v0.3.0-rc.1` → Commit `21ba56ed0d918cea7c60090bcc50937adc16269a`
- **Ausführliche Release Notes:** [`docs/releases/v0.3.0-rc.1.md`](docs/releases/v0.3.0-rc.1.md)
- **Migration:** [`docs/releases/migration-to-v0.3.0-rc.1.md`](docs/releases/migration-to-v0.3.0-rc.1.md)

## v0.1.5 — Deterministic Cycles (Entwicklungsmeilenstein)

Persönliche Jahre, Monate und Tage sowie vier Pinnacles und Challenges;
`profile-calculation-result-v2`. Kein veröffentlichter Tag.

- **Details:** [`docs/releases/v0.1.5.md`](docs/releases/v0.1.5.md)

## v0.1.4 — Complete Core Profile (Entwicklungsmeilenstein)

Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-, Persönlichkeits- und
Reifezahl, Namenssegmente, aktiver Name und Y-Varianten;
`profile-calculation-result-v1`. Kein veröffentlichter Tag.

- **Details:** [`docs/releases/v0.1.4.md`](docs/releases/v0.1.4.md)

## v0.1.3 — Contract Integrity (2026-07-26)

Veröffentlichtes Release: vollständiger Calculation-Hash-Envelope, explizite
Schema-Version, verpflichtendes `--as-of-date`, kanonische Serialisierung,
versionierte JSON-Schemas, Lockfile- und Schema-Drift-Gates.

- **Tag:** `v0.1.3` → Commit `9c50f4d`
- **Ausführliche Release Notes:** [`docs/releases/v0.1.3.md`](docs/releases/v0.1.3.md)
