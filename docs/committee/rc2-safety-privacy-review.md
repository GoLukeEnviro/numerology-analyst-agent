# RC2 Committee — Safety, Datenschutz & Minderjährigenschutz

> **Perspektive:** Safety / Privacy  
> **Stand:** 2026-08-02

## Findings

| ID | Severity | Finding | Evidenz | Empfehlung | Release-Blocker? |
|----|----------|---------|---------|------------|------------------|
| SAF-01 | Info | LLM default off; Runtime-Marker-Gates für Legal/Transfer | `NUMRA_LLM_ENABLED`; safety runtime_gate; launch-checklist | Keine Dummy-Marker auf echten Hosts | Nein für deterministischen RC2 |
| SAF-02 | High (extern) | Öffentlicher Launch: Betreiber/Recht/DNS/TLS unvollständig | `docs/operations/launch-checklist.md` alle Pflichtzeilen offen | PUBLIC_DEPLOYMENT=NO_GO | Ja für **Public**, nein für privates RC2 |
| SAF-03 | Info | Keine Klarname/Geburtsdatum im DeepSeek-Adapter-Pfad (Design) | Agent-Modelle; README | Live-Smoke nur mit synthetischen Daten | Nein |
| SAF-04 | Medium | Provider-Smoke legal blockiert | LEGAL/TRANSFER nicht confirmed | Deterministisch fortfahren | Nein für RC2 mit LLM off |

## Akzeptiertes Restrisiko

- Ohne öffentliche DNS/TLS bleibt Angriffsfläche auf Loopback/SSH-Tunnel begrenzt.

## Verdict

```text
CRITICAL_OPEN=0
HIGH_OPEN=0_FOR_PRIVATE_RC2
PUBLIC_LAUNCH=NO_GO
```
