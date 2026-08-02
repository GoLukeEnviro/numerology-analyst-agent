# RC2 Committee — Release Decision

> **Stand:** 2026-08-02  
> **Entscheidungstyp:** formal, nachvollziehbar  
> **Perspektiven:** Engineering, Methodologie, Forschung, Safety/Privacy, Produkt/UX

## Gate-Werte

```text
CRITICAL_FINDINGS_OPEN=0
HIGH_FINDINGS_OPEN=1
HIGH_FINDINGS_ACCEPTED_WITH_OWNER=0
HIGH_FINDINGS_BLOCKING=private_staging_host (ENG-03)
MEDIUM_OPEN=rollback_sha_contract_fix_in_flight;closed_beta_for_stable_only
RELEASE_DECISION=NO_GO
DETERMINISTIC_CODE_QUALITY=PASS
RC1_TAG_UNCHANGED=YES
RC1_TAG_SHA=21ba56ed0d918cea7c60090bcc50937adc16269a
```

## Begründung

Der **Code-Stand** auf main ist für den deterministischen Pfad (LLM off) quality-gate-grün.  
Der **Release-Kandidat `v0.3.0-rc.2` darf nicht getaggt werden**, solange:

1. kein genehmigter privater Staging-Host Deploy/Health/Profile beweist,  
2. Backup create → validate → restore → re-smoke fehlt,  
3. Rollback-Rehearsal auf dem Host (mit SHA-kompatiblen Tags) fehlt.

Skript-Existenz und reiner Desktop-Docker-Smoke ersetzen den Host-Vertrag nicht.

## Bedingungen für Wechsel zu `GO` oder `GO_WITH_CONDITIONS`

| # | Bedingung | Nachweis |
|---|-----------|----------|
| 1 | Staging-Host vom Betreiber benannt | SSH-Alias in Inventar/Acceptance |
| 2 | Deploy pinned SHA, LLM=false | Digests + health + profile |
| 3 | Restore PASS | Acceptance-Report |
| 4 | Rollback PASS | Acceptance-Report |
| 5 | Rollback-SHA-Fix auf main | PR merge + Rehearsal-Log |
| 6 | Keine neuen Critical/High im Code | frische Gates |

Optional für deterministischen RC2: `REAL_PROVIDER_SMOKE=BLOCKED_LEGAL` ist akzeptabel.

## Explizit nicht freigegeben

- Public deployment  
- Stable `v0.3.0`  
- V2 Guided Masterplan Implementierung  
- Bewegung von Tag `v0.3.0-rc.1`

## Signatur (rollenbasierte Synthese)

```text
DECISION_OWNER=Lead Orchestrator (role-based sequential review)
HUMAN_LEGAL_OPERATOR_GATES=EXTERNAL
DATE=2026-08-02
```
