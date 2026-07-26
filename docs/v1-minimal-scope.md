# V1 Minimal Scope — Release `0.1.3 Contract Integrity` (erreicht) / `0.1.4 Complete Core Profile` (nächstes Ziel)

> **Dokumenttyp:** Operativer Release-Scope (Schmaler Zuschnitt des Master-Vertrags)
> **Version:** 1.1
> **Stand:** 2026-07-26 (aktualisiert nach v0.1.3)
> **Status:** Release `0.1.3` ist LIVE. Release `0.1.4` ist das nächste Ziel.
> **Beziehung:** Leitet ab aus `docs/governance/master-implementation-contract.md`. Der Master-Vertrag bleibt die North-Star-Plattform-Roadmap; dieses Dokument definiert die schmale operative Release-Roadmap.

---

## 1. Warum dieses Dokument

Lukes Review-Fazit (bindend): Die langfristige Plattform-Architektur (5 Ebenen, 15 Phasen 0–14 im Master-Vertrag) bleibt als **North-Star** erhalten. Sie ist aber nicht das operative Release-Ziel. Stattdessen wird eine **schmalere operative Release-Roadmap** eingeführt (`0.1.3 → 0.4.0`), mit der `0.1.3` als „Contract Integrity" den ersten stabilen Meilenstein darstellt.

Die North-Star (Phase 5–14 des Master-Vertrags) wird nicht gelöscht, sondern auf die Releases `0.2.0`, `0.3.0`, `0.4.0` und später verteilt. Was in `0.1.3` NICHT enthalten ist, ist nicht abgelehnt — es ist nur auf später verschoben.

---

## 2. Ziel von Release `0.1.3` (erreicht)

**Ein vollständig funktionierender, auditierbarer Numerologie-Kern mit CLI.**

Konkret:

- Eine Person kann über eine CLI mit Name + Geburtsdatum eingegeben werden.
- Der pythagoreische Rechenkern berechnet Life Path A + B deterministisch.
- Jede Berechnung hat einen nachvollziehbaren Audit-Trace.
- Alle Ergebnisse sind JSON-strukturiert und schema-validiert.
- Tests (Unit, Property, Golden) decken den Kern mit ≥ 95 % Coverage ab.
- CI läuft sauber (Ruff, Mypy strict, Pytest).

**Was `0.1.3` NICHT ist:** kein vollständiges Profil (fehlende Namenszahlen), kein Wissenspaket, keine freie Interpretation, keine API, kein Agent, kein Forschungsrahmen, kein Committee-Prozess. Diese sind spätere Releases.

---

## 3. Ziel von Release `0.1.4` (nächstes Ziel)

**Vollständiges deterministisches Personenprofil ohne Interpretation und ohne Zyklen.**

Konkret:

- Geburtstagszahl, Einstellungszahl, Ausdruckszahl, Seelenstrebenzahl, Persönlichkeitszahl, Reifezahl.
- Namenssegmentierung (Mehrfachnamen, Bindestriche, Apostrophe).
- Y-Klassifikation (duale Ausgabe bei Mehrdeutigkeit).
- Core Name und Active Name getrennt.
- Profilservice, CLI-Erweiterung, neue Schemas.
- Legacy-Life-Path-Vertrag bleibt unverändert.

---

## 3. Realistische Größenordnung

- **0.1.3 (erreicht):** ~1 Woche für Contract Integrity (Life Path A/B + Tooling + CI + Tests).
- **0.1.4 (nächstes Ziel):** ~1–2 Wochen für Complete Core Profile (alle Namenszahlen + Segmentierung).
- Die 15 Phasen (0–14) des Master-Vertrags werden hier **nicht 1:1 abgearbeitet**, sondern in operative Releases konsolidiert.

---

## 4. Enthalten in `0.1.3` (erreicht)

Diese Liste beschreibt den tatsächlichen Umfang von Release `0.1.3`.

### 4.1 Governance & Spezifikation

