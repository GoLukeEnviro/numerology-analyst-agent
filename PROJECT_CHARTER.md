# Project Charter — Numerology Analyst Agent

> **Dokumenttyp:** Projektcharter (verbindlich für V1)
> **Quelle der Wahrheit:** Master-Vertrag `docs/governance/master-implementation-contract.md` (externer Master-Prompt, intern importiert; Section 1, 2, 3)
> **Stand:** 2026-07-25 (V1.1 — Lukes Review vom 2026-07-25 eingearbeitet)
> **Sprache:** Deutsch (Fachbegriffe auf Englisch, wo idiomatisch)
> **Status:** Plan V1.1 — Phase 0 IN PROGRESS (Planartefakte erstellt, Implementierung 0.1.0 ausstehend)

Dieses Dokument definiert **Was** gebaut wird und **Warum**. Die **Wie**-Ebene
liegt in `ROADMAP.md`, der Übersetzungsplan in `docs/audit/implementation-plan.md`.

---

## 1. Projektmission

> Vom uneinheitlichen **Fachgebiet** zu einem überprüfbaren **System** zu einem kontrollierten **Agenten** — in genau dieser Reihenfolge, niemals umgekehrt.

Das Projekt **Numerology Analyst Agent** baut das bestehende GitHub-Repository
zu einer vollständigen, reproduzierbaren und erweiterbaren Plattform für
**numerologische Berechnung, strukturierte Deutung, Forschung, Evaluation und
agentische Nutzung** aus.

### Auftrag an den Principal

Rolle: **Principal Engineer, Domain Architect, Research Engineer und Repository Maintainer**.

### Drei ausdrückliche Anti-Ziele

Das Projekt darf **nicht** werden:

1. **Kein reines Prompt-Repository** — ein System-Prompt allein reicht nicht.
2. **Kein einfacher Numerologie-Rechner** — nur Berechnen ohne Wissensmodell,
   Forschungsrahmen und Safety ist unvollständig.
3. **Keine lose Sammlung esoterischer Texte** — Deutungstexte ohne versioniertes
   Wissensmodell, Provenienz und Gegenhypothesen sind nicht akzeptabel.

Der bestehende Custom-GPT-Systemprompt ist **nur eine mögliche
Benutzerschnittstelle** und darf weder Berechnungslogik noch Fachwissen
duplizieren oder ersetzen.

---

## 2. Die fünf Ebenen der Plattform

Das System muss fünf voneinander getrennte Ebenen besitzen. Jede Ebene hat
eigene Verträge, eigene Versionierung und eigene Verantwortung.

| # | Ebene | Kurzbeschreibung | Was sie NICHT tut |
|---|-------|------------------|-------------------|
| 1 | **Fachmodell** | Numerologie als formal spezifiziertes Fachgebiet (Methoden, Claim-Taxonomie, Evidenzgrade, Positionierung) | Enthält keine Berechnungscodes |
| 2 | **Rechenkern** | Deterministischer, auditierbarer Berechnungsmotor (kein LLM, kein Netzwerk) | Enthält keine Deutungstexte |
| 3 | **Wissensmodell** | Versioniertes Wissens- und Interpretationsmodell (Zahlen, Meisterzahlen, Schatten, Gegenhypothesen) | Enthält keine Berechnungslogik |
| 4 | **Forschungsrahmen** | Empirischer Forschungs- und Evaluierungsrahmen (Hypothesenregister, Nullmodelle, Permutation, Power) | Bestätigt keine numerologischen Hypothesen |
| 5 | **App-Schicht** | Anwendungs-, API- und Agentenschicht (CLI, FastAPI, optionaler LLM-Adapter) | Erfindet keine Zahlen, überschreibt keine validierten Ergebnisse |

### Verarbeitungs-Pipeline (technisch)

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

### Paketgrenzen (verbindlich)

- `numerology_domain` — Typen, Regeln, Methodenversionen, Verträge
- `numerology_engine` — reine Berechnungen
- `numerology_knowledge` — Laden und Validieren von Wissenspaketen
- `numerology_interpretation` — regelbasierte Komposition
- `numerology_research` — Daten- und Statistikpipelines
- `numerology_safety` — Datenschutz, Krisengrenzen, Minderjährigenschutz
- `numerology_agent` — dünner Adapter für LLM-gestützte Erklärungen
- `apps/api` — FastAPI
- `apps/cli` — Typer-CLI

