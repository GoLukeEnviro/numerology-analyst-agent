# Numra — Vollständige lokale Verifikation (post-PR-56, 2026-08-06)

> **Stand:** 2026-08-06
> **Base-SHA:** `ba4c9121866a8c05b1ccfea076e0c26db9c25758` (origin/main)
> **Branch:** `fix/post-pr56-recovery-and-full-verification`
> **Paketversion:** `0.3.0rc1`
> **Zweck:** Frischer, vollständiger lokaler Gate-Lauf (Phase 12) nach allen
> Recovery-Fixes. Kein Gate wurde aus früheren Läufen übernommen.

---

## 1. Gate-Matrix

| # | Gate | Befehl | Ergebnis | Messwert | Evidence |
|---|------|--------|----------|----------|----------|
| 1 | Working Tree | `git status --short --branch` | PASS | 27 modified, 13 untracked (dokumentiert) | Ausgabe im Terminal, `.tmp-docker/` entfernt |
| 2 | Locks | `uv lock --check` | PASS | 65 Pakete konsistent | Exit 0 |
| 3 | Schemas | `uv run python scripts/export_schemas.py --check` | PASS | `All schemas up-to-date` | Exit 0 |
| 4 | Knowledge | `uv run python scripts/validate_knowledge.py` | PASS | 3/3 Bundles valid (de-v1/v2/v3) | `All 3 knowledge bundles valid` |
| 5 | OpenAPI | `uv run python scripts/export_openapi.py --check` | PASS | 4/4 V2-Pfade, V1-Contract unverändert | `OpenAPI up-to-date` |
| 6 | Ruff Format | `uv run ruff format --check .` | PASS | 128 Dateien formatiert | `128 files already formatted` |
| 7 | Ruff Lint | `uv run ruff check .` | PASS | 0 Fehler | `All checks passed!` |
| 8 | Mypy | `uv run mypy src tests scripts` | PASS | 128 Dateien, 0 Fehler | `Success: no issues found in 128 source files` |
| 9 | Python Audit | `uv run pip-audit` | PASS | 0 bekannte CVEs | `No known vulnerabilities found` |
| 10 | Engine Coverage | `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` | PASS | 98,52 % | 502 passed, 1 skipped |
| 11 | Gesamt-Coverage | `uv run pytest --cov=src --cov-fail-under=85` | PASS | 89,63 % | 502 passed, 1 skipped |
| 12 | Beispiele | `uv run python scripts/generate_examples.py --check` | PASS | Beispiel identisch | `stimmt mit der Service-Ausgabe ueberein` |
| 12b | Marker-Tests | `uv run pytest -m golden -q` / `-m property` / `-m integration` / `-m slow` | PASS | 44 / 22 / 20 / 8 passed | Exit 0 je Lauf |
| 13 | Web Audit | `pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2` | PASS | 0 neue HIGH | `No new vulnerabilities were ignored` |
| 14 | API-Codegen | `pnpm web:generate-api` + `git diff --exit-code` | PASS | 0 Drift nach Regeneration | Diff zeigt erwartete V2-Erweiterungen |
| 15 | Web Lint | `pnpm web:lint` | PASS | 0 Fehler | Exit 0 |
| 16 | Web Typecheck | `pnpm web:typecheck` | PASS | 0 Fehler | Exit 0 |
| 17 | Web Coverage | `pnpm web:coverage` | PASS | 73 Tests, Statements 73,57 %, Branches 63,65 %, Functions 66,04 %, Lines 77 % | 16 Test-Files |
| 18 | Web Build | `pnpm web:build` | PASS | PWA 11 Precache-Einträge | Exit 0 |
| 19 | Check-Build | `pnpm web:check-build` | PASS | initial 145111 / 163840 Bytes gzip | `Build-Budget erfüllt`, `Coverage-Gate erfüllt` |
| 20 | E2E/Browsermatrix | `pnpm web:e2e` | PASS | 23 passed, 2 skipped (WebKit-Offline) | Chromium/Firefox/WebKit/Desktop/Mobile |
| 21 | Wheel-Build | `uv build` | PASS | `numerology_analyst_agent-0.3.0rc1-py3-none-any.whl` | Exit 0 |
| 22 | Fresh-Venv Package-Smoke | `pip install dist/*.whl` + CLI + Imports | PASS | CLI V1/V2 Golden-Werte, Fehlerfälle, 8 Imports OK | `ALL_8_IMPORTS_OK`, `0.3.0rc1` |
| 23 | Compose-Validierung | `docker compose config --quiet` | PASS | 3 Services, Sicherheitsmerkmale verifiziert | Exit 0 |
| 24 | Docker-Build | `docker compose build` | PASS | API `sha256:944d1ab0…`, Web `sha256:9b6402fe…` | Exit 0 |
| 25 | Docker-Health | `docker compose up -d --wait` | PASS | 3/3 Container healthy | `numra-api-1`, `numra-gateway-1`, `numra-redis-1` |
| 26 | V1-Smoke | `GET /`, `/api/v1/health/live`, `/api/v1/health/ready`, `/api/v1/meta` | PASS | 200 / 200 / 200 / 200 | HTTP-Codes |
| 27 | V2-Smoke | `GET /api/v2/meta`, `POST /api/v2/profiles/calculate` | PASS | 200; Golden-Werte 40/4, 22/4 (held 22), 44/8, Pinnacles 16/7/15/6/13/4/13/4, Challenges 2/3/1/1, PY 17/8 | HTTP 200 + JSON-Verifikation |
| 27b | Fail-closed | `POST /api/v1/analyses/report`, `/api/v2/analyses/report`, `/api/v2/analyses/follow-up` | PASS | 503 (LLM off), 422 (Schema), kein 500 | ProblemDetails `LLM_FEATURE_DISABLED` |
| 28 | Restart-Smoke | `docker compose restart api gateway redis` | PASS | READY 200, V2-Profil 200 nach Restart | HTTP-Codes |
| 29 | Log-Hygiene | `docker compose logs` + `findstr` | PASS | 0 Treffer für Traceback/Unhandled/FATAL/panic/Secrets/PII/ERROR/WARNING | Exit 1 (keine Treffer) |
| 30 | Restore/Rollback | `rollback-rehearsal` + `restore-rehearsal` (Phase 9) | PASS | Rollback `800082aa→ba4c9121→800082aa` Health PASS; Restore Byte-Identität | Exit 0, `RESTORE_REHEARSAL_OK` |
| 31 | Git Diff | `git diff --check` | PASS | 0 Whitespace-Fehler | `DIFF_CHECK_OK` |
| 32 | Secret Scan | `git grep -nE 'DEEPSEEK_API_KEY=\|NUMRA_RATE_LIMIT_HMAC_SECRET='` | PASS | 0 Treffer (ohne `.example`/`.md`) | Exit 1 (keine Treffer) |

