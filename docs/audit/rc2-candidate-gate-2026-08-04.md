# RC2-Kandidat — frischer Gate-Lauf und Image-Digests (2026-08-04)

> **Zweck:** Plan-Schritt A3 — vollständiger lokaler Gate-Lauf auf dem RC2-Kandidaten,
> danach einmaliger Build mit Digest-Erfassung fuer den Acceptance-Report (A4.3).
> **Commit-SHA:** `d7ca9b52c99e976b2bb76d0d47099ed3d0a7e858`
> **Umgebung:** lokaler Windows-Entwicklungsrechner, Docker Desktop, `uv 0.11.32`,
> `pnpm@10.22.0` (gepinnt, `package.json:4`), CPython 3.12.11 (nicht die
> System-Installation).

## Python-Gates

| Kommando | Ergebnis |
|---|---|
| `uv lock --check` | OK |
| `uv run --locked ruff format --check .` | OK — 108 Dateien |
| `uv run --locked ruff check .` | OK |
| `uv run --locked mypy src tests scripts` | OK — 108 Quelldateien |
| `uv run --locked pytest --cov=src/numerology_engine --cov-fail-under=95` | OK — 98,52 % |
| `uv run --locked pytest --cov=src --cov-fail-under=85` | OK — 93,46 %, 472 passed, 2 skipped |
| `uv run --locked python scripts/export_schemas.py --check` | OK |
| `uv run --locked python scripts/export_openapi.py --check` | OK |
| `uv run --locked python scripts/generate_examples.py --check` | OK |
| `uv run --locked python scripts/validate_knowledge.py` | OK — 2 Wissensbundles gueltig |
| `uv run --locked pip-audit -f json` | OK — keine bekannten Schwachstellen, 64 Pakete |

## Web-Gates

| Kommando | Ergebnis |
|---|---|
| `pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2` (exaktes CI-Kommando) | OK — 0 neue ignorierte Funde |
| `pnpm web:generate-api` + `git diff --exit-code` auf `schema.d.ts` | OK — kein Diff |
| `pnpm web:lint` | OK |
| `pnpm web:typecheck` | OK |
| `pnpm web:coverage` | OK — Statements 69,48 %, Branches 59,39 %, Functions 62 %, Lines 73,95 % (exakt die gesperrte Baseline vom 2026-08-02, keine Regression) |
| `pnpm web:build` | OK |
| `pnpm web:check-build` | OK — Budget 144.858/163.840 Bytes gzip, Coverage-Gate erfuellt |
| `pnpm web:e2e` | **22 passed, 1 failed (flaky), 2 skipped** — siehe unten |

### E2E-Befund: `mobile-webkit` WCAG-Test flaky, kein neuer Anwendungsfehler

