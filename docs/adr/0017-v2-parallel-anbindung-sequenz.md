# ADR 0017: V2-Parallel-Entwicklung — Sequenzielle Anbindung an RC2-Releasepfad

> **Status:** ACCEPTED
> **Datum:** 2026-08-04
> **Kontext:** Drei parallele Programme existieren:
>   - (A) RC2 Release Readiness (Staging, Operational Acceptance)
>   - (B) pythagorean-v2 + Full Analysis V2/V3 (Backend-Wellen 1-3, Web-Welle 4)
>   - (C) V2 Guided Masterplan (Nutzer-geführte Eingabe)

---

## Entscheidung

- **A** bleibt primärer Releasepfad.
- **B** darf parallel entwickelt werden, aber ausschließlich unter `/api/v2`, hinter
  Feature Flag, V1 unverändert, kein Default-Wechsel, nicht zwingend Bestandteil des
  RC2-Tags.
- **C** bleibt bis nach Stable `v0.3.0` gesperrt.

## Verzahnungsregel

Solange Strang A offen ist, kein V2-Merge nach `main`; Welle 4 (Web) erst nach dem
RC2-Schnitt.

## Konsequenzen

Klare Trennung der Entwicklungsstränge, keine Blockade von RC2 durch V2-Arbeiten.

## Verweise

- ADR 0016 — V2 User-Owned Masterplan Boundary (SUPERSEDED im Geltungsbereich der
  Sequenzentscheidung durch ADR 0017)
- `docs/plans/numra-full-analysis-v2-v3.md` — Full-Analysis-Plan V2/V3 (kanonisiert am
  2026-08-04)
- `.claude/plans/dapper-fluttering-kazoo.md` — Strang-B-Planung