- [x] Master-Vertrag im Repository (`docs/governance/master-implementation-contract.md`)
- [x] README und Minimal-Scope (dieses Dokument)
- [x] ADRs `0001`–`0006` (Y-Regel, Umlaute, Mehrfachnamen, Core/Active-Name, Package-Layout, Release-Sequenz)
- [x] Die sechs Aussageklassen als Domain-Modelle (`input_fact`, `calculation_fact`, `traditional_claim`, `interpretive_hypothesis`, `empirical_evidence`, `practical_suggestion`)
- [x] Explizite Normalisierungspolicy:
  - `y_mode = phonetic` (siehe ADR 0001)
  - `de-direct-v1` für Umlaute (siehe ADR 0002)
- [x] Methoden-Policy als Domain-Typ (`MethodPolicy`), keine stillen Defaults

### 4.2 Deterministische Berechnungen (0.1.3)

- [x] Lebenswegzahl — Methode A (Gesamtdigit) und Methode B (Komponenten)
- [ ] Geburtstagszahl → **0.1.4**
- [ ] Einstellungszahl → **0.1.4**
- [ ] Ausdruckszahl → **0.1.4**
- [ ] Seelenstrebenzahl → **0.1.4**
- [ ] Persönlichkeitszahl → **0.1.4**
- [ ] Reifezahl → **0.1.4**

> Zyklusmodelle (Pinnacles, Challenges, persönliche Jahre/Monate/Tage) sind **NICHT** in `0.1.3` oder `0.1.4` enthalten — siehe `0.1.5`.

### 4.3 Verträge & Auditierbarkeit (0.1.3)

- [x] Audit-Trace für jede Berechnung (jeder Reduktionsschritt, jede Transformation)
- [x] JSON-Schemas (`person-input-v1.schema.json`, `calculation-result-v1.schema.json`, `method-policy-v1.schema.json`)
- [x] Deterministischer Hash-Envelope des Berechnungsvertrags
- [x] Schema-Version im Calculation-Result-Contract
- [x] Verpflichtendes `as_of_date` (kein `date.today()`-Fallback)
- [ ] Konsistenzprüfung: `Ausdrucks-Rohsumme = Vokalsumme + Konsonantensumme` → **0.1.4**

### 4.4 Schnittstellen (0.1.3)

- [x] **CLI** (Typer) — `numerology profile` und `numerology version`
- [x] JSON-Output, schema-validiert
- [x] **KEINE** FastAPI/HTTP-API in `0.1.3` (siehe `0.3.0`)

### 4.5 Qualitätssicherung (0.1.3)

- [x] Golden Tests (kanonische Testfälle mit erwarteten Ergebnissen)
- [x] Unit-Tests für jede Berechnung
- [x] Property-Based Tests (Hypothesis) für Reduktion, Trace-Stabilität, Invarianten
- [x] Ruff (Format + Check)
- [x] Mypy strict
- [x] Pytest mit Coverage
- [x] CI (GitHub Actions): `Quality Gates` (ruff, mypy, pytest + cov) + `Package Smoke` (Wheel-Build + Fresh-Venv-Install)
- [x] Core-Coverage **≥ 95 %** (erreicht: 95,73 %)
- [x] Gesamt-Coverage **≥ 85 %** (erreicht: 92,58 %)
- [x] Schema-Drift-Check in CI
- [x] Lockfile-Check in CI

### 4.6 Tooling (0.1.3)

- [x] `pyproject.toml` mit `uv`, Ruff, Mypy strict, Pytest, Hypothesis
- [x] `uv.lock` committed
- [x] Paketstruktur: `numerology_domain`, `numerology_engine`, `numerology_cli`, `numerology_api` (nur die für `0.1.3` nötigen Pakete — keine Attrappenpakete)

---

## 5. NICHT enthalten in `0.1.3` (erreicht) — auf spätere Releases verschoben

