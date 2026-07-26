# ADR 0006 — Operational Release Sequencing

> **Status:** Akzeptiert (26. Juli 2026)
> **Kontext:** Nach Abschluss von `v0.1.3` muss die operative Release-Sequenz für die folgenden Versionen festgelegt werden.
> **Betrifft:** Release-Planung, Roadmap

---

## Entscheidung

Die operative Release-Sequenz ab `v0.1.3` ist:

```
0.1.3 Contract Integrity          ✅ LIVE
0.1.4 Complete Core Profile      ⏳ als nächstes
0.1.5 Deterministic Cycles       ⏳ folgt
0.2.0 Knowledge and Interpretation ⏳ folgt
0.3.0 Interfaces, Safety and Agent ⏳ folgt
0.4.0 Research Preview            ⏳ folgt
1.0.0 Platform V1                ⏳ folgt
```

## Zusätzliche Festlegungen

1. **Safety Minimum für 0.2.0:** Ein minimales Claims- und Minderjährigen-Safety-Gate wird bereits für `0.2.0` verpflichtend. Vollständige Privacy-, Crisis- und API-Safety folgt in `0.3.0`.

2. **Kein Feature-Code ohne Spec:** Keine neue Berechnung darf implementiert werden, bevor ihre Methode vollständig spezifiziert und manuell geprüft ist (Welle 2).

3. **Legacy-Kompatibilität:** Der bestehende `0.1.3`-Vertrag (`calculate_life_path`, `calculation-result-v1`) darf nicht still verändert werden. Neue Verträge werden parallel eingeführt.

## Begründung

- Die Sequenz minimiert Abhängigkeiten: Rechenkern → Wissen → Interpretation → Schnittstellen → Forschung.
- Jeder Release baut auf dem vorherigen auf und ist eigenständig testbar.
- Safety wird schrittweise eingeführt, nicht als Big-Bang.

## Konsequenzen

- Releases sind streng sequenziell. Kein paralleles Arbeiten an zwei Releases.
- Jeder Release bekommt einen eigenen Major/Minor-Bump.
- Die Roadmap in `ROADMAP.md` wird entsprechend aktualisiert.
