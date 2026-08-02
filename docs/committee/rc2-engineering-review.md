# RC2 Committee — Engineering & Architecture

> **Perspektive:** Engineering / Architektur  
> **Stand:** 2026-08-02  
> **Code-Baseline (Gates):** `5976ae2299059451461f634cb89f525151fda8b2`  
> **main nach Docs:** `8b0c711e510ebfb19f5cc814edab9d08e005c4eb`  
> **Methode:** rollenbasierte Analyse mit Repo-Evidenz (kein fiktives Gremium)

## Findings

| ID | Severity | Finding | Evidenz | Empfehlung | Release-Blocker? |
|----|----------|---------|---------|------------|------------------|
| ENG-01 | Medium (fixed) | `rollback-rehearsal.sh` erzeugte Zeitstempel-Tags, die `rollback.sh` (`^[0-9a-f]{40}$`) ablehnt | Script-Diff + Contract-Test | Fix: Git-SHA-Tags, `NUMRA_RELEASE_DIR`, Health-Retry; lokal PASS | Nein nach Merge |
| ENG-02 | Info | Frische Gates auf main grün (Python, Determinismus, Web E2E, Container) | CI 30766934433; lokale phase1-Logs | Beibehalten vor jedem RC-Tag | Nein |
| ENG-03 | High (ops) | Privates Staging auf genehmigtem Host nicht ausgeführt | `docs/operations/vps-inventory-2026-07-26.md`; Staging-Acceptance BLOCKED | Host zuweisen, dann Deploy/Restore/Rollback | **Ja** für RC2-Tag |
| ENG-04 | Low | Frontend-Coverage-Gate und Modularisierung nach PR #34 | CI Web quality job | Keine Aktion | Nein |

## Akzeptiertes Restrisiko

- Determinismus-Hash-Vertrag und Golden-Tests decken den Rechenkern ab; verbleibendes Risiko liegt in Betriebsnachweisen, nicht in der Kernlogik.

## Verdict dieser Perspektive

```text
CRITICAL_OPEN=0
HIGH_OPEN=1 (ENG-03 private staging host)
ENGINEERING_OK_FOR_CODE=YES
ENGINEERING_OK_FOR_RC2_TAG=NO_UNTIL_STAGING
```
