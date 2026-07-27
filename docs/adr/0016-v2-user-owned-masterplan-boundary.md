# ADR 0016 — V2 User-Owned Masterplan Boundary

> **Status:** Akzeptiert (28. Juli 2026)
> **Kontext:** Numra V1 (Pythagoreischer Standard, Determinismus vor LLM) ist mit `0.3.0rc1` funktional abgeschlossen. Ein darüber hinausgehender "V2 Masterplan" (Mehrsprachigkeit, erweiterte Methodensysteme, Community-Forschungspipeline, Benutzerkonten) liegt als Vision vor, darf aber nicht in den V1-Scope übergreifen.
> **Betrifft:** Produkt-Scope, V1/V2-Grenze, Roadmap, Spezifikation

---

## Entscheidung

Ein separater, **nutzergebauter V2-Masterplan** wird als Spezifikation
dokumentiert (`docs/product/numra-v2-guided-masterplan.md`), jedoch NICHT
in den V1-Implementierungsscope aufgenommen. Diese ADR zieht die harte Grenze:

1. **V1 (Scope von `0.3.0rc1` und stabil `0.3.0`):**
   - Pythagoreische Methode `pythagorean-v1` (kanonisch),
   - deterministischer Rechenkern, auditierbare Hashes,
   - versioniertes de-v1/de-v2-Wissen,
   - regelbasierte Interpretation,
   - optionale, kontrollierte DeepSeek-Adapterschicht,
   - lokale-first PWA.

2. **V2 (Spezifikation, keine Implementierung in diesem Release):**
   - erweiterte Methodensysteme (chaldäisch, kabbalistisch),
   - Mehrsprachigkeit über Deutsch hinaus,
   - Forschungs-Community-Features (Präregistrierung, geteilte Datensätze),
   - Benutzerkonten und cloudbasierte Synchronisation,
   - Vektor-Retrieval / fortgeschrittene Agenten-Workflows,
   - die in Master-Vertrag §11 genannten Zukunftsmodule.

Die Spezifikation `docs/product/numra-v2-guided-masterplan.md` ist eine
**Produktvision**, kein Implementierungsauftrag. Sie beschreibt, was V2
enthalten könnte, damit die V1-Architektur die nötigen Erweiterungspunkte
bereithält — ohne dass V2-Code in V1 eingeht.

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
- Master-Vertrag §11 — Zukunftsmodule (nicht Teil von V1)
- `docs/product/numra-v2-guided-masterplan.md` (Spezifikation)
- `PROJECT_CHARTER.md`, `ROADMAP.md`