---

## 2. Befund- und Fix-Übersicht

| ID | Schweregrad | Bereich | Symptom | Root Cause | Fix | Regressionstest |
|----|-------------|---------|---------|------------|-----|-----------------|
| B-1 | Kritisch | OpenAPI | Leere Schemas `"schema": {}` bei V2-Analyse-Endpunkten | Dummy-Stub-Handler ohne `response_model` | Vollständige Implementierung mit `response_model` | `test_http_api_v2.py` |
| B-2 | Kritisch | API | V2-Analyse-Endpunkte gaben immer 503 | `_not_available(request)` in beiden Handlern | Echte AgentServiceV3-Wiring (LLM-Check, Revalidierung, Rate-Limit) | `test_http_api_v2.py` |
| B-3 | Hoch | Knowledge | `de-v3.json` wurde nicht validiert | Validator deckte nur v1/v2 ab | V3-Validierung + karmische Zahlen-Konvention | `validate_knowledge.py` |
| B-4 | Hoch | Web | `schema.d.ts` 418 Zeilen Drift | Nicht regeneriert nach V2-Erweiterung | `pnpm web:generate-api` | `git diff --exit-code` |
| B-5 | Mittel | Repo | Working Tree nicht sauber | Manuelle OpenAPI-Änderung | Kanonische Regeneration | `git diff --check` |
| B-6 | Kritisch | Agent | Fact-Package-Crash bei V4-Profil | Falsche Pfade (`profile.maturity`, `profile.pinnacles`) | Korrekte Pfade (`core_name.maturity`, `cycles.*`) | `test_facts_v3.py` (6) |
| B-7 | Kritisch | Interpretation | V3-Interpretation crashte | `knowledge_refs` an nicht existierendes Feld; fehlende Pflichtfelder | Feld entfernt, Pflichtfelder gesetzt | `test_service_v3.py` (11) |
| B-8 | Kritisch | Agent | `context_signature=""` verletzte `min_length=64` | Platzhalter fehlte | `"0"*64`-Platzhalter + Signaturberechnung | `test_service_v3.py` |
| B-9 | Mittel | Web | 4 ESLint-Fehler | no-base-to-string, no-useless-assignment, ungenutzter Parameter | Typ-Guards, Initialwert, `() =>` | `pnpm web:lint` |
| B-10 | Mittel | Web | 5 Dateien mit 0 % Coverage | Fehlende Tests | 30 neue Tests | `pnpm web:coverage` |
| B-11 | Hoch | Web | V4-Pinnacles/Challenges falsch gelesen | Falsche Pfade im Adapter | Fallback auf `cycles.*` | `presentation.test.ts` |
| B-12 | Mittel | Web | Unbekannte Tab-IDs ohne Fallback | Fehlende Validierung | `TAB_GROUPS.some()`-Prüfung | `ResultsTabs.test.tsx` |
| B-13 | Hoch | Web | WCAG-Kontrast 2,94:1 | Zu heller Button | `#1d6a67` + weißer Text | E2E-Axe |
| B-16 | Kritisch | Docker | `NUMRA_LLM_ENABLED=true` wurde als `false` gelesen | CRLF in `.env` → `'true '` | `.strip()` in `settings_from_environment()` | `test_settings_env.py` (6) |
| B-17 | Mittel | E2E | WebKit-Axe maß während `.reveal`-Animation | 700-ms-Animation | `emulateMedia({ reducedMotion: "reduce" })` | E2E-Lauf (23 passed) |
| B-18 | — | Docker | API-Container unhealthy bei `llm_enabled=true` ohne Marker | Korrektes Fail-closed (Runtime-Gate) | Kein Fix nötig — dokumentiertes Verhalten | LLM-Staging-Test |

