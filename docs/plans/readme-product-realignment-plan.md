# README Product Realignment Plan

> **Status:** Approved
> **Erstellt:** 28. Juli 2026
> **Umsetzung:** Erst nach Abschluss der RC Integration Closure
> **Zielbranch:** `docs/readme-product-realignment`
> **Abhängigkeiten:** Calculation Contract V2, Core Integration Closure, Frontend Concurrency Closure, Staging Contract Closure

---

## Zweck

Die `README.md` im Repository-Root soll von einem technischen Statusdokument zu einer
**ehrlichen, professionellen Produktseite** umgebaut werden. Sie muss das tatsächlich
funktionierende Produkt beschreiben — nicht den vorgesehenen Zielzustand. Attraktivität
folgt Wahrheit, nicht umgekehrt.

### Nicht-Ziele

- Kein zweites Governance-Handbuch (dafür existieren `PROJECT_CHARTER.md`, `ROADMAP.md`, ADRs)
- Keine vollständige 15-Phasen-Roadmap
- Keine internen Prozessdetails oder Audit-Berichte
- Keine erfundenen Kontaktdaten oder Danksagungen
- Keine statischen Test-/Coverage-Zahlen
- Keine Forschungsfeatures als aktuelle Features

---

## Sequenzierung (bindend)

```
Calculation Contract V2 Closure
→ Core Integration Closure (Prompt / Knowledge / Composer-Verdrahtung)
→ Frontend Concurrency Closure (Abort-Race-Fix + Tests)
→ Staging Contract Closure
→ V2 Product Realignment
→ README Product Realignment          ← dieser Plan
→ Release Reconciliation
→ finaler Staging-Test (Deploy, Live-Smoke, Backup/Restore, Rollback)
→ Tag v0.3.0-rc.1
```

Die README wird **vor dem Tag**, aber nach allen technischen Closure-PRs finalisiert.
Der Screenshot wird beim README-PR aus dem finalen Build erzeugt.

---

## Finale Struktur (15 Sektionen, Ziel ~200 Zeilen)

```
┌──────────────────────────────────────────────────┐
│  # Numra                                          │
│  *Numerologie nachvollziehbar — deterministisch,  │
│  versioniert, lokal-first*                        │
│                                                   │
│  [CI] [Python 3.12+] [MIT] [PWA] [Int. Closure]  │
│  (5 Badges, kein Coverage, kein RC-Status)        │
├──────────────────────────────────────────────────┤
│  📸 Screenshot — erst nach Closure + echter       │
│     Aufnahme (docs/assets/numra-profile-          │
│     dashboard-dark.png), kein Platzhalter         │
├──────────────────────────────────────────────────┤
│  ## Inhalt                                        │
├──────────────────────────────────────────────────┤
│  ## Was ist Numra?                                │
│  1 Satz + 3-Spalten-Kerntabelle                   │
├──────────────────────────────────────────────────┤
│  ## Kernfunktionen                                │
│  ### Für Anwender (6 Punkte, ehrlich formuliert)  │
│  ### Für Entwickler (4 Punkte)                    │
├──────────────────────────────────────────────────┤
│  ## So funktioniert Numra                         │
│  Mermaid-Flowchart + Text-Pipeline + Ebenen-      │
│  Tabelle (Mermaid ergänzt, ersetzt nicht)         │
├──────────────────────────────────────────────────┤
│  ## Wissenschaftliche und methodische             │
│     Positionierung                                │
│  6 Aussageklassen-Tabelle + Determinismus-vor-    │
│  LLM-Callout + Keine-Diagnosen-Hinweis            │
├──────────────────────────────────────────────────┤
│  ## Datenschutz und optionale KI                  │
│  Lokale Speicherung, lokale Verschlüsselung,      │
│  DeepSeek deaktiviert, keine Klarnamen            │
├──────────────────────────────────────────────────┤
│  ## Tech-Stack (Tabelle, keine fixen Versionen)   │
├──────────────────────────────────────────────────┤
│  ## Schnellstart                                  │
│  ### CLI                                          │
│  ### PWA und API                                  │
│  ### Docker                                       │
├──────────────────────────────────────────────────┤
│  ## Qualitätssicherung                            │
│  (<details> einklappbar, keine statischen Zahlen) │
├──────────────────────────────────────────────────┤
│  ## Projektstatus                                 │
│  Ehrlicher Statusblock (s. 4.13)                  │
├──────────────────────────────────────────────────┤
│  ## Roadmap (nur nächste 3–4 Meilensteine)        │
├──────────────────────────────────────────────────┤
│  ## Mitwirken                                     │
│  (keine erfundene Sprachpflicht)                  │
├──────────────────────────────────────────────────┤
│  ## Lizenz und rechtlicher Hinweis                │
└──────────────────────────────────────────────────┘
```

