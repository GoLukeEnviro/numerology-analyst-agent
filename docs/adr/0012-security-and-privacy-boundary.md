# ADR 0012: Security- und Datenschutzgrenze

- Status: akzeptiert
- Datum: 2026-07-26

## Entscheidung

FastAPI erzwingt eine exakte Origin-Allowlist für verändernde Requests, ein
konfigurierbares Request-Bodylimit, stabile Feldgrenzen, `no-store` und
Browser-Security-Header. Logs enthalten nur begrenzte Request-Metadaten;
Fehlermeldungen, Request-/Response-Bodies, Querystrings und Stacktraces werden
nicht protokolliert.

Die Web-App rendert keinen fremden HTML-Inhalt. Ihre Produktions-CSP wird am
Gateway gesetzt und erlaubt nur selbst gehostete App-Assets und die eigene API.
Service Worker und Reverse Proxy speichern keine personenbezogenen
API-Antworten.

LLM-Eingaben werden pseudonymisiert, als Daten gekapselt und gegen typische
Rollen-, Regelüberschreibungs- und Jailbreak-Muster geprüft. Provider-Ausgaben
müssen Schema-, Fakten-, Quellen- und Sprachregeln erfüllen oder werden
verworfen.

## Folgen

- Der öffentliche Launch setzt HTTPS, geprüfte Rechtstexte und eine bestätigte
  Drittlandtransfergrundlage voraus.
- Debugging stützt sich auf Korrelations-ID und reproduzierbare Requests, nicht
  auf gespeicherte Nutzdaten.
- Bodylimit, Header, Origin-Regel, Redaction und Safety-Gates sind automatisiert
  getestet; Lockfiles werden in CI auf bekannte Schwachstellen geprüft.
