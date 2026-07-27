# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektüberblick

**Numra** (`numerology-analyst-agent`) ist eine auditierbare Numerologie-Plattform: ein
deterministischer, LLM-freier Python-Rechenkern + FastAPI-Backend + eine
lokale-first React/PWA-Frontend. Quelle der Wahrheit für Scope, Prinzipien und
Phasen: `PROJECT_CHARTER.md`, `ROADMAP.md`, `docs/governance/master-implementation-contract.md`
und `.github/copilot-instructions.md`. Bei Widersprüchen gewinnt der Master-Vertrag.

**Bindendes Grundprinzip: Determinismus vor LLM.** Alle Berechnungen funktionieren
vollständig ohne Sprachmodell. Ein LLM darf validierte Ergebnisse ausschließlich
erklären/sprachlich aufbereiten — niemals selbst rechnen, Daten erfinden,
Methodenversionen vermischen oder validierte Ergebnisse überschreiben. Daraus folgt:
**kein** Netzwerk- oder LLM-Import in `src/numerology_engine/`.

Das System unterscheidet technisch zwischen sechs Aussageklassen, die in Domainmodellen,
Schemas, API-Ausgaben und Tests sichtbar sein müssen: `input_fact`, `calculation_fact`,
`traditional_claim`, `interpretive_hypothesis`, `empirical_evidence`, `practical_suggestion`
(siehe `PROJECT_CHARTER.md` §3).

## Befehle

### Python (Rechenkern, API, CLI) — `uv`-basiert

```bash
uv sync --locked --all-groups          # Abhängigkeiten installieren (dev-Gruppe inkl.)
uv run ruff format --check .           # Format-Check
uv run ruff check .                    # Lint
uv run mypy src tests scripts          # Strict Typecheck
uv run pytest                          # Gesamte Test-Suite
uv run pytest --cov=src/numerology_engine --cov-fail-under=95   # Core-Coverage-Gate
uv run pytest --cov=src --cov-fail-under=85                     # Gesamt-Coverage-Gate
uv run pip-audit                       # Dependency-Security-Scan
```

Äquivalente `Makefile`-Targets: `make sync`, `make lint`, `make typecheck`, `make test`,
`make test-cov-core`, `make test-cov-total`, `make test-cov`, `make all` (alle Quality Gates).

Einzelnen Test ausführen:

```bash
uv run pytest tests/unit/test_profile_calculation.py::test_life_path_a_reduces_master_number
uv run pytest -m golden          # nur golden-marker
uv run pytest -m property         # nur hypothesis property-Tests
uv run pytest tests/golden/test_profile_golden.py -k "karmic"
```

Marker sind in `pyproject.toml` unter `[tool.pytest.ini_options]` deklariert:
`golden`, `integration`, `property`, `unit`.

Schema-/OpenAPI-/Beispiel-Export (müssen mit `--check` reproduzierbar bleiben):

```bash
uv run python scripts/export_schemas.py --check
uv run python scripts/export_openapi.py --check
uv run python scripts/generate_examples.py --check
```

CLI lokal ausführen (Beispiel):

```bash
uv run numerology profile --name "Max Mustermann" --birth 1985-07-25 --as-of-date 2026-07-26
```

FastAPI lokal:

```bash
uv run uvicorn numerology_api.app:app --reload --port 8000
```

### Web/PWA (`apps/web`) — pnpm-Workspace

Von Repo-Root aus (Wrapper-Skripte in `package.json`):

```bash
pnpm install --frozen-lockfile
pnpm web:lint           # eslint --max-warnings 0
pnpm web:typecheck       # tsc -b --pretty false
pnpm web:test            # vitest run
pnpm web:build           # tsc -b && vite build
pnpm web:check-build     # scripts/check-build.mjs
pnpm web:e2e             # playwright test
pnpm web:generate-api    # openapi-typescript ../../openapi/numra-v1.json -o src/api/schema.d.ts
```

Einzelnen Vitest-Test: `pnpm --filter @numra/web exec vitest run <pfad>`.
Einzelnen Playwright-Test: `pnpm --filter @numra/web exec playwright test <pfad>`.

Dev-Server: `pnpm --filter @numra/web dev` (läuft auf `http://localhost:5173`,
erwartet die FastAPI-API auf Port 8000 als CORS-Origin).

Der API-Client (`apps/web/src/api/schema.d.ts`) wird aus `openapi/numra-v1.json`
generiert — nach Änderungen an FastAPI-Endpunkten `uv run python scripts/export_openapi.py`
und danach `pnpm web:generate-api` ausführen, nicht von Hand editieren.

### Container-Smoke

```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait
curl --fail http://127.0.0.1:8080/api/v1/health/ready
docker compose down
```

## Architektur

### Fünf getrennte Ebenen mit harten Paketgrenzen

Der Master-Vertrag verlangt fünf Ebenen (Fachmodell, Rechenkern, Wissensmodell,
Forschungsrahmen, App-Schicht), realisiert als acht Python-Pakete unter `src/` plus
zwei App-Pakete. **Keine zyklischen Abhängigkeiten zwischen diesen Paketen.**

