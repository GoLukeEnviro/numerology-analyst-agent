# Numra – Numerologie nachvollziehbar

> **Installierbare, lokale-first Numerologie-PWA mit auditierbarem Rechenkern** —
> deterministische Berechnung, versioniertes Wissen, klare Aussageklassen und
> optionaler, fail-closed validierter LLM-Bericht.

---

## Status: Produktionskandidat – öffentlicher Launch extern gesperrt

Auf dem stabilen `0.1.3`-Life-Path-Vertrag bauen zwei neue, getrennt
versionierte Verträge auf:

- `0.1.4`: Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-,
  Persönlichkeits- und Reifezahl, Namenssegmente, aktiver Name und Y-Varianten.
- `0.1.5`: persönliche Jahre, Monate und Tage sowie vier Pinnacles und Challenges.

Der bestehende `calculation-result-v1`-Vertrag bleibt kompatibel. Das
vollständige Profil verwendet `profile-calculation-result-v2`; sein Hash umfasst
alle fachlichen Eingaben einschließlich `as_of_date`, Policy, Resultate und Trace.
`consent_given` bleibt ausdrücklich ausgeschlossen.

Der Branch `codex/numra-pwa` implementiert den vollständigen vertikalen
Produktschnitt:

- React/Vite/TypeScript-PWA mit Dark/Light Theme und Offline-Lesezugriff
- lokale Profile, Berichte, Rückfragen und Notizen in IndexedDB
- optionaler PBKDF2-/AES-GCM-Passphraseschutz sowie Export/Import
- clientseitiger PDF-Export und Expertenansicht
- FastAPI für Vollprofil, Zyklen, Health/Meta und optionale LLM-Analyse
- versioniertes Wissen, regelbasierte Interpretation und Safety-Gates
- DeepSeek-Adapter ohne Klarname oder vollständiges Geburtsdatum
- Redis ausschließlich für flüchtige, HMAC-pseudonymisierte Quoten
- gehärteter Docker-/Nginx-Stack mit Commit-SHA-Release und Rollback

Der öffentliche Launch bleibt gesperrt, bis ein VPS eindeutig zugeordnet,
Domain und DNS bereitgestellt, Betreiberangaben ergänzt, HTTPS aktiviert und
die rechtlichen Launch-Gates bestätigt wurden. Die deterministische Anwendung
bleibt vollständig nutzbar, während DeepSeek standardmäßig deaktiviert ist.

- **Repository:** `GoLukeEnviro/numerology-analyst-agent`
- **Source of Truth (intern):** `docs/governance/master-implementation-contract.md`
- **Methoden-ADRs:** `docs/adr/0001`–`docs/adr/0004` (bindend)
- **Roadmap:** `ROADMAP.md` (15 Phasen, 0–14, mit Gates)

---

## Was dieses Projekt ist

Der **Numerology Analyst Agent** ist eine vollständige, reproduzierbare und erweiterbare Plattform, die das bisher uneinheitliche Feld der Numerologie in eine überprüfbare Struktur überführt. Das Projekt besteht aus **fünf voneinander getrennten Ebenen**, jeweils mit eigenen Verträgen, eigener Versionierung und eigener Verantwortung:

| #   | Ebene                | Kurzbeschreibung                                                                                           |
| --- | -------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | **Fachmodell**       | Numerologie als formal spezifiziertes Fachgebiet (Methoden, Claim-Taxonomie, Evidenzgrade, Positionierung) |
| 2   | **Rechenkern**       | Deterministischer, auditierbarer Berechnungsmotor — kein LLM, kein Netzwerk                                |
| 3   | **Wissensmodell**    | Versioniertes Wissens- und Interpretationsmodell (Zahlen, Meisterzahlen, Schatten, Gegenhypothesen)        |
| 4   | **Forschungsrahmen** | Empirischer Forschungs- und Evaluierungsrahmen (Hypothesenregister, Nullmodelle, Permutation, Power)       |
| 5   | **App-Schicht**      | Anwendungs-, API- und Agentenschicht (CLI, FastAPI, optionaler dünner LLM-Adapter)                         |

