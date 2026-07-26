# Master Implementation Contract — Numerology Analyst Agent

> **Dokumenttyp:** Normativer Vertrag (Source of Truth für Charter, Roadmap, ADRs, Methodenspezifikation)
> **Version:** 1.0
> **Eingereicht am:** 2026-07-25
> **Status:** Bindend für V1-Implementierung
> **SHA256-Platzhalter:** `[BEI COMMIT VON LUKE EINZUTRAGEN]`
> **Änderungsprozess:** Änderungen an diesem Vertrag erfordern einen ADR und ein formelles Review. Direkte Edits ohne ADR sind nichtig.
> **Beziehung zu anderen Dokumenten:** PROJECT_CHARTER, ROADMAP, ADRs leiten aus diesem Vertrag ab. Bei Widerspruch gilt dieser Vertrag.

---

# Originaler Master-Implementierungsprompt

# MASTER-IMPLEMENTIERUNGSPROMPT
## Numerologie-Analyst-Agent als vollständige Domänen-, Forschungs- und Produktplattform

**Ziel-Repository:** `GoLukeEnviro/numerology-analyst-agent`  
**Dokumenttyp:** Ausführbarer Implementierungsauftrag für einen Coding-/GitHub-Agenten  
**Primärziel:** Das vollständige Fachgebiet und die technische Plattform aufbauen – nicht lediglich das Gesprächsverhalten eines Chatbots definieren.

---

## 1. Auftrag

Du bist der verantwortliche Principal Engineer, Domain Architect, Research Engineer und Repository Maintainer für das Projekt **Numerology Analyst Agent**.

Baue das bestehende GitHub-Repository zu einer vollständigen, reproduzierbaren und erweiterbaren Plattform für numerologische Berechnung, strukturierte Deutung, Forschung, Evaluation und agentische Nutzung aus.

Das Projekt darf **kein reines Prompt-Repository**, **kein einfacher Numerologie-Rechner** und **keine lose Sammlung esoterischer Texte** werden.

Es muss fünf voneinander getrennte Ebenen besitzen:

1. **Numerologie als formal spezifiziertes Fachmodell**
2. **Deterministischer und auditierbarer Rechenkern**
3. **Versioniertes Wissens- und Interpretationsmodell**
4. **Empirischer Forschungs- und Evaluierungsrahmen**
5. **Anwendungs-, API- und Agentenschicht**

Der bestehende Custom-GPT-Systemprompt ist lediglich eine mögliche Benutzerschnittstelle. Er darf weder Berechnungslogik noch Fachwissen duplizieren oder ersetzen.

---

## 2. Nicht verhandelbare Grundsätze

### 2.1 Keine erfundenen Zustände

Vor jeder Änderung:

- Repository klonen oder vorhandenen Checkout identifizieren.
- Aktuellen Branch, Remote, Commit-Stand und Working Tree prüfen.
- Vorhandene Dateien vollständig inventarisieren.
- Keine Datei, kein Commit, kein Test und kein Release als existent oder erfolgreich bezeichnen, bevor dies tatsächlich geprüft wurde.

### 2.2 Trennung der Aussagearten

Das gesamte System muss technisch zwischen folgenden Aussageklassen unterscheiden:

1. `input_fact` – vom Nutzer oder Datensatz gelieferte Information
2. `calculation_fact` – deterministisch berechnetes Ergebnis
3. `traditional_claim` – überlieferte numerologische Bedeutung
4. `interpretive_hypothesis` – daraus abgeleitete, korregierbare Interpretation
5. `empirical_evidence` – Ergebnis einer statistischen Untersuchung
6. `practical_suggestion` – nicht verbindliche Handlungsoption

Diese Typen müssen im Domainmodell, in JSON-Schemas, API-Ausgaben, Berichten und Tests sichtbar sein.

### 2.3 Wissenschaftliche Positionierung

Numerologische Traditionen sind keine wissenschaftlich bestätigten psychologischen Messverfahren.

Das Projekt darf:

- traditionelle Systeme formal dokumentieren,
- deren Berechnungen reproduzierbar machen,
- Interpretationen transparent modellieren,
- empirische Behauptungen ergebnisoffen untersuchen.

Das Projekt darf nicht:

- symbolische Deutungen als wissenschaftliche Fakten ausgeben,
- statistische Korrelationen als Kausalität darstellen,
- fehlende Evidenz als Beleg für spirituelle Wahrheit umdeuten,
- medizinische oder psychologische Diagnosen ableiten.

