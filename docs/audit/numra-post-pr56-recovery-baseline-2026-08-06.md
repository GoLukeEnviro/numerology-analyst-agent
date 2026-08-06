# Numra — Post-PR56 Recovery Baseline

**Datum:** 2026-08-06
**Auftrag:** GOAL „Numra vollständig reparieren, lokal verifizieren und kontrolliert bis RC2/Stable führen"
**Branch:** `fix/post-pr56-recovery-and-full-verification`
**Status:** Baseline erfasst, Fehler noch nicht behoben (Phase 0 abgeschlossen)

---

## 1. Repository-Zustand

| Metrik | Wert |
| ------ | ---- |
| Base-SHA (HEAD / origin/main) | `ba4c9121866a8c05b1ccfea076e0c26db9c25758` |
| Erwarteter Main-Head (Auftrag) | `ba4c9121866a8c05b1ccfea076e0c26db9c25758` → **übereinstimmend** |
| Tag `v0.3.0-rc.1` (Tag-Objekt) | `cec214ec6c8a9b41f13a073d738ffea3734d9d60` |
| Tag `v0.3.0-rc.1` (Commit) | `21ba56ed0d918cea7c60090bcc50937adc16269a` → **entspricht Auftragserwartung** |
| Paketversion (pyproject.toml) | `0.3.0rc1` |
| Web-Version (apps/web/package.json) | `0.3.0-rc.1` |
| Working Tree | sauber (keine uncommitteten Änderungen) |
| Offene PRs | 0 (entspricht `OPEN_PRS_EXPECTED=0`) |
| Offene Issues | 10 (#37, #39, #40, #41, #43, #44, #45, #46, #47, #48) |

### Git-Referenzen

- `main` → `ba4c912` (chore: finale Bereinigung vor Merge)
- `origin/main` → `ba4c912`
- `fix/state-reconciliation` → `5d5c9c4` (lokaler Alt-Branch, unverändert)
- Tags: `v0.3.0-rc.1`, `v0.1.3`, `v0.1.2`, `v0.1.1`, `v0.1.0`

### Letzte Commits auf main (Auszug)

```
ba4c912 chore: finale Bereinigung vor Merge
800082a docs: Staging-Acceptance-Vorlage für Issue #39 (RC2-Blocker)
6f8ddcd chore: finaler Cleanup — Formatierung, Docs, alle Änderungen gebündelt
00e40b5 feat: Welle 5A — Provider-Evaluation (DeepSeek Thinking vs Non-Thinking)
06a7991 feat: Welle 4 — Web-Migration (Tab-UI, Storage v4, Offline, Print/PDF)
039ca9c feat: Welle 3 — Berichtserzeugung V3 (Provider, Service, Prompts, Routen)
2db4138 feat: Welle 2 — Fact Package V3, Knowledge V3, Interpretation V3
32a80a3 feat: Welle 1 — API-Grundlage für /api/v2 Stack
```

---

## 2. Toolchain

| Tool | Version |
| ---- | ------- |
| git | 2.55.0.windows.3 |
| python (System) | 3.10.0 (Projekt verlangt ≥3.12; uv verwaltet eigene Umgebung) |
| uv | 0.11.32 |
| node | v24.14.0 |
| pnpm | 10.22.0 |
| docker (Client) | 29.6.2 |
| docker (Server) | Docker Desktop 4.83.0, Engine 29.6.2, linux/amd64 |
| gh (GitHub CLI) | aktiv, Account `GoLukeEnviro`, Scopes: gist, read:org, repo, workflow |

---

## 3. GitHub-Zustand

### CI-Runs (letzte 30, Auszug)

| Workflow | Branch | Event | Conclusion | Run-ID |
| -------- | ------ | ----- | ---------- | ------ |
| CI | main | push | **failure** | 31074104096 |
| CodeQL | main | push | success | 31074104075 |
| CI | feat/v2-full-analysis-welle-0 | pull_request | **failure** | 31074103448 |
| CodeQL | feat/v2-full-analysis-welle-0 | pull_request | success | 31074103726 |

### Bekannte CI-Fehler (aus Run 31074104096, Logs)

1. **OpenAPI-Drift** (Job „Quality Gates", Step „Verify OpenAPI contract"):
   - Befehl: `uv run python scripts/export_openapi.py --check`
   - Fehler: `OpenAPI drift detected. Run: uv run python scripts/export_openapi.py`
   - Exitcode: 1
2. **Web-Type-Drift** (Job „Web quality", Step „Verify generated API types"):
   - Befehl: `pnpm web:generate-api` + `git diff --exit-code -- apps/web/src/api/schema.d.ts`
   - Fehler: Diff zeigt fehlende V2-Pfade `/api/v2/meta` und `/api/v2/profiles/calculate` sowie V2-Schemas (`MetaResponseV2`, `NameNumberSetV2`, `NumberModel`, `ProfileCalculationRequestV2`, `ProfileCalculationResultV4`)
   - **Auffällig:** Im generierten Diff erscheinen NUR `meta` und `profiles/calculate` — die Pfade `/api/v2/analyses/report` und `/api/v2/analyses/follow-up` fehlen im regenerierten Output (Hypothese H5: Router-Wiring unvollständig)
   - Exitcode: 1

### Offene Issues (relevant für diesen Auftrag)

| Issue | Titel | Status |
| ----- | ----- | ------ |
| #37 | [EPIC] Numra v0.3.0-rc.2 → Stable v0.3.0 | OPEN |
| #39 | Private staging environment and deployment evidence | OPEN |
| #40 | Backup restore and rollback rehearsal | OPEN |
| #41 | Provider and API end-to-end smoke | OPEN |
| #43 | Accessibility and cross-device beta matrix | OPEN |
| #44 | Committee release review | OPEN |
| #45 | Prepare v0.3.0-rc.2 | OPEN |
| #46 | Closed beta acceptance | OPEN |
| #47 | Prepare stable v0.3.0 | OPEN |
| #48 | Public launch external gates | OPEN |

---

## 4. Secret-Hygiene

| Prüfung | Ergebnis |
| ------- | -------- |
| `git check-ignore .env` | `.env` ist ignoriert ✓ |
| `git ls-files .env` | `.env` ist NICHT getrackt ✓ |
| Secret-Scan (getrackte Dateien) | Keine `DEEPSEEK_API_KEY=`/`NUMRA_RATE_LIMIT_HMAC_SECRET=`-Werte in getrackten Dateien ✓ |
| Lokale `.env` | Enthält echte Secrets (DeepSeek-Key, HMAC-Secret). **Wird nicht committet, nicht in Berichte übernommen.** Für deterministische Tests wird `NUMRA_LLM_ENABLED=false` verwendet. |

---

## 5. Externe Blocker (Stand Baseline)

| Gate | Status |
| ---- | ------ |
| Genehmigter privater Staging-Host | **BLOCKED** (kein genehmigter Host vorhanden; Issue #39 offen) |
| Legal Approval / Transfer Approval | **BLOCKED** (keine Freigaben vorhanden) |
| Provider-Secret für echten Smoke | **BLOCKED** (nur lokales Dummy/`.env`-Secret; kein genehmigter Provider-Smoke) |
| Reale Beta-Tester | **BLOCKED** (keine Tester vorhanden) |
| Produktionsdomain / Public Deployment | **BLOCKED** (nicht freigegeben) |

Alle lokal ausführbaren Gates sind davon unabhängig und werden vollständig abgearbeitet.

---

## 6. Befund B-0: RC1-Tag-SHA weicht von Auftragserwartung ab

- Erwartet (Auftrag): `21ba56ed0d918cea7c60090bcc50937adc16269a`
- Tatsächlich: `cec214ec6c8a9b41f13a073d738ffea3734d9d60`

**Bewertung:** Der Tag `v0.3.0-rc.1` ist ein annotierter Tag; `git rev-parse v0.3.0-rc.1` liefert die Tag-Objekt-SHA, nicht die Commit-SHA. Die Abweichung ist daher plausibel durch Tag-Objekt vs. Commit-Objekt erklärbar. Verifikation der Commit-SHA des Tags folgt in Phase 1 (`git rev-parse v0.3.0-rc.1^{commit}`). Kein Hinweis auf Tag-Manipulation.

---

## 7. Nächste Schritte

1. Phase 1: Fehler reproduzieren (OpenAPI-Export, Knowledge-Validierung, Web-Codegen) und Befundtabelle erstellen.
2. Phase 2: OpenAPI-/Codegen-Drift beheben, V1-Contract-Gate prüfen, V2-Vollständigkeit (4 Endpunkte) verifizieren.
3. Weitere Phasen gemäß Auftrag (3–20).
