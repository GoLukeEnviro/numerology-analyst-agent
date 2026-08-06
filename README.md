# Numra – Numerologie nachvollziehbar

> **Installierbare, lokale-first Numerologie-PWA mit auditierbarem Rechenkern** —
> deterministische Berechnung, versioniertes Wissen, klare Aussageklassen und
> optionaler, fail-closed validierter LLM-Bericht.

---

## Status: post-PR-56 main (0.3.0rc1) – nächster Meilenstein v0.3.0-rc.2 – Launch extern gesperrt

Der Release-Kandidat **`v0.3.0-rc.1`** ist getaggt und zeigt unveränderlich auf
Commit `21ba56ed0d918cea7c60090bcc50937adc16269a`. Er umfasst die vollständige
**Integration Closure** (Backend, Frontend, API, Container) und baut auf dem
stabilen `0.1.3`-Life-Path-Vertrag auf, der um die getrennt versionierten
Verträge `0.1.4` (vollständiges Kernprofil) und `0.1.5` (deterministische
Zyklen) erweitert wurde.

Der aktuelle `main` (HEAD `ba4c9121866a8c05b1ccfea076e0c26db9c25758`) enthält
seit PR **#56** zusätzlich den **V2/V3-Stack** (Backend-Wellen 1–3, Web-Welle 4)
unter `/api/v2` — kontrolliert hinter `product_default_method_version=v1` und
`rollout_stage=disabled` (ADR 0028). Die Paketversion bleibt **`0.3.0rc1`**;
alle weiteren Änderungen gehören zu **`v0.3.0-rc.2`**. Live-Status:
`docs/audit/current-state-numra-post-rc1-2026-08-02.md` und
`docs/audit/numra-post-pr56-recovery-baseline-2026-08-06.md`.

Der bestehende `calculation-result-v1`-Vertrag bleibt kompatibel. Das
vollständige Profil verwendet `profile-calculation-result-v3`; sein Hash umfasst
alle fachlichen Eingaben einschließlich `as_of_date`, Policy, Resultate und Trace.
`consent_given` bleibt ausdrücklich ausgeschlossen.

Der aktuelle `main`-Quellstand enthält den vollständigen vertikalen
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
bleibt vollständig nutzbar, während DeepSeek standardmäßig deaktiviert ist
(`NUMRA_LLM_ENABLED=false`).

- Lokaler Restore-Test: **PASS** (`docs/operations/rollback-rehearsal-local-2026-08-04.md`)
- Lokaler Rollback-Rehearsal: **PASS**
- Privates Host-Staging-Restore: **NOT_EXECUTED**
- Privates Host-Staging-Rollback: **NOT_EXECUTED**

> **Tag-Status:** `v0.3.0-rc.1` existiert und zeigt auf
> `21ba56ed0d918cea7c60090bcc50937adc16269a`. Der Tag wird nicht bewegt; alle
> neuen Änderungen gehören zu `v0.3.0-rc.2`. Ausführliche Release Notes:
> `docs/releases/v0.3.0-rc.1.md`; Plan:
> `docs/plans/numra-0.3.0-rc1-implementation-plan.md`; IST-Bestandsaufnahme:
> `docs/audit/current-state-numra-rc.md`; V2-Grenze: ADR 0016.

- **Repository:** `GoLukeEnviro/numerology-analyst-agent`
- **Source of Truth (intern):** `docs/governance/master-implementation-contract.md`
- **Methoden-ADRs:** `docs/adr/0001`–`docs/adr/0004` (bindend)
- **Roadmap:** `ROADMAP.md` (15 Phasen, 0–14, mit Gates)

> **Screenshot:** Der Profil-Dashboard-Screenshot
> (`docs/assets/numra-profile-dashboard-dark.png`, Dark Theme, synthetisches
> Golden-Profil) wird beim nächsten Deployment aus dem finalen Build erzeugt
> und hier eingebunden. Bis dahin wird bewusst kein Platzhalter-Bild
> veröffentlicht.

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

Der **V2 Guided Masterplan** (`docs/product/numra-v2-guided-masterplan.md`) ist
eine **Produktspezifikation**, kein vollständig implementiertes Feature (ADR
0016). Forschungs- und Plattformerweiterungen (Methodensysteme,
Mehrsprachigkeit, Cloud, Agenten-Workflows) sind **Zukunftsmodule** und in
`docs/roadmaps/numra-platform-expansion-roadmap.md` dokumentiert.

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

> **Stand:** 2026-08-06. Der Release-Kandidat `v0.3.0-rc.1` ist getaggt
> (`21ba56ed0d918cea7c60090bcc50937adc16269a`) und umfasst die vollständige
> Integration Closure. Seit PR #56 enthält `main` zusätzlich den V2/V3-Stack
> (kontrolliert, ADR 0028). Der öffentliche Launch bleibt extern gesperrt.

