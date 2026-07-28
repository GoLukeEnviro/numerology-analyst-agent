# Numra V2 — Guided Masterplan (Spezifikation)

> **Status:** Spezifikation / Produktvision — KEINE Implementierung in V1
> **Änderungsprozess:** Änderungen erfordern einen ADR. Siehe ADR 0016.
> **Beziehung zu V1:** V1 (`0.3.0rc1` / stabil `0.3.0`) ist funktional
> abgeschlossen. V2 ist ein späteres, separat geplantes Programm (Welle 9).
> **Beziehung zur Plattform-Erweiterung:** Erweiterte Methodensysteme,
> Mehrsprachigkeit, Forschungs-Community-Features, Cloud-Synchronisation,
> fortgeschrittene Agenten-Workflows und weitere Zukunftsdomänen (Astrologie,
> Human Design, Enneagramm) gehören NICHT zu diesem Dokument. Sie sind in
> `docs/roadmaps/numra-platform-expansion-roadmap.md` ausgelagert.

---

## 1. Zweck

Dieses Dokument beschreibt den **nutzergebauten Guided Masterplan**: einen
Reflexions- und Zielsetzungsprozess, der auf dem deterministischen
numerologischen Profil (V1) aufbaut, aber die eigentliche Planung
vollständig dem Nutzer überlässt. Es ist eine **Produktvision**, kein
Implementierungsauftrag. Kein Code in diesem Dokument geht in den
V1-Release ein (ADR 0016).

## 2. Leitprinzipien (unverändert aus V1)

- Determinismus vor LLM — alle Berechnungen funktionieren ohne Sprachmodell.
- Sechs Aussageklassen werden streng getrennt.
- Keine erfundenen Daten, keine Diagnosen, keine garantierte Zukunft.
- Lokale-first, Privatsphäre Standard.
- Auditierbarkeit — jeder Berechnungsschritt ist reproduzierbar.

Der Guided Masterplan erweitert den Umfang, ändert aber keines dieser
Prinzipien.

## 3. Verbindliche Nutzer-Autonomie-Regel

**Nur der Nutzer kann eine `PracticalSuggestion` oder `ActionOption` in eine
`AcceptedAction` umwandeln.**

Numra (Regelwerk oder LLM-Adapter) darf Optionen vorschlagen, Muster
spiegeln und Gegenhypothesen anbieten — es darf niemals selbst eine
Massnahme als angenommen markieren, priorisieren oder terminieren. Diese
Regel ist nicht verhandelbar und gilt für jede zukünftige
Guided-Masterplan-Implementierung ohne Ausnahme. Sie ist die zentrale
Sicherheitsgrenze dieses gesamten Programms — vergleichbar mit der
Determinismus-vor-LLM-Grenze in V1.

## 4. Core-Datenmodelle (Spezifikation)

| Modell | Zweck |
|---|---|
| `UserGoal` | Ein vom Nutzer selbst formuliertes Ziel, nicht von Numra vorgeschlagen. |
| `LifeArea` | Ein vom Nutzer priorisierter Lebensbereich (z. B. Beruf, Beziehungen, Gesundheit). |
| `ReflectionEntry` | Ein Reflexionseintrag des Nutzers zur eigenen Situation. |
| `ObservedPattern` | Ein vom System gespiegeltes, aber nicht bewertetes Muster aus den Reflexionen. |
| `UserConstraint` | Eine vom Nutzer benannte Einschränkung oder Ressourcengrenze. |
| `PriorityDecision` | Die Entscheidung des Nutzers, welche Lebensbereiche/Ziele Vorrang haben. |
| `ActionOption` | Eine unverbindliche, vergleichbare Handlungsoption (vom System oder Nutzer erzeugt). |
| `AcceptedAction` | Eine vom Nutzer explizit angenommene `ActionOption` — einziger Übergang gemäss §3. |
| `Milestone` | Ein vom Nutzer definierter Meilenstein zu einer `AcceptedAction`. |
| `Habit` | Eine vom Nutzer festgelegte, wiederkehrende Gewohnheit. |
| `ReviewCheckpoint` | Ein vom Nutzer terminierter Check-in-Zeitpunkt zur Standortbestimmung. |
| `MasterplanVersion` | Eine versionierte Momentaufnahme des gesamten Masterplans zu einem Zeitpunkt. |