Die Verarbeitungs-Pipeline ist: Eingaben → Normalisierung → Methoden-/Policy-Auswahl → deterministischer Rechenkern → auditierbares Ergebnis → Wissensauflösung → Interpretationskomposition → Safety-/Evidenz-/Aussageklassifizierung → CLI / API / Agent / Bericht.

---

## Was dieses Projekt NICHT ist

Ausdrücklich **kein**:

- **Kein reines Prompt-Repository** — ein Systemprompt allein reicht nicht. Der bestehende Custom-GPT-Prompt ist _nur eine mögliche Benutzerschnittstelle_ und darf weder Berechnungslogik noch Fachwissen duplizieren oder ersetzen.
- **Kein einfacher Numerologie-Rechner** — reines Berechnen ohne Wissensmodell, Forschungsrahmen und Safety ist unvollständig.
- **Keine lose Sammlung esoterischer Texte** — Deutungstexte ohne versioniertes Wissensmodell, Provenienz und Gegenhypothesen sind nicht akzeptabel.

### Zukunftsmodule (NICHT in V1)

Die folgenden Systeme sind ausdrücklich **ausgeschlossen** aus Version 1 und werden nur als dokumentierte Erweiterungspunkte angelegt:

- Chaldäische Numerologie
- Kabbalistische / Gematria-nahe Systeme
- Astrologie
- **Human Design**
- Enneagramm

---

## Wissenschaftliche Positionierung

**Numerologische Traditionen sind keine wissenschaftlich validierten psychologischen Messverfahren.**

Das Projekt **darf**:

- traditionelle Systeme formal dokumentieren,
- deren Berechnungen reproduzierbar machen,
- Interpretationen transparent modellieren,
- empirische Behauptungen ergebnisoffen untersuchen.

Das Projekt **darf nicht**:

- symbolische Deutungen als wissenschaftliche Fakten ausgeben,
- statistische Korrelationen als Kausalität darstellen,
- fehlende Evidenz als Beleg für spirituelle Wahrheit umdeuten,
- medizinische oder psychologische Diagnosen ableiten.

Die Nutzeransicht unter `/wissen`, das Threat Model und die versionierten
Wissenspakete dokumentieren diese Positionierung.

### Sechs Aussageklassen

Das gesamte System trennt technisch zwischen sechs Aussageklassen, die in Code, Schemas, API-Ausgaben, Berichten und Tests sichtbar sein müssen:

| Klasse                    | Bedeutung                                        |
| ------------------------- | ------------------------------------------------ |
| `input_fact`              | Vom Nutzer / Datensatz gelieferte Information    |
| `calculation_fact`        | Deterministisch berechnetes Ergebnis             |
| `traditional_claim`       | Überlieferte numerologische Bedeutung            |
| `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation |
| `empirical_evidence`      | Ergebnis einer statistischen Untersuchung        |
| `practical_suggestion`    | Nicht verbindliche Handlungsoption               |

---

## Determinismus vor LLM

**Alle Berechnungen funktionieren ohne Sprachmodell vollständig.** Ein LLM (optional, letzte Phase) darf ausschließlich validierte Ergebnisse erklären, Deutungshypothesen formulieren und Ausgaben sprachlich anpassen. Ein LLM darf niemals Zahlen selbst berechnen, fehlende Daten erfinden, Methodenversionen vermischen oder validierte Rechenergebnisse überschreiben. Die Plattform funktioniert vollständig ohne LLM.

---

## Quick Start

Voraussetzung: Python 3.12+ und [`uv`](https://docs.astral.sh/uv/).

```bash
# Abhängigkeiten installieren (inkl. dev-Gruppe, mit Lock-Vertrag)
uv sync --locked --all-groups

