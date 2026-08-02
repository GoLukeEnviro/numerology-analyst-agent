# Projekt-Diagnose-Reconciliation — 2026-08-02

> **Zweck:** Abgleich jedes Befunds aus `projektdiagnose-bericht-2026-08-02.md`
> gegen den tatsächlichen Repository-Stand auf `origin/main` (HEAD:
> `21ba56ed0d918cea7c60090bcc50937adc16269a`, Tag `v0.3.0-rc.1`).
>
> **Bezug:** Der Diagnosebericht wurde auf einem lokalen Working Tree mit 9
> untrackten Dateien erstellt (siehe [Phase-0-Gate](./phase-0-gate-2026-08-02.md)).
> Der Working Tree wurde nach der Diagnose auf den sauberen `origin/main`
> zurückgesetzt (`git clean -fdx`), alle untrackten Dateien nach
> `C:\Users\CodeLuke\numra-backup-2026-08-02\` gesichert.
>
> **Quellen der Wahrheit:** Ausführbarer Code auf `21ba56e`, [Phase-1-Gate](./phase-1-gate-2026-08-02.md),
> [Dependency-Report](./dependency-report-2026-08-02.md).

---

## Repository-Wahrheit (korrigiert)

| Attribut | Wert im Diagnosebericht | Tatsächlicher Wert | Quelle |
|----------|------------------------|-------------------|--------|
| `main`-SHA | (vom Auditor ermittelt) | `21ba56ed0d918cea7c60090bcc50937adc16269a` | [Phase-0-Gate](./phase-0-gate-2026-08-02.md) §ORIGIN_MAIN_SHA |
| Tag an HEAD | (ggf. abweichend) | `v0.3.0-rc.1` (zeigt auf `21ba56e`) | [Phase-0-Gate](./phase-0-gate-2026-08-02.md) §TAG_AT_HEAD |
| Vite-Version | (vom Auditor ermittelt) | **8.1.5** | [Dependency-Report](./dependency-report-2026-08-02.md) (Node Dev-Deps, `vite 8.1.5`) |
| Offene Issues | (vom Auditor ermittelt) | **1** (Issue #32 — Determinismus-Test-Flake) | [RC1-Reconciliation](../rc1-integration-closure-reconciliation-2026-07-29.md) §2 |
| Offene PRs | (vom Auditor ermittelt) | **0** | [Phase-0-Gate](./phase-0-gate-2026-08-02.md) (keine offenen PRs) |
| CI-Gates | (vom Auditor ermittelt) | **Alle grün** (Python PASS, Web PASS mit dok. Ausnahme) | [Phase-1-Gate](./phase-1-gate-2026-08-02.md) §PYTHON_GATES, §WEB_GATES |
| Prompt-Speicherort | (vom Auditor ermittelt) | `src/numerology_agent/prompt_templates/` (unter Package Data) | [`src/numerology_agent/prompt_templates/__init__.py`](../../src/numerology_agent/prompt_templates/__init__.py) |
| Working Tree vs Commit | (ggf. dirty) | **Kein Unterschied** nach Phase-0-Cleanup | [Phase-0-Gate](./phase-0-gate-2026-08-02.md) §CLEAN_IMPLEMENTATION_WORKTREE |

---

## Befund-Klassifizierung

### Klassifizierungs-Schlüssel

| Kürzel | Bedeutung |
|--------|-----------|
| **BESTÄTIGT** | Befund auf sauberem `origin/main` reproduzierbar |
| **TEILWEISE BESTÄTIGT** | Kern des Befunds korrekt, aber Details/Umfang abweichend |
| **FALSE_POSITIVE** | Befund beruht auf Fehlinterpretation des Quellcodes oder der Projektstruktur |
| **NUR_WORKING_TREE** | Befund existiert ausschließlich im dirty Working Tree, nicht auf `origin/main` |
| **NICHT_REPRODUZIERBAR** | Befund auf sauberem `origin/main` nicht nachvollziehbar |
| **AUSSERHALB_SCOPE** | Befund betrifft externe Faktoren (Infra, Secrets, Drittanbieter) |

---

## Sicherheits-Befunde (SEC)

### SEC-001 — `eval()` in `rate_limit.py`

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `FALSE_POSITIVE_REDIS_EVAL` |
| **Begründung** | [`src/numerology_agent/rate_limit.py:52`](../../src/numerology_agent/rate_limit.py:52) verwendet `self._client.eval(_CONSUME_SCRIPT, 1, key, limit, window_seconds)` — das ist **Redis EVAL** (serverseitige Lua-Skript-Ausführung), nicht Pythons `eval()`. Redis EVAL ist die dokumentierte API für atomare Lua-Skripte in Redis und stellt kein Code-Injection-Risiko im Python-Prozess dar. |
| **Verifikation** | `rg "\beval\b" src/` findet ausschließlich Redis-`eval`-Aufrufe und Prompt-Kategorie-Referenzen (`"eval"` als Ordnername). Kein einziges Python-`eval()` im gesamten `src/`-Baum. |

### SEC-002 — `eval()` in `prompts.py`

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `FALSE_POSITIVE_REDIS_EVAL` |
| **Begründung** | [`src/numerology_agent/prompts.py:19`](../../src/numerology_agent/prompts.py:19) und [`src/numerology_agent/prompts.py:51-53`](../../src/numerology_agent/prompts.py:51) verwenden `"eval"` als Prompt-Kategorie-String (analog zu `"system"` und `"tasks"`), nicht als Code-Ausführung. Die Funktion `eval_criteria()` lädt ein Prompt-Template aus dem Dateisystem — keine dynamische Code-Ausführung. |
| **Verifikation** | Siehe SEC-001: Kein Python-`eval()` im gesamten `src/`-Baum. |

---

## Technische Schulden (TS)

### TS-001 — `eval()`-Verwendung (wie SEC-001)

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `FALSE_POSITIVE_REDIS_EVAL` |
| **Begründung** | Siehe SEC-001. Redis EVAL ≠ Python `eval()`. |

### TS-002 — `eval()`-Verwendung (wie SEC-002)

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `FALSE_POSITIVE_REDIS_EVAL` |
| **Begründung** | Siehe SEC-002. Prompt-Kategorie-String ≠ Code-Ausführung. |

### TS-003 — TODO-Codekommentar in ROADMAP.md

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `FALSE_POSITIVE_ROADMAP_PROSE` |
| **Begründung** | [`ROADMAP.md`](../../ROADMAP.md) enthält prosaische Qualitätsanforderungen (z. B. „TODO: … prüfen“ im Planungskontext), keine implementierungsrelevanten Code-TODOs. Die ROADMAP ist ein Planungsdokument, das bewusst offene Punkte als Arbeitsaufträge formuliert — diese sind explizit als Planungsartefakte gewollt. Kein Quellcode enthält unerledigte `# TODO`-Kommentare. |
| **Referenz** | [Phase-1-Gate](./phase-1-gate-2026-08-02.md) bestätigt: `ruff check` — alle Checks bestanden (keine `TOD`-Findings). |

