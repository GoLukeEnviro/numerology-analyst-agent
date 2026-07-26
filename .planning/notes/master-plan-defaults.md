# Master Plan Defaults — Numerology Analyst Agent

> **Dokumenttyp:** Entscheidungs-Log der autonomen Defaults
> **Stand:** 2026-07-25
> **Sprache:** Deutsch
> **Status:** Phase 0 IN PROGRESS — Defaults vorentschieden, revidierbar

Dieses Dokument hält die 10 autonomen Defaults fest, die Luke (Principal)
für diese Plan-Session vorgegeben hat. Jeder Default ist mit Begründung,
Revisions-Option und Auswirkungen auf Phasen dokumentiert.

**Revisions-Regel:** Luke kann jeden Default jederzeit revidieren. Bei
Revision muss `ROADMAP.md`, `docs/audit/implementation-plan.md` und
`docs/audit/gap-analysis.md` entsprechend aktualisiert werden.

---

## Default 1 — Scope dieser Session

### Entscheidung
**Nur Plan-Dokumente, keine Code-Implementierung.**

### Begründung
Plan-Phase vor Implementierung. Liefert die 5 Dokumente
(`PROJECT_CHARTER.md`, `ROADMAP.md`, `docs/audit/gap-analysis.md`,
`docs/audit/implementation-plan.md`, `.planning/notes/master-plan-defaults.md`)
ohne in Code/Tooling zu investieren. Reduziert Risiko von Fehlinvestitionen,
bevor Luke die Architektur abnimmt.

### Revisions-Optionen
- **Revidieren:** „Code-Implementierung sofort starten (Phase 0+1)."
- **Revidieren:** „Andere Plan-Dokumente priorisieren."

### Auswirkungen auf Phasen
- Keine Phasen-Implementierung in dieser Session.
- Phasen starten erst, wenn Luke die Plan-Dokumente abnimmt.
- Alle Phasen bleiben in Status "Plan — nicht gestartet".

---

## Default 2 — Git-Domain

### Entscheidung
**Lokaler Commit OK auf Feature-Branch `plan/master-plan-v1`. KEIN Push ohne
Lukes Review. KEIN Direct-Push auf `main`. KEIN Force-Push.**

### Begründung
Git-Disziplin gemäß `writer-contract-discipline.md` (User-Memory):
Lokaler Windows-VS-Code-Agent darf **nicht** pushen. Plan-Phase braucht
Review, bevor öffentliche Remote-History gemutiert wird. Schützt `main`
vor unfertigem Plan-Inhalt.

### Revisions-Optionen
- **Revidieren:** „Push auf `plan/master-plan-v1` erlaubt (ohne Merge in main)."
- **Revidieren:** „Lokaler Commit auch verboten — nur Dateien, kein Commit."

### Auswirkungen auf Phasen
- Diese Session macht **keinen** Commit (Default-Auslegung: nur Datei-Erstellung,
  Commit überlässt Luke).
- Für jede Folge-Phase gilt: Feature-Branch, kein Direct-Push, kein Force-Push.
- Branch-Strategie in `docs/audit/implementation-plan.md` §5 dokumentiert.

---

## Default 3 — Empirische Datenquelle (Phase 7)

### Entscheidung
**Synthetische Testdaten für V1, öffentliche Biografien (Wikipedia) optional später.**

### Begründung
PII-Vermeidung in V1. Synthetische Daten sind deterministisch, offline,
rechtlich unbedenklich. Öffentliche Biografien bringen PII-Risiko
(Verstorbene vs. Lebende, DSGVO-Relevanz bei EU-Personen). Reihenfolge:
erst synthetisch stabil, dann optional echte Daten mit explicit consent
oder historische Verstorbene.

### Revisions-Optionen
- **Revidieren:** „Öffentliche Biografien (Wikipedia) schon in V1."
- **Revidieren:** „Komplett private/eingewilligte Datensätze später."

