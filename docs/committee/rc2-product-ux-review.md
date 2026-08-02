# RC2 Committee — Produkt, UX & Accessibility

> **Perspektive:** Produkt / UX / a11y  
> **Stand:** 2026-08-02

## Findings

| ID | Severity | Finding | Evidenz | Empfehlung | Release-Blocker? |
|----|----------|---------|---------|------------|------------------|
| UX-01 | Info | Playwright-Matrix (Chromium/Firefox/WebKit/mobile) auf main grün mit CI=true | phase1-web-e2e-rerun.log; CI Web job | Vor RC2-Tag wiederholen | Nein |
| UX-02 | Info | Automatisierte WCAG-Tags im Primary Flow ohne Violations (E2E) | `e2e/profile-flow.spec.ts` axe test PASS | Closed Beta für manuelle Screenreader | Nein für RC2 |
| UX-03 | Medium | Closed Beta mit realen Geräten/Testern nicht durchgeführt | Issue #46 | Vor Stable | Ja für **Stable**, nein für RC2-Tag |
| UX-04 | Low | react-router HIGH deferred (Major) | dependency-decision-rc2 | Gezielter Upgrade-Stream | Nein mit dokumentiertem Owner |

## Akzeptiertes Restrisiko

- Axe deckt nicht alle Screenreader-Pfade; Residualrisiko für Closed Beta getrackt (#43/#46).

## Verdict

```text
CRITICAL_OPEN=0
HIGH_OPEN=0_FOR_RC2
CLOSED_BETA=NOT_STARTED
```