Es dürfen **keine zyklischen Abhängigkeiten** entstehen.

---

## 3. Die sechs nicht verhandelbaren Aussageklassen

Das gesamte System muss technisch zwischen sechs Aussageklassen unterscheiden.
Diese Typen müssen im Domainmodell, in JSON-Schemas, API-Ausgaben, Berichten
und Tests sichtbar sein.

| # | Klasse | Definition | Beispiel |
|---|--------|------------|----------|
| 1 | `input_fact` | Vom Nutzer oder Datensatz gelieferte Information | "Geburtsdatum: 1985-03-12" |
| 2 | `calculation_fact` | Deterministisch berechnetes Ergebnis | "Lebenswegzahl: 3 (Methode A, pythagorean-v1)" |
| 3 | `traditional_claim` | Überlieferte numerologische Bedeutung | "Die Zahl 7 gilt traditionell als Sucher nach Wahrheit" |
| 4 | `interpretive_hypothesis` | Daraus abgeleitete, korrigierbare Interpretation | "Die Häufung der 7 könnte auf eine Tendenz zur Introversion hindeuten" |
| 5 | `empirical_evidence` | Ergebnis einer statistischen Untersuchung | "Permutationstest p = 0.42 — kein signifikanter Zusammenhang" |
| 6 | `practical_suggestion` | Nicht verbindliche Handlungsoption | "Praxis-Tipp: Reflektiere Zeiten bewusster Zurückgezogenheit" |

### Warum diese Trennung existiert

Ohne diese Trennung verschmilzt der Agent **Tradition** (unverifiziert),
**Berechnung** (deterministisch) und **Deutung** (hypothetisch) zu einer
autoritären Aussage, die nicht mehr falsifizierbar ist. Das wäre nach
§2.3 (Wissenschaftliche Positionierung) unzulässig.

---

## 4. Wissenschaftliche Positionierung (§2.3 Master-Prompt)

### Klares Bekenntnis

**Numerologische Traditionen sind keine wissenschaftlich bestätigten psychologischen Messverfahren.**

### Was das Projekt **darf**

- traditionelle Systeme **formal dokumentieren**,
- deren Berechnungen **reproduzierbar** machen,
- Interpretationen **transparent** modellieren,
- empirische Behauptungen **ergebnisoffen** untersuchen.

### Was das Projekt **nicht darf**

- symbolische Deutungen als wissenschaftliche Fakten ausgeben,
- statistische Korrelationen als Kausalität darstellen,
- fehlende Evidenz als Beleg für spirituelle Wahrheit umdeuten,
- medizinische oder psychologische Diagnosen ableiten.

Diese Grenzen sind **nicht verhandelbar** und werden in Phase 1 (Governance),
Phase 6 (Interpretation), Phase 7 (Forschung) und Phase 8 (Safety) technisch
durchgesetzt.

---

## 5. Determinismus-vor-LLM-Prinzip (§2.4 Master-Prompt)

### Was deterministisch funktionieren MUSS

**Alle Berechnungen müssen ohne Sprachmodell vollständig funktionieren.**

Der Rechenkern (Phase 4) ist das Fundament. Kein LLM darf jemals:

- Zahlen selbst unkontrolliert berechnen,
- fehlende Daten erfinden,
- Methodenversionen vermischen,
- validierte Rechenergebnisse überschreiben.

### Was ein LLM **darf**

Ein LLM (Phase 10, optional) darf ausschließlich:

- **validierte** Ergebnisse erklären,
- unterschiedliche **Deutungshypothesen** formulieren,
- Ausgaben sprachlich anpassen.

### Konsequenz für die Architektur

- Phase 10 (Agent) ist die **letzte** inhaltliche Phase vor Evaluation/Doku.
- Der Agent ist ein **dünner Adapter** über validierten Services.
- Mock-Provider in V1, echte Provider optional später.
- Plattform funktioniert **vollständig ohne LLM**.

---

## 6. V1-Scope — ausschließlich pythagoreischer Standard

### Was in V1 implementiert wird