---

## Die 12 Korrekturen gegenüber dem initialen Plan

| # | Korrektur | Umsetzung |
|---|-----------|-----------|
| 1 | Badges sind nicht kritisch | Nur 5 verlässliche Badges: CI, Python, License, PWA, Integration Closure |
| 2 | Kein RC-Badge vor Tag | `Integration Closure` bis `v0.3.0-rc.1` getaggt ist |
| 3 | Keine statischen Testzahlen | Formulierung: „umfangreiche Testmatrix mit getrennten Coverage-Gates" |
| 4 | Coverage-Badge nur mit Quelle | Weglassen bis Codecov/Coveralls eingerichtet |
| 5 | „Ende-zu-Ende-Verschlüsselung" ersetzen | „Lokale passphrasengeschützte Verschlüsselung — PBKDF2 + AES-GCM" |
| 6 | KI-Funktion nicht als produktiv darstellen | „Vorbereitete optionale KI-Schicht — standardmäßig deaktiviert und noch nicht öffentlich freigegeben" |
| 7 | Profil vorsichtig formulieren während Closure | „Auditierbarer Profilrechner — kanonischer V2-Methodenvertrag in Integration Closure" |
| 8 | Forschungsfeatures nur unter Roadmap | Klar labeln: „Geplant / nicht implementiert" |
| 9 | Tech-Stack korrigieren | Redis 8 (nicht 7), keine fixen Versionsnummern |
| 10 | Mermaid ergänzt, nicht ersetzt | Mermaid-Flowchart + Text-Pipeline + Ebenen-Tabelle |
| 11 | Keine erfundene Sprachpflicht | „Verwende klaren Conventional-Commit-ähnlichen Präfix" |
| 12 | Kein Kontakt ohne echte Daten | Abschnitt entfällt bis Launch-Gates (Betreiber, Adresse, Support, Datenschutz) geklärt |

---

## Vier getroffene Entscheidungen

### 1. Screenshot

**Kein Platzhalter in der veröffentlichten README.**

Nach Closure: `docs/assets/numra-profile-dashboard-dark.png` aus finalem Build erzeugen.
- Golden-Reference-Profil von Lukas oder vollständig synthetisches Profil
- Keine personenbezogenen Daten
- Desktop Dark-Theme
- Optional zusätzlich Mobile-Ansicht

### 2. Coverage-Badge

**Derzeit kein Badge.**

Später: pytest coverage XML → GitHub Action → Codecov/Coveralls → dynamischer Badge.
Ein statischer Badge würde falsche Aktualität suggerieren.

### 3. Sprache

**README-Fließtext vollständig auf Deutsch.**

Englisch nur für etablierte Fachbegriffe: API, CLI, PWA, local-first, fail-closed,
OpenAPI, Pull Request, Commit, Runtime, DeepSeek, Framework- und Paketnamen,
Feld- und Vertragsnamen im Code.

