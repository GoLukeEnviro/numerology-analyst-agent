# Dependency- und Security-Entscheidung (RC2) — 2026-08-02

> **Bezug:** Issue #42 · Epic #37 · Mess-SHA main vor Docs-Merge:
> `5976ae2299059451461f634cb89f525151fda8b2` (Gates unverändert auf
> Docs-only-Merge `7f9795c…` anwendbar).  
> **Primärquellen:** `pip-audit`, `pnpm audit`, GitHub Advisory
> [GHSA-qwww-vcr4-c8h2](https://github.com/advisories/GHSA-qwww-vcr4-c8h2),
> CI-Workflow `.github/workflows/ci.yml`.

## Python

| Prüfung | Ergebnis | Entscheidung |
|---------|----------|--------------|
| `uv run pip-audit` (2026-08-02) | No known vulnerabilities found | **behalten** — keine Aktion |

## Node / Frontend

| Paket | Version | Advisory | Severity | Entscheidung |
|-------|---------|----------|----------|--------------|
| `react-router` (via `react-router-dom`) | 7.18.x | GHSA-qwww-vcr4-c8h2 | HIGH | **DEFER mit CI-Ignore** bis gezielter Major-Upgrade-Stream |

### Begründung (kein Blind-Upgrade)

- Patch-Pfad laut Advisory: `>= 8.3.0` (Major von v7 → v8).
- CI verwendet bereits `pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2`
  (`.github/workflows/ci.yml`).
- Frischer `pnpm audit --audit-level high` ohne Ignore: **FAIL** (1 high).
- Frischer Audit mit CI-Ignore: **PASS**.
- Routing, Deep Links, PWA-Offline und Browser-E2E (5 Projekte) sind
  release-kritisch; Major-Upgrade ohne dedizierten Fix-Branch und voller
  E2E-/Budget-Matrix ist unzulässig (Orchestrierungsregel: keine blinden Majors).

### Risiko und Owner

| Feld | Wert |
|------|------|
| Risiko | XSS/Open-Redirect-Klasse laut Advisory in `react-router` ≥7.12.0 &lt;8.3.0 |
| Exploit-Pfad in Numra | Client-only SPA-Routing; kein serverseitiges HTML-Templating |
| Akzeptiertes Restrisiko bis RC2-Upgrade-PR | **JA**, mit Owner: Release-Orchestrator / Issue #42 |
| Nächster Schritt | Optionaler Branch `fix/rc2-dependency-security` mit Upgrade + voller Web-Matrix vor stable, nicht blockierend für deterministisches Staging |

## Container / Runtime-Oberfläche (Kurzcheck)

- Deterministischer Stack: `NUMRA_LLM_ENABLED=false` Default.
- Compose-Health live/ready + Profilberechnung lokal (Docker Desktop) 2026-08-02 **PASS**.
- Keine neuen Python-CVEs; Secret-Handling-Regeln unverändert (keine Klartext-Keys in Git).

## Gate

```text
DEPENDENCY_DECISION=DEFER_REACT_ROUTER_MAJOR
PIP_AUDIT=PASS
PNPM_AUDIT_WITH_CI_IGNORE=PASS
PNPM_AUDIT_RAW_HIGH=FAIL_EXPECTED
MAJOR_UPGRADE_PERFORMED=NO
```
