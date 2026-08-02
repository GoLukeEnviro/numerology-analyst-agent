# Gap-Analyse — Numerology Analyst Agent

> **Dokumenttyp:** Audit / Lückenanalyse  
> **Stand der Kernabschnitte:** 2026-07-26 (V1.2 — State Reconciliation nach v0.1.3)  
> **Sprache:** Deutsch  
> **Hinweis 2026-08-02:** Die Abschnitte unten sind die **historische** Gap-Matrix
> ab Foundation `v0.1.3`. Der **aktuelle** post-RC1-Stand (RC1 getaggt, PR #34/#35
> gemergt, Staging/Committee/Beta noch offen) steht in
> `docs/audit/current-state-numra-post-rc1-2026-08-02.md` und im Statusblock von
> `ROADMAP.md`. Historische „0.1.4 ausstehend“-Formulierungen hier nicht als
> Live-Status lesen.

## 1. Historische Baseline (25. Juli 2026)

> Die folgende Baseline beschreibt den Zustand **vor** der Implementierung von v0.1.3.
> Sie dient als Referenz für die Entwicklung des Projekts. Der aktuelle Ist-Zustand
> nach v0.1.3 steht in Abschnitt 2.

> Laut Session-Memory hat eine Vorgängersession fälschlich behauptet, 51 Dateien,
> Roadmap, Gap-Analyse, Committee-Pack, Archiv und Manifest erstellt zu haben.
> Diese Datei ist die **tatsächliche** Gap-Analyse nach realer Verifikation.

### Verifikations-Output (2026-07-25)

```text
Get-ChildItem -Force | Select-Object Mode, Length, Name

Mode   Length Name
----   ------ ----
d--h-         .git
-a---     262 README.md
```

```text
git log --oneline -5
64536c2 (HEAD -> main, origin/main, origin/HEAD) Initial commit
```

