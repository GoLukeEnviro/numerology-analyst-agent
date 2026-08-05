# ADR 0025 — OpenAPI-Artifact-Strategie: numra-api.json + v1-contract.json

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Der bestehende OpenAPI-Exporter (`scripts/export_openapi.py`) schreibt die Spezifikation fest nach `openapi/numra-v1.json`. Die Web-App (`apps/web/package.json`, `pnpm web:generate-api`) generiert ihre Typen aus dieser Datei. Sobald `/api/v2/*` in dieselbe FastAPI-App aufgenommen wird, enthielte `numra-v1.json` auch V2-Pfade — der Dateiname wäre irreführend und das Dokument nicht mehr byte-identisch.
> **Betrifft:** API-Dokumentation, CI/CD, Web-App

---

## Entscheidung

### Zwei Ausgabe-Artefakte

```
openapi/numra-api.json              ← vollständiges Dokument (V1 + V2)
openapi/contracts/v1-contract.json  ← V1-Schema-Closure (nur V1-Pfade, rekursiv)
```

### v1-contract.json — rekursive Schema-Closure

Ein reiner Pfad-Snapshot reicht nicht: Ein V1-Pfad kann dieselbe `$ref`-Adresse verwenden, während das referenzierte Schema unter `components.schemas` verändert wurde. `v1-contract.json` enthält daher:

- ausgewählte V1-Pfade
- zugehörige Operationen
- **rekursiv alle referenzierten `components.schemas`** (Schema-Closure)
- relevante Responses, Security Schemes, Parameter
- kanonisch sortierte Serialisierung

### Umstellung der kritischen Pfade

- `scripts/export_openapi.py` schreibt nach `openapi/numra-api.json` (nicht mehr `numra-v1.json`)
- `apps/web/package.json`: `pnpm web:generate-api` liest aus `openapi/numra-api.json`
- Die Web-App generiert ihre Typen aus dem gemeinsamen API-Dokument

### Was nicht verlangt wird

„Gesamte OpenAPI-Datei byte-identisch" — stattdessen präzise:

> Request-/Response-Schemas und Operations der bestehenden `/api/v1/analyses/*`- und `/api/v1/meta`-Pfade bleiben unverändert (inkl. referenzierter Schema-Closure).

## Konsequenzen

- **Positiv:** Ein gemeinsames API-Dokument für die Web-App.
- **Positiv:** V1-Vertrag separat und maschinell prüfbar.
- **Neutral:** `numra-v1.json` wird obsolet (bleibt aus Rollback-Gründen bestehen).

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `scripts/export_openapi.py` — bestehender Exporter
- `apps/web/package.json` — `pnpm web:generate-api`