### 2.4 Determinismus vor LLM

Alle Berechnungen müssen ohne Sprachmodell vollständig funktionieren.

Ein LLM darf:

- validierte Ergebnisse erklären,
- unterschiedliche Deutungshypothesen formulieren,
- Ausgaben sprachlich anpassen.

Ein LLM darf niemals:

- Zahlen selbst unkontrolliert berechnen,
- fehlende Daten erfinden,
- Methodenversionen vermischen,
- validierte Rechenergebnisse überschreiben.

---

## 3. Zielbild des Fachgebiets

Das Repository soll ein bisher uneinheitliches Feld in eine überprüfbare Struktur überführen.

Dafür sind folgende Fachbereiche zu modellieren:

### 3.1 Numerologische Methodologie

Mindestens dokumentieren:

- Pythagoreische Numerologie
- Chaldäische Numerologie
- Kabbalistische/Gematria-nahe Systeme
- historische und moderne Varianten
- Unterschiede bei Buchstabenwerten
- unterschiedliche Reduktionsregeln
- Meisterzahlen
- karmische Zahlen
- Behandlung von Umlauten, Akzenten, Bindestrichen und Mehrfachnamen
- Behandlung des Buchstabens Y
- Namensänderungen und Geburtsname
- Datumsberechnung
- Zyklusmodelle
- Kompatibilitätsmodelle

**Version 1 implementiert ausschließlich einen klar definierten pythagoreischen Standard.**  
Alle weiteren Systeme werden zunächst nur als dokumentierte Erweiterungspunkte und Methodenspezifikationen angelegt.

### 3.2 Kernberechnungen in Version 1

Implementieren und vollständig testen:

- Lebenswegzahl
  - Gesamtdigit-Methode
  - Komponenten-Methode
  - dokumentierter Umgang mit abweichenden Ergebnissen
- Geburtstagszahl
- Einstellungszahl
- Ausdrucks-/Schicksalszahl
- Seelenstrebenzahl
- Persönlichkeitszahl
- Reifezahl
- Namenssegmente und Namensanteile
- Meisterzahlen 11, 22 und 33
- verstärkte Doppelzahlen wie 44/8
- karmische Schuldenzahlen 13/4, 14/5, 16/7 und 19/1
- persönliche Jahre, Monate und Tage
- Pinnacles
- Challenges
- nachvollziehbare Rechenspur für jedes Ergebnis

### 3.3 Deutungsontologie

Erstelle kein loses Textarchiv. Entwickle ein versioniertes Wissensmodell mit:

- Zahlenarchetypen 1–9
- Meisterzahlen
- zusammengesetzten Zahlen
- Stärken
- Schattenausprägungen
- Entwicklungsaufgaben
- Regulationsaufgaben
- Beziehungsdynamiken
- Lebensphasen
- Kontextmodifikatoren
- Gegenhypothesen
- Unsicherheiten
- Quellen- und Traditionshinweisen

Jeder Wissenseintrag benötigt mindestens:

- stabile ID
- Methodensystem
- Methodenversion
- Zahl oder Kombination
- Aussageklasse
- Kontext
- Textbaustein
- Intensität
- Konfidenzklasse
- Gegenhypothese
- Quellenstatus
- Sprache
- Version

### 3.4 Empirischer Forschungsbereich

Baue einen eigenständigen Forschungsbereich, der numerologische Hypothesen nicht bestätigt, sondern testbar macht.

Erforderlich:

- Hypothesenregister
- Präregistrierungs-Templates
- Datenprovenienz
- Datenwörterbuch
- Feature Engineering
- Nullmodelle
- Permutationstests
- Effektstärken
- Konfidenzintervalle
- Power-Analysen
- Multiple-Testing-Korrektur
- Confounder-Kontrolle
- explorative versus konfirmatorische Kennzeichnung
- reproduzierbare Ergebnisberichte
- Negativresultate als gültige Ergebnisse

Bevorzugte Forschungsdaten:

- öffentliche historische oder biografische Daten
- öffentlich dokumentierte Personen
- synthetische Testdaten
- explizit eingewilligte Daten

Keine privaten personenbezogenen Datensätze in Git.

---

## 4. Technische Zielarchitektur

Verwende eine modulare Python-Architektur.

### 4.1 Verbindlicher Technologie-Stack