| Paket | Verantwortung | Regel |
|---|---|---|
| `numerology_domain` | Verträge/Typen: `PersonInput`, `MethodPolicy`, `ProfileCalculationResult`, Schema-Versionen | Reine Datenmodelle (pydantic v2, `frozen=True`) |
| `numerology_engine` | Deterministischer Rechenkern (Normalisierung, Alphabet, Reduktion, Datumsalgorithmen, Zyklen, Trace) | **Kein Netzwerk, kein LLM-Import, keine globale State, keine Randomness** |
| `numerology_knowledge` | Lädt/validiert versionierte Wissenspakete (`data/de-v1.json`) | Enthält keine Berechnungslogik |
| `numerology_interpretation` | Regelbasierte, rückverfolgbare Interpretationskomposition | Keine freie LLM-Erfindung als Kernfunktion |
| `numerology_safety` | Claims-/Sprach-/Prompt-Injection-Validierung | Setzt auf Rechenkern auf, nicht umgekehrt |
| `numerology_agent` | Dünner, optionaler LLM-Adapter (DeepSeek), Rate-Limiting, Mock-fähig | Darf validierte Ergebnisse nie überschreiben |
| `numerology_api` | Zustandslose FastAPI-Grenze (`app.py`, `http_models.py`, `contracts.py`) | Owns HTTP-Verträge, Middleware, Rate-Limit-Verdrahtung |
| `numerology_cli` | Typer-CLI (`profile`-Command) | Dünne Hülle über `numerology_engine` |
| `apps/web` | React/Vite/TypeScript-PWA | Konsumiert `numerology_api` über generierten OpenAPI-Client |

Import-Reihenfolge folgt der Pipeline: `domain → engine → knowledge → interpretation
→ safety → agent → api/cli`. `ruff.lint.isort` mit `known-first-party` erzwingt das.

### Verarbeitungs-Pipeline

```
Eingaben → Normalisierung → Methoden-/Policy-Auswahl → deterministischer Rechenkern
  → auditierbares Ergebnis (Trace + Hash) → Wissensauflösung → Interpretationskomposition
  → Safety-/Evidenz-/Aussageklassifizierung → CLI / API / Agent / Bericht
```

### Determinismus- und Hash-Vertrag

- Alle Domain-Modelle sind immutable (`pydantic` v2, `frozen=True`); Serialisierung
  erfolgt immer mit `sort_keys=True` — identischer Input + Policy ⇒ byte-identisches JSON.
- Jede Berechnung trägt einen `deterministic_hash` (SHA-256) über ein
  `CalculationHashEnvelope`: Schema-Version, fachlich relevante Eingaben, vollständige
  Policy, Ergebnisse und Trace. `consent_given` ist explizit vom Hash ausgeschlossen.
- `--as-of-date` ist an CLI und API verpflichtend — macht Läufe unabhängig vom
  Systemdatum reproduzierbar. Aktueller Rechenkern-Vertrag: `profile-calculation-result-v3`
  (kompatibel zu `calculation-result-v1`).
- Golden-Cases in `tests/golden/cases.yaml` und `tests/golden/profile_cases.yaml` sind
  gepinnte Referenzwerte — Änderungen daran sind ein Vertragsbruch, kein Refactoring.

### FastAPI-App (`src/numerology_api/app.py`)

`create_app()` ist eine Factory (kein globaler State außer dem Modul-Level `app`).
Middleware-Kette (Reihenfolge relevant): `OriginValidationMiddleware` →
`RequestBodyLimitMiddleware` → `AccessLogMiddleware` → `CORSMiddleware` →
`SecurityHeadersMiddleware` → `CorrelationIdMiddleware`. LLM-Endpunkte
(`/api/v1/analyses/*`) sind nur aktiv wenn `NUMRA_LLM_ENABLED=true`; sie verifizieren
eingehende Profile gegen eine neu berechnete kanonische Version (`canonical_analysis_profile`),
bevor der Agent aufgerufen wird — Clients können Profile nicht fälschen, um den Agent
zu manipulieren. Rate-Limiting läuft über Redis, ausschließlich mit HMAC-pseudonymisierten
Keys (`pseudonymous_key`), nie mit Klartext-IP/Device-ID.

### Web-App (`apps/web/src`)

- `api/` — generierter OpenAPI-Client (`schema.d.ts`, nicht editieren) + `client.ts`.
- `features/{profile,analysis,report,export}/` — vertikale Feature-Slices.
- `storage/` — lokale IndexedDB-Persistenz (Dexie) inkl. optionaler PBKDF2-/AES-GCM-Verschlüsselung (`crypto.ts`).
- `pwa/` — Service-Worker-Update-Handling (`vite-plugin-pwa`/Workbox).
- Die App funktioniert offline-lesend; alle Profile/Berichte/Notizen liegen primär lokal.

### Wissenspakete

`src/numerology_knowledge/data/de-v1.json` ist das versionierte, schema-validierte
deutsche Wissenspaket. Neue Inhalte brauchen stabile IDs, Quellenstatus (z. B.
`tradition_unverified`) und dürfen keine Berechnungslogik enthalten.

## Verbindliche Coding-Regeln (Auszug, siehe `.github/copilot-instructions.md` für Details)

- Keine `any`-artigen Typen; `mypy strict` ist scharf gestellt (siehe `pyproject.toml`).
- Kein `# type: ignore` ohne Begründung im Kommentar.
- Keine Vermischung von Methodenversionen (nur `pythagorean-v1` in V1; chaldäische/kabbalistische
  Werte sind eine Verunreinigung, siehe `PROJECT_CHARTER.md` §6).
- Keine erfundenen Daten — fehlende Werte explizit als fehlend markieren.
- Keine Diagnosesprache in Interpretations-/Wissenstexten (Claims-Validator-Blacklist).
- Commits: Deutsch, Format `<type>: <kurzbeschreibung>`, Fokus aufs Warum
  (`feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `build`, `ci`).
- Kein Direktpush/Force-Push auf `main`, kein `--no-verify`.
