# Dependency- und Security-Entscheidung (RC2) — 2026-08-03

> **Bezug:** Issue #42 · Epic #37 · Plan-Schritt A1 (Audit- und Advisory-Gate)
> **Vorgänger:** [`dependency-decision-rc2-2026-08-02.md`](./dependency-decision-rc2-2026-08-02.md) —
> bleibt als historisches Artefakt gültig, wird durch dieses Dokument abgelöst.
> **Mess-Basis:** Worktree auf `6b4d71ab` plus die Fixes dieser Session,
> `pnpm@10.22.0` (gepinnt in `package.json:4`), Node/pnpm lokal verifiziert.
> **Primärquellen:** `pnpm audit --json`, `pip-audit`, GitHub Advisory Database.

## Anlass

Der Diagnoselauf vom Vormittag des 2026-08-03 meldete **ein** `high`-Advisory
(react-router). Eine erneute Messung am selben Tag meldete **drei**. Zwei davon sind neu
in der Advisory-Datenbank und betreffen Pakete, für die das Repository bereits eine
Mitigation trug, die nicht mehr ausreicht.

## Node / Frontend — Messung 2026-08-03

| Advisory | Paket | Pfad | Severity | Patch ab | Entscheidung |
|---|---|---|---|---|---|
| [GHSA-qwww-vcr4-c8h2](https://github.com/advisories/GHSA-qwww-vcr4-c8h2) | `react-router` 7.18.1 | `apps__web>react-router-dom>react-router` | HIGH | 8.3.0 (Major) | **DEFER mit dokumentierter Ausnahme** |
| [GHSA-rgw5-rvv9-x895](https://github.com/advisories/GHSA-rgw5-rvv9-x895) (CVE-2026-69152) | `brace-expansion` | `apps__web>eslint>minimatch>brace-expansion` | HIGH | 5.0.9 | **BEHOBEN** per Override |
| [GHSA-7p8r-x3mc-p8w7](https://github.com/advisories/GHSA-7p8r-x3mc-p8w7) (CVE-2026-18446) | `fast-uri` | `apps__web>vite-plugin-pwa>workbox-build>ajv>fast-uri` | HIGH | 3.1.5 | **BEHOBEN** per Override |

### Überholte Mitigation (der eigentliche Befund)

`package.json` trug ein Override `brace-expansion@<=5.0.7: 5.0.8`. Das neue Advisory
beschreibt ausdrücklich eine **Umgehung der vorherigen Mitigation** („bypassing the
CVE-2026-14257 mitigation") und ist erst ab `5.0.9` behoben. Das bestehende Override
löste die alte Lücke, nicht die neue.

Angewandte Änderungen in `package.json`:

```text
brace-expansion@<=5.0.7: 5.0.8   →   brace-expansion@<5.0.9: 5.0.9
(neu)                            →   fast-uri@<3.1.5: 3.1.5
```

Lockfile-Auswirkung: 11 Einfügungen, 10 Löschungen — ausschließlich
`brace-expansion 5.0.8 → 5.0.9` und `fast-uri 3.1.4 → 3.1.5`. Keine weiteren
Paketbewegungen.

### react-router — Ausnahme mit Ablaufdatum

Die Zurückstellung des Major-Upgrades bleibt bestehen. Sie stützt sich **nicht** auf die
LLM-Konfiguration (das wäre sachfremd — das Advisory hat keinen Bezug zu
`NUMRA_LLM_ENABLED`), sondern auf technische Nichtbetroffenheit:

| Prüfung | Ergebnis |
|---|---|
| Betroffene Fläche laut Advisory | instabile React-Router-**RSC**-APIs, Server Actions |
| Verwendung in Numra | `apps/web/src/App.tsx:2` importiert ausschließlich `BrowserRouter`, `Route`, `Routes`, `useNavigate`, `useParams` |
| RSC- oder `unstable_`-Importe | keine — Volltextsuche über `apps/web` ohne Treffer |
| Serverseitiges HTML-Templating | nicht vorhanden (Vite-SPA, statisches Bundle) |
| Offener Nachweis | Bundle-Ebene: dass der betroffene Codepfad im gebauten Artefakt nicht erreichbar ist |

| Feld | Wert |
|---|---|
| Owner | Release-Orchestrator · Issue #42 |
| Akzeptiertes Restrisiko | JA, bis zum Upgrade-Stream |
| **Ablaufdatum der Ausnahme** | **vor `v0.3.0` stable** — nicht verlängerbar ohne erneute Entscheidung |
| **Nächstes Prüfdatum** | beim RC2-Schnitt sowie bei jedem Advisory-Datenbank-Update |
| Umsetzungspfad | Branch `fix/rc2-dependency-security`, Upgrade auf ≥ 8.3.0 mit voller Web- und E2E-Matrix |

## Python

| Prüfung | Ergebnis | Entscheidung |
|---|---|---|
| `uv run --locked pip-audit -f json` (2026-08-03) | keine bekannten Schwachstellen, 64 Pakete | behalten — keine Aktion |

## Verifikation dieser Entscheidung

```text
vorher   pnpm audit --json                → 3 high (1124282, 1130705, 1130720)
nachher  pnpm audit --json                → 1 high, advisories[] leer (ignoriert)
nachher  pnpm audit --audit-level=high    → Exit 0 ("1 high, 1 ignored")
CI-Gate  pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2  → Exit 0
```

Regressionsfreiheit nach den Overrides:

```text
pnpm web:lint       Exit 0
pnpm web:typecheck  Exit 0
pnpm web:test       Exit 0  (11 Dateien, 43 Tests)
pnpm web:build      Exit 0  (PWA precache 11 entries, 485,14 KiB)
```

## Hinweis zur Ausnahme-Konfiguration

Die Ausnahme ist an **zwei** Stellen hinterlegt: als CLI-Flag in
`.github/workflows/ci.yml:152` (mit der korrekten Nichtbetroffenheitsbegründung in den
Kommentarzeilen 149–151) und deklarativ unter `pnpm.auditConfig` in `package.json`.

Zu beachten: Unter pnpm 10 nimmt `auditConfig.ignoreCves` **CVE-IDs** entgegen;
GHSA-Kennungen gehören nach `auditConfig.ignoreGhsas`. Ein GHSA-Wert im `ignoreCves`-Feld
bleibt wirkungslos. Für die Pflege bedeutet das: Die wirksamen Mechanismen sind das
CI-Flag und `ignoreGhsas`. Eine Zusammenführung auf **eine** Quelle wäre die sauberere
Lösung und ist beim RC2-Schnitt zu entscheiden.

## Gate

```text
DEPENDENCY_DECISION=DEFER_REACT_ROUTER_MAJOR
BRACE_EXPANSION_OVERRIDE=5.0.9_APPLIED
FAST_URI_OVERRIDE=3.1.5_APPLIED
PIP_AUDIT=PASS
PNPM_AUDIT_WITH_CI_IGNORE=PASS
PNPM_AUDIT_RAW_HIGH=1_IGNORED_DOCUMENTED
MAJOR_UPGRADE_PERFORMED=NO
WEB_GATES_AFTER_OVERRIDES=PASS
RC2_CONDITION_6=PROVISIONAL_PASS
```

`RC2_CONDITION_6` bleibt `PROVISIONAL`, bis der Bundle-Nachweis für die
react-router-Nichtbetroffenheit vorliegt und die Ausnahme auf eine Quelle
zusammengeführt ist.