- Python 3.12 oder höher
- `uv` für Abhängigkeiten und virtuelle Umgebung
- `pydantic` v2 für Verträge und Validierung
- `pytest` für Tests
- `hypothesis` für Property-Based Tests
- `ruff` für Linting und Formatierung
- `mypy` im strikten Modus
- `FastAPI` für die HTTP-API
- `Typer` für die CLI
- `PyYAML` oder validierte JSON-Dateien für Wissenspakete
- `DuckDB` und Parquet für Forschungsdaten
- `Polars` oder Pandas für Analysepipelines
- `MkDocs Material` für technische und fachliche Dokumentation
- GitHub Actions für CI
- SemVer für Releases

Keine unnötige Datenbank, kein Vektorstore und kein LLM-Framework im Basiskern.

### 4.2 Schichten

```text
Eingaben
  ↓
Normalisierung und Validierung
  ↓
Methoden- und Policy-Auswahl
  ↓
Deterministischer Rechenkern
  ↓
Auditierbares Berechnungsergebnis
  ↓
Wissensauflösung
  ↓
Interpretationskomposition
  ↓
Safety-, Evidenz- und Aussageklassifizierung
  ↓
CLI / API / Agent / Bericht
```

### 4.3 Paketgrenzen

- `numerology_domain`: Typen, Regeln, Methodenversionen und Verträge
- `numerology_engine`: reine Berechnungen
- `numerology_knowledge`: Laden und Validieren von Wissenspaketen
- `numerology_interpretation`: regelbasierte Komposition
- `numerology_research`: Daten- und Statistikpipelines
- `numerology_safety`: Datenschutz, Krisengrenzen und Minderjährigenschutz
- `numerology_agent`: dünner Adapter für LLM-gestützte Erklärungen
- `apps/api`: FastAPI
- `apps/cli`: Typer-CLI

Es dürfen keine zyklischen Abhängigkeiten entstehen.

---

## 5. Verbindliche Repository-Struktur

Erstelle mindestens folgende Struktur. Dateien dürfen nur entfallen, wenn die Abweichung in einem ADR begründet wird.

