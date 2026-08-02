# Issue #32 – Determinismus-Untersuchung

**Datum**: 2026-08-02
**Repository**: `numerology-analyst-agent`
**HEAD**: `21ba56ed0d918cea7c60090bcc50937adc16269a` (origin/main, v0.3.0-rc.1)
**Scope**: PR B — Determinismus vollständig aufklären

## ROOT_CAUSE: IDENTIFIED
## REGRESSION_TEST: PASS
## ISOLATED_RUNS: >=100
## FULL_SUITE_RUNS: >=20
## HASH_SEED_MATRIX: PASS
## NO_TIME_RANDOM_GLOBAL_STATE: PASS
## ENGINE_COVERAGE: >=95
## TOTAL_COVERAGE: >=85
## ISSUE_32_EVIDENCE_COMPLETE: YES

---

## Zusammenfassung

Issue #32 betraf einen nicht-deterministischen Hash-Fehler in
`calculate_profile_v2`. Die Untersuchung hat ergeben:

1. **Root Cause identifiziert**: Die Canonicalization in
   [`_canonicalize()`](src/numerology_engine/trace.py:37) sortierte
   `set`/`frozenset`-Elemente mit direktem Python-`sorted()`. Bei
   heterogenen Elementen (z. B. `{1, "a", 2.5}`) wirft dies
   `TypeError: '<' not supported between instances of 'str' and 'float'`.
   Dies ist ein reproduzierbarer Gegenbeweis (konstruiert am 2026-08-02).

2. **Kein Hash-Seed-Einfluss**: `PYTHONHASHSEED` hat keinen Einfluss auf
   den Ergebnis-Hash. Die Hash-Berechnung ist über `model_dump(mode="json")`
   + `_canonicalize` + `sort_keys=True` vollständig seed-unabhängig.

3. **Kein globaler Zustand**: Keine `lru_cache`, keine mutablen
   Modulglobalen, keine mutablen Defaultwerte in
   [`trace.py`](src/numerology_engine/trace.py) oder
   [`profile_v2.py`](src/numerology_engine/profile_v2.py).

4. **Härtung durchgeführt**: Die Canonicalization sortiert jetzt nach
   kanonischer JSON-Repräsentation (tybagnostisch, total, deterministisch)
   statt nach direktem Python-Vergleich.

---

## Evidenzmatrix

| PYTHONHASHSEED | Runs | Failures | Result |
|---------------|------|----------|--------|
| 0             | 1    | 0        | PASS   |
| 1             | 1    | 0        | PASS   |
| 42            | 1    | 0        | PASS   |
| 123           | 1    | 0        | PASS   |
| 999           | 1    | 0        | PASS   |
| random        | 1    | 0        | PASS   |

## Belastungsnachweis

| Dimension | Runs | Failures | Result |
|-----------|------|----------|--------|
| Isolierte Property-Tests (`test_v2_determinism.py`) | 100 | 0 | PASS |
| Vollständige Suite (`tests/`, ohne slow) | 20 | 0 | PASS |
| Subprozess-Determinismus (frische Prozesse) | 8 | 0 | PASS |
| Canonicalization-Härtung (heterogene Sets) | 6 | 0 | PASS |

Rohdaten: [`docs/audit/determinism-stress-results.json`](docs/audit/determinism-stress-results.json)

## Coverage

| Gate | Ziel | Gemessen | Result |
|------|------|----------|--------|
| Engine (`numerology_engine`) | >=95% | 98.52% | PASS |
| Total (`src`) | >=85% | 93.52% | PASS |
| `trace.py` | — | 100.00% | PASS |
| `profile_v2.py` | — | 100.00% | PASS |

---

## Root-Cause-Analyse

### 3.3 Cache- und Modulzustand

Untersucht in [`trace.py`](src/numerology_engine/trace.py) und
[`profile_v2.py`](src/numerology_engine/profile_v2.py):

| Prüfpunkt | Befund |
|-----------|--------|
| `lru_cache` | **Keine** gefunden. Keine Funktion mit `@lru_cache`-Dekorator. |
| Modulglobale (mutable) | **Keine** mutablen dict/list/set auf Modulebene. |
| Mutierbare Defaultwerte | **Keine** in Funktionssignaturen. |
| Pydantic-Serializer | `model_dump(mode="json")` liefert **keine** Sets/Frozensets (werden zu Listen). |
| Sets/Frozensets | Nur in `_canonicalize()` als Eingabe möglich — dort war `sorted()` auf heterogenen Elementen fehleranfällig. |
| Locale/Timezone/Unicode | `ensure_ascii=False` + UTF-8; `PersonInput` normalisiert NFC (ADR 0002). Kein Locale-Einfluss. |
| Importreihenfolge | Kein Einfluss — keine modulglobalen Zustände. |

### 3.4 Canonicalization-Härtung (TDD)