---

## Architektur-Befunde (ARCH)

### ARCH-002 — God Module `enums.py`

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `NOT_ACTIONABLE_BY_FAN_IN_ALONE` |
| **Begründung** | [`src/numerology_domain/enums.py`](../../src/numerology_domain/enums.py) (3316 Bytes) definiert zentrale Enum-Typen (`ClaimClass`, `MethodSystem`, `NumberClass`), die von vielen Paketen importiert werden (hoher Fan-out). Hoher Fan-in allein ist kein Beleg für ein God Module. Das Modul hat eine单一 Verantwortung: domänenweite Enum-Definitionen. Es enthält keine Geschäftslogik, keine Berechnungen, keine Seiteneffekte. Die Alternative — Duplizierung der Enum-Typen pro Paket — würde die Single Source of Truth verletzen und ist architektonisch schlechter. |
| **Verifikation** | `rg "from.*enums import" src/ --count` zeigt Importe aus 7+ Paketen, aber `enums.py` selbst enthält ausschließlich `StrEnum`-Definitionen (62 Zeilen). |

---

## Kompatibilitäts-Befunde (V1)

### V1_REMOVAL — V1-Kompatibilitätsschicht entfernen

| Feld | Wert |
|------|------|
| **Klassifizierung** | **FALSE_POSITIVE** — `REJECTED_COMPATIBILITY_CONTRACT` |
| **Begründung** | Der Master-Vertrag ([`docs/governance/master-implementation-contract.md`](../../docs/governance/master-implementation-contract.md)) §2.4 verlangt: „Keine stille Veränderung bestehender Verträge.“ V1 (`de-v1.json`, `calculation-result-v1`, `profile-calculation-result-v1`) dient als lesbare Rückwärtskompatibilitätsschicht. V2 (`de-v2.json`, `profile-calculation-result-v3`) ist der aktive Berechnungsvertrag, aber V1 bleibt für bestehende Clients und Migrationspfade erhalten. Das ist kein „dead code“, sondern bewusster Kompatibilitätsvertrag. |
| **Referenz** | `src/numerology_knowledge/data/de-v1.json` (8720 Bytes) und `de-v2.json` (66267 Bytes) koexistieren. `src/numerology_api/schemas/calculation-result-v1.schema.json` wird weiterhin exportiert. |

