# ADR 0005 — Current Package Layout and Schema Source

> **Status:** Akzeptiert (26. Juli 2026)
> **Kontext:** Der Master-Vertrag spezifiziert `apps/cli` und `apps/api` als Schnittstellen-Pfade. Die tatsächliche Implementierung weicht ab.
> **Betrifft:** Paketstruktur, Schema-Quelle

---

## Entscheidung

1. **CLI** liegt unter `src/numerology_cli/`, nicht `apps/cli/`.
2. **API-Vertrag** liegt unter `src/numerology_api/`, nicht `apps/api/`.
3. **Versionierte JSON-Schemas** liegen unter `src/numerology_api/schemas/`.
4. Dieser Pfad ist die **Source of Truth** für installierbare Schemas.
5. Es gibt **keine parallele manuell gepflegte zweite Schemaquelle**.

## Begründung

- `src/`-Layout ist idiomatisch für Python-Projekte mit `hatchling`-Build.
- Schemas im Wheel-Paket ermöglichen `importlib.resources`-Zugriff zur Laufzeit.
- Eine einzige Schema-Quelle verhindert Drift zwischen Build-Artefakt und manueller Kopie.

## Konsequenzen

- Der Master-Vertrag wird in diesem Punkt nicht 1:1 umgesetzt.
- Zukünftige ADRs und Dokumente referenzieren die tatsächlichen Pfade.
- Eine Migration zu `apps/` ist nicht geplant, aber bei Bedarf durch ADR änderbar.
