# Numra Full Analysis Experience — Execution Plan

> **Dokumenttyp:** Execution Plan
> **Architekturquelle:** `docs/plans/numra-full-analysis-v2-v3.md`
> **Sequenz-Governance:** `docs/adr/0017-v2-parallel-anbindung-sequenz.md` (ACCEPTED)
> **Ersetzt die Architekturquelle:** NEIN
> **Darf Architekturentscheidungen verändern:** NEIN
> **Erstellt:** 2026-08-05
> **Repository:** `GoLukeEnviro/numerology-analyst-agent`
> **Sprache:** Deutsch

---

## SEQUENCING_GATE (verbindlich, aus ADR 0017 + ADR 0028)

```
ADR 0017 (2026-08-04) untersagte einen V2-Merge nach main, solange der
RC2-Releasepfad offen ist, und verlangte Welle 4 erst nach dem RC2-Schnitt.

PR #56 hat den V2/V3-Stack (Backend-Wellen 1–3, Web-Welle 4) dennoch nach
main gebracht. Der Widerspruch wird nicht durch Umschreiben der Historie
verborgen, sondern durch ADR 0028 (2026-08-06) kanonisiert:

- V2/V3 verbleibt auf main (kein Revert, kein Force-Push).
- product_default_method_version=v1 bleibt verbindlich.
- rollout_stage=disabled bleibt verbindlich.
- V2/V3 ist nicht Bestandteil des RC2-Default-Scopes.
- Guided Masterplan bleibt bis nach Stable v0.3.0 gesperrt.
- Neue Merge-/Release-Gates und ein klarer Rollbackpfad sind definiert.
```

Der operative RC2-Blocker **Issue #39** (genehmigter privater Staging-Host + reale Deployment-Evidenz) ist weiterhin offen.

---

## BASELINE_ALREADY_IMPLEMENTED

### V1-Guard

```
Status: DONE
Datei: src/numerology_api/routes/profiles.py:51-52
Funktion: method_version_mismatch_response() + Guard
Verhalten: policy.version != "v1" → 422 METHOD_VERSION_MISMATCH
Aktion in Welle 1: Nicht erneut implementieren. Bestehendes Verhalten mit
  Regressionstest und V1-Contract-Snapshot absichern.
```

### Wheel-Ressourcenprüfung

```
Status: DONE
Datei: tests/integration/test_production_graph.py:274-282 (test_wheel_contains_prompt_templates)
Geprüfte Dateien: de-report-system.md, de-report-task.md, de-follow-up-task.md, de-report-eval.md
Aktion in Welle 3: Bestehenden Test um V3-Ressourcen ERWEITERN:
  - numerology_agent/prompt_templates/system/de-report-system-v3.md
  - numerology_agent/prompt_templates/tasks/de-report-task-v3.md
  - numerology_knowledge/data/de-v3.json
Keine neue Datei tests/deployment/test_wheel_resources.py anlegen.
```

---

## Kurzfassung (TL;DR)

Vollständiger paralleler V2/V3-Stack (Berechnung, API, Wissen, Agent, Idempotenz, Web-Tabs) für die Numra Full Analysis Experience. Der V1-Stack bleibt in allen dokumentierten Erfolgsfällen rückwärtskompatibel. Der V2/V3-Stack entsteht als vollständig paralleler, neuer Stack (`/api/v2/*`, `*_v3.py`-Dateien, `de-v3.json`, `de-report-*-v3.md`), der sich mit V1 ausschließlich den unveränderten Rechenkern und eine gemeinsame Präsentationsschicht teilt.

**Leitprinzip — präzisiert:**

> Keine geteilten **versionierten HTTP-Request-/Response-Modelle, Reportmodelle, Providerresultate oder zustandsbehafteten Services** zwischen `/api/v1` und `/api/v2`.
>
> **Erlaubte Wiederverwendung** stabiler, unveränderter Domainprimitiven und technischer Low-Level-Infrastruktur (z. B. `PersonInput`, `MethodPolicy`, `ProfileCalculationResultV4`, `KarmicOccurrence`, `ProblemDetails`, Rate-Limit- und Circuit-Breaker-Primitiven, kanonische Hash-Helfer), sofern dadurch kein V1-Vertrag verändert wird.

**Produktfluss:**

```
Personendaten → deterministische pythagorean-v2-Berechnung
→ ProfileCalculationResultV4 → minimiertes Closed-Book-Faktenpaket
→ versioniertes internes Numra-Wissen → strukturierter DeepSeek-Bericht
→ validiertes AnalysisReportV3 → lokale Berichtshistorie
→ neun barrierefreie Ergebnisreiter → spätere Offline-Lesbarkeit
```

---

## Nicht verhandelbare Prinzipien

1. **Determinismus vor LLM:** Alle Zahlen werden ausschließlich deterministisch berechnet. Das LLM darf niemals Zahlen selbst berechnen oder verändern.
2. **Getrennte Lebenswege:** Die primäre `40/4` und sekundäre `22/4` bleiben als getrennte Werte erhalten.
3. **Meisterzahlen:** Eine gehaltene Meisterzahl darf nicht auf ihren Root-Wert abgeflacht werden. Die sekundäre Lebenswegmethode überschreibt die primäre niemals.
4. **Klassische Meisterzahlliste:** 11, 22 und 33. `44/8` ist eine verstärkte Doppelzahl, keine klassische Meisterzahl.
5. **Provider-Isolation:** Der Provider erhält keine Websuche und keine Tools.
6. **V1-Unverletzlichkeit:** Alte V1-Verträge werden nicht still verändert.
7. **Getrennte Versionsachsen:** Wissens-, Prompt-, Profil-, API- und Reportversionen bleiben getrennte Achsen.
8. **Privacy:** Keine Berichtsinhalte oder vollständigen Fact Packages in Logs. Keine dauerhafte serverseitige Speicherung persönlicher Profile oder Analysen. Kurzzeitige Idempotenzspeicherung muss verschlüsselt und TTL-begrenzt sein.
9. **Safety:** Keine Diagnose-, Schicksals- oder wissenschaftlich unbelegten Tatsachenbehauptungen.