### Auswirkungen auf Phasen
- Phase 7: Sample-Datensatz rein synthetisch (`research/data/sample/`).
- Phase 8: PII-Scanner prüft, dass keine echten Biografien in Git landen.
- **OFFEN-7:** Sample-Größe muss Phase 7 definieren (z.B. 1000 synthetische
  Profile mit deterministischem Seed).

---

## Default 4 — Knowledge Pack Autorschaft (Phase 5)

### Entscheidung
**KI-generierter erster Draft als `traditional_claim` mit
`quellenstatus: tradition_unverified`, klar markiert.**

### Begründung
Wissensbasis aus menschlicher Autorschaft wäre ideal, aber für V1
zeitlich unrealistisch. KI-Draft mit klarer Markierung als
`quellenstatus: tradition_unverified` ist transparent: jeder Leser
weiß, dass es sich um KI-generierten, nicht verifizierten Text handelt.
Ethisch vertretbar, solange die Markierung maschinenlesbar und
auditierbar ist.

### Revisions-Optionen
- **Revidieren:** „Menschliche Autorschaft verpflichtend (länger, teurer)."
- **Revidieren:** „Mixed Model: KI-Draft + menschliche Review pro Entry."

### Auswirkungen auf Phasen
- Phase 5: `knowledge/manifest.yaml` MUSS enthalten pro Entry:
  `generated: true`, `model: <name>`, `date: <iso>`, `quellenstatus: tradition_unverified`.
- Phase 5 Gate: Validator prüft, dass jeder `traditional_claim` mit
  `quellenstatus: tradition_unverified` diese Felder hat.
- Phase 13 (Committee): Methodologie-Perspektive prüft die Markierung.
- **OFFEN-8:** Welches KI-Modell? Phase 5 muss konkret benennen.

---

## Default 5 — LLM-Provider (Phase 10)

### Entscheidung
**Provider-Abstraktion mit Mock-Provider, kein echter Provider in V1.**

### Begründung
Determinismus-vor-LLM (Master-Prompt §2.4). Ohne deterministischen
Rechenkern (Phase 4) ist ein echter LLM-Provider kontraproduktiv. Mock
macht Agent testbar, deterministisch und offline. Echter Provider ist
optional später, nach Committee-Freigabe.

### Revisions-Optionen
- **Revidieren:** „Echter Provider (z.B. OpenAI/Anthropic) schon in V1."
- **Revidieren:** „Lokaler Provider (Ollama) als zweiter Adapter."

### Auswirkungen auf Phasen
- Phase 10: `numerology_agent` importiert ohne echten Provider.
- Phase 10 Gate: Plattform funktioniert ohne LLM.
- Phase 11: Prompt-Evals (Halluzination, Extraktion, absolute Aussagen)
  laufen gegen Mock-Provider mit kontrollierten Test-Antworten.
- Echter Provider = Zukunftsmodule (post-0.1.0).

---

## Default 6 — License

### Entscheidung
**MIT.**

### Begründung
Permissive License, niedrige Einstiegshürde für Forschung und
Wiederverwendung. Passend zu "research & development repository".
Kompatibel mit allen Abhängigkeiten des Tech-Stacks.

### Revisions-Optionen
- **Revidieren:** „Apache 2.0 (mit Patent-Grant)."
- **Revidieren:** „GPL (Copyleft)."

### Auswirkungen auf Phasen
- Phase 14: `LICENSE` (MIT-Text) im Repo-Root.
- Phase 14: `CITATION.cff` referenziert License.
- Phase 1: Governance-Doku nennt MIT.

---

## Default 7 — Visibility

### Entscheidung
**Public (Repo ist schon public).**

