# Plan — State Reconciliation: Repository-Truth und pnpm GHSA-Mapping

> **Zweck:** Verbindlicher Ausführungsplan für die State-Reconciliation-Änderungen.
> **Status:** `READY_TO_PUSH` — lokale Änderungen sind committed, `origin/main` liegt zurück.
> **Stand:** 2026-08-04 (aktualisiert nach Zustandsprüfung)
> **Sprache:** Deutsch

---

## 0. Repository-Zustandsmatrix (verifiziert 2026-08-04)

| Ebene | Status |
|---|---|
| GitHub `origin/main` | `a3f168e` — veraltet; OPS-003 und Dokumentationsdrift vorhanden |
| Lokaler Branch | `main` @ `9cc7e44` — 4 Commits ahead of `origin/main` |
| `fix/state-reconciliation` Branch | existiert @ `5d5c9c4`, bereits nach `main` gemerged in `bd42752` |
| Lokaler Arbeitsbaum | sauber; Reconciliation-Korrekturen sind committed |
| Uncommitted | nur diese Plan-Datei (`plans/state-reconciliation-pr-plan.md`, untracked) |
| Pull Request | nicht erforderlich — Änderungen sind auf `main`, müssen nur gepusht werden |

### Commit-Historie (origin/main..HEAD)

| Commit | Beschreibung |
|---|---|
| `5d5c9c4` | `fix(state): Repository-Truth wiederherstellen und Sequenz-Governance etablieren` |
| `bd42752` | `merge: fix/state-reconciliation — Repository-Truth, Sequenz-ADR 0017, Full-Analysis-Plan` |
| `199277c` | `fix(security): correct pnpm GHSA audit mapping` |
| `9cc7e44` | `docs: clarify ADR supersession and reconciliation scope` |

---

## 1. Phase 1 — Bereits committete Änderungen verifizieren

Keine erneute Implementierung. Nur prüfen, dass die 4 Commits die erwarteten Änderungen enthalten.

### 1.1 Commit-Inhalte prüfen

```bash
git diff origin/main..HEAD -- package.json
git diff origin/main..HEAD -- docs/adr/0016-v2-user-owned-masterplan-boundary.md
git diff origin/main..HEAD -- docs/adr/0017-v2-parallel-anbindung-sequenz.md
git diff origin/main..HEAD -- ROADMAP.md
```

### 1.2 Alle geänderten Dateien erfassen

```bash
git diff --name-only origin/main..HEAD
git diff --stat origin/main..HEAD
```

---

## 2. Phase 2 — Semantische Gates

### 2.1 OPS-003 Contract-Test

```bash
node - <<'NODE'
const fs = require("fs");

const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
const audit = pkg?.pnpm?.auditConfig ?? {};

if (!audit.ignoreGhsas?.includes("GHSA-qwww-vcr4-c8h2")) {
  throw new Error("GHSA fehlt in ignoreGhsas");
}

if ((audit.ignoreCves ?? []).includes("GHSA-qwww-vcr4-c8h2")) {
  throw new Error("GHSA steht weiterhin in ignoreCves");
}

console.log("OPS-003: PASS");
NODE
```

### 2.2 Dokumentationskonsistenz

```bash
rg -n \
  'PR #55 \(offen|PR #55.*CI läuft|ignoreCves|SUPERSEDED im Geltungsbereich|B0-Sequenz-ADR noch nicht geschrieben|origin/main.*5976ae|Offene PRs / Issues.*0 / 0' \
  README.md ROADMAP.md docs plans .claude package.json
```

Jeder verbliebene Treffer muss entweder entfernt oder ausdrücklich als historisch gekennzeichnet sein.

### 2.3 Diff-Hygiene

```bash
git diff --check origin/main..HEAD
git diff --stat origin/main..HEAD
git ls-files --eol package.json
git diff --exit-code origin/main..HEAD -- pnpm-lock.yaml
```

Der Lockfile muss unverändert bleiben.

### 2.4 Security Audit

```bash
pnpm audit --audit-level high
pnpm audit --audit-level high --ignore GHSA-qwww-vcr4-c8h2
```

