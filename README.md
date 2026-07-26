# Numerology Analyst Agent

> **Auditierbare Domänenplattform für numerologische Berechnung** — deterministischer Rechenkern, versionierte Wissenspakete, empirischer Forschungsrahmen, optionale Agenten-Schicht. **Kein Chatbot, kein simpler Rechner, keine Esoterik-Sammlung.**

---

## Status: Release `0.1.3` — Contract Integrity

`0.1.3` ist der aktuelle stabile Release.

`0.1.3` stärkt den deterministischen Berechnungsvertrag: Der Hash umfasst
jetzt den vollständigen fachlich relevanten Input (Schema-Version, Eingaben,
Policy, Ergebnisse, Trace), `consent_given` ist ausgeschlossen, Sets werden
kanonisiert, `--as-of-date` ist verpflichtend, und versionierte JSON-Schemas
liegen im installierten Wheel. Nur Life Path A/B ist enthalten; alle weiteren
Zahlen folgen in späteren Releases.

**Breaking Changes gegenüber `0.1.0`–`0.1.2`:**

- `--as-of-date` ist nicht mehr optional.
- Die Hashsemantik wurde geändert — alte Hashwerte sind nicht mit `0.1.3` vergleichbar.
- `schema_version` ist neu im Calculation-Result-Contract.

Die **Plan-Phase ist abgeschlossen** (Plan-Konsolidierung V1.1, Stand 2026-07-25).
Das Walking-Skeleton-Release `0.1.0 Deterministic Core` ist **LIVE** und
implementiert einen vertikalen Slice durch alle Schichten — vom Input
(`PersonInput`) über Normalisierung (`de-direct-v1`) und Rechenkern
(Life Path A/B) bis hin zur deterministischen JSON-Ausgabe der CLI, Golden
Tests und CI. **Nur Life Path A/B** ist enthalten; alle weiteren Zahlen
(Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-, Persönlichkeits-,
Reifezahl, Zyklen, Interpretationen) folgen in späteren Releases.

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

Vollständige Positionierung: `docs/field/scientific-positioning.md` (folgt in Phase 1).

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

## Quick Start (`0.1.3`)

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
uv run pytest --cov=src/numerology_engine --cov-fail-under=95
uv run pytest --cov=src --cov-fail-under=85
uv run python scripts/export_schemas.py --check
uv run python scripts/generate_examples.py --check
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
| `numerology_api`    | Dünner JSON-Adapter (KEIN FastAPI im Skeleton)               |
| `numerology_cli`    | Typer-CLI mit `profile`-Command                              |

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

| Komponente                                                           | Status                      |
| -------------------------------------------------------------------- | --------------------------- |
| Plan-Konsolidierung V1.1                                             | ✅ abgeschlossen            |
| Master-Vertrag (`docs/governance/master-implementation-contract.md`) | ✅ vorhanden, bindend       |
| `PROJECT_CHARTER.md`                                                 | ✅ vorhanden                |
| `ROADMAP.md` (15 Phasen, 0–14)                                       | ✅ vorhanden                |
| `docs/audit/gap-analysis.md`                                         | ✅ vorhanden                |
| `docs/audit/implementation-plan.md`                                  | ✅ vorhanden                |
| Methoden-ADRs `docs/adr/0001`–`0004`                                 | ✅ vorhanden, bindend       |
| `.github/agents/*` (6 Agent-Verträge)                                | ✅ Plan-Konsolidierung V1.1 |
| **Release `0.1.3` Contract Integrity**                               | ✅ **LIVE**                              |
| Release `0.1.2` Packaging-Hardening                                  | ✅ abgelöst durch `0.1.3`               |
| Release `0.1.0` Walking Skeleton                                     | ✅ abgelöst durch `0.1.3`               |
| Phasen 1–14 (Vollausbau)                                             | ⏳ folgen                   |
| Vollständiger deterministischer Profilkern (`0.1.4`)                 | ⏳ folgt nach `0.1.3`       |
| Wissensmodell + Interpretation (`0.2.0`)                             | ⏳ blockiert bis `0.1.4`    |

Release `0.1.0` wurde nach dem Merge von PR #2 als Tag `v0.1.0` veröffentlicht.
Release `0.1.3` erscheint nach Merge von PR #6.

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
