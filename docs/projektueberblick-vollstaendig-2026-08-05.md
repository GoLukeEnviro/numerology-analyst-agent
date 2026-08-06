# Numra — Vollständiger Projektüberblick

> **Dokumenttyp:** Umfassender Projektstatus- und Architekturbericht
> **Erstellt:** 2026-08-05
> **Sprache:** Deutsch
> **Basis:** Live-Zustand des Repos (main `9cc7e44`), `ROADMAP.md`, `PROJECT_CHARTER.md`,
> `docs/audit/current-state-numra-post-rc1-2026-08-02.md`, `whats-next.md`, GitHub-Issue-/PR-Status
>
> **Hinweis:** Dieses Dokument ist eine **Momentaufnahme**. Verbindlich bleiben
> `PROJECT_CHARTER.md`, `ROADMAP.md` und der Master-Vertrag
> `docs/governance/master-implementation-contract.md`.

---

## 1. Kurzprofil

| Kennzeichen | Wert |
|---|---|
| **Projekt** | Numra — `numerology-analyst-agent` |
| **Repository** | `GoLukeEnviro/numerology-analyst-agent` |
| **Mission** | Vom uneinheitlichen Fachgebiet → überprüfbares System → kontrollierter Agent (in genau dieser Reihenfolge) |
| **Positionierung** | Auditierbare Numerologie-Plattform: deterministischer, **LLM-freier** Rechenkern + FastAPI + lokale-first React/PWA |
| **Paketversion** | `0.3.0rc1` |
| **Aktueller Branch** | `main` |
| **Aktueller HEAD** | `9cc7e44` (synchron mit `origin/main`) |
| **Immutable Tag** | `v0.3.0-rc.1` → `21ba56ed…` |
| **Commits gesamt** | 44 |
| **Erster Commit** | `64536c2` (2026-07-24) |
| **License** | MIT |
| **Python** | 3.12+ |

---

## 2. Projektziel & Anti-Ziele

### Mission (Charter §1)

> Vom uneinheitlichen **Fachgebiet** zu einem überprüfbaren **System** zu einem
> kontrollierten **Agenten** — in genau dieser Reihenfolge, niemals umgekehrt.

Das System baut das bestehende GitHub-Repository zu einer vollständigen,
reproduzierbaren und erweiterbaren Plattform für **numerologische Berechnung,
strukturierte Deutung, Forschung, Evaluation und agentische Nutzung** aus.

### Drei Anti-Ziele (was das Projekt NICHT sein darf)

1. **Kein reines Prompt-Repository** — ein System-Prompt allein reicht nicht.
2. **Kein einfacher Numerologie-Rechner** — ohne Wissensmodell, Forschungsrahmen, Safety unvollständig.
3. **Keine lose Sammlung esoterischer Texte** — Deutungstexte ohne versioniertes Wissensmodell, Provenienz und Gegenhypothesen sind nicht akzeptabel.

---

## 3. Die fünf Ebenen der Plattform

| # | Ebene | Kurzbeschreibung | Was sie NICHT tut |
|---|-------|------------------|-------------------|
| 1 | **Fachmodell** | Numerologie als formal spezifiziertes Fachgebiet (Methoden, Claim-Taxonomie, Evidenzgrade) | Enthält keine Berechnungscodes |
| 2 | **Rechenkern** | Deterministischer, auditierbarer Berechnungsmotor (kein LLM, kein Netzwerk) | Enthält keine Deutungstexte |
| 3 | **Wissensmodell** | Versioniertes Wissens- und Interpretationsmodell (Zahlen, Meisterzahlen, Schatten, Gegenhypothesen) | Enthält keine Berechnungslogik |
| 4 | **Forschungsrahmen** | Empirischer Forschungs- und Evaluierungsrahmen (Hypothesenregister, Nullmodelle, Permutation, Power) | Bestätigt keine numerologischen Hypothesen |
| 5 | **App-Schicht** | Anwendungs-, API- und Agentenschicht (CLI, FastAPI, optionaler LLM-Adapter) | Erfindet keine Zahlen, überschreibt keine validierten Ergebnisse |

### Verarbeitungs-Pipeline

```text
Eingaben
  ↓
Normalisierung und Validierung
  ↓
Methoden- und Policy-Auswahl
  ↓
Deterministischer Rechenkern
  ↓
Auditierbares Berechnungsergebnis (Trace + Hash)
  ↓
Wissensauflösung
  ↓
Interpretationskomposition
  ↓
Safety-, Evidenz- und Aussageklassifizierung
  ↓
CLI / API / Agent / Bericht
```

---

## 4. Die sechs nicht verhandelbaren Aussageklassen

Jedes Dokument, Schema, jede API-Ausgabe, jeder Bericht und jeder Testfall
muss zwischen folgenden Klassen unterscheiden:

| # | Klasse | Bedeutung | Beispiel |
|---|--------|-----------|----------|
| 1 | `input_fact` | Vom Nutzer/Datensatz gelieferte Information | "Geburtsdatum: 1985-03-12" |
| 2 | `calculation_fact` | Deterministisch berechnetes Ergebnis | "Lebenswegzahl: 3 (Methode A, pythagorean-v1)" |
| 3 | `traditional_claim` | Überlieferte numerologische Bedeutung | "Die Zahl 7 gilt traditionell als Sucher nach Wahrheit" |
| 4 | `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation | "Häufung der 7 könnte auf Introversion hindeuten" |
| 5 | `empirical_evidence` | Ergebnis einer statistischen Untersuchung | "Permutationstest p = 0.42 — kein signifikanter Zusammenhang" |
| 6 | `practical_suggestion` | Nicht verbindliche Handlungsoption | "Praxis-Tipp: Reflektiere Zeiten bewusster Zurückgezogenheit" |

**Warum:** Ohne Trennung verschmilzt der Agent Tradition (unverifiziert),
Berechnung (deterministisch) und Deutung (hypothetisch) zu einer autoritären
Aussage, die nicht mehr falsifizierbar ist — unzulässig nach §2.3.

---

## 5. Architektur & Paketstruktur

### 5.1 Python-Pakete unter `src/` (8 Pakete, 46 Quelldateien)

| Paket | Dateien | Verantwortung | Regel |
|---|---|---|---|
| `numerology_domain` | 4 (+6 Modelle) | Verträge/Typen: `PersonInput`, `MethodPolicy`, `ProfileCalculationResult`, Schema-Versionen | Reine Datenmodelle (pydantic v2, `frozen=True`) |
| `numerology_engine` | 11 | Deterministischer Rechenkern (Normalisierung, Alphabet, Reduktion, Datumsalgorithmen, Zyklen, Trace) | **Kein Netzwerk, kein LLM, keine globale State, keine Randomness** |
| `numerology_knowledge` | 3 | Lädt/validiert versionierte Wissenspakete | Enthält keine Berechnungslogik |
| `numerology_interpretation` | 4 | Regelbasierte, rückverfolgbare Interpretationskomposition | Keine freie LLM-Erfindung als Kernfunktion |
| `numerology_safety` | 3 | Claims-/Sprach-/Prompt-Injection-Validierung | Setzt auf Rechenkern auf, nicht umgekehrt |
| `numerology_agent` | 8 (+Templates) | Dünner, optionaler LLM-Adapter (DeepSeek), Rate-Limiting, Mock-fähig | Darf validierte Ergebnisse nie überschreiben |
| `numerology_api` | 8 (6 Routen) | Zustandslose FastAPI-Grenze | Owns HTTP-Verträge, Middleware, Rate-Limit-Verdrahtung |
| `numerology_cli` | 2 | Typer-CLI (`profile`-Command) | Dünne Hülle über `numerology_engine` |

**API-Routen:** `health.py`, `meta.py`, `profiles.py`, `cycles.py`, `analyses.py`.

**Import-Reihenfolge (verbindlich):**
`domain → engine → knowledge → interpretation → safety → agent → api/cli`.
Keine zyklischen Abhängigkeiten. `ruff.lint.isort` mit `known-first-party` erzwingt das.

### 5.2 Web/PWA (`apps/web`)

- **Stack:** React + Vite + TypeScript (strict) + Vitest + Playwright, pnpm-Workspace
- **Feature-Slices:** `profile`, `analysis`, `report`, `export`
- **`api/`:** generierter OpenAPI-Client (`schema.d.ts`, nicht editieren) + `client.ts`
- **`storage/`:** lokale IndexedDB-Persistenz (Dexie) inkl. optionaler PBKDF2-/AES-GCM-Verschlüsselung
- **`pwa/`:** Service-Worker-Update-Handling (Workbox), offline-lesend
- **Tests:** 11 unit/vitest, 1 E2E-Spec (`profile-flow.spec.ts`)

### 5.3 Wissenspakete

- `src/numerology_knowledge/data/de-v1.json` — versioniertes, schema-validiertes deutsches Wissenspaket
- `src/numerology_knowledge/data/de-v2.json` — V2-Wissensmodell (ab RC1)

---

## 6. Deterministischer Kern (bindendes Prinzip)

**Determinismus vor LLM — alle Berechnungen funktionieren ohne Sprachmodell.**

Ein LLM darf **ausschließlich**:
- validierte Ergebnisse erklären,
- Deutungshypothesen formulieren,
- Ausgaben sprachlich anpassen.

Ein LLM darf **niemals**:
- Zahlen selbst (unkontrolliert) berechnen,
- fehlende Daten erfinden,
- Methodenversionen vermischen,
- validierte Rechenergebnisse überschreiben.

**Code-Konsequenz:** kein `import openai` / `anthropic` / `requests` in
`src/numerology_engine/`. Netzwerk-/LLM-Zugriff im Rechenkern ist ein harter Verstoß.

### Determinismus- und Hash-Vertrag

- Alle Domain-Modelle immutable (`pydantic` v2, `frozen=True`); Serialisierung
  mit `sort_keys=True` → identischer Input + Policy ⇒ byte-identisches JSON.
- Jede Berechnung trägt `deterministic_hash` (SHA-256) über ein
  `CalculationHashEnvelope` (Schema-Version, Eingaben, Policy, Ergebnisse, Trace).
  `consent_given` ist explizit vom Hash ausgeschlossen.
- `--as-of-date` an CLI und API **verpflichtend** → Läufe unabhängig vom Systemdatum reproduzierbar.
- Aktueller Rechenkern-Vertrag: `profile-calculation-result-v3`.
- Golden-Cases (`tests/golden/`) sind **gepinnte Referenzwerte** — Änderungen = Vertragsbruch.

---

## 7. Technologie-Stack

| Schicht | Technologie | Regel |
|---------|-------------|-------|
| Sprache | **Python 3.12+** | Keine veraltete Syntax |
| Abhängigkeiten / Venv | **`uv`** | Reproduzierbar, `uv.lock` ist Quelle der Wahrheit |
| Verträge / Validierung | **`pydantic` v2** | Strikte Modelle |
| Unit-Tests | **`pytest`** | Standard |
| Property-Tests | **`hypothesis`** | Pflicht für Reduktion, Trace, Invarianten |
| Lint + Format | **`ruff`** | Strikt |
| Typen | **`mypy` strict** | Keine `any`, kein ungerechtfertigtes `# type: ignore` |
| HTTP-API | **FastAPI** | OpenAPI generiert |
| CLI | **Typer** | Typisiert |
| Wissenspakete | **YAML / validiertes JSON** | Schema-validiert |
| Forschungsdaten | DuckDB + Parquet | (Phase 7, noch nicht gestartet) |
| Doku | **MkDocs Material** | optional/separat (PARTIAL) |
| CI | **GitHub Actions** (ci.yml, codeql.yml) | Pflicht-Checks |
| Versionierung | **SemVer** | Klar, maschinenlesbar |
| Frontend | React/Vite/TS + Vitest + Playwright, pnpm | Local-first PWA |