Überschriften auf Deutsch: „Was ist Numra?", „Kernfunktionen", „Architektur",
„Schnellstart", „Qualitätssicherung", „Projektstatus", „Mitwirken", „Lizenz".

### 4. Umfang

**~200 Zeilen. Kein zweites Governance-Handbuch.**

Aufnehmen: Hero, Badges, Screenshot (nach Aufnahme), Inhaltsverzeichnis, Was-ist-Numra,
Kernfunktionen, Pipeline/Architektur, wissenschaftliche Positionierung, Datenschutz/KI,
Tech-Stack, Quick Start (3 Pfade), Quality Gates, Projektstatus, Roadmap (nur nächste
Meilensteine), Contributing, Lizenz.

Nicht aufnehmen: 8+ Badges nur der Optik wegen, statische Coverage-Zahlen, unfertige
Screenshots, Forschungsfeatures als aktuelle Features, Kontakt ohne Daten, Danksagung
ohne Inhalt, vollständige 15-Phasen-Roadmap, Audit-Berichte, interne Prozessdetails.

---

## Statusblock (ehrlich, bis zur Closure)

```markdown
## Projektstatus

Numra befindet sich in der **Integration Closure für den ersten
0.3.0-Release-Kandidaten**.

Der deterministische Rechenkern, die lokale PWA, API, Speicherung,
Verschlüsselung und die versionierten Verträge sind implementiert. Vor dem
ersten RC-Tag werden derzeit insbesondere der kanonische Berechnungsvertrag,
die Prompt-/Knowledge-/Composer-Integration, die Frontend-Concurrency und der
private Staging-Vertrag abgeschlossen.

- **Aktuelle Quellversion:** `0.3.0rc1`
- **Jüngster veröffentlichter Tag:** `v0.1.3`
- **RC-Tag:** noch nicht gesetzt
- **DeepSeek:** standardmäßig deaktiviert
- **Öffentlicher Launch:** nicht freigegeben
```

---

## Definition of Done für den README-PR

- [ ] Keine Aussage über nicht implementierte Funktionen
- [ ] Kein RC-Badge vor vorhandenem Tag
- [ ] Kein Coverage-Badge ohne dynamische Quelle
- [ ] Kein leerer Screenshot-Platzhalter
- [ ] Keine personenbezogenen Daten im Screenshot
- [ ] DeepSeek-Status korrekt dargestellt (deaktiviert, nicht freigegeben)
- [ ] Aktuelle Methodenversion korrekt benannt (V2 nach Closure)
- [ ] Quick-Start-Befehle frisch ausgeführt und verifiziert
- [ ] Interne Links geprüft (keine 404)
- [ ] Mermaid-Diagramm auf GitHub korrekt gerendert
- [ ] README-Ziellänge ca. 180–250 Zeilen
- [ ] README ist Produktseite, nicht Audit- oder Governance-Dokument

---

## Freigabe

```
README-Struktur:                    GO
Hero und Logo:                      GO
Inhaltsverzeichnis:                 GO
Featureübersicht:                   GO MIT STATUSKORREKTUREN
Mermaid-Architektur:                GO
Tech-Stack:                         GO MIT REDIS-/VERSIONSKORREKTUR
Quick Start mit drei Pfaden:        GO
Contributing:                       GO OHNE ERFUNDENE SPRACHPFLICHT
Lizenzabschnitt:                    GO
Screenshot-Platzhalter:             NO-GO
Screenshot nach echter Aufnahme:    GO
statischer Coverage-Badge:          NO-GO
RC1-Release-Badge:                  NO-GO BIS TAG
Forschungsfeatures als Features:    NO-GO
komplette Umsetzung vor Closure:    NO-GO
```

**Schlussentscheidung: Der Plan ist nach diesen Korrekturen freigabefähig.**
Umsetzung erfolgt im Branch `docs/readme-product-realignment` nach Abschluss aller
technischen Closure-PRs und vor dem Tag `v0.3.0-rc.1`.
