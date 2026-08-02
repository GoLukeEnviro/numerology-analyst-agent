# RC2 Committee — Findings-Synthese

> **Stand:** 2026-08-02  
> **Quellen:** `rc2-*-review.md`

## Aggregate

| Severity | Open | Accepted with owner | Closed/Info |
|----------|------|---------------------|-------------|
| Critical | 0 | 0 | — |
| High | 1 (private staging host missing — ENG-03) | 0 | Public launch High only for public path |
| Medium | 2 (rollback tag contract fix; closed beta for stable) | 1 (react-router defer #42) | — |
| Low/Info | — | — | Multiple |

## Release-Blocker für `v0.3.0-rc.2` Tag

1. **ENG-03:** Genehmigter privater Staging-Host + Deploy/Health/Profile  
2. **Restore + Rollback** real auf diesem Host (nicht nur Skript-Existenz)  
3. **ENG-01:** Rollback-Rehearsal SHA-Tag-Fix gemergt und lokal/remote geübt  

## Nicht-Blocker für deterministischen RC2 (LLM off)

- Legal LLM transfer (SAF-04) — LLM bleibt aus  
- Closed Beta (UX-03) — erst vor Stable  
- Public launch checklist (SAF-02) — separater GO  

## Owner-Map

| Finding | Owner |
|---------|-------|
| Staging host | Betreiber / Operator |
| Rollback SHA fix | Engineering (PR in Flight) |
| react-router defer | #42 Release-Orchestrator |
| Closed beta | #46 |
