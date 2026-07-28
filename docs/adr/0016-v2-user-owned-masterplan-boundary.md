# ADR 0016 — V2 User-Owned Masterplan Boundary

> **Status:** Akzeptiert (28. Juli 2026); realignt auf den nutzergebauten
> Guided Masterplan (29. Juli 2026)
> **Kontext:** Numra V1 (Pythagoreischer Standard, Determinismus vor LLM) ist mit `0.3.0rc1` funktional abgeschlossen. Ein darüber hinausgehender "V2 Masterplan" liegt als Vision vor, darf aber nicht in den V1-Scope übergreifen. Die ursprüngliche V2-Spezifikation war von der eigentlichen Guided-Masterplan-Vision abgedriftet und enthielt Plattform-Erweiterungsideen, die separat gehören — siehe Realignment unten.
> **Betrifft:** Produkt-Scope, V1/V2-Grenze, Roadmap, Spezifikation

---

## Entscheidung

Ein separater, **nutzergebauter Guided Masterplan** wird als Spezifikation
dokumentiert (`docs/product/numra-v2-guided-masterplan.md`), jedoch NICHT
in den V1-Implementierungsscope aufgenommen. Diese ADR zieht die harte Grenze:

1. **V1 (Scope von `0.3.0rc1` und stabil `0.3.0`):**
   - Pythagoreische Methode `pythagorean-v1` (kanonisch),
   - deterministischer Rechenkern, auditierbare Hashes,
   - versioniertes de-v1/de-v2-Wissen,
   - regelbasierte Interpretation,
   - optionale, kontrollierte DeepSeek-Adapterschicht,
   - lokale-first PWA.

2. **V2 Guided Masterplan (Spezifikation, keine Implementierung in diesem
   Release):** ein nutzergebauter Reflexions- und Zielsetzungsprozess auf
   Basis des V1-Profils, mit den Core-Modellen `UserGoal`, `LifeArea`,
   `ReflectionEntry`, `ObservedPattern`, `UserConstraint`,
   `PriorityDecision`, `ActionOption`, `AcceptedAction`, `Milestone`,
   `Habit`, `ReviewCheckpoint`, `MasterplanVersion` und der verbindlichen
   Regel, dass nur der Nutzer eine Option in eine `AcceptedAction`
   umwandeln kann (siehe `docs/product/numra-v2-guided-masterplan.md` §3).

3. **Plattform-Erweiterung (separat ausgelagert, kein Teil des Guided
   Masterplan):** erweiterte Methodensysteme (chaldäisch, kabbalistisch),
   Mehrsprachigkeit über Deutsch hinaus, Forschungs-Community-Features,
   Benutzerkonten und cloudbasierte Synchronisation, fortgeschrittene
   Agenten-Workflows sowie die in Master-Vertrag §11 genannten
   Zukunftsdomänen (Astrologie, Human Design, Enneagramm) — siehe
   `docs/roadmaps/numra-platform-expansion-roadmap.md`.

Die Spezifikation `docs/product/numra-v2-guided-masterplan.md` ist eine
**Produktvision**, kein Implementierungsauftrag. Sie beschreibt, was der
Guided Masterplan enthalten könnte, damit die V1-Architektur die nötigen
Erweiterungspunkte bereithält — ohne dass V2-Code in V1 eingeht.

## Realignment (29. Juli 2026)

Die ursprüngliche Fassung von `docs/product/numra-v2-guided-masterplan.md`
vermischte den nutzergebauten Guided Masterplan mit Plattform-
Erweiterungsideen (Methodensysteme, Mehrsprachigkeit, Forschung, Cloud,
Agenten-Workflows, Zukunftsdomänen). Diese Vermischung widersprach der
ursprünglichen Guided-Masterplan-Vision und wurde korrigiert:

- Die Guided-Masterplan-Spezifikation beschreibt jetzt primär den
  nutzergebauten Flow und die Core-Modelle (Abschnitt 2 oben).
- Alle Plattform-Erweiterungsideen wurden unverändert inhaltlich nach
  `docs/roadmaps/numra-platform-expansion-roadmap.md` verschoben.
- Die alte Fassung bleibt in der Git-Historie dieser Datei erhalten
  (Rollback: `git log -- docs/product/numra-v2-guided-masterplan.md`).

## Begründung

- **Scope-Disziplin:** Master-Vertrag §11 listet Zukunftsmodule ausdrücklich
  als "nicht Teil von Version 1" auf. Ein V2-Masterplan im V1-Repo riskiert
  Scope-Creep und verletzt das Determinismus-vor-LLM-Prinzip durch
  vorzeitige Komplexität.
- **Architekturelle Vorsorge:** Die Plugin-/Methodenschnittstellen aus dem
  Master-Vertrag ermöglichen es, V2-Module später ergänzend hinzuzufügen,
  ohne den pythagoreischen Kern zu verändern. Die V2-Spezifikation macht
  deutlich, welche Erweiterungspunkte V1 bereithalten muss.
- **Klare Nutzererwartung:** Anwender und Mitwirkende müssen verstehen,
  dass V1 ein abgeschlossenes, deterministisches Produkt ist und dass V2
  ein späteres, separat geplantes Programm darstellt.

## Konsequenzen

- Kein V2-Code in V1-Commits. V2-spezifische Implementierungen werden
  zurückgewiesen, solange sie nicht über ein separates V2-Programm
  formal freigegeben sind.
- Die V2-Spezifikation darf Architekturentscheidungen in V1 inspirieren
  (Erweiterungspunkte), aber keine V1-Verträge oder -Methoden verändern.
- Ein späteres V2-Implementierungsprogramm (Welle 9) hat seine eigene
  Roadmap, eigene ADRs und eigene Release-Sequenz.
- Die Trennung wird in `ROADMAP.md` und `PROJECT_CHARTER.md` sichtbar gemacht.

## Verweise

- ADR 0015 — Kumulative Release-Normalisierung auf 0.3.0rc1
- `docs/roadmaps/numra-platform-expansion-roadmap.md` — ausgelagerte
  Plattform-Erweiterungsideen
- Master-Vertrag §11 — Zukunftsmodule (nicht Teil von V1)
- `docs/product/numra-v2-guided-masterplan.md` (Spezifikation)
- `PROJECT_CHARTER.md`, `ROADMAP.md`
