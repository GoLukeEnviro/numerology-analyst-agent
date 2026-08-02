# Handoff – Numra post-RC1 → RC2 / Stable 0.3.0

**Aktualisiert:** 2026-08-02  
**Sprache:** Deutsch

---

## Aktueller Bezug (Live-Steuerung)

| Label | Wert |
|-------|------|
| `origin/main` | `5976ae2299059451461f634cb89f525151fda8b2` |
| Version | `0.3.0rc1` |
| Immutable Tag | `v0.3.0-rc.1` → `21ba56ed0d918cea7c60090bcc50937adc16269a` |
| PR #34 / #35 | gemergt (Ship-Hygiene + Audit-Konsolidierung) |
| Issue #32 | geschlossen (über PR #34) |
| Frische Gates 2026-08-02 | PASS (Python, Determinismus, Web+E2E, Container, CI/CodeQL) |
| Staging / Restore / Rollback | **NOT_EXECUTED** |
| Öffentlicher Launch | **NO_GO** |

**Aktuelle Statusquelle:**  
`docs/audit/current-state-numra-post-rc1-2026-08-02.md`  
`ROADMAP.md` (Statusblock V1.6)

**Historisch (nicht extrapolieren):**

- `docs/audit/numra-post-implementation-verification-2026-08-02.md` — Messung vor Merge #34
- `docs/audit/phase-0-gate-2026-08-02.md` / `phase-1-gate-2026-08-02.md` — RC1-Mess-SHA
- `docs/audit/current-state-numra-rc.md` — RC-Vorbereitung 28.07.2026

---

## Kritischer Pfad (Reihenfolge)

```text
Repository-Wahrheit (docs) aktualisieren
→ main frisch verifiziert (done 2026-08-02)
→ private Staging-Abnahme (NUMRA_LLM_ENABLED=false)
→ Backup create + validate + restore + re-smoke
→ Rollback-Rehearsal (baseline → candidate → rollback → redeploy)
→ Committee Review (5 Perspektiven)
→ release/v0.3.0-rc.2 taggen + GitHub-Prerelease
→ Closed Beta (P0/P1 = 0)
→ stable v0.3.0
→ Public Deploy separat GO|NO_GO
→ ADR Post-0.3 Sequenz (V2 erst danach)
```

## Nächste sinnvolle einzelne Maßnahme

1. **[P1]** Betreiber bestätigt **einen** Numra-Staging-SSH-Alias; Preflight
   (`deploy/scripts/preflight.sh`) und deterministisches Deploy des
   aktuellen main-SHA.
2. Parallel (max. 3 Streams, nur nach grünem main): Security-Entscheidung
   zu `react-router` GHSA-qwww-vcr4-c8h2, a11y/Geräte-Matrix, Ops-Readiness-
   Doku — ohne Feature-Scope und ohne V2.

## Harte Grenzen

- Kein Direct-/Force-Push auf `main`
- Tag `v0.3.0-rc.1` niemals bewegen
- Keine Secrets/PII in Git, Issues, Logs
- Keine V2-/Research-/Platform-Implementierung vor stable 0.3.0 + ADR
- Skript vorhanden ≠ ausgeführt
