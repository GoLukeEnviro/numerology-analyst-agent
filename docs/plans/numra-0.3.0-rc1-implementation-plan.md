# Numra 0.3.0-rc.1 — Implementationsplan

> **Status:** Bindend für die Release-Sequenz
> **Quelle:** Freigegebener Implementationsplan v3 (Session-Artefakt)
> **Basis-SHA:** `8faba1b4442939a97252282c60b3f4f808d62235` (origin/main)
> **Ziel:** Lokale Release-Vollendung und DeepSeek-Aktivierung als
> `0.3.0rc1`, ohne vorzeitigen öffentlichen Launch.
> **Erstellt:** 28. Juli 2026

---

## Bindende Linie (niemals verletzen)

- **Determinismus vor LLM** — keine Berechnung durch ein Sprachmodell.
- **Sechs Aussageklassen trennen:** `input_fact`, `calculation_fact`,
  `traditional_claim`, `interpretive_hypothesis`, `empirical_evidence`,
  `practical_suggestion`.
- Keine erfundenen Daten. Keine Diagnosen. Keine nicht-versionierten
  Vertragsänderungen. Keine Placeholders. Keine Secrets in Git/Logs/Chat.
- **Quelle der Wahrheit = ausführbarer Code**, nicht Agentenberichte oder Audits.
- Lokal-first — VPS/Beta/Launch erst nach lokaler Abnahme.

---

## Welle 0 — Reality Check (PFLICHT, keine Mutation)

1. `git status --short` (muss clean), `git fetch origin --tags --prune`.
2. Verifiziere: `origin/main = 8faba1b4442939a97252282c60b3f4f808d62235`.
3. `git switch main && git pull --ff-only origin main` → `HEAD = 8faba1b`.
4. Komplett NEU inventarisieren (PR #11/#12 berücksichtigen — Hardening,
   CodeQL, zusätzliche Tests nicht neu planen).
5. Echte Test-/Coverage-Baselines aus Läufen ableiten.
6. `docs/audit/current-state-numra-rc.md` erstellen (16 Pflichtabschnitte).
7. Danach: jeder neue Branch basiert auf aktuellem `origin/main`.

**Bestätigte Baselines (28.07.2026):** 207 Python-Tests, 34 Vitest-Tests,
Engine-Coverage 97,12 %, Gesamt-Coverage 93,02 %, alle Drifts grün.

---

## PR-Sequenz (strikt, sequenziell mergen, keine parallelen Vertragsänderungen)

### PR A — `docs/release-governance-v0.3.0-rc1` (Welle 1)

- `docs/plans/numra-0.3.0-rc1-implementation-plan.md` (diese Datei).
- `docs/adr/0015-cumulative-release-normalization.md` (Zielversion 0.3.0rc1
  NUR dokumentiert).
- `docs/adr/0016-v2-user-owned-masterplan-boundary.md` (V2-Grenze/Spezifikation).
- `docs/product/numra-v2-guided-masterplan.md` (nur Spezifikation).
- `docs/audit/current-state-numra-rc.md`.
- `CLAUDE.md` (Projekt-Instruktion versionieren).
- README/ROADMAP-Hinweis auf RC-Vorbereitung.
- **KEIN Versions-Bump** (`pyproject.toml`/Web/OpenAPI/PWA unverändert).
- Verify: `export_openapi/schemas/examples --check` grün (kein Drift).

### PR B — `feat/deepseek-live-activation` (Welle 2)

- `DeepSeekSettings` erweitern: `thinking_enabled`, `reasoning_effort`,
  `max_output_tokens`, `max_retries` (`timeout_seconds` existiert bereits).