- [ ] **Geburtstagszahl, Einstellungszahl, Ausdruckszahl, Seelenstrebenzahl, Persönlichkeitszahl, Reifezahl** → `0.1.4 Complete Core Profile`
- [ ] **Namenssegmentierung und Y-Klassifikation** → `0.1.4`
- [ ] **Core Name / Active Name getrennt** → `0.1.4`
- [ ] **Zyklusmodelle** (Pinnacles, Challenges, persönliche Jahre/Monate/Tage) → `0.1.5 Deterministic Cycles`
- [ ] **Vollständiges Wissenspaket** (`knowledge/de/pythagorean-v1/*.yaml`) → `0.2.0 Knowledge`
- [ ] **Freie Interpretation** (regelbasierte Komposition, Spannungsmodell, Gegenhypothesen) → `0.2.0 Knowledge`
- [ ] **Safety Minimum** (Claims-Validator, Minderjährigenmodus) → `0.2.0`
- [ ] **FastAPI** → `0.3.0 Interfaces`
- [ ] **Vollständiges Safety-Subsystem** (Privacy, Crisis, PII) → `0.3.0`
- [ ] **Agent** (`numerology_agent`, LLM-Adapter) → `0.3.0`
- [ ] **Research Framework** (Hypothesenregister, Nullmodelle, Permutation) → `0.4.0 Research Preview`
- [ ] **Committee-Prozess** → `0.4.0` oder später
- [ ] **MkDocs-Material-Dokumentation** → `0.2.0` oder später

---

## 6. Walking Skeleton (erster Code-PR)

Bevor irgendwelche „vollständigen" Berechnungen implementiert werden, muss ein durchgehender dünner Strang funktionieren. Das **Walking Skeleton** für `0.1.0`:

```text
PersonInput
  → MethodPolicy (y_mode=phonetic, umlaut_policy=de-direct-v1, name_basis=core_name)
    → Normalizer (NFC + de-direct-v1 + Akzent-Entfernung + calculation_name)
      → LifePath A (Gesamtdigit) + LifePath B (Komponenten)
        → CalculationTrace (jeder Schritt dokumentiert)
          → JSON output (schema-validiert, deterministischer Hash)
            → CLI command (`numerology calculate profile`)
              → Golden tests (kanonische Fälle mit erwarteten Werten)
                → CI (ruff + mypy + pytest grün)
```

**Akzeptanz für das Walking Skeleton:**

1. Der CLI-Befehl `numerology calculate profile --name "..." --date "..."` gibt ein valides JSON zurück.
2. Wenigstens eine Kernzahl (Lebensweg A und B) ist berechnet und im Trace dokumentiert.
3. Der gleiche Input + Policy erzeugt byte-stabiles JSON.
4. Golden Tests laufen grün.
5. CI ist grün.

Sobald das Walking Skeleton steht, werden die weiteren Kernzahlen (Geburtstagszahl, Einstellungszahl, Ausdruckszahl, Seelenstrebenzahl, Persönlichkeitszahl, Reifezahl) schrittweise hinzugefügt — jedes Mal mit Unit-, Property- und Golden-Tests.

---

## 7. Akzeptanzkriterien für `0.1.0` (konservativ, nachweisbar)

Jede dieser Aussagen ist mit einem technischen Nachweis zu belegen. „Ich glaube, es funktioniert" reicht nicht (CLAUDE.md §4).

### 7.1 Funktionale Kriterien

- [ ] **AC-1:** Für mindestens **5 kanonische Golden Cases** liefert der Kern die erwarteten Lebenswegzahlen (A und B) — nachgewiesen durch grüne Golden Tests.
- [ ] **AC-2:** Für mindestens **5 kanonische Namen** liefert der Kern die erwarteten Ausdrucks-/Seelenstreben-/Persönlichkeitszahlen — nachgewiesen durch grüne Golden Tests.
- [ ] **AC-3:** Der CLI-Befehl `numerology calculate profile` funktioniert mit Name + Datum und gibt schema-validiertes JSON zurück.
- [ ] **AC-4:** Mehrdeutige Y-Fälle werden als solche markiert und erzeugen entweder Nutzer-Entscheidungs-Prompt oder Mehrfachausgabe — **niemals** stilles Raten (siehe ADR 0001).
- [ ] **AC-5:** Deutsche Umlaute (Ä, Ö, Ü, ß) werden nach `de-direct-v1` normalisiert, dokumentiert im Trace (siehe ADR 0002).
- [ ] **AC-6:** Mehrfachnamen und Bindestriche werden segmentiert behandelt, Gesamtsumme + Segmentergebnisse ausgegeben (siehe ADR 0003).
- [ ] **AC-7:** `core_name` und `active_name` werden getrennt berechnet, niemals still zusammengerechnet (siehe ADR 0004).

