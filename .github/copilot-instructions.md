# Copilot Instructions — Numerology Analyst Agent

> Repository-level Instruktionen für GitHub Copilot und Coding-Agenten.
> **Quelle der Wahrheit:** `NUMEROLOGIE_ANALYST_AGENT_MASTER_IMPLEMENTIERUNGSPROMPT.md` (extern), `PROJECT_CHARTER.md`.
> **Stand:** 2026-07-25 · **Sprache:** Deutsch (Fachbegriffe auf Englisch, wo idiomatisch)

---

## Projektbeschreibung

Der **Numerology Analyst Agent** ist eine auditierbare Domänenplattform für numerologische Berechnung, strukturierte Deutung, Forschung und agentische Nutzung — aufgeteilt in fünf getrennte Ebenen (Fachmodell, deterministischer Rechenkern, versioniertes Wissensmodell, empirischer Forschungsrahmen, App-/Agent-Schicht). V1 implementiert ausschließlich einen pythagoreischen Standard (`pythagorean-v1`). Numerologie ist empirisch nicht validiert; das Projekt gibt keine medizinischen oder psychologischen Diagnosen.

---

## Verbindlicher Technologie-Stack

| Schicht | Technologie | Regel |
|---------|-------------|-------|
| Sprache | **Python 3.12+** | Keine veraltete Syntax |
| Abhängigkeiten / Venv | **`uv`** | Reproduzierbar, `uv.lock` ist Quelle der Wahrheit |
| Verträge / Validierung | **`pydantic` v2** | Strikte Modelle, keine `BaseModel`-Locken ohne Validierung |
| Unit-Tests | **`pytest`** | Standard |
| Property-Based Tests | **`hypothesis`** | Pflicht für Reduktion, Trace, Invarianten |
| Lint + Format | **`ruff`** | Strikt, kein Ausnehmen von Regeln ohne Begründung |
| Typen | **`mypy` strict** | **Keine `any`-Types.** Keine `# type: ignore` ohne Begründung |
| HTTP-API | **FastAPI** | OpenAPI generiert |
| CLI | **Typer** | Typisiert |
| Wissenspakete | **YAML / validiertes JSON** | Schema-validiert |
| Forschungsdaten | DuckDB + Parquet | Reproduzierbar |
| Doku | **MkDocs Material** | `--strict` |
| CI | GitHub Actions | Pflicht-Checks |
| Versionierung | **SemVer** | Klar, maschinenlesbar |

**Explizit NICHT im Basiskern:** keine Datenbank, kein Vektorstore, kein LLM-Framework.

### Determinismus-vor-LLM-Prinzip (BINDEND)

**Alle Berechnungen müssen ohne Sprachmodell vollständig funktionieren.**

Ein LLM darf **ausschließlich**:
- validierte Ergebnisse erklären,
- Deutungshypothesen formulieren,
- Ausgaben sprachlich anpassen.

Ein LLM darf **niemals**:
- Zahlen selbst (un kontrolliert) berechnen,
- fehlende Daten erfinden,
- Methodenversionen vermischen,
- validierte Rechenergebnisse überschreiben.

Das bedeutet für Code-Arbeit: **kein** `import openai` / `import anthropic` / `import requests` in `src/numerology_engine/`. Netzwerk- oder LLM-Zugriff im Rechenkern ist ein harter Verstoß.

---

## Die sechs Aussageklassen (BINDEND)

Jedes Dokument, jedes Schema, jede API-Ausgabe, jeder Bericht und jeder Testfall muss zwischen folgenden Aussageklassen unterscheiden:

| Klasse | Bedeutung |
|--------|-----------|
| `input_fact` | Vom Nutzer / Datensatz gelieferte Information |
| `calculation_fact` | Deterministisch berechnetes Ergebnis |
| `traditional_claim` | Überlieferte numerologische Bedeutung |
| `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation |
| `empirical_evidence` | Ergebnis einer statistischen Untersuchung |
| `practical_suggestion` | Nicht verbindliche Handlungsoption |

Ohne diese Trennung verschmilzt der Agent Tradition (unverifiziert), Berechnung (deterministisch) und Deutung (hypothetisch) zu einer autoritären Aussage, die nicht mehr falsifizierbar ist. Das ist unzulässig (§2.3 Master-Prompt).

---

## Coding-Standards

- **Keine `any`-Types.** Verwende stattdessen `Unknown`, Generics oder Protokolle.
- **Kein `# type: ignore` ohne schriftliche Begründung** im Kommentar.
- **Keine stillen Defaults** außerhalb einer dokumentierten kanonischen Standardkonfiguration.
- **Keine Methodenversionen vermischen** (`pythagorean-v1` ist kanonisch; chaldäische Werte sind eine Verunreinigung).
- **Keine erfundenen Daten.** Wenn Daten fehlen, explizit als fehlend markieren — nicht raten.
- **Keine zyklischen Imports** zwischen den Paketen (`numerology_domain`, `_engine`, `_knowledge`, `_interpretation`, `_research`, `_safety`, `_agent`, `apps/api`, `apps/cli`).
- **Keine Diagnosesprache** in Interpretations- oder Wissenstexten (Blacklist via Claims-Validator).
- **Keine leeren Placeholder-Dateien**, die fertige Funktionalität vortäuschen.
- **Jede Berechnung bekommt einen Audit-Trace** und einen deterministischen Hash.