```text
.
├── README.md
├── PROJECT_CHARTER.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── GOVERNANCE.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── uv.lock
├── Makefile
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
├── mkdocs.yml
│
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── pull_request_template.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug.yml
│   │   ├── feature.yml
│   │   ├── method-change.yml
│   │   ├── research-proposal.yml
│   │   └── config.yml
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       ├── docs.yml
│       └── release.yml
│
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── data-flow.md
│   │   ├── dependency-rules.md
│   │   └── threat-model.md
│   ├── field/
│   │   ├── field-charter.md
│   │   ├── scientific-positioning.md
│   │   ├── glossary.md
│   │   ├── claim-taxonomy.md
│   │   ├── evidence-grading.md
│   │   ├── method-comparison.md
│   │   └── limitations.md
│   ├── methods/
│   │   ├── pythagorean-v1.md
│   │   ├── normalization.md
│   │   ├── reductions.md
│   │   ├── names.md
│   │   ├── dates.md
│   │   ├── cycles.md
│   │   └── compatibility.md
│   ├── research/
│   │   ├── research-charter.md
│   │   ├── reproducibility.md
│   │   ├── statistics-policy.md
│   │   ├── data-governance.md
│   │   └── publication-policy.md
│   ├── safety/
│   │   ├── privacy.md
│   │   ├── minors.md
│   │   ├── mental-health-boundaries.md
│   │   └── responsible-interpretation.md
│   ├── committee/
│   │   ├── review-model.md
│   │   ├── release-checklist.md
│   │   └── decision-template.md
│   └── adr/
│       ├── 0001-architecture.md
│       ├── 0002-canonical-method.md
│       ├── 0003-knowledge-packs.md
│       └── 0004-llm-boundary.md
│
├── schemas/
│   ├── person-input.schema.json
│   ├── calculation-result.schema.json
│   ├── interpretation.schema.json
│   ├── knowledge-entry.schema.json
│   ├── research-hypothesis.schema.json
│   └── report.schema.json
│
├── knowledge/
│   ├── README.md
│   ├── manifest.yaml
│   ├── de/
│   │   └── pythagorean-v1/
│   │       ├── numbers-1-9.yaml
│   │       ├── master-numbers.yaml
│   │       ├── compound-numbers.yaml
│   │       ├── karmic-debts.yaml
│   │       ├── cycles.yaml
│   │       └── relationships.yaml
│   └── fixtures/
│       └── minimal-pack.yaml
│
├── prompts/
│   ├── README.md
│   ├── system/
│   │   └── analyst-v1.md
│   ├── tasks/
│   │   ├── explain-profile.md
│   │   ├── compare-profiles.md
│   │   └── generate-roadmap.md
│   └── eval/
│       ├── safe-boundaries.md
│       └── extraction-resistance.md
│
├── src/
│   ├── numerology_domain/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── models.py
│   │   ├── policies.py
│   │   ├── methods.py
│   │   ├── provenance.py
│   │   └── exceptions.py
│   ├── numerology_engine/
│   │   ├── __init__.py
│   │   ├── normalization.py
│   │   ├── reduction.py
│   │   ├── alphabet.py
│   │   ├── names.py
│   │   ├── dates.py
│   │   ├── cycles.py
│   │   ├── compatibility.py
│   │   ├── trace.py
│   │   └── service.py
│   ├── numerology_knowledge/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── registry.py
│   │   └── resolver.py
│   ├── numerology_interpretation/
│   │   ├── __init__.py
│   │   ├── composer.py
│   │   ├── tensions.py
│   │   ├── counter_hypotheses.py
│   │   ├── evidence.py
│   │   └── service.py
│   ├── numerology_research/
│   │   ├── __init__.py
│   │   ├── datasets.py
│   │   ├── features.py
│   │   ├── null_models.py
│   │   ├── statistics.py
│   │   ├── confounders.py
│   │   ├── preregistration.py
│   │   └── reporting.py
│   ├── numerology_safety/
│   │   ├── __init__.py
│   │   ├── privacy.py
│   │   ├── minors.py
│   │   ├── crisis.py
│   │   └── claims.py
│   └── numerology_agent/
│       ├── __init__.py
│       ├── context.py
│       ├── tools.py
│       ├── renderer.py
│       └── service.py
│
├── apps/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── methods.py
│   │       ├── calculate.py
│   │       ├── interpret.py
│   │       └── compare.py
│   └── cli/
│       ├── __init__.py
│       └── main.py
│
├── research/
│   ├── README.md
│   ├── registry/
│   │   ├── hypotheses.yaml
│   │   └── preregistrations/
│   ├── queries/
│   │   └── public-biographies.sparql
│   ├── pipelines/
│   │   ├── ingest.py
│   │   ├── clean.py
│   │   ├── feature_engineering.py
│   │   └── evaluate.py
│   ├── reports/
│   │   └── .gitkeep
│   └── data/
│       ├── README.md
│       ├── sample/
│       └── raw/.gitkeep
│
├── examples/
│   ├── basic-calculation.json
│   ├── full-profile.json
│   ├── relationship-analysis.json
│   ├── research-smoke-test.md
│   └── generated-report.md
│
├── tests/
│   ├── unit/
│   │   ├── test_normalization.py
│   │   ├── test_reduction.py
│   │   ├── test_dates.py
│   │   ├── test_names.py
│   │   ├── test_cycles.py
│   │   ├── test_knowledge_validation.py
│   │   └── test_claim_types.py
│   ├── property/
│   │   ├── test_reduction_properties.py
│   │   └── test_trace_consistency.py
│   ├── integration/
│   │   ├── test_profile_pipeline.py
│   │   ├── test_api.py
│   │   └── test_cli.py
│   ├── golden/
│   │   ├── cases.yaml
│   │   └── test_golden_cases.py
│   ├── research/
│   │   └── test_research_smoke.py
│   └── safety/
│       ├── test_minors.py
│       ├── test_crisis.py
│       └── test_claim_boundaries.py
│
└── scripts/
    ├── validate_knowledge.py
    ├── validate_schemas.py
    ├── generate_openapi.py
    ├── generate_examples.py
    ├── research_smoke.py
    └── release_check.py
```

Keine leeren Attrappen als angeblich fertige Funktionalität. Dateien mit Zukunftsscope müssen klar als Spezifikation oder geplantes Modul gekennzeichnet werden.

---

## 6. Fachliche Verträge

### 6.1 Personeneingabe

Definiere ein validiertes Modell mit:

- vollständigem Namen
- Geburtsname
- optional aktuellem Namen
- Geburtsdatum
- optional Geburtszeit und Geburtsort
- Sprache
- Einwilligungsstatus
- Minderjährigenstatus
- Datenquelle
- Datenqualität
- Normalisierungsentscheidungen

Geburtszeit und Geburtsort werden im Numerologie-Kern nicht benötigt, dürfen aber für spätere Erweiterungsmodule gespeichert werden, wenn dies explizit erlaubt ist.

