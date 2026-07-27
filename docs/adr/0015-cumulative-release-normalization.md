# ADR 0015 — Kumulative Release-Normalisierung auf 0.3.0rc1

> **Status:** Akzeptiert (28. Juli 2026)
> **Kontext:** Numra-Integration auf `main` (`8faba1b`) vereint die ADR-0006-Folgen `0.1.4`, `0.1.5`, `0.2.0` und `0.3.0` in einem Quellstand, der formal `0.1.5` trägt. Diese Versionseinheit ist mehrdeutig und blockiert einen eindeutigen nächsten Tag.
> **Betrifft:** Release-Planung, Versionierung, SemVer, Tag-Strategie

---

## Entscheidung

Der kumulierte Quellstand auf `main` wird normativ als Release-Kandidat
**`0.3.0rc1`** (SemVer-Pre-Release) klassifiziert. Diese ADR dokumentiert
ausschließlich die Zielversion; sie verändert keine Code-Version, keinen
Vertrag und keine Konfiguration. Der tatsächliche Version-Bump erfolgt
getrennt in PR E (`release/v0.3.0-rc1`).

Schreibweise:

- Python-Version (`pyproject.toml`): `0.3.0rc1` (PEP 440).
- Web-Version (`apps/web/package.json`): `0.3.0-rc.1` (npm/SemVer).
- Tag: `v0.3.0-rc.1`.

## Begründung

ADR 0006 legt eine strenge sequenzielle Releasefolge fest
(`0.1.4 → 0.1.5 → 0.2.0 → 0.3.0`). Diese Folge wurde operativ nicht
eingehalten: PR #10 (Numra-PWA), PR #11 (Post-Merge-Hardening) und PR #12
(CodeQL-Baseline) haben Funktionsbereiche aller vier Versionen gemeinsam
integriert, ohne dass Zwischentags erzeugt wurden.

Eine nachträgliche Erzeugung der Tags `v0.1.4`, `v0.1.5`, `v0.2.0` wäre
denkbar, würde aber:

1. Tags auf Commits setzen, die nie als Release geprüft wurden (kein
   Staging-Drill, keine 17-Punkte-Abnahme, kein Backup/Restore-Nachweis),
2. die Historie verfälschen, da diese Versionen nie unabhängig existierten,
3. den ADR-0006-Geist verletzen (jeder Release = eigenständig geprüft).

Stattdessen wird der gesamte kumulierte Stand als ein Release-Kandidat
`0.3.0rc1` behandelt. Das `rc1`-Pre-Release-Kennzeichen macht explizit, dass:

- der Funktionsumfang von `0.3.0` erreicht ist,
- aber noch nicht die volle produktive Abnahme (Staging, Live-Smoke,
  Rechtsfreigabe, öffentlicher Launch) stattgefunden hat,
- Breaking Changes gegenüber `0.1.3` vorliegen (V3-Profile, neue Verträge,
  PWA-Architektur) und über Migration Notes dokumentiert werden.

## Abgrenzung zu ADR 0006

ADR 0006 bleibt als Planungsfolie gültig. Diese ADR 0015 überschreibt nicht
die Sequenzlogik, sondern erklärt den operativ eingetretenen Sonderfall
(kumulierte Integration ohne Zwischenreleases). Künftige Versionen ab
`0.3.0` (stabil) folgen wieder der normalen SemVer- und ADR-0006-Logik.

## Konsequenzen

- Kein nachträgliches Erzeugen von `v0.1.4`, `v0.1.5`, `v0.2.0`-Tags.
- Der nächste Tag ist `v0.3.0-rc.1` und wird ausschließlich auf dem
  Staging-geprüften main-SHA gesetzt (PR E + Staging-Gate).
- PR A (diese ADR) nimmt KEINEN Code-Version-Bump vor.
- Migration Notes (`docs/releases/migration-to-v0.3.0-rc.1.md`) dokumentieren
  die Breaking Changes gegenüber `v0.1.3`.
- Nach erfolgreichem öffentlichem Launch wird `0.3.0` (stabil) als regulärer
  Release gesetzt.

## Verweise

- ADR 0006 — Operational Release Sequencing
- ADR 0016 — V2 User-Owned Masterplan Boundary
- `docs/audit/current-state-numra-rc.md`
- `docs/plans/numra-0.3.0-rc1-implementation-plan.md`
- `PROJECT_CHARTER.md`, `ROADMAP.md`