- **Ein** klar definierter pythagoreischer Standard, Methodenversion `pythagorean-v1`.
- Kernberechnungen: Lebensweg (A+B), Geburtstags-, Einstellungs-, Ausdrucks-/Schicksals-, Seelenstreben-, Persönlichkeits-, Reifezahl.
- Meisterzahlen 11, 22, 33. Verstärkte Doppelzahlen wie 44/8.
- Karmische Schulden 13/4, 14/5, 16/7, 19/1.
- Persönliche Jahre, Monate, Tage. Pinnacles. Challenges.
- Nachvollziehbare Rechenspur für jedes Ergebnis.

### Was in V1 NICHT implementiert wird

- Chaldäische Engine
- Kabbalistische/Gematria-Engine
- Astrologie
- Human Design
- Enneagramm

Diese Systeme werden **nur** als dokumentierte Erweiterungspunkte und
Methodenspezifikationen angelegt (Phase 1, §3.1 des Master-Prompts). Sie sind
ausdrücklich Zukunftsmodule (§11 Master-Prompt).

### OFFEN-Punkte (nicht vom Master-Prompt spezifiziert, müssen in Phase 3 geklärt werden)

> Diese Punkte werden in `ROADMAP.md` Phase 3 als Gate-Bedingung explizit gelistet.

- **OFFEN-1:** Exakte Buchstabenbelegung für den Buchstaben **Y** (Vokal vs. Konsonant je nach Kontext). Master-Prompt erwähnt "Y-Regel als Policy", spezifiziert aber nicht den Algorithmus. → Phase 3 muss Entscheidung treffen und dokumentieren.
- **OFFEN-2:** Locale-Verhalten bei **Umlauten** (ä, ö, ü → wie reduzieren? ä = a+e oder direkt? oder transkribieren?). → Phase 3 muss explizite Normalisierungsregeln definieren.
- **OFFEN-3:** Behandlung von **Akzenten** (é, è, ê, ñ). Master-Prompt erwähnt nur "Behandlung von Umlauten, Akzenten" als Aufgabe, kein Algorithmus. → Phase 3.
- **OFFEN-4:** **Mehrfachnamen** und **Bindestriche** — Master-Prompt listet als Aufgabe, spezifiziert keine Regel. → Phase 3.
- **OFFEN-5:** **Namensänderungen / Geburtsname** — welcher Name für welche Zahl? Master-Vertrag fordert "Namensbasis" als Policy-Feld, aber keine kanonische Regel. → Phase 3.

---

## 6b. Release-Strategie (V1.1)

> **Lukes Architekturentscheidung (2026-07-25):** Die Roadmap wird in zwei
> Ebenen geteilt — eine langfristige **North-Star-Roadmap** (alle 15 Phasen,
> die komplette Plattformvision) und eine operative **Release-Roadmap**
> (kurzfristige, lieferbare Releases).

### North-Star-Roadmap

- **15 Phasen (0–14)** — die komplette Plattformvision, verbindlich für V1.
- Lücken zwischen Ist und Soll bleiben für North-Star relevant
  (siehe `docs/audit/gap-analysis.md`).

### Operative Release-Roadmap

| Release | Titel | Phasen | Ziel |
|----------|-------|--------|------|
| **0.1.0** | Deterministic Core | 0–4 | Governance + Tooling + Methodenspec + Rechenkern + CLI-Basis + Tests (~2–4 Wochen) |
| **0.2.0** | Knowledge and Interpretation | 5–6 | Wissensmodell + regelbasierte Interpretation |
| **0.3.0** | Interfaces and Agent | 8, 9 (Core), 10 | Safety + Core CLI/API (ohne Forschung) + Mock-Provider + Agent-Adapter |
| **0.4.0** | Research Preview | 7 | Forschungs-/Meta-Analyse-Rahmen — **explizit als Preview, nicht als wissenschaftliche Validierung** |

Phasen 11–14 werden in die jeweiligen Releases eingebettet (kein eigener Release).

→ Details zu 0.1.0 siehe `docs/v1-minimal-scope.md`.

---

## 7. Nicht-Ziele von V1

| Anti-Ziel aus §1 Master-Prompt | Konsequenz |
|-------------------------------|------------|
| Kein reines Prompt-Repository | `prompts/` existiert, ist aber **Adapter**, nicht Quelle der Wahrheit |
| Kein einfacher Numerologie-Rechner | Rechenkern + Wissensmodell + Forschung + Safety sind Pflicht |
| Keine lose Esoterik-Sammlung | Wissenspakete sind versioniert, schema-validiert, mit Gegenhypothesen |

