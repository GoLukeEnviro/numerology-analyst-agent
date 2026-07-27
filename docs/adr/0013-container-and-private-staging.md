# ADR 0013: Containerstack und privates Staging

- Status: akzeptiert
- Datum: 2026-07-26

## Entscheidung

Numra wird als drei Services ausgeliefert:

- `gateway`: statische PWA und interner Nginx-Reverse-Proxy
- `api`: zustandslose FastAPI-Anwendung
- `redis`: ausschließlich flüchtige Quoten-Zähler

Nur das Gateway bindet einen Host-Port, und zwar
`127.0.0.1:8080`. API und Redis liegen in einem internen Docker-Netz. Alle
Container verwenden ein read-only Root-Dateisystem, entfernen Linux
Capabilities und setzen `no-new-privileges`. API, Gateway und Redis laufen
unter expliziten Nicht-root-UIDs; Redis verwendet ausschließlich ein tmpfs.

Basisimages sind per Multi-Arch-Digest gebunden. Anwendungsimages tragen beim
Deployment den vollständigen Commit-SHA. Uvicorn- und Gateway-Access-Logs sind
deaktiviert.

Vor Verfügbarkeit einer geprüften Domain ist nur privates Staging über eine
SSH-Portweiterleitung erlaubt. Der Host-Port 8080 wird nicht in einer Firewall
oder einem öffentlichen Listener freigegeben.

## Folgen

- Ein Healthcheck-Fehler verhindert, dass abhängige Services als bereit gelten.
- Redis-Neustarts löschen sämtliche Quoten; das ist beabsichtigt.
- Lokale Profile existieren nicht im Stack und werden nicht gesichert.
- CI baut den echten Stack und wartet auf alle Healthchecks.
- TLS-Terminierung, Domain und HSTS bleiben Aufgabe des Host-Nginx in Schritt
  12.
