# Accessibility- und Geräte-Matrix (RC2-Vorbereitung) — 2026-08-02

> **Bezug:** Issue #43 · Epic #37  
> **Mess-SHA (E2E):** `5976ae2299059451461f634cb89f525151fda8b2`  
> **Lauf:** `pnpm web:e2e` mit `CI=true` (saubere Ports 8000/5173)

## Playwright-Projekte

| Projekt | Ergebnis | Evidenz |
|---------|----------|---------|
| chromium | PASS (5 tests) | phase1-web-e2e-rerun.log |
| firefox | PASS | phase1-web-e2e-rerun.log |
| webkit | PASS | phase1-web-e2e-rerun.log |
| mobile-chrome | PASS | phase1-web-e2e-rerun.log |
| mobile-webkit | PASS | phase1-web-e2e-rerun.log |

Gesamt: **25 passed**, EXIT=0, Dauer ~176 s.

## Abgedeckte Flows (automatisiert)

- Profil berechnen, speichern, PDF-Export  
- Persistenz nach Browser-Restart  
- Offline-Restart (WebKit skipped by design)  
- Light Theme + Installationshinweise  
- Axe WCAG 2.2 AA Tags im Primary Flow (Home, Analyse, Atlas)

## Nicht abgedeckt (Closed Beta #46)

- Reale iOS/Android-Geräte außerhalb Playwright-Emulation  
- Screenreader manuell (VoiceOver/TalkBack)  
- Physische Tastatur auf allen Geräten mit echten Usern  

## Residualrisiko

| Risiko | Owner | Status |
|--------|-------|--------|
| Manuelle a11y-Lücken | #43 / #46 | getrackt |
| react-router advisory | #42 | deferred, dokumentiert |

## Gate

```text
PLAYWRIGHT_MATRIX=PASS
AXE_PRIMARY_FLOW=PASS
MANUAL_DEVICE_BETA=NOT_STARTED
P0_A11Y_BLOCKERS=0
```