---

## Verbindlicher Berechnungsvertrag

### Referenzprofil: Lukas Springer

| Feld                   | Wert                                                  |
| ---------------------- | ----------------------------------------------------- |
| Geburtsdatum           | 18.07.1986                                            |
| Life Path Primary      | `40/4` (root=4)                                       |
| Life Path Secondary    | `22/4` (root=4, held_master_value=22, is_master=true) |
| Geburtstag             | `18/9`                                                |
| Einstellung            | `25/7`                                                |
| Ausdruck               | `62/8`                                                |
| Seelenstreben          | `18/9`                                                |
| Persönlichkeit         | `44/8` (keine Meisterzahl!)                           |
| Reife                  | `12/3`                                                |
| Persönliches Jahr 2026 | `17/8`                                                |
| Pinnacles              | 16/7, 15/6, 13/4, 13/4                                |
| Challenges             | 2, 3, 1, 1                                            |

### Berechnungs-API

- `calculate_profile_v2()` (bereits implementiert)
- `MethodPolicy.version = "v2"`
- `ProfileCalculationResultV4` (bereits implementiert)
- `NumberModel` mit voller Reduktionskette, karmischen Ursprüngen, Master-Handling
- Keine Formeländerung am bestehenden Rechenkern

---

## Öffentliche API-Verträge

### V1 (unverändert, rückwärtskompatibel)

```
POST /api/v1/profiles/calculate   → calculate_profile()           → ProfileCalculationResult
POST /api/v1/analyses/report      → AgentService                  → AnalysisReport (analysis-report-v2)
POST /api/v1/analyses/follow-up   → AgentService                  → AnalysisFollowUp (v2)
GET  /api/v1/meta                 → MetaResponse (unverändert)
```

**V1-Guard-Fix:** `policy.version != "v1"` → 422 `METHOD_VERSION_MISMATCH` — **BEREITS IMPLEMENTIERT** (siehe BASELINE_ALREADY_IMPLEMENTED).

### V2 (neu, vollständig parallel)

```
POST /api/v2/profiles/calculate   → calculate_profile_v2()        → ProfileCalculationResultV4
POST /api/v2/analyses/report      → AgentServiceV3                → AnalysisReportV3
POST /api/v2/analyses/follow-up   → AgentServiceV3                → AnalysisFollowUpV3
GET  /api/v2/meta                 → MetaResponseV2
```

`/api/v2/analyses/*` akzeptiert `ProfileCalculationResultV4` direkt — keine Union mit V1-Modellen.

### MetaResponseV2

```python
class MetaResponseV2:
    api_version: Literal["v2"]
    endpoint_method_version: Literal["v2"]
    supported_method_versions: tuple[Literal["v2"], ...]
    product_default_method_version: Literal["v1", "v2"]  # v1 bis Welle 5C
    rollout_stage: Literal["disabled", "opt_in", "canary", "default"]
    supported_profile_schema_versions: tuple[str, ...]
    supported_report_schema_versions: tuple[str, ...]
    supported_knowledge_bundles: tuple[str, ...]
```

---

## Parallele V3-Dateistruktur

### Unverändert (V1/V2-Stack)

```
src/numerology_agent/models.py
src/numerology_agent/provider.py
src/numerology_agent/deepseek.py
src/numerology_agent/prompts.py
src/numerology_agent/service.py
src/numerology_interpretation/service.py
src/numerology_knowledge/models.py
src/numerology_knowledge/loader.py
src/numerology_api/routes/profiles.py          ← V1-Guard bereits implementiert
src/numerology_api/routes/analyses.py
src/numerology_api/routes/meta.py
```

### Neu (V2/V3-Stack)

```
src/numerology_agent/models_v3.py
src/numerology_agent/facts_v3.py               ← Fact-Entry- und Provider-Package-Builder
src/numerology_agent/provider_v3.py
src/numerology_agent/deepseek_v3.py
src/numerology_agent/prompts_v3.py
src/numerology_agent/service_v3.py             ← ausschließlich AgentServiceV3
src/numerology_interpretation/service_v3.py
src/numerology_knowledge/models_v3.py
src/numerology_knowledge/loader_v3.py
src/numerology_knowledge/data/de-v3.json
src/numerology_api/routes/profiles_v2.py
src/numerology_api/routes/analyses_v2.py
src/numerology_api/routes/meta_v2.py
src/numerology_api/analysis_runtime_v2.py
src/numerology_api/dependencies_v3.py
src/numerology_api/idempotency.py
```

**Hinweis:** `facts_v3.py` enthält die Fact-Entry- und Provider-Package-Builder (in Welle 2), `service_v3.py` enthält ausschließlich den `AgentServiceV3` (in Welle 3). Kein God-Modul.

---

## V3-Wissensmodell

### KnowledgeEntryV3

- `method_system: Literal["pythagorean-v2"]`
- `result_contexts: tuple[ResultContextV3, ...]` mit Kontexten für `life_path_primary` und `life_path_secondary` als getrennte Werte

### ResultContextV3

```python
ResultContextV3 = Literal[
    "life_path_primary",
    "life_path_secondary",
    "birthday",
    "attitude",
    "expression",
    "soul_urge",
    "personality",
    "maturity",
    "personal_year",
    "personal_month",
    "personal_day",
    "pinnacle",
    "challenge",
]
```

### KnowledgeBundleV3

- `version: Literal["v3"]`
- `bundle_id: Literal["numra-knowledge-de-v3"]`
- Explizites Laden: `load_knowledge_bundle_v3(locale="de", bundle_id="numra-knowledge-de-v3")`
- **Nicht** automatisch anhand von `profile.schema_version` auswählen
- Fail-closed bei null Treffern oder mehreren gleichwertigen Treffern

---

## Fact Package

### AnalysisFactEntryV3

