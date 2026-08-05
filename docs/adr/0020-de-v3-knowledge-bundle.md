# ADR 0020 — Unveränderlichkeit von de-v2.json; de-v3.json als neues Bundle

> **Status:** ACCEPTED
> **Datum:** 2026-08-05
> **Kontext:** Das Wissenspaket `de-v2.json` (`KnowledgeBundleV2`, `bundle_id="numra-knowledge-de-v2"`) wird aktiv von `/api/v1/analyses/*` verwendet und in bestehenden Berichten über `provenance.knowledge_bundle` referenziert. Der neue `pythagorean-v2`-Berechnungsvertrag benötigt erweiterte `result_contexts` (`life_path_primary`, `life_path_secondary` als getrennte Werte), die das V2-Modell nicht abbilden kann.
> **Betrifft:** Wissen, Versionierung, Abwärtskompatibilität

---

## Entscheidung

1. **`de-v2.json` bleibt unverändert und byte-identisch.** Bestehende Berichte referenzieren dieses Bundle und müssen ihre `knowledge_refs` weiterhin auflösen können.

2. **`de-v3.json` entsteht als eigenständiges, neues Bundle:**
   - `bundle_id = "numra-knowledge-de-v3"`
   - `version = "v3"`
   - `method_system = "pythagorean-v2"`
   - Erweiterte `ResultContextV3`-Werte inkl. `life_path_primary`, `life_path_secondary`

3. **Explizite Bundle-Auswahl**, nicht implizit über Profilschema:

```python
bundle = load_knowledge_bundle_v3(
    locale="de",
    bundle_id="numra-knowledge-de-v3",
)
```

Die Profil- und Wissensversion sind gemäß der Versionsarchitektur **unabhängige Achsen**.

4. **Paralleles V3-Wissensmodell:**

```
src/numerology_knowledge/models.py       unverändert (V2)
src/numerology_knowledge/loader.py       unverändert (V2)
src/numerology_knowledge/models_v3.py    neu (V3)
src/numerology_knowledge/loader_v3.py    neu (V3)
src/numerology_knowledge/data/de-v3.json neu
```

5. **Fail-closed-Resolver:** Der V3-Resolver bricht bei null Treffern und bei mehreren gleichwertigen Treffern ab — kein stilles `candidates[0]`.

## Konsequenzen

- **Positiv:** Bestehende Berichte und V1-Analyse-Pipeline bleiben voll funktionsfähig.
- **Positiv:** Wissensinhalte können unabhängig vom Profilschema versioniert werden.
- **Negativ:** Zwei Wissens-Bundles müssen parallel gepflegt werden (V2 + V3).

## Verweise

- ADR 0018 — V2-Stack-Isolation
- `src/numerology_knowledge/models.py` — `KnowledgeBundleV2`, `KnowledgeEntryV2`
- `src/numerology_knowledge/data/de-v2.json` — bestehendes Bundle