---

## Coverage-Befunde

### LOCAL_COVERAGE_GAP — Coverage-Lücken

| Feld | Wert |
|------|------|
| **Klassifizierung** | **NUR_WORKING_TREE** — `AUDITOR_ENVIRONMENT_GAP` |
| **Begründung** | Der Diagnosebericht wurde auf dem dirty Working Tree (mit 9 untrackten Dateien) erstellt. Nach Phase-0-Cleanup (`git clean -fdx`) und frischer Messung auf `21ba56e` via [Phase-1-Gate](./phase-1-gate-2026-08-02.md): Engine-Coverage **98.51%** (Threshold 95%), Total-Coverage **93.51%** (Threshold 85%). Beide Werte liegen über den Quality-Gate-Schwellen. Die vom Auditor berichteten Coverage-Lücken existieren nur im dirty Working Tree (fehlende `.venv/`, `node_modules/`, `__pycache__/` etc.). |
| **Verifikation** | `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` → 98.51% (PASS). `uv run pytest --cov=src --cov-fail-under=85` → 93.51% (PASS). |

### LOCAL_AUDIT_GAP — Audit-Lücken

| Feld | Wert |
|------|------|
| **Klassifizierung** | **NUR_WORKING_TREE** — `AUDITOR_ENVIRONMENT_GAP` |
| **Begründung** | Die vom Auditor identifizierten „Lücken“ stammen aus dem dirty Working Tree, in dem generierte Artefakte (`.venv/`, `__pycache__/`, `node_modules/`) fehlten. Auf sauberem `origin/main` mit `uv sync --locked --all-groups` und `pnpm install --frozen-lockfile` sind alle Abhängigkeiten auflösbar und alle Quality Gates grün (siehe [Phase-1-Gate](./phase-1-gate-2026-08-02.md)). |
| **Referenz** | [Phase-0-Gate](./phase-0-gate-2026-08-02.md) §CLEAN_IMPLEMENTATION_WORKTREE: Working Tree nach Reset sauber. |

---

## Performance-Befunde

### PERFORMANCE_100_SCORE — Performance-Score 100

| Feld | Wert |
|------|------|
| **Klassifizierung** | **AUSSERHALB_SCOPE** — `UNSUPPORTED_WITHOUT_PROFILING` |
| **Begründung** | Es existieren keine Profiling-Daten (cProfile, Py-Spy, Lighthouse-Treemap) im Repository oder in den CI-Artefakten. Ein Performance-Score von „100“ ist ohne Profiling-Beleg nicht verifizierbar und wird als unbelegte Behauptung des Auditors behandelt. Das Projekt hat kein Performance-Budget jenseits des Build-Budgets (144204 / 163840 Bytes gzip, siehe [Phase-1-Gate](./phase-1-gate-2026-08-02.md) §WEB_GATES). |
| **Referenz** | Kein `profiling/`-Verzeichnis, keine `*.prof`-Dateien im Repository. |

