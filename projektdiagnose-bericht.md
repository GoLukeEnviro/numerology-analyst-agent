# 🔍 Projektdiagnose & GAP-Analyse

**Projekt**: Numra (`numerology-analyst-agent`)
**Pfad**: `E:\VS-code-Projekte-5.2025\numerology-analyst-agent` — analysiert im Worktree `.claude/worktrees/projekt-diagnose-b2c8c9`, Branch `claude/projekt-diagnose-b2c8c9`, HEAD `6b4d71ab`
**Datum**: 2026-08-03
**Erstellt von**: Claude Code, Skill `projekt-diagnose`
**Analyseumfang**: alle sieben Bereiche
**Stand des Arbeitsverzeichnisses**: sauber — keine Änderungen an versionierten Dateien, eine unversionierte Datei (`.claude/plans/dapper-fluttering-kazoo.md`, das Planungsartefakt dieses Laufs). Die Analyse beschreibt damit den Commit-Stand.

> **Evidenz lesen:** `GEMESSEN` = in diesem Lauf durch ein Kommando ermittelt ·
> `BERICHTET` = aus einem Repo-Artefakt übernommen, nicht nachgeprüft ·
> `UNVERIFIZIERT` = in diesem Lauf nicht bestimmbar. Das vollständige Messprotokoll
> steht in Anhang A.

## Inhalt