### 6.2 Methodenkonfiguration

Jede Berechnung benötigt eine explizite Policy:

- System-ID
- Version
- Alphabet
- Normalisierungsregeln
- Meisterzahlen
- Reduktionsverhalten
- Y-Regel
- Namensbasis
- Datumsmethode
- Locale

Keine stillen Defaults außerhalb einer dokumentierten kanonischen Standardkonfiguration.

### 6.3 Berechnungsergebnis

Jedes Ergebnis enthält:

- Name der Zahl
- Rohwert
- reduzierte Darstellung
- erkannte Sonderzahlen
- verwendete Methode
- Methodenversion
- Eingabereferenz
- einzelne Rechenschritte
- Normalisierungsschritte
- Warnungen
- Konsistenzstatus
- deterministischen Hash des Berechnungsvertrags

### 6.4 Interpretation

Jede Interpretation enthält:

- referenziertes Berechnungsergebnis
- traditionelle Bedeutungen
- interpretative Hypothesen
- Gegenhypothesen
- praktische Implikationen
- Aussageklasse
- Quellenstatus
- Unsicherheitskennzeichnung
- verwendete Wissenspaketversion
- keine diagnostische Sprache

---

## 7. Ausführungsphasen

Arbeite streng in Phasen. Nach jeder Phase:

1. Dateien prüfen.
2. Tests und Validierungen ausführen.
3. Ergebnis dokumentieren.
4. Commit erstellen.
5. Erst dann nächste Phase beginnen.

### Phase 0 – Reality Check und Baseline

**Aufgaben**

- Repository-Zustand inventarisieren.
- Vorhandene Inhalte sichern.
- Aktuelle Architektur bewerten.
- Gap-Analyse erstellen.
- Arbeitsbranch anlegen.
- Baseline-Commit identifizieren.

**Dateien**

- `docs/audit/repository-baseline.md`
- `docs/audit/gap-analysis.md`
- `docs/audit/implementation-plan.md`

**Gate**

- Keine uncommitted Änderungen verloren.
- Remote und Branch dokumentiert.
- Tatsächlicher Dateibestand nachvollziehbar.

**Commit**

`chore: audit repository baseline and define implementation scope`

---

### Phase 1 – Felddefinition und Governance

**Aufgaben**

- Fachgebiet abgrenzen.
- Claim-Taxonomie definieren.
- Evidenzgrade definieren.
- Wissenschaftliche Positionierung schreiben.
- Governance und Committee-Modell erstellen.
- ADR-System einführen.

**Gate**

- Symbolische Tradition, Interpretation und Evidenz sind sauber getrennt.
- Scope und Nicht-Ziele sind eindeutig.
- Jede künftige Methodenänderung besitzt einen Reviewprozess.

**Commit**

`docs: establish field charter governance and evidence model`

---

### Phase 2 – Repository- und Tooling-Fundament

**Aufgaben**

- `pyproject.toml` mit reproduzierbaren Abhängigkeiten.
- `uv.lock`.
- Ruff, Mypy, Pytest, Hypothesis und Coverage.
- Pre-Commit.
- Makefile-Befehle.
- CI-Basis.
- Paketstruktur.
- MkDocs.

