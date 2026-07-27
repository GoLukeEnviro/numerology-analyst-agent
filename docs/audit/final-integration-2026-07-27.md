# Numra — finales Integrationsaudit

> Stand: 27. Juli 2026
>
> Produktintegration auf `main`: `2a514e926912ba2cdb41ffb08ea083e04082cee2`
>
> PWA-Integration: [PR #10](https://github.com/GoLukeEnviro/numerology-analyst-agent/pull/10)
>
> Abschluss-Hardening: [PR #11](https://github.com/GoLukeEnviro/numerology-analyst-agent/pull/11)
>
> CodeQL-Baseline: [PR #12](https://github.com/GoLukeEnviro/numerology-analyst-agent/pull/12)

## Ergebnis

Der geplante Numra-Quellstand ist kontrolliert über geschützte Pull Requests
auf `main` integriert. Es erfolgten weder ein Direct-Push auf `main` noch ein
Force-Push oder ein öffentliches Deployment. Der projektlokale Worktree und
der lokale Backup-Branch bleiben erhalten.

PR #11 schloss die im unabhängigen Abschlussreview gefundenen P0-/P1-Risiken:

- kanonische serverseitige Neuberechnung vor jedem LLM-Aufruf,
- HMAC-gebundene und erneut validierte Berichtskontexte,
- pseudonymisierte Provider-Payloads und PII-Sperren,
- geräteweite und IP-HMAC-basierte Tageskontingente,
- gehärtete Proxy-Vertrauenskette,
- getrennte Core-/Active-Reifezahlen und vollständiger Active-Trace,
- unveränderte lokale V2-Lesbarkeit mit kontrollierter V3-Neuberechnung,
- übertragbarer V2-Export und dokumentierte V1-Vault-Wiederherstellung,
- echte Redis-Readiness sowie LLM-fail-closed,
- automatisierte WCAG-2.2-AA-Prüfung mit axe.

Nach dem finalen Review waren keine P0-/P1-Befunde offen.

## Abnahmebelege

Lokale Verifikation des finalen Funktionsstands:

- 207 Python-Tests,
- Engine-Coverage 97,12 Prozent,
- Gesamt-Coverage 93,02 Prozent,
- Ruff Format/Lint und Mypy strict,
- Schema-, OpenAPI- und Beispiel-Driftchecks,
- `pip-audit` ohne bekannte Python-Schwachstelle,
- 34 Vitest-/React-Testing-Library-Tests,
- ESLint, TypeScript strict, PWA-Produktionsbuild und Bundle-Budget,
- axe/WCAG 2.2 AA auf Chromium, Firefox, WebKit und beiden Mobile-Profilen,
- realer Docker-Build mit drei gesunden Services,
- Health-, Berechnungs-, Origin-, Header-, Nicht-root/read-only-,
  Log-Redaktions- und LLM-disabled-Smokes.

GitHub-Abnahme:

- [PR-#11-CI](https://github.com/GoLukeEnviro/numerology-analyst-agent/actions/runs/30302799545):
  alle vier Required Checks grün,
- [Post-Merge-main-CI](https://github.com/GoLukeEnviro/numerology-analyst-agent/actions/runs/30303170910):
  alle vier Jobs einschließlich vollständiger Linux-Browsermatrix grün.

Ein erster Web-Job scheiterte ausschließlich an einem inkonsistenten externen
Google-APT-Mirror während des Playwright-Setups. Der unveränderte Rerun war
vollständig grün.

## GitHub- und Security-Status

`main` erzwingt weiterhin:

1. Quality Gates,
2. Package Smoke,
3. Web Quality,
4. Container Build and Health Smoke.

Strict Status Checks und lineare Historie sind aktiv. Force-Push und
Branch-Löschung sind deaktiviert. Eine Reviewpflicht wurde bewusst nicht
aktiviert, da kein dauerhaft verfügbarer unabhängiger Reviewer garantiert ist.

Secret Scanning meldete keine Funde. Der React-Router-Hinweis
`GHSA-qwww-vcr4-c8h2` betrifft ausschließlich nicht verwendete instabile
RSC-/Server-Action-Pfade und ist mit dokumentierter Begründung als toleriertes
Risiko klassifiziert. Die Behebung erfordert den separat zu validierenden
Major-Upgrade auf React Router 8.3.0. PR #12 ergänzt CodeQL zunächst als
nicht verpflichtende Baseline.

## Versions- und Releaseentscheidung

Das jüngste veröffentlichte Release bleibt `v0.1.3`.

ADR 0006 verlangt die sequenzielle Folge `0.1.4` → `0.1.5` → `0.2.0` →
`0.3.0`. Der integrierte Quellstand vereint diese geplanten Funktionsbereiche,
während `pyproject.toml` formal `0.1.5` trägt. Eine einzelne nächste
Produktversion ist daraus nicht normativ eindeutig ableitbar. Deshalb wurde
kein willkürlicher Tag und kein GitHub-Release erzeugt. Diese Entscheidung
blockiert weder Quellintegration noch lokales oder privates Staging.

## DeepSeek und öffentlicher Launch

Der DeepSeek-Adapter ist mit `deepseek-v4-pro`, strukturiertem JSON,
Thinking/high, maximal 8.192 Ausgabetokens, Retry sowie Claims-/Safety-Prüfung
implementiert. DeepSeek bleibt standardmäßig deaktiviert. Ein lokaler
Provider-Smoke fand nicht statt, weil keine projektlokale Env-Datei vorlag.

Folgende externe Werte und Freigaben fehlen weiterhin:

- DeepSeek API-Key,
- rechtliche Prüfung des Drittlandtransfers,
- bestätigtes VPS-Ziel,
- Domain, DNS und TLS-Kontaktadresse,
- Betreiberanschrift, Impressums- und Datenschutzkontakt,
- ausdrückliche Freigabe für den öffentlichen Launch.

Ohne diese Angaben dürfen weder Provider noch öffentliche Produktion aktiviert
werden.