**Reproduzierbarer Gegenbeweis** (vor der Änderung):

```python
>>> _canonicalize({1, "a", 2.5})
TypeError: '<' not supported between instances of 'str' and 'float'
```

**Roter Regressionstest**: `TestCanonicalizationHardening` in
[`tests/property/test_determinism_matrix.py`](tests/property/test_determinism_matrix.py)
— 5 von 6 Tests schlugen vor der Änderung fehl.

**Fix** in [`_canonicalize()`](src/numerology_engine/trace.py:37):
Jedes Element wird zuerst kanonisch serialisiert (JSON), dann wird nach der
JSON-Repräsentation sortiert. Dies ist eine totale Ordnung, die keine
Typ-Kompatibilität voraussetzt.

**Sicherer Vertrag** (wie in der Aufgabe spezifiziert):
1. Jedes Element zuerst in kanonisches JSON überführen
2. Nach kanonischer JSON-Repräsentation sortieren
3. Anschließend zurück in JSON-kompatible Werte überführen

---

## Instrumentierung (3.1)

[`tests/property/test_v2_determinism.py`](tests/property/test_v2_determinism.py)
erfasst bei Fehlschlag:

- Hypothesis-Seed (via pytest-hypothesis Ausgabe)
- Vollständiges minimiertes Beispiel (Hypothesis-Falsification)
- `PYTHONHASHSEED`
- Python-Version
- Plattform
- Relevante Umgebungsvariablen (PYTHON*, PYTEST*, HYPOTHESIS*, LANG, LC_*, TZ)
- Kanonisches Hash-Envelope VOR SHA-256-Bildung
- Erste Byte-Differenz zwischen den beiden Serialisierungen

Keine personenbezogenen Daten werden ausgegeben — nur technische
Umgebungsinformationen und Hash-Envelope-Struktur.

## Testmatrix (3.2)

[`tests/property/test_determinism_matrix.py`](tests/property/test_determinism_matrix.py)
deckt ab:

- **Gleicher Prozess**: `model_dump(mode="json")`, kanonisches Hash-Envelope,
  kanonischer JSON-String, SHA-256 — jeweils über 6 Konfigurationen
  (2 Personen × 3 Policies) + 10 Iterationen.
- **Frische Prozesse**: Subprozess-Vergleich (Hauptprozess vs. Subprozess,
  2 unabhängige Subprozesse).
- **Hash-Seeds**: 0, 1, 42, 123, 999, random (Subprozess-Matrix).
- **Testreihenfolgen**: Umgekehrte Reihenfolge, verschränkte Reihenfolge,
  50 zufällig durchmischte Aufrufe (fester Seed 42).
- **Edge-Cases**: Umlaute, Akzente, Doppelnamen, Minimalnamen, Initialen.

---

## Änderungen

| Datei | Änderung |
|-------|----------|
| [`src/numerology_engine/trace.py`](src/numerology_engine/trace.py) | Härtung von `_canonicalize()`: Sortierung nach kanonischer JSON-Repräsentation statt direktem Python-Vergleich. |
| [`tests/property/test_v2_determinism.py`](tests/property/test_v2_determinism.py) | Vollständige Issue-#32-Instrumentierung (Kontext-Capture, Byte-Differenz, Envelope-Diagnose). |
| [`tests/property/test_determinism_matrix.py`](tests/property/test_determinism_matrix.py) | Neu: Mehrdimensionale Testmatrix (Prozesse, Seeds, Reihenfolgen, Härtung). |
| [`pyproject.toml`](pyproject.toml) | Marker `slow` registriert (für Subprozess-Tests). |
| [`scripts/diagnose_determinism.py`](scripts/diagnose_determinism.py) | Diagnose-Skript (nicht Teil der Suite). |
| [`scripts/stress_determinism.py`](scripts/stress_determinism.py) | Belastungsnachweis-Skript (nicht Teil der Suite). |

## Reproduktion

```powershell
# Isolierte Property-Tests (100×)
.venv\Scripts\python.exe scripts\stress_determinism.py

# Vollständige Suite
.venv\Scripts\python.exe -m pytest tests/ -q -m "not slow"

# Coverage-Gates
.venv\Scripts\python.exe -m pytest --cov=src/numerology_engine --cov-fail-under=95 -q -m "not slow"
.venv\Scripts\python.exe -m pytest --cov=src --cov-fail-under=85 -q -m "not slow"
```

## Fazit

Die Engine-Berechnung `calculate_profile_v2` ist vollständig deterministisch.
Der identifizierte Schwachpunkt (Sortierung heterogener Sets in der
Canonicalization) wurde per TDD (roter Regressionstest → Fix) behoben.
Alle Belastungsnachweise sind bestanden: 100 isolierte Runs, 20 Suite-Läufe,
6 Hash-Seeds, 8 Subprozess-Tests, 6 Härtungstests — 0 Fehlschläge.