Jedes Modell ist auditierbar und versioniert, analog zu `ProfileCalculationResult`
in V1: keine stille Mutation, jede Änderung erzeugt eine neue
`MasterplanVersion`.

## 5. Guided Flow

Der Guided Masterplan folgt einer festen Abfolge von Schritten. Jeder
Schritt gehört dem Nutzer; Numra unterstützt, entscheidet aber nicht:

1. **Profil verstehen** — das deterministische V1-Profil als Ausgangsbasis.
2. **Themen auswählen** — der Nutzer wählt relevante Themenfelder.
3. **Eigene Situation beschreiben** — freie `ReflectionEntry`-Einträge.
4. **Ziel formulieren** — der Nutzer erstellt eine `UserGoal`.
5. **Gegenhypothesen prüfen** — Numra spiegelt alternative Sichtweisen,
   ohne eine davon als richtig zu markieren.
6. **Hindernisse und Ressourcen erfassen** — `UserConstraint`-Einträge.
7. **Lebensbereiche priorisieren** — `PriorityDecision` über `LifeArea`.
8. **Optionen vergleichen** — mehrere `ActionOption` nebeneinander, ohne
   Ranking durch das System.
9. **Massnahme selbst auswählen** — der Nutzer erzeugt eine `AcceptedAction`
   (einziger Umwandlungspunkt, siehe §3).
10. **Meilensteine definieren** — `Milestone`-Einträge zur `AcceptedAction`.
11. **Gewohnheiten festlegen** — `Habit`-Einträge.
12. **Check-ins durchführen** — `ReviewCheckpoint`, gefolgt von einer neuen
    `MasterplanVersion`.

Der Flow ist iterierbar: nach einem Check-in kann der Nutzer zu jedem
früheren Schritt zurückkehren, ohne bisherige `MasterplanVersion`-Einträge zu
verlieren.

## 6. Architekturelle Erweiterungspunkte in V1

V1 hält bereits folgende Erweiterungspunkte bereit, die der Guided Masterplan
nutzen kann:

| Erweiterungspunkt | V1-Realisierung |
|---|---|
| Methoden-Versionierung | `MethodPolicy`, `pythagorean-v1` kanonisch |
| Wissenspaket-Versionierung | `KnowledgeBundle.version`, Loader für mehrere Versionen |
| Aussageklassen-Taxonomie | `ClaimType`-Enum, `claim_class` in V2-Wissen |
| Agenten-Adapter-Grenze | `numerology_agent` ist dünne Schicht, deterministisch geprüft |
| Export-/Import-Verträge | versioniert (`numra-export-v2`) |

## 7. Was der Guided Masterplan NICHT ist

- Keine Ablösung von V1. V1 bleibt das stabile, deterministische Produkt.
- Keine Gelegenheit, das Determinismus-vor-LLM-Prinzip aufzuweichen.
- Kein System, das selbst Massnahmen auswählt, priorisiert oder abschliesst
  (siehe §3).
- Kein Vehikel für medizinische, psychologische oder identitätsstiftende
  Diagnosen.
- Keine erweiterten Methodensysteme, Mehrsprachigkeit, Forschungs-Community,
  Cloud-Synchronisation oder Zukunftsdomänen — siehe
  `docs/roadmaps/numra-platform-expansion-roadmap.md`.

## 8. Entscheidungsprozess für den Guided Masterplan

Ein formelles Implementierungsprogramm (Welle 9) wird erst nach stabil
freigegebenem `0.3.0` begonnen. Es hat:

- eigene Roadmap (`docs/roadmaps/v2-guided-masterplan-*.md`),
- eigene ADRs (`0017+`),
- eigene Release-Sequenz,
- eigene Tests für die Nutzer-Autonomie-Regel (§3) als Hard-Gate.

Bis dahin ist dieses Dokument die einzige autorisierte Quelle für den Guided
Masterplan.

## 9. Verweise

- ADR 0016 — V2 User-Owned Masterplan Boundary
- ADR 0015 — Kumulative Release-Normalisierung auf 0.3.0rc1
- `docs/roadmaps/numra-platform-expansion-roadmap.md` — ausgelagerte
  Plattform-Erweiterungsideen (Methodensysteme, Mehrsprachigkeit, Forschung,
  Cloud, Agenten-Workflows, Zukunftsdomänen)
- Master-Vertrag §11 — Zukunftsmodule
- `PROJECT_CHARTER.md`, `ROADMAP.md`
