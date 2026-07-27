# Numra Threat Model

Stand: 2026-07-26

## Schutzgüter

- Namen, Geburtsdaten, lokale Profile, Berichte, Rückfragen und Notizen
- Integrität des deterministischen Rechenkerns und seiner Hashverträge
- Trennung von Berechnungsfakten, Tradition und interpretativen Hypothesen
- LLM-Schlüssel, HMAC-Schlüssel und Deployment-Konfiguration
- Verfügbarkeit der API und Nachvollziehbarkeit über Korrelations-IDs

## Vertrauensgrenzen

```text
Browser / lokale IndexedDB
  │ HTTPS: flüchtige Berechnung
  ▼
Nginx ── FastAPI ── Redis (nur kurzlebige HMAC-Zähler)
                     │
                     └── optional DeepSeek
                         (nur pseudonymisierte Fakten und Wissensauszüge)
```

Die Browserablage ist unter Kontrolle des jeweiligen Geräts. Das öffentliche
Netz, Browser-Erweiterungen, Reverse Proxy, API-Prozess, Redis und externer
LLM-Anbieter sind getrennte Vertrauensbereiche.

## Bedrohungen und Kontrollen

| Bedrohung | Auswirkung | Kontrollen |
|---|---|---|
| Manipulierte oder übergroße Eingabe | Ressourcenverbrauch, unerwartete Berechnung | Pydantic `extra=forbid`, Feldgrenzen, 64-KiB-Bodylimit, Nginx-Limit, deterministische Policy |
| Cross-Origin-Missbrauch | Fremde Website löst API-Aufrufe aus | exakte CORS-Allowlist und zusätzliche Origin-Prüfung für schreibende Methoden |
| XSS / Clickjacking | Diebstahl lokaler Profile | React-Textescaping, keine HTML-Injektion, CSP, `frame-ancestors`, `X-Frame-Options`, selbst gehostete Assets |
| Injection in Logs | PII-Leak oder Log-Forging | keine Bodies, Querystrings oder Antworten; nur begrenzte Metadaten und validierte Korrelations-ID |
| Profilantwort im HTTP-/SW-Cache | Offenlegung auf gemeinsamem Gerät | `Cache-Control: no-store`; Service Worker cached keine API-Routen oder POST-Antworten |
| Browserdiebstahl | Offenlegung lokaler Daten | optional PBKDF2-HMAC-SHA256/AES-GCM, Schlüssel nur im RAM, Auto-Sperre, vollständiges Löschen |
| Prompt Injection | Regelumgehung oder Datenabfluss | Nutztext als Daten im JSON-Kontext, Rollen-/Jailbreak-Filter, unveränderliche Fakten, Schema-/Claim-/Safety-Validierung |
| LLM-Halluzination | Diagnose, Absolutheit oder veränderte Zahl | LLM berechnet nie; zwei fail-closed Validierungsversuche; Quellen- und Zahlenreferenzen müssen bekannt sein |
| Quoten-/IP-Missbrauch | Kosten und Verfügbarkeit | Geräte-/Profilquote plus kurzlebiger IP-HMAC-Tagesschlüssel in Redis |
| Secret-Leak | Provider- oder Infrastrukturzugriff | Pydantic `SecretStr`, root-lesbare Env-Datei, keine Secrets im Image/Repository/Log |
| Supply-Chain-Schwachstelle | Codeausführung über Abhängigkeit | feste Lockfiles, `pip-audit`, `pnpm audit`, reproduzierbare Images mit Commit-SHA |

### Befristete Audit-Ausnahme

`GHSA-qwww-vcr4-c8h2` betrifft laut Advisory ausschließlich React Routers RSC
Framework Mode und die Ausführung von Server Actions. Numra verwendet nur den
deklarativen `BrowserRouter` im statischen Vite-Client, besitzt keine
React-Server-Komponenten und keine Server Actions. Die Registry nennt eine
behobene Version, die dort am 2026-07-26 noch nicht veröffentlicht ist. Nur
diese Advisory-ID wird deshalb im expliziten CI-Auditbefehl befristet
ignoriert; alle übrigen hohen Funde bleiben build-blockierend. Die Ausnahme ist
bei jedem Router-Update zu entfernen beziehungsweise neu zu prüfen.

## Datenschutzprinzipien

- Keine Konten, Profil-CRUD-API oder serverseitige Profilhistorie.
- Berechnungsdaten leben nur für die Dauer eines Requests im Prozess.
- Redis enthält keine Namen, Geburtsdaten, Berichte oder Rückfragen.
- DeepSeek erhält keinen Klarnamen und kein vollständiges Geburtsdatum.
- Die LLM-Funktion ist standardmäßig deaktiviert und erfordert eine gesonderte
  Einwilligung sowie die externe Prüfung des Drittlandtransfers.
- Backups umfassen nur Deployment-Konfiguration, nie Nutzungsprofile.

## Verbleibende Risiken und Launch-Gates

- Ein kompromittiertes Endgerät oder eine bösartige Browser-Erweiterung kann
  entsperrte Inhalte lesen. Numra kann diese lokale Vertrauensgrenze nicht
  vollständig absichern.
- Betreiberidentität, Datenschutzkontakt, Auftrags-/Transfergrundlage für
  DeepSeek und endgültige Rechtstexte müssen vor öffentlichem Launch durch den
  Betreiber beziehungsweise Rechtsberatung bestätigt werden.
- HSTS wird erst nach erfolgreichem HTTPS- und Renewal-Test auf der endgültigen
  Domain aktiviert.
- Neue Abhängigkeiten oder Provider erfordern eine erneute Threat-Model-Prüfung.