```python
class AnalysisFactEntryV3:
    calculation_ref: str
    result_context: str
    role: Literal["primary", "secondary", "supporting"]
    raw_total: int
    reduction_chain: tuple[int, ...]
    root_value: int
    held_master_value: int | None
    display_notation: str
    is_master: bool
    compound_classification: str | None
    karmic_occurrences: tuple[KarmicOccurrence, ...]
    calculation_method: str
    method_version: str
    components: tuple[int, ...]
    trace_ref: str
```

### AnalysisFactPackageV3

```python
class AnalysisFactPackageV3:
    calculation_hash: str
    profile_schema_version: str
    method_version: str
    entries: tuple[AnalysisFactEntryV3, ...]
```

Das interne Package ist request-scoped, transient, nicht geloggt und wird nicht dauerhaft gespeichert.

### ProviderFactPackageV3

Aus `AnalysisFactPackageV3` abgeleitet, minimiert:

- Keine vollständigen Namen
- Keine Buchstabenketten
- Keine technischen Traces
- `trace_ref` nur als opake Kennung

---

## V3-Berichtvertrag (vollständig)

### ClaimV3

```python
class ClaimV3:
    claim_id: str
    claim_type: ClaimType
    text: str
    calculation_refs: tuple[str, ...]
    knowledge_refs: tuple[str, ...]
    uncertainty: str | None
    composer_rule_id: str | None
```

### 18 feste Section-IDs

| #   | Section-ID                        | UI-Reiter                |
| --- | --------------------------------- | ------------------------ |
| 1   | `executive_overview`              | Überblick                |
| 2   | `life_path_and_purpose`           | Lebensweg                |
| 3   | `birthday_and_attitude`           | Lebensweg                |
| 4   | `inner_motivation`                | Inneres Profil           |
| 5   | `expression_and_external_persona` | Ausdruck und Wirkung     |
| 6   | `maturity_and_development`        | Inneres Profil           |
| 7   | `number_harmonies`                | Muster und Spannungen    |
| 8   | `number_tensions`                 | Muster und Spannungen    |
| 9   | `repetitions_and_missing_values`  | Muster und Spannungen    |
| 10  | `life_phases`                     | Lebensphasen             |
| 11  | `personal_cycles`                 | Lebensphasen             |
| 12  | `pinnacles`                       | Lebensphasen             |
| 13  | `challenges`                      | Lebensphasen             |
| 14  | `shadow_patterns`                 | Schatten und Entwicklung |
| 15  | `development_opportunities`       | Schatten und Entwicklung |
| 16  | `practical_integration`           | Integration              |
| 17  | `final_synthesis`                 | Integration              |
| 18  | `method_and_calculation_notes`    | Rechenweg                |

### AnalysisSectionV3

```python
class AnalysisSectionV3:
    section_id: str                    # eine der 18 festen IDs
    applicable: bool
    model_heading: str | None
    summary: str                       # max. 800 Zeichen (1400 für executive_overview/final_synthesis)
    claims: tuple[ClaimV3, ...]        # 1–4 wenn applicable=true, 0 wenn false
    supporting_calculation_refs: tuple[str, ...]
    supporting_knowledge_refs: tuple[str, ...]
    counter_hypotheses: tuple[str, ...]   # 0–2
    reflection_questions: tuple[str, ...]  # 0–2
    practical_options: tuple[str, ...]     # 0–2
    limitations: tuple[str, ...]           # 0–1
```

### Validator

```python
@model_validator(mode="after")
def validate_applicability(self):
    if self.applicable:
        if not 1 <= len(self.claims) <= 4:
            raise ValueError("applicable section requires 1-4 claims")
    else:
        if self.claims or self.supporting_calculation_refs or self.supporting_knowledge_refs:
            raise ValueError("non-applicable section must contain no claims or references")
    return self
```

### AnalysisReportContentV3

```python
class AnalysisReportContentV3:
    summary: str
    sections: tuple[AnalysisSectionV3, ...]
    global_limitations: tuple[str, ...]
```

Keine zusätzlichen globalen `suggestions` — praktische Optionen liegen bereits eindeutig in den Sections.

### AnalysisReportV3 (vollständiger Envelope)

```python
class AnalysisReportV3:
    schema_version: Literal["analysis-report-v3"]
    report_id: UUID
    content: AnalysisReportContentV3
    report_content_hash: str
    generation_context_hash: str
    provenance: AnalysisProvenanceV3
    context_signature: str
```

---

## Provider und Prompts

### DeepSeekProviderV3

- Lädt ausschließlich `de-report-system-v3.md` und `de-report-task-v3.md`
- **Keine Tools, keine Websuche**
- Zielkonfiguration:
  - `model = deepseek-v4-pro`
  - `thinking = enabled`
  - `reasoning_effort = high`
  - `temperature` = nicht senden
  - `top_p` = nicht senden
  - `response_format = json_object`

### ProviderResultV3

```python
class ProviderResultV3:
    content: str
    model: str
    finish_reason: str               # NEU: explizit ausgewertet
    provider_fingerprint: str | None
    prompt_tokens: int
    completion_tokens: int
```

### Finish-Reason-Matrix

| `finish_reason`                | Behandlung                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| `stop`                         | Normal validieren                                                                     |
| `length`                       | Max. 1 Zusatzversuch mit größerem Budget, dann Kapitelorchestrierung oder Fail-Closed |
| `content_filter`               | Fail-Closed, keine Teilantwort speichern                                              |
| `tool_calls`                   | Provider-Vertragsverletzung (keine Tools angeboten)                                   |
| `insufficient_system_resource` | Transienter Retry                                                                     |
| leer / unbekannt               | Fail-Closed + Telemetrie                                                              |

Nie unvollständige Berichte speichern.

---

## Idempotenz

### Request-Modelle

```python
class AnalysisReportRequestV2:
    request_id: UUID                  # Idempotenz-Key der Berichtserzeugung
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4

class AnalysisFollowUpRequestV2:
    request_id: UUID                  # Idempotenz-Key des Follow-ups
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4
    report: AnalysisReportV3
    question: str
```

