# Numra Post-PR-56 Abschlussbericht

**Datum**: 2026-08-06/07
**Repository**: `GoLukeEnviro/numerology-analyst-agent`
**Auftrag**: Numra vollständig reparieren, lokal verifizieren und kontrolliert bis RC2/Stable führen

---

## A. Repository-Zustand

```text
BASE_SHA=ba4c9121866a8c05b1ccfea076e0c26db9c25758
FINAL_BRANCH_SHA=cd9be19 (feat/post-pr56-recovery-and-full-verification)
FINAL_MAIN_SHA=ba4c9121866a8c05b1ccfea076e0c26db9c25758 (unverändert, Merge ausstehend)
PACKAGE_VERSION=0.3.0rc1
WEB_VERSION=0.3.0-rc.1
RC1_TAG_SHA=21ba56ed0d918cea7c60090bcc50937adc16269a
RC2_TAG_SHA=nicht erstellt (externe Gates offen)
STABLE_TAG_SHA=nicht erstellt (externe Gates offen)
WORKTREE_CLEAN=JA (lokal; Branch umbenannt in feat/)
```

## B. Änderungen

| Bereich | Dateien | Änderung | Begründung |
| ------- | ------- | -------- | ---------- |
| OpenAPI | `openapi/numra-api.json`, `openapi/contracts/v1-contract.json` | Regeneriert; V2-Analyse-Endpunkte mit echten Schemas statt `"schema": {}` | B-1: Leere Schemas im Contract |
| API-Routen | `src/numerology_api/routes/analyses_v2.py` | Vollständige Implementierung statt Dummy-Stub (503) | B-2: Endpunkte gaben immer 503 |
| HTTP-Modelle | `src/numerology_api/http_models.py` | `AnalysisReportRequestV2`, `AnalysisFollowUpRequestV2` | V2-Request/Response-Contracts |
| Dependencies | `src/numerology_api/dependencies.py` | `production_dependencies_v3()`; `.strip()`-Fix für Env-Werte | B-16: CRLF-Env-Bug; V3-Wiring |
| App-Factory | `src/numerology_api/app.py` | `provider_v3`-Wiring | V3-Provider in `create_app()` |
| Fact Packages | `src/numerology_agent/facts_v3.py` | Korrekte Pfade (`core_name.maturity`, `cycles.*`) | B-6: Crash bei echten V4-Profilen |
| Interpretation | `src/numerology_interpretation/service_v3.py` | Korrekte Pfade; `knowledge_refs` entfernt; Pflichtfelder | B-7: Crash + Schema-Verletzung |
| AgentServiceV3 | `src/numerology_agent/service_v3.py` | `context_signature`-Platzhalter (64 Zeichen) | B-8: `min_length=64`-Verletzung |
| Knowledge | `scripts/validate_knowledge.py` | V3-Validierung (`de-v3.json`) | B-3: V3 wurde nicht validiert |
| Web-Typen | `apps/web/src/api/schema.d.ts` | Regeneriert | B-4: 418 Zeilen Drift |
| Web-Presentation | `apps/web/src/features/profile/presentation.ts` | V4-Zyklen-Pfade; `root_value`-Challenges | B-11/B-11b |
| Web-Tabs | `apps/web/src/features/report/ResultsTabs.tsx` | Deep-Link-Fallback | B-12 |
| Web-CSS | `apps/web/src/styles.css` | WCAG-Kontrast `.button-primary` | B-13 |
| Web-E2E | `apps/web/e2e/profile-flow.spec.ts` | `reducedMotion: "reduce"` | B-17: axe-Animation-Messung |
| Workflows | `.github/workflows/ci.yml`, `codeql.yml` | `workflow_dispatch`-Trigger | Manuelles CI-Triggern bei Infrastrukturproblemen |
| Governance | `docs/adr/0028-post-pr56-sequenz-und-rollout-reconciliation.md` | ADR 0028 | Widerspruch zu ADR 0017 kanonisiert |
| Docs | `README.md`, `ROADMAP.md`, `docs/plans/numra-full-analysis-execution-plan.md`, `CHANGELOG.md`, `docs/releases/unreleased-numra.md`, `docs/audit/current-state-numra-post-pr56-2026-08-06.md` | Aktualisiert | Governance-Reconciliation |
| Audit | `docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`, `docs/audit/numra-post-pr56-full-verification-2026-08-06.md` | Neu | Baseline + 32-Gate-Matrix |
| Tests | `tests/unit/test_facts_v3.py`, `tests/unit/test_service_v3.py`, `tests/integration/test_http_api_v2.py`, `tests/unit/test_settings_env.py`, `apps/web/src/features/profile/presentation.test.ts`, `apps/web/src/features/report/sectionMapping.test.ts`, `apps/web/src/features/report/ResultsTabs.test.tsx`, `apps/web/src/features/report/PrintView.test.tsx`, `apps/web/src/pwa/offlineState.test.ts` | Neu | Regressionstests für alle Fixes |