### 7.2 Nicht-funktionale Kriterien

- [ ] **AC-8:** `uv run ruff format --check .` → grün.
- [ ] **AC-9:** `uv run ruff check .` → grün.
- [ ] **AC-10:** `uv run mypy src tests scripts` → grün (strict).
- [ ] **AC-11:** `uv run pytest --cov=src --cov-fail-under=90` → grün (Core-Coverage 90–95 %).
- [ ] **AC-12:** `uv run python scripts/validate_schemas.py` → grün.
- [ ] **AC-13:** Identische Eingabe + Policy erzeugen byte-identisches JSON (Property-Based Test mit Hypothesis, ≥ 100 Beispiele).
- [ ] **AC-14:** Kein `import openai` / `import anthropic` / `import requests` / `import httpx` in `src/numerology_engine/` (Determinismus-vor-LLM, Master-Vertrag §2.4).
- [ ] **AC-15:** Keine `any`-Types, keine `# type: ignore` ohne Begründung.

### 7.3 Konsistenz-Kriterien

- [ ] **AC-16:** Ausdrucks-Rohsumme = Vokalsumme + Konsonantensumme — Property-Based Test bestätigt diese Invariante für alle gültigen Namen.
- [ ] **AC-17:** Jede Berechnung hat einen Audit-Trace mit mindestens: Input-Referenz, Methodenversion, einzelne Reduktionsschritte, Normalisierungsentscheidungen, deterministischer Hash.
- [ ] **AC-18:** Y-Mehrdeutigkeit wird im Trace als `disambiguation_required: true` markiert.

---

## 8. Ausblick auf spätere Releases (operative Roadmap)

Die Releases bauen aufeinander auf. Jedes spätere Release braucht `0.1.0` als feste Grundlage.

### 8.1 Release `0.2.0` — Knowledge

- Versioniertes Wissensmodell (`numerology_knowledge/`)
- Deutsche Content Packs für pythagoreische Archetypen 1–9, Meisterzahlen 11/22/33, karmische Schulden
- Regelbasierte Interpretations-Komposition (`numerology_interpretation/`)
- Gegenhypothesen, Aussageklassen-Tagging
- (Wahrscheinlich:) Zyklusmodelle (Pinnacles, Challenges, persönliche Jahre)
- Quellenstatus, Traditionshinweise
- Schema für Wissenseinträge

**Abhängigkeit:** Setzt `0.1.0` als deterministische Grundlage voraus.

### 8.2 Release `0.3.0` — Interfaces + Agent

- FastAPI (`apps/api/`) mit OpenAPI-Schema
- Vollständige CLI-Erweiterung (`numerology analyze profile`, `numerology compare profiles`)
- Safety-Subsystem (`numerology_safety/`): Minderjährigenschutz, Krisenunterbrechung, Claims-Validator
- Agenten-Adapter (`numerology_agent/`): LLM optional, kann keine Rechenergebnisse überschreiben
- Prompt-Evals (Hallucination, Extraktion, absolute Aussagen)

**Abhängigkeit:** Setzt `0.1.0` und `0.2.0` voraus.

### 8.3 Release `0.4.0` — Research Preview

- Forschungsrahmen (`numerology_research/`): Hypothesenregister, Präregistrierung, Nullmodelle, Permutation
- DuckDB + Parquet für Forschungsdaten
- Polars/Pandas-Analysepipelines
- Reproduzierbarer Smoke-Test mit synthetischen Daten
- Committee-Review-Prozess (5 Perspektiven: Engineering, Methodologie, Statistik, Safety, Produkt)

**Abhängigkeit:** Setzt `0.1.0`, `0.2.0`, `0.3.0` voraus.

### 8.4 Danach

- MkDocs-Material-Dokumentation in voller Breite
- Kompatibilitätsanalysen, Public-Biographies-Datenquellen
- Zukunftsmodule (Chaldäisch, Kabbala, Astrologie) — Master-Vertrag §11

---

## 9. OFFEN-Punkte (nicht von Luke oder Master-Vertrag geklärt)

Diese Punkte sind für `0.1.0` noch nicht final spezifiziert. Sie müssen vor oder während der Implementierung geklärt werden — entweder durch Luke oder durch einen späteren ADR.