Der erste Befehl prüft, ob `auditConfig.ignoreGhsas` tatsächlich funktioniert. Der zweite reproduziert den aktuellen CI-Vertrag.

---

## 3. Phase 3 — Push nach origin/main

### 3.1 Vorbedingung

- Alle Gates aus Phase 2 müssen PASS sein
- Kein uncommitteter Diff außer dieser Plan-Datei

### 3.2 Push

```bash
git push origin main
```

### 3.3 Erwartetes Ergebnis

- `origin/main` zeigt auf `9cc7e44`
- GitHub zeigt die Reconciliation-Änderungen im Default-Branch
- OPS-003 ist auf GitHub-`main` behoben

---

## 4. Phase 4 — GitHub-Tracker nach dem Push abgleichen

| Issue | Maßnahme nach Push |
|---|---|
| **#37 RC2 Epic** | Neue Baseline (`9cc7e44`) und getrennte Streams dokumentieren; Epic offen lassen |
| **#42 Security** | OPS-003-Nachweis und Audit-Ergebnis hinterlegen; bei vollständigem PASS schließen |
| **#44 Committee Review** | `REVIEW_COMPLETE`, `DECISION_NO_GO`, `AWAITING_STAGING_REVIEW`; offen lassen |
| **#49 Sequencing ADR** | ADR 0017 als erfüllt dokumentieren; Guided-Masterplan-Sperre separat erhalten |

### Besonders wichtig bei #49

ADR 0017 ändert die bisherige Sequenzentscheidung teilweise:

- Full Analysis V2/V3 darf parallel und isoliert vorbereitet werden.
- V1 bleibt unverändert.
- Kein Default-Switch.
- Guided Masterplan bleibt bis Stable v0.3.0 gesperrt.
- Forschung/Plattformausbau bleibt außerhalb des aktuellen Scopes.

---

## 5. Phase 5 — Danach zwei parallele Arbeitsstränge

Nur **zwei** aktive Streams; der dritte Slot bleibt für Sicherheits-/CI-Fixes frei.

### Stream A — RC2 Operational Readiness

1. genehmigten privaten Staging-Host festlegen,
2. Host-Preflight für #39,
3. bekannten RC1-Stand deployen,
4. RC2-Kandidat per festem Image-Digest deployen,
5. Backup und isolierten Restore ausführen,
6. vollständigen Rollback-Ablauf ausführen,
7. Health- und Profil-Smoke,
8. A11y-/Gerätematrix abschließen,
9. Committee-Re-Review,
10. erst danach RC2-Versionierung und Tag.

Solange kein Host-Proof existiert:

```text
RELEASE_DECISION=NO_GO
OPERATIONAL_ACCEPTANCE=BLOCKED_BY_STAGING
RC2_RELEASED=NO
```

### Stream B — Full Analysis V2/V3

Nach Push von ADR 0017 als separater Epic:

1. **Welle 0:** Vertrags-ADRs, Feature Flags, Methodenrouting, API-Grenzen.
2. **Welle 1:** `/api/v2/meta` und `/api/v2/profiles/calculate`.
3. **Welle 2:** Fact Package und Knowledge V3.
4. **Welle 3:** V3-Agent, 18 Abschnitte, Idempotenz und Analysehistorie.
5. **Welle 4:** Neun UI-Tabs, `reportId`-gebundene Notizen und Follow-ups, PDF/Print.
6. **Welle 5:** Evaluation, Closed Beta, Opt-in, späterer Default-Gate.

Harte Grenzen:

```text
/api/v1 unverändert
kein V1-Schema-Drift
kein automatischer Default-Switch
Guided Masterplan nicht implementieren
keine Research-Preview-Erweiterung
```

---

## 6. Unmittelbare Ausführungsreihenfolge

1. Commit-Inhalte verifizieren (Phase 1).
2. Semantische Gates ausführen (Phase 2).
3. Bei PASS: `git push origin main` (Phase 3).
4. Nach erfolgreichem Push: Issues #37, #42, #44 und #49 reconciliieren (Phase 4).
5. RC2-Staging und Full-Analysis-Welle 0 als getrennte Streams starten (Phase 5).
