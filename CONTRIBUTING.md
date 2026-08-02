# Contributing — Numra (Numerology Analyst Agent)

> **Sprache:** Deutsch (Fachbegriffe auf Englisch, wo idiomatisch).
> **Stand:** 2026-08-02 — abgestimmt auf `v0.3.0-rc.1`.

Danke für dein Interesse an Numra. Dieses Dokument beschreibt, wie du
reproduzierbar entwickelst, welche Regeln für Branches, Commits und Pull
Requests gelten und welche fachlichen und sicherheitsrelevanten Grenzen
absolut verbindlich sind.

---

## 1. Grundprinzipien

1. **Determinismus vor LLM.** Alle Berechnungen funktionieren vollständig ohne
   Sprachmodell. Ein LLM darf ausschließlich validierte Ergebnisse erklären,
   Deutungshypothesen formulieren und Ausgaben sprachlich anpassen — niemals
   Zahlen berechnen, Daten erfinden, Methodenversionen vermischen oder
   validierte Rechenergebnisse überschreiben.
2. **Keine fachliche Berechnung im LLM.** Der Rechenkern
   (`numerology_engine`) ist pure, deterministische Logik ohne Netzwerk- und
   LLM-Zugriff. Der LLM-Adapter (`numerology_agent`) ist eine dünne,
   fail-closed validierte Schicht über validierten Services.
3. **Aussageklassen strikt trennen.** Jede Aussage gehört zu genau einer der
   sechs Klassen (`input_fact`, `calculation_fact`, `traditional_claim`,
   `interpretive_hypothesis`, `empirical_evidence`, `practical_suggestion`).
   Diese Trennung muss in Code, Schemas, API-Ausgaben, Berichten und Tests
   sichtbar sein.
4. **Keine Diagnosen, keine garantierte Zukunft.** Das Projekt gibt keine
   medizinischen, psychologischen oder sonstigen diagnostischen Aussagen ab.
5. **Lokal-first und Datenschutz.** Persönliche Daten bleiben lokal
   (IndexedDB, optional PBKDF2-/AES-GCM-verschlüsselt). Keine privaten
   personenbezogenen Daten im Repository.

---

## 2. Setup