### Begründung
Repository `GoLukeEnviro/numerology-analyst-agent` ist bereits public.
Forschungs- und Entwicklungscharakter. PII-frei in V1 (Default #3).
Public-Visibility zwingt zu sauberer Safety-Disziplin (Phase 8).

### Revisions-Optionen
- **Revidieren:** „Private bis Phase 13 (Committee), dann public."
- **Revidieren:** „Permanent private (Forschung-only)."

### Auswirkungen auf Phasen
- Phase 8: Secret-Scan + PII-Scan verpflichtend (Public = höheres Risiko).
- Phase 14: GitHub Release public, Branch Protection, CODEOWNERS.
- Phase 12: README auf Produkt- und Fachgebietsebene für public audience.

---

## Default 8 — Branch-Strategie (V1.1, nach Lukes Review)

### Entscheidung
**Branch pro Issue oder vertikalem Slice — nicht pro Phase. Mehrere atomare Commits erlaubt. Draft-PR früh. Required Checks pro PR. Squash-Merge nach Review. Milestone-Review zusätzlich.**

### Begründung
Branch-pro-Phase funktionierte praktisch nicht sauber: Phase 2 konnte nicht zuverlässig auf Phase 1 aufbauen, wenn die Branches getrennt blieben; ohne PR-Merge wurde das Review-Gate umgangen; ein Commit pro mehrtägiger Phase verhindert sinnvolle Zwischenschritte und erschwert Fehleranalyse. Luke hat diese Kritik am 2026-07-25 vorgebracht (Plan-Review). Lösung: Branch pro logischem Slice, mehrere Commits, Draft-PR früh, Milestone-Review als zusätzliches Gate.

### Revisions-Optionen
- **Revidieren:** „Branch pro Phase doch zulassen (für sehr kleine Phasen)."
- **Revidieren:** „Milestone-Review weglassen, nur PR-Review."

### Auswirkungen auf Phasen
- Mehrere PRs pro Phase sind erlaubt (z.B. Phase 4 Rechenkern könnte 3–5 PRs haben: Normalisierung, Reduktion, Audit-Trace, Service-Fassade, Tests).
- Milestone-Review-Gate am Ende jedes Releases (0.1.0, 0.2.0, 0.3.0, 0.4.0).
- Siehe `docs/audit/implementation-plan.md` § „Branch- und PR-Modell" für Details.

---

## Default 9 — Commit-Cadence

### Entscheidung
**1 Commit pro Phase auf Feature-Branch (wie Master-Prompt vorgibt).**

### Begründung
Master-Prompt §7 definiert explizit einen Commit pro Phase mit
Deutschsprachiger Commit-Message (`type: kurzbeschreibung`). Halten an
diesem Rhythmus macht Historie nachvollziehbar und Gate-Zustände
reproduzierbar.

### Revisions-Optionen
- **Revidieren:** „Mehrere Commits pro Phase erlaubt (feingranularer)."
- **Revidieren:** „Conventional Commits statt Master-Prompt-Stil."

### Auswirkungen auf Phasen
- Commit-Messages aus `ROADMAP.md` übernommen (alle 15 Phasen, 0–14).
- Phase 14: Empfohlene Commit-Reihenfolge aus Master-Prompt §7 Phase 14.
- **OFFEN-6:** Phase-14-Commit-Message ist im Master-Prompt nicht definiert.
  Vorschlag in `ROADMAP.md` Phase 14: `release: version 0.1.0 of numerology analyst agent v1`.

**Commit-Sprache (V1.1-Klarstellung):** Commit-Messages aus dem Master-Vertrag (`docs/governance/master-implementation-contract.md` §7) sind **englisch** und werden als Vorgabe übernommen. Eigene Commits außerhalb der Phasen-Vorgaben folgen CLAUDE.md §7 (deutsch): Format `<type>: <kurzbeschreibung>`, Fokus auf Warum.

---

## Default 10 — Sprache

### Entscheidung
**Deutsch für Doku, Englisch für Code-Kommentare.**

### Begründung
Doku primär für Luke (deutschsprachig). Code international verständlich
(public repo, Default #7). Fachbegriffe auf Englisch, wo idiomatisch
(Coverage, Property-Based Tests, etc.). Entspricht CLAUDE.md „Immer auf Deutsch"
für Konversation und Doku.

### Revisions-Optionen
- **Revidieren:** „Englisch für alle Doku (international)."
- **Revidieren:** „Deutsch für alle Doku und Code-Kommentare."

### Auswirkungen auf Phasen
- Phase 1, 3, 5, 12: Doku deutsch (Fachtexte, Methodenspec, Wissensbasis, README).
- Phase 4, 6, 7, 8, 9, 10, 11: Code-Kommentare englisch.
- Phase 13: Committee-Review englisch (international lesbar) oder deutsch
  (Luke entscheidet).
- Phase 14: Release-Notes englisch (international public).

---

## Default 11 — Release-Strategie (V1.1, nach Lukes Review am 2026-07-25)

### Entscheidung
**Trennung von North-Star-Roadmap und operativer Release-Roadmap.**

- **North-Star-Roadmap** = die 15 Phasen (0–14) aus dem Master-Vertrag. Sie beschreibt die langfristige Plattformvision und bleibt als Referenz erhalten.
- **Operative Release-Roadmap** = die konkreten Releases, die ausgeliefert werden:
  - `0.1.0 Deterministic Core` — Phasen 0–4 (Governance + Tooling + Methodenspec + Rechenkern + CLI), ~2–4 Wochen.
  - `0.2.0 Knowledge and Interpretation` — Phasen 5–6 (Wissensmodell + Interpretation).
  - `0.3.0 Interfaces and Agent` — Phasen 8–10 (Safety vollständig + FastAPI + Mock-Provider + Agent-Adapter).
  - `0.4.0 Research Preview` — Phase 7 (synthetische Datensätze, Nullmodelle, Permutationstests) — explizit als **Preview**, nicht als wissenschaftliche Validierung von Numerologie.

### Begründung
Lukes Review (2026-07-25): „Der jetzige Plan versucht, die komplette langfristige Produktvision bereits als Release `0.1.0` umzusetzen. Dadurch wird aus einem kontrollierbaren Kernprojekt ein 14- bis 16-wöchiges Plattformprogramm, bevor überhaupt die erste belastbare Berechnung läuft." Lösung: Architektur bleibt, V1-Zuschnitt wird getrennt. Siehe `docs/v1-minimal-scope.md` für 0.1.0-Details.

### Revisions-Optionen
- **Revidieren:** „Research doch schon in 0.1.0 (wenn Luke die Forschungs-Plattform Priorität gibt)."
- **Revidieren:** „0.1.0 noch schmaler (nur Life Path A/B, keine weiteren Kernzahlen)."

### Auswirkungen auf Phasen
- Phase 7 (Forschung) wird NACH Phase 9/10 ausgeliefert (als 0.4.0 Research Preview).
- Phase 11–14 (Evaluation, Doku, Committee, Release) werden IN die jeweiligen Releases eingebettet, nicht als separate Meilensteine.

---

## Revisions-Protokoll

| Datum | Default | Änderung | Begründung | Geändert durch |
|-------|---------|----------|------------|----------------|
| 2026-07-25 | (initial) | Alle 10 Defaults initial gesetzt | Vorgabe Luke (Principal) | Luke |

### Bei Revision zu tun

1. Default in dieser Datei aktualisieren (neue Entscheidung + Begründung + Datum).
2. Protokoll-Zeile oben hinzufügen.
3. `ROADMAP.md` aktualisieren, falls Commit-Message/Aufwand/Delegation betroffen.
4. `docs/audit/implementation-plan.md` aktualisieren, falls Milestone/Akzeptanzkriterien betroffen.
5. `docs/audit/gap-analysis.md` aktualisieren, falls Priorität/Blocker betroffen.

---

## Querverweise

| Siehe | Für |
|-------|-----|
| `PROJECT_CHARTER.md` | Mission, Scope, Aussageklassen |
| `ROADMAP.md` | Phasen-Übersetzung dieser Defaults |
| `docs/audit/gap-analysis.md` | Lücken Ist/Soll |
| `docs/audit/implementation-plan.md` | Übersetzungsplan, kritischer Pfad |
| Master-Prompt §1–11 | Quelle der Wahrheit |
| User-Memory `writer-contract-discipline.md` | Git-Disziplin (Default #2 Begründung) |
| CLAUDE.md §7 | Git-Konventionen |

---

*End of Master Plan Defaults — Numerology Analyst Agent V1*