**Explizit NICHT im Basiskern:** keine Datenbank, kein Vektorstore, kein LLM-Framework.

---

## 8. Test- & Qualitätslandschaft

### Python-Tests (36 Test-Dateien)

| Bereich | Anzahl Dateien | Zweck |
|---|---|---|
| `tests/unit/` | 22 | Unit-Tests für Business-Logik |
| `tests/golden/` | 5 | Gepinnte Referenzwerte (Profile, Hash, V2) |
| `tests/property/` | 5 | Hypothesis Property-Based Tests |
| `tests/integration/` | 6 | API-/Datenbank-/Service-Interaktionen |
| `tests/deployment/` | 3 | Deployment-Smoke |

### Quality Gates (Pflicht vor Merge)

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests scripts        # strict
uv run pytest --cov=src/numerology_engine --cov-fail-under=95   # Core-Gate
uv run pytest --cov=src --cov-fail-under=85                     # Gesamt-Gate
uv run pip-audit                     # Dependency-Security
```

Äquivalente `Makefile`-Targets: `make lint`, `make typecheck`, `make test`,
`make test-cov-core`, `make test-cov-total`, `make all`.

Schema-/OpenAPI-/Beispiel-Export (müssen `--check`-reproduzierbar bleiben):
`scripts/export_schemas.py`, `scripts/export_openapi.py`, `scripts/generate_examples.py`.

### Web-Gates (pnpm)

```bash
pnpm web:lint           # eslint --max-warnings 0
pnpm web:typecheck      # tsc -b
pnpm web:test           # vitest run
pnpm web:build          # tsc -b && vite build
pnpm web:e2e            # playwright test
pnpm web:check-build    # scripts/check-build.mjs
```

### Determinismus-Matrix

- Frische Gates 2026-08-02 auf `5976ae2`: **PASS** (Python, Determinismus-Matrix mit 6 Seeds, Web inkl. E2E, Container, Remote-CI/CodeQL).

---

## 9. Release-Historie & Status

### Veröffentlichte Releases / Meilensteine

| Release | Titel | Status |
|---------|-------|--------|
| **0.1.3** | Contract Integrity | ✅ Tag `v0.1.3` @ `9c50f4d` |
| **0.1.4** | Complete Core Profile | ✅ auf `main` (kein eigener Tag) |
| **0.1.5** | Deterministic Cycles | ✅ auf `main` (kein eigener Tag) |
| **0.2.x-Umfang** | Knowledge + Interpretation | ✅ auf `main` (kumulativ in RC1) |
| **0.3.0-rc.1** | Integration Closure | ✅ Tag `v0.3.0-rc.1` @ `21ba56ed…` (immutable) |
| **post-RC1 main** | Ship-Hygiene #34 + Audit #35 | ✅ `5976ae2`, Version bleibt `0.3.0rc1` |
| **0.3.0-rc.2** | Staging-bewiesener RC | ❌ **nächster** Code-Release — **BLOCKED_BY_STAGING** |
| **0.3.0 (stable)** | Stable nach Closed Beta | ❌ nach RC2 + Beta; P0/P1 = 0 |
| **Research / V2** | Research Preview + Guided Masterplan | ❌ **DEFERRED** bis stable 0.3.0 + ADR |

### Phasen-Statusmatrix (Master-Vertrag Phase 0–14)

| Phase | Titel | Zustand |
|-------|-------|---------|
| 0 | Reality Check | **COMPLETE** |
| 1 | Governance | **COMPLETE** (Committee als Artefakt-Flow noch **NOT_STARTED**) |
| 2 | Tooling | **COMPLETE** (MkDocs Material **PARTIAL**) |
| 3 | Methodenspezifikation | **COMPLETE** |
| 4 | Rechenkern | **COMPLETE** |
| 5 | Wissensmodell | **COMPLETE** |
| 6 | Interpretation | **COMPLETE** |
| 7 | Forschung | **NOT_STARTED** |
| 8 | Safety/Privacy | Code **COMPLETE**; Rechtsfreigabe **EXTERNALLY_BLOCKED** |
| 9 | CLI/API/Berichte | **COMPLETE** |
| 10 | Agent | **COMPLETE** (fail-closed, LLM default off) |
| 11 | Evaluation | **COMPLETE** |
| 12 | Dokumentation | **PARTIAL** (Staging-Bericht offen) |
| 13 | Committee Review | **COMPLETE** — Entscheidung `NO_GO`, Betriebsabnahme `BLOCKED_BY_STAGING` |
| 14 | Release | RC1 **COMPLETE**; RC2 **BLOCKED_BY_STAGING**; Stable **NOT_STARTED** |

### Was NICHT bewiesen ist (reale Betriebsleistung)

| Thema | Status |
|-------|--------|
| Privates Staging auf bestätigtem Host | **NOT_EXECUTED** |
| Echter Provider-/LLM-Smoke (Legal/Transfer/Secret) | **BLOCKED** / optional |
| Verschlüsseltes Config-Backup + Restore | **PASS (lokal)** |
| Rollback-Rehearsal | **PASS (lokal)** |
| Committee Release Review | **COMPLETE**, Entscheidung **NO_GO** |
| Closed Beta | **NOT_STARTED** |
| Stable `v0.3.0` | **NOT_STARTED** |
| Öffentlicher Launch | **NO_GO** |

---

## 10. GitHub-Issues & PRs

### Offene Issues (Stand 2026-08-05)

| # | Titel | Priorität |
|---|-------|-----------|
| **37** | [EPIC] Numra v0.3.0-rc.2 → Stable v0.3.0 | — |
| 39 | Private staging environment and deployment evidence | P1 |
| 40 | Backup restore and rollback rehearsal | P1 |
| 41 | Provider and API end-to-end smoke | P1 |
| 43 | Accessibility and cross-device beta matrix | P1 |
| 44 | Committee release review | P1 |
| 45 | Prepare v0.3.0-rc.2 | P1 |
| 46 | Closed beta acceptance | P1 |
| 47 | Prepare stable v0.3.0 | P1 |
| 48 | Public launch external gates | P2 |

### Kürzlich gemergte PRs

| PR | Titel | Datum |
|----|-------|-------|
| #55 | RC2-Vorarbeiten: CQ-001, OPS-001/002, Committee-Status, Rehearsal, Gate-Protokoll | 2026-08-04 |
| #54 | Projektdiagnose, ARCH-001/TEST-001-Fixes, Security-Patches | 2026-08-04 |
| #53 | docs: V2/V3 Full-Analysis-Architekturplan einfrieren | 2026-08-03 |
| #52 | feat: RemixIcon für PDF-Export-Button | 2026-08-02 |
| #51 | fix(deploy): SHA-compatible rollback rehearsal | 2026-08-02 |
| #50 | docs: RC2 dependency decision and blocked staging preflight | 2026-08-02 |
| #36 | docs: reconcile post-RC1 repository state and release roadmap | 2026-08-02 |
| #35 | docs: consolidate post-RC1 audit and OpenAPI artifacts | 2026-08-02 |
| #34 | chore: Ship-Hygiene nach RC1 (Gates, Modularisierung, #32) | 2026-08-02 |

---

## 11. Architektur-Entscheidungen (ADRs, 17 Stück)

| ADR | Thema |
|-----|-------|
| 0001 | Y-Rule phonetisch |
| 0002 | Unicode-/Umlaut-Normalisierung (de, direkt, V1) |
| 0003 | Mehrfachnamen & Bindestriche |
| 0004 | Core-Name vs. aktiver Name |
| 0005 | Aktuelles Package-Layout & Schema-Quelle |
| 0006 | Operative Release-Sequenzierung |
| 0007 | Numra-PWA-Architektur |
| 0008 | Nur-lokale personenbezogene Daten |
| 0009 | LLM-Provider-Grenze |
| 0010 | Lokaler verschlüsselter Speicher |
| 0011 | PWA-Cache, Theme & PDF-Export |
| 0012 | Security- & Privacy-Grenze |
| 0013 | Container & privates Staging |
| 0014 | Kontrollierter öffentlicher Launch |
| 0015 | Kumulative Release-Normalisierung |
| 0016 | V2-User-owned Masterplan-Grenze |
| 0017 | V2-Parallel-Anbindung-Sequenz |

---

## 12. Container & Deployment

### Compose-Dateien
- `compose.yaml` — Standard-Stack
- `compose.llm-staging.yaml` — LLM-Staging-Variante

### Docker
- `docker/api.Dockerfile`, `docker/web.Dockerfile`
- `docker/nginx/` — `default.conf`, `security-headers.conf`

### Deploy-Skripte (`deploy/scripts/`)
`preflight.sh` · `stage.sh` · `release.sh` · `rollback.sh` · `rollback-rehearsal.sh`
· `backup-config.sh` · `restore-config.sh` · `build-release-image.sh`
· `api-smoke.sh` · `provider-smoke.sh` · `public-launch-check.sh` · `enable-https.sh`

### Container-Smoke (lokal)
```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait
curl --fail http://127.0.0.1:8080/api/v1/health/ready
docker compose down
```

### FastAPI-App (`src/numerology_api/app.py`)
`create_app()` ist eine Factory (kein globaler State außer Modul-Level `app`).
Middleware-Kette (Reihenfolge relevant): `OriginValidationMiddleware` →
`RequestBodyLimitMiddleware` → `AccessLogMiddleware` → `CORSMiddleware` →
`SecurityHeadersMiddleware` → `CorrelationIdMiddleware`.

- **LLM-Endpunkte** (`/api/v1/analyses/*`) nur aktiv wenn `NUMRA_LLM_ENABLED=true`.
  Sie verifizieren eingehende Profile gegen eine neu berechnete kanonische Version
  (`canonical_analysis_profile`) — Clients können Profile nicht fälschen.
- **Rate-Limiting** läuft über Redis, ausschließlich HMAC-pseudonymisierte Keys
  (`pseudonymous_key`), nie Klartext-IP/Device-ID.

---

## 13. Sicherheitslage

- **`react-router` GHSA-qwww-vcr4-c8h2 (HIGH):** in CI via
  `pnpm auditConfig.ignoreGhsas` geführt; Patch ≥8.3.0 ist Major-Risiko →
  gehört in den RC2 Security-Stream (kein stilles Major-Upgrade ohne E2E).
- **Python `pip-audit`:** keine bekannten CVEs (Messung 2026-08-02 auf main).
- **pnpm-Overrides:** `brace-expansion`, `js-yaml`, `fast-uri` (Transitiv-Härtung).
- **Secrets/PII:** keine im Repository; `.env` in `.gitignore`; Secret Scanning 0 Alerts (Stand 2026-07-27).
- **DeepSeek-Adapter:** pseudonymisiert (keine Namen/Geburtsdaten im Payload),
  standardmäßig deaktiviert (`llm_enabled=False`), kein API-Key im Repo.

---

## 14. Harte Grenzen (unverhandelbar)

- Kein Vermischen von Methodenversionen (nur `pythagorean-v1` in V1; chaldäische/kabbalistische Werte = Verunreinigung).
- Keine stillen Defaults außerhalb der kanonischen Konfiguration.
- Keine erfundenen Daten (insbesondere `empirical_evidence` ohne statistischen Nachweis).
- Keine Diagnosen (medizinisch, psychologisch, identitätsstiftend).
- Keine garantierte Zukunft in Interpretationen.
- Keine starre Identitätszuschreibung bei Minderjährigen.
- Keine privaten personenbezogenen Daten im Repository.
- Keine Secrets/API-Keys/Tokens in Code, Config, Tests, Commits, Logs.
- Keine leeren Placeholder, die Fertigkeit vortäuschen.
- **Kein LLM-/Netzwerkzugriff im Rechenkern** (`numerology_engine`).
- Kein Direct-/Force-Push auf `main`, kein `--no-verify`.
- Tag `v0.3.0-rc.1` niemals bewegen.
- Keine V2-/Research-/Platform-Implementierung vor stable 0.3.0 + ADR.

---

## 15. Kritischer Pfad / Nächste Schritte

```text
Repository-Wahrheit (docs) aktualisieren
→ main frisch verifiziert (done 2026-08-02)
→ private Staging-Abnahme (NUMRA_LLM_ENABLED=false)        ← EINZIGER BLOCKER
→ Backup create + validate + restore + re-smoke
→ Rollback-Rehearsal (baseline → candidate → rollback → redeploy)
→ Committee Review (5 Perspektiven)
→ release/v0.3.0-rc.2 taggen + GitHub-Prerelease
→ Closed Beta (P0/P1 = 0)
→ stable v0.3.0
→ Public Deploy separat GO|NO_GO
→ ADR Post-0.3 Sequenz (V2 erst danach)
```

### Unmittelbare nächste sinnvolle Einzelmaßnahme

1. **[P1]** Betreiber bestätigt **einen** Numra-Staging-SSH-Alias; Preflight
   (`deploy/scripts/preflight.sh`) und deterministisches Deploy des aktuellen main-SHA.
2. Parallel (max. 3 Streams, nur nach grünem main): Security-Entscheidung zu
   `react-router` GHSA, a11y/Geräte-Matrix, Ops-Readiness-Doku.

### Zustandssperre (solange kein Host-Proof)

```text
RELEASE_DECISION=NO_GO
OPERATIONAL_ACCEPTANCE=BLOCKED_BY_STAGING
RC2_RELEASED=NO
```

---

## 16. V2-Parallel-Strang (ADR 0017)

Full Analysis V2/V3 darf **parallel und isoliert** vorbereitet werden:
- ausschließlich unter `/api/v2`,
- hinter Feature Flag,
- `/api/v1` unverändert, kein V1-Schema-Drift,
- kein automatischer Default-Switch,
- Guided Masterplan bleibt bis Stable v0.3.0 gesperrt,
- keine Research-Preview-Erweiterung,
- kein V2-Merge auf `main` solange Strang A (RC2) offen ist.

Wegen der **harten Sequenzregel** gilt: **Guided Masterplan ist nicht die
aktuelle Implementierung** (ADR 0016); erst nach stable 0.3.0 + Sequenz-ADR.

---

## 17. API-Referenz (v1, Detail)

### 17.1 Übersicht der Endpunkte

| Methode | Pfad | Router | Beschreibung |
|---------|------|--------|--------------|
| `GET` | `/api/v1/health/ready` | `health.py` | Readiness-Probe (Container-Smoke) |
| `GET` | `/api/v1/meta` | `meta.py` | Metadaten (Version, Methoden, Schema-Versionen) |
| `POST` | `/api/v1/profiles/calculate` | `profiles.py` | Deterministische Profilberechnung (pythagorean-v1) |
| `POST` | `/api/v1/analyses/report` | `analyses.py` | LLM-Bericht (nur wenn `NUMRA_LLM_ENABLED=true`) |
| `POST` | `/api/v1/analyses/follow-up` | `analyses.py` | LLM-Follow-up (nur wenn LLM aktiv) |
| `cycles` | (reserviert) | `cycles.py` | Absichtlich leer — Zyklen sind Teil des Profils |

### 17.2 `POST /api/v1/profiles/calculate`

```json
{
  "person": {
    "core_name": "Max Mustermann",
    "birth_date": "1985-07-25",
    "active_name": "Max M.",
    "as_of_date": "2026-07-26"
  },
  "policy": { "version": "pythagorean-v1" }
}
```

**Schutz vor Methodenvermischung:** Falls `policy.version != pythagorean-v1`,
liefert der Endpunkt stabil `422 METHOD_VERSION_MISMATCH` (ProblemDetails),
statt ein v1-Ergebnis mit v2-Policy im Envelope zu mischen. Antwortmodell:
`ProfileCalculationResult`.

### 17.3 `POST /api/v1/analyses/*` (LLM, fail-closed)

- **Aktiv nur** wenn `NUMRA_LLM_ENABLED=true` und Provider/Rate-Limiter/Circuit-Breaker initialisiert.
- Sonst `503 llm_disabled_response`.
- **Integritäts-Check:** eingehendes `profile` wird gegen eine **frisch
  berechnete kanonische Version** (`canonical_analysis_profile`) verifiziert —
  Clients können Profile nicht fälschen, um den Agent zu manipulieren.
- **Rate-Limits** (HMAC-pseudonymisierte Keys): `device-report` (Limit 1/Scope),
  Follow-up entsprechend; Überlauf → `429`.
- **Resilience:** Circuit-Breaker + Analyse-Fehlerklassifikation → `503`.

### 17.4 Fehlerformat (ProblemDetails, RFC 7807)

- Basis-URI: `PROBLEM_BASE` (siehe `numerology_api/problem_details.py`)
- Felder: `type`, `title`, `status`, `code`, `detail`, `correlation_id`
- Kontexte: `400` (Rejected), `422` (Validation/Method-Version), `429` (Rate),
  `503` (LLM disabled/generation error)

---

## 18. CLI-Referenz (`numerology` / Typer)

### 18.1 Command `profile`

```bash
numerology profile --name "Max Mustermann" --birth 1985-07-25 --as-of-date 2026-07-26
```

| Option | Kurz | Pflicht | Bedeutung |
|--------|------|---------|-----------|
| `--name` | `-n` | ✅ | Vollständiger Geburtsname (`core_name`) |
| `--birth` | `-b` | ✅ | Geburtsdatum als ISO `YYYY-MM-DD` |
| `--active-name` | — | — | Aktuell verwendeter Name (optional) |
| `--as-of-date` | — | ✅ | Verpflichtendes Bewertungsdatum; `birth <= as_of` |

### 18.2 Eigenschaften

- **Ausgabe:** kanonisches, key-sortiertes JSON auf stdout (Determinismus: identischer
  Input ⇒ byte-identischer Output).
- **Fehler:** stderr + Non-Zero-Exit-Code.
- **Version:** dynamisch aus Paket-Metadaten gelesen (kein Hardcode-Drift); Fallback `0.0.0+dev`.
- **Datums-Strikt:** `date.fromisoformat` weist nicht-null-padded Daten ab
  (z. B. `1985-7-5`) — determinismuskorrekt.
- `--as-of-date` ist verpflichtend (v0.1.3 Contract Integrity) — `date.today()`
  würde Reproduzierbarkeit brechen.

---

## 19. Paketinternes Modul-Inventar

### 19.1 `numerology_engine` (Rechenkern, 11 Module)

| Modul | Verantwortung |
|-------|---------------|
| `alphabet.py` | Buchstaben-Wertetabelle (pythagoreisch) |
| `normalization.py` | Namens-/Unicode-Normalisierung |
| `reduction.py` | Zahlenreduktion (Quersummen, Meisterzahlen) |
| `numbers.py` | Zahlenwerte (Lebensweg, Ausdruck, etc.) |
| `dates.py` | Datumsalgorithmen |
| `cycles.py` | Persönliche Jahre/Monate/Tage, Pinnacles, Challenges |
| `profile.py` | Komplette Profilberechnung (v1) |
| `profile_v2.py` | Profilberechnung (V2-Wissensmodell) |
| `service.py` | Berechnungsservice / Orchestrierung |
| `trace.py` | Audit-Trace-Erfassung |
| `__init__.py` | Paket-Exporte |

### 19.2 `numerology_domain/_models` (6 Module)

`base.py` · `input.py` (`PersonInput`) · `calculation.py` (`ProfileCalculationResult`,
Hash-Envelope) · `cycles.py` · `profile.py` · `__init__.py` — alles `frozen=True`-Pydantic.

### 19.3 `numerology_agent` (8 Module)

| Modul | Verantwortung |
|-------|---------------|
| `provider.py` | Provider-Abstraktion |
| `deepseek.py` | DeepSeek-Adapter (JSON-Output, Thinking) |
| `models.py` | `AnalysisReport`, `AnalysisFollowUp` |
| `prompts.py` | Prompt-Konstruktion |
| `rate_limit.py` | Rate-Limiting (HMAC-pseudonymisiert) |
| `resilience.py` | Circuit-Breaker, Retry |
| `service.py` | Agent-Service (generiert Berichte/Follow-ups) |
| `prompt_templates/` | System-/Task-/Eval-Templates |

### 19.4 `numerology_knowledge` (3 Module)

`loader.py` (Laden) · `models.py` (Schema-Modelle) · `__init__.py`. Daten:
`data/de-v1.json` (8,7 KB), `data/de-v2.json` (66,3 KB).

### 19.5 `numerology_interpretation` (4 Module)

`models.py` · `rules.py` (regelbasierte Komposition) · `service.py` · `__init__.py`.

### 19.6 `numerology_safety` (3 Module)

`validation.py` (Claims-/Sprach-Validierung) · `runtime_gate.py` (Datei-Marker-Gates) · `__init__.py`.

---

## 20. Runtime-Sicherheitsgates (LLM-Produktion)

Die Datei-Marker-Gates verlangen **vor** LLM-Operationen in Produktion:

```text
/etc/numra/numra-legal-approved      → existiert, root:root, Mode 0600
/etc/numra/llm-transfer-approved     → existiert, root:root, Mode 0600
```

- `GateResult`: `exists` + `owner_correct` + `permissions_correct`.
- `RuntimeGateResult.all_passed` ist `True` nur wenn **beide** Gates bestehen
  (oder auf nicht-relevanter Plattform übersprungen).
- `failure_reasons` listet die verletzten Gates für Debugging.
- Damit ist die rechtliche Freigabe und der Drittlandtransfer (DeepSeek)
  **technisch erzwungen**, nicht nur dokumentiert.

---

## 21. Web-App-UI im Detail

### 21.1 Feature-Slices & Komponenten

| Feature | Komponenten / Tests |
|---------|---------------------|
| `profile` | `NumberAtlas.tsx` (+Test), `ExpertDetails.tsx`, `ProfileActions.tsx` |
| `analysis` | `AnalysisWizard.tsx` (+Test) |
| `report` | `ReportExperience.tsx` (+Test) |
| `export` | PDF-Export (RemixIcon, ADR 0011) |

### 21.2 Weitere Struktur

- `api/` — generierter Client (`schema.d.ts`, `client.ts`); Regenerierung via
  `pnpm web:generate-api` aus `openapi/numra-v1.json` (nicht von Hand editieren).
- `storage/` — IndexedDB (Dexie) + optionale PBKDF2-/AES-GCM-Verschlüsselung (ADR 0010, 0012).
- `pwa/` — Service-Worker-Update-Handling (Workbox, ADR 0007, 0011).
- `test/` — Test-Setup/Harness.
- `e2e/profile-flow.spec.ts` — Playwright End-to-End-Flow.

---

## 22. Docker-Build-Detail

### 22.1 `docker/api.Dockerfile` (Multi-Stage)

1. **Builder** (`ghcr.io/astral-sh/uv:0.9.26-python3.12-bookworm-slim`, pinned SHA):
   - `uv sync --locked --no-dev --no-editable` (Bytecode-Kompilierung, Link-Mode copy).
   - Kopiert nur `pyproject.toml`, `uv.lock`, `README.md`, `src/` — reproduzierbar.
2. **Runtime** (`python:3.12.11-slim-bookworm`, pinned SHA):
   - Dedizierter nicht-privilegierter User `numra` (UID/GID `10001`).
   - `.venv` wird vom Builder mit `--chown=10001:10001` kopiert.
   - `USER 10001:10001` — **kein Root im Container**.
   - `EXPOSE 8000`; CMD `uvicorn ... --proxy-headers --forwarded-allow-ips=172.30.0.10`.

### 22.2 `docker/web.Dockerfile` & `docker/nginx/`

- Nginx-Server mit `security-headers.conf` (Sicherheits-Header).
- `deploy/nginx/numra-http/https.conf.template` — HTTPS-Template für Launch.

### 22.3 Compose-Varianten

- `compose.yaml` — Standard (API + Web + Nginx + Redis).
- `compose.llm-staging.yaml` — LLM-Staging-Variante (Provider).

---

## 23. Vollständiges Test-Inventar

### 23.1 `tests/unit/` (22 Dateien)

`test_agent` · `test_alphabet` · `test_calculation_v2` · `test_contracts` ·
`test_cycles` · `test_dates` · `test_deepseek_provider` · `test_domain_models_v2` ·
`test_hash_contract` · `test_interpretation` · `test_knowledge_v2` · `test_knowledge` ·
`test_normalization` · `test_profile_calculation` · `test_prompts` · `test_rate_limit` ·
`test_reduction` · `test_resilience` · `test_rules` · `test_runtime_gate` · `test_safety`.

### 23.2 `tests/property/` (4 Test-Dateien + 5 Dateien gesamt)

`test_determinism_matrix` · `test_profile_properties` · `test_reduction_properties` ·
`test_v2_determinism` — Hypothesis Property-Based Tests.

### 23.3 `tests/golden/` (4 Test-Dateien + Cases)

`test_golden_cases` · `test_hash_golden` · `test_profile_golden_v2` · `test_profile_golden`
+ Referenzdaten `cases.yaml`, `profile_cases.yaml`, `reference_profiles_v2.yaml`.

### 23.4 `tests/integration/` (6 Dateien)

`test_analysis_api` · `test_cli` · `test_deepseek_live_smoke` · `test_http_api` ·
`test_production_graph` (Dependency-Graph-/Zyklus-Prüfung).

### 23.5 `tests/deployment/` (3 Dateien)

`test_launch_contract` · `test_stack_contract` — Deploy-/Launch-Verträge.

### 23.6 Marker (pyproject)

`golden` · `integration` · `property` · `unit` — Filterung z. B. `pytest -m golden`,
`pytest -m property`.

---

## 24. Kernzahlen (erweitert)

| Metrik | Wert |
|--------|------|
| Python-Pakete | 8 |
| Python-Quelldateien (src) | ~46 |
| Engine-Module | 11 |
| Agent-Module | 8 |
| Domain-Modelle | 6 |
| API-Routen | 5 aktiv + 1 reserviert (cycles) |
| ADRs | 17 |
| Web-Features | 4 (profile, analysis, report, export) |
| Web-UI-Komponenten (tsx) | 7 + Tests |
| Vitest-Tests | 11 |
| E2E-Specs | 1 (`profile-flow`) |
| Unit-Test-Dateien | 22 |
| Property-Test-Dateien | 4 |
| Golden-Test-Dateien | 4 (+3 Referenz-YAML) |
| Integrations-Test-Dateien | 6 |
| Deployment-Test-Dateien | 3 |
| Wissenspakete | de-v1 (8,7 KB), de-v2 (66,3 KB) |
| Deploy-Skripte | 12 |
| Runtime-Gates | 2 Datei-Marker (legal + LLM-Transfer) |
| Docker-User | nicht-privilegiert (UID 10001) |
| Commits | 44 |
| Gemergte PRs (neueste 10) | 10 |
| Offene Issues | 10 |

---

## 25. Quellenverzeichnis

- `PROJECT_CHARTER.md` — Was/Warum von V1
- `ROADMAP.md` — 15 Phasen (0–14) mit Gates, Release-Strategie
- `docs/audit/current-state-numra-post-rc1-2026-08-02.md` — frische Repository-Wahrheit
- `docs/audit/current-state-numra-rc.md` — RC-Vorbereitung (historisch)
- `docs/releases/v0.3.0-rc.1.md`, `v0.1.3.md`, `unreleased-numra.md`
- `docs/operations/rollback-rehearsal-local-2026-08-04.md` — lokaler Restore/Rollback-Nachweis
- `docs/committee/rc2-*.md` — Committee Review (Entscheidung NO_GO)
- `docs/operations/launch-checklist.md` — Launch-Gates
- `whats-next.md` — Handoff post-RC1 → RC2 / Stable
- `plans/state-reconciliation-pr-plan.md` — State-Reconciliation (untracked)
- `CHANGELOG.md` — schlanker Release-Index
- `pyproject.toml` — Stack, Gates, Ruff/Mypy/Pytest-Konfiguration
- `package.json` — pnpm-Workspace, Overrides, GHSA-AuditConfig
- `src/numerology_api/routes/*.py` — API-Referenz (health, meta, profiles, cycles, analyses)
- `src/numerology_cli/main.py` — CLI-Referenz
- `src/numerology_engine/*.py` — Rechenkern-Modul-Inventar
- `src/numerology_agent/*.py` — Agent-/Provider-/Rate-Limit-Module
- `src/numerology_safety/runtime_gate.py` — Datei-Marker-Gates
- `docker/api.Dockerfile` — Multi-Stage-Build, nicht-privilegierter User
- `compose.yaml` / `compose.llm-staging.yaml` — Compose-Varianten
- `tests/*` — Vollständiges Test-Inventar

---

*Ende des Berichts — Momentaufnahme vom 2026-08-05.*