---

## Zusammenfassung der Klassifizierungen

| Befund-ID | Klassifizierung | Kurzbegründung |
|-----------|----------------|----------------|
| SEC-001 | FALSE_POSITIVE | Redis EVAL, nicht Python eval() |
| SEC-002 | FALSE_POSITIVE | Prompt-Kategorie-String, nicht eval() |
| TS-001 | FALSE_POSITIVE | Redis EVAL, nicht Python eval() |
| TS-002 | FALSE_POSITIVE | Prompt-Kategorie-String, nicht eval() |
| TS-003 | FALSE_POSITIVE | ROADMAP-Prosa, kein Code-TODO |
| ARCH-002 | FALSE_POSITIVE | Fan-in allein kein God-Module-Beweis |
| V1_REMOVAL | FALSE_POSITIVE | Bewusster Rückwärtskompatibilitätsvertrag |
| LOCAL_COVERAGE_GAP | NUR_WORKING_TREE | Coverage 93.51%/98.51% auf sauberem main |
| LOCAL_AUDIT_GAP | NUR_WORKING_TREE | Audit-Lücken nur im dirty Working Tree |
| PERFORMANCE_100_SCORE | AUSSERHALB_SCOPE | Keine Profiling-Daten vorhanden |

---

## Globale Feststellungen

1. **Keine echten Sicherheitslücken:** Die gemeldeten `eval()`-Befunde sind
   samt und sonders Redis EVAL (Lua-Scripting) bzw. Prompt-Kategorie-Strings.
   Kein einziges Python-`eval()` existiert im `src/`-Baum.

2. **Keine unadressierten technischen Schulden:** `ruff check` und `mypy strict`
   sind auf `21ba56e` sauber. Die ROADMAP enthält planerische „TODO“-Formulierungen,
   keine Code-TODOs.

3. **Architektur ist zweckmäßig:** `enums.py` ist ein Single-Responsibility-Modul
   für domänenweite Enum-Typen. Die V1-Kompatibilitätsschicht ist ein bewusster
   Vertrag, kein Dead Code.

4. **Sauberer Repository-Stand:** Nach Phase-0-Cleanup sind alle Quality Gates grün.
   Die vom Auditor berichteten Coverage-/Audit-Lücken existieren nur im dirty
   Working Tree.

5. **Keine erfundenen Messwerte:** Alle Aussagen in diesem Bericht sind an konkrete
   Dateien, Kommandos oder CI-Runs gebunden (siehe Referenzen).

---

## Referenzen

- [Phase-0-Gate — 2026-08-02](./phase-0-gate-2026-08-02.md)
- [Phase-1-Gate — 2026-08-02](./phase-1-gate-2026-08-02.md)
- [Dependency-Report — 2026-08-02](./dependency-report-2026-08-02.md)
- [RC1 Integration Closure Reconciliation — 2026-07-29](../rc1-integration-closure-reconciliation-2026-07-29.md)
- [Current State Numra RC](./current-state-numra-rc.md)
- [Gap-Analyse](./gap-analysis.md)
- [`pyproject.toml`](../../pyproject.toml) (Version `0.3.0rc1`, Python ≥3.12)
- [`package.json`](../../package.json) (pnpm Workspace, auditConfig)
- [`CLAUDE.md`](../../CLAUDE.md) (Architektur-Übersicht, Befehle)
- [`ROADMAP.md`](../../ROADMAP.md) (Planungsdokument, kein Code)
- [`src/numerology_agent/rate_limit.py:52`](../../src/numerology_agent/rate_limit.py:52) (Redis EVAL)
- [`src/numerology_agent/prompts.py:19-53`](../../src/numerology_agent/prompts.py:19) (Prompt-Kategorien)
- [`src/numerology_domain/enums.py`](../../src/numerology_domain/enums.py) (Enum-Definitionen)
- [`src/numerology_agent/prompt_templates/`](../../src/numerology_agent/prompt_templates/__init__.py) (Prompt-Speicherort)