---

## Commit-Konvention

- **Sprache:** Deutsch
- **Format:** `<type>: <kurzbeschreibung>`
- **Fokus auf das Warum**, nicht auf das Was
- **Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `build`, `ci`

Beispiele aus dem Master-Prompt:

- `chore: audit repository baseline and define implementation scope`
- `docs: establish field charter governance and evidence model`
- `feat: implement deterministic pythagorean calculation engine`
- `test: complete regression evaluation and release quality gates`

---

## Branch-Konvention

- **Ein Branch pro Issue oder vertikalem Slice** (`feat/<phase>-<scope>`, `fix/<issue>-<kurz>`, `docs/<scope>`).
- **Draft-PR früh**, sobald erste Teilergebnisse stehen.
- **Required Checks müssen grün sein** vor Merge:
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src apps`
  - `uv run pytest --cov=src --cov-fail-under=85`
  - `uv run python scripts/validate_knowledge.py` (ab Phase 5)
  - `uv run mkdocs build --strict` (ab Phase 2)
- **Squash-Merge** nach Review.
- **Keine Direktpushes** auf `main`, **kein Force-Push**, **kein `--no-verify`**.
- **Phasen-Commits** orientieren sich an der Phasenfolge im Master-Prompt.

---

## Tabu-Liste (unverhandelbar)

Folgende Aktionen sind **strikte Verstöße** und führen zu Blockade:

- **Kein Vermischen von Methodenversionen** (z.B. chaldäische Buchstabenwerte in pythagoreischer Methode).
- **Keine stillen Defaults** außerhalb der dokumentierten kanonischen Konfiguration.
- **Keine erfundenen Daten** (insbesondere `empirical_evidence` ohne echten statistischen Nachweis).
- **Keine Diagnosen** (medizinisch, psychologisch, identitätsstiftend).
- **Keine garantierte Zukunft** in Interpretationen.
- **Keine starre Identitätszuschreibung** bei Minderjährigen.
- **Keine privaten personenbezogenen Daten** im Repository.
- **Keine Secrets / API-Keys / Tokens** in Code, Config, Tests, Commits oder Logs.
- **Keine leeren Placeholder**, die Fertigkeit vortäuschen.
- **Kein LLM-Aufruf** im Rechenkern (`numerology_engine`).
- **Kein Netzwerkzugriff** im Rechenkern.

---

## Rollen / Agenten

Für fachlich spezialisierte Aufgaben stehen in `.github/agents/` sechs Agent-Verträge zur Verfügung:

| Agent | Fokus |
|-------|-------|
| `domain-architect.agent.md` | Numerologie-Domäne, Claim-Taxonomie, Methodenspezifikation |
| `calculation-engineer.agent.md` | Deterministischer Rechenkern, Property-Based Tests, Coverage ≥ 95 % |
| `knowledge-editor.agent.md` | Versionierte Content Packs, Schema-Validierung, Quellenstatus |
| `research-reviewer.agent.md` | Nullmodelle, Permutation, Multiple-Testing, Präregistrierung |
| `safety-reviewer.agent.md` | Minderjährigenschutz, Krisenunterbrechung, PII-Regeln, Claims-Validator |
| `release-engineer.agent.md` | Branch Protection, Required Checks, SemVer, GitHub Releases |

Jeder Agentenvertrag enthält die neun Pflichtfelder (Zweck, erlaubte Pfade, erforderliche Inputs, verbotene Aktionen, Pflichtbefehle, erwartete Artefakte, Übergabeformat, Abbruch-/Eskalationsbedingungen, technische Nachweise).

---

## Weiterführende Doku

- `PROJECT_CHARTER.md` — Was / Warum von V1
- `ROADMAP.md` — 15 Phasen (0–14) mit Gates
- `docs/audit/` — Repository-Baseline, Gap-Analyse, Übersetzungsplan
- `docs/field/scientific-positioning.md` (folgt) — Wissenschaftliche Positionierung
- `docs/adr/` (folgt) — Architecture Decision Records
