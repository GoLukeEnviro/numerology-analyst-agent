# Numra Platform Expansion Roadmap

> **Status:** Zukunftsvision, keine Implementierung geplant vor Welle 9
> **Beziehung zu V1/V2:** Diese Module gehören NICHT zum nutzergebauten
> Guided Masterplan (siehe `docs/product/numra-v2-guided-masterplan.md`)
> und NICHT zu V1 (`0.3.0rc1` / stabil `0.3.0`). Sie sind eine separate,
> spätere Plattform-Erweiterung mit eigener Roadmap, eigenen ADRs und
> eigener Release-Sequenz (Welle 9+).

---

## 1. Zweck

Dieses Dokument sammelt Ideen für eine spätere Plattform-Erweiterung von
Numra, die über den nutzergebauten Guided Masterplan hinausgehen. Es wurde
aus `docs/product/numra-v2-guided-masterplan.md` ausgelagert (ADR 0016,
Realignment), weil diese Themen dort das Kernbild des nutzergebauten
Entwicklungsplans verwässert hatten. Kein Inhalt dieses Dokuments ist
Implementierungsauftrag.

## 2. Erweiterte Methodensysteme

- **Chaldäische Numerologie** (eigenes Modul, eigener Alphabet-Map).
- **Kabbalistische / Gematria-nahe Systeme** (Hebräisch, Sephiroth-Bezug).
- **Historische und moderne Varianten** (z. B. moderne Reduktion, Y-Regel).
- Plugin-/Methodenschnittstelle: Jede Methode bekommt eine eigene Version
  (z. B. `chaldean-v1`), eigenen Hash und eigene Wissenspakete. Keine
  Vermischung mit `pythagorean-v1`.

## 3. Mehrsprachigkeit

- Wissenspakete je Locale (`en-v1`, `fr-v1`, etc.).
- Lokalisierung der UI, CLI, API-Beschreibungen und Berichte.
- Methodenspezifische Alphabet-Maps je Sprache (z. B. Umlaut-Behandlung).
- Bestehendes `de-v1`/`de-v2` bleibt kanonisch für Deutsch.

## 4. Forschungs-Community-Features

- **Präregistrierung** von Hypothesen vor der Datenerhebung.
- **Geteilte, anonymisierte Datensätze** (DuckDB + Parquet).
- **Nullmodelle und Permutationstests** als Standard-Pipeline.
- **Multiple-Testing-Korrektur** (FDR, Bonferroni) als Pflicht.
- Open-Science-Export (reproduzierbare Analyse-Snapshots).
- Komitee-gesteuerte Begutachtung empirischer Behauptungen.

## 5. Benutzerkonten und Cloud-Synchronisation

- Optionale, opt-in cloudbasierte Profilsynchronisation.
- Ende-zu-Ende-Verschlüsselung für synchronisierte Daten.
- Mehrgeräte-Nutzung ohne Verlust der lokalen-first-Garantie.
- Explizite Trennung: lokale Daten bleiben primär, Cloud ist optional.

## 6. Fortgeschrittene Agenten-Workflows

- Vektor-Retrieval über das versionierte Wissen (nur für Empfehlung, nicht
  für Berechnung — Determinismus bleibt unangetastet).
- Tool-Calls (mehrstufige Agenten-Interaktion) — klar abgegrenzt vom
  one-shot-RC1-Modell.
- Bewertete, menschlich kuratierte Interpretationsvorschläge.
- Personalisierte Lernpfade (pädagogische Erklärungen).

## 7. Zukunftsdomänen (separat zu bewerten)

- Astrologie, Human Design, Enneagramm — als eigenständige Module mit
  eigenen Methodenversionen, nicht als Numerologie-Erweiterung und nicht
  als Teil des Guided Masterplan.

## 8. Verhältnis zum Guided Masterplan

Der Guided Masterplan (`docs/product/numra-v2-guided-masterplan.md`) ist ein
nutzergebauter Reflexions- und Zielsetzungsprozess auf Basis des
numerologischen Profils. Er benötigt keines der hier gelisteten Module, um
vollständig zu funktionieren. Sollte ein hier gelistetes Modul (z. B.
Mehrsprachigkeit) später gebraucht werden, um den Guided Masterplan einem
neuen Nutzerkreis zugänglich zu machen, geschieht das über eine eigene,
separat freigegebene Erweiterung dieser Roadmap — nicht durch stille
Vermischung in die Guided-Masterplan-Spezifikation.

## 9. Entscheidungsprozess

Ein formelles Implementierungsprogramm für eines dieser Module wird erst
nach stabil freigegebenem `0.3.0` und nach dem separaten
Guided-Masterplan-Programm (Welle 9) begonnen. Jedes Modul benötigt:

- einen eigenen ADR,
- eine eigene Roadmap-Sektion mit Scope-Grenze,
- eigene Tests und eigene Release-Sequenz.

## 10. Verweise

- ADR 0016 — V2 User-Owned Masterplan Boundary
- `docs/product/numra-v2-guided-masterplan.md` — Guided-Masterplan-Spezifikation
- Master-Vertrag §11 — Zukunftsmodule
- `PROJECT_CHARTER.md`, `ROADMAP.md`