### Idempotenzschlüssel

- `pseudonymous_device_key + operation_type + request_id`

### Request-Context-Hash

**Für Berichte (`operation="report"`):**

```
operation_type, calculation_hash, generation_context_hash, report_schema_version
```

**Für Follow-ups (`operation="follow_up"`):**

```
operation_type, calculation_hash, report_id, report_content_hash,
normalisierte Frage, follow_up_prompt_version
```

### IdempotencyStoreV3

```python
class IdempotencyStoreV3(Protocol):
    async def acquire(*, key, request_context_hash, operation, ttl_seconds) -> AcquireResultV3
    async def complete(*, key, owner_token, response_type, encrypted_response) -> None
    async def fail(*, key, owner_token, error_code, retryable) -> None
```

Zustände: `PENDING`, `COMPLETED`, `FAILED`
TTL: 1–6 Stunden (keine Verlängerung durch Reads)
Atomar via `SET NX` / Lua-Skript

### Prüf-Reihenfolge

```
1. Request validieren
2. Kanonisches Profil prüfen
3. Idempotenz prüfen (existierende Response? laufende Generierung?)
4. Atomaren Lock erwerben
5. Rate-Limit prüfen
6. Provider aufrufen
7. Verschlüsselte Response speichern
8. Lock auf COMPLETED setzen
```

| Zustand                                      | Antwort                                                                             |
| -------------------------------------------- | ----------------------------------------------------------------------------------- |
| Gleicher Key, Generierung läuft              | `202` + `Retry-After`-Header, `code: ANALYSIS_GENERATION_IN_PROGRESS`, `request_id` |
| Gleicher Key, abgeschlossen                  | Identische gespeicherte Response                                                    |
| Gleicher Key, anderer `request_context_hash` | `409 IDEMPOTENCY_KEY_CONFLICT`                                                      |
| Neuer Key                                    | Neue Berichtsgenerierung                                                            |

### Idempotenz-Kryptovertrag (vollständig)

```
NUMRA_IDEMPOTENCY_ENCRYPTION_KEY

Regeln:
- separater Schlüssel, NIEMALS NUMRA_RATE_LIMIT_HMAC_SECRET wiederverwenden
- authentifizierte Verschlüsselung: AES-GCM-256
- zufälliger 96-Bit-Nonce pro Cache-Eintrag
- operation_type, request_context_hash und Key-ID als AAD
- Ciphertext, Nonce und Key-ID im Redis-Value
- KEINE Klartext-Response im Redis
- V3-Analyse-Start schlägt fail-fast fehl, wenn der Schlüssel fehlt
- V1-Startup bleibt davon unbeeinflusst
- Schlüsselrotation muss mindestens die maximale TTL überlappen
```

### 202-Vertrag (laufende Generierung)

```
HTTP 202
Retry-After: <Sekunden>
Content-Type: application/problem+json

{
  "type": ".../analysis-generation-in-progress",
  "title": "Analysis generation in progress",
  "status": 202,
  "code": "ANALYSIS_GENERATION_IN_PROGRESS",
  "request_id": "<UUID>"
}
```

Der Client wiederholt denselben Request mit derselben `request_id`.

---

## Hashes und Signatur

### generation_context_hash

Enthält mindestens:

```
calculation_hash, profile_schema_version, method_version,
provider_fact_package_hash, capability_matrix_version,
prompt_version, prompt_content_hash,
knowledge_bundle_id, knowledge_content_hash,
report_schema_version, model, thinking_mode,
reasoning_effort, orchestration_version
```

### report_content_hash

Hash über kanonisch serialisierte Inhalte:

```
schema_version
content.summary
content.sections
content.global_limitations
```

**Nicht enthalten:** `report_id`, `report_content_hash` selbst, `context_signature`, Zeitstempel, Tokenzahlen, Provider-Fingerprint.

### Envelope-Reihenfolge

```
1. Reportinhalt validieren
2. report_content_hash berechnen
3. generation_context_hash einsetzen
4. report_id erzeugen
5. Finale Envelope bilden
6. context_signature über die Envelope (ohne context_signature) berechnen
```

### Kanonische JSON-Serialisierung

```python
json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

---

## Größenbudgets

```
MAX_CANONICAL_REPORT_BYTES =
    V2_FOLLOW_UP_REQUEST_LIMIT
    - MAX_SERIALIZED_V4_PROFILE_BYTES
    - MAX_SERIALIZED_QUESTION_BYTES
    - ENVELOPE_OVERHEAD_BYTES
    - SAFETY_MARGIN_BYTES
```

Getestet mit:

- Allen Golden-Profilen
- Maximalfällen (lange Namen, aktive Namen, maximale Traces, maximale erlaubte Sections, maximale Frage)

Kein globales Hochsetzen des Body-Limits ohne pfadspezifische Risikoanalyse.

### Token-Limit

```
NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS = 32768

Dies ist eine anfängliche projektinterne Kosten-, Latenz- und
Validierungsgrenze, NICHT das technische Maximum des Providers.
DeepSeek dokumentiert für deepseek-v4-pro eine maximale Ausgabe
von bis zu 384K Tokens.

