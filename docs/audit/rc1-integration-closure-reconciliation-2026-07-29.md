# Numra — RC1 Integration Closure Reconciliation

> Stand: 29. Juli 2026
>
> Basis-SHA: `1d2286e44157972a9a535460d0a691b44f25ff29` (origin/main)
>
> Zweck: Abgleich der RC1-Releaseunterlagen nach Abschluss der Integration-
> Closure-PRs (#19–#23, umgesetzt über PR #26/#27/#29/#30/#31). Diese Datei
> erweitert `docs/audit/final-integration-2026-07-27.md` und
> `docs/audit/current-state-numra-rc.md` um die seit dem 27. Juli integrierten
> Änderungen. Sie ersetzt keine dieser Dokumente, sondern dokumentiert das
> Delta bis zu diesem Basis-SHA.

---

## 1. Integrierte Closure-PRs

| PR | Titel | Merge-SHA | Issue |
|---|---|---|---|
| #26 | fix(engine): pythagorean-v2 Berechnungsvertrag mit Referenzkorpus | `e28e3e2` | Closes #19 |
| #27 | fix(agent): Prompt-, Knowledge- und Composer-Funktionen in Produktionspfade integriert | `d76d4de` | Closes #21 |
| #29 | fix(web): Abort-/Resubmit-Race in Analyse- und Report-Fluss schliessen | `67bf9fb` | Closes #22 |
| #30 | fix(deploy): ausfuehrbaren LLM-Staging-, Runtime-Gate- und Rollback-Vertrag herstellen | `89db34a` | Closes #23 |
| #31 | docs: Numra V2 auf nutzergebauten Guided Masterplan zurueckfuehren | `240ced6` | Closes #24 |
| #28 | docs: version README product realignment plan | `1d2286e` | (Plan-Dokument, README-Umsetzung folgt separat) |

Issue #20 (manuell verifiziertes Golden Reference Corpus) wurde nach
Verifikation der bereits mit PR #26 gelieferten 5 Referenzprofile
(`tests/golden/reference_profiles_v2.yaml`,
`docs/methods/reference-profile-derivations-v2.md`) als erledigt geschlossen.

Kein Direct-Push auf `main`, kein Force-Push auf `main`. Alle PRs wurden
mittels `gh pr merge --squash --match-head-commit <exact-head-sha>` gemergt,
jeweils erst nachdem der Feature-Branch auf den aktuellen `main`-Stand
rebased und alle Required Checks erneut grün waren.

## 2. Lokale Quality-Gate-Baselines (frisch gemessen, 29.07.2026)

Alle Werte wurden aus echten Läufen auf `1d2286e` abgeleitet, nicht aus
vorherigen Audit-Texten übernommen.

### Python

| Gate | Ergebnis |
|---|---|
| `uv run ruff format --check .` | 89 Dateien korrekt formatiert |
| `uv run ruff check .` | Alle Checks bestanden |
| `uv run mypy src tests scripts` | Success: keine Issues in 89 Dateien |
| `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` | 413 passed, 2 skipped — Engine-Coverage 98.51 % |
| `uv run pytest --cov=src --cov-fail-under=85` | 413 passed, 2 skipped — Gesamt-Coverage 93.51 % |
| `uv run python scripts/export_schemas.py --check` | Alle Schemas aktuell |
| `uv run python scripts/export_openapi.py --check` | OpenAPI aktuell |
| `uv run python scripts/generate_examples.py --check` | Beispiel stimmt mit Service-Ausgabe überein |
| `uv run python scripts/validate_knowledge.py` | de-v1 und de-v2 Wissensbündel valide |

**Bekannter, nicht release-blockierender Flake:** In 1 von 9 lokalen
Vollsuite-Läufen mit `--cov` schlug
`tests/property/test_v2_determinism.py::test_v2_hash_stable_for_same_input`
fehl; isoliert und in allen weiteren Wiederholungen (8/9 Vollsuite-Läufe,
alle Einzelläufe der Testdatei) bestanden. In keinem der tatsächlichen
GitHub-Actions-CI-Läufe von PR #26/#27/#29/#30/#31 trat dieser Fehlschlag
auf. Nachverfolgt in Issue #32 — nicht in diesem PR behoben.

### Frontend

| Gate | Ergebnis |
|---|---|
| `pnpm install --frozen-lockfile` | Lockfile aktuell, 555 Pakete |
| `pnpm web:lint` | Keine Findings |
| `pnpm web:typecheck` | Keine Fehler |
| `pnpm web:test` | 43 passed (11 Testdateien) |
| `pnpm web:build` | Build erfolgreich, PWA-Precache 11 Einträge |

### Container / Deployment

| Gate | Ergebnis |
|---|---|
| `docker compose config --quiet` | Gültig |
| `docker compose -f compose.yaml -f compose.llm-staging.yaml config --quiet` | Gültig |
| `sh -n` auf alle `deploy/scripts/*.sh` | Alle syntaktisch korrekt |
| CI: Runtime-Gate-Integrationstest (Dummy-Marker, LLM-Staging-Override) | Grün (verifiziert in PR #30) |

## 3. Versionsabgleich

| Datei | Wert | Format |
|---|---|---|
| `pyproject.toml` | `0.3.0rc1` | PEP 440 |
| `apps/web/package.json` | `0.3.0-rc.1` | SemVer |
| `openapi/numra-v1.json` | `0.3.0rc1` | PEP 440 (aus `pyproject.toml` exportiert) |

Beide Schreibweisen sind für ihr jeweiliges Ökosystem korrekt und
bezeichnen dieselbe Version — kein Widerspruch, keine Änderung nötig.

## 4. Release Notes

`docs/releases/v0.3.0-rc.1.md` wurde um einen Abschnitt "Integration Closure
(2026-07-29)" ergänzt, der die fünf oben gelisteten PRs mit ihren konkreten
Änderungen dokumentiert, sowie um den bekannten Test-Flake (Issue #32) und
die explizite Feststellung, dass das Setzen von Tag/GitHub-Release eine
separate menschliche Entscheidung bleibt (siehe Abschnitt 5).

## 5. Tag- und Release-Entscheidung

**Kein Tag wurde in diesem PR gesetzt.** Gemäß Issue #25 (Abschnitt "Out of
Scope") ist das Setzen eines Git-Tags oder GitHub-Release ausdrücklich eine
menschliche Entscheidung und nicht Teil der Integration-Closure-Reconciliation.
Dieser PR liefert ausschließlich:

- konsistente, aktuelle Release Notes,
- diesen Audit-Reconciliation-Bericht,
- den Nachweis, dass alle lokalen und Remote-CI-Gates auf dem finalen
  Merge-Stand grün sind.

Der Tag `v0.3.0-rc.1` auf dem finalen `main`-SHA nach diesem PR bleibt eine
ausstehende, bewusst nicht automatisierte Entscheidung des Betreibers.

## 6. Nicht in diesem PR abgeschlossen

- Issue #32 (Determinismus-Test-Flake) — dediziertes Follow-up.
- Die eigentliche README-Realignment-Umsetzung (`docs/plans/readme-product-realignment-plan.md`
  aus PR #28 ist ein Plan-Dokument; die tatsächliche README-Überarbeitung
  ist laut Plan ein separater, späterer PR).
- Öffentliches Staging/Deployment — weiterhin explizit außerhalb des Scopes
  (siehe ADR 0013, Issue #23 "Out of Scope").
