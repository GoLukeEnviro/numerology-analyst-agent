# Numerology Analyst Agent

> Auditierbare Domänenplattform für numerologische Berechnung, strukturierte Deutung, Forschung und agentische Nutzung.

**Status:** Plan-Phase (Plan-Konsolidierung V1.1, Stand 2026-07-25). Implementierung von V1 noch nicht gestartet.
**Quelle der Wahrheit:** `NUMEROLOGIE_ANALYST_AGENT_MASTER_IMPLEMENTIERUNGSPROMPT.md` (extern)
**Repository:** `GoLukeEnviro/numerology-analyst-agent`
**Geplantes Release:** `0.1.0 Deterministic Core` (pythagoreischer Standard, ~2–4 Wochen ab Implementierungsstart)

---

## Was dieses Projekt ist

Der **Numerology Analyst Agent** ist eine vollständige, reproduzierbare und erweiterbare Plattform, die das bisher uneinheitliche Feld der Numerologie in eine überprüfbare Struktur überführt. Das Projekt besteht aus **fünf voneinander getrennten Ebenen**, jeweils mit eigenen Verträgen, eigener Versionierung und eigener Verantwortung:

| # | Ebene | Kurzbeschreibung |
|---|-------|------------------|
| 1 | **Fachmodell** | Numerologie als formal spezifiziertes Fachgebiet (Methoden, Claim-Taxonomie, Evidenzgrade, Positionierung) |
| 2 | **Rechenkern** | Deterministischer, auditierbarer Berechnungsmotor — kein LLM, kein Netzwerk |
| 3 | **Wissensmodell** | Versioniertes Wissens- und Interpretationsmodell (Zahlen, Meisterzahlen, Schatten, Gegenhypothesen) |
| 4 | **Forschungsrahmen** | Empirischer Forschungs- und Evaluierungsrahmen (Hypothesenregister, Nullmodelle, Permutation, Power) |
| 5 | **App-Schicht** | Anwendungs-, API- und Agentenschicht (CLI, FastAPI, optionaler dünner LLM-Adapter) |

Die Verarbeitungs-Pipeline ist: Eingaben → Normalisierung → Methoden-/Policy-Auswahl → deterministischer Rechenkern → auditierbares Ergebnis → Wissensauflösung → Interpretationskomposition → Safety-/Evidenz-/Aussageklassifizierung → CLI / API / Agent / Bericht.

---

## Was dieses Projekt NICHT ist

Ausdrücklich **kein**:

- **Kein reines Prompt-Repository** — ein Systemprompt allein reicht nicht. Der bestehende Custom-GPT-Prompt ist *nur eine mögliche Benutzerschnittstelle* und darf weder Berechnungslogik noch Fachwissen duplizieren oder ersetzen.
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

| Klasse | Bedeutung |
|--------|-----------|
| `input_fact` | Vom Nutzer / Datensatz gelieferte Information |
| `calculation_fact` | Deterministisch berechnetes Ergebnis |
| `traditional_claim` | Überlieferte numerologische Bedeutung |
| `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation |
| `empirical_evidence` | Ergebnis einer statistischen Untersuchung |
| `practical_suggestion` | Nicht verbindliche Handlungsoption |

---

## Determinismus vor LLM

**Alle Berechnungen funktionieren ohne Sprachmodell vollständig.** Ein LLM (optional, letzte Phase) darf ausschließlich validierte Ergebnisse erklären, Deutungshypothesen formulieren und Ausgaben sprachlich anpassen. Ein LLM darf niemals Zahlen selbst berechnen, fehlende Daten erfinden, Methodenversionen vermischen oder validierte Rechenergebnisse überschreiben. Die Plattform funktioniert vollständig ohne LLM.

---

## V1-Scope — ausschließlich pythagoreischer Standard

Version 1 implementiert **ausschließlich** einen klar definierten pythagoreischen Standard (Methodenversion `pythagorean-v1`):

- Kernberechnungen: Lebensweg (Methoden A + B), Geburtstags-, Einstellungs-, Ausdrucks-/Schicksals-, Seelenstreben-, Persönlichkeits-, Reifezahl
- Meisterzahlen 11, 22, 33; verstärkte Doppelzahlen wie 44/8
- Karmische Schuldenzahlen 13/4, 14/5, 16/7, 19/1
- Persönliche Jahre, Monate, Tage; Pinnacles; Challenges
- Nachvollziehbare Rechenspur (Audit-Trace) für jedes Ergebnis

Offene Spezifikationspunkte (Y-Regel, Umlaute, Akzente, Mehrfachnamen, Geburtsname) werden in Phase 3 als Gate-Bedingung geklärt — sie werden nicht erfunden.

---

## Aktueller Status

| Komponente | Status |
|------------|--------|
| Master-Prompt (extern) | ✅ Quelle der Wahrheit |
| `PROJECT_CHARTER.md` | ✅ vorhanden |
| `ROADMAP.md` (15 Phasen, 0–14) | ✅ vorhanden |
| `docs/audit/gap-analysis.md` | ✅ vorhanden |
| `docs/audit/implementation-plan.md` | ✅ vorhanden |
| `.github/agents/*` (6 Agent-Verträge) | ✅ Plan-Konsolidierung V1.1 |
| Phase 0 (Baseline) | ⏳ noch ausstehend (`repository-baseline.md`) |
| Phasen 1–14 | ⏳ nicht gestartet |

Implementierung beginnt nach Freigabe von Milestone M1 (Phasen 0–4).

---

## Quick Start

> Quick Start wird mit Release `0.1.0 Deterministic Core` bereitgestellt. Aktuell liegen nur Plan-Dokumente vor.

Vorgesehen (folgt):

```bash
uv sync --all-groups
uv run pytest
uv run numerology calculate profile --name "Max Mustermann" --date 1985-03-12
```

---

## Dokumentation

| Dokument | Zweck |
|----------|-------|
| `PROJECT_CHARTER.md` | Was und Warum von V1 (verbindlich) |
| `ROADMAP.md` | 15 Phasen (0–14) mit Gates, Commits, Aufwand, Delegation |
| `docs/v1-minimal-scope.md` | Scope von Release 0.1.0 Deterministic Core (vorhanden, bindend) |
| `docs/governance/master-implementation-contract.md` | Normativer Master-Vertrag (vorhanden, bindend) |
| `docs/adr/` | 4 ADRs zu Methodenentscheidungen (vorhanden, bindend) |
| `docs/audit/` | Repository-Baseline, Gap-Analyse, Übersetzungsplan |
| `docs/field/` | Fachgebiet, Claim-Taxonomie, wissenschaftliche Positionierung (folgt) |

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