- `complete()` parametrisieren; `temperature`/`top_p` ENTFERNEN.
- Env-Umbau mit Fallback: `new=DEEPSEEK_*`, `fallback=NUMRA_DEEPSEEK_*` +
  Deprecation-Warning ohne Secret. `NUMRA_LLM_ENABLED`,
  `_RATE_LIMIT_HMAC_SECRET`, `_REDIS_URL`, `_ENVIRONMENT`,
  `_ALLOWED_ORIGINS`, `_MAX_REQUEST_BODY_BYTES` bleiben unter `NUMRA_`.
- Provenance: `thinking="enabled"`, `reasoning_effort="high"`,
  `effective_sampling="provider_managed"`, `temperature=None`, `top_p=None`.
- Provider-Retry NUR bei Netz/Timeout/429/502/503/504; fail-closed bei
  400/401/403/key/Modell. Clock/Sleeper/Jitter injizierbar.
- Circuit Breaker (neu: `src/numerology_agent/resilience.py`).
- Agent-Service: max. 1 kontrollierte Neugenerierung bei korrigierbarem
  JSON/Schema; FAIL-CLOSED bei erfundenen Zahlen/unbekannten IDs/Injection/PII/Diagnose.
- `reasoning_content`-Hygiene präzise testen (ProviderResult/Report/Export/
  IndexedDB/Logs/API-Antwort — weder Feld noch Wert). RC1: keine Tool-Calls,
  alle one-shot.
- NEUER VERTRAG `analysis-report-v2` + `analysis-follow-up-v2`,
  `prompt_version=numra-report-de-v2`. V1 bleibt lesbar; neue Erzeugung
  ausschließlich V2; Migration kontrolliert. `AnalysisClaim` um
  `uncertainty`/`counter_hypothesis`/`composer_rule_id` ergänzen.
- `prompts/**` (system/tasks/eval) aus Datei laden; 10 Systemprinzipien.
- `tests/integration/test_deepseek_live_smoke.py` opt-in
  (`NUMRA_RUN_LIVE_DEEPSEEK_TESTS`); ohne Key = SKIP; 10 Punkte bei Key.
- `compose.yaml`, `deploy/numra.env.example`, PowerShell-Smokes,
  `docs/operations/llm-provider.md` synchronisieren; `ReportExperience.tsx`
  Consent verifizieren.

### PR C — `content/knowledge-de-v2` (Welle 3)

- Knowledge V2: Compound-Struktur (`raw_value`/`reduced_value`/
  `compound_notation`/`classification`), KEIN `number:int` für Compounds.
- `KnowledgeEntry` V2 erweitern (`stable_id`, `method_system`, `claim_class`,
  `constructive`/`shadow_expression`, `development_theme`, `uncertainty`,
  `result_contexts`, `authoring_provenance`, …).
- Kontextsensitiver Resolver: `number:4` vs `compound:13/4` vs `master:22`
  vs `context:life_path`. Stable-ID z. B.
  `de.pythagorean.v2.compound.13-4.life_path`.
- `src/numerology_knowledge/data/de-v2.json` (V1 unverändert lesbar);
  Loader: V2 Default.
- Abdeckung: 0–9, 11/22/33, Compound (10/1, 12/3, 15/6, 17/8, 20/2, 21/3,
  23/5, 24/6, 25/7, 26/8, 27/9, 28/1, 29/11, 30/3, 31/4, 32/5, 34/7, 35/8,
  36/9, 37/1, 38/11, 39/3, 40/4, 44/8), Karmaschulden 13/4, 14/5, 16/7, 19/1;
  `result_contexts` aus 13 Dimensionen.
- `scripts/validate_knowledge.py` NEU (Required CI-Check).
- `InterpretationClaim` um `composer_rule_id`/`uncertainty`/
  `counter_hypothesis`; neues `rules.py` mit Reinforcement/Tension/
  Core-vs-Active/Inner-vs-Outer/LifePath-vs-Expression/Maturity/Cycle;
  Beziehung = nicht-wertende Resonanz/Spannung.

### PR D — `feat/rc1-ux-accessibility-closure` (Welle 4)