# Profil berechnen (--as-of-date ist verpflichtend seit 0.1.3)
numerology profile \
    --name "Max Mustermann" \
    --birth 1985-07-25 \
    --as-of-date 2026-07-26
```

`--as-of-date` ist **verpflichtend** (seit `0.1.3`). Der Parameter macht den
Lauf deterministisch unabhängig vom Tagesdatum der Maschine.

### PWA und API lokal

Voraussetzungen: Node.js gemäß `.node-version`, pnpm 10.22 und Python 3.12.

```bash
pnpm install --frozen-lockfile
uv sync --locked --all-groups

# Terminal 1
uv run uvicorn numerology_api.app:app --reload --port 8000

# Terminal 2
pnpm --filter @numra/web dev
```

Die PWA läuft anschließend unter `http://localhost:5173`.

### Produktionsnaher Container-Smoke

```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait
curl --fail http://127.0.0.1:8080/api/v1/health/ready
docker compose down
```

Deployment, privates SSH-Staging und Launch-Gates stehen in
[`deploy/README.md`](deploy/README.md) und
[`docs/operations/launch-checklist.md`](docs/operations/launch-checklist.md).

### Beispiel-Output (gekürzt)

```json
{
  "schema_version": "calculation-result-v1",
  "deterministic_hash": "5ec8117ea20995b8eb9aaa7f539bf2e125844860272de851d684ca777e985258",
  "input": {
    "core_name": "Max Mustermann",
    "birth_date": "1985-07-25",
    "as_of_date": "2026-07-26"
  },
  "method": { "system": "pythagorean", "version": "v1" },
  "results": {
    "life_path_a": {
      "raw_total": 37,
      "reduced_value": 1,
      "compound_notation": "37/10/1",
      "karmic_debt": null
    },
    "life_path_b": {
      "raw_total": 19,
      "reduced_value": 1,
      "compound_notation": "19/10/1",
      "karmic_debt": { "number": 19, "origin": "component_sum" }
    }
  },
  "consistency": { "a_equals_b": true }
}
```

- `schema_version`: Version des CalculationResult-Vertrags (seit `0.1.3`).
- `deterministic_hash`: SHA-256 über das CalculationHashEnvelope (Schema, Input, Policy, Ergebnisse, Trace). `consent_given` ist ausgeschlossen.

### Quality Gates

Alle Gates müssen grün sein:

```bash
uv lock --check
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests scripts
uv run pip-audit
uv run pytest --cov=src/numerology_engine --cov-fail-under=95
uv run pytest --cov=src --cov-fail-under=85
uv run python scripts/export_schemas.py --check
uv run python scripts/export_openapi.py --check
uv run python scripts/generate_examples.py --check
pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2
pnpm web:lint
pnpm web:typecheck
pnpm web:test
pnpm web:build
pnpm web:check-build
pnpm web:e2e
docker compose config --quiet
```

### Architektur (`0.1.0`-Scope)

```
PersonInput → MethodPolicy → Normalizer (de-direct-v1) → Life Path A/B
            → CalculationTrace → JSON (CLI) → Golden tests → CI
```

Paketgrenzen (Master-Vertrag §4.3, hier nur der 0.1.0-Scope):

| Paket               | Verantwortung                                                |
| ------------------- | ------------------------------------------------------------ |
| `numerology_domain` | Verträge: `PersonInput`, `MethodPolicy`, `CalculationResult` |
| `numerology_engine` | Deterministischer Rechenkern (pure functions, kein Netzwerk) |
| `numerology_api`    | Zustandslose FastAPI-Grenze und versionierte HTTP-Verträge    |
| `numerology_cli`    | Typer-CLI mit `profile`-Command                              |
| `numerology_knowledge` | Versioniertes deutsches Wissenspaket                      |
| `numerology_interpretation` | Regelbasierte, referenzierte Interpretation          |
| `numerology_safety` | Claims-, Sprach- und Prompt-Injection-Gates                   |
| `numerology_agent`  | Optionaler pseudonymisierter LLM-Provider-Adapter             |