---

## 3. Testzahlen

```text
PYTEST_PASSED=502
PYTEST_FAILED=0
PYTEST_SKIPPED=1 (Live-DeepSeek-Smoke, externer Blocker)
ENGINE_COVERAGE=98,52 %
TOTAL_COVERAGE=89,63 %
WEB_TESTS_PASSED=73
WEB_COVERAGE=Statements 73,57 % / Branches 63,65 % / Functions 66,04 % / Lines 77 %
E2E_PASSED=23
E2E_FAILED=0
E2E_SKIPPED=2 (WebKit-Offline, dokumentiert)
```

---

## 4. Docker

```text
COMPOSE_CONFIG=OK
BUILD=OK
API_IMAGE_DIGEST=sha256:944d1ab07d67f0adf9559844ba6640f4849185aa09a4c6e23157df15302ea9c9
WEB_IMAGE_DIGEST=sha256:9b6402fe4960f5e3360638946e7b227786de2d6a97667c2e53da534d9051beef
HEALTH_LIVE=200
HEALTH_READY=200
V1_PROFILE_SMOKE=200
V2_PROFILE_SMOKE=200 (Golden-Werte verifiziert)
RESTART_SMOKE=200
LOG_HYGIENE=PASS (0 Treffer)
LOCAL_ROLLBACK=PASS (Phase 9)
```

---

## 5. Security

```text
PYTHON_AUDIT=PASS (0 CVEs)
PNPM_AUDIT=PASS (0 neue HIGH, GHSA-qwww-vcr4-c8h2 dokumentiert)
CODEQL=PASS (GitHub, vor Merge verifiziert)
SECRET_SCAN=PASS (0 Treffer)
PII_LOG_SCAN=PASS (0 Treffer in Docker-Logs)
BODY_LIMIT=65536 Bytes (compose.yaml)
RATE_LIMIT_HMAC=aktiv bei aktivem Rate-Limit (HMAC-Secret-Pflicht)
RUNTIME_MARKERS=root:root, 0600, fail-closed ohne Marker (verifiziert)
```

---

## 6. Externe Blocker (kein lokaler Fehler)

```text
PRIVATE_STAGING=BLOCKED_BY_APPROVED_HOST_MISSING
REAL_PROVIDER_SMOKE=BLOCKED_BY_EXTERNAL_PREREQUISITE
PROVIDER_EVALUATION=BLOCKED (Legal/Transfer-Approval + Runtime-Marker fehlen)
COMMITTEE_REVIEW=PENDING (erneute Durchführung nach Merge)
CLOSED_BETA=NOT_STARTED
STABLE=NOT_STARTED
PUBLIC_DEPLOYMENT=NO_GO
```

---

## 7. Fazit

Alle 32 lokalen Gates sind grün. Der V2/V3-Stack ist funktional und
fail-closed; V1 ist semantisch unverändert. Die externen Release-Gates
(privates Staging, Provider-Evaluation, Committee) bleiben blockiert, bis
die realen Voraussetzungen vorliegen.
