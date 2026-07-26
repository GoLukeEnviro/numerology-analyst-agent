# Repository Baseline — v0.1.3

> **Dokumenttyp:** Audit / Baseline
> **Stand:** 26. Juli 2026
> **Repository:** `GoLukeEnviro/numerology-analyst-agent`
> **Default-Branch:** `main`
> **Aktueller `main`-Commit:** `21f5297`
> **Tag `v0.1.3`:** `9c50f4d` (unverändert seit Release)
> **Sprache:** Deutsch

---

## 1. Repository-Metriken

| Metrik | Wert |
|--------|------|
| Getrackte Dateien | 66 |
| Branches (remote) | `main` |
| Tags | `v0.1.0`, `v0.1.2`, `v0.1.3` |
| Gemergte PRs | #5, #6, #7, #8 |
| Offene PRs | 0 |
| Offene Issues | 0 |
| CI-Workflows | 1 (`ci.yml`) |
| CI-Jobs | 2 (`Quality Gates`, `Package Smoke`) |

---

## 2. Paketstruktur

```
src/
├── numerology_api/        # API-Verträge + versionierte JSON-Schemas
│   ├── __init__.py
│   ├── contracts.py
│   └── schemas/           # Source of Truth für installierbare Schemas
│       ├── calculation-result-v1.schema.json
│       ├── method-policy-v1.schema.json
│       └── person-input-v1.schema.json
├── numerology_cli/        # Typer-CLI
│   ├── __init__.py
│   └── main.py
├── numerology_domain/     # Pydantic-Domainmodelle
│   ├── __init__.py
│   ├── enums.py
│   ├── exceptions.py
│   └── models.py
└── numerology_engine/     # Deterministischer Rechenkern
    ├── __init__.py
    ├── alphabet.py
    ├── dates.py
    ├── normalization.py
    ├── reduction.py
    ├── service.py
    └── trace.py
```

**Abweichung vom Master-Vertrag:** CLI liegt unter `src/numerology_cli`, nicht `apps/cli`. API-Vertrag liegt unter `src/numerology_api`, nicht `apps/api`. Siehe ADR 0005.

---

## 3. Installierbare Pakete

- `numerology-analyst-agent` (via `uv build` / PyPI)
- Wheel: `numerology_analyst_agent-0.1.3-py3-none-any.whl`
- Source Distribution: `numerology_analyst_agent-0.1.3.tar.gz`

---

## 4. CLI-Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `numerology version` | Installierte Paketversion ausgeben |
| `numerology profile` | Life Path (A + B) berechnen und kanonisches JSON ausgeben |

---

## 5. CI-Jobs

| Jobname | Beschreibung |
|---------|-------------|
| `Quality Gates` | Ruff format + check, mypy strict, pytest + coverage |
| `Package Smoke` | Wheel bauen, in frischem Venv installieren, CLI ausführen |

---

## 6. Coverage-Schwellen

| Scope | Schwelle | Aktuell |
|-------|----------|---------|
| `src/numerology_engine` | ≥ 95 % | 95,73 % |
| `src` (gesamt) | ≥ 85 % | 92,58 % |

---

## 7. Veröffentlichte Artefakte (v0.1.3)

| Artefakt | Status |
|----------|--------|
| Tag `v0.1.3` | ✅ veröffentlicht |
| GitHub Release `v0.1.3 — Contract Integrity` | ✅ veröffentlicht |
| Wheel (`numerology_analyst_agent-0.1.3-py3-none-any.whl`) | ✅ im Release |
| Source Distribution (`numerology_analyst_agent-0.1.3.tar.gz`) | ✅ im Release |
| Release Notes (GitHub) | ✅ vorhanden |
| Release Notes (Repository) | ✅ unter `docs/releases/v0.1.3.md` |

---

## 8. Vorhandene Schemas

| Schema | Version | Quelle |
|--------|---------|--------|
| `person-input-v1.schema.json` | v1 | `src/numerology_api/schemas/` |
| `calculation-result-v1.schema.json` | v1 | `src/numerology_api/schemas/` |
| `method-policy-v1.schema.json` | v1 | `src/numerology_api/schemas/` |

---

## 9. Testdateien

```
tests/
├── conftest.py
├── golden/
│   ├── cases.yaml
│   ├── test_golden_cases.py
│   └── test_hash_golden.py
├── integration/
│   └── test_cli.py
├── property/
│   └── test_reduction_properties.py
└── unit/
    ├── test_alphabet.py
    ├── test_contracts.py
    ├── test_dates.py
    ├── test_normalization.py
    └── test_reduction.py
```

**Gesamt:** 118 Tests.

---

## 10. Bekannte technische Schulden

- Keine Namenszahlen (Geburtstags-, Einstellungs-, Ausdrucks-, Seelenstreben-, Persönlichkeits-, Reifezahl)
- Keine Zyklen (persönliches Jahr/Monat/Tag, Pinnacles, Challenges)
- Kein Wissensmodell
- Keine Interpretation
- Kein Safety-Subsystem
- Keine FastAPI
- Kein Agent
- Kein Forschungsrahmen
- Keine MkDocs-Dokumentation
- Kein Committee-Prozess
- `v1-minimal-scope.md` referenziert noch Release `0.1.0` statt `0.1.3`
- `gap-analysis.md` enthält historische Baseline vom 25.07.2026 (Ein-Datei-Zustand)
- `ROADMAP.md` zeigt Phase 0 als `IN PROGRESS` mit `0.1.0` als Ziel

---

## 11. Noch nicht implementierter Scope

Siehe `docs/audit/gap-analysis.md` (aktuelle Gap-Matrix) und `ROADMAP.md` (operative Release-Roadmap).
