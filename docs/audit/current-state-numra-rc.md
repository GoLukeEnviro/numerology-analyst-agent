# Numra — aktueller Quellstand (RC-Vorbereitung)

> Stand: 28. Juli 2026
>
> Basis-SHA: `8faba1b4442939a97252282c60b3f4f808d62235` (origin/main)
>
> Zweck: Vollständige NEU-Inventarisierung als Grundlage für die Release-Sequenz
> `0.3.0rc1`. Diese Datei erfüllt die Bestandsaufnahmepflicht aus
> Master-Vertrag §2.1 (Keine erfundenen Zustände) und liefert die
> Abschlussbericht-Struktur aus §10. Sie ersetzt keine Verifizierung durch
> ausführbaren Code.

---

## 1. Repository-Zustand

| Kennzeichen | Wert |
|---|---|
| Remote | `github.com/GoLukeEnviro/numerology-analyst-agent` |
| `origin/main` | `8faba1b4442939a97252282c60b3f4f808d62235` |
| Lokaler `HEAD` (main) | `8faba1b` (synchron mit origin) |
| jüngste Tags | `v0.1.0`, `v0.1.1`, `v0.1.2`, `v0.1.3` |
| jüngster Release-Tag | `v0.1.3` |
| Offene PRs | keine |
| Offene Dependabot-Alerts | keine |

Jüngste main-Commits:

1. `8faba1b` CodeQL-Baseline und finales Integrationsaudit (#12)
2. `2a514e9` Post-Merge-Integrität, Datenschutz und Kompatibilität härten (#11)
3. `3c970ae` feat: Numra PWA — vollständiger Profilkern (#10, Squash)

Lokaler Backup-Branch `backup/0.1.3-before-venv-cleanup` (`8f05b07`) bleibt erhalten.

## 2. Versionierungs-Widerspruch (Anlass für RC1)

Der integrierte Quellstand vereint die geplanten Funktionsbereiche `0.1.4`
(Kompatibilität/Härten), `0.1.5` (DeepSeek + Bericht) und `0.2.0`/`0.3.0`
(PWA + Wissensmodell). Die formale Version in `pyproject.toml` und
`openapi/numra-v1.json` lautet `0.1.5`, die Web-App trägt `0.1.0`. ADR 0006
verlangt eine sequenzielle Releasefolge `0.1.4 → 0.1.5 → 0.2.0 → 0.3.0`.

Diese Mehrdeutigkeit wurde in PR #11 und PR #12 bewusst nicht durch einen
willkürlichen Tag aufgelöst. Stattdessen normalisiert ADR 0015 ( dieser
Release-Sequenz) den kumulierten Stand auf `0.3.0rc1`, ohne die
ADR-0006-Folge nachträglich zu verfälschen. Der tatsächliche Version-Bump
erfolgt ausschließlich in PR E.

## 3. Lokale Quality-Gate-Baselines (am 28.07.2026 neu gemessen)

Alle Werte wurden aus echten Läufen abgeleitet, nicht aus Audit-Texten
übernommen.

### Python

| Gate | Ergebnis |
|---|---|
| `uv run ruff format --check .` | 68 Dateien korrekt formatiert |
| `uv run ruff check .` | alle Checks bestanden |
| `uv run mypy src tests scripts` | Success: keine Issues in 68 Dateien |
| `uv run pytest` | **207 passed** in 21,47 s |
| Engine-Coverage (`--cov=src/numerology_engine`) | **97,12 %** (331 stmts, 6 miss) |
| Gesamt-Coverage (`--cov=src`) | **93,02 %** (1343 stmts, 69 miss) |

### Verträge / Drift

| Gate | Ergebnis |
|---|---|
| `scripts/export_openapi.py --check` | OpenAPI up-to-date |
| `scripts/export_schemas.py --check` | alle Schemas up-to-date |
| `scripts/generate_examples.py --check` | Beispiel stimmt mit Service-Ausgabe überein |

### Web (`apps/web`)

| Gate | Ergebnis |
|---|---|
| `pnpm web:lint` | keine Warnungen (`--max-warnings 0`) |
| `pnpm web:typecheck` | keine Fehler |
| `pnpm web:test` | **34 passed** (10 Test-Dateien) in 15,02 s |
| `pnpm web:build` | PWA-Build, 11 precache-Einträge (480,87 KiB) |

## 4. Paketgrenzen und Pipeline (IST)

Acht Python-Pakete unter `src/` plus zwei App-Pakete, keine zyklischen
Imports (durch `ruff.isort` mit `known-first-party` erzwungen).

```
numerology_domain → numerology_engine → numerology_knowledge
  → numerology_interpretation → numerology_safety → numerology_agent
  → numerology_api / numerology_cli / apps/web
```

| Paket | IST-Zustand |
|---|---|
| `numerology_domain` | Verträge/Typen, immutable (`frozen=True`), Schema-Versionen vorhanden |
| `numerology_engine` | Deterministischer Kern, kein Netz/LLM-Import, Hash via `CalculationHashEnvelope` |
| `numerology_knowledge` | Loader für `data/de-v1.json`, `KnowledgeEntry` mit `number:int` (kein Compound) |
| `numerology_interpretation` | Regelbasierte Komposition, keine freie LLM-Erfindung |
| `numerology_safety` | Claims-/Sprach-/Prompt-Injection-Validierung |
| `numerology_agent` | DeepSeek-Adapter, Agent-Service, Rate-Limit |
| `numerology_api` | FastAPI-Grenze (`create_app()`-Factory), Middleware-Kette, LLM-Endpunkte hinter `NUMRA_LLM_ENABLED` |
| `numerology_cli` | Typer-CLI (`profile`-Command) |
| `apps/web` | React/Vite/TS-PWA, generierter OpenAPI-Client, IndexedDB (Dexie) |

## 5. Determinismus- und Hash-Vertrag

- Alle Domain-Modelle immutable (`pydantic` v2, `frozen=True`).
- Serialisierung mit `sort_keys=True` — identischer Input + Policy ⇒ byte-identisches JSON.
- Jede Berechnung trägt `deterministic_hash` (SHA-256) über `CalculationHashEnvelope`.
- `--as-of-date` an CLI und API verpflichtend.
- Aktueller Rechenkern-Vertrag: `profile-calculation-result-v3`.
- `consent_given` ist vom Hash ausgeschlossen.
- Golden-Cases in `tests/golden/` sind gepinnte Referenzwerte — Änderungen sind Vertragsbruch.

## 6. DeepSeek-IST-Stand (relevant für PR B)

`src/numerology_agent/deepseek.py`:

- `DeepSeekSettings`: nur `api_key`, `base_url`, `model` (`deepseek-v4-pro`), `timeout_seconds`.
- Anfrage-Body: `temperature=0.2`, `top_p=1`, `thinking={"type":"enabled"}`,
  `reasoning_effort="high"`, `max_tokens=8192`, `response_format={"type":"json_object"}`.
- Keine Provider-Retry-Logik, kein Circuit Breaker, keine `max_retries`-Settings.

`src/numerology_agent/service.py`:

- 2 Versuche bei Schema-Validierungsfehler (`for _attempt in range(2)`).
- Fail-closed bei erfundenen Zahlen, unbekannten Knowledge-Referenzen, PII,
  Prompt-Injection, Safety-Verletzung.
- Provenance hardcodiert: `temperature=0.2`, `top_p=1`, `thinking="enabled/high"`.
- HMAC-Signatur (`context_signature`) bindet Bericht an kanonisches Profil.

`src/numerology_agent/models.py`:

- `AnalysisReport.schema_version = "analysis-report-v1"`.
- `AnalysisFollowUp.schema_version = "analysis-follow-up-v1"`.
- `ProviderRequest.prompt_version = "numra-report-de-v1"`.
- `AnalysisProvenance.temperature/top_p` sind Pflicht-`float`, `effective_sampling="provider_managed"`, `reasoning_effort="high"`.
- `AnalysisClaim` hat KEINE `uncertainty`/`counter_hypothesis`/`composer_rule_id`.

PR B hebt diese auf v2 (`analysis-report-v2`, `numra-report-de-v2`),
parametrisiert die Settings, ergänzt Circuit Breaker und providerseitiges
Retry bei Netz-/Timeout-/429-/5xx-Fehlern, entfernt `temperature`/`top_p`
aus Anfrage und Provenance und lädt Prompts aus Dateien.

## 7. Knowledge-IST-Stand (relevant für PR C)

`src/numerology_knowledge/data/de-v1.json` (V1, lesbar):

- `KnowledgeEntry.number: int` — keine Compound-Struktur.
- Felder: `number`, `title`, `traditional_claims`, `reflection_prompts`,
  `practical_suggestions`, `counter_hypotheses`, `source_refs`.
- Keine `stable_id`, kein `method_system`, kein `claim_class`,
  keine `constructive`/`shadow_expression`, kein `development_theme`,
  keine `result_contexts`, kein `authoring_provenance`.

PR C führt V2 mit Compound-Struktur (`raw_value`/`reduced_value`/
`compound_notation`/`classification`), kontextsensitivem Resolver und
neuen Pflichtfeldern ein. V1 bleibt lesbar; V2 wird Default für Neuerzeugung.

## 8. API-IST-Stand

- FastAPI-Factory `create_app()`, Middleware-Kette:
  `OriginValidation` → `RequestBodyLimit` → `AccessLog` → `CORS` →
  `SecurityHeaders` → `CorrelationId`.
- LLM-Endpunkte `/api/v1/analyses/*` nur aktiv bei `NUMRA_LLM_ENABLED=true`.
- Eingehende Profile werden vor LLM-Aufruf als kanonisches V3 neu berechnet
  (`canonical_analysis_profile`).
- Rate-Limiting über Redis mit HMAC-pseudonymisierten Keys.
- OpenAPI `info.version = 0.1.5`.

## 9. Web-App-IST-Stand (relevant für PR D)

- `apps/web/src/api/schema.d.ts` aus `openapi/numra-v1.json` generiert.
- Vertikale Feature-Slices: `features/{profile,analysis,report,export}`.
- IndexedDB-Persistenz via Dexie (inkl. optionaler PBKDF2/AES-GCM).
- Service-Worker via `vite-plugin-pwa` (Workbox), `registerType: "prompt"`.
- PWA-Manifest in `vite.config.ts` ohne `version`/`version_name`-Felder.
- `@tanstack/react-query` in `package.json` (Nutzung in PR D zu prüfen).
- `AbortController`/Abbrechen-Button, Insight→Next-Step-Brücke,
  Server-Quota-Display, Skip-to-Content noch offen (PR D).

## 10. Safety- und Datenschutz-IST

- `numerology_safety.validation`: `assert_text_safe`, `assert_prompt_safe`.
- Claims-Validator verbietet Diagnosesprache, absolute Vorhersagen,
  identitätsdefinierende Aussagen.
- PII-Prüfung gegen Profilnamen und Geburtsdaten (mehre Datumsformate).
- Provider-Payload ist pseudonymisiert (nur reduzierte Werte + Referenzen).
- `numra-export-v2` mit Klartext-Innenvertrag, V1-Vault wiederherstellbar.
- LLM standardmäßig deaktiviert.

## 11. CI- und Branch-Protection-IST

Erforderliche Checks auf `main` (vier):

1. Quality Gates (ruff, mypy strict, pytest + cov)
2. Package Smoke (wheel build + fresh-venv install + CLI run)
3. Web Quality (lint, typecheck, test, build)
4. Container Build and Health Smoke

Zusätzlich:

- Strict Status Checks: aktiv.
- Lineare Historie: aktiv.
- Force-Push: deaktiviert.
- Branch-Löschung: deaktiviert.
- Reviewpflicht: bewusst nicht aktiv (kein dauerhaft verfügbarer Reviewer).
- CodeQL (PR #12): vorhanden, NICHT als Required Check konfiguriert (Baseline).

## 12. Security- und Dependency-IST

- Secret Scanning: 0 Alerts.
- `pip-audit`: keine bekannte Python-Schwachstelle.
- `GHSA-qwww-vcr4-c8h2` (React-Router): betrifft ausschließlich ungenutzte
  instabile RSC-/Server-Action-Pfade; dokumentiert toleriert bis zum
  Major-Upgrade auf React Router 8.3.0.
- CodeQL: Baseline-Lauf vorhanden, keine P0/P1-Befunde gemeldet.

## 13. Was PR #11 bereits abdeckt (nicht neu planen)

Die folgenden Themen sind durch PR #11 erledigt und in PR B/C/D nicht erneut
zu planen:

- kanonische serverseitige Neuberechnung vor jedem LLM-Aufruf,
- geräteweite Tagesquoten und nicht spoofbare Proxy-Vertrauenskette,
- getrennte Core-/Active-Reifezahlen und vollständiger Active-Trace,
- `numra-export-v2` mit Klartext-Innenvertrag,
- HMAC-gebundene Berichtskontexte,
- PII-Prüfung von Bericht und Rückfrage,
- echter Redis-Readiness-Ping,
- axe-basierte WCAG-2.2-AA-Prüfung, tastaturzugängliche mobile Tabellen,
  kontrastfeste Aktionsbuttons.

PR #12 ist abgeschlossen: CodeQL-Baseline und diese finales-Integrationsaudit
als Artefakte.

## 14. Offene externe Gates (nicht lokaler Scope)

Folgende Werte und Freigaben fehlen und blockieren öffentlichen Launch,
nicht aber die RC-Tag-Erstellung nach erfolgreichem privatem Staging:

- DeepSeek API-Key,
- rechtliche Prüfung des Drittlandtransfers (DeepSeek),
- bestätigtes VPS-Ziel,
- Domain, DNS und TLS-Kontaktadresse,
- Betreiberanschrift, Impressums- und Datenschutzkontakt,
- ausdrückliche Freigabe für den öffentlichen Launch.

## 15. Staging-Gate-Vorbereitung

Nach PR-E-Merge wird der finale main-SHA (`$ReleaseSha`) erfasst und exakt
dieser SHA auf privates Staging deployt. Erst nach echtem DeepSeek-Live-Smoke,
Backup/Restore-Drill, Rollback-Nachweis, 17-Punkte-Abnahme und Setzen der
Runtime-Dateimarker (`/etc/numra/numra-legal-approved`,
`/etc/numra/llm-transfer-approved`, root:root:0600) wird der Tag
`v0.3.0-rc.1` auf genau diesem SHA erzeugt. Kein Tag auf einem anderen Commit.

## 16. Definition of Done (Master §9) — IST-Erfüllung

| DoD-Kriterium | IST |
|---|---|
| Fachgebiet formal dokumentiert | ja (Master-Vertrag, Methodenspezifikation) |
| kanonische Methode versioniert | ja (`pythagorean-v1`) |
| Rechenkern deterministisch | ja (207 Tests, 97,12 % Engine-Coverage) |
| jede Berechnung hat Auditspur | ja (`CalculationHashEnvelope`, Trace) |
| Wissensinhalte getrennt und versioniert | V1 ja; V2 (PR C) offen |
| Interpretationen rückverfolgbar und hypothetisch gekennzeichnet | ja (Claim-Klassen) |
| empirische Forschung ergebnisoffen | Rahmen vorhanden; Welle 9 später |
| Safety- und Datenschutzregeln technisch geprüft | ja |
| CLI und API funktionieren | ja |
| Agent nur als kontrollierte Adapterschicht | ja; PR B schärft Retry/Circuit Breaker |
| Tests, Typecheck, Lint, Docs, Build grün | lokal ja; CI pro PR |
| Committee Review | Welle 6/7 später |
| echter PR und nachvollziehbares Release | PR-Sequenz A–E; Tag nach Staging-Gate |

---

## Quellen der Wahrheit

Ausführbarer Code auf `8faba1b` ist die Quelle der Wahrheit für alle
Behauptungen in dieser Datei. Die lokalen Gate-Ergebnisse wurden am 28.07.2026
neu gemessen und sind reproduzierbar. PR-Beschreibungen dienen nur als Kontext,
nicht als Beweis.
