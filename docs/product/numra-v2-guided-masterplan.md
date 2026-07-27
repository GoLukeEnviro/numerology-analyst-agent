# Numra V2 — Guided Masterplan (Spezifikation)

> **Status:** Spezifikation / Produktvision — KEINE Implementierung in V1
> **Anderungsprozess:** Änderungen erfordern einen ADR. Siehe ADR 0016.
> **Beziehung zu V1:** V1 (`0.3.0rc1` / stabil `0.3.0`) ist funktional
> abgeschlossen. V2 ist ein späteres, separat geplantes Programm.

---

## 1. Zweck

Dieses Dokument beschreibt, was Numra V2 enthalten *könnte*, damit die
V1-Architektur die nötigen Erweiterungspunkte bereithält. Es ist eine
**Produktvision**, kein Implementierungsauftrag. Kein Code in diesem
Dokument geht in den V1-Release ein (ADR 0016).

## 2. Leitprinzipien (unverändert aus V1)

- Determinismus vor LLM — alle Berechnungen funktionieren ohne Sprachmodell.
- Sechs Aussageklassen werden streng getrennt.
- Keine erfundenen Daten, keine Diagnosen, keine garantierte Zukunft.
- Lokale-first, Privatsphäre Standard.
- Auditierbarkeit — jeder Berechnungsschritt ist reproduzierbar.

V2 erweitert den Umfang, ändert aber keines dieser Prinzipien.

## 3. Mögliche V2-Module (Spezifikation)

### 3.1 Erweiterte Methodensysteme

- **Chaldäische Numerologie** (eigenes Modul, eigener Alphabet-Map).
- **Kabbalistische / Gematria-nahe Systeme** (Hebräisch, Sephiroth-Bezug).
- **Historische und moderne Varianten** (z. B. moderne Reduktion, Y-Regel).
- Plugin-/Methodenschnittstelle: Jede Methode bekommt eine eigene Version
  (z. B. `chaldean-v1`), eigenen Hash und eigene Wissenspakete. Keine
  Vermischung mit `pythagorean-v1`.

### 3.2 Mehrsprachigkeit

- Wissenspakete je Locale (`en-v1`, `fr-v1`, etc.).
- Lokalisierung der UI, CLI, API-Beschreibungen und Berichte.
- Methodenspezifische Alphabet-Maps je Sprache (z. B. Umlaut-Behandlung).
- Bestehendes `de-v1`/`de-v2` bleibt kanonisch für Deutsch.

### 3.3 Forschungs-Community-Features

- **Präregistrierung** von Hypothesen vor der Datenerhebung.
- **Geteilte, anonymisierte Datensätze** (DuckDB + Parquet).
- **Nullmodelle und Permutationstests** als Standard-Pipeline.
- **Multiple-Testing-Korrektur** (FDR, Bonferroni) als Pflicht.
- Open-Science-Export ( reproduzierbare Analyse-Snapshots).
- Komitee-gesteuerte Begutachtung empirischer Behauptungen.

### 3.4 Benutzerkonten und Synchronisation

- Optionale, opt-in cloudbasierte Profilsynchronisation.
- Ende-zu-Ende-Verschlüsselung für synchronisierte Daten.
- Mehrgeräte-Nutzung ohne Verlust der lokalen-first-Garantie.
- Explizite Trennung: lokale Daten bleiben primär, Cloud ist optional.

### 3.5 Fortgeschrittene Agenten-Workflows

- Vektor-Retrieval über das versionierte Wissen (nur für Empfehlung, nicht
  für Berechnung — Determinismus bleibt unangetastet).
- Tool-Calls (mehrstufige Agenten-Interaktion) — klar abgegrenzt vom
  one-shot-RC1-Modell.
- Bewertete, menschlich kuratierte Interpretationsvorschläge.
- Personalisierte Lernpfade (pädagogische Erklärungen).

### 3.6 Zukunftsdomänen (separat zu bewerten)

- Astrologie, Human Design, Enneagramm — als eigenständige Module mit
  eigenen Methodenversionen, nicht als Numerologie-Erweiterung.

## 4. Architekturelle Erweiterungspunkte in V1

V1 hält bereits folgende Erweiterungspunkte bereit, die V2 nutzen kann:

| Erweiterungspunkt | V1-Realisierung |
|---|---|
| Methoden-Versionierung | `MethodPolicy`, `pythagorean-v1` kanonisch |
| Plugin-/Methodenschnittstelle | Master-Vertrag §5; `numerology_engine` ist erweiterbar |
| Wissenspaket-Versionierung | `KnowledgeBundle.version`, Loader für mehrere Versionen |
| Locale-Modell | `KnowledgeBundle.locale` |
| Aussageklassen-Taxonomie | `ClaimType`-Enum, `claim_class` in V2-Wissen |
| Agenten-Adapter-Grenze | `numerology_agent` ist dünne Schicht, deterministisch geprüft |
| Forschungsrahmen | DuckDB + Parquet, Nullmodelle skizziert |
| Export-/Import-Verträge | versioniert (`numra-export-v2`) |

## 5. Was V2 NICHT ist

- Keine Ablösung von V1. V1 bleibt das stabile, deterministische Produkt.
- Keine Gelegenheit, das Determinismus-vor-LLM-Prinzip aufzuweichen.
- Keine Bühne für ungeprüfte empirische Behauptungen als Fakten.
- Kein Vehikel für medizinische, psychologische oder identitätsstiftende
  Diagnosen.

## 6. Entscheidungsprozess für V2

Ein formelles V2-Implementierungsprogramm (Welle 9) wird erst nach stabil
freigegebenem `0.3.0` begonnen. Es hat:

- eigene Roadmap (`docs/roadmaps/v2-*.md`),
- eigene ADRs (`0017+`),
- eigene Release-Sequenz,
- eigene Präregistrierung und Begutachtung.

Bis dahin ist dieses Dokument die einzige autorisierte V2-Quelle.

## 7. Verweise

- ADR 0016 — V2 User-Owned Masterplan Boundary
- ADR 0015 — Kumulative Release-Normalisierung auf 0.3.0rc1
- Master-Vertrag §11 — Zukunftsmodule
- `PROJECT_CHARTER.md`, `ROADMAP.md`
