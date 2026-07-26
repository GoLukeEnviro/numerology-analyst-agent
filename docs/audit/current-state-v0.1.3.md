# Current State — v0.1.3

> **Dokumenttyp:** Statusbericht
> **Stand:** 26. Juli 2026
> **Sprache:** Deutsch

---

## 1. Foundation Release 0.1.3 abgeschlossen

Der Release `v0.1.3 — Contract Integrity` ist veröffentlicht und enthält:

- Deterministischer Rechenkern: Life Path A + B
- Meisterzahlen 11, 22, 33
- Karmische Marker 13, 14, 16, 19
- Normalisierung `de-direct-v1`
- Audit-Trace für jede Berechnung
- Versionierter Calculation-Hash-Envelope
- Verpflichtendes `as_of_date`
- Versionierte JSON-Schemas im Wheel
- Golden-, Unit-, Property- und CLI-Tests
- Core-Coverage ≥ 95 %, Gesamt-Coverage ≥ 85 %
- Package-Smoke-Test in CI
- Branch Protection und Required Checks

## 2. Nächster Release: 0.1.4 — Complete Core Profile

Geplante Inhalte:

- Geburtstagszahl
- Einstellungszahl
- Ausdruckszahl
- Seelenstrebenzahl
- Persönlichkeitszahl
- Reifezahl
- Namenssegmentierung
- Y-Klassifikation
- Core Name / Active Name
- Profilservice, CLI-Erweiterung, neue Schemas

## 3. Release-Sequenz

```
0.1.3 Contract Integrity          ✅ LIVE
0.1.4 Complete Core Profile      ⏳ als nächstes
0.1.5 Deterministic Cycles       ⏳ folgt
0.2.0 Knowledge and Interpretation ⏳ folgt
0.3.0 Interfaces, Safety and Agent ⏳ folgt
0.4.0 Research Preview            ⏳ folgt
1.0.0 Platform V1                ⏳ folgt
```

## 4. Offene fachliche Entscheidungen

- Y-Regel: Mehrdeutiges Y → beide Varianten berechnen (siehe ADR 0001, Ergänzung ausstehend)
- Umlaut-Normalisierung: `de-direct-v1` bestätigt (ADR 0002)
- Mehrfachnamen/Bindestriche: Segmentierung bestätigt (ADR 0003)
- Core Name vs. Active Name: Getrennte Berechnung bestätigt (ADR 0004)
- Zyklen in 0.1.5 (separates Release, nicht in 0.1.4)