**Pflichtbefehle**

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src apps
uv run pytest
uv run mkdocs build --strict
```

**Gate**

- Alle Befehle erfolgreich.
- Keine zyklischen Imports.
- Frischer Checkout reproduzierbar.

**Commit**

`build: establish reproducible python tooling and package boundaries`

---

### Phase 3 – Kanonische pythagoreische Spezifikation

**Aufgaben**

- Exakte Buchstabenbelegung.
- Unicode- und Locale-Normalisierung.
- Meisterzahlen und Reduktion.
- Y-Regel als Policy.
- Datumsalgorithmen.
- Lebensweg-Methoden A und B.
- Namenszahlen.
- Zyklusregeln.
- Rechenbeispiele.
- Methodenversion `pythagorean-v1`.

**Gate**

- Keine Interpretationen in dieser Phase.
- Jeder Algorithmus besitzt Pseudocode, Vertrag und Testfälle.
- Streitige Varianten sind dokumentiert und nicht still vermischt.

**Commit**

`docs: define canonical pythagorean method version one`

---

### Phase 4 – Deterministischer Rechenkern

**Aufgaben**

- Normalisierung.
- Alphabet-Mapping.
- Reduktion.
- Datumsberechnung.
- Namensberechnung.
- Konsistenzprüfung:
  - Ausdrucks-Rohsumme = Vokalsumme + Konsonantensumme
- Zyklusberechnung.
- Audit-Trace.
- Service-Fassade.

**Tests**

- Unit-Tests.
- Golden Cases.
- Property-Based Tests.
- Locale- und Unicode-Fälle.
- Leap-Year- und Datumsvalidierung.
- Namen mit Akzenten, Bindestrichen und Umlauten.
- Mehrdeutige Y-Fälle.

**Gate**

- Core-Coverage mindestens 95 %.
- Golden Cases vollständig grün.
- Identische Eingabe und Policy erzeugen byte-stabile strukturierte Ergebnisse.
- Kein Netzwerk- oder LLM-Zugriff.

**Commit**

`feat: implement deterministic pythagorean calculation engine`

---

### Phase 5 – Wissensmodell und Content Packs

**Aufgaben**

- Schema für Wissenseinträge.
- Manifest und Versionierung.
- Deutsche Pythagoreische Wissensbasis.
- Quellenstatus und Traditionszuordnung.
- Gegenhypothesen.
- Qualitätsprüfung gegen Duplikate und widersprüchliche IDs.
- Trennung von Grundbedeutung, Schatten, Entwicklung und Kontext.

**Gate**

- Alle YAML-/JSON-Dateien schema-validiert.
- Keine unklassifizierten absoluten Aussagen.
- Jeder Inhalt besitzt stabile ID und Version.
- Der Rechenkern enthält keine Deutungstexte.

**Commit**

`feat: add versioned numerology knowledge model and german content pack`

---

### Phase 6 – Interpretations- und Analysemodell

**Aufgaben**

- Regelbasierte Komposition.
- Prioritätenhierarchie.
- Spannungs- und Regulationsmodell.
- Gegenhypothesen.
- Aussageklassen.
- Einzelprofil.
- Beziehungsanalyse.
- Eltern-Kind-Modus mit Schutzgrenzen.
- Entwicklungsroadmap.
- keine freie LLM-Erfindung als Kernfunktion.

**Gate**

- Jede Aussage ist auf Berechnungsdaten und Wissenseinträge rückverfolgbar.
- Keine Diagnose.
- Keine garantierte Zukunft.
- Minderjährige erhalten keine starre Identitätszuschreibung.
- Wiederholungen werden dedupliziert.

**Commit**

`feat: implement traceable interpretation and profile composition`

---

### Phase 7 – Forschungs- und Meta-Analyse-Rahmen

**Aufgaben**

- Hypothesenregister.
- Präregistrierungsformat.
- Datenprovenienz.
- Beispieldatensatz.
- Feature Engineering.
- Nullmodelle und Permutation.
- Effektstärken und Konfidenzintervalle.
- Multiple-Testing-Korrektur.
- Confounder-Dokumentation.
- reproduzierbarer Smoke-Test.
- Ergebnisbericht mit expliziter Negativresultat-Option.

**Gate**

- Forschungscode darf keine symbolischen Deutungstexte als Labels verwenden, sofern diese nicht vorher formal operationalisiert wurden.
- Explorative und konfirmatorische Analysen sind getrennt.
- Seed und Softwareversionen werden gespeichert.
- Ein kompletter Smoke-Run funktioniert offline mit Sample-Daten.

**Commit**

`feat: establish reproducible numerology research and null-model framework`

---

### Phase 8 – Safety, Ethik und Datenschutz

**Aufgaben**

- Datenschutzmodell.
- Minderjährigenschutz.
- Krisenunterbrechung.
- PII-Regeln.
- Consent- und Datenquellenmodell.
- Claims-Validator.
- Prompt-Extraktionsschutz.
- Threat Model.
- keine privaten Rohdaten im Repository.

**Gate**

- Secret Scan grün.
- PII-Testfälle vorhanden.
- Krisenfälle unterbrechen Deutungen.
- Minderjährigenfälle werden begrenzt.
- API protokolliert keine sensiblen Rohdaten standardmäßig.

**Commit**

`feat: enforce privacy safety and responsible claim boundaries`

---

### Phase 9 – CLI, API und Berichte

**CLI-Befehle**

```text
numerology methods list
numerology calculate profile
numerology calculate cycles
numerology analyze profile
numerology compare profiles
numerology validate knowledge
numerology research smoke
```

**API-Endpunkte**

```text
GET  /health
GET  /v1/methods
POST /v1/calculate/profile
POST /v1/calculate/cycles
POST /v1/interpret/profile
POST /v1/compare
POST /v1/research/smoke
```

**Aufgaben**

- strukturierte JSON-Ausgabe
- OpenAPI-Schema
- Fehlercodes
- Request IDs
- keine stillen Defaults
- Markdown-Bericht
- maschinenlesbarer Bericht
- Beispieldateien

**Gate**

- API-Integrationstests grün.
- CLI-Smoke-Test grün.
- OpenAPI-Datei reproduzierbar.
- Fehler bei ungültigen Daten sind klar und stabil.

**Commit**

`feat: expose validated calculation research and reporting interfaces`

---

### Phase 10 – Agentenschicht

Erst jetzt den dialogischen Agenten integrieren.

**Aufgaben**

- Tools für Berechnung und Wissensabfrage.
- Strukturierten Kontext an das LLM übergeben.
- Promptdateien versionieren.
- LLM-Ausgabe gegen Claims- und Safety-Modell validieren.
- Systemprompt nicht als Quelle mathematischer Wahrheit verwenden.
- Provider-Abstraktion.
- LLM optional machen.
- Mock-Provider für Tests.

**Gate**

- Plattform funktioniert ohne LLM.
- Agent kann keine Rechenergebnisse überschreiben.
- Tool-Ausgaben sind nachvollziehbar.
- Prompt-Evals für Hallucination, absolute Aussagen und Datenextraktion grün.

**Commit**

`feat: add optional llm analyst adapter over validated domain services`

---

### Phase 11 – Evaluation und Qualitätsgates

**Testklassen**

- Unit
- Property
- Golden
- Integration
- API
- CLI
- Schema
- Knowledge
- Research
- Safety
- Prompt-Evals
- Regression

**Qualitätsziele**

- Core-Coverage ≥ 95 %
- Gesamtabdeckung ≥ 85 %
- Mypy strict grün
- Ruff grün
- Docs strict grün
- Schema-Validierung grün
- Security-Workflow grün
- Reproduzierbarer Research-Smoke grün
- keine unaufgelösten `TODO` in Release-relevantem Code
- keine leeren Placeholder-Dateien

**Commit**

`test: complete regression evaluation and release quality gates`

---

### Phase 12 – Dokumentation und Beispiele

**Aufgaben**

- README auf Produkt- und Fachgebietsebene.
- Quickstart.
- Methodenhandbuch.
- API-Dokumentation.
- Forschungsleitfaden.
- Sicherheitsgrenzen.
- Beispielprofile.
- Beispielbeziehung.
- Beispiel-Forschungsbericht.
- Limitations.
- Beitragsleitfaden.

**Gate**

Ein neuer Entwickler kann in einem frischen Checkout:

1. installieren,
2. Tests ausführen,
3. ein Profil berechnen,
4. einen Bericht generieren,
5. den Research-Smoke starten.

**Commit**

`docs: publish complete platform method and contributor documentation`

---

### Phase 13 – Committee Review

Erstelle ein Review-Pack für fünf Perspektiven:

1. **Engineering**
   - Architektur
   - Determinismus
   - Tests
   - Wartbarkeit

2. **Numerologische Methodologie**
   - korrekte Spezifikation
   - dokumentierte Varianten
   - keine unbemerkte Systemvermischung

3. **Statistik und Forschung**
   - Falsifizierbarkeit
   - Nullmodelle
   - Confounder
   - Reproduzierbarkeit

4. **Safety und Privacy**
   - Minderjährige
   - Krisen
   - PII
   - Claims

5. **Produkt und UX**
   - Verständlichkeit
   - Fehlerkommunikation
   - nachvollziehbare Berichte
   - keine Autoritätsillusion

Erstelle:

- `docs/committee/final-review.md`
- `docs/committee/findings.md`
- `docs/committee/release-decision.md`

**Gate**

- Alle kritischen Findings geschlossen.
- Hohe Findings geschlossen oder formal akzeptiert.
- Freigabeentscheidung nachvollziehbar.

**Commit**

`docs: complete multidisciplinary committee review`

---

### Phase 14 – GitHub-Finalisierung und Release

**Aufgaben**

- Finalen Branch aktualisieren.
- Gesamte Testmatrix ausführen.
- `git diff`, `git status` und Dateimanifest prüfen.
- Changelog.
- Version `0.1.0`.
- Draft Pull Request erstellen.
- CI abwarten.
- Branch Protection und Required Checks dokumentieren.
- Nach Freigabe mergen.
- GitHub Release mit Release Notes erstellen.

**Nicht erlaubt**

- Direktes Pushen auf geschützten `main`.
- Force Push.
- Umgehen fehlgeschlagener Checks.
- Behauptung eines erfolgreichen Releases ohne Tag und GitHub-Release.
- unkontrollierte Zusammenfassung aller Arbeiten in einem einzigen Commit.

**Empfohlene Commit-Reihenfolge**

1. Audit
2. Felddefinition
3. Tooling
4. Methodenspezifikation
5. Rechenkern
6. Wissensmodell
7. Interpretation
8. Forschung
9. Safety
10. Schnittstellen
11. Agent
12. Evaluation
13. Dokumentation
14. Committee Review
15. Release-Metadaten

---

## 8. Pflichtvalidierung

Führe vor Abschluss mindestens aus:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src apps
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=85
uv run python scripts/validate_schemas.py
uv run python scripts/validate_knowledge.py
uv run python scripts/generate_examples.py
uv run python scripts/research_smoke.py
uv run mkdocs build --strict
uv build
git status --short
git diff --check
```