Voraussetzungen: Python 3.12+, [`uv`](https://docs.astral.sh/uv/),
Node.js gemäß `.node-version`, pnpm 10.22.

```bash
# Python-Abhängigkeiten (inkl. dev-Gruppe, mit Lock-Vertrag)
uv sync --locked --all-groups

# Frontend-Abhängigkeiten (mit Lockfile)
pnpm install --frozen-lockfile
```

### Lokale Entwicklung

```bash
# Terminal 1: API
uv run uvicorn numerology_api.app:app --reload --port 8000

# Terminal 2: PWA
pnpm --filter @numra/web dev
```

Die PWA läuft anschließend unter `http://localhost:5173`.

---

## 3. Branch- und PR-Regeln

### Branch-Namen

| Präfix   | Verwendung                          |
| -------- | ----------------------------------- |
| `feature/*`  | Neue Funktionalität            |
| `fix/*`      | Fehlerbehebung                 |
| `refactor/*` | Strukturverbesserung ohne Verhaltensänderung |

Beispiele: `feature/v2-knowledge-bundle`, `fix/abort-race`,
`refactor/export-schemas`.

### Regeln

- **Keine Direktpushes auf `main`.** Jede Änderung läuft über einen Pull
  Request.
- **Kein Force-Push** auf geteilte Branches.
- **Kein `--no-verify`.** Pre-Commit- und CI-Checks dürfen nicht umgangen
  werden.
- **Ein PR = ein fokussiertes Thema.** Kleine, reviewbare PRs sind besser als
  große Sammel-PRs.
- **PR-Beschreibung** erklärt das *Warum* und referenziert betroffene
  Verträge, ADRs oder Issues.
- **CI muss grün sein**, bevor ein PR gemergt wird.

---

## 4. Quality Gates

Alle folgenden Gates müssen lokal und in CI grün sein:

```bash
# Python
uv lock --check
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests scripts
uv run pip-audit
uv run pytest --cov=src/numerology_engine --cov-fail-under=95
uv run pytest --cov=src --cov-fail-under=85

# Schema- und OpenAPI-Drift (siehe Abschnitt 6)
uv run python scripts/export_schemas.py --check
uv run python scripts/export_openapi.py --check
uv run python scripts/generate_examples.py --check
uv run python scripts/validate_knowledge.py

# Frontend
pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2
pnpm web:lint
pnpm web:typecheck
pnpm web:test
pnpm web:build
pnpm web:check-build
pnpm web:e2e

# Container
docker compose config --quiet
```

**Coverage-Ziele:** Rechenkern ≥ 95 %, Gesamtabdeckung ≥ 85 %.

---

## 5. Determinismus-vor-LLM-Prinzip

- Der Rechenkern ist **pure functions**: keine globale State, keine
  Randomness, keine Zeitabhängigkeit. `--as-of-date` ist verpflichtend und
  macht Läufe reproduzierbar.
- Serialisierung immer mit `sort_keys=True`; identischer Input ergibt
  byte-identisches JSON und identischen SHA-256-Hash.
- Der Hash umfasst das CalculationHashEnvelope (Schema, fachlich relevante
  Eingaben, Policy, Ergebnisse, Trace). `consent_given` ist ausgeschlossen.
- **Kein Netzwerk- oder LLM-Zugriff im Rechenkern.** Der LLM-Adapter darf
  validierte Ergebnisse nicht überschreiben und keine fehlenden Daten
  erfinden.

---

## 6. Aussageklassen

| Klasse                    | Bedeutung                                        |
| ------------------------- | ------------------------------------------------ |
| `input_fact`              | Vom Nutzer / Datensatz gelieferte Information    |
| `calculation_fact`        | Deterministisch berechnetes Ergebnis             |
| `traditional_claim`       | Überlieferte numerologische Bedeutung            |
| `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation |
| `empirical_evidence`      | Ergebnis einer statistischen Untersuchung        |
| `practical_suggestion`    | Nicht verbindliche Handlungsoption               |

Jede neue Ausgabe, jeder neue Bericht und jedes neue Schema muss jede Aussage
einer dieser Klassen zuordnen. Unklassifizierte absolute Aussagen sind nicht
zulässig.

---

## 7. Schema- und OpenAPI-Driftregeln

Versionierte JSON-Schemas (`src/numerology_api/schemas/`), die OpenAPI-Spec
(`openapi/numra-v1.json`) und die Beispieldateien (`examples/`) werden aus
den pydantic-Modellen generiert. Sie sind **Single Source of Truth** und
müssen mit dem Code synchron bleiben.

- Nach jeder Vertragsänderung die Artefakte neu generieren:
  ```bash
  uv run python scripts/export_schemas.py
  uv run python scripts/export_openapi.py
  uv run python scripts/generate_examples.py
  ```
- Vor jedem Commit den Drift-Check ausführen:
  ```bash
  uv run python scripts/export_schemas.py --check
  uv run python scripts/export_openapi.py --check
  uv run python scripts/generate_examples.py --check
  ```
- **Keine manuellen Edits** an generierten Artefakten — Änderungen gehören in
  die pydantic-Modelle.
- Vertragsänderungen sind **abwärtskompatibel** zu halten (V1 bleibt lesbar,
  neue Erzeugung in V2) und benötigen einen ADR, sofern sie Methoden- oder
  Vertragssemantik betreffen.

---

## 8. Commit-Konvention (Conventional Commits)

Commit-Nachrichten folgen [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <kurzbeschreibung>
```

| Typ      | Verwendung                                        |
| -------- | ------------------------------------------------- |
| `feat`   | Neue Funktionalität                               |
| `fix`    | Fehlerbehebung                                    |
| `refactor` | Strukturverbesserung ohne Verhaltensänderung    |
| `docs`   | Dokumentation                                     |
| `test`   | Tests                                             |
| `build`  | Build-/Tooling-Änderungen                         |
| `chore`  | Wartung, Dependencies, Metadaten                  |
| `release`| Release-Vorbereitung                              |

Beispiele:

```
feat(engine): add pythagorean-v2 calculation contract
fix(web): close abort-resubmit race in analysis wizard
docs: align README and release truth after RC1 tag
```

Der Fokus liegt auf dem **Warum**. Keine leeren Commit-Bodies, keine
Sammel-Commits über unzusammenhängende Themen.

---

## 9. Security- und Datenschutzgrenzen

- **Keine Secrets im Repository.** API-Keys, Passwörter und Tokens gehören in
  Umgebungsvariablen (12-Factor). `DEEPSEEK_API_KEY` und verwandte Variablen
  werden niemals committet.
- **Keine privaten personenbezogenen Daten im Repository.** Test- und
  Beispieldaten sind synthetisch. Screenshots und Beispiele verwenden
  ausschließlich synthetische Golden-Profile.
- **Lokale Speicherung.** Profile, Berichte, Rückfragen und Notizen liegen in
  IndexedDB; Verschlüsselung optional mit PBKDF2 + AES-GCM.
- **LLM standardmäßig deaktiviert** (`NUMRA_LLM_ENABLED=false`). Der
  DeepSeek-Adapter sendet keine Klarnamen und kein vollständiges Geburtsdatum.
- **Redis** wird ausschließlich für flüchtige, HMAC-pseudonymisierte Quoten
  verwendet.
- **Fail-closed.** Bei harten Provider-Fehlern (400/401/403) oder fehlender
  Konfiguration wird der LLM-Pfad geschlossen, nicht stillschweigend
  umgangen.
- **Keine Diagnosen.** Krisen- und Minderjährigenschutz-Gates dürfen nicht
  geschwächt werden.

---

## 10. Release-Prozess

- Ausführliche Release Notes sind die **Single Source of Truth**:
  `docs/releases/`. Der Root-`CHANGELOG.md` verlinkt nur darauf und erzeugt
  keine zweite Releasebeschreibung.
- Tags werden **nicht bewegt**. Neue Änderungen nach einem Tag gehören zum
  nächsten Release (z. B. `v0.3.0-rc.2`).
- Der öffentliche Launch bleibt gesperrt, bis VPS, Domain, DNS, TLS,
  Betreiberangaben und rechtliche Launch-Gates bestätigt sind
  (`docs/operations/launch-checklist.md`).

---

## 11. Weiterführende Dokumentation

| Dokument | Zweck |
| -------- | ----- |
| `README.md` | Produktübersicht und Quick Start |
| `PROJECT_CHARTER.md` | Was und Warum von V1 (verbindlich) |
| `ROADMAP.md` | 15 Phasen (0–14) mit Gates |
| `docs/governance/master-implementation-contract.md` | Normativer Master-Vertrag |
| `docs/adr/` | Architektur-Entscheidungen (bindend) |
| `docs/releases/` | Ausführliche Release Notes (SSOT) |
| `docs/safety/privacy.md` | Datenschutz- und Sicherheitsgrenzen |