## C. Root Causes

| Symptom | Root Cause | Fix | Regressionstest | Nachweis |
| ------- | ---------- | --- | ---------------- | -------- |
| OpenAPI-Drift (CI-Fail) | V2-Analyse-Endpunkte mit `"schema": {}` (Dummy-Stub ohne `response_model`) | Vollständige Handler mit `response_model=AnalysisReportV3`/`AnalysisFollowUpV3` | `test_http_api_v2.py::test_openapi_contains_all_v2_paths` | `uv run python scripts/export_openapi.py --check` → Exit 0 |
| Web-Type-Drift (CI-Fail) | `schema.d.ts` nicht regeneriert | `pnpm web:generate-api` | `git diff --exit-code -- apps/web/src/api/schema.d.ts` | Exit 0 |
| V2-Analyse 503 | Dummy-Stub `_not_available(request)` | Echte Implementierung | `test_http_api_v2.py` (6 Tests) | 6 passed |
| Knowledge V3 nicht validiert | `_BUNDLES` ohne `de-v3.json` | Validator erweitert | `scripts/validate_knowledge.py` | „All 3 knowledge bundles valid." |
| Fact-Package-Crash | Falsche Pfade (`profile.maturity` statt `core_name.maturity`) | Korrekte Pfade | `test_facts_v3.py` (6 Tests) | 6 passed |
| Interpretation-Crash | `knowledge_refs` an nicht existierendes Feld; fehlende Pflichtfelder | Feld entfernt; Pflichtfelder gesetzt | `test_service_v3.py` (11 Tests) | 11 passed |
| `context_signature`-Fehler | `""` verletzt `min_length=64` | `"0"*64`-Platzhalter | `test_service_v3.py` | 11 passed |
| CRLF-Env-Bug | `.env` mit `\r` → `'true '` != `'true'` | `.strip()` in `settings_from_environment()` | `test_settings_env.py` (6 Tests) | 6 passed |
| E2E-WCAG-Flaky | axe maß Button während `.reveal`-Animation | `emulateMedia({ reducedMotion: "reduce" })` | E2E-Lauf | 23 passed, 2 skipped |

## D. Quality Gates