| Komponente | Status |
| --- | --- |
| Governance-Grundlagen | ✅ vorhanden und bindend |
| Getaggtes Release `v0.1.3` | ✅ veröffentlicht; Life Path A/B und Contract Integrity |
| Vollständiges Profil und deterministische Zyklen | ✅ in `v0.3.0-rc.1` enthalten |
| Wissensmodell, Interpretation und Safety-Gates | ✅ in `v0.3.0-rc.1` enthalten |
| FastAPI und optionaler DeepSeek-Adapter | ✅ in `v0.3.0-rc.1` enthalten; LLM standardmäßig deaktiviert |
| React/Vite/TypeScript-PWA | ✅ in `v0.3.0-rc.1` enthalten |
| Gehärteter Docker-/Nginx-Stack | ✅ in `v0.3.0-rc.1` enthalten |
| Integration Closure (Backend, Frontend, API, Container) | ✅ abgeschlossen (PRs #26–#31) |
| Release-Kandidat `v0.3.0-rc.1` | ✅ getaggt auf `21ba56e`; Details: `docs/releases/v0.3.0-rc.1.md` |
| V2/V3-Stack (Backend-Wellen 1–3, Web-Welle 4) | ✅ auf `main` seit PR #56; `product_default_method_version=v1`, `rollout_stage=disabled` (ADR 0028) |
| V2-OpenAPI-Contract (4 Endpunkte) | ✅ driftfrei regeneriert; V1-Contract semantisch unverändert |
| Knowledge V3-Validierung | ✅ `scripts/validate_knowledge.py` validiert de-v1/v2/v3 |
| LLM-Staging | 🟡 technisch vorbereitet (`compose.llm-staging.yaml`); echtes Betreiber-/Legal-/VPS-Staging separat und noch offen |
| V2 Guided Masterplan | 📄 Produktspezifikation, nicht implementiert (`docs/product/numra-v2-guided-masterplan.md`, ADR 0016); bis nach Stable gesperrt |
| Forschungs-/Plattformerweiterungen | 📄 Zukunftsmodule (`docs/roadmaps/numra-platform-expansion-roadmap.md`) |
| Öffentlicher Launch | 🔒 bis VPS, Domain, TLS, Betreiberangaben und Rechtsfreigaben bestätigt sind |

**Versionshinweis:** `pyproject.toml` steht formal auf `0.3.0rc1`; der kumulierte
Funktionsumfang ist über ADR 0015 als Release-Kandidat `v0.3.0-rc.1`
normalisiert und getaggt. Die Dateien `docs/releases/v0.1.4.md` und
`v0.1.5.md` beschreiben Entwicklungsmeilensteine, keine veröffentlichten Tags.

---

## Dokumentation

| Dokument                                            | Zweck                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------- |
| `PROJECT_CHARTER.md`                                | Was und Warum von V1 (verbindlich)                                    |
| `ROADMAP.md`                                        | 15 Phasen (0–14) mit Gates, Commits, Aufwand, Delegation              |
| `docs/v1-minimal-scope.md`                          | Scope von Release 0.1.0 Deterministic Core (vorhanden, bindend)       |
| `docs/governance/master-implementation-contract.md` | Normativer Master-Vertrag (vorhanden, bindend)                        |
| `docs/adr/`                                         | ADRs zu Methoden-, Architektur- und Release-Entscheidungen (bindend)  |
| `docs/releases/`                                    | Ausführliche Release Notes (SSOT für Releases)                        |
| `docs/audit/`                                       | Repository-Baseline, Gap-Analyse, Übersetzungsplan                    |
| `docs/field/`                                       | Fachgebiet, Claim-Taxonomie, wissenschaftliche Positionierung (geplant) |

Agentenverträge: siehe `.github/agents/`.

---

## Lizenz

**MIT.** Der vollständige Lizenztext liegt in [`LICENSE`](LICENSE).

---

## Beitragsweise

Beiträge sind willkommen. Bitte [`CONTRIBUTING.md`](CONTRIBUTING.md) lesen —
dort stehen Setup, Branch-/PR-Regeln, Quality Gates, Commit-Konventionen sowie
die Security- und Datenschutzgrenzen. Grundregeln: keine Direktpushes auf
`main`, kein Force-Push, kein `--no-verify`.

---

## Wissenschaftliche Ehrlichkeit

Dieses Projekt dokumentiert numerologische Traditionen formal und macht ihre Berechnungen reproduzierbar. **Numerologie ist empirisch nicht validiert.** Das Projekt gibt keine medizinischen, psychologischen oder sonstigen diagnostischen Aussagen. Siehe `docs/field/scientific-positioning.md` (folgt).