- `AbortController` in `client.ts`/`ReportExperience`/`AnalysisWizard` +
  Abbrechen-Button.
- Insight→Next-Step-Brücke (Dexie `notes`-Store, `reportId`-verknüpft;
  NICHT an DeepSeek).
- Server-Quota-Display statt irreführendem localStorage-Quota; 429
  benutzerfreundlich.
- Skip-to-Content-Link, `html lang="de"`, Kontrast-Review, PWA-Toast-Focus.
- `@tanstack/react-query` entfernen (nur nach Import-Prüfung).
- Frontend-Tests/Mocks an `analysis-report-v2` + `deepseek-v4-pro`
  migrieren.

### PR E — `release/v0.3.0-rc1` (Welle E) — EIGENTLICHER Versions-Bump

- Tatsächlicher Bump: `pyproject.toml` `0.3.0rc1`, `web/package.json`
  `0.3.0-rc.1`, OpenAPI `info.version`, API-Meta, PWA-Manifest
  `version`/`version_name`.
- Finales Regenerieren: `export_openapi`/`export_schemas`/`generate_examples`
  (`--check`-konform).
- `docs/releases/v0.3.0-rc.1.md` + `migration-to-v0.3.0-rc.1.md`.
- Vollständige lokale Gates grün (Python + Web + Container).
- **NOCH KEIN Tag, KEIN GitHub-Prerelease.** PR-E-CI grün → Squash-Merge.

---

## Staging-Gate (Welle 5 — RC-Tag-Gate, nicht optional)

PR E gemergt → finalen main-SHA (`$ReleaseSha = git rev-parse HEAD`)
erfassen → exakt diesen SHA auf privates Staging deployen
(`deploy/scripts/release.sh $ReleaseSha`) → echter DeepSeek-Live-Smoke +
Backup/Restore + Rollback + 17-Punkte-Abnahme → Runtime-Dateimarker-Gate
in Python ergänzen (`/etc/numra/numra-legal-approved`,
`/etc/numra/llm-transfer-approved` root:root:0600) → erneut sicherstellen:
`origin/main` unverändert → nur dann: `git tag -a v0.3.0-rc.1 $ReleaseSha`
+ GitHub-Prerelease mit Artefakten.

**KEIN Tag auf anderem Commit als dem geprüften Staging-Commit.**

---

## Nachgelagert (nur skizzieren, NICHT starten)

- **Welle 6:** Beta.
- **Welle 7:** MkDocs VOLLSTÄNDIG + eigene CI-Jobs + `docs/committee/`.
- → Tag `v0.3.0` stabil.
- **Welle 8:** Research 0.4.0.
- **Welle 9:** V2 Masterplan = späteres Implementierungsprogramm
  (Spezifikation liegt bereits in PR A / ADR 0016).

---

## Stopp-Kriterien — BLOCKED melden bei

- Working-Tree nicht clean.
- Welle-0-Start: `origin/main` nicht `8faba1b`.
- danach: Branch nicht auf aktuellem `origin/main`.
- rotem Required Check.
- unverversionierter Vertragsänderung.
- nicht herleitbaren Golden Cases.
- veränderten Calc-Facts durch DeepSeek.
- PII an DeepSeek.
- Key in Git/Logs.
- nicht-validierbarem JSON.
- Safety-Durchlass.
- Backup/Rollback-Fehler.
- fehlenden Rechtsangaben.
- existierendem Tag.
- main-SHA nach Staging-Abnahme verändert.

**KEIN Gate-Umgehen.**

---

## Berichtformat (je PR und final)

Base SHA / Head SHA / origin/main zum Branch-Zeitpunkt · umgesetzter Scope ·
nicht umgesetzter Scope · Vertragsänderungen · DeepSeek/Datenschutz ·
Tests + Coverage · lokale Gates · Remote-CI · nächste erlaubte Schritte.
Konkrete Ergebnisse, keine Aktivitätsberichte.