Die Evaluation (Welle 5A) darf eine andere projektinterne Grenze
empfehlen, sofern Größenbudget, Kostenbudget, Latenz, Validierung
und Idempotenzspeicherung nachweislich bestanden sind.
```

---

## Web-Erfahrung

### Präsentationsmodell-Adapter

`toProfilePresentationModel()` bildet sowohl V1/V3- als auch V4-Profile auf ein stabiles `ProfilePresentationModel` ab.

### Neun Hauptreiter (18→9-Mapping)

| UI-Reiter                | Sections                                                                |
| ------------------------ | ----------------------------------------------------------------------- |
| Überblick                | `executive_overview`                                                    |
| Lebensweg                | `life_path_and_purpose`, `birthday_and_attitude`                        |
| Inneres Profil           | `inner_motivation`, `maturity_and_development`                          |
| Ausdruck und Wirkung     | `expression_and_external_persona`                                       |
| Muster und Spannungen    | `number_harmonies`, `number_tensions`, `repetitions_and_missing_values` |
| Lebensphasen             | `life_phases`, `personal_cycles`, `pinnacles`, `challenges`             |
| Schatten und Entwicklung | `shadow_patterns`, `development_opportunities`                          |
| Integration              | `practical_integration`, `final_synthesis`                              |
| Rechenweg                | `method_and_calculation_notes`                                          |

### Anforderungen

- WAI-ARIA-konforme Tabs (role=tablist/tab/tabpanel)
- Tastaturnavigation (Pfeiltasten, Home/End)
- Deep Links via `useSearchParams()`
- Feste UI-Labels aus `SECTION_UI_LABELS`-Tabelle
- **Keine LLM-Aufrufe beim Reiterwechsel**
- Mobile: scrollbare Tab-Leiste mit Scroll-Indikator
- Lineare Druckansicht (`@media print`)
- PDF-Export aller Inhalte
- Icon-Bibliothek: `@remixicon/react` (bereits vorhanden, keine zweite hinzufügen)

---

## Lokale Speicherung (IndexedDB)

### reports-Tabelle (Dexie-Schema v4)

```
reportId (UUID, Primärschlüssel)
profileId
reportContentHash
generationContextHash
methodVersion
reportSchemaVersion
calculationHash
createdAt
payload (verschlüsselt bei aktivem Vault)
```

- Mehrere Berichte pro Profil (Historie, keine Exception mehr)
- `threads` und `notes` erhalten zusätzlich `reportId`
- Altdaten bleiben lesbar (Migration, kein Datenverlust)
- Export-/Importschema auf v3

### Offline-Status

```
PROFILE_CALCULATION_REQUIRES_NETWORK
REPORT_GENERATION_REQUIRES_NETWORK
SAVED_PROFILE_AVAILABLE_OFFLINE
SAVED_REPORT_AVAILABLE_OFFLINE
```

Produkttexte dürfen nicht behaupten, DeepSeek arbeite vollständig lokal.

---

## OpenAPI-Strategie

- `openapi/numra-api.json` — vollständiges Dokument (V1 + V2)
- `openapi/contracts/v1-contract.json` — V1-Schema-Closure (rekursiv alle referenzierten `components.schemas`)
- `scripts/export_openapi.py` schreibt nach `numra-api.json`
- `apps/web/package.json`: `pnpm web:generate-api` liest aus `numra-api.json`
- Web-App generiert Typen aus `numra-api.json`

---

## ADR-Planung (Welle 0)

Bestehende ADR 0017 (`0017-v2-parallel-anbindung-sequenz.md`, ACCEPTED) wird **unverändert respektiert** und legt die Sequenz-Governance fest. Neue ADRs beginnen ab der nächsten tatsächlich freien Nummer: **0018**.

**Post-PR-56-Ergänzung (2026-08-06):** PR #56 hat den V2/V3-Stack nach `main`
gebracht, obwohl ADR 0017 einen V2-Merge vor dem RC2-Schnitt untersagte.
**ADR 0028** (`docs/adr/0028-post-pr56-sequenz-und-rollout-reconciliation.md`)
kanonisiert diesen Zustand: V2/V3 verbleibt auf `main`, `v1` bleibt Default,
`rollout_stage=disabled`, V2/V3 außerhalb des RC2-Default-Scopes, Guided
Masterplan bis nach Stable gesperrt, neue Merge-/Release-Gates und
Rollbackpfad definiert.

### Welle 0 — Vertrags- und Releaseentscheidungen

**Ziel:** Architekturentscheidungen dokumentieren, bevor Code geschrieben wird. Nach Welle 0 darf die Architektur nicht erneut grundsätzlich umgebaut werden.

**15 Schritte (parallelisierbar):**

| #   | ADR      | Thema                                                                                       |
| --- | -------- | ------------------------------------------------------------------------------------------- |
| 1   | —        | Bestehende ADR 0017 unverändert respektieren (RC2-Sequenz, kein V2-Merge vor RC2-Schnitt)   |
| 2   | ADR 0018 | Strikt paralleler Stack `/api/v2/*` — keine geteilten versionierten HTTP-/Report-Modelle    |
| 3   | ADR 0019 | `ProfileCalculationResultV4` direkt in `/api/v2/analyses/*` — keine `Literal`-Verschärfung  |
| 4   | ADR 0020 | Unveränderlichkeit von `de-v2.json`; `de-v3.json` als neues Bundle                          |
| 5   | ADR 0021 | Trennung `AnalysisFactPackageV3` (transient) vs. `ProviderFactPackageV3` (Closed-Book)      |
| 6   | ADR 0022 | `finish_reason`-Klassifikationsmatrix                                                       |
| 7   | ADR 0023 | API-Idempotenz über `request_id`, `IdempotencyStoreV3`-Vertrag, vollständiger Kryptovertrag |
| 8   | ADR 0024 | Dependency-Wiring (`provider_v3`, `circuit_breaker_v3`, `idempotency_store`)                |
| 9   | ADR 0025 | OpenAPI-Artifact-Strategie                                                                  |
| 10  | ADR 0026 | Gesamtgrößenbudget + Token-Limit (`NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS = 32768`)             |
| 11  | ADR 0027 | Hash-/Signaturkanonisierung                                                                 |
| 12  | —        | Capability-Matrix der 18 Sections (`docs/methods/capability-matrix-v3.md`)                  |
| 13  | —        | Report-Längenbudgets (`docs/methods/section-budgets-v3.md`)                                 |
| 14  | —        | Golden-E2E-Testfall: Lukas Springer über vollständigen V2/V3-Graphen                        |
| 15  | —        | Mobile-Strategie für 9 Reiter                                                               |

**Neue Dateien (Welle 0):**

- `docs/adr/0018-v2-stack-isolation.md` bis `docs/adr/0027-hash-canonization.md` (10 ADRs)
- `docs/methods/capability-matrix-v3.md`
- `docs/methods/section-budgets-v3.md`

**Verifikation:** Alle ADRs vorhanden, Capability-Matrix listet 18 Section-IDs, Golden-E2E dokumentiert.

---

## Numerische Rollout-Gates (Welle 5C)

Diese Werte sind in Welle 0 zu spezifizieren:

| Gate                  | Messdefinition                                           | Datengrundlage                | Mindeststichprobe          | Owner            |
| --------------------- | -------------------------------------------------------- | ----------------------------- | -------------------------- | ---------------- |
| `schema_success_rate` | Anteil gültiger JSON-Responses an Gesamt-Requests        | Welle 5A Evaluation + 5B Beta | ≥ 100 Requests             | Agent-Entwickler |
| `provider_error_rate` | Anteil Provider-Fehler (5xx, timeout) an Gesamt-Requests | Welle 5A Evaluation + 5B Beta | ≥ 100 Requests             | Agent-Entwickler |
| `P95_latency`         | 95. Perzentil der End-to-End-Latenz (Request→Response)   | Welle 5A Evaluation + 5B Beta | ≥ 100 Requests             | Agent-Entwickler |
| `cost_per_report`     | Durchschnittliche API-Kosten pro Bericht (USD)           | Welle 5A Evaluation           | ≥ 15 Läufe (5 Profile × 3) | Agent-Entwickler |

Die konkreten Grenzwerte werden in Welle 0 festgelegt oder spätestens vor Welle 5A mit verbindlichem Zeitpunkt versehen. **Welle 5C darf nicht starten, solange ein Gate noch nur „Grenzwert" oder „Budget" heißt.**

---

## Implementierungswellen

### Übersicht

```
Welle 0  →  ADRs + Plan-Grundlage (auf isoliertem V2-Branch)
Welle 1  →  API-Grundlage (Profile V2, Meta V2, Interfaces, OpenAPI, CLI)
Welle 2  →  Fact Package + Knowledge V3 + Interpretation V3
Welle 3  →  Berichtserzeugung (Provider, Service, Prompts, Idempotenz, /api/v2/analyses/*)
Welle 4  →  Web-Migration (Tab-UI, Storage, Offline, Print/Export)
Welle 5A →  Provider-Evaluation (kein Default-Wechsel)
Welle 5B →  Opt-in-Beta (V1 bleibt Default)
Welle 5C →  Default-Wechsel (nur bei vollständig bestandenen Gates)
```

**IST-Zustand (2026-08-06):** Wellen 0–4 sind durch PR #56 auf `main`
(`ba4c9121…`) — kontrolliert gemäß ADR 0028 (`product_default_method_version=v1`,
`rollout_stage=disabled`). Welle 5A ist **BLOCKED** (Legal/Transfer-Approval +
Runtime-Marker fehlen). Welle 5B/5C bleiben gesperrt bis nach Stable `v0.3.0`.

---

### Welle 1 — API-Grundlage

**Ziel:** V2-Endpunkte, Interfaces, Settings, OpenAPI. **Keine** aktive V2-Analyse-Pipeline.

**Schritte:**

| #   | Schritt                             | Datei                                                                                                                     | Abhängigkeit                        |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| 1   | ~~V1-Guard-Fix~~                    | ~~`src/numerology_api/routes/profiles.py`~~                                                                               | **BASELINE: BEREITS IMPLEMENTIERT** |
| 2   | V2-Profil-Endpunkt                  | `src/numerology_api/routes/profiles_v2.py` (neu)                                                                          | —                                   |
| 3   | V2-Meta-Endpunkt (`MetaResponseV2`) | `src/numerology_api/routes/meta_v2.py` (neu)                                                                              | —                                   |
| 4   | V2-Analyse-Runtime                  | `src/numerology_api/analysis_runtime_v2.py` (neu)                                                                         | —                                   |
| 5   | Dependency-Wiring-Interfaces        | `src/numerology_agent/provider_v3.py`, `src/numerology_api/idempotency.py`, `src/numerology_api/dependencies_v3.py` (neu) | —                                   |
| 6   | `create_app` erweitern              | `src/numerology_api/app.py`                                                                                               | Schritt 5                           |
| 7   | OpenAPI umstellen                   | `scripts/export_openapi.py`, `apps/web/package.json`                                                                      | Schritt 2+3                         |
| 8   | CLI `--method-version`              | `src/numerology_cli/main.py`                                                                                              | —                                   |

**Verifikation:**

- `uv run pytest` — bestehende Suite grün
- `/api/v2/profiles/calculate` → 200 (Lukas)
- V1-Guard-Regressionstest: `/api/v1/profiles/calculate` mit `version="v2"` → 422
- `/api/v1/analyses/report` + `/api/v1/meta` unverändert
- `v1-contract.json` Schema-Closure identisch
- `uv run python scripts/export_openapi.py --check` grün

---

### Welle 2 — Fakten und Wissen

**Ziel:** Fact-Package, V3-Wissen, V3-Interpretation. Noch keine Provider-Integration.

**Schritte:**

| #   | Schritt                   | Datei                                               | Abhängigkeit |
| --- | ------------------------- | --------------------------------------------------- | ------------ |
| 1   | V3-Fact-Modelle           | `src/numerology_agent/models_v3.py` (neu, Teil 1)   | —            |
| 2   | Fact-Package-Builder      | `src/numerology_agent/facts_v3.py` (neu)            | Schritt 1    |
| 3   | V3-Wissensmodell          | `src/numerology_knowledge/models_v3.py` (neu)       | —            |
| 4   | V3-Wissensdaten           | `src/numerology_knowledge/data/de-v3.json` (neu)    | Schritt 3    |
| 5   | V3-Wissensloader          | `src/numerology_knowledge/loader_v3.py` (neu)       | Schritt 3+4  |
| 6   | V3-Interpretation         | `src/numerology_interpretation/service_v3.py` (neu) | Schritt 5    |
| 7   | Capability-Matrix ablegen | `docs/methods/capability-matrix-v3.md`              | Welle 0      |

**Verifikation:**

- `tests/unit/test_analysis_fact_package.py` (neu)
- `tests/unit/test_knowledge_v3.py` (neu)
- Bestehende `test_agent.py`/`test_interpretation.py` unverändert grün

---

### Welle 3 — Berichtserzeugung

**Ziel:** Vollständige V3-Berichtspipeline mit Idempotenz.

**Schritte:**

| #   | Schritt                     | Datei                                                                                        | Abhängigkeit  |
| --- | --------------------------- | -------------------------------------------------------------------------------------------- | ------------- |
| 1   | V3-Report-Modelle           | `src/numerology_agent/models_v3.py` (erweitern um ClaimV3, SectionV3, ReportV3)              | Welle 2       |
| 2   | V3-Prompts + Loader         | `src/numerology_agent/prompts_v3.py`, `de-report-system-v3.md`, `de-report-task-v3.md` (neu) | —             |
| 3   | V3-Provider (finish_reason) | `src/numerology_agent/deepseek_v3.py` (neu)                                                  | Schritt 1+2   |
| 4   | V3-Agent-Service            | `src/numerology_agent/service_v3.py` (neu, ausschließlich AgentServiceV3)                    | Schritt 3     |
| 5   | Idempotenz-Implementierung  | `src/numerology_api/idempotency.py` (erweitern mit Kryptovertrag)                            | Welle 1       |
| 6   | V2-Analyse-Routen           | `src/numerology_api/routes/analyses_v2.py` (neu)                                             | Schritt 4+5   |
| 7   | Größenbudget-Tests          | (Tests)                                                                                      | Schritt 6     |
| 8   | Wheel-Smoke erweitern       | `tests/integration/test_production_graph.py` (erweitern um V3-Ressourcen)                    | Schritt 1+2+4 |

**Verifikation:**

- `tests/unit/test_agent_v3.py` (neu)
- `tests/unit/test_idempotency.py` (neu)
- `tests/integration/test_production_graph.py` (erweitert)
- `uv run pytest --cov=src --cov-fail-under=85` grün
- Wheel-Smoke: `de-report-system-v3.md`, `de-report-task-v3.md`, `de-v3.json` im Wheel vorhanden und lesbar

---

### Welle 4 — Web-Migration (BEGINNT ERST NACH RC2-SCHNITT)

**Ziel:** 9 Reiter, Berichtshistorie, Offline, Print/PDF.

**Schritte:**

| #   | Schritt                     | Datei                                                                                            | Abhängigkeit |
| --- | --------------------------- | ------------------------------------------------------------------------------------------------ | ------------ |
| 1   | Präsentationsmodell-Adapter | `apps/web/src/features/profile/presentation.ts` (neu)                                            | —            |
| 2   | API-Client V2-Endpunkte     | `apps/web/src/api/client.ts`, `apps/web/src/api/schema.d.ts`                                     | Welle 1      |
| 3   | Section-Mapping (18→9)      | `apps/web/src/features/report/sectionMapping.ts` (neu)                                           | —            |
| 4   | ResultsTabs (WAI-ARIA)      | `apps/web/src/features/report/ResultsTabs.tsx` (neu)                                             | Schritt 3    |
| 5   | ReportExperience umbauen    | `apps/web/src/features/report/ReportExperience.tsx`                                              | Schritt 4    |
| 6   | Druckansicht + PDF          | `apps/web/src/features/report/PrintView.tsx` (neu), `apps/web/src/features/export/profilePdf.ts` | Schritt 1    |
| 7   | Storage Schema v4           | `apps/web/src/storage/database.ts`, `apps/web/src/storage/repository.ts`                         | —            |
| 8   | Offline-Status              | `apps/web/src/pwa/offlineState.ts` (neu)                                                         | —            |
| 9   | AnalysisWizard v1/v2        | `apps/web/src/features/analysis/AnalysisWizard.tsx`                                              | Schritt 2    |

**Verifikation:**

- `pnpm web:typecheck` grün
- `pnpm web:test` grün
- `pnpm web:e2e` grün (Playwright + axe-core)

---

### Welle 5A — Provider-Evaluation

**Ziel:** Empirische DeepSeek-Konfigurationsevaluation.

- `scripts/eval_deepseek_config.py` (neu)
- 5 Golden-Profile × 3 Läufe × 2 Varianten (Thinking vs. Non-Thinking)
- Metriken: Zahlenkorrektheit, Kapitelabdeckung, Schema-Treue, Varianz, Trunkierung, Kosten, Latenz
- `max_output_tokens` kalibrieren (≤ `NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS`)
- `MAX_CANONICAL_REPORT_BYTES` festlegen

**Kein Default-Wechsel nach der Evaluation.**

---

### Welle 5B — Opt-in-Beta

- `rollout_stage = "opt_in"`
- V2 im Wizard manuell auswählbar, V1 bleibt Default
- Telemetrie nur Metriken, keine Inhalte

---

### Welle 5C — Default-Wechsel

Nur bei vollständig bestandenen Gates (alle numerischen Werte müssen in Welle 0 konkret festgelegt sein):

```
reference_integrity = 100%
Lukas 40/4 = PASS, Lukas 22/4 held_master_value=22 = PASS
unknown_references = 0
truncated_reports = 0
PII_leakage = 0
V1_contract_snapshot = PASS
schema_success_rate >= [konkreter Grenzwert]
provider_error_rate <= [konkretes Budget]
P95_latency <= [konkretes Budget]
cost_per_report <= [konkretes Budget]
rollback_test = PASS
A11y = PASS
Export/Import = PASS
Offline-Reopen = PASS
```

- `product_default_method_version = "v2"`, `rollout_stage = "default"`
- Wizard-Default auf `v2`

---

## Dateiübersicht

### Neue Dateien (38+)

| Welle | Datei                                                                                                                                                                                                                                                                                                    |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | `docs/adr/0018–0027` (10 ADRs), `docs/methods/capability-matrix-v3.md`, `docs/methods/section-budgets-v3.md`                                                                                                                                                                                             |
| 1     | `src/numerology_api/routes/profiles_v2.py`, `src/numerology_api/routes/meta_v2.py`, `src/numerology_api/analysis_runtime_v2.py`, `src/numerology_api/idempotency.py`, `src/numerology_api/dependencies_v3.py`, `src/numerology_agent/provider_v3.py`                                                     |
| 2     | `src/numerology_agent/models_v3.py`, `src/numerology_agent/facts_v3.py`, `src/numerology_knowledge/models_v3.py`, `src/numerology_knowledge/loader_v3.py`, `src/numerology_knowledge/data/de-v3.json`, `src/numerology_interpretation/service_v3.py`                                                     |
| 3     | `src/numerology_agent/deepseek_v3.py`, `src/numerology_agent/prompts_v3.py`, `src/numerology_agent/service_v3.py`, `src/numerology_agent/prompt_templates/system/de-report-system-v3.md`, `src/numerology_agent/prompt_templates/tasks/de-report-task-v3.md`, `src/numerology_api/routes/analyses_v2.py` |
| 4     | `apps/web/src/features/profile/presentation.ts`, `apps/web/src/features/report/sectionMapping.ts`, `apps/web/src/features/report/ResultsTabs.tsx`, `apps/web/src/features/report/PrintView.tsx`, `apps/web/src/pwa/offlineState.ts`                                                                      |
| 5A    | `scripts/eval_deepseek_config.py`                                                                                                                                                                                                                                                                        |

### Geänderte Dateien (12+)

| Welle | Datei                                               | Änderung                                      |
| ----- | --------------------------------------------------- | --------------------------------------------- |
| 1     | `src/numerology_api/app.py`                         | `create_app()`-Signatur                       |
| 1     | `scripts/export_openapi.py`                         | Ausgabeziele                                  |
| 1     | `apps/web/package.json`                             | generate-api-Pfad                             |
| 1     | `src/numerology_cli/main.py`                        | --method-version                              |
| 3     | `src/numerology_agent/models_v3.py`                 | Report-Modelle (ClaimV3, SectionV3, ReportV3) |
| 3     | `src/numerology_api/idempotency.py`                 | RedisIdempotencyStoreV3 + Krypto              |
| 3     | `tests/integration/test_production_graph.py`        | V3-Ressourcen im Wheel                        |
| 4     | `apps/web/src/api/client.ts`                        | V2-Endpunkte                                  |
| 4     | `apps/web/src/api/schema.d.ts`                      | Regenerierung                                 |
| 4     | `apps/web/src/features/report/ReportExperience.tsx` | Tabs integrieren                              |
| 4     | `apps/web/src/features/export/profilePdf.ts`        | Präsentationsmodell                           |
| 4     | `apps/web/src/storage/database.ts`                  | Schema v4                                     |
| 4     | `apps/web/src/storage/repository.ts`                | Mehrfachberichte, reportId                    |
| 4     | `apps/web/src/features/analysis/AnalysisWizard.tsx` | v1/v2-Konfiguration                           |

---

## Rollback-Strategie

- `/api/v2/analyses/*`-Router aus `src/numerology_api/app.py` deaktivieren → V1 unberührt
- `rollout_stage = "disabled"` → Web-App zeigt kein V2
- `product_default_method_version = "v1"` → Wizard-Default bleibt V1

---

## Abnahmekriterien (Gesamt)

```
1.  uv run pytest --cov=src/numerology_engine --cov-fail-under=95     ✅
2.  uv run pytest --cov=src --cov-fail-under=85                        ✅
3.  uv run python scripts/export_openapi.py --check                    ✅
4.  pnpm web:typecheck && pnpm web:test && pnpm web:e2e                ✅
5.  Lukas 40/4 primary, 22/4 secondary, held_master_value=22           ✅
6.  Golden-E2E: alle Referenzprofile über vollen V2/V3-Graphen         ✅
7.  Wheel-Smoke: V3-Ressourcen im installierten Wheel                  ✅
8.  reference_integrity = 100%                                         ✅
9.  unknown_references = 0                                             ✅
10. truncated_reports = 0                                              ✅
11. PII_leakage = 0                                                    ✅
12. V1_contract_snapshot = PASS                                        ✅
13. rollback_test = PASS                                               ✅
14. A11y = PASS                                                        ✅
15. Export/Import = PASS                                               ✅
16. Offline-Reopen = PASS                                              ✅
```

---

## Verifikation (pro Welle)

```bash
# Nach jeder Welle:
uv run pytest --cov=src/numerology_engine --cov-fail-under=95
uv run pytest --cov=src --cov-fail-under=85
uv run python scripts/export_openapi.py --check   # ab Welle 1

# Ab Welle 4 zusätzlich:
pnpm web:typecheck
pnpm web:test
pnpm web:e2e
```

---

## Dokumentation und Release

Reihenfolge:

1. Plan einfrieren ✅ (dieses Dokument)
2. Welle-0-ADRs (ab 0018, auf isoliertem V2-Branch)
3. Umsetzung (Wellen 1–3 auf V2-Branch; Welle 4 nach RC2-Schnitt)
4. Changelog unter `Unreleased` pflegen
5. Opt-in-Beta (Welle 5B)
6. README-Update
7. Default-Rollout (Welle 5C)

Nach Welle 0 darf die Architektur nicht erneut ohne belegten Blocker grundsätzlich umgebaut werden.

---

## Abschlussbericht (nach jeder Welle)

Nach jeder Welle ist zu liefern:

- Geänderte Dateien
- Erfüllte Gates
- Fehlgeschlagene Gates
- Migrationsauswirkungen
- OpenAPI-Auswirkungen
- Privacy-Auswirkungen
- Rollback-Punkt
- Testresultate
- Commit-SHA
- Nächster zulässiger Schritt

Danach an jedem Human-Gate stoppen.