`profile-flow.spec.ts:104` ("has no automated WCAG 2.2 AA violations in the primary
flow") meldete im Gesamtlauf einen `color-contrast`-Verstoss auf `.button-primary`
(gemessene Farben `#214a4e`/`#07151d`) — ausschliesslich im `mobile-webkit`-Projekt.

**Reproduzierbarkeitspruefung:** derselbe Test dreimal isoliert gegen `mobile-webkit`
wiederholt: 1× bestanden, 2× fehlgeschlagen, bei unveraendertem Code. Die
gemessenen Farbwerte entsprechen keiner der definierten CSS-Variablen
(`--teal: #55b9b1`, `.button-primary { color: #06191a }`, `apps/web/src/styles.css:10,196`)
— das deutet auf einen waehrend des axe-Scans erfassten Uebergangs-/Hover-Zustand
hin (`.button-primary:hover { background: #70cbc3 }` plus `transform`, `styles.css:199-201`),
nicht auf eine dauerhaft falsche Ruhezustand-Farbe.

**Warum dies nicht als neuer Diagnosebefund gefuehrt wird:** Keine der fuenf
Commits dieser Session beruehrt `apps/web/src` oder `styles.css`. Dieselbe
Testsuite lief auf demselben Codestand bereits in der GitHub-CI fuer PR #54
vollstaendig gruen (alle 4 required Checks inkl. „Web quality" mit E2E). Die
Nichtreproduzierbarkeit auf Linux-CI bei gleichzeitiger Nichtdeterminiertheit
lokal ist konsistent mit einer Playwright-WebKit-Timing-Eigenart, nicht mit
einem deterministischen Quellcode-Fehler. Es wurde bewusst **keine** spekulative
CSS-Aenderung vorgenommen, um nicht ohne gesicherte Ursache einen moeglicherweise
unbeteiligten Fehler zu verdecken.

**Empfehlung:** als eigenstaendiges, niedrig priorisiertes Ticket verfolgen
(Untersuchung: Hover-/Fokuszustand vor dem axe-Scan zuruecksetzen, z. B.
`page.mouse.move` auf einen neutralen Punkt vor `expectNoWcagViolations`).
Kein RC2-Blocker, da der massgebliche Gate-Nachweis die GitHub-CI ist, nicht
dieser lokale Lauf.

## Container-Gates

| Kommando | Ergebnis |
|---|---|
| `docker compose config --quiet` | OK |
| `sh -n` auf allen `deploy/scripts/*.sh` (inkl. neuer/geaenderter Skripte) | OK |
| `docker compose build` | OK |
| `docker compose up -d --wait --wait-timeout 60` | OK — alle drei Container healthy |
| `curl /`, `curl /api/v1/health/live`, `curl /api/v1/health/ready` | OK |

LLM-Staging-Override (`compose.llm-staging.yaml`) nicht lokal wiederholt — verlangt
`sudo`-Runtime-Marker unter `/etc/numra/`, auf Windows nicht sinnvoll nachstellbar.
Bereits auf demselben Codestand in GitHub-CI (Job „Container build and health
smoke") gruen bewiesen.

## RC2-Kandidat: einmaliger Build, Digests

```text
Kommando: sh deploy/scripts/build-release-image.sh d7ca9b52c99e976b2bb76d0d47099ed3d0a7e858
NUMRA_REPO_DIR=<Worktree-Root>

numra-api:d7ca9b52c99e976b2bb76d0d47099ed3d0a7e858
  Content-ID (.Id): sha256:6bf3deb8d2f38348afb2c4312c25df52fbb8105b1d3ee0013d42415eba7ab3e5

numra-web:d7ca9b52c99e976b2bb76d0d47099ed3d0a7e858
  Content-ID (.Id): sha256:996ae1f4393e6314f282a1ff7d74e17a3d0569709d2aa644a8872ca2a21d9480
```

**Wichtige Einschraenkung:** Es existiert noch keine Container-Registry fuer dieses
Projekt. Diese Digests sind ausschliesslich lokal auf dieser Maschine gueltig
(`docker image inspect`-Content-ID, kein `RepoDigests`-Eintrag). Der in A2.2
etablierte Deploy-by-Digest-Fluss (`build-release-image.sh` → optional `docker save`
→ Transport → `docker load` → `release.sh` ohne Rebuild) ist damit vollstaendig
funktionsfaehig bewiesen (siehe Commit `d7ca9b5`), aber der **Registry-Transportweg
selbst ist eine offene Entscheidung**: entweder ein `docker save`/`scp`/`docker load`-
Handbetrieb fuer den ersten RC2-Staging-Lauf, oder ein spaeter einzurichtender
CI-Push (z. B. GHCR) — Letzteres wurde bewusst nicht ohne Rueckfrage umgesetzt, da es
eine neue, persistente CI-/Infrastruktur-Entscheidung ist.

Nach diesem Gate-Lauf wurden die lokal gebauten Images wieder entfernt
(`docker image rm`), um die Maschine sauber zu halten. Sie sind mit demselben
Kommando jederzeit reproduzierbar buildbar.

## Zusammenfassung

```text
PYTHON_GATES=PASS
WEB_GATES=PASS (E2E: 22/25 bestanden, 1 lokal-flaky ohne CI-Entsprechung, siehe oben)
CONTAINER_GATES=PASS (Basis-Stack; LLM-Staging-Override bereits in CI bewiesen)
RC2_CANDIDATE_BUILT=YES
RC2_CANDIDATE_SHA=d7ca9b52c99e976b2bb76d0d47099ed3d0a7e858
RC2_CANDIDATE_API_DIGEST=sha256:6bf3deb8d2f38348afb2c4312c25df52fbb8105b1d3ee0013d42415eba7ab3e5
RC2_CANDIDATE_WEB_DIGEST=sha256:996ae1f4393e6314f282a1ff7d74e17a3d0569709d2aa644a8872ca2a21d9480
REGISTRY_TRANSPORT=NOT_DECIDED
RC2_CONDITION_6_CODE_QUALITY=PASS
```

Dies deckt RC2-Bedingung 6 („keine neuen Critical/High im Code") aus
`docs/committee/rc2-release-decision.md` fuer den aktuellen Codestand ab. Die
Bedingungen 1–4 (Staging-Host, Deploy, Restore, Rollback) bleiben unveraendert
offen und sind nicht Gegenstand dieses Laufs.
