# Numra — kumulativer, noch nicht getaggter Quellstand

> **Stand:** 27. Juli 2026
> **Quellintegration:** PR #10 auf `main`
> **Release-Status:** kein neuer Tag; jüngstes veröffentlichtes Release ist `v0.1.3`

## Integrierter Umfang

Der aktuelle `main`-Quellstand enthält kumulativ:

- vollständiges pythagoreisches Profil und deterministische Zyklen,
- versioniertes Wissen, regelbasierte Interpretation und Safety-Gates,
- zustandslose FastAPI und eine React/Vite/TypeScript-PWA,
- lokale IndexedDB-Speicherung, Verschlüsselung, PDF und Offline-Lesezugriff,
- optionalen, pseudonymisierten DeepSeek-Adapter,
- einen gehärteten Docker-/Nginx-Stack mit Release-/Rollback-Automation.

Der anschließende Abschlussreview identifizierte Korrekturen, die vor einer
Releasefreigabe ebenfalls in diesen unreleased Stand gehören:

- serverseitige Neuberechnung und Integritätsprüfung aller an LLM-Endpunkte
  gesendeten Profile,
- getrennte Core-/Active-Name-Reifezahlen einschließlich Active-Trace,
- wiederherstellbare Voll-Exporte auch zwischen unterschiedlich geschützten
  lokalen Bibliotheken,
- erneute Reportvalidierung und PII-Sperren für Rückfragen,
- geräteweite Tageskontingente sowie eine gehärtete Proxy-Vertrauenskette,
- echte Redis-Readiness und explizite Thinking-/Sampling-Provenienz,
- der aktuelle Providervertrag `deepseek-v4-pro`.

Der öffentliche Launch ist nicht Bestandteil dieser Quellintegration.

## Warum noch kein Release-Tag existiert

ADR 0006 schreibt die Reihenfolge `0.1.4` → `0.1.5` → `0.2.0` → `0.3.0`
und eigenständige Release-Gates vor. PR #10 integrierte diese Arbeitsstände
kumulativ in einem einzigen Quellmerge:

- `pyproject.toml` trägt formal `0.1.5`,
- der Funktionsumfang reicht bis in die geplanten Bereiche `0.2.0`/`0.3.0`,
- die Zwischenstände wurden nicht jeweils separat auf `main` getaggt und
  freigegeben.

Eine nachträgliche Versionsbehauptung wäre deshalb willkürlich. Der nächste
Tag wird erst festgelegt, wenn die Governance entweder die kumulative
Releaseversion bestätigt oder eine nachvollziehbare neue Sequenz beschließt.
Schema- und Methodenverträge werden dafür nicht unnötig verändert.

## Externe Launch-Gates

Folgende Werte und Freigaben fehlen weiterhin und werden nicht erfunden:

- DeepSeek API-Key und rechtliche Drittlandtransfer-Freigabe,
- bestätigtes VPS-Ziel,
- Domain, DNS und TLS-Kontaktadresse,
- Betreiberanschrift, Impressums- und Datenschutzkontakt,
- ausdrückliche Entscheidung für einen öffentlichen Launch.

Bis dahin bleibt DeepSeek standardmäßig deaktiviert und es erfolgt kein
öffentliches Deployment.