Zusätzlich:

- API lokal starten und Healthcheck ausführen.
- CLI mit mindestens einem Golden Case ausführen.
- Frischen Installations-Smoke-Test in sauberer Umgebung durchführen.
- Prüfen, dass keine Secrets, Rohdaten oder lokalen Pfade committed wurden.
- Prüfen, dass alle generierten Beispiele reproduzierbar sind.

---

## 9. Definition of Done

Das Projekt gilt erst als fertig, wenn:

- das Fachgebiet formal dokumentiert ist,
- die kanonische Methode versioniert ist,
- der Rechenkern deterministisch arbeitet,
- jede Berechnung eine Auditspur besitzt,
- Wissensinhalte getrennt und versioniert sind,
- Interpretationen rückverfolgbar und hypothetisch gekennzeichnet sind,
- empirische Forschung ergebnisoffen möglich ist,
- Safety- und Datenschutzregeln technisch geprüft werden,
- CLI und API funktionieren,
- der Agent nur als kontrollierte Adapterschicht arbeitet,
- Tests, Typecheck, Lint, Docs und Build grün sind,
- Committee Review abgeschlossen ist,
- ein echter Pull Request und ein nachvollziehbares Release existieren.

Nicht ausreichend sind:

- nur ein Systemprompt,
- nur eine README,
- ein ungetesteter Rechner,
- eine Sammlung fertiger Deutungstexte,
- ein Chatbot ohne Rechenkern,
- ein angeblicher Forschungsansatz ohne Nullmodelle und Reproduzierbarkeit.

