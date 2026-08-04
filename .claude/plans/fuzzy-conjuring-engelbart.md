# Plan: CLAUDE.md aktualisieren (Numra)

## Context

`/init` wurde aufgerufen. Ein CLAUDE.md existiert bereits im Repo-Root und ist inhaltlich
umfangreich und größtenteils korrekt. Gemäß `/init`-Vorgabe ("wenn bereits vorhanden,
Verbesserungen vorschlagen") wurde die Datei NICHT neu geschrieben, sondern gegen den
aktuellen Repo-Zustand verifiziert (3 parallele Explore-Agents: Python-Kern, Web-App,
Governance-Dokumente). Ziel dieses Plans: gezielte, minimal-invasive Korrekturen und
Ergänzungen an der bestehenden CLAUDE.md — keine Neustrukturierung, keine Dopplung von
Inhalten, die bereits in `PROJECT_CHARTER.md`/`ROADMAP.md`/README.md stehen und dort
gepflegt werden sollten.

Prinzip **MINIMAL TOUCH**: nur Fakten korrigieren, die nachweislich veraltet/falsch sind,
und nur Architektur-Infos ergänzen, die für produktive Arbeit im Repo unmittelbar relevant
sind (nicht jede Datei auflisten).

## Verifizierte Befunde (Belege aus Repo-Exploration)

**Fehlerhaft/veraltet in aktueller CLAUDE.md:**
1. Dev-Server-Beschreibung: CLAUDE.md sagt "erwartet die FastAPI-API auf Port 8000 als
   CORS-Origin" — tatsächlich nutzt `apps/web/vite.config.ts` einen **Dev-Proxy**
   (`server.proxy["/api"] → http://127.0.0.1:8000`, ebenso `preview`), keine CORS-Origin.
2. Wissenspaket-Abschnitt nennt nur `de-v1.json` als das versionierte Paket — tatsächlich
   ist laut `src/numerology_knowledge/.../loader.py` (Default `version: str = "v2"`)
   **`de-v2.json` das kanonische/aktuelle Bundle**; v1 bleibt nur für Migration ladbar.

**Fehlend, aber architektur-relevant:**
3. Pytest-Marker: zusätzlich zu `golden, integration, property, unit` existiert auch
   `slow` (Determinismus-Matrix-Tests) in `pyproject.toml`.
4. Weitere Scripts existieren neben den drei genannten: `scripts/validate_knowledge.py`,
   `scripts/diagnose_determinism.py`, `scripts/stress_determinism.py`.
5. Es existiert bereits additiv ein **`profile-calculation-result-v4`**-Schema
   (`ProfileCalculationResultV4` in `numerology_domain`, `calculate_profile_v2()` in
   `src/numerology_engine/profile_v2.py`) — noch NICHT über API/CLI erreichbar, nur
   engine-intern. Wichtig, damit ein Agent nicht versehentlich v4 als produktiv behandelt
   oder v3/v4 vermischt (Charter §6: keine Methodenversionsmischung).
6. `pnpm web:coverage` (vitest run --coverage) fehlt in der Skript-Liste.
7. Playwright-Config-Pfad (`apps/web/playwright.config.ts`) und E2E-Tests-Ordner
   (`apps/web/e2e/`) sind nicht erwähnt.
8. Web-App-Struktur: Top-Level-Dateien `App.tsx`, `theme.ts`, `main.tsx`, `styles.css`
   sowie `test/` (Vitest-Setup) fehlen; wichtig zu wissen, dass es **keine** separaten
   `components/`, `hooks/`, `routes/`, `i18n/`-Verzeichnisse gibt (schlankere Struktur als
   die Feature-Slice-Beschreibung vermuten lässt).
9. Projektstatus/Sperren aus README.md: aktuell `v0.3.0-rc.1`, öffentlicher Launch
   gesperrt bis VPS/Domain/DNS/HTTPS/Rechtsfreigaben erfüllt sind
   (`docs/operations/launch-checklist.md`, `deploy/README.md`). `pyproject.toml`-Version
   (`0.1.5`) weicht bewusst vom funktionalen Stand (`v0.3.0-rc.1`, ADR 0015) ab — sonst
   potenzielle Verwechslungsquelle.
10. ROADMAP-Status: Phase 7 (`numerology_research`-Paket, in Charter §2 genannt) ist
    `NOT_STARTED` — Paket existiert noch nicht unter `src/`. Sollte als "geplant, nicht
    implementiert" vermerkt werden, damit kein Agent es fälschlich sucht oder anlegt.
11. `.github/agents/*.agent.md` definiert sechs rollenspezifische Vertragsagenten
    (`domain-architect`, `calculation-engineer`, `knowledge-editor`, `research-reviewer`,
    `safety-reviewer`, `release-engineer`) — relevant, falls im PR-Prozess auf diese
    Rollen Bezug genommen wird.

**Bewusst NICHT übernommen** (zu granular / gehört in andere Docs, nicht CLAUDE.md):
- Anti-Ziele-Liste, Committee-Gate-Details, PROJECT_CHARTER §6-Einzelpunkte (Y-Regel etc.)
  → bleiben Sache von `PROJECT_CHARTER.md`/`ROADMAP.md` als Source of Truth.
- CONTRIBUTING.md-Commit-Format-Nuance (`type(scope):` vs. `type:`) → CLAUDE.md-Format
  bleibt verbindlich für Agenten-Commits, kein Konflikt-Vermerk nötig.
- zweite OpenAPI-Datei (`numra-v1-pre-refactor.json`) → keine Handlungsrelevanz.

## Konkrete Änderungen an `CLAUDE.md`

1. **Python-Befehle-Block**: `slow`-Marker ergänzen; die drei zusätzlichen Scripts in
   einer Zeile nach dem bestehenden Export-Block ergänzen (validate_knowledge,
   diagnose_determinism, stress_determinism).
2. **Web/PWA-Befehle-Block**: `pnpm web:coverage` ergänzen; Playwright-Zeile um
   Config-Pfad und `e2e/`-Ordner erweitern.
3. **Dev-Server-Satz korrigieren**: von "CORS-Origin" auf "Vite-Dev-Proxy `/api` →
   `http://127.0.0.1:8000`" ändern.
4. **Web-App-Abschnitt** (`apps/web/src`): Zeile ergänzen zu Top-Level-Dateien
   (`App.tsx`, `main.tsx`, `theme.ts`, `styles.css`, `test/`) und Hinweis, dass es keine
   separaten components/hooks/routes/i18n-Verzeichnisse gibt.
5. **Determinismus-/Hash-Vertrag-Abschnitt**: Satz ergänzen zu `profile-calculation-result-v4`
   (engine-only, `calculate_profile_v2()`, noch nicht über API/CLI exponiert).
6. **Wissenspakete-Abschnitt**: `de-v1.json` → `de-v2.json` als aktuelles kanonisches
   Bundle korrigieren, v1 als Migrationspfad erwähnen.
7. **Golden-Cases-Erwähnung** (im Determinismus-Abschnitt): dritte Datei
   `tests/golden/reference_profiles_v2.yaml` ergänzen.
8. **Neuer kurzer Abschnitt "Projektstatus"** (nach Projektüberblick): Release-Stand
   `v0.3.0-rc.1`, Launch-Sperre + Verweis auf `docs/operations/launch-checklist.md`,
   Versions-Hinweis (`pyproject.toml` vs. funktionaler Stand), Hinweis dass
   `numerology_research` (Phase 7) noch nicht implementiert ist.
9. **Ergänzung zu Contributor-Rollen** (im bestehenden Abschnitt "Verbindliche
   Coding-Regeln" oder direkt danach): ein Satz zu `.github/agents/*.agent.md`
   Rollen-Kontrakten.

Alle Änderungen sind additive Ein-/Zwei-Satz-Ergänzungen oder Ein-Wort-Korrekturen an der
bestehenden Struktur — keine Abschnitte werden entfernt oder umsortiert.

## Verifikation

- Nach der Bearbeitung: Datei erneut lesen und gegen die obige Liste abgleichen
  (alle 9 Punkte umgesetzt, keine ungewollten Nebenänderungen).
- Stichprobenartig die zitierten Pfade/Namen nochmals gegen Repo prüfen (bereits durch
  die drei Explore-Agents mit Dateibelegen bestätigt).