Zusätzlich:

- Kein Produktiv-LLM in V1 (Mock-Provider, siehe Default #5).
- Keine privaten personenbezogenen Daten im Repository (Default #3, Phase 7/8).
- Keine Force-Pushes, keine Direct-Pushes auf `main` (Default #8).
- Keine medizinischen/psychologischen Diagnosen (§2.3).
- Keine Behauptung eines fertigen Releases ohne Tag und GitHub-Release (Phase 14).

---

## 8. Verbindlicher Technologie-Stack (V1)

| Schicht | Technologie | Begründung |
|---------|-------------|------------|
| Sprache | Python ≥ 3.12 | Modernes Typsystem, Ökosystem |
| Abhängigkeiten / Venv | `uv` | Reproduzierbar, schnell |
| Verträge / Validierung | `pydantic` v2 | Strikte Modelle, JSON-Schema-Export |
| Unit-Tests | `pytest` | Standard |
| Property-Based Tests | `hypothesis` | Invarianten für Reduktion, Trace |
| Lint + Format | `ruff` | Ein Tool, schnell, streng |
| Typen | `mypy` strict | Determinismus braucht Typsicherheit |
| HTTP-API | `FastAPI` | OpenAPI, Validierung |
| CLI | `Typer` | Typisiert, automatisch Hilfetexte |
| Wissenspakete | YAML / validiertes JSON | Menschenlesbar, diffbar |
| Forschungsdaten | DuckDB + Parquet | Spaltenorientiert, reproduzierbar |
| Analyse | Polars (oder Pandas) | Schnelle, typisierte Pipelines |
| Doku | MkDocs Material | Statisches Site-Build, `--strict` |
| CI | GitHub Actions | Standard für GitHub-Repo |
| Versionierung | SemVer | Klar, maschinenlesbar |

**Explizit NICHT in V1:**

- Keine unnötige Datenbank im Basiskern.
- Kein Vektorstore.
- Kein LLM-Framework im Basiskern.

---

## 9. Definition of Done (Auszug aus Master-Prompt §9)

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

### Nicht ausreichend (explizit)

- nur ein Systemprompt,
- nur eine README,
- ein ungetesteter Rechner,
- eine Sammlung fertiger Deutungstexte,
- ein Chatbot ohne Rechenkern,
- ein angeblicher Forschungsansatz ohne Nullmodelle und Reproduzierbarkeit.

---

## 10. Verweise

| Dokument | Zweck |
|----------|-------|
| `README.md` | Aktueller Ist-Zustand (nur Header) |
| `ROADMAP.md` | **15 Phasen (0–14)** mit Gates, Commits, Aufwand, Delegation |
| `docs/audit/gap-analysis.md` | Lücke zwischen Soll und Ist |
| `docs/audit/implementation-plan.md` | Übersetzungsplan Master-Vertrag → ausführbare Schritte |
| `docs/v1-minimal-scope.md` | Details zu Release 0.1.0 (Vorgabe Luke) |
| `.planning/notes/master-plan-defaults.md` | Autonome Defaults, revidierbar durch Luke |
| `docs/governance/master-implementation-contract.md` | Interner Master-Vertrag (Import des externen Master-Prompts) |
| `.github/agents/*.agent.md` | Verbindliche Agenten-Verträge (Delegation) |

---

## 11. Geltungsbereich dieses Charters

- Verbindlich für V1-Scope (pythagoreisch, Phasen 0–14).
- Zukunftsmodule (Chaldäa, Kabbala, Astrologie, Human Design, Enneagramm) sind **ausdrücklich ausgeschlossen**.
- Bei Konflikt mit dem Master-Vertrag: **Master-Vertrag ist Quelle der Wahrheit**.
- Bei Konflikten zwischen diesem Charter und `ROADMAP.md`: Charter definiert **Was/Why**, Roadmap definiert **Wie/Wann**.
- OFFEN-Punkte (§6) werden in Phase 3 spezifiziert — nicht erfunden.

---

*End of Charter — Numerology Analyst Agent V1.1 (Stand 2026-07-25)*