- **OFFEN-1: Zyklusmodelle in `0.1.0`?** Der Master-Vertrag §3.2 listet Pinnacles, Challenges, persönliche Jahre als Kernberechnungen. Lukes `0.1.0`-Scope nennt sie nicht explizit. Klärung: bleiben Zyklen in `0.2.0`, oder werden sie in `0.1.0` als Minimum (z. B. nur persönliches Jahr) aufgenommen?
- **OFFEN-2: Minderjährigen-Status in `0.1.0`?** Lukes `0.1.0`-Scope listet `numerology_safety/` nicht. Aber der Master-Vertrag §6.1 verlangt `minderjaehrigenstatus` im `PersonInput`-Modell. Klärung: Feld in `0.1.0` mitführen (nur Datenpunkt, keine Logik), oder ganz weglassen?
- **OFFEN-3: Meisterzahlen-Behandlung in `0.1.0`?** Lebensweg 11/22/33 sind kanonisch. Klärung: in `0.1.0` als Berechnung enthalten (Reduktion behält Meisterzahlen bei), oder einfache Reduktion auf 1–9 in `0.1.0`?
- **OFFEN-4: Karmische Schuldenzahlen in `0.1.0`?** Analog OFFEN-3. Klärung nötig.
- **OFFEN-5: Sprach-Scope des `calculation_name`.** `de-direct-v1` ist Deutsch. Was passiert mit englischen, französischen, spanischen Namen? `OFFEN: muss geklärt werden, ob `0.1.0` nur deutsche Locale oder generische ASCII-Reduktion anbietet`.
- **OFFEN-6: CLI-Output-Format.** Reines JSON, oder JSON + menschenlesbarer Markdown-Report? Lukes `0.1.0`-Scope nennt „JSON-Output, schema-validiert". Klärung, ob `0.1.0` nur JSON oder beide Formate liefert.
- **OFFEN-7: MkDocs in `0.1.0`.** Master-Vertrag Phase 2 verlangt `mkdocs build --strict`. Lukes `0.1.0`-Scope erwähnt MkDocs nicht. Klärung: optional in `0.1.0`, oder als Pflicht?
- **OFFEN-8: Golden-Case-Quelle.** Wer definiert die 5+ kanonischen Golden Cases? Lukes Vorgabe, publizierte Quelle, oder eigene Festlegung mit Luke-Review?

---

## 10. Beziehung zum Master-Vertrag

Dieses Dokument **modifiziert** nicht den Master-Vertrag. Es **setzt einen engeren Release-Rahmen**. Bei Widerspruch in der Release-Logik gilt dieses Dokument; bei Widerspruch in den Fachprinzipien (Determinismus, Aussageklassen, Safety) gilt der Master-Vertrag.

| Aspekt | Master-Vertrag | V1 Minimal Scope (`0.1.0`) |
|---|---|---|
| Zeitliche Größenordnung | 14–16 Wochen, 15 Phasen | 2–4 Wochen, 1–3 PRs |
| Coverage-Schwelle Core | ≥ 95 % | 90–95 % |
| MkDocs strict als Gate | Ja (Phase 2) | OFFEN (siehe OFFEN-7) |
| API | Ja (Phase 9) | Nein (`0.3.0`) |
| Wissenspaket | Ja (Phase 5) | Nein (`0.2.0`) |
| Agent | Ja (Phase 10) | Nein (`0.3.0`) |
| Research | Ja (Phase 7) | Nein (`0.4.0`) |
| Committee | Ja (Phase 13) | Nein (`0.4.0` oder später) |
| North-Star-Status | Vollständig erhalten | Vollständig erhalten |

---

## 11. Änderungsprozess

Änderungen an diesem Scope erfordern:

1. Einen ADR (für inhaltliche/fachliche Änderungen, z. B. neue OFFEN-Antwort), oder
2. Eine explizite schriftliche Freigabe von Luke (für Scope-Anpassungen wie „Zyklen doch in `0.1.0`"), oder
3. Ein formelles Review, wenn der Scope grundsätzlich erweitert werden soll.

Direkte Edits ohne einen dieser drei Wege sind nichtig (analog zum Master-Vertrag).