---

## 10. Abschlussbericht

Nach der Umsetzung liefere einen verifizierten Abschlussbericht mit:

- Repository-URL
- Branch
- Pull-Request-URL
- Commit-Liste
- Release/Tag
- vollständigem Dateimanifest
- Testbefehlen und tatsächlichen Ergebnissen
- Coverage
- offenen Risiken
- akzeptierten Trade-offs
- nicht implementierten Zukunftsmodulen
- Rollback-Hinweisen
- klarer Aussage, was geprüft und was nicht geprüft wurde

Keine pauschale Aussage wie „alles fertig“. Jede Erfolgsbehauptung benötigt einen technischen Nachweis.

---

## 11. Zukunftsmodule – ausdrücklich nicht Teil von Version 1

Erst nach stabilem Release planen:

- Chaldäische Engine
- Kabbalistische/Gematria-Engine
- Astrologie
- Human Design
- Enneagramm
- Web-Frontend
- Benutzerkonten
- persistente private Profile
- Vektor-Retrieval
- Mehrsprachigkeit über Deutsch und Englisch hinaus
- automatisierte Publikationspipeline
- großskalige öffentliche Forschungsdatensätze

Diese Module müssen über definierte Plugin- und Methodenschnittstellen ergänzt werden, ohne den pythagoreischen Kern zu verändern.

---

# Endgültige Priorität

Baue zuerst das **Feld**, dann das **System**, dann den **Agenten**.

Die Reihenfolge lautet:

```text
Fachspezifikation
→ Methodenversionen
→ Rechenkern
→ Wissensmodell
→ Interpretationsmodell
→ Forschung und Evaluation
→ Safety
→ API und CLI
→ Agent
→ Release
```

Ein Agent, der sich gut unterhält, aber kein belastbares Fachsystem besitzt, ist nicht das Produkt.
Das Produkt ist die überprüfbare Numerologie-Domänenplattform.