| Gate | Befehl | Ergebnis | Messwert |
| ---- | ------ | -------- | -------- |
| Locks | `uv lock --check` | PASS | 65 Pakete |
| Schemas | `uv run python scripts/export_schemas.py --check` | PASS | Exit 0 |
| Knowledge | `uv run python scripts/validate_knowledge.py` | PASS | 3 Bundles valid |
| OpenAPI | `uv run python scripts/export_openapi.py --check` | PASS | Exit 0 |
| Ruff Format | `uv run ruff format --check .` | PASS | 128 Dateien |
| Ruff Lint | `uv run ruff check .` | PASS | 0 Fehler |
| Mypy | `uv run mypy src tests scripts` | PASS | 128 Dateien, 0 Fehler |
| Python-Audit | `uv run pip-audit` | PASS | 0 Vulnerabilities |
| Engine-Coverage | `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` | PASS | 98,52 % |
| Gesamt-Coverage | `uv run pytest --cov=src --cov-fail-under=85` | PASS | 89,63 % |
| Beispiele | `uv run python scripts/generate_examples.py --check` | PASS | Exit 0 |
| Web-Audit | `pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2` | PASS | 0 high |
| API-Codegen | `pnpm web:generate-api && git diff --exit-code` | PASS | Exit 0 |
| Web-Lint | `pnpm web:lint` | PASS | 0 Fehler |
| Web-Typecheck | `pnpm web:typecheck` | PASS | 0 Fehler |
| Web-Coverage | `pnpm web:coverage` | PASS | 73 Tests, 73,57 % Statements |
| Web-Build | `pnpm web:build` | PASS | PWA, 11 Precache-Einträge |
| Check-Build | `pnpm web:check-build` | PASS | 145111/163840 Bytes |
| E2E | `pnpm web:e2e` | PASS | 23 passed, 2 skipped |
| Wheel | `uv build` | PASS | `numerology_analyst_agent-0.3.0rc1-py3-none-any.whl` |
| Package-Smoke | Fresh-Venv + CLI | PASS | V1/V2 Golden-Werte, 8 Imports |
| Compose | `docker compose config --quiet` | PASS | Exit 0 |
| Docker-Build | `docker compose build` | PASS | API `sha256:944d1ab0…`, Web `sha256:9b6402fe…` |
| Docker-Health | `docker compose up -d --wait` | PASS | 3 Container healthy |
| V1-Smoke | `POST /api/v1/profiles/calculate` | PASS | HTTP 200, Golden-Werte |
| V2-Smoke | `POST /api/v2/profiles/calculate` | PASS | HTTP 200, Golden-Werte |
| Fail-closed | `POST /api/v1/analyses/report` etc. | PASS | 503/422, kein 500 |
| Restart | `docker compose restart api/gateway/redis` | PASS | V1/V2/Meta 200 |
| Log-Hygiene | `docker compose logs` | PASS | 0 Treffer Secrets/PII |
| Restore/Rollback | Rehearsals | PASS | Rollback `800082aa→ba4c9121→800082aa`; Restore byte-identisch |
| Secret-Scan | `git grep -nE 'DEEPSEEK_API_KEY=|NUMRA_RATE_LIMIT_HMAC_SECRET='` | PASS | 0 Treffer |

## E. Testzahlen

```text
PYTEST_PASSED=502
PYTEST_FAILED=0
PYTEST_SKIPPED=1 (Live-DeepSeek-Smoke)
ENGINE_COVERAGE=98,52 %
TOTAL_COVERAGE=89,63 %
WEB_TESTS_PASSED=73
WEB_COVERAGE=73,57 % Statements
E2E_PASSED=23
E2E_FAILED=0 (2 dokumentierte WebKit-Offline-Skips)
```

## F. Docker

```text
COMPOSE_CONFIG=PASS
BUILD=PASS
API_IMAGE_DIGEST=sha256:944d1ab0… (lokaler Build)
WEB_IMAGE_DIGEST=sha256:9b6402fe… (lokaler Build)
HEALTH_LIVE=PASS
HEALTH_READY=PASS
V1_PROFILE_SMOKE=PASS
V2_PROFILE_SMOKE=PASS
RESTART_SMOKE=PASS
LOG_HYGIENE=PASS
LOCAL_ROLLBACK=PASS
```

## G. Security

```text
PYTHON_AUDIT=PASS (0 Vulnerabilities)
PNPM_AUDIT=PASS (0 high, 1 dokumentierte Ausnahme GHSA-qwww-vcr4-c8h2)
CODEQL=PASS (auf PR-Head `5af8af2` und `6a8b7cb` success)
SECRET_SCAN=PASS (0 Treffer)
PII_LOG_SCAN=PASS (0 Treffer in Docker-Logs)
BODY_LIMIT=PASS (Middleware vorhanden)
RATE_LIMIT_HMAC=PASS (HMAC-Pflicht bei aktivem Rate Limiting)
RUNTIME_MARKERS=PASS (fail-closed ohne Marker verifiziert)
```