### Determinismus

- Pure Functions, keine globale State, keine Randomness, keine Zeitabhängigkeit
  (der CLI-Parameter `--as-of-date` ist verpflichtend und macht den Lauf
  reproduzierbar).
- Immutable Domain-Modelle (pydantic v2, `frozen=True`).
- Serialisierung immer mit `sort_keys=True` ⇒ identischer Input ergibt
  byte-identisches JSON und identischen SHA-256-Hash.
- Der Hash umfasst das CalculationHashEnvelope: Schema-Version, fachlich
  relevante Eingaben, vollständige Policy, Ergebnisse und Trace.
  `consent_given` ist ausgeschlossen. Sets/Frozensets werden kanonisiert.

### Methoden-Policy (V1-Defaults)

- System: `pythagorean` v1
- Y-Regel: `phonetic` (ADR 0001) — im 0.1.0-Scope nur als Policy-Feld
  modelliert (Life Path hängt nicht vom Namen ab).
- Umlaute: `de-direct-v1` (Ä→A, Ö→O, Ü→U, ß→SS; ADR 0002)
- Namensbasis: `both_separate` (ADR 0004)
- Meisterzahlen: 11, 22, 33 (werden gehalten, nicht weiter reduziert)
- Karmische Schulden (13/14/16/19): nur Metadatum, keine Auswertung in 0.1.0

---

## Aktueller Status

