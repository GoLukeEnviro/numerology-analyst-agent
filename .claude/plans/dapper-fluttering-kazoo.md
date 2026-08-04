# Numra — Weg bis `v0.3.0-rc.2`, mit parallelem V2-Strang (Fassung 2)

## Fortschritt (Stand 2026-08-04, Abend)

| Schritt | Stand |
|---|---|
| Diagnose + Bericht | ✅ Score 81,95, `projektdiagnose-bericht.md` |
| ARCH-001 · 422-Guard am Profilendpunkt | ✅ gemerged (PR #54) |
| TEST-001 · Wheel-Ressourcenprüfung | ✅ gemerged (PR #54) |
| A1 · Audit-/Advisory-Gate | ✅ gemerged (PR #54) — 2 echte Fixes (brace-expansion, fast-uri), react-router-Ausnahme dokumentiert mit Ablaufdatum vor stable |
| CQ-001 · toter Re-Export-Aggregator | ✅ PR #55 |
| A2.3 · Committee-Status-Widersprüche | ✅ PR #55 — 4 Stellen korrigiert (Review COMPLETE / Entscheidung NO_GO / Betrieb BLOCKED_BY_STAGING) |
| A2.4 · Rollback-Rehearsal lokal (ENG-01) | ✅ PR #55 — real gegen Docker-Stack bewiesen, Exit 0 |
| A2.1 · restore-config.sh (OPS-001) | ✅ PR #55 — funktional bewiesen (Encrypt/Decrypt/Restore-Zyklus) |
| A2.2 · release.sh Deploy-by-Digest (OPS-002) | ✅ PR #55 — real bewiesen, Digests nach Deploy = Digests nach Build |
| A3 · frischer Gate-Lauf + RC2-Kandidat | ✅ PR #55 — alle Gates grün, Digests erfasst, 1 flaky lokaler E2E-Test dokumentiert und als Folgeaufgabe ausgelagert |
| **A0 · Staging-Host** | ❌ **weiterhin extern offen — einziger verbleibender Blocker für A4** |
| A4 · Staging-Nachweis | ⬚ blockiert durch A0 |
| A5 · Committee-Re-Review | ⬚ blockiert durch A4 |
| A6 · RC2-Schnitt | ⬚ blockiert durch A5 |
| Strang B · V2-Anbindung | ○ Plan liegt vor (PR #53, `.claude/plans/`, nicht `docs/plans/`), B0-Sequenz-ADR noch nicht geschrieben |

PR #54 (main) und PR #55 (offen, CI läuft) fassen den gesamten host-unabhängigen Teil von
Strang A zusammen. Nach A0 sind nur noch A4–A6 offen.

## Kontext

Nach der Projektdiagnose vom 2026-08-03 (Score 81,95, Bericht unter
`projektdiagnose-bericht.md`) und der Behebung von ARCH-001 und TEST-001 soll der Weg bis
zum fertigen Projekt geplant werden.

Drei Weichen sind entschieden:

| Frage | Entscheidung |
|---|---|
| Zielmarke | **`v0.3.0-rc.2`** |
| Staging-Host | **existiert noch nicht** → Beschaffung ist Teil des Plans |
| V2-Programm (`pythagorean-v2`) | **parallel aufnehmen**, trotz Deferral in ADR 0016 |

Das Committee-Review für RC2 **ist bereits durchgeführt** (`docs/committee/rc2-*.md`,
Stand 2026-08-02) und endet auf `RELEASE_DECISION=NO_GO` mit sechs Bedingungen —
nicht wegen Codemängeln (`CRITICAL_FINDINGS_OPEN=0`, `DETERMINISTIC_CODE_QUALITY=PASS`),
sondern weil der Betriebsnachweis fehlt.

Diese Fassung arbeitet 13 Review-Korrekturen ein. Sieben davon sind ausführungskritisch;
drei ließen sich am Repository direkt belegen und werden als **neue Betriebsbefunde**
geführt, die die Diagnose nicht erfasst hatte (sie prüfte Betriebsskripte nicht auf
Semantik):

| ID | Befund | Beleg |
|---|---|---|
| **OPS-001** | Kein Restore-Skript vorhanden. `backup-config.sh:25` entschlüsselt nur zur *Verifikation* — das belegt Lesbarkeit, nicht Wiederherstellbarkeit. | `deploy/scripts/` enthält kein `restore-*` |
| **OPS-002** | `release.sh:33` führt `docker compose build --pull` **auf dem Zielhost** aus. Lokal getestetes und auf Staging laufendes Image sind damit nicht dasselbe OCI-Artefakt, trotz identischem Git-SHA. | `deploy/scripts/release.sh:32-34` |
| **OPS-003** | `package.json:20-24` trägt eine **GHSA-ID im `ignoreCves`-Feld**. Das Projekt pinnt `pnpm@10.22.0`; dort erwartet `ignoreCves` CVE-IDs, GHSA-IDs gehören nach `ignoreGhsas`. Das erklärt, warum der Diagnoselauf das Advisory trotz Ausnahme meldete. | `package.json:4`, `:20-24`; Messung 2026-08-03 |

Stand der sechs Committee-Bedingungen:

| # | Bedingung | Stand |
|---|---|---|
| 1 | Staging-Host benannt | ❌ offen — **Gate 1**, blockiert 2–4 |
| 2 | Deploy mit gepinntem SHA, `LLM=false` | ❌ braucht 1 **und** OPS-002 |
| 3 | Restore PASS | ❌ braucht 1 **und** OPS-001 |
| 4 | Rollback PASS | ❌ braucht 1 **und** eine Known-Good-Baseline |
| 5 | Rollback-SHA-Fix auf `main` | ✅ `aa3c2c8` (PR #51); Rehearsal-Übung fehlt noch |
| 6 | Keine neuen Critical/High im Code | ⚠️ **PROVISIONAL** bis OPS-003 geklärt — **Gate 2** |

**Es gibt damit zwei Gates, nicht eines.** Der Staging-Host ist der größere, aber das
Audit-/Advisory-Gate ist unabhängig davon offen.

## Regeln für beide Stränge

- Tag `v0.3.0-rc.1` wird nicht bewegt. Paketversion bleibt `0.3.0rc1` bis zum RC2-Schnitt.
- Kein Direktpush auf `main`, kein Force-Push, kein `--no-verify`.
- Jede Verhaltensänderung an einem öffentlichen Vertrag braucht einen Test, der den alten
  Zustand reproduziert (Muster: `test_v1_endpoint_rejects_a_foreign_method_version`).
- **Build once, test once, promote by digest.** Nachweise gelten nur mit Git-SHA *und*
  Image-Digest. Skript-Existenz ist kein Nachweis.
- Committee-Status und Release-Status bleiben getrennt: Ein abgeschlossenes Review ist
  keine Freigabe.

---

# Strang A — Weg zu `v0.3.0-rc.2`

## A0 · Gate 1: Staging-Host

**Ihre Aufgabe, blockiert A4.** Genau ein SSH-Alias als Numra-Stagingziel benennen.
`docs/operations/vps-inventory-2026-07-26.md` hält fest, dass kein Ziel eindeutig als
Numra-VPS erkennbar ist. Mindestanforderung aus `deploy/scripts/preflight.sh`:
Docker-fähig, ≥ 40 GiB frei unter `/opt`, `127.0.0.1:8080` verwendbar.

> Die Roadmap schließt „ungeprüftes Shared-Hermes/Trading-Hosting" ausdrücklich aus.
> Eine Mitnutzung bräuchte eine bewusste ADR-Entscheidung statt einer stillen Umwidmung.

## A1 · Gate 2: Audit- und Advisory-Vertrag (OPS-003)

Sofort umsetzbar, unabhängig vom Host. Bedingung 6 gilt bis zum Abschluss als
`PROVISIONAL`, nicht als erfüllt.

1. Gepinnte pnpm-Version bestätigen (`package.json:4` → `pnpm@10.22.0`) und gegen die
   in CI tatsächlich verwendete Version abgleichen.
2. Die fehlerhafte Zuordnung entfernen: GHSA-ID gehört unter pnpm 10 nach
   `auditConfig.ignoreGhsas`, nicht nach `ignoreCves`.
3. **Nichtbetroffenheit technisch belegen statt behaupten.** Das Advisory
   (`GHSA-qwww-vcr4-c8h2`, betroffen `>=7.12.0 <8.3.0`, behoben `8.3.0`) betrifft die
   instabilen React-Router-**RSC**-APIs. Erster Nachweis liegt vor: `apps/web/src/App.tsx:2`
   importiert `BrowserRouter` aus `react-router-dom` — klassisches Client-Side-Routing,
   kein `unstable_`-Import, keine Server Components. Zu ergänzen ist der Bundle-Nachweis,
   dass der betroffene Code im Build nicht erreichbar ist.
4. Ausnahme nur mit Advisory-ID, technischer Nichtbetroffenheitsbegründung, Owner
   (Issue #42), **Ablaufdatum und erneutem Prüfdatum** dokumentieren.
5. `pnpm audit --json` und den exakten CI-Audit-Befehl ausführen, Exitcode und geparste
   Advisory-Anzahl protokollieren.

> **Korrektur gegenüber Fassung 1:** Die Zurückstellung war dort mit „deterministischer
> RC2, LLM off" begründet. Das ist sachlich falsch — die Schwachstelle hat keinen Bezug
> zur LLM-Konfiguration. Tragfähig ist allein der RSC-Nichtbetroffenheitsnachweis.

## A2 · Weitere host-unabhängige Vorarbeiten

**A2.1 — Restore-Fähigkeit herstellen (OPS-001).** Ein `restore-config.sh` erstellen, das
den in A4.4 verlangten Ablauf ausführbar macht, plus Ergänzung der Launch-Checkliste:
Zeile 39 verlangt heute nur „Entschlüsseln und Inhaltsprüfung" — das ist der zu schwache
Nachweis, den das Review zu Recht bemängelt.

**A2.2 — Deploy-by-Digest herstellen (OPS-002).** `release.sh` so ändern, dass es ein
bereits gebautes Image über `image@sha256:<digest>` deployt, statt auf dem Zielhost neu
zu bauen. Ein Docker-Tag ist veränderlich, ein Digest ist inhaltsbasiert und
unveränderlich. Ohne diese Änderung ist Bedingung 2 formal nicht belegbar.

**A2.3 — Doku-Widersprüche schließen, mit getrennten Zuständen.** Drei Stellen behaupten
`Committee Review = NOT_STARTED`, obwohl sieben ausgefüllte Reviews vorliegen:
`ROADMAP.md` (Statusmatrix Phase 13), `docs/audit/current-state-numra-post-rc1-2026-08-02.md`
(Abschnitt 2), `docs/releases/unreleased-numra.md`. Korrekt ist **nicht** „abgeschlossen",
sondern die Trennung:

```text
Committee Review:       COMPLETE
Release Decision:       NO_GO
Operational Acceptance: BLOCKED_BY_STAGING
RC2 Release:            NOT_RELEASED
```

**A2.4 — Rollback-Rehearsal lokal üben.** Bedingung 5 ist gemergt, ENG-01 verlangt
zusätzlich „lokal/remote geübt". `deploy/scripts/rollback-rehearsal.sh` gegen den lokalen
Stack ausführen, Protokoll ablegen. Der Vertrag ist testgesichert
(`test_rollback_rehearsal_uses_sha_tags_compatible_with_rollback_script`).

**A2.5 — Quick Win.** **CQ-001**: 72 Zeilen doppelte Exportliste zwischen
`src/numerology_domain/models.py:19` und `_models/__init__.py:9` entdoppeln.

> **ARCH-003 (`--method-version` in der CLI) gehört nicht hierher.** Fassung 1 hatte sie
> unter Strang A geführt und zugleich versprochen, dass kein V2-Code in den RC2-Tag
> fließt — ein Widerspruch. Die Option macht V2 erreichbar und ist damit Strang B (B2).

**Nicht in RC2:** Abhängigkeits-Aktualisierungen TS-002/003/004 (`redis` 8.x, `mypy` 2.x,
`pytest-cov` 7.x, `ruff` 0.16, TypeScript 7.x). Vier erfordern das Anheben deklarierter
Obergrenzen; `mypy 2.x` und `typescript 7.x` bringen erfahrungsgemäß neue Befunde. Kurz
vor einem Release-Schnitt gefährdet das Bedingung 6 ohne Nutzen für RC2. Einplanen im
Beta-Fenster vor stable.

## A3 · Frische Gates auf dem RC2-Kandidaten

Vollständig lokal reproduzieren (Kommandos siehe *Verifikation*), Ergebnis als
Gate-Protokoll unter `docs/audit/` ablegen (Muster: `phase-*-gate-2026-08-02.md`).
Danach den RC2-Kandidaten **einmal** bauen, in die Registry pushen und den Digest
erfassen — alle folgenden Schritte laufen gegen genau diesen Digest.

## A4 · Staging-Nachweis (braucht A0, A2.1, A2.2)

**A4.1 — Preflight.** `deploy/scripts/preflight.sh`, Ergebnis dokumentieren.

**A4.2 — Known-Good-Baseline zuerst.** Auf einem frischen Host existiert kein „vorheriger
Image-Tag", auf den zurückgerollt werden könnte. Deshalb zuerst den unveränderten
**RC1-Stand** deployen, Commit-SHA und Image-Digest erfassen, Smoke ausführen und als
`KNOWN_GOOD` markieren. Ohne diese Baseline ist Bedingung 4 nicht sauber belegbar.

**A4.3 — RC2-Kandidat deployen.** Exakt gepinnter Commit-SHA, exakt gepinnter
Image-Digest aus A3, `NUMRA_LLM_ENABLED=false`. Danach Health live/ready, echte
Profilberechnung (`deploy/scripts/api-smoke.sh`) und Log-Prüfung: weder Name noch
Geburtsdatum, kein Request-Body, keine Profilantwort, keine LLM-Ausgabe.
Deployment-Digest gegen den getesteten Digest vergleichen.

**A4.4 — Restore-Rehearsal (echter Nachweis).**

1. Zustand vor Backup erfassen
2. Backup erstellen, Hash dokumentieren
3. Konfiguration gezielt entfernen oder in eine leere Recovery-Umgebung wechseln
4. dokumentierten Restore-Prozess ausführen (A2.1)
5. Dateirechte, Eigentümer und Konfigurationswerte strukturell prüfen
6. Container neu starten
7. Ready-, Profil- und Persistenz-Smoke ausführen, Restore-Ergebnis und Backup-ID
   dokumentieren

**A4.5 — Rollback auf die `KNOWN_GOOD`-Baseline** aus A4.2 — auf den Digest, nicht auf
einen symbolischen oder veränderlichen Tag. Danach vollständiger Smoke.

**A4.6 — Optional: Forward-Deploy des RC2-Kandidaten wiederholen.** Beweist, dass
Rollback und erneute Promotion beide funktionieren.

Jeder Schritt fließt in einen Acceptance-Report unter `docs/operations/` mit:
Git-Commit-SHA, Image-Digest, Compose-Konfigurationshash, Build-/Workflow-Run-ID,
Zeitpunkt, Plattform/Architektur.

## A5 · Committee-Re-Review — evidenzbasiert, nicht redaktionell

Die Gate-Werte werden **nicht überschrieben**, sondern aus Belegen neu abgeleitet. Für
jede der sechs Bedingungen entsteht ein Closure-Eintrag:

```text
Condition-ID · vorheriger Status · neuer Status · Commit-SHA · Image-Digest
· Acceptance-Report · Datum · Reviewer · verbleibendes Risiko
```

Erst wenn alle blockierenden Bedingungen durch Belege geschlossen sind, wird
`RELEASE_DECISION` in `docs/committee/rc2-release-decision.md` neu berechnet. Neue
Erkenntnisse (OPS-001 bis OPS-003, die Fixes dieser Session) in `rc2-findings.md`
einpflegen.

## A6 · RC2-Schnitt

Paketversion auf `0.3.0rc2`, PR gegen `main`, CI abwarten, nach Merge `v0.3.0-rc.2`
taggen, GitHub-Release mit Notes aus `docs/releases/v0.3.0-rc.2.md`. Aufzunehmen sind
die seit RC1 gemergten PRs (#34, #35, #36, #50, #51, #52), die beiden Fixes dieser
Session — der 422-Guard am Profilendpunkt als **für Clients sichtbare
Verhaltensänderung** und die scharf geschaltete Wheel-Ressourcenprüfung — sowie
OPS-001/002/003.

Im Release-Skript validieren, dass Paketversion `0.3.0rc2` und Tag `v0.3.0-rc.2`
denselben Release bezeichnen.

**Tag-Gate:**

```text
RELEASE_DECISION=GO
  oder
RELEASE_DECISION=GO_WITH_CONDITIONS  UND  BLOCKING_CONDITIONS_OPEN=0
  UND jede verbleibende Bedingung ausdrücklich als non-blocking klassifiziert
  UND Owner, Frist und Risikoakzeptanz dokumentiert
```

---

# Strang B — `pythagorean-v2` produktiv anbinden

Eigener Branch, parallel. RC2 hängt an Betriebsnachweis und Audit-Gate; V2-Code fließt
nicht in den RC2-Tag.

## B0 · Sequenz-ADR — Bestandteil von Welle 0

ADR 0016 führt V2 als `DEFERRED` mit der Bedingung „keine Implementierung vor stable
0.3.0 + Sequenz-ADR". Der vorgezogene Start ist damit vereinbar, aber nur über genau
diesen Weg: einen ADR, der die Sequenzentscheidung ablöst und begründet, warum vorgezogen
wird (ein fertiger, unerreichbarer Vertrag altert weiter) und wie das RC2-Risiko begrenzt
bleibt (eigener Branch, kein Eintrag in den RC2-Tag).

**ADR 0016 wird nicht still editiert**, sondern im Geltungsbereich ausdrücklich als
`SUPERSEDED` gekennzeichnet. B0 ist einer der 15 ADRs aus Welle 0 und ersetzt darin die
bisherige Sequenzentscheidung — es entsteht kein 16. ADR.

**Ohne diesen ADR entsteht genau die stille Vertragsänderung, die der Master-Vertrag §2.4
untersagt.** Er ist der erste Schritt von Strang B.

## B1 · Umsetzungsplan versionieren

Der 26-Korrekturen-Plan liegt als Session-Artefakt vor und ist nicht versioniert. Vor
Welle 1 als `docs/plans/numra-v2-anbindung.md` ins Repository legen, damit die Wellen
referenzierbar sind.

## B2–B7 · Wellen

| Welle | Inhalt | Bezug zu Strang A |
|---|---|---|
| 0 | 15 ADRs inkl. Sequenz-ADR (B0) | unabhängig |
| 1 | API-Grundlage: `/api/v2/profiles`, `/api/v2/meta`, Dependency-Wiring, OpenAPI-Artefaktstrategie · **plus ARCH-003 (`--method-version`)** | nutzt den 422-Guard dieser Session als Vorbild |
| 2 | Fakten- und Wissensmodell (`de-v3.json`, `AnalysisFactEntryV3`) | unabhängig |
| 3 | Berichtserzeugung: `AgentServiceV3`, V3-Provider, Idempotenz, `/api/v2/analyses` | unabhängig |
| 4 | Web-Migration, Tab-UI, Storage-Versionierung, Offline-Zustände | berührt `apps/web` — erst nach dem RC2-Schnitt mergen |
| 5A–5C | DeepSeek-Evaluation, Opt-in-Beta, Default-Wechsel | frühestens nach RC2 |

## Schließkriterium für TS-001 — jetzt festgelegt

Der Befund lautet „kein Produktionspfad erreicht den V2-Rechenkern". Er wird deshalb
**nicht erst mit Welle 5C** geschlossen, sondern sobald folgendes gilt:

```text
TS-001 geschlossen, wenn:
- mindestens ein freigegebener Produktionsendpunkt den V2-Kern erreicht
- der V2-Methodenvertrag end-to-end erhalten bleibt (keine Reduktion gehaltener Meisterzahlen)
- OpenAPI, Persistenz und Berichtspfad konsistent versioniert sind
- Golden- und Contract-Tests diesen Pfad absichern
```

Realistisch ist das nach Welle 3. Der **Default-Wechsel in Welle 5C ist ein separates
Produkt-Gate**, keine Bedingung für die Schließung des Befunds. Der Befund wird nicht
nachträglich so umgedeutet, dass er zur Roadmap passt.

## Verzahnungsregel

Solange Strang A offen ist: **kein V2-Merge nach `main`.** Welle 4 fasst Dateien an, die
der RC2-Staging-Nachweis abdeckt — ein Merge davor entwertet den bewiesenen Stand.

---

## Verifikation

Umgebungsnachweis vor jedem Gate-Lauf:

```bash
uv --version && uv lock --check && uv run --locked python --version
pnpm --version && node --version
```

Python-Gates mit definierter Umgebung und getrennten Coverage-Artefakten:

```bash
uv sync --locked --exact
uv run --locked ruff format --check . && uv run --locked ruff check .
uv run --locked mypy src tests scripts
COVERAGE_FILE=<scratchpad>/.coverage-engine uv run --locked pytest --cov=src/numerology_engine --cov-fail-under=95 --cov-report=json:<scratchpad>/coverage-engine.json -o cache_dir=<scratchpad>/pytest-cache-engine
COVERAGE_FILE=<scratchpad>/.coverage-all uv run --locked pytest --cov=src --cov-fail-under=85 --cov-report=json:<scratchpad>/coverage-all.json -o cache_dir=<scratchpad>/pytest-cache-all
uv run --locked python scripts/export_openapi.py --check
uv run --locked python scripts/export_schemas.py --check
uv run --locked python scripts/generate_examples.py --check
uv run --locked --no-sync pip-audit --format json --output <scratchpad>/pip-audit.json
```

Web-Gates **inklusive Sicherheitsaudit** (in Fassung 1 fehlte `pnpm audit`):

```bash
pnpm web:lint && pnpm web:typecheck && pnpm web:test && pnpm web:build && pnpm web:e2e
pnpm audit --json > <scratchpad>/pnpm-audit.json
pnpm audit --audit-level=high
```

Container:

```bash
docker compose config --quiet && docker compose build && docker compose up -d --wait
curl --fail http://127.0.0.1:8080/api/v1/health/ready
```

**Exitcode-Semantik.** `pip-audit` und `pnpm audit` Exit 1 bedeutet „Schwachstellen
gefunden" — ein gültiges Messergebnis, kein Werkzeugfehler. Nur fehlendes Werkzeug,
Registry-/Netzfehler, Timeout oder ungültiges JSON sind Messfehler. `docker compose up
--wait` wartet auf `running` beziehungsweise `healthy`; der Ready-Endpoint-Check bleibt
trotzdem zwingend.

**Abnahme Strang A:** Tag-Gate aus A6 erfüllt, `v0.3.0-rc.2` existiert mit Release-Notes,
`v0.3.0-rc.1` unbewegt, Acceptance-Report mit Git-SHA und Image-Digest vorhanden.

**Abnahme Strang B:** Golden-Fall Lukas Springer über den vollen V2-Graphen — primär
`40/4` nie überschrieben, sekundär `22/4` mit gehaltenem Meisterwert 22 bis in den Bericht.

## Kritische Dateien

- **Betrieb:** `deploy/scripts/{preflight,stage,release,backup-config,rollback,rollback-rehearsal,api-smoke}.sh`, neu `restore-config.sh`, `docs/operations/launch-checklist.md`
- **Audit-Ausnahme:** `package.json:4` (pnpm-Pin), `:20-24` (Ausnahmefeld)
- **Status und Wahrheit:** `ROADMAP.md` (Statusmatrix), `docs/audit/current-state-numra-post-rc1-2026-08-02.md`, `docs/releases/unreleased-numra.md`, neu `docs/releases/v0.3.0-rc.2.md`
- **Committee:** `docs/committee/rc2-release-decision.md`, `rc2-findings.md`
- **Quick Win:** `src/numerology_domain/models.py:19`
- **Strang B:** ADR 0016 (auf `SUPERSEDED` setzen), neuer Sequenz-ADR, neu `docs/plans/numra-v2-anbindung.md`, danach die `*_v3.py`-Module

## Was dieser Plan bewusst nicht enthält

Closed Beta, stable `v0.3.0` und der öffentliche Launch. Sie liegen hinter RC2 und hängen
an Gates, die nicht durch Umsetzungsarbeit erreichbar sind: Testpersonen mit Einwilligung,
Domain und DNS, HTTPS, Impressum, Betreiberangaben und die rechtliche Freigabe für
Drittlandtransfer. `docs/operations/launch-checklist.md` führt sie vollständig; sie werden
nach dem RC2-Schnitt zu einem eigenen Planungsschnitt.