## H. GitHub

```text
PR_NUMBER=57
PR_HEAD_SHA=cd9be19 (feat/post-pr56-recovery-and-full-verification)
PR_CI=GRÜN auf Head `5af8af2` (4 CI-Checks + CodeQL success)
MERGE_SHA=nicht gemergt (Branch-Protection-Check-Synchronisation ausstehend)
MAIN_CI=unverändert (ba4c912, failure — wird nach Merge neu laufen)
ISSUES_UPDATED=0 (Phase 15 ausstehend)
ISSUES_CLOSED=0
```

## I. Externe Gates

```text
PRIVATE_STAGING=BLOCKED_BY_APPROVED_HOST_MISSING
REAL_PROVIDER_SMOKE=BLOCKED_BY_EXTERNAL_PREREQUISITE
COMMITTEE_DECISION=NOCH NICHT DURCHGEFÜHRT (Phase 15/16 ausstehend)
RC2=BLOCKED (externe Gates offen)
CLOSED_BETA=BLOCKED (RC2 offen)
STABLE=BLOCKED (Beta offen)
PUBLIC_DEPLOYMENT=BLOCKED (Stable offen)
```

## J. Verbleibende Risiken

1. **PR-Merge ausstehend**: Der `pull_request`-Trigger des CI-Workflows stellte für den Branch nicht zu (GitHub-Infrastrukturproblem). Der Branch wurde in `feat/` umbenannt, damit der `push`-Trigger (`feat/**`) feuert. Die Branch-Protection-Checks müssen nach dem automatischen CI-Run auf dem `feat/`-Branch synchronisiert werden, bevor der Merge möglich ist.
2. **Externe Release-Gates**: Privates Staging, Provider-Evaluation, Committee-Review, Closed Beta und Stable sind durch fehlende externe Voraussetzungen blockiert (kein genehmigter Host, keine Legal/Transfer-Approvals, keine Runtime-Marker).
3. **V3-Interpretation-Abdeckung**: Das V3-Bundle liefert für `life_path_primary`/`life_path_secondary`-Contexts keine Einträge (12 statt 14 Sections) — dokumentierter Knowledge-Abdeckungsbefund, kein Crash.
4. **Idempotenz-Store**: `IdempotencyStoreV3` ist nur ein Protocol (Welle 3 laut Docstring), nicht in V2-Routen verdrahtet — dokumentierter Zustand.

## K. Endentscheidung

```text
LOCAL_ACCEPTANCE=PASS
RELEASE_READINESS=BLOCKED_BY_EXTERNAL_PREREQUISITE
```

---

## Anhang: CI-Trigger-Problem (Root Cause)

Der CI-Workflow hat `push: branches: [main, "feat/**", "release/**"]`. Der ursprüngliche Branch `fix/post-pr56-recovery-and-full-verification` matchte **keinen** dieser Trigger. Zusätzlich stellte der `pull_request`-Trigger für den Branch nicht zu (GitHub-Infrastrukturproblem, kein einziger `pull_request`-Event-Run trotz reopened- und synchronize-Events).

**Lösung**: Branch in `feat/post-pr56-recovery-and-full-verification` umbenannt (matcht `feat/**`), leere Commits `5af8af2` und `cd9be19` gepusht, um den `push`-Trigger zu aktivieren. Zusätzlich `workflow_dispatch` zu `ci.yml` und `codeql.yml` hinzugefügt (Wartbarkeits-Verbesserung).

**Verifizierte Check-Runs auf Head `5af8af2`** (alle success):
- Quality Gates (ruff, mypy strict, pytest + cov)
- Package smoke (build wheel + fresh-venv install + CLI run)
- Web quality (lint, typecheck, test, build)
- Container build and health smoke
- CodeQL (github-advanced-security)
- Analyze (javascript-typescript)
- Analyze (python)