```text
git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

### Was existiert (verifiziert)

- **1 Datei:** `README.md` (262 Bytes — nur ein Projekt-Header, keine Struktur).
- **1 Commit:** `64536c2` "Initial commit" auf `main` und `origin/main`.
- **Keine** Branches außer `main`.
- **Keine** Tags.
- **Keine** Pull Requests.
- **Keine** GitHub Actions Workflows.
- **Keine** Paketstruktur, kein `pyproject.toml`, keine CI, keine Tests.

### Was NICHT existiert (verifiziert — entgegen Vorgängersession-Behauptung)

- Keine Roadmap, keine Gap-Analyse, kein Committee-Pack, kein Archiv, kein Manifest.
- Keine 51 Dateien. Realität: README-Header nur.

### Diese Plan-Session

Diese Session erstellt **ausschließlich** die 5 Plan-Dokumente gemäß Auftrag:

1. `PROJECT_CHARTER.md` ✅ (diese Session)
2. `ROADMAP.md` ✅ (diese Session)
3. `docs/audit/gap-analysis.md` ✅ (diese Datei)
4. `docs/audit/implementation-plan.md` ✅ (diese Session)
5. `.planning/notes/master-plan-defaults.md` ✅ (diese Session)

**Keine** Code-Dateien, kein Tooling-Setup, kein Git-Push.

---

## 2. Aktueller Ist-Zustand nach v0.1.3 (26. Juli 2026)

### Was existiert (verifiziert)

- **66 getrackte Dateien** in 5 Paketen (`numerology_domain`, `numerology_engine`, `numerology_cli`, `numerology_api`, Tests).
- **3 Tags:** `v0.1.0`, `v0.1.2`, `v0.1.3`.
- **4 gemergte PRs:** #5 (Branch Protection), #6 (Contract Integrity), #7 (Release-Doku), #8 (Release-Notes-Archiv).
- **1 CI-Workflow** mit 2 Jobs: `Quality Gates` (ruff, mypy, pytest + coverage) und `Package Smoke` (Wheel-Build + Fresh-Venv-Install).
- **Vollständige Toolchain:** `uv`, `ruff`, `mypy strict`, `pytest`, `hypothesis`, `coverage`.
- **Typer-CLI** mit 2 Befehlen: `numerology version`, `numerology profile`.
- **3 versionierte JSON-Schemas** im Wheel: `person-input-v1`, `calculation-result-v1`, `method-policy-v1`.
- **118 Tests** in 4 Kategorien: Unit, Property, Golden, Integration.
- **Core-Coverage:** 95,73 % (`numerology_engine`).
- **Gesamt-Coverage:** 92,58 % (`src`).
- **Deterministischer Rechenkern:** Life Path A + B, Meisterzahlen 11/22/33, karmische Marker 13/14/16/19, Normalisierung `de-direct-v1`, Audit-Trace, versionierter Hash-Envelope.
- **Verpflichtendes `as_of_date`** (kein `date.today()`-Fallback).
- **Branch Protection** und Required Checks aktiv.
- **Release Notes** unter `docs/releases/v0.1.3.md`.

### Was NICHT existiert (nach v0.1.3)

- Keine Namenszahlen (Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-, Persönlichkeits-, Reifezahl).
- Keine Namenssegmentierung oder Y-Klassifikation.
- Keine Zyklen (persönliches Jahr/Monat/Tag, Pinnacles, Challenges).
- Kein Wissensmodell (`numerology_knowledge/`).
- Keine Interpretation (`numerology_interpretation/`).
- Kein Safety-Subsystem (`numerology_safety/`).
- Keine FastAPI.
- Kein Agent (`numerology_agent/`).
- Kein Forschungsrahmen (`numerology_research/`).
- Keine MkDocs-Dokumentation.
- Kein Committee-Prozess.

---

## 3. Soll-Zustand (Master-Prompt-Vision)

Das vollständige V1-System umfasst laut Master-Prompt:

- **5 Ebenen** der Plattform (Fachmodell, Rechenkern, Wissensmodell,
  Forschungsrahmen, App-Schicht).
- **6 Aussageklassen** im gesamten System sichtbar.
- **15 Phasen (0–14)** mit definierten Gates und Commits.
- **~70+ Dateien** in klarer Repository-Struktur (Master-Vertrag §5).
- **Verbindlicher Tech-Stack** (Python 3.12, uv, pydantic v2, pytest, hypothesis,
  ruff, mypy strict, FastAPI, Typer, DuckDB, Polars, MkDocs Material, SemVer).
- **Definition of Done** (Master-Vertrag §9) mit 13 Kriterien.

Siehe `PROJECT_CHARTER.md` und `ROADMAP.md` für die ausführliche Übersetzung.

---

## 3. Gap-Kategorien

Pro Kategorie: **Ist** / **Soll** / **Gap** / **Priorität** / **kritische Blocker**.

**Prioritäts-Skala:**

- **P0 (blockierend)** — Phase X kann nicht starten, solange nicht gelöst.
- **P1 (hoch)** — Blockiert Folgemonate, aber Phase kann starten.
- **P2 (mittel)** — Vor Release 0.1.4 zu lösen.
- **P3 (niedrig)** — Schönheit / Polishing vor Release.

---

### 3.1 Governance

| Feld | Wert |
|------|------|
| **Ist** | ADRs `0001`–`0006` vorhanden. Claim-Taxonomie in Domain-Modellen (`enums.py`). Kein separates `GOVERNANCE.md`. Kein Committee-Modell. |
| **Soll** | `GOVERNANCE.md`, `docs/field/claim-taxonomy.md`, `docs/field/evidence-grading.md`, ADRs `0001`–`0004`, `docs/committee/review-model.md`. |
| **Gap** | ADR-System etabliert. Claim-Taxonomie als Enum vorhanden. Governance-Dokumente und Committee-Modell fehlen noch. |
| **Priorität** | **P2** (für 0.2.0/0.3.0). |
| **Blocker** | Keine für 0.1.4. Committee wird erst für 1.0.0 benötigt. |

---

### 3.2 Tooling

| Feld | Wert |
|------|------|
| **Ist** | `pyproject.toml`, `uv.lock`, `.gitignore`, `ruff`, `mypy strict`, `pytest`, `hypothesis`, `coverage`, GitHub Actions CI (2 Jobs). Kein Makefile, keine pre-commit, kein MkDocs. |
| **Soll** | Vollständige Toolchain: uv, ruff, mypy strict, pytest, hypothesis, coverage, pre-commit, Makefile, 4 GitHub-Workflows (ci, security, docs, release), MkDocs-Material. |
| **Gap** | Basistoolchain vollständig. Makefile, pre-commit, MkDocs, Security/Docs/Release-Workflows fehlen. |
| **Priorität** | **P2** (für 0.2.0/0.3.0). |
| **Blocker** | Keine für 0.1.4. Bestehende Toolchain ist ausreichend. |

---

### 3.3 Methodenspezifikation

| Feld | Wert |
|------|------|
| **Ist** | ADRs `0001`–`0004` dokumentieren Y-Regel, Umlaute, Mehrfachnamen, Core/Active-Name. Normalisierung `de-direct-v1` implementiert. Keine vollständige Methodenspezifikation in `docs/methods/`. |
| **Soll** | `docs/methods/pythagorean-v1.md`, `normalization.md`, `reductions.md`, `names.md`, `dates.md`, `cycles.md`, `compatibility.md`. Methodenversion `pythagorean-v1`. |
| **Gap** | ADR-Entscheidungen vorhanden. Vollständige Methodenspezifikation fehlt (Welle 2). |
| **Priorität** | **P1** (für Welle 2 vor 0.1.4-Implementierung). |
| **Blocker** | Keine neue Berechnung ohne vollständige Spec. Bestehende Life-Path-Berechnung ist durch ADRs abgedeckt. |

---

### 3.4 Rechenkern

| Feld | Wert |
|------|------|
| **Ist** | `src/numerology_engine/` mit normalization, reduction, alphabet, dates, trace, service. Life Path A + B, Meisterzahlen, karmische Marker. Coverage 95,73 %. **Keine** Namenszahlen, keine Zyklen. |
| **Soll** | `src/numerology_engine/` mit normalization, reduction, alphabet, names, dates, cycles, compatibility, trace, service. Coverage ≥ 95 %. Byte-stabile Ergebnisse. Golden Cases. Property-Based Tests. |
| **Gap** | Life-Path-Kern vollständig. Namenszahlen, Zyklen, Compatibility fehlen. |
| **Priorität** | **P0** für 0.1.4 (Namenszahlen), **P1** für 0.1.5 (Zyklen). |
| **Blocker** | Ohne Namenszahlen kein vollständiges Profil (0.1.4). |

---

### 3.5 Wissensmodell

| Feld | Wert |
|------|------|
| **Ist** | Keine `knowledge/`-Verzeichnis. Kein Schema, kein Manifest, keine Wissenspakete. |
| **Soll** | `schemas/knowledge-entry.schema.json`, `knowledge/manifest.yaml`, deutsche Pythagoreische Wissensbasis (numbers-1-9, master-numbers, compound-numbers, karmic-debts, cycles, relationships). |
| **Gap** | 100 % Wissensmodell fehlt. |
| **Priorität** | **P1** (Phase 5, abhängig von Phase 3+4). |
| **Blocker** | Default #4 erlaubt KI-generierten Draft, aber nur als `traditional_claim` mit `quellenstatus: tradition_unverified`. Wenn diese Markierung fehlt, ethisch/technisch kritisch. |

---

### 3.6 Interpretation

| Feld | Wert |
|------|------|
| **Ist** | Keine `numerology_interpretation`-Pakete. Keine Kompositionsregeln. |
| **Soll** | `src/numerology_interpretation/` mit composer, tensions, counter_hypotheses, evidence, service. Regelbasiert, rückverfolgbar. Eltern-Kind-Modus mit Schutzgrenzen. |
| **Gap** | 100 % Interpretationsmodell fehlt. |
| **Priorität** | **P1** (Phase 6, abhängig von Phase 4+5). |
| **Blocker** | Diagnose-Sprache muss verhindert werden; Identitätszuschreibung bei Minderjährigen verboten (§2.3). |

---

### 3.7 Forschung

| Feld | Wert |
|------|------|
| **Ist** | Kein `research/`-Verzeichnis. Keine Hypothesen, keine Pipelines, keine Statistik. |
| **Soll** | `research/` mit registry, queries, pipelines (ingest, clean, feature_engineering, evaluate), reports, sample data. Hypothesenregister, Präregistrierungs-Template, Nullmodelle, Permutationstests, Effektstärken, Power-Analysen, Multiple-Testing-Korrektur. |
| **Gap** | 100 % Forschungsrahmen fehlt. |
| **Priorität** | **P2** (Phase 7, abhängig von Phase 2+4). |
| **Blocker** | Default #3: Synthetische Testdaten für V1, öffentliche Biografien (Wikipedia) optional später. Keine PII in Git (Phase 8 prüft). |

---

### 3.8 Safety

| Feld | Wert |
|------|------|
| **Ist** | Keine `numerology_safety`-Pakete. Kein Threat Model. Keine PII-Regeln. Keine Krisen-Logik. |
| **Soll** | `src/numerology_safety/` mit privacy, minors, crisis, claims. `docs/safety/privacy.md`, `minors.md`, `mental-health-boundaries.md`, `responsible-interpretation.md`. `docs/architecture/threat-model.md`. |
| **Gap** | 100 % Safety fehlt. |
| **Priorität** | **P1** (Phase 8, abhängig von Phase 4). |
| **Blocker** | PII-Leak, Krisen-Andeutungen ohne Unterbrechung, Minderjährigen-Zuschreibung — alle ethisch kritisch. Release ohne Safety nicht vertretbar. |

---

### 3.9 API / CLI

| Feld | Wert |
|------|------|
| **Ist** | Keine `apps/`-Verzeichnis. Keine FastAPI, keine Typer-CLI. Keine OpenAPI. |
| **Soll** | `apps/api/` mit main, dependencies, routes (health, methods, calculate, interpret, compare). `apps/cli/main.py`. 7 CLI-Befehle, 7 API-Endpunkte. Reproduzierbare OpenAPI. |
| **Gap** | 100 % Schnittstellen fehlen. |
| **Priorität** | **P2** (Phase 9 Core, abhängig von Phase 4 + Basis-Schemas + Phase 8; Research-Endpunkt abhängig von Phase 7). |
| **Blocker** | Stille Defaults verletzen §6.2 (Methodenkonfiguration). OpenAPI muss deterministisch sein. **Hinweis V1.1:** Core CLI/API ist von Phase 7 entkoppelt — kommt in Release 0.3.0, der Research-Endpunkt `/v1/research/smoke` erst in 0.4.0 (Lukes Korrektur #6). |

---

### 3.10 Agent

| Feld | Wert |
|------|------|
| **Ist** | Keine `numerology_agent`-Pakete. Keine Prompts, keine Provider-Abstraktion. |
| **Soll** | `src/numerology_agent/` mit context, tools, renderer, service. `prompts/system/analyst-v1.md`, `prompts/tasks/`, `prompts/eval/`. Provider-Abstraktion mit Mock-Provider (Default #5). |
| **Gap** | 100 % Agent fehlt. |
| **Priorität** | **P2** (Phase 10, abhängig von Phase 9). |
| **Blocker** | LLM darf keine calc-facts überschreiben (§2.4). Mock-Only in V1. |

---

### 3.11 Tests

| Feld | Wert |
|------|------|
| **Ist** | Keine `tests/`-Verzeichnis. Keine Unit-Tests, keine Property-Tests, keine Golden Cases, keine Integration/Safety/Research-Tests. |
| **Soll** | `tests/unit/`, `tests/property/`, `tests/integration/`, `tests/golden/`, `tests/research/`, `tests/safety/`. Coverage ≥ 95 % Core, ≥ 85 % gesamt. |
| **Gap** | 100 % Tests fehlen. |
| **Priorität** | **P0** für Core (Phase 4), **P1** für Rest (Phase 11). |
| **Blocker** | Ohne Tests kein Determinismus-Nachweis, kein Release. |

---

### 3.12 Dokumentation

| Feld | Wert |
|------|------|
| **Ist** | `README.md` mit nur einem Header (262 Bytes). |
| **Soll** | `docs/` mit index, getting-started, architecture/, field/, methods/, research/, safety/, committee/, adr/. MkDocs-Material, `mkdocs build --strict` grün. |
| **Gap** | >95 % Doku fehlt. README existiert, ist aber nur Header. |
| **Priorität** | **P2** (Phase 12, nach Feature-Freeze). |
| **Blocker** | Quickstart muss 1:1 mit Realität matchen — sonst bricht Onboarding. |

> **Hinweis:** Diese Plan-Session erstellt 4 zusätzliche Markdown-Dateien
> (`PROJECT_CHARTER.md`, `ROADMAP.md`, `docs/audit/implementation-plan.md`,
> `.planning/notes/master-plan-defaults.md` plus diese Datei). Diese sind
> **Plan-Dokumente**, kein Ersatz für die feature-bezogene Doku aus Phase 12.

---

### 3.13 Committee

| Feld | Wert |
|------|------|
| **Ist** | Keine `docs/committee/`. Kein Review-Modell, keine Findings, keine Release-Decision. |
| **Soll** | `docs/committee/review-model.md`, `release-checklist.md`, `decision-template.md`, `final-review.md`, `findings.md`, `release-decision.md`. 5 Review-Perspektiven. |
| **Gap** | 100 % Committee fehlt. |
| **Priorität** | **P2** (Phase 13, nach Phase 12). |
| **Blocker** | Release ohne Committee-Freigabe nicht zulässig (Master-Prompt §9). |

---

### 3.14 Release

| Feld | Wert |
|------|------|
| **Ist** | Kein Tag. Keine GitHub Release. Keine Branch Protection. Keine CHANGELOG. |
| **Soll** | Version `0.1.0`, GitHub Release mit Notes, Branch Protection, Required Checks, CHANGELOG.md, CITATION.cff, LICENSE. |
| **Gap** | 100 % Release-Artefakte fehlen. |
| **Priorität** | **P2** (Phase 14, nach Phase 13). |
| **Blocker** | Kein Force-Push, keine Direct-Pushes auf `main`, keine Behauptung eines fertigen Releases ohne Tag (Default #8, Master-Prompt §7 Phase 14). |

---

## 4. Klare Aussage

> **Nicht vorhanden: 100 % aller Phasen-Artefakte (Phase 0–14).**
>
> **Realität:** `README.md`-Header nur. 1 Commit (`64536c2`). Working tree clean.
>
> Diese Plan-Session fügt 5 Plan-Dokumente hinzu (`PROJECT_CHARTER.md`,
> `ROADMAP.md`, `docs/audit/gap-analysis.md`, `docs/audit/implementation-plan.md`,
> `.planning/notes/master-plan-defaults.md`). Diese ersetzen **keine**
> Phase-Implementierung, sondern definieren Scope, Lücken und Plan.

### Blockierende P0-Gaps (vor Start von M2)

1. **Governance** (P0): Claim-Taxonomie fehlt → Phase 1 muss zuerst.
2. **Tooling** (P0): Keine Toolchain → Phase 2 muss zuerst.
3. **Methodenspec** (P0): Keine Spezifikation, OFFEN-Punkte ungelöst →
   Phase 3 muss zuerst.
4. **Rechenkern** (P0): Keine Berechnung → Phase 4 (XL) blockiert fast alles.
5. **Tests Core** (P0): Ohne Tests kein Determinismus-Nachweis.

### Sequenz der Schließung

- M1 (Phase 0–3) schließt: Governance + Tooling + Methodenspec.
- M2 (Phase 4–6) schließt: Rechenkern + Wissensmodell + Interpretation.
- M3 (Phase 7–10) schließt: Forschung + Safety + API/CLI + Agent.
- M4 (Phase 11–14) schließt: Tests-Vollständigkeit + Doku + Committee + Release.

---

## 5. OFFEN-Punkte (nicht vom Master-Prompt spezifiziert)

Diese Punkte sind **nicht erfindbar** — sie müssen in Phase 3 von Luke
(Principal) entschieden oder durch research geklärt werden.

| ID | Thema | Konsequenz bei Nicht-Entscheidung |
|----|-------|-----------------------------------|
| OFFEN-1 | Y-Regel (Vokal vs. Konsonant je nach Kontext) | Phase 3 blockiert → Phase 4 blockiert |
| OFFEN-2 | Umlaut-Normalisierung (ä, ö, ü) | Phase 3 blockiert |
| OFFEN-3 | Akzent-Behandlung (é, ñ) | Phase 3 blockiert |
| OFFEN-4 | Mehrfachnamen / Bindestriche | Phase 3 blockiert |
| OFFEN-5 | Geburtsname vs. aktueller Name als Policy-Feld | Phase 3 blockiert |
| OFFEN-6 | Phase-14-Commit-Message | Master-Prompt schweigt; Vorschlag in ROADMAP Phase 14 |
| OFFEN-7 | Default #3: Bevorzugt synthetische Daten in V1 — konkrete Sample-Größe? | Phase 7 muss Sample-Größe definieren |
| OFFEN-8 | Default #4: KI-Autorschaft — welches Modell für Drafts? | Phase 5 muss Modell im Manifest vermerken |

→ Siehe auch `PROJECT_CHARTER.md` §6 und `.planning/notes/master-plan-defaults.md`.

---

## 6. Querverweise

| Siehe | Für |
|-------|-----|
| `PROJECT_CHARTER.md` | Mission, Aussageklassen, V1-Scope, Release-Strategie |
| `ROADMAP.md` | 15 Phasen (0–14) mit Gates, Commits, Aufwand |
| `docs/audit/implementation-plan.md` | Übersetzungsplan, Dependency Graph, kritischer Pfad, Risiken |
| `docs/v1-minimal-scope.md` | Details zu Release 0.1.0 (Vorgabe Luke) |
| `.planning/notes/master-plan-defaults.md` | Autonome Defaults |
| `docs/governance/master-implementation-contract.md` | Interner Master-Vertrag (Quelle der Wahrheit) |
| `.github/agents/*.agent.md` | Agenten-Verträge (Delegation) |

---

## 7. Release-Strategie-Anpassung (V1.1)

> Lukes Review (2026-07-25) hat die Roadmap in eine langfristige
> **North-Star-Roadmap** (alle 15 Phasen) und eine operative
> **Release-Roadmap** (0.1.0 → 0.4.0) getrennt. Details siehe
> `PROJECT_CHARTER.md` §6b, `ROADMAP.md` *Release-Strategie*, und
> `docs/v1-minimal-scope.md`.

### Konsequenz für diese Lückenanalyse

- **North-Star bleibt verbindlich:** Die hier katalogisierten Lücken bleiben
  für das Endprodukt V1 relevant. Keine Lücke wird "weggeschnitten".
- **0.1.0 hat deutlich schmaleren Scope:** Release 0.1.0 umfasst nur die
  Phasen 0–4 (Governance, Tooling, Methodenspec, Rechenkern + CLI-Basis +
  Tests). Die Lücken in den Bereichen Wissensmodell (3.5), Interpretation
  (3.6), Forschung (3.7), Safety-vollständig (3.8), API/CLI-vollständig
  (3.9), Agent (3.10), Doku (3.12), Committee (3.13) und Release (3.14)
  sind für 0.1.0 **nicht blockierend** — sie blockieren erst die
  entsprechenden späteren Releases.
- **Phase 7 (Forschung) ist Preview:** Release 0.4.0 ist explizit als
  *Preview* markiert, nicht als wissenschaftliche Validierung. Keine
  empirische Behauptung als "bestätigt" verkaufen.
- **Phase 9 (API/CLI) ist entkoppelt:** Core CLI/API (Phase 4 + Schemas +
  Phase 8) kommt in 0.3.0; der Research-Endpunkt `/v1/research/smoke`
  (Phase 7) erst in 0.4.0.

### P0-Blocker für 0.1.4 (Complete Core Profile)

1. **Methodenspezifikation (P1):** Vollständige Spec für Namenszahlen, Y-Klassifikation, Segmentierung muss vor Implementierung stehen (Welle 2).
2. **Rechenkern-Namenszahlen (P0):** Namenssegmentierung, Y-Klassifikation, Ausdrucks-/Seelenstreben-/Persönlichkeits-/Reifezahl müssen implementiert werden.
3. **Tests Core (P0):** Golden Cases, Unit-Tests, Property-Tests für alle neuen Zahlen.
4. **Legacy-Kompatibilität (P0):** Bestehender `0.1.3`-Vertrag darf nicht still verändert werden.

### Bereits geschlossene P0-Blocker (durch v0.1.3)

- ✅ **Tooling:** `pyproject.toml`, `uv.lock`, ruff, mypy strict, pytest, hypothesis, CI vorhanden.
- ✅ **Rechenkern-Basis:** Life Path A + B, Meisterzahlen, karmische Marker, Audit-Trace, Hash-Envelope.
- ✅ **Tests Core:** 118 Tests, Core-Coverage 95,73 %, Gesamt-Coverage 92,58 %.
- ✅ **CLI-Basis:** `numerology version`, `numerology profile` mit verpflichtendem `--as-of-date`.
- ✅ **Schemas:** 3 versionierte JSON-Schemas im Wheel, Drift-Check in CI.
- ✅ **Branch Protection:** Required Checks aktiv.

---

*Ende der Gap-Analyse — Numerology Analyst Agent V1.2 (Stand 2026-07-26)*