1. [Executive Summary](#-executive-summary)
2. [Projektstruktur & Architektur](#️-1-projektstruktur--architektur)
3. [Codequalität](#-2-codequalität)
4. [Technische Schulden](#-3-technische-schulden)
5. [Sicherheit](#-4-sicherheit)
6. [Tests & Qualitätssicherung](#-5-tests--qualitätssicherung)
7. [Dokumentation](#-6-dokumentation)
8. [Performance & Wartbarkeit](#-7-performance--wartbarkeit)
9. [GAP-Analyse](#-8-gap-analyse)
10. [Priorisierte Handlungsempfehlungen](#-9-priorisierte-handlungsempfehlungen)
11. [Maßnahmen-Roadmap](#️-10-maßnahmen-roadmap)
12. [Anhang](#-anhang)

---

## 📊 Executive Summary

Numra ist ein technisch überdurchschnittlich diszipliniertes Projekt: keine zyklischen Importe, `mypy strict`, gemessene Testabdeckung von 93,44 % gesamt und 98,52 % im Rechenkern, 465 grüne Tests, 16 ADRs und ein durchgehend belegter Determinismus-Vertrag. Der mit Abstand schwerwiegendste Befund liegt nicht in der Codequalität, sondern in der Anbindung: Der vollständig implementierte, zu 100 % testabgedeckte und golden-verifizierte Berechnungsvertrag `pythagorean-v2` wird von **keinem** Produktionspfad erreicht — nachgewiesen über sechs Stufen bis hin zu einem Laufzeittest gegen den echten Endpunkt. Verschärfend kommt hinzu, dass der Profilendpunkt eine Anfrage mit `policy.version="v2"` nicht ablehnt, sondern mit HTTP 200 und einem V1-Ergebnis beantwortet, das die V2-Policy im Envelope trägt; ein Client kann diese Fehletikettierung nicht erkennen. Auf der Abhängigkeitsseite meldet `pip-audit` null Schwachstellen, `pnpm audit` dagegen eine mit `high` bewertete CSRF-Lücke in `react-router`, deren Behebung einen Hauptversionssprung erfordert.

### Gesamtbewertung

| Metrik | Wert |
|---|---|
| **Gesamt-Score** | **81,95 / 100** |
| Einstufung | Gut — solide Basis mit geringfügigem Verbesserungspotenzial |
| Befunde gesamt | 14 (1 kritisch, 2 hoch) |
| Ungemessene Leitmetriken | 1 von 7 |

> Der Gesamt-Score verdichtet sieben Bereiche zu einer Zahl. Er eignet sich zum Vergleich
> desselben Projekts über die Zeit und zum Auffinden des schwächsten Bereichs — nicht zum
> Vergleich verschiedener Projekte und nicht als Freigabekriterium. Die fachliche
> Richtigkeit des Codes prüft diese Diagnose an keiner Stelle.

### Einzelbewertungen

| Bereich | Score | Gewicht | Beitrag | Einstufung | Leitmetrik-Evidenz |
|---|---|---|---|---|---|
| Projektstruktur & Architektur | 81/100 | 10 % | 8,10 | Gut | GEMESSEN |
| Codequalität | 88/100 | 20 % | 17,60 | Gut | GEMESSEN |
| Technische Schulden | 66/100 | 20 % | 13,20 | Befriedigend | GEMESSEN |
| Sicherheit | 88/100 | 20 % | 17,60 | Gut | GEMESSEN |
| Tests & Qualitätssicherung | 88/100 | 15 % | 13,20 | Gut | GEMESSEN (Python) / UNVERIFIZIERT (Web) |
| Dokumentation | 95/100 | 5 % | 4,75 | Hervorragend | GEMESSEN |
| Performance & Wartbarkeit | 75/100 | 10 % | 7,50 | Gut | UNVERIFIZIERT |

**Deckel-Hinweis.** Der Bereich *Performance & Wartbarkeit* ist auf 75 gedeckelt: Der statische Musterscan ist gelaufen und ergibt genau einen Treffer oberhalb der Schwellen, aber eine Performance-Aussage setzt eine Laufzeitmessung voraus. Es wurde kein Benchmark ausgeführt und es existieren keine Profiling-Artefakte im Repository. Beim Bereich *Tests* wurde eine nach Produktions-LOC gewichtete Teilbewertung angewandt (Details in Abschnitt 5.4), weil nur die Python-Coverage freigegeben und gemessen wurde.

### ⚠️ Widersprüche

Befunde, die einer anderen Quelle widersprechen. Beide Seiten sind benannt, keine ist
als richtig gesetzt — diese Punkte brauchen eine menschliche Entscheidung.

| # | Befund | Quelle A | Quelle B |
|---|---|---|---|
| — | Keine Widersprüche festgestellt | — | — |

Geprüft wurde gezielt gegen `docs/audit/project-diagnosis-reconciliation-2026-08-02.md` (der Abgleich einer Vordiagnose vom Vortag) sowie gegen den vom Auftraggeber gelieferten, unumgesetzten Umsetzungsplan zum `pythagorean-v2`-Vertrag. In beiden Fällen ergab die unabhängige Nachprüfung Übereinstimmung statt Widerspruch:

- Der Vorbericht stuft die `eval`-Meldungen als Fehlalarme ein (`FALSE_POSITIVE_REDIS_EVAL`, dort Zeile 55). Die hier durchgeführte Einzelprüfung von `src/numerology_agent/rate_limit.py:22` und `:52` bestätigt das unabhängig: Es handelt sich um Redis-Lua-Ausführung mit festem Skript-Literal, nicht um Pythons `eval`.
- Der Vorbericht nennt Coverage-Werte von 93,51 % und 98,51 % (dort Zeile 126, Evidenz `BERICHTET`). Die eigene Messung in diesem Lauf ergibt 93,44 % und 98,52 % — die Abweichung liegt im Bereich der seither erfolgten Commits und stützt die Vorwerte.
- Der Umsetzungsplan trifft 17 Ist-Aussagen über den aktuellen Code. Die nachgeprüften Aussagen zu `routes/profiles.py`, `analysis_runtime.py`, `numerology_cli/main.py`, `prompts.py` und `deepseek.py` bestätigten sich. Dass die geplanten Wellen 0–5C noch nicht umgesetzt sind, ist **kein** Widerspruch, sondern der erwartbare Zustand eines Plandokuments.

---

## 🏗️ 1. Projektstruktur & Architektur

### 1.1 Verzeichnisstruktur

```
numerology-analyst-agent/
├── src/                          Python-Pakete (Rechenkern, API, CLI)
│   ├── numerology_domain/        Verträge und Typen (pydantic v2, frozen)
│   ├── numerology_engine/        deterministischer Rechenkern (V1 + V2)
│   ├── numerology_knowledge/     versionierte Wissenspakete
│   ├── numerology_interpretation/regelbasierte Interpretationskomposition
│   ├── numerology_safety/        Claims-, Sprach- und Injection-Validierung
│   ├── numerology_agent/         optionaler LLM-Adapter (DeepSeek)
│   ├── numerology_api/           zustandslose FastAPI-Grenze
│   └── numerology_cli/           Typer-CLI
├── apps/web/src/                 React/Vite/TypeScript-PWA
│   ├── api/                      generierter OpenAPI-Client
│   ├── features/                 vertikale Feature-Slices
│   ├── storage/                  IndexedDB (Dexie) inkl. Verschlüsselung
│   └── pwa/                      Service-Worker-Update-Handling
├── tests/                        unit · integration · golden · property · deployment
├── docs/                         adr · governance · methods · audit · plans · releases · …
├── openapi/                      exportierte API-Verträge
├── scripts/                      Export-, Validierungs- und Diagnosewerkzeuge
├── deploy/ · docker/             Betriebsartefakte
└── examples/ · prompts/
```

### 1.2 Technologie-Stack

| Kategorie | Technologie | Version | Evidenz |
|---|---|---|---|
| Sprache Backend | Python | ≥ 3.12 (Lauf: CPython 3.12.11) | GEMESSEN (`uv run --locked python --version`) |
| Paketmanager Backend | uv | 0.11.32 | GEMESSEN (`uv --version`) |
| Web-Framework | FastAPI | 0.140.0 | GEMESSEN (`uv tree --frozen --outdated`) |
| ASGI-Server | uvicorn[standard] | 0.51.0 | GEMESSEN (`uv tree --frozen --outdated`) |
| Datenmodelle | pydantic | 2.13.4 | GEMESSEN (`uv tree --frozen --outdated`) |
| CLI | typer | 0.27.0 | GEMESSEN (`uv tree --frozen --outdated`) |
| Rate-Limiting | redis | 7.4.1 | GEMESSEN (`uv tree --frozen --outdated`) |
| Sprache Frontend | TypeScript | 5.9.3 | GEMESSEN (`pnpm outdated --recursive --format json`) |
| UI | React / react-dom | 19.2.8 | GEMESSEN (`pnpm outdated --recursive --format json`) |
| Build | Vite | 8.1.5 | GEMESSEN (`pnpm outdated --recursive --format json`) |
| Lokale Persistenz | Dexie (IndexedDB) | 4.4.4 | GEMESSEN (`pnpm outdated --recursive --format json`) |
| Test Backend | pytest / hypothesis | 9.1.1 / 6.161.5 | GEMESSEN (`uv tree --frozen --outdated`) |
| Test Frontend | vitest / Playwright | 4.1.10 / 1.62.0 | GEMESSEN (`pnpm outdated --recursive --format json`) |
| Lint / Typen | ruff 0.12.12 · mypy 1.20.2 (strict) | — | GEMESSEN (`uv tree --frozen --outdated`) |
| CI | GitHub Actions | `ci.yml`, `codeql.yml` | GEMESSEN (`python scripts/inventar.py`) |

### 1.3 Architekturmuster

Das Projekt setzt eine **geschichtete Paketarchitektur mit gerichteter Abhängigkeitskette** um. Woran das erkennbar ist — nicht behauptet, sondern gemessen:

- **Acht separate Python-Pakete** unter `src/`, jedes mit eigener Verantwortung (Verzeichnisstruktur, siehe 1.1).
- **Null zyklische Importe** über den gesamten Importgraphen (`python scripts/inventar.py`). Das ist bei acht Paketen kein Zufall, sondern das Ergebnis der über `ruff.lint.isort` mit `known-first-party` erzwungenen Importrichtung.
- **Der Rechenkern ist tatsächlich isoliert**: Der Musterscan findet in `src/numerology_engine/` keinen Netzwerk- oder LLM-Import. Das im Master-Vertrag verankerte Grundprinzip „Determinismus vor LLM" ist damit strukturell und nicht nur dokumentarisch durchgesetzt.
- **Die API-Schicht ist zustandslos** aufgebaut: `create_app()` ist eine Factory, die Middleware-Kette wird explizit in definierter Reihenfolge verdrahtet (`src/numerology_api/app.py:64-86`).
- **Das Frontend folgt vertikalen Feature-Slices** (`apps/web/src/features/{profile,analysis,report,export}/`) mit getrennter Speicher- und PWA-Schicht.

Die drei vom Werkzeug gemeldeten God-Module sind **Fan-in-Artefakte, keine Befunde**: `numerology_domain.models` (42 eingehende Importe) ist ein reines Re-Export-Aggregat, `numerology_domain.enums` (22) enthält ausschließlich Enum-Definitionen, `numerology_engine.profile` (14) ist der V1-Rechenkern selbst. Hoher Fan-in ohne Geschäftslogik und ohne Seiteneffekte belegt kein God-Module; die Alternative — Duplizierung der Verträge je Paket — wäre architektonisch schlechter.

Die Schwäche liegt woanders: **Die Versionierung der Berechnungsmethode ist in der Architektur angelegt, aber an der Systemgrenze nicht durchgesetzt.** Der Rechenkern kennt zwei Methodenverträge, die API kennt nur einen — und lehnt den anderen nicht ab, sondern beantwortet ihn falsch.

### 1.4 Bewertung

**Score**: 81/100 – Gut · Leitmetrik: GEMESSEN

Die Fünf-Ebenen-Struktur ist real umgesetzt und messbar eingehalten: null zyklische Importe, saubere Importrichtung, kein Netzwerk- oder LLM-Import im Rechenkern. Der Abzug entfällt vollständig auf die nicht durchgesetzte Methodenversionierung an der API- und CLI-Grenze. Abzug: ARCH-001 (hoch), ARCH-002 (mittel), ARCH-003 (niedrig).

| # | Befund | Schwere | Fundstelle | Evidenz | Aufwand |
|---|---|---|---|---|---|
| ARCH-001 | Profilendpunkt akzeptiert `policy.version="v2"` und antwortet mit einem V1-Ergebnis | hoch | `src/numerology_api/routes/profiles.py:26` | GEMESSEN | gering |
| ARCH-002 | Analyse-Runtime kanonisiert Profile ausnahmslos mit dem V1-Rechenkern | mittel | `src/numerology_api/analysis_runtime.py:55` | GEMESSEN | mittel |
| ARCH-003 | CLI bietet keine Auswahl der Berechnungsmethode | niedrig | `src/numerology_cli/main.py:98` | GEMESSEN | gering |

---

## 📝 2. Codequalität

### 2.1 Metriken

| Metrik | Wert | Bewertung | Evidenz |
|---|---|---|---|
| Codezeilen gesamt | 34.321 | — | GEMESSEN |
| Dateien > 400 Zeilen | 19 | unkritisch — überwiegend generierte Artefakte | GEMESSEN |
| Funktionen > 50 Zeilen | 30 | erhöht | GEMESSEN |
| Zyklische Abhängigkeiten | 0 | vorbildlich | GEMESSEN |
| Code-Duplikate (≥ 10 Zeilen) | 10 | gering | GEMESSEN |
| Tiefe Verschachtelung (> 4) | 1 | vorbildlich | GEMESSEN |
| Funktionen mit > 5 Parametern | 4 | gering | GEMESSEN |

Von den 19 Dateien über 400 Zeilen sind 13 generierte oder deklarative Artefakte: OpenAPI-Exporte (2 × 1.775 Zeilen), JSON-Schemas (4 Dateien), das Wissensbundle `de-v2.json` (1.452), Stylesheet (1.358) und Dokumentation (Master-Vertrag 1.247, ROADMAP 981). Nur sechs sind echte Logikmodule, davon zwei Testdateien. Die Zahl ist damit deutlich weniger alarmierend, als sie isoliert wirkt.

### 2.2 Befunde

| # | Befundtyp | Datei | Zeile | Beschreibung | Schwere | Evidenz |
|---|---|---|---|---|---|---|
| CQ-001 | Duplikation | `src/numerology_domain/models.py` | 19 | 72 aufeinanderfolgende Zeilen identisch mit `_models/__init__.py:9` — die Exportliste des Domain-Pakets ist doppelt gepflegt | mittel | GEMESSEN |
| CQ-002 | Lange Funktionen | `src/numerology_api/app.py` | 44 | `create_app` mit 120 Zeilen bündelt Middleware-Verdrahtung, Router-Registrierung und Abhängigkeitsaufbau | mittel | GEMESSEN |
| CQ-003 | Große Datei / Struktur | `apps/web/src/App.tsx` | 332 | 641 Zeilen mit drei längeren Seitenkomponenten (`ProfilePage` 129, `HomePage` 87, `SettingsPage` 77) außerhalb der Feature-Slice-Struktur | niedrig | GEMESSEN |

Die übrigen langen Funktionen liegen im Rechenkern (`calculate_cycles_v2` 118 Zeilen, `_name_numbers` 102, `calculate_cycles` 94) und sind durch die zusammenhängende Fachlogik weitgehend gerechtfertigt — eine Zerlegung würde dort die Nachvollziehbarkeit der Berechnungsschritte eher verschlechtern.

### 2.3 Namensgebung & Stil

Die Namenskonventionen sind konsistent und über Werkzeuge abgesichert: `ruff` mit aktivierter `RUF`-Regelgruppe und `isort`-Konfiguration, `mypy` im Strict-Modus mit `pydantic`-Plugin (`pyproject.toml:71-128`). Die Paketbenennung folgt durchgehend dem Präfix `numerology_*`, die Frontend-Struktur dem Feature-Slice-Schema. Auffällig positiv: Schema- und Methodenversionen sind als benannte Konstanten geführt (`PYTHAGOREAN_V1_VERSION`, `PYTHAGOREAN_V2_VERSION` in `src/numerology_domain/_models/input.py:31`) statt als verstreute Zeichenketten-Literale — dass die API diese Konstanten trotzdem nicht auswertet, ist ein Anbindungs-, kein Stilproblem.

Ein Stolperstein für Lesende: Die Bezeichnung „V2" trägt im Projekt **zwei unabhängige Bedeutungen** — die Berechnungsmethode (`pythagorean-v2`) und die Schemaversion (`profile-calculation-result v2`, im Frontend als `LegacyV2ProfileCalculationResult`). Beide Achsen sind technisch sauber getrennt, aber die gleichlautende Benennung lädt zu Verwechslungen ein.

### 2.4 Bewertung

**Score**: 88/100 – Gut · Leitmetrik: GEMESSEN

`ruff` und `mypy strict` sind scharf konfiguriert, die Struktur ist konsistent, und die auf den ersten Blick hohen Werte bei großen Dateien lösen sich bei Betrachtung als generierte Artefakte weitgehend auf. Abzug: CQ-001 (mittel), CQ-002 (mittel), CQ-003 (niedrig).

---

## 💸 3. Technische Schulden

### 3.1 Veraltete Abhängigkeiten

| Abhängigkeit | Aktuell | Neueste | Rückstand | Priorität | Evidenz |
|---|---|---|---|---|---|
| redis | 7.4.1 | 8.1.0 | Major — **außerhalb** der Deklaration `>=5,<8` | hoch | GEMESSEN |
| fastapi | 0.140.0 | 0.141.1 | Minor — im Bereich | mittel | GEMESSEN |
| uvicorn[standard] | 0.51.0 | 0.52.1 | Minor — im Bereich | niedrig | GEMESSEN |
| typer | 0.27.0 | 0.27.1 | Patch — im Bereich | niedrig | GEMESSEN |
| mypy (dev) | 1.20.2 | 2.3.0 | Major — **außerhalb** `>=1.11,<2.0` | mittel | GEMESSEN |
| pytest-cov (dev) | 6.3.0 | 7.1.0 | Major — **außerhalb** `>=5.0,<7.0` | niedrig | GEMESSEN |
| ruff (dev) | 0.12.12 | 0.16.1 | Minor — **außerhalb** `>=0.6,<0.13` | niedrig | GEMESSEN |
| hypothesis (dev) | 6.161.5 | 6.165.0 | Patch — im Bereich | niedrig | GEMESSEN |
| typescript | 5.9.3 | 7.0.2 | **Zwei Hauptversionen** | mittel | GEMESSEN |
| jsdom | 29.1.1 | 30.0.1 | Major | niedrig | GEMESSEN |
| vite | 8.1.5 | 8.2.0 | Minor | niedrig | GEMESSEN |
| react-hook-form | 7.83.0 | 7.84.0 | Minor | niedrig | GEMESSEN |
| globals | 17.7.0 | 17.9.0 | Minor | niedrig | GEMESSEN |
| react-router-dom | 7.18.1 | 7.18.2 | Patch — schließt SEC-001 **nicht** | hoch | GEMESSEN |
| @playwright/test, @types/node, @types/react, @types/react-dom, @vitejs/plugin-react | — | — | Patch | niedrig | GEMESSEN |

**Kategorisierung nach der geforderten Dreiteilung.** Kategorie 1 (direkte Abhängigkeit veraltet, im deklarierten Bereich aktualisierbar): `fastapi`, `uvicorn`, `typer`, `hypothesis` sowie die Web-Pakete mit Patch- und Minor-Rückstand. Kategorie 2 (nur transitiv veraltet): `react-router` — nicht direkt deklariert, sondern über `react-router-dom` eingebunden, siehe SEC-001. Kategorie 3 (neue Version außerhalb des zulässigen Versionsbereichs): `redis`, `mypy`, `pytest-cov`, `ruff` — hier genügt kein Lockfile-Update, die Obergrenze in `pyproject.toml` muss bewusst angehoben werden.

**Einschränkung der Web-Messung:** `node_modules` war zum Messzeitpunkt nicht installiert, `pnpm` meldet daher `current=null`. Gemessen wurde die **deklarierte** gegen die **neueste** Version. Da alle Web-Abhängigkeiten in `apps/web/package.json` exakt gepinnt sind (keine `^`- oder `~`-Bereiche), entspricht die deklarierte der installierten Version — die Aussage bleibt belastbar, ist aber formal eine Deklarations- und keine Installationsmessung. Von 31 gelisteten Paketen liegen 11 tatsächlich hinter der neuesten Version; die übrigen 20 sind aktuell und erscheinen nur wegen des fehlenden `current`-Werts in der Liste.

### 3.2 TODO / FIXME / HACK / XXX

| Typ | Datei | Zeile | Text |
|---|---|---|---|
| TODO | `ROADMAP.md` | 730 | Planungsprosa („TODO-Check in Phase 11") — kein Code-TODO |
| TODO | `docs/audit/project-diagnosis-reconciliation-2026-08-02.md` | 84 | Zitat des obigen Eintrags in einem Audit-Dokument |
| TODO | `docs/audit/project-diagnosis-reconciliation-2026-08-02.md` | 89 | Zitat im selben Dokument |

**Kein einziges TODO, FIXME, HACK oder XXX im Quellcode.** Alle drei Treffer liegen in Planungs- beziehungsweise Auditdokumenten und beziehen sich auf denselben ROADMAP-Eintrag. Das ist ein bemerkenswert sauberer Befund für ein Projekt dieser Größe und deckt sich mit der Beobachtung, dass `ruff` mit aktivierter Regelgruppe ohne Fund durchläuft.

### 3.3 Hotspots

| Datei | Commits (12 Monate) | Evidenz |
|---|---|---|
| `README.md` | 12 | GEMESSEN |
| `.github/workflows/ci.yml` | 9 | GEMESSEN |
| `pyproject.toml` | 8 | GEMESSEN |

Die Hotspots liegen ausschließlich in Dokumentation, CI-Konfiguration und Manifest — **kein einziges Logikmodul** überschreitet die Hotspot-Schwelle von 8 Änderungen. Das ist ein Stabilitätsindiz für den Kern: Die Änderungslast trägt die Peripherie. Bei 36 Commits insgesamt und einem Revert (`2a60fe75`, ein zurückgenommener Branch-Protection-Test) ist die Historie zudem noch jung und arm an Korrekturschleifen.

### 3.4 Refactoring-Aufwand

| Befund | Aufwand | Kategorie |
|---|---|---|
| TS-001 — V2-Rechenkern produktiv anbinden | sehr_hoch | Architektur / Vertragsanbindung |
| TS-002 — Python-Laufzeitabhängigkeiten aktualisieren (inkl. `redis`-Grenze) | mittel | Abhängigkeitspflege |
| TS-003 — Web-Abhängigkeiten aktualisieren (inkl. TypeScript-Major) | mittel | Abhängigkeitspflege |
| TS-004 — Entwicklungswerkzeuge entfrieren (`mypy`, `pytest-cov`, `ruff`) | mittel | Werkzeugkette |
| ARCH-001 — Versions-Guard am Profilendpunkt | gering | API-Vertrag |
| ARCH-002 — Versionsbewusste Profil-Kanonisierung | mittel | API-Vertrag |
| ARCH-003 — CLI-Methodenoption | gering | CLI |
| CQ-001 — Exportliste entdoppeln | gering | Codequalität |
| CQ-002 — `create_app` zerlegen | mittel | Codequalität |
| CQ-003 — Seitenkomponenten aus `App.tsx` lösen | mittel | Frontend-Struktur |
| SEC-001 — `react-router` auf 8.x heben | hoch | Sicherheit |
| TEST-001 — Wheel-Test in der Pipeline scharf schalten | gering | Testinfrastruktur |
| DOC-001 — Web-Kernmodule kommentieren | mittel | Dokumentation |
| PERF-001 — Verschachtelung im Diagnoseskript reduzieren | gering | Wartbarkeit |

Aufwandsklassen: `gering` < 1 PT · `mittel` 1–3 PT · `hoch` 3–10 PT · `sehr_hoch` > 10 PT.

### 3.5 Bewertung

**Score**: 66/100 – Befriedigend · Leitmetrik: GEMESSEN

Der Bereich trägt den schwersten Einzelbefund des gesamten Laufs. TS-001 beschreibt eine Schuld besonderer Art: Es fehlt nichts, was gebaut werden müsste — es fehlt die Verbindung zwischen Gebautem und Produktivsystem. Der V2-Vertrag ist zu 100 % testabgedeckt, golden-verifiziert und in `docs/methods/reference-profile-derivations-v2.md` spezifiziert; er ist schlicht nicht erreichbar. Solcher Code altert, ohne Nutzen zu stiften, und muss bei jeder Änderung mitgepflegt werden. Abzug: TS-001 (kritisch, −25), TS-002 (mittel, −5), TS-003 (mittel als Wiederholung desselben Typs, −2), TS-004 (niedrig, −2).

**Bewusste Abweichung vom Standardverfahren:** Die V2-Isolation trägt ihren Score-Abzug **ausschließlich hier**. Architektur, Tests und Dokumentation referenzieren TS-001, ziehen dafür aber nichts ab — andernfalls würde derselbe Root Cause vierfach bestraft. ARCH-001 und ARCH-002 sind davon unabhängig bewertet, weil sie eigenständige Schäden beschreiben: die stille Fehletikettierung einer angeforderten Version und eine versionsblinde Integritätsprüfung. Beide bestünden auch dann fort, wenn V2 nie angebunden würde.

---

## 🔒 4. Sicherheit

### 4.1 Abhängigkeits-Schwachstellen

Auditor Python: `uv run --locked pip-audit -f json` · Status: **OK** (Exit 0 — keine bekannten Schwachstellen bei 64 geprüften Paketen)
Auditor Web: `pnpm audit --json` · Status: **OK** (Exit 1 — Funde vorhanden; gültiges JSON, damit ein Messergebnis und kein Werkzeugfehler)

| Abhängigkeit | Version | CVE / Advisory | Schwere | Evidenz |
|---|---|---|---|---|
| react-router (transitiv über react-router-dom) | 7.18.1 | Advisory 1124282 — CWE-352, „RSC Mode CSRF Bypass Allows Action Execution Before 400 Response"; verwundbar `>=7.12.0 <8.3.0`, behoben ab `8.3.0` | high | GEMESSEN |
| *(Python-Ökosystem)* | 64 Pakete | keine | — | GEMESSEN |

Verteilung laut `pnpm audit` bei 624 Abhängigkeiten: 1 × high, 0 × critical, 0 × moderate, 0 × low, 0 × info.

### 4.2 Unsichere Code-Muster

| # | Muster | Datei | Zeile | Risiko | Schwere | Evidenz |
|---|---|---|---|---|---|---|
| — | Nach vollständiger Einzelprüfung verbleibt kein bestätigtes unsicheres Muster | — | — | — | — | GEMESSEN |

Der Musterscan meldete acht als `kritisch` klassifizierte Treffer. Der Belegpflicht folgend wurde **jeder einzelne** im Quelltext gegengeprüft — keine Stichprobe, weil es sich um Geheimnis- und Hochrisikokategorien handelt. Alle acht sind Fehlalarme:

| Treffer | Fundstelle | Prüfergebnis |
|---|---|---|
| Dynamische Codeauswertung | `src/numerology_agent/rate_limit.py:22` und `:52` | Redis-`eval` (serverseitiges Lua), nicht Pythons `eval`. Das Skript ist das feste Literal `_CONSUME_SCRIPT` (Zeile 34–44), Schlüssel und Limits werden als `KEYS`/`ARGV` parametrisiert übergeben. Kein Injektionspfad im Python-Prozess. |
| Dynamische Codeauswertung | `tests/unit/test_rate_limit.py:22` | Test-Doppel derselben Redis-Schnittstelle. |
| Dynamische Codeauswertung | `docs/audit/project-diagnosis-reconciliation-2026-08-02.md:55` | Zitat des obigen Befunds in einem Auditdokument. |
| SQL per Zeichenkettenverkettung | `tests/unit/test_agent.py:195` | Kein SQL — die Zeile erzeugt einen Hash-Platzhalter (`"f" * 64`) für einen Manipulationstest. |
| SQL per Zeichenkettenverkettung | `tests/golden/test_hash_golden.py:73` | Kein SQL — f-String einer Assertion-Fehlermeldung, die das Wort „update" enthält. Das Projekt verwendet backendseitig überhaupt keine SQL-Datenbank (Redis und clientseitiges IndexedDB). |
| Geheimnis-Zuweisung an Literal | `.github/workflows/ci.yml:214` und `:215` | CI-Dummy-Werte für einen Staging-Smoke-Test. Die Bezeichner sind `DEEPSEEK_API_KEY` und `NUMRA_RATE_LIMIT_HMAC_SECRET`; die Werte sind selbstdokumentierende Platzhalter, die im Klartext als Nicht-Geheimnis ausgewiesen sind. Die Werte werden hier bewusst nicht wiedergegeben. |

### 4.3 Zugangsdaten

Werte werden grundsätzlich nicht ausgelesen. Gemeldet werden ausschließlich Fundort und
Bezeichnername.

| # | Fund | Datei | Zeile | Risiko |
|---|---|---|---|---|
| — | Keine Zugangsdaten-Dateien im Arbeitsbaum | — | — | — |

Die Existenzprüfung über `python scripts/ignore_regeln.py` findet **null** Dateien der Kategorien `.env*`, `*.pem`, `*.key`, `id_rsa`, `.npmrc`, `.netrc` und vergleichbar. Die beiden Bezeichner-Treffer in der CI-Konfiguration sind in 4.2 eingeordnet.

**Geltungsbereich dieser Aussage:** Der Musterscan untersucht den **aktuellen Arbeitsbaum**. Die Git-Historie wurde nicht auf früher committete und später entfernte Geheimnisse geprüft. Aus diesem Bericht folgt daher nicht, dass das Repository historisch frei von Zugangsdaten ist.

### 4.4 Bewertung

**Score**: 88/100 – Gut · Leitmetrik: GEMESSEN

Beide Ökosystem-Auditoren liefen erfolgreich durch. Positiv über die Auditwerte hinaus: Das Rate-Limiting arbeitet ausschließlich mit HMAC-pseudonymisierten Schlüsseln (`pseudonymous_key`, `src/numerology_agent/rate_limit.py:10-12`) statt mit Klartext-IP oder Geräte-ID; die Middleware-Kette ist vollständig und in definierter Reihenfolge verdrahtet (`src/numerology_api/app.py:64-86`) und umfasst Origin-Validierung, Body-Limit, CORS, Security-Header und Correlation-ID; die LLM-Endpunkte verifizieren eingereichte Profile gegen eine neu berechnete kanonische Version, bevor Kontingent verbraucht wird (`src/numerology_api/analysis_runtime.py:47-60`); ein CodeQL-Workflow ist aktiv. Abzug: SEC-001 (hoch).

**Einordnung zu SEC-001:** Das Advisory beschreibt einen CSRF-Bypass im **RSC-Modus** von React Router. Numra ist eine Vite-SPA ohne React Server Components, wodurch die praktische Ausnutzbarkeit fraglich erscheint. Diese Einordnung ist eine statische Bewertung anhand der Advisory-Beschreibung und der Projektstruktur — sie ersetzt keine Prüfung des Advisory-Details und rechtfertigt kein Aussitzen. Der verfügbare Patch 7.18.2 schließt die Lücke nicht; erforderlich ist der Sprung auf 8.3.0 oder höher, also ein Hauptversionswechsel mit eigenem Migrationsaufwand.

---

## 🧪 5. Tests & Qualitätssicherung

### 5.1 Testabdeckung

| Metrik | Wert | Evidenz | Quelle |
|---|---|---|---|
| Test-Framework | pytest 9.1.1 + hypothesis 6.161.5 (Backend), vitest 4.1.10 + Playwright 1.62.0 (Web) | GEMESSEN | `uv tree --frozen --outdated`, `pnpm outdated` |
| Testdateien | 56 | GEMESSEN | `python scripts/inventar.py` |
| Produktionsdateien | 87 | GEMESSEN | `python scripts/inventar.py` |
| Verhältnis Test/Prod | 0,64 (5.560 zu 7.568 Zeilen) | GEMESSEN | `python scripts/inventar.py` |
| **Coverage Gesamt (Lines)** | **93,44 %** | **GEMESSEN** | `uv run --locked pytest --cov=src --cov-fail-under=85` (Exit 0) |
| **Coverage Rechenkern** | **98,52 %** | **GEMESSEN** | `uv run --locked pytest --cov=src/numerology_engine --cov-fail-under=95` (Exit 0) |
| Coverage `profile_v2.py` | 100,00 % | GEMESSEN | Zeilenbericht desselben Laufs |
| Tests bestanden / übersprungen | 465 / 2 | GEMESSEN | `uv run --locked pytest` |
| Coverage Web | — | UNVERIFIZIERT | keine Freigabe zur Testausführung für das Web-Paket |
| Coverage-Gate in CI (Kern) | 95 % | BERICHTET | `.github/workflows/ci.yml:57` |
| Coverage-Gate in CI (gesamt) | 85 % | BERICHTET | `.github/workflows/ci.yml:60` |
| Coverage-Gate Web vorhanden | ja | BERICHTET | `apps/web/scripts/check-build.mjs:42` |

Beide Python-Gates sind erfüllt, und zwar mit Reserve: 93,44 % gegen ein Ziel von 85 %, 98,52 % gegen 95 %. Die CI-Schwellwerte sind hier ausdrücklich als `BERICHTET` geführt — sie belegen, was die Pipeline *verlangt*, nicht was der Code *erreicht*. Was er erreicht, steht in den beiden fett gesetzten Zeilen und stammt aus diesem Lauf.

Bemerkenswert ist die Testtiefe jenseits der reinen Prozentzahl: Golden-Korpora mit handverifizierten Referenzprofilen (`tests/golden/reference_profiles_v2.yaml`), Property-Tests auf Determinismus (`tests/property/test_v2_determinism.py`, `test_determinism_matrix.py`) und Hash-Vertragstests. Die Testsuite prüft nicht nur, ob Code läuft, sondern ob er *dieselben* Ergebnisse liefert — das passt zum Determinismus-Anspruch des Projekts.

### 5.2 Module ohne Testabdeckung

| # | Modul / Funktion | Datei | Risiko |
|---|---|---|---|
| 1 | `numerology_knowledge/models.py` — 81,05 % Zeilenabdeckung, ungedeckt: 50–53, 160–163, 186 | `src/numerology_knowledge/models.py` | mittel — betroffen ist die Auflösung von Wissenseinträgen, deren Fehlverhalten sich in Interpretationstexten niederschlägt |
| 2 | `numerology_interpretation/service.py` — 88,73 %, ungedeckt: 42, 52–54, 97 | `src/numerology_interpretation/service.py` | mittel — Kompositionslogik der Interpretation |
| 3 | `numerology_engine/reduction.py` — 91,49 %, ungedeckt: 69, 103 | `src/numerology_engine/reduction.py` | gering — im Rechenkern, aber eng umgrenzte Restpfade |
| 4 | `numerology_safety/runtime_gate.py` — 91,67 %, ungedeckt: 63→65, 66, 68, 132 | `src/numerology_safety/runtime_gate.py` | mittel — Sicherheitsgate, ungedeckte Zweige betreffen Ablehnungspfade |
| 5 | **Gesamtes Web-Paket** | `apps/web/src/` | unbestimmt — Coverage `UNVERIFIZIERT`, siehe 5.4 |

Kein Modul ist gänzlich ungetestet; die Lücken sind Restzweige. Der einzige strukturell blinde Fleck ist das Web-Paket, und zwar aus Messgründen, nicht aus Projektgründen — ein Coverage-Gate ist dort vorhanden (`check-build.mjs:42`).

### 5.3 CI/CD-Pipeline

| Schritt | Vorhanden | Fundstelle |
|---|---|---|
| Linting | ja (ruff, eslint `--max-warnings 0`) | `.github/workflows/ci.yml:14`, `:104` |
| Type-Check | ja (mypy strict, tsc) | `.github/workflows/ci.yml:14`, `:104` |
| Unit-Tests | ja (pytest, vitest) | `.github/workflows/ci.yml:14`, `:154` |
| Integration-Tests | ja (inkl. Container-Health-Smoke) | `.github/workflows/ci.yml:171` |
| Security-Scan | ja (CodeQL, `pip-audit`, `auditConfig` in `package.json`) | `.github/workflows/codeql.yml` |
| Build | ja (Wheel + sdist, Web-Build, gepinnte Images) | `.github/workflows/ci.yml:66`, `:81`, `:186` |
| Deploy | Rollback-Rehearsal vorhanden; kein automatischer Produktiv-Deploy | `deploy/`, Commit `aa3c2c8` |

Die Pipeline ist für ein Projekt dieser Größe ungewöhnlich vollständig — vier getrennte Jobs, inklusive Paket-Smoke mit Frischinstallation in einer leeren virtuellen Umgebung und Container-Health-Prüfung.

Genau in dieser Job-Trennung liegt allerdings TEST-001: `tests/integration/test_production_graph.py:221` überspringt sich selbst, wenn kein Wheel unter `dist/` liegt. Der Job *Quality Gates* (`ci.yml:14`), der pytest ausführt, baut kein Wheel; `uv build` läuft ausschließlich im separaten Job *Package smoke* (`ci.yml:81`). Der Test, der prüft, ob Paketressourcen wie Prompt-Vorlagen und Wissensbundles im gebauten Wheel enthalten sind, läuft damit weder lokal noch in der Pipeline — und ein Skip zählt in der Ergebniszeile als Erfolg.

### 5.4 Bewertung

**Score**: 88/100 – Gut · Leitmetrik: GEMESSEN (Python) / UNVERIFIZIERT (Web)

**Rechenweg der gewichteten Teilbewertung.** Der Bereich umfasst zwei Stacks, von denen nur einer gemessen werden durfte. Statt den belegten Wert durch den unbelegten zu entwerten oder den unbelegten stillschweigend mitzubewerten, wird nach gemessenen Produktions-Codezeilen gewichtet:

| Größe | Wert | Herkunft |
|---|---|---|
| Produktions-LOC Python | 4.763 (62,94 %) | GEMESSEN, identische Zählweise wie `inventar.py` |
| Produktions-LOC Web | 2.805 (37,06 %) | GEMESSEN, identische Zählweise wie `inventar.py` |
| Summe | 7.568 | deckungsgleich mit `inventar.json` (`test_prod.produktionszeilen`) |
| Python-Teilscore | 95 | Coverage gemessen, beide Gates erfüllt, 465 Tests grün; Abzug TEST-001 (−5) |
| Web-Teilscore | 75 | gedeckelt, da Coverage `UNVERIFIZIERT` |
| **Ergebnis** | 0,6294 × 95 + 0,3706 × 75 = **87,6 → 88** | |

Diese Aufteilung ist eine ausdrücklich benannte Abweichung vom Standardverfahren der Score-Rubrik. Ohne sie stünde hier entweder eine unzulässig hohe Zahl (die Python-Messung auf den ganzen Bereich übertragen) oder eine unfair niedrige (der gesamte Bereich auf 75 gedeckelt, obwohl 63 % des Produktionscodes belegt gemessen wurden).

---

## 📚 6. Dokumentation

### 6.1 README

| Kriterium | Status | Anmerkung |
|---|---|---|
| Existiert | ✅ | `README.md`, 27 Abschnitte |
| Projektbeschreibung | ✅ | „Was dieses Projekt ist" (Zeile 72) und ausdrücklich „Was dieses Projekt NICHT ist" (Zeile 88) — die Negativabgrenzung ist selten und hier fachlich geboten |
| Setup-Anleitung | ✅ | „Quick Start" (Zeile 156) inklusive PWA/API-Start und Container-Smoke |
| Nutzungsbeispiele | ✅ | „Beispiel-Output" (Zeile 205), CLI-Aufruf mit Pflichtparameter `--as-of-date` |
| API-Referenz | ⚠️ teilweise | Kein eigener README-Abschnitt; die API ist über die exportierte OpenAPI-Spezifikation (`openapi/numra-v1.json`) und `/api/docs` dokumentiert |
| Contributing-Guide | ✅ | `CONTRIBUTING.md` vorhanden, aus README verlinkt (Zeile 360) |
| Lizenz | ✅ | `LICENSE` vorhanden, README-Abschnitt Zeile 354 |

Zusätzlich enthält die README einen Statusabschnitt mit ausdrücklicher Launch-Sperre und einen Abschnitt „Wissenschaftliche Ehrlichkeit" (Zeile 369) — für ein Projekt in diesem Themenfeld eine relevante und ungewöhnlich transparente Selbsteinordnung.

### 6.2 API-Dokumentation

Die API ist über einen reproduzierbaren OpenAPI-Export dokumentiert (`scripts/export_openapi.py` mit `--check`-Modus, Ergebnis unter `openapi/numra-v1.json`, 1.775 Zeilen). Der Frontend-Client wird daraus generiert (`pnpm web:generate-api`), womit Vertrag und Konsument nicht auseinanderlaufen können. Ergänzend liegen JSON-Schemas je Ergebnisvertrag unter `src/numerology_api/schemas/` (v1, v2, v3). Das ist ein überdurchschnittlich sauberer Stand — die Dokumentation ist hier nicht beschreibend, sondern ausführbar geprüft.

### 6.3 Inline-Kommentare

| Metrik | Wert | Evidenz |
|---|---|---|
| Kommentarzeilen | 1.724 | GEMESSEN |
| Codezeilen | 34.321 | GEMESSEN |
| Kommentaranteil | 4,8 % | GEMESSEN |
| Unterdokumentierte Dateien (< 5 %) | 19 | GEMESSEN |

Ein hoher Kommentaranteil belegt keine Qualität. Stichprobenergebnis: Die geprüften Python-Kommentare sind aktuell und tragen Information, die der Code nicht selbst ausdrückt — etwa die Begründung der dynamischen Versionsermittlung in `src/numerology_cli/main.py:11-12` und `:29-34` (mit Datum und Anlass) sowie die Vertragsdokumentation im Kopf von `src/numerology_engine/profile_v2.py:1-15`, die die Methodenanforderung ausdrücklich benennt. Kein Fall veralteter oder irreführender Kommentierung gefunden. Die niedrige Quote ist damit kein Qualitäts-, sondern ein Verteilungsproblem: Sie konzentriert sich auf das Web-Paket.

### 6.4 Architektur-Dokumentation

16 ADRs unter `docs/adr/`, ergänzt um einen 1.247-zeiligen Master-Implementierungsvertrag (`docs/governance/master-implementation-contract.md`), Methodendokumentation (`docs/methods/`, darunter die Herleitung der V2-Referenzprofile), ein Auditverzeichnis mit nachvollziehbaren Gate- und Reconciliation-Dokumenten sowie Release-Notizen. Die Dokumentationslandschaft ist für die Projektgröße außergewöhnlich dicht und, wichtiger, **querverwiesen**: ADR-0015 verweist auf den zugehörigen Umsetzungsplan, der Reconciliation-Bericht auf die Gate-Dokumente, die README auf beides.

### 6.5 Bewertung

**Score**: 95/100 – Hervorragend · Leitmetrik: GEMESSEN

Die README deckt alle geprüften Kriterien bis auf eine eigenständige API-Referenz ab, die durch den geprüften OpenAPI-Export mehr als aufgewogen wird. 16 ADRs, Master-Vertrag, Methodendokumentation und ein gepflegtes Auditverzeichnis heben den Bereich deutlich über den Durchschnitt. Abzug: DOC-001 (mittel) — der Gesamt-Kommentaranteil liegt mit 4,8 % knapp unter dem Schwellwert, und elf Web-Produktionsdateien haben 0,0 %, darunter ausgerechnet die Module mit nicht offensichtlicher Logik: `storage/repository.ts` (451 Zeilen), `storage/crypto.ts` (lokale Verschlüsselung) und `features/report/ReportExperience.tsx`.

---

## ⚡ 7. Performance & Wartbarkeit

Die folgenden Befunde sind **statisch erkannte Muster**. Ihr Vorkommen im Code ist belegt,
ihre Laufzeitwirkung wurde nicht gemessen — diese Diagnose führt kein Profiling durch.

### 7.1 Leistungsrelevante Muster

| # | Muster | Datei | Zeile | Beschreibung | Schwere |
|---|---|---|---|---|---|
| PERF-001 | Verschachtelungstiefe 5 | `scripts/diagnose_determinism.py` | 39 | GEMESSEN: einziger Treffer oberhalb der Schwelle (Tiefe 4) im gesamten Repository. UNVERIFIZIERT: ob daraus eine Laufzeitwirkung folgt — es handelt sich um ein manuell aufgerufenes Diagnoseskript außerhalb des Produktionspfads. | niedrig |

Nicht gefunden wurden: N+1-Zugriffsmuster, synchrone I/O in asynchronem Kontext, fehlende Paginierung an Listenendpunkten, ineffiziente Datenstrukturen in Schleifen. Das bedeutet, dass die genannten Prüfungen nichts gefunden haben — nicht, dass es nichts zu finden gibt.

Die 45 gemeldeten Ausgabeanweisungen (`print`) liegen sämtlich in CLI-Werkzeugen unter `scripts/` (`diagnose_determinism.py` 23, `stress_determinism.py` 6, `validate_knowledge.py` 6, `generate_examples.py` 4, `export_openapi.py` 3, `export_schemas.py` 3) sowie zwei `console.log` in `apps/web/scripts/check-build.mjs`. Dort ist Konsolenausgabe der Zweck des Programms; kein Befund.

### 7.2 Wartbarkeitsrisiken

| # | Risiko | Datei | Zeile | Beschreibung | Schwere |
|---|---|---|---|---|---|
| 1 | Doppelt gepflegte Exportliste | `src/numerology_domain/models.py` | 19 | Siehe CQ-001 — Vertragsänderungen müssen an zwei Stellen nachgezogen werden; ein Vergessen fällt erst zur Laufzeit auf | mittel |
| 2 | Stets übersprungener Wheel-Test | `tests/integration/test_production_graph.py` | 221 | Siehe TEST-001 — Paketressourcen werden faktisch nie gegen das gebaute Wheel geprüft, der Skip erscheint als Erfolg | mittel |
| 3 | Eingefrorene Werkzeugkette | `pyproject.toml` | 27 | Siehe TS-004 — `mypy`, `pytest-cov` und `ruff` sind durch Obergrenzen von ihren aktuellen Hauptversionen abgeschnitten | niedrig |

Positiv zur Wartbarkeit: Fehlerbehandlung erfolgt an den Systemgrenzen (Origin-Validierung, Body-Limit, Problem-Details-Antworten), eine Logging-Strategie ist mit `AccessLogMiddleware` und `CorrelationIdMiddleware` vorhanden, und die Korrelations-ID zieht sich durch die Antwortkette.

### 7.3 Bewertung

**Score**: 75/100 – Gut · Leitmetrik: UNVERIFIZIERT

Der statische Musterscan ist gelaufen und liefert ein sehr sauberes Bild: genau ein Treffer oberhalb der Schwellen, und der liegt in einem Hilfsskript. Der Bereich ist dennoch auf 75 gedeckelt, weil die Leitmetrik für eine Performance-Aussage eine **Laufzeitmessung** ist. Es wurde kein Benchmark ausgeführt, und im Repository existieren keine Profiling-Artefakte (kein `profiling/`-Verzeichnis, keine `*.prof`-Dateien, keine Lighthouse-Berichte). Vorkommen sind gemessen, Laufzeitwirkung ist es nicht — ein höherer Score wäre nicht belegbar, sondern nur plausibel. Abzug über den Deckel hinaus: PERF-001 (niedrig).

Ein Performance-Budget existiert immerhin für den Web-Build (JavaScript-Budget in `apps/web/scripts/check-build.mjs`), es ist aber ein Größen-, kein Laufzeitbudget.

---

## 📊 8. GAP-Analyse

### 8.1 Ist gegen Soll

| Bereich | Ist-Zustand | Soll-Zustand | Lücke | Belegt durch |
|---|---|---|---|---|
| Berechnungsmethode | Produktivsystem rechnet ausschließlich `pythagorean-v1` | `pythagorean-v2` als erreichbarer Vertrag (implementiert, golden-verifiziert, dokumentiert) | Vollständige Anbindung fehlt: API, CLI, Analyse-Runtime, Frontend | TS-001, `src/numerology_engine/profile_v2.py:505`, Runtime-Smoke |
| API-Versionsvertrag | `policy.version="v2"` → HTTP 200 mit V1-Ergebnis | Unbekannte oder nicht unterstützte Methodenversion → 422 | Guard fehlt vollständig | ARCH-001, `src/numerology_api/routes/profiles.py:26` |
| Profil-Integritätsprüfung | Kanonisierung fest auf V1 | Versionsbewusste Kanonisierung | V2-Profile könnten die Prüfung strukturell nie bestehen | ARCH-002, `src/numerology_api/analysis_runtime.py:55` |
| CLI-Funktionsumfang | Nur V1 aufrufbar | Methodenversion wählbar | Option fehlt | ARCH-003, `src/numerology_cli/main.py:98` |
| Web-Testabdeckung | ungemessen in diesem Lauf; Gate in CI vorhanden | gemessene Abdeckung mit Schwellwert | Messlücke (keine Freigabe), kein Projektmangel | `apps/web/scripts/check-build.mjs:42` |
| Paketressourcen-Prüfung | Test überspringt sich in jedem Lauf | Prüfung läuft in der Pipeline | Wheel wird im pytest-Job nicht gebaut | TEST-001, `.github/workflows/ci.yml:14` gegen `:81` |
| Abhängigkeitsaktualität | 4 Python-Laufzeit-, 4 Dev- und 11 Web-Pakete veraltet; 4 davon außerhalb der deklarierten Grenzen | aktuelle Stände innerhalb gepflegter Grenzen | Versionsobergrenzen für `redis`, `mypy`, `pytest-cov`, `ruff` blockieren | TS-002, TS-004, `pyproject.toml:21,27,29,30` |
| Sicherheitslage Web | 1 × `high` (CWE-352), Fix erst ab Hauptversion 8 | keine offenen Advisories | Hauptversionssprung `react-router` erforderlich | SEC-001, `pnpm audit --json` |
| Performance-Nachweis | keine Laufzeitmessung, keine Profiling-Artefakte | belastbare Laufzeit-/Lastaussage | Messlücke | Anhang A, Zeile „Laufzeit-Benchmark" |
| Dokumentation Web-Kernmodule | 11 Produktionsdateien mit 0,0 % Kommentaranteil | Erklärung nicht offensichtlicher Logik | Verschlüsselung, Migration und Persistenz sind unkommentiert | DOC-001, `apps/web/src/storage/repository.ts` |

### 8.2 Erläuterung

Die Lücken dieses Projekts sind fast durchweg **Anbindungs- und Nachweislücken, keine Substanzlücken.** Das ist ein ungewöhnliches und in dieser Form günstiges Profil: Was gebaut wurde, ist mit hoher Disziplin gebaut — messbar an null Zyklen, null Code-TODOs, 98,52 % Kernabdeckung und einer vollständigen CI-Kette. Was fehlt, ist die letzte Meile zwischen Gebautem und Nutzbarem.

Der dominante Fall ist `pythagorean-v2`. Der Vertrag hält, was seine Dokumentation verspricht — der Laufzeittest reproduziert für den Referenzfall die primäre `40/4` (nicht als Meisterzahl markiert) neben der sekundären `22/4` mit gehaltenem Meisterwert 22, exakt wie im Golden-Korpus hinterlegt. Diese fachliche Eigenschaft, gehaltene Meisterzahlen sichtbar zu halten statt sie auf eine bedeutungslose Wurzel abzuflachen, ist der eigentliche Zweck des V2-Vertrags. Sie erreicht derzeit keinen Anwender.

Erschwerend ist die zweite Ordnung dieses Problems: Es fehlt nicht nur die Anbindung, es fehlt auch die *Ablehnung*. Ein Client, der `policy.version="v2"` anfordert, erhält keine Fehlermeldung, sondern ein plausibel aussehendes V1-Ergebnis mit V2-Etikett. Das verwandelt eine sichtbare Funktionslücke in einen unsichtbaren Datenfehler — und ist der Grund, warum ARCH-001 trotz geringen Behebungsaufwands als `hoch` eingestuft ist.

Ein struktureller Nebenbefund: TEST-001 und die Web-Coverage-Messlücke haben dieselbe Form wie das Hauptproblem. In allen drei Fällen existiert der Mechanismus (Wheel-Test, Coverage-Gate, V2-Rechenkern), aber der Pfad, auf dem er wirksam würde, ist nicht geschlossen. Wer TS-001 angeht, sollte TEST-001 mitnehmen — es ist derselbe Denkfehler in klein.

**Verhältnis zum vorliegenden Umsetzungsplan.** Für den größten Teil dieser Lücken existiert bereits ein detaillierter, unumgesetzter Plan (paralleler `/api/v2/*`-Stack, Wellen 0–5C). Der Plan ist zum Diagnosezeitpunkt **nicht begonnen**: Es existieren keine `*_v3.py`-Module, kein `/api/v2/`-Router, kein `de-v3.json`. Ein Plan senkt die technische Schuld nicht, er terminiert sie — die Bewertung in Abschnitt 3 ist deshalb unabhängig von seiner Existenz vorgenommen. Die Roadmap in Abschnitt 10 ordnet die Befunde jedoch seinen Wellen zu, statt eine konkurrierende Reihenfolge vorzuschlagen.

---

## 🎯 9. Priorisierte Handlungsempfehlungen

### 🔴 Kritisch — sofortiger Handlungsbedarf

| # | Empfehlung | Bereich | Aufwand | Nutzen | Befund-IDs |
|---|---|---|---|---|---|
| 1 | Versions-Guard am Profilendpunkt einziehen: `policy.version` prüfen und bei nicht unterstützter Version mit 422 ablehnen, statt still V1 zu rechnen | Architektur | gering | Beseitigt sofort eine unsichtbare Fehletikettierung; wirkt unabhängig davon, wann V2 angebunden wird | ARCH-001 |
| 2 | Entscheidung herbeiführen und dokumentieren, ob `pythagorean-v2` produktiv angebunden oder bewusst stillgelegt wird | Technische Schulden | gering (Entscheidung) | Beendet den Schwebezustand; jede Weiterentwicklung des Rechenkerns hängt daran | TS-001 |

Empfehlung 1 steht bewusst vor Empfehlung 2: Sie kostet unter einem Personentag, ist unabhängig von der Anbindungsentscheidung und schließt die gefährlichste Eigenschaft des aktuellen Zustands — dass ein Fehler nicht als Fehler sichtbar wird.

### 🟠 Hoch — kurzfristig, unter 4 Wochen

| # | Empfehlung | Bereich | Aufwand | Nutzen | Befund-IDs |
|---|---|---|---|---|---|
| 3 | `react-router` auf ≥ 8.3.0 heben; Migrationsaufwand des Hauptversionssprungs einplanen. Der Patch 7.18.2 genügt nicht | Sicherheit | hoch | Schließt die einzige offene Schwachstelle mit Schweregrad `high` | SEC-001 |
| 4 | Wheel-Ressourcen-Test scharf schalten: `uv build` im pytest-Job ergänzen oder den Test in den Package-Smoke-Job verschieben | Tests | gering | Beendet einen Test, der als Erfolg zählt, ohne je zu laufen | TEST-001 |
| 5 | Versionsbewusste Profil-Kanonisierung in der Analyse-Runtime vorbereiten | Architektur | mittel | Voraussetzung für jede V2-Anbindung des LLM-Pfads | ARCH-002 |

### 🟡 Mittel — unter 3 Monaten

| # | Empfehlung | Bereich | Aufwand | Nutzen | Befund-IDs |
|---|---|---|---|---|---|
| 6 | Python-Laufzeitabhängigkeiten aktualisieren; für `redis` die Obergrenze `<8` bewusst anheben oder die Begrenzung begründen | Technische Schulden | mittel | Vermeidet wachsenden Migrationsstau | TS-002 |
| 7 | Werkzeugkette entfrieren: `mypy` auf 2.x, `pytest-cov` auf 7.x, `ruff` auf 0.16.x | Technische Schulden | mittel | Neue Prüfregeln werden nutzbar; der Sprung wird mit jeder Hauptversion teurer | TS-004 |
| 8 | TypeScript-Rückstand von zwei Hauptversionen adressieren | Technische Schulden | mittel | Verhindert, dass der Frontend-Stack den Anschluss verliert | TS-003 |
| 9 | Exportliste des Domain-Pakets entdoppeln | Codequalität | gering | Entfernt eine Fehlerquelle, die erst zur Laufzeit auffällt | CQ-001 |
| 10 | Kernmodule der Web-Persistenz kommentieren: Verschlüsselung, Migration, Repository | Dokumentation | mittel | Betrifft die Module mit der am wenigsten offensichtlichen Logik | DOC-001 |
| 11 | CLI um eine Methodenversions-Option ergänzen | Architektur | gering | Macht den V2-Vertrag ohne API-Änderung erprobbar | ARCH-003 |

### 🟢 Niedrig — langfristig

| # | Empfehlung | Bereich | Aufwand | Nutzen | Befund-IDs |
|---|---|---|---|---|---|
| 12 | `create_app` in Middleware-, Router- und Abhängigkeitsaufbau zerlegen | Codequalität | mittel | Bessere Testbarkeit der App-Zusammensetzung | CQ-002 |
| 13 | Seitenkomponenten aus `App.tsx` in Feature-Slices lösen | Codequalität | mittel | Stellt die sonst konsequente Frontend-Struktur wieder her | CQ-003 |
| 14 | Verschachtelung in `scripts/diagnose_determinism.py` reduzieren | Performance | gering | Lesbarkeit eines Diagnosewerkzeugs | PERF-001 |

### 🔬 Messlücken schließen

Maßnahmen, die keine Mängel beheben, sondern die Aussagekraft der nächsten Diagnose erhöhen.

| # | Ungemessene Leitmetrik | Notwendiges Kommando | Warum sie fehlt |
|---|---|---|---|
| M1 | Web-Testabdeckung | `pnpm --filter @numra/web exec vitest run --coverage` | Keine Freigabe zur Testausführung für das Web-Paket in diesem Lauf. Der Tests-Score ist deshalb für den Web-Anteil (37,06 % der Produktions-LOC) auf 75 gedeckelt. |
| M2 | Laufzeit-Performance | Profiling des API-Pfads (cProfile oder py-spy) plus Lighthouse-Lauf gegen den Web-Build | Kein Benchmark ausgeführt, keine Profiling-Artefakte im Repository. Der Bereich Performance ist deshalb auf 75 gedeckelt. |
| M3 | Installierter Web-Abhängigkeitsstand | `pnpm install --frozen-lockfile` vor `pnpm outdated` | `node_modules` war nicht installiert; gemessen wurde die deklarierte statt der installierten Version. Wegen exakter Pinnung bleibt die Aussage belastbar, ist aber formal schwächer. |
| M4 | Historische Geheimnisse | Verlaufsprüfung des Git-Repositories mit einem dafür gebauten Werkzeug | Der Musterscan untersucht ausschließlich den aktuellen Arbeitsbaum. |

---

## 🗺️ 10. Maßnahmen-Roadmap

Die Spalte **Plan-Zuordnung** verweist auf die Wellen des vorliegenden, noch nicht begonnenen Umsetzungsplans zum `pythagorean-v2`-Vertrag. Wo dort „außerhalb" steht, deckt der Plan den Befund nicht ab und die Maßnahme ist eigenständig einzuplanen.

### 🚀 Quick Wins — 1 bis 2 Wochen

| # | Maßnahme | Bereich | Aufwand | Erwarteter Effekt | Plan-Zuordnung |
|---|---|---|---|---|---|
| 1 | Versions-Guard am Profilendpunkt (422 statt stiller V1-Berechnung) | Architektur | gering | Unsichtbarer Datenfehler wird zu sichtbarem Vertragsfehler | Welle 1 |
| 2 | Wheel-Ressourcen-Test in der Pipeline scharf schalten | Tests | gering | Ein bislang wirkungsloser Test wird wirksam | außerhalb |
| 3 | Exportliste des Domain-Pakets entdoppeln | Codequalität | gering | Eine Fehlerquelle weniger bei jeder Vertragsänderung | außerhalb |
| 4 | CLI-Option für die Methodenversion | Architektur | gering | V2 wird ohne API-Änderung erprobbar | Welle 1 |
| 5 | Web-Coverage einmalig messen und als Baseline festhalten | Tests | gering | Schließt Messlücke M1, hebt den Deckel im Web-Anteil | außerhalb |

### 📅 Mittelfristig — 1 bis 3 Monate

| # | Maßnahme | Bereich | Aufwand | Erwarteter Effekt | Plan-Zuordnung |
|---|---|---|---|---|---|
| 6 | `react-router` auf ≥ 8.3.0 migrieren | Sicherheit | hoch | Einzige offene `high`-Schwachstelle geschlossen | außerhalb |
| 7 | Python-Laufzeitabhängigkeiten aktualisieren, `redis`-Obergrenze klären | Technische Schulden | mittel | Migrationsstau abgebaut | außerhalb |
| 8 | Werkzeugkette entfrieren (`mypy`, `pytest-cov`, `ruff`) | Technische Schulden | mittel | Neue Prüfregeln nutzbar | außerhalb |
| 9 | Versionsbewusste Profil-Kanonisierung | Architektur | mittel | Voraussetzung für den V2-Analysepfad | Welle 1 |
| 10 | Web-Kernmodule kommentieren (Verschlüsselung, Migration, Persistenz) | Dokumentation | mittel | Wartbarkeit der schwierigsten Frontend-Logik | Welle 4 (begleitend) |
| 11 | TypeScript-Hauptversionsrückstand adressieren | Technische Schulden | mittel | Frontend-Stack bleibt anschlussfähig | außerhalb |

### 🏗️ Langfristig — 3 bis 12 Monate

| # | Maßnahme | Bereich | Aufwand | Erwarteter Effekt | Plan-Zuordnung |
|---|---|---|---|---|---|
| 12 | `pythagorean-v2` produktiv anbinden — oder bewusst und dokumentiert stilllegen | Technische Schulden | sehr_hoch | Beendet den schwersten Befund dieses Berichts; macht gehaltene Meisterzahlen für Anwender sichtbar | Wellen 0–5C (Kern des Plans) |
| 13 | Laufzeit-Profiling und Lighthouse-Baseline etablieren | Performance | mittel | Schließt Messlücke M2, hebt den Performance-Deckel | außerhalb |
| 14 | `create_app` zerlegen, Seitenkomponenten aus `App.tsx` lösen | Codequalität | mittel | Testbarkeit und Strukturkonsistenz | Welle 4 (teilweise) |

---

## 📎 Anhang

### A. Messprotokoll

Jedes Kommando dieses Laufs. Alles, was hier nicht mit `OK` steht, konnte nicht gemessen
werden und erscheint im Bericht als `BERICHTET` oder `UNVERIFIZIERT`.

| Kommando | Zweck | Status | Grund |
|---|---|---|---|
| `uv --version` | Werkzeugnachweis Paketmanager (0.11.32) | OK | — |
| `uv lock --check` | Lockfile-Integrität vor allen Läufen sicherstellen (kein stilles Update) | OK | — |
| `uv run --locked python --version` | Interpreter-Nachweis: CPython 3.12.11, **nicht** die System-Installation 3.10.0 | OK | — |
| `git rev-parse HEAD` | Commit-Stand des Laufs (`6b4d71ab`) | OK | — |
| `git status --porcelain=v1 --untracked-files=all` | Working-Tree-Status | OK | — |
| `python scripts/inventar.py <P>` | Strukturmetriken, LOC, Duplikate, Zyklen, God-Module | OK | — |
| `python scripts/git_metriken.py <P>` | Hotspots, Commits, Reverts, Working-Tree | OK | — |
| `python scripts/muster_scan.py <P>` | TODO/FIXME, unsichere Muster, Geheimnis-Indikatoren | OK | — |
| `python scripts/ignore_regeln.py <P>` | Existenzprüfung Geheimnisdateien (Inhalt wird nie gelesen) | OK | — |
| `uv run --locked python <scratchpad>/smoke_v2.py` | Runtime-Smoke: erreicht ein Produktionsendpunkt den V2-Rechenkern? | OK | — |
| `uv run --locked pip-audit -f json` | CVE-Audit Python (Exit 0 = keine Funde) | OK | — |
| `pnpm audit --json` | CVE-Audit Web (Exit 1 = Funde vorhanden; gültiges JSON, also Messergebnis) | OK | — |
| `uv tree --frozen --outdated --depth 1` | Aktualität der Python-Abhängigkeiten | OK | — |
| `pnpm outdated --recursive --format json` | Aktualität der Web-Abhängigkeiten (Exit 1 = veraltete Pakete vorhanden) | OK | — |
| `uv run --locked pytest --cov=src --cov-fail-under=85 …` | Gesamt-Coverage; Artefakte vollständig ins Scratchpad umgeleitet | OK | — |
| `uv run --locked pytest --cov=src/numerology_engine --cov-fail-under=95 …` | Core-Coverage-Gate des Rechenkerns | OK | — |
| `uv run --locked python <scratchpad>/prod_loc_split.py` | Produktions-LOC je Stack für die gewichtete Tests-Bewertung | OK | — |
| `pnpm --filter @numra/web exec vitest run --coverage` | Web-Coverage | UEBERSPRUNGEN | keine Freigabe zur Testausführung für das Web-Paket |
| Laufzeit-Benchmark / Profiling (cProfile, Lighthouse) | Performance-Leitmetrik | UEBERSPRUNGEN | kein Benchmark-Werkzeug und keine Profiling-Artefakte im Repository; nicht Teil des freigegebenen Umfangs |

**Artefakt-Isolation.** Sämtliche Mess-, Coverage-, Cache- und Auditartefakte wurden in ein Scratchpad-Verzeichnis außerhalb des Repositoriums geschrieben (`COVERAGE_FILE`, `--cov-report=json:…`, `-o cache_dir=…`, alle JSON-Ausgaben). Alle Python-Aufrufe liefen mit `--locked`, damit kein Lauf das Lockfile verändert. Die von `uv` erzeugte virtuelle Umgebung `.venv/` ist durch `.gitignore` abgedeckt und erscheint nicht im Git-Status.

### B. Validierung

| Prüfung | Ergebnis |
|---|---|
| `validiere_befunde.py` (Befunde) | ✅ Exit 0 — 14 Befunde, 7 Bereiche geprüft |
| `validiere_befunde.py --bericht` | ✅ Exit 0 — siehe Abschlussmeldung |
| Warnungen | keine |
| `git status --porcelain` nach dem Lauf | nur unversionierte Dateien: `projektdiagnose-bericht.md` (dieser Bericht) und `.claude/plans/dapper-fluttering-kazoo.md` (Planungsartefakt des Laufs); keine Änderung an versionierten Dateien, kein `uv.lock`-Diff |

### C. Methodik und Grenzen

Statische Analyse des Repositoriums: Struktur- und Zeilenmetriken, Musterscan,
Abhängigkeits- und Konfigurationsanalyse, Git-Historie. Ergänzt um zwei Laufzeitelemente:
die freigegebene Ausführung der Python-Testsuite mit Coverage und einen In-Process-Smoke-Test
der FastAPI-Anwendung zur Klärung der Frage, welche Berechnungsmethode ein Produktionsendpunkt
tatsächlich ausführt.

Nicht durchgeführt: Laufzeit- und Lastanalyse, Profiling, Penetrationstests, Prüfung der
fachlichen Richtigkeit numerologischer Aussagen, Bewertung von Geschäftslogik gegen Anforderungen,
Ausführung der Web-Testsuite, Prüfung der Git-Historie auf entfernte Geheimnisse. Sicherheitsaussagen
beschränken sich auf statisch erkennbare Muster und auf das, was der eingesetzte Auditor
meldet. Ein leerer Befundbereich bedeutet, dass die genannten Prüfungen nichts gefunden
haben — nicht, dass es nichts zu finden gibt.

Zur Erreichbarkeitsaussage in TS-001: Sie stützt sich auf sechs Stufen — Textreferenzen,
statischen Importgraphen, API- und CLI-Entry-Points, Agent-/Runtime-Aufrufgraph, einen
Laufzeittest gegen den Produktionsendpunkt und den Abgleich mit einem Golden-Fall. Die
zulässige Formulierung lautet daher „kein untersuchter Produktionspfad erreicht den
V2-Rechenkern" — nicht „er wird definitiv nie produktiv verwendet".

### D. Ausschlussregeln

Von der Analyse ausgenommen: `node_modules`, `.venv`, `__pycache__`, `.pytest_cache`,
`.mypy_cache`, `.ruff_cache`, `dist`, `build`, `.git`, `coverage`, `htmlcov`, `site-packages`,
`.worktrees` sowie Lockfiles (`uv.lock`, `pnpm-lock.yaml`, …), generierte Typdeklarationen
(`*.d.ts`), Minifikate, Binär-, Medien- und Archivdateien. Analysiert wurden 351 Dateien,
davon 293 mit erkannter Sprache.

Maßgeblich ist `scripts/ignore_regeln.py`. Zugangsdaten-Dateien werden ausschließlich über
ihre Existenz erfasst, ihr Inhalt wird nie gelesen.

### E. Glossar

| Begriff | Bedeutung |
|---|---|
| PT | Personentage (Aufwandsschätzung) |
| CVE | Common Vulnerabilities and Exposures — Kennung einer bekannten Schwachstelle |
| CWE | Common Weakness Enumeration — Klassifikation eines Schwachstellentyps |
| ADR | Architecture Decision Record |
| GAP | Lücke zwischen Ist- und Soll-Zustand |
| Hotspot | Datei mit überdurchschnittlich vielen Änderungen |
| God Module | Modul mit zu vielen eingehenden Abhängigkeiten |
| N+1 | Abfragemuster, das pro Ergebniszeile eine weitere Abfrage auslöst |
| Leitmetrik | Die Kennzahl, deren Evidenz über den Score-Deckel eines Bereichs entscheidet |
| RSC | React Server Components — Rendering-Modus, auf den sich SEC-001 bezieht |
| Golden-Case | Gepinnter Referenzfall mit handverifiziertem Erwartungswert |