> **Stand:** 2026-07-27, verifiziert durch tatsächlichen Testlauf (nicht nur
> Dokumentenlage). Zwei Zustände sind zu unterscheiden: was auf `main`
> gemerged/getaggt ist, und was auf dem Branch `codex/numra-pwa` (offener
> Draft-**PR #10**) bereits implementiert, aber noch **nicht gemerged** ist.

| Komponente                                                                 | Status                                                                  |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Governance-Grundlagen (Master-Vertrag, Charter, Roadmap, ADRs, Agenten)    | ✅ vorhanden, bindend                                                   |
| **`main`: Release `0.1.3` Contract Integrity** (Life Path A/B)            | ✅ **LIVE**, getaggt `v0.1.3`                                           |
| Release `0.1.0`–`0.1.2` (Walking Skeleton, Packaging)                     | ✅ abgelöst durch `0.1.3`                                               |
| **`codex/numra-pwa` (PR #10, offen/Draft): Complete Core Profile (0.1.4)** | ✅ implementiert — Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-, Persönlichkeits-, Reifezahl, Namenssegmente |
| **`codex/numra-pwa`: Deterministic Cycles (0.1.5)**                       | ✅ implementiert — persönliche Jahre/Monate/Tage, 4 Pinnacles/Challenges |
| **`codex/numra-pwa`: Wissensmodell + regelbasierte Interpretation**       | ✅ implementiert (`numerology_knowledge`, `numerology_interpretation`) |
| **`codex/numra-pwa`: Safety-Gates** (Claims-/Sprachvalidierung, Threat Model, Privacy-Doku) | ✅ implementiert (`numerology_safety`)                    |
| **`codex/numra-pwa`: FastAPI** (Health/Meta, Profil-Berechnung, optionale LLM-Analyse mit Follow-up) | ✅ implementiert (`numerology_api`)             |
| **`codex/numra-pwa`: optionaler LLM-Adapter** (DeepSeek, pseudonymisiert, fail-closed, standardmäßig deaktiviert) | ✅ implementiert (`numerology_agent`)   |
| **`codex/numra-pwa`: React/Vite/TypeScript-PWA** (Profile, Berichte, PDF-Export, IndexedDB, Verschlüsselung) | ✅ implementiert (`apps/web`)              |
| **`codex/numra-pwa`: gehärteter Docker-/Nginx-Stack, Release/Rollback/Backup-Skripte** | ✅ implementiert (`docker/`, `deploy/`)                       |
| Forschungs-/Meta-Analyse-Rahmen (Phase 7 / Release `0.4.0`)                | ❌ nicht begonnen                                                        |
| MkDocs-Dokumentation, Committee-Review-Prozess                             | ❌ nicht begonnen                                                        |
| **Öffentlicher Launch**                                                    | 🔒 **explizit gesperrt** bis VPS/Domain/TLS/Recht bestätigt sind (siehe `docs/operations/launch-checklist.md`) |

**Wichtig:** `pyproject.toml` steht formal auf Version `0.1.5`, obwohl der
`codex/numra-pwa`-Branch inhaltlich bereits deutlich weiter ist (Wissen,
Interpretation, Safety, API, Agent, PWA — Umfang entspricht eher den
Releases `0.2.0`/`0.3.0` im ursprünglichen Plan). Die Versionsnummer wurde
dafür noch nicht angehoben; das ist eine offene Entscheidung, keine
technische Lücke.

Von mir lokal verifiziert (2026-07-27, Branch `codex/numra-pwa` bzw. der
identische Analyse-Branch): 188 Python-Tests grün, Engine-Coverage 97,53 %,
Gesamt-Coverage 93,22 %, Ruff/Mypy strict grün, Schema-/OpenAPI-/Beispiel-
Drift-Checks grün, 28 Vitest-Tests grün, Web-Lint/Typecheck/Build grün,
`docker compose config` grün. Remote-CI auf dem aktuellen HEAD (`f2baef9`)
ist ebenfalls grün.

Release `0.1.0` wurde nach dem Merge von PR #2 als Tag `v0.1.0`
veröffentlicht, Release `0.1.3` nach Merge von PR #6 als Tag `v0.1.3`. Die
Releases `0.1.4` und `0.1.5` existieren bislang nur als Versionsstand/
Release-Notes innerhalb des noch offenen PR #10 — dafür wurden keine
eigenen Tags geschnitten.

---

## Dokumentation

| Dokument                                            | Zweck                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------- |
| `PROJECT_CHARTER.md`                                | Was und Warum von V1 (verbindlich)                                    |
| `ROADMAP.md`                                        | 15 Phasen (0–14) mit Gates, Commits, Aufwand, Delegation              |
| `docs/v1-minimal-scope.md`                          | Scope von Release 0.1.0 Deterministic Core (vorhanden, bindend)       |
| `docs/governance/master-implementation-contract.md` | Normativer Master-Vertrag (vorhanden, bindend)                        |
| `docs/adr/`                                         | 4 ADRs zu Methodenentscheidungen (vorhanden, bindend)                 |
| `docs/audit/`                                       | Repository-Baseline, Gap-Analyse, Übersetzungsplan                    |
| `docs/field/`                                       | Fachgebiet, Claim-Taxonomie, wissenschaftliche Positionierung (folgt) |

Agentenverträge: siehe `.github/agents/`.

---

## Lizenz

**MIT** (geplant). Die `LICENSE`-Datei wird in Phase 14 (GitHub-Finalisierung) hinzugefügt.

---

## Beitragsweise

Beitragsrichtlinien werden in einer späteren Phase in `CONTRIBUTING.md` veröffentlicht. Bis dahin: keine Direktpushes auf `main`, kein Force-Push, kein `--no-verify`, Commits auf Deutsch mit Fokus auf das Warum.

---

## Wissenschaftliche Ehrlichkeit

Dieses Projekt dokumentiert numerologische Traditionen formal und macht ihre Berechnungen reproduzierbar. **Numerologie ist empirisch nicht validiert.** Das Projekt gibt keine medizinischen, psychologischen oder sonstigen diagnostischen Aussagen. Siehe `docs/field/scientific-positioning.md` (folgt).
