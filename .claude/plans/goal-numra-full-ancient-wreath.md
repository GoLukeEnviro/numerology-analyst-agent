# Numra Full Analysis Experience — Anbindung an den kanonischen `pythagorean-v2`-Vertrag

## Context

Numra soll kein Zahlen-Dashboard bleiben, sondern nach Eingabe von Name, Geburtsdatum und
Berechnungsdatum eine vollständige, KI-gestützte Closed-Book-Analyse liefern: deterministische
Berechnung → DeepSeek-Bericht → lokale Speicherung → reiterbasierte Darstellung → spätere
Offline-Lesbarkeit.

Der dafür vorgesehene Berechnungsvertrag `pythagorean-v2` (`calculate_profile_v2` /
`ProfileCalculationResultV4`) — der gehaltene Meisterzahlen wie die sekundäre 22/4 neben der
primären 40/4 sichtbar hält, statt sie auf eine bedeutungslose 4 abzuflachen — ist bereits
vollständig implementiert, dokumentiert (`docs/methods/reference-profile-derivations-v2.md`)
und golden-getestet (`tests/golden/reference_profiles_v2.yaml`, Referenzfall Lukas Springer
18.07.1986). Ein dreifacher Code-Audit (Rechenkern/API, Agent/Prompt/Knowledge, Web-UI) hat
bestätigt, dass dieser Vertrag **komplett von der Produktionsoberfläche isoliert** ist: API-Route,
LLM-Analyse-Pipeline, CLI, Web-App und Agent-System-Prompt verwenden ausnahmslos die alte Methode
`pythagorean-v1`.

Dieser Plan wurde zweimal einer fachlichen Gegenprüfung unterzogen. Die erste Runde ergab 15
Korrekturen (u. a. verdeckter Breaking Change am Report-Envelope, fehlende Provider/Intern-Payload-
Trennung, unpräzise Offline-Zustände). Die zweite Runde deckte sieben verbleibende technische
Vertragslücken auf, die vor allem eines gemeinsam haben: **der V1- und der V2/V3-Stack dürfen sich
niemals dieselben Modelle, Unions oder Endpunkte teilen** — jede geteilte Struktur ist ein
potenzieller stiller Breaking Change am bestehenden `/api/v1/`-Vertrag. Konkret:

1. `schema_version`-Felder in den Domainmodellen sind aktuell `str`, nicht `Literal` — eine
   diskriminierte Pydantic-Union ist damit technisch noch nicht möglich.
2. Eine gemeinsame `AnalysisProfile`-Union über V1 und V2 hinweg würde `/api/v1/analyses/report`
   ungewollt für V4-Payloads öffnen und dessen OpenAPI-Vertrag verändern.
3. Die geplante `MetaResponse`-Erweiterung hätte bestehende Felder von `/api/v1/meta` ersetzt statt
   sie unverändert zu lassen.
4. `AgentService`/`AnalysisReport`/`AnalysisDraft`/`ProviderRequest` sind die **produktiven V2-Namen**
   (nicht Altlasten) und dürfen nicht umgebaut werden — der neue 18-Section-Vertrag braucht eigene,
   parallele Klassen.
5. Der bestehende Prompt-Loader (`src/numerology_agent/prompts.py:36-48`) kennt keinen
   Versions-Parameter — neue `-v3.md`-Dateien würden ohne Loader-Änderung nie geladen.
6. `ProviderResult` (`src/numerology_agent/models.py:30-42`) und `DeepSeekProvider.complete()`
   (`src/numerology_agent/deepseek.py:165-192`) lesen `finish_reason` gar nicht aus — ein
   abgeschnittener Bericht (`max_tokens` überschritten) würde unbemerkt als vollständig behandelt.
7. Drei kleinere Schemawidersprüche (nicht-anwendbare Sections dürften laut Claims-Grenze trotzdem
   Claims verlangen; ein einzelner „Fingerprint" vermischt Konfigurations- und Inhaltsidentität;
   das vollständige interne Fact Package sollte nicht standardmäßig serverseitig persistiert werden).

Dieser Plan behebt alle 26 Korrekturen aus den bisherigen Runden. Leitprinzip der finalen Architektur:
**Der V1-Stack (Berechnung, Analyse-API, Meta, Agent-Modelle, Prompts) bleibt in seinen
dokumentierten Erfolgsfällen, Response-Envelopes, Request-Schemas und bestehenden Berechnungen
rückwärtskompatibel. Die einzige bewusste Verhaltensänderung ist die Ablehnung versionsfremder
V2-Anfragen am V1-Profilendpunkt (`version="v2"` → 422 statt stiller Falschberechnung). Der volle
V2/V3-Analyseflow entsteht als vollständig paralleler, neuer Stack** (`/api/v2/*`, `AgentServiceV3`,
`AnalysisReportV3`, `de-report-system-v3.md`, `de-v3.json`, `DeepSeekProviderV3`), der sich mit dem
V1-Stack ausschließlich den unveränderten Rechenkern (`calculate_profile_v2` existiert bereits)
und in der Web-App eine gemeinsame Präsentationsschicht teilt. Bei `/api/v1/analyses/*` und
`/api/v1/meta` bleiben die OpenAPI- und Response-Verträge unverändert.

**Geltungsbereich dieser Planungsrunde:** Es wird kein Produktivcode geändert, nichts committet,
nichts gepusht/gemergt. Das Dokument ist die Grundlage für einen separaten Umsetzungsauftrag.

---

## Versions-Glossar (verbindlich für alle folgenden Abschnitte)

| Achse              | V1-Stack (unverändert)                                                                             | V2/V3-Stack (neu, parallel)                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Berechnungsmethode | `pythagorean-v1`                                                                                   | `pythagorean-v2` (Formeln bereits implementiert, keine Änderung)                                         |
| Profil-Schema      | `ProfileCalculationResult` (`profile-calculation-result-v3`)                                       | `ProfileCalculationResultV4` (`profile-calculation-result-v4`)                                           |
| Profil-Endpunkt    | `POST /api/v1/profiles/calculate` (unverändert + Guard-Fix)                                        | `POST /api/v2/profiles/calculate` (neu)                                                                  |
| Analyse-Endpunkt   | `POST /api/v1/analyses/report`/`follow-up` (unverändert)                                           | `POST /api/v2/analyses/report`/`follow-up` (neu)                                                         |
| Agent-Service      | `AgentService` (unverändert)                                                                       | `AgentServiceV3` (neu)                                                                                   |
| Report-Modelle     | `AnalysisDraft`, `AnalysisReport` (`analysis-report-v2`), `ProviderRequest` (`numra-report-de-v2`) | `AnalysisDraftV3`, `AnalysisReportV3` (`analysis-report-v3`), `ProviderRequestV3` (`numra-report-de-v3`) |
| Prompt-Dateien     | `de-report-system.md`, `de-report-task.md` (unverändert)                                           | `de-report-system-v3.md`, `de-report-task-v3.md` (neu)                                                   |
| Wissens-Bundle     | `de-v2.json`/`KnowledgeBundleV2` (unverändert)                                                     | `de-v3.json` (neu, eigene `bundle_id`)                                                                   |
| Meta-Endpunkt      | `GET /api/v1/meta` (unverändert)                                                                   | `GET /api/v2/meta` (neu, Capability-Vertrag)                                                             |

In Doku/PRs immer explizit benennen, welcher Stack gemeint ist — nie nur „v2".

---

## Bestätigte Audit-Befunde (Kurzform, mit Beleg)

| Befund                                                                                   | Beleg                                                                                                      | Klassifizierung                                             |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| API-Route ignoriert `policy.version`, berechnet immer mit V1                             | `src/numerology_api/routes/profiles.py:11-26`                                                              | V2_NOT_IN_PRODUCTION, PAYLOAD_INFORMATION_LOSS              |
| LLM-Analyse-Pipeline akzeptiert nur V1-Schema                                            | `src/numerology_api/analysis_runtime.py:47-60`                                                             | V2_NOT_IN_PRODUCTION                                        |
| CLI hat keinen Versions-Parameter                                                        | `src/numerology_cli/main.py:97`                                                                            | V2_NOT_IN_PRODUCTION                                        |
| `/api/v1/meta` ist `Literal["v1"]`-typisiert                                             | `src/numerology_api/http_models.py:123,126`                                                                | CALCULATION_CONTRACT_DRIFT                                  |
| Agent-Payload liefert nur reduzierte Zahlen, falscher Profiltyp                          | `src/numerology_agent/service.py:97-148`                                                                   | PAYLOAD_INFORMATION_LOSS, CALCULATION_CONTRACT_DRIFT        |
| System-Prompt erzwingt `pythagorean-v1`                                                  | `src/numerology_agent/prompt_templates/system/de-report-system.md:37`                                      | PROMPT_CONTRACT_DRIFT                                       |
| Section-Liste offen (1–16, Freitext-Titel) statt 18 fester IDs                           | `src/numerology_agent/prompt_templates/tasks/de-report-task.md:19`, `src/numerology_agent/models.py:56-65` | PROMPT_CONTRACT_DRIFT, REPORT_SCHEMA_TOO_GENERIC            |
| Interpretationsschicht nutzt nur `.reduced_value`, `entry_for` verliert Kompound-Kontext | `src/numerology_interpretation/rules.py:38-41`, `src/numerology_knowledge/models.py:165-190`               | CALCULATION_CONTRACT_DRIFT                                  |
| `schema_version`-Felder sind `str`, nicht `Literal`                                      | `src/numerology_domain/_models/profile.py:36,61`                                                           | Diskriminierte Union technisch noch nicht möglich           |
| Prompt-Loader kennt keinen Versions-Parameter                                            | `src/numerology_agent/prompts.py:36-48`                                                                    | Neue Prompt-Dateien würden ohne Loader-Änderung nie geladen |
| `ProviderResult`/`complete()` lesen `finish_reason` nicht aus                            | `src/numerology_agent/models.py:30-42`, `src/numerology_agent/deepseek.py:186-192`                         | Abgeschnittene Berichte unentdeckt                          |
| Web-App sendet hartkodiert `version:"v1"`                                                | `apps/web/src/features/analysis/AnalysisWizard.tsx:66`                                                     | V2_NOT_IN_PRODUCTION                                        |
| Bericht und Zahlen sind getrennte Seiten, keine Tabs, kein ARIA                          | `apps/web/src/features/report/ReportExperience.tsx:224-286`                                                | UX_INFORMATION_ARCHITECTURE_GAP                             |
| Zweiter Bericht pro Profil wird per Exception abgelehnt, keine Versionierung             | `apps/web/src/storage/repository.ts:213-228`, `database.ts:30-35`                                          | PAYLOAD_INFORMATION_LOSS                                    |
| Kein reaktiver Online/Offline-State                                                      | `AnalysisWizard.tsx:80`, `ReportExperience.tsx:88,126`                                                     | OFFLINE_MODE_AMBIGUITY                                      |
| DeepSeek-Request enthält keine Tools/Websuche (bereits korrekt)                          | `src/numerology_agent/deepseek.py`                                                                         | NO_DEFECT                                                   |
| Golden-Tests für Lukas 40/4 primär, 22/4 sekundär korrekt und vollständig                | `tests/golden/reference_profiles_v2.yaml:29-95`, `docs/methods/reference-profile-derivations-v2.md:57-99`  | NO_DEFECT                                                   |

---

## Zielarchitektur / Produktionsgraph (finale Fassung)

```
V1-Stack (unverändert):
  V1-Erfolgsverträge rückwärtskompatibel;
  Analyses- und Meta-Verträge unverändert;
  Profilendpunkt mit dokumentiertem Versions-Guard.
  POST /api/v1/profiles/calculate  → calculate_profile()        → ProfileCalculationResult
  POST /api/v1/analyses/report     → AgentService                → AnalysisReport (analysis-report-v2)
  GET  /api/v1/meta                → MetaResponse (unverändert)

V2/V3-Stack (neu, vollständig parallel):
  PersonInput + MethodPolicy(version="v2")
    → calculate_profile_v2()                       [unverändert, bereits vorhanden]
    → ProfileCalculationResultV4
    → POST /api/v2/profiles/calculate               [NEU]
    → Client speichert V4-Profil
    → POST /api/v2/analyses/report                  [NEU, Request-Modelle mit request_id, ProfileCalculationResultV4 direkt]
    → canonical_analysis_profile_v2()                [NEU, in analysis_runtime_v2.py]
    → build_analysis_fact_package_v3()               [NEU, request-scoped, nicht standardmäßig persistiert]
    → derive_provider_fact_package_v3()              [NEU, minimiert/pseudonymisiert]
    → compose_interpretation_for_profile_v4()        [NEU, lädt de-v3.json]
    → ProviderRequestV3(prompt_version=numra-report-de-v3, facts=ProviderFactPackageV3, plan=18 Section-IDs)
    → DeepSeekProviderV3.complete(...)  [paralleler V3-Provider, finish_reason ausgewertet, Idempotenz über generation_request_id]
    → AnalysisDraftV3 (18 Sections, Längenbudgets, applicable-Validator) → AgentServiceV3._validate_draft_v3()
    → AnalysisReportV3(schema_version=analysis-report-v3, report_id, report_content_hash, generation_context_hash, signiert)
    → Web: ResultsTabs (9 Hauptreiter, WAI-ARIA, 18→9-Mapping clientseitig)
    → IndexedDB: reports (versioniert, unveränderlich, Historie; threads/notes an reportId gebunden)
  GET /api/v2/meta                                   [NEU, Capability-Vertrag]
```

### `/api/v2/analyses/*` akzeptiert `ProfileCalculationResultV4` direkt — keine Union nötig (Korrektur 16)

Da `/api/v2/analyses/*` derzeit ausschließlich V4-Profile akzeptiert, ist weder eine diskriminierte
Union noch eine `Literal`-Verschärfung der bestehenden Domainmodelle erforderlich. Die aktuellen
`schema_version`-Felder (`str`) und die bestehende V1-`AnalysisProfile`-Union bleiben **unverändert**
und byte-identisch — eine Typverschärfung auf `Literal` würde das generierte JSON-Schema der
bestehenden V1-Requestmodelle verändern und damit `/api/v1/analyses/*` im OpenAPI-Vertrag
nicht mehr byte-identisch halten. Deshalb gilt:

```python
class AnalysisReportRequestV2(_HttpModel):     # neu
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4
```

Eine diskriminierte Union (bzw. ein HTTP-spezifischer diskriminierter Wrapper) wird **erst dann**
eingeführt, wenn im V2-API-Vertrag tatsächlich mehrere Profilvarianten existieren. Die bestehenden
Domainmodelle und V1-OpenAPI-Schemas bleiben unverändert.

### Keine geteilte `AnalysisProfile`-Union über API-Versionen hinweg (Korrektur 17)

Die bestehende `AnalysisProfile`-Union (`ProfileCalculationResult | LegacyV2ProfileCalculationResult`)
bleibt **unverändert** und wird ausschließlich von `/api/v1/analyses/*` verwendet. Für den neuen
Pfad wird `ProfileCalculationResultV4` direkt verwendet (keine geteilte Union, keine
`AnalysisProfileV2`-Konstruktion nötig — siehe Korrektur 16):

```python
# unverändert, nur V1/V3
AnalysisProfile = ProfileCalculationResult | LegacyV2ProfileCalculationResult

class AnalysisReportRequest(_HttpModel):       # unverändert
    profile: AnalysisProfile
    ...

# neu, nur V4 — direkt, ohne Union
class AnalysisReportRequestV2(_HttpModel):     # neu
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4

class FollowUpRequestV2(_HttpModel):           # neu, analog für Rückfragen
    ...
```

Damit bleibt die OpenAPI-Spezifikation von `/api/v1/analyses/report` exakt gleich; `/api/v2/analyses/report`
akzeptiert ausschließlich V4-Profile.

### `/api/v1/meta` unverändert, Capability-Vertrag unter `/api/v2/meta` (Korrektur 18)

`GET /api/v1/meta` bleibt exakt wie heute (inkl. `api_version: Literal["v1"]`,
`method_version: Literal["v1"]`). Ein neuer Endpunkt `GET /api/v2/meta` liefert den erweiterten
Fähigkeits-Vertrag. **API-Vertrag und Web-Rollout werden getrennt:** Der V2-Endpunkt ist immer
`v2` (der V2-Rechenkern akzeptiert ausschließlich `policy.version == "v2"`), während der
Produkt-Default erst in Welle 5C wechselt:

```python
class MetaResponseV2(_HttpModel):
    api_version: Literal["v2"] = "v2"
    endpoint_method_version: Literal["v2"] = "v2"
    supported_method_versions: tuple[Literal["v2"], ...] = ("v2",)

    product_default_method_version: Literal["v1", "v2"]
    rollout_stage: Literal["disabled", "opt_in", "canary", "default"]
```

Es gilt:

```text
endpoint_method_version = v2        immer (unabhängig vom Rollout)
product_default_method_version = v1 bis 5C, danach v2
```

`rollout_stage` folgt dem tatsächlichen Produkt-Rollout-Stand (`disabled` → `opt_in`/`canary` →
`default`) und darf dem echten Stand nie voreilen.

Außerdem erhält `/api/v2/profiles/calculate` einen **eigenen stabilen Guard** — nicht nur den
indirekten `PolicyError` des Rechenkerns, der sonst als allgemeiner Berechnungsfehler behandelt
würde:

```text
policy.version != "v2"
→ 422 METHOD_VERSION_MISMATCH
```

Gegenstück dazu ist der V1-Guard (`version != "v1" → 422`) am V1-Profilendpunkt.

### Vollständig paralleler Agent-Service und parallele Dateistruktur (Korrektur 19)

`AgentService`, `AnalysisDraft`, `AnalysisReport` (`analysis-report-v2`), `ProviderRequest`
(`numra-report-de-v2`), `FollowUpDraft`, `AnalysisFollowUp`, `FollowUpProviderRequest` sind die
**produktiven, aktuell von `/api/v1/analyses/*` genutzten Namen** und werden nicht verändert oder
umgebaut. Der neue 18-Section-Vertrag entsteht als eigenständige, parallele Klassenfamilie. Um V3
**konsequent aus gemeinsamen Dateien herauszulösen**, entsteht pro V3-Art eine eigene Datei — die
bestehenden Dateien bleiben vollständig unverändert:

```text
src/numerology_agent/models.py          unverändert
src/numerology_agent/prompts.py         unverändert
src/numerology_agent/service.py         unverändert
src/numerology_agent/provider.py        unverändert
src/numerology_agent/deepseek.py        unverändert

src/numerology_agent/models_v3.py       neu
src/numerology_agent/prompts_v3.py      neu
src/numerology_agent/service_v3.py      neu
src/numerology_agent/provider_v3.py     neu
src/numerology_agent/deepseek_v3.py     neu
```

Die V3-Klassenfamilie (in `models_v3.py`):

```text
AnalysisDraftV3           (neu)
AnalysisReportV3          (neu, schema_version="analysis-report-v3")
ProviderRequestV3         (neu, prompt_version="numra-report-de-v3")
FollowUpDraftV3           (neu)
AnalysisFollowUpV3        (neu)
FollowUpProviderRequestV3 (neu)
```

Ebenso für die Interpretation:

```text
numerology_interpretation/service.py       unverändert
numerology_interpretation/service_v3.py    neu
```

`canonical_analysis_profile_v2()` (neu, in `src/numerology_api/analysis_runtime_v2.py`) ergänzt den
API-Stack. Rollback erfolgt durch Router-/Feature-Flag-Umschaltung (den `/api/v2/analyses/*`-Router
aus `app.py` entfernen bzw. deaktivieren), nicht durch verzweigte Logik innerhalb des produktiven
`AgentService`. Das eliminiert jedes Regressionsrisiko für den bestehenden V1-Analysepfad.

### V3-Prompt-Loader parallel statt Erweiterung (Korrektur 20)

`src/numerology_agent/prompts.py` bleibt **unverändert** (inkl. unverändertem globalem Default).
Stattdessen entsteht `src/numerology_agent/prompts_v3.py`, das den bestehenden Low-Level-Loader
verwendet und explizit die V3-Dateien lädt:

```python
# prompts_v3.py (neu) — nutzt intern load_prompt aus prompts.py
def system_prompt_v3(locale: str = "de") -> str:
    return load_prompt("system", f"{locale}-report-system-v3")

def report_task_prompt_v3(locale: str = "de") -> str:
    return load_prompt("tasks", f"{locale}-report-task-v3")
```

Damit muss der bestehende globale Prompt-Default **überhaupt nicht verändert** werden.
`DeepSeekProviderV3` (siehe Korrektur 21) verwendet fest den V3-Promptvertrag und wird von
`AgentServiceV3` verwendet; der bestehende `DeepSeekProvider` (V1) lädt weiterhin die V2-Prompts.

### Paralleler Provider-Stack mit `finish_reason` (Korrektur 21)

`ProviderResult`, `LlmProvider` und `DeepSeekProvider` sind die **produktiven V1-Verträge** und
werden nicht erweitert (der bestehende Vertrag lautet `complete(payload, schema) -> ProviderResult`
ohne `finish_reason`; `ProviderResult` wird in bestehenden Unit-/Integrationstests direkt
konstruiert). Der V3-Stack bekommt eine eigene, parallele Providerfamilie:

```python
class ProviderResultV3(_AgentModel):   # neu
    content: str
    model: str
    finish_reason: str                 # NEU
    provider_fingerprint: str | None = None
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
```

```python
class LlmProviderV3(Protocol):         # neu
    async def complete(
        self,
        payload: dict[str, Any],
        schema: dict[str, Any],
    ) -> ProviderResultV3: ...
```

`DeepSeekProviderV3` verwendet fest den V3-Promptvertrag — dadurch braucht `complete()` keinen
zusätzlichen `prompt_version`-Parameter. Die gemeinsamen Low-Level-Helfer für HTTP, Retry und
Fehlerklassifikation dürfen intern wiederverwendet werden, solange die öffentlichen Verträge
getrennt bleiben. In `DeepSeekProviderV3.complete()`:

```python
choice = body["choices"][0]
content = choice["message"].get("content")
finish_reason = str(choice.get("finish_reason", ""))
if not isinstance(content, str) or not content.strip():
    raise ProviderError("LLM provider returned empty content")
return ProviderResultV3(content=content, finish_reason=finish_reason, ...)
```

Verbindliche Klassifikation aller `finish_reason`-Fälle (nicht nur `length`):

| `finish_reason`                | Behandlung                                                                        |
| ------------------------------ | --------------------------------------------------------------------------------- |
| `stop`                         | normal validieren                                                                 |
| `length`                       | höheres Budget (max. ein Zusatzversuch), danach Kapitelstrategie oder Fail-Closed |
| `content_filter`               | Fail-Closed, keine Teilantwort speichern                                          |
| `tool_calls`                   | Provider-Vertragsverletzung, da keine Tools angeboten werden                      |
| `insufficient_system_resource` | transienter Retry                                                                 |
| leer/unbekannt                 | Fail-Closed und Telemetrie                                                        |

Verbindliche Strategie bei `finish_reason == "length"` (nicht nur identischer Retry):

1. Nicht als gültigen Bericht akzeptieren/speichern.
2. Maximal ein kontrollierter Zusatzversuch mit erhöhtem `max_output_tokens` (innerhalb der
   Codegrenze `≤ 32_768`, `deepseek.py:62`).
3. Bleibt es bei `length`, entweder auf eine Kapitel-Orchestrierung (siehe „Ein LLM-Call"-Abschnitt)
   wechseln oder fail-closed mit einer für den Nutzer verständlichen Fehlermeldung abbrechen — nie
   einen unvollständigen Bericht stillschweigend als vollständig ausliefern.
4. Die `max_output_tokens ≤ 32_768`-Codegrenze wird in der Welle-5-Evaluation explizit als
   Kalibrierungs-Obergrenze berücksichtigt.
5. Hinweis: Im Thinking Mode werden Temperatur und `top_p` weiterhin nicht unterstützt bzw.
   ignoriert (DeepSeek API Docs) — in der Welle-5-Evaluation entsprechend behandeln.

### Drei Schema-Korrekturen (Korrektur 22)

**A. Nicht-anwendbare Sections dürfen keine Claims erzwingen:**

```python
@model_validator(mode="after")
def validate_applicability(self) -> "AnalysisSectionV3":
    if self.applicable:
        if not 1 <= len(self.claims) <= 4:
            raise ValueError("applicable section requires 1-4 claims")
    else:
        if self.claims or self.supporting_calculation_refs or self.supporting_knowledge_refs:
            raise ValueError("non-applicable section must contain no claims or references")
    return self
```

**B. Getrennte Hash-/ID-Konzepte statt eines einzelnen „Fingerprints":**

```text
generation_context_hash  = Hash über die KONFIGURATION eines Laufs
                            (identifiziert die KONFIGURATION eines Laufs — zwei Läufe mit derselben
                            Konfiguration können unterschiedliche Texte erzeugen)
report_content_hash      = Hash des kanonisch serialisierten, fertigen Reports (identifiziert den
                            KONKRETEN Inhalt)
report_id                = UUID der konkreten Berichtsversion (Primärschlüssel in der Historie)
```

**Exakte Projektion für `generation_context_hash`** (eine bloße Versionsbezeichnung reicht nicht,
falls eine Promptdatei irrtümlich unter derselben Versionsnummer verändert wird):

```text
calculation_hash
profile_schema_version
method_version
provider_fact_package_hash
capability_matrix_version
prompt_version
prompt_content_hash
knowledge_bundle_id
knowledge_content_hash
report_schema_version
model
thinking_mode
reasoning_effort
orchestration_version
```

**Exakte Projektion für `report_content_hash`** — Hash über kanonisch serialisierte Inhalte:

```text
schema_version
summary
sections
limitations
suggestions
```

Nicht enthalten: `report_content_hash` selbst, `context_signature`, `report_id`, Tokenverbrauch,
Zeitstempel, Provider-Fingerprint.

**Verbindliche Reihenfolge der Envelope-Bildung:**

```text
1. Reportinhalt validieren
2. report_content_hash berechnen
3. generation_context_hash einsetzen
4. report_id erzeugen
5. finale Envelope bilden
6. context_signature über die Envelope ohne context_signature berechnen
```

Dafür sind explizite Stabilitätstests erforderlich. `context_signature` (HMAC, bestehender
Mechanismus in `service.py:80-95`) signiert weiterhin den vollständigen Bericht und bleibt
unverändert in seiner Funktion.

**Kanonische Serialisierung als Algorithmus festschreiben** (damit Hashes reproduzierbar und
idealiter sprachübergreifend prüfbar sind):

```python
json.dumps(
    projection,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

Falls Hashes später auch in TypeScript geprüft werden sollen, ist ein sprachübergreifend
festgelegtes kanonisches JSON-Verfahren vorzuziehen (z. B. [RFC 8785 / JCS]).

**C. Internes Fact Package nicht standardmäßig serverseitig persistieren:**

`AnalysisFactPackageV3` (das vollständige, aus `AnalysisFactEntryV3`-Entries aufgebaute Objekt) ist
**request-scoped/transient** — wird für den Provider-Aufruf gebaut und danach verworfen, nicht
geloggt und nicht standardmäßig in einer Datenbank/einem Audit-Log gespeichert. In
`AnalysisProvenance` werden nur `calculation_hash`, die Versionskennungen (`method_version`,
`prompt_version`, `knowledge_bundle`, `report_schema_version`) und die tatsächlich verwendeten
Referenz-IDs (`calculation_ref`/`knowledge_ref` je Claim, bereits heute vorhanden) gespeichert —
das reicht für vollständige Nachvollziehbarkeit/Audit, ohne die serverseitige Datenhaltung
personenbezogener Ableitungen unnötig auszuweiten.

### API-Idempotenz für Berichtserzeugung und Follow-ups (Korrektur 23)

`report_id` (UUID), `generation_context_hash` und `report_content_hash` verhindern allein noch
keinen Doppelbericht bei Netzwerk-Retry: Wenn der Client die Berichtsanfrage sendet, der Server den
Bericht erfolgreich erzeugt, aber die Antwort im Netzwerk verloren geht, erzeugt eine wiederholte
Anfrage einen zweiten Bericht mit neuer UUID. Deshalb trägt jeder V2-Analyserequest eine vom Client
erzeugte stabile Request-ID — **sowohl Berichtserzeugung als auch Follow-ups** (eine Rückfrage kann
genauso doppelt erzeugt werden):

```python
class AnalysisReportRequestV2(_HttpModel):      # neu
    generation_request_id: UUID                 # Idempotenz-Key der Berichtserzeugung
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4

class AnalysisFollowUpRequestV2(_HttpModel):    # neu
    follow_up_request_id: UUID                  # Idempotenz-Key des Follow-ups
    consent: Literal[True]
    device_id: str
    profile: ProfileCalculationResultV4
    report: AnalysisReportV3
    question: str
```

(Alternativ neutral einheitlich `request_id` in beiden Modellen — eine Benennung wird bei der
Implementierung festgelegt.) Der Idempotenzschlüssel setzt sich zusammen aus
`pseudonymous_device_key + operation_type + request_id`, damit Berichtserzeugung und Follow-ups
nicht miteinander kollidieren.

#### Eigener IdempotencyStoreV3-Vertrag (nicht den RateLimiter zweckentfremden)

Der bestehende `RateLimiter` bietet nur ein `consume()`-Verfahren und ist dafür ungeeignet. Es
entsteht ein separater Vertrag, der **sowohl Berichte als auch Follow-ups** speichert:

```python
class IdempotencyStoreV3(Protocol):
    async def acquire(
        self,
        *,
        key: str,
        request_context_hash: str,
        operation: Literal["report", "follow_up"],
        ttl_seconds: int,
    ) -> AcquireResultV3: ...

    async def complete(
        self,
        *,
        key: str,
        owner_token: str,
        response_type: Literal["report", "follow_up"],
        encrypted_response: bytes,
    ) -> None: ...

    async def fail(
        self,
        *,
        key: str,
        owner_token: str,
        error_code: str,
        retryable: bool,
    ) -> None: ...
```

Der Redis-Zugriff muss atomar über `SET NX` oder ein Lua-Skript erfolgen. Zustände: `PENDING`,
`COMPLETED`, `FAILED`, plus Besitzer-/Lock-Token (`owner_token`) und Ablaufzeit für abgestürzte
Prozesse.

**Request-Context-Hash** (ersetzt die reine `calculation_hash`-Konfliktprüfung, die bei Follow-ups
nicht ausreicht — sonst würde bei gleichem Key, gleichem Hash, aber anderer Frage fälschlich die
Antwort auf die erste Frage zurückgegeben):

Für Berichte (`operation="report"`):

```text
operation_type
calculation_hash
generation_context_hash
report_schema_version
```

Für Follow-ups (`operation="follow_up"`):

```text
operation_type
calculation_hash
report_id
report_content_hash
normalisierte Frage
follow_up_prompt_version
```

Damit führt derselbe Key mit verändertem Inhalt zuverlässig zu `409 IDEMPOTENCY_KEY_CONFLICT`.

**Semantik nach `FAILED`:**

- retryfähiger Fehler (`retryable=True`): derselbe Key darf kontrolliert neu übernommen werden;
- nicht retryfähiger Fehler (`retryable=False`): dieselbe Fehlerantwort wird wiedergegeben, oder der
  Key bleibt bis zur TTL gesperrt.

#### Verbindliche Reihenfolge: Idempotenz **vor** Rate-Limit

Wird zuerst das Geräte-/IP-Kontingent verbraucht, blockiert das Rate-Limit einen Wiederholungsversuch
nach verlorener HTTP-Response, bevor die gespeicherte idempotente Response erreicht wird. Deshalb:

```text
1. Request validieren
2. kanonisches Profil prüfen
3. Idempotency-Key suchen
4. vorhandene fertige Response zurückgeben
5. laufende Generierung erkennen
6. atomaren Idempotency-Lock erwerben
7. erst jetzt Rate-Limit verbrauchen
8. Provider aufrufen
9. Response speichern
10. Lock auf COMPLETED setzen
```

Nur der Besitzer eines **neuen** Idempotency-Keys darf Kontingent verbrauchen.

#### Cache-Privacy und TTL

Numra speichert Profile und Berichte nicht dauerhaft serverseitig. Zur zuverlässigen Idempotenz darf
die **verschlüsselte** Analyse-Response kurzzeitig mit fester TTL gespeichert werden:

- verschlüsselte Ablage mit eigenem Verschlüsselungsschlüssel,
- keine Klarnamen im Redis-Key,
- keine Inhalte in Logs,
- feste Löschung durch TTL ohne Verlängerung durch Reads,
- dokumentierte maximale Aufbewahrung.

Anfangs werden **1 bis 6 Stunden** statt pauschal 24 Stunden angesetzt; eine längere Frist muss aus
realen Retry-/Nutzungsmustern begründet werden.

Verhalten:

| Zustand                                  | Antwort                                |
| ---------------------------------------- | -------------------------------------- |
| gleicher Key, Generierung läuft          | `202` oder definierter Conflict-Status |
| gleicher Key, Generierung abgeschlossen  | identische gespeicherte Response       |
| gleicher Key, anderer `calculation_hash` | `409 IDEMPOTENCY_KEY_CONFLICT`         |
| neuer Key                                | neue Berichtsgenerierung               |

Zusätzliche Tests:

```text
gleicher Idempotency-Key + gleicher Kontext     → gleicher report_id und gleicher Bericht
gleicher Key + anderer calculation_hash         → 409
Netzwerk-Retry nach erfolgreicher Generierung   → kein zweiter Provider-Aufruf
parallele Requests mit gleichem Key             → genau ein aktiver Provider-Aufruf
Follow-up-Retry                                 → keine zweite KI-Antwort
```

### Dependency-Wiring für den parallelen Stack (Korrektur 24)

Der bestehende App-Container kennt nur `provider`, `rate_limiter`, `circuit_breaker`;
`production_dependencies()` erzeugt aktuell ausschließlich den bestehenden `DeepSeekProvider` und
den Rate-Limiter. Der neue Stack braucht zusätzlich `provider_v3`, `circuit_breaker_v3`,
`idempotency_store_v3` und `v3_analysis_enabled`.

**Interfaces und Settings entstehen in Welle 1** (damit `create_app` typisiert erweiterbar ist,
ohne dass die Welle-3-Implementierungen bereits vorliegen):

```text
provider_v3.py:
- LlmProviderV3 Protocol
- ProviderResultV3

idempotency.py:
- IdempotencyStoreV3 Protocol
- AcquireResultV3
- Status-Enums

dependencies_v3.py:
- Settings und Factory-Schnittstellen
```

`create_app` wird entsprechend erweitert:

```python
def create_app(
    settings: ApiSettings | None = None,
    *,
    provider: LlmProvider | None = None,
    provider_v3: LlmProviderV3 | None = None,
    rate_limiter: RateLimiter | None = None,
    idempotency_store: IdempotencyStoreV3 | None = None,
) -> FastAPI:
    ...
```

Und am App-State verfügbar gemacht:

```text
api.state.provider
api.state.provider_v3
api.state.circuit_breaker
api.state.circuit_breaker_v3
api.state.rate_limiter
api.state.idempotency_store
```

**Die konkreten Implementierungen folgen in Welle 3** (erst wenn die V3-Verträge vollständig sind):

```text
DeepSeekProviderV3
RedisIdempotencyStoreV3
AgentServiceV3
/api/v2/analyses/*
```

Kritische Dateien: `src/numerology_api/app.py`, `src/numerology_api/dependencies.py`,
`src/numerology_api/dependencies_v3.py` (oder ein `ProviderRegistry`). Ohne dieses Wiring ist der
parallele Stack nicht ausführbar.

### OpenAPI-Artifact-Strategie (Korrektur 25)

Der bestehende Exporter (`scripts/export_openapi.py`) schreibt die OpenAPI-Spezifikation der
**gesamten App** fest nach `openapi/numra-v1.json`; auch die Web-App (`apps/web/package.json`,
`pnpm web:generate-api`) generiert ihre Typen fest aus dieser Datei. Sobald `/api/v2/*` in dieselbe
FastAPI-App aufgenommen wird, enthielte `numra-v1.json` auch V2-Pfade — der Dateiname wäre falsch und
das Gesamtdokument nicht mehr byte-identisch.

**Gewählte Lösung — gemeinsames API-Dokument mit V1-Schema-Closure:**

```text
openapi/numra-api.json                 # enthält V1 und V2 (vollständiges Gesamtdokument)
openapi/contracts/v1-contract.json     # Contract-Snapshot mit Schema-Closure
```

Ein reiner Pfad-Snapshot reicht **nicht**: Ein V1-Pfad kann dieselbe `$ref`-Adresse verwenden,
während das referenzierte Schema unter `components.schemas` verändert wurde. `v1-contract.json`
enthält daher:

- ausgewählte V1-Pfade,
- zugehörige Operationen,
- **rekursiv alle referenzierten `components.schemas`** (Schema-Closure),
- relevante Responses,
- Security Schemes,
- Parameter,
- kanonisch sortierte Serialisierung.

**Beide kritischen Dateien werden umgestellt:** `scripts/export_openapi.py` schreibt nach
`openapi/numra-api.json`, und `apps/web/package.json` (`pnpm web:generate-api`) liest aus
`openapi/numra-api.json`. Die Web-App generiert aus `numra-api.json`.

Der Plan verlangt daher **nicht** „gesamte OpenAPI-Datei byte-identisch", sondern präzise:

```text
Request-/Response-Schemas und Operations der bestehenden /api/v1/analyses/*- und
/api/v1/meta-Pfade bleiben unverändert (inkl. referenzierter Schema-Closure).
```

### Gesamtgrößenbudget für Bericht und Follow-up-Request (Korrektur 26)

Das globale HTTP-Request-Limit liegt standardmäßig bei **65.536 Bytes**. Ein V3-Follow-up enthält
vollständiges V4-Profil, vollständigen Bericht (18 Sections), Claims, Referenzen, Gegenhypothesen,
Fragen, Optionen, Provenienz und Signaturen — und kann trotz einzelner Section-Limits das bestehende
Limit überschreiten.

**Keine feste 48–56-KiB-Spanne vorab festlegen.** Stattdessen wird das Berichtslimit rechnerisch
aus dem Follow-up-Budget abgeleitet:

```text
MAX_CANONICAL_REPORT_BYTES
=
MAX_FOLLOW_UP_REQUEST_BYTES
- MAX_SERIALIZED_V4_PROFILE_BYTES
- MAX_SERIALIZED_QUESTION_BYTES
- ENVELOPE_OVERHEAD_BYTES
- SAFETY_MARGIN_BYTES
```

Das wird mit zwei Korpora getestet:

1. Golden-Referenzprofile,
2. zulässige Maximalfälle mit langen Namen, aktivem Namen und umfangreichen Traces.

Beispieltest:

```python
payload_size = len(
    request.model_dump_json().encode("utf-8")
)
assert payload_size <= configured_v2_follow_up_limit
```

Erst danach wird entschieden:

- den Bericht kleiner halten, **oder**
- ausschließlich für `/api/v2/analyses/follow-up` ein höheres, geprüftes, pfadspezifisches Limit
  einführen.

Ein globales Hochsetzen verändert die Sicherheitsgrenze aller Endpunkte und wird vermieden.

---

## Endpoint-Übersicht (final)

```text
/api/v1/profiles/*   → V1-Berechnung, unverändert (+ Guard-Fix: version="v2" → 422)
/api/v1/analyses/*    → analysis-report-v2, unverändert
/api/v1/meta          → unverändert

/api/v2/profiles/*    → pythagorean-v2 / ProfileCalculationResultV4
/api/v2/analyses/*    → analysis-report-v3 (AgentServiceV3)
/api/v2/meta          → Capability-/Versionsvertrag (MetaResponseV2)
```

---

## Analysis Fact Entry und Fact Package — präzise Trennung

Die 15 genannten Felder gehören nicht zum gesamten Package, sondern zu **einem einzelnen
Berechnungsfakt**. Der Vertrag unterscheidet einen Entry vom Package:

```python
class AnalysisFactEntryV3(_FrozenModel):
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

```python
class AnalysisFactPackageV3(_FrozenModel):
    calculation_hash: str
    profile_schema_version: str
    method_version: str
    entries: tuple[AnalysisFactEntryV3, ...]
```

Dazu gilt:

- `trace_ref` ist eine **Referenz**; eine vollständige Trace-Auflösung heißt `trace_steps` bzw.
  `resolved_trace`.
- Der Provider erhält ausschließlich die opake Referenz bzw. eine gezielt minimierte Erklärung.

Zwei getrennte, request-scoped Verträge (siehe Korrektur 22C zur Persistenz):

- `AnalysisFactPackageV3` (intern, vollständig, transient) — lebt nur für die Dauer des Requests.
- `ProviderFactPackageV3` (an DeepSeek gesendet, Closed-Book-minimiert) — abgeleitet via
  `derive_provider_fact_package_v3()`: `trace_ref` nur als opake Kennung, keine normalisierten
  Namen/Buchstabenfolgen, keine überschüssigen Geburtsdatumskomponenten, keine Audit-Metadaten.

---

## Wissenspaket-Unveränderlichkeit und V3-Wissensmodell

`de-v2.json`/`KnowledgeBundleV2` bleiben byte-identisch und weiterhin ladbar (bestehende Berichte
referenzieren dieses Bundle über `provenance.knowledge_bundle`). Für die V2/V3-Anbindung entsteht
`de-v3.json` mit eigener `bundle_id` (`numra-knowledge-de-v3`) und eigener Inhaltsversion
(`life_path_primary`/`life_path_secondary` als getrennte `result_context`-Werte).

Das bestehende Modell kann dieses Bundle nicht validieren (`KnowledgeEntryV2.method_system` erlaubt
nur `pythagorean-v1`, `ResultContext` kennt `life_path_primary`/`life_path_secondary` nicht,
`KnowledgeBundleV2.version` ist auf `"v2"` begrenzt; der Loader kennt nur `v1`/`v2`). Deshalb entsteht
ein paralleles V3-Wissensmodell:

```text
src/numerology_knowledge/models.py      unverändert
src/numerology_knowledge/loader.py      unverändert

src/numerology_knowledge/models_v3.py   neu
src/numerology_knowledge/loader_v3.py   neu
```

Mindestens:

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

```python
class KnowledgeEntryV3(_KnowledgeModel):
    method_system: Literal["pythagorean-v2"] = "pythagorean-v2"
    result_contexts: tuple[ResultContextV3, ...]
    ...
```

```python
class KnowledgeBundleV3(_KnowledgeModel):
    version: Literal["v3"] = "v3"
    entries: tuple[KnowledgeEntryV3, ...]
```

Der V3-Resolver sollte bei **mehreren Treffern nicht** wieder `candidates[0]` zurückgeben, sondern
bei Uneindeutigkeit fail-closed abbrechen.

**Wichtig:** Das Bundle wird **nicht** automatisch anhand von `profile.schema_version` ausgewählt —
Profil- und Wissensversion sind laut Versionsarchitektur unabhängige Achsen. Stattdessen wird
explizit geladen:

```python
bundle = load_knowledge_bundle_v3(
    locale="de",
    bundle_id="numra-knowledge-de-v3",
)
```

bzw. explizit in `AgentServiceV3` konfiguriert.

---

## Offline-Zustände

Die Berechnung läuft weiterhin serverseitig (`/api/v2/profiles/calculate`) — sie ist **nicht**
offline verfügbar (eine echte Rechenkern-Portierung wäre ein eigener, hier nicht enthaltener
Stream). Vier präzise Zustände statt der ursprünglich drei:

```text
PROFILE_CALCULATION_REQUIRES_NETWORK
REPORT_GENERATION_REQUIRES_NETWORK
SAVED_PROFILE_AVAILABLE_OFFLINE
SAVED_REPORT_AVAILABLE_OFFLINE
```

---

## „Ein LLM-Call" als UX-, nicht Provider-Vertrag

Verbindlich bleibt der UX-Vertrag: ein Nutzerauftrag erzeugt genau eine Berichtsversion, ein
Reiterwechsel löst nie einen weiteren Aufruf aus. Ob das Backend dafür intern einen einzigen
Provider-Request nutzt oder (bei wiederholtem `finish_reason=="length"`, siehe Korrektur 21) auf
mehrere deterministisch orchestrierte Kapitel-Calls umschaltet, wird erst nach der
Welle-5-Evaluation entschieden und ändert den UI-Vertrag nicht.

---

## Längenbudgets und Kapazitätsmatrix pro Section

```text
summary:               max. 800 Zeichen (executive_overview/final_synthesis: max. 1400)
claims:                1-4 bei applicable=true, 0 bei applicable=false (Korrektur 22A)
counter_hypotheses:    0-2
reflection_questions:  0-2
practical_options:     0-2
limitations:           0-1
method_and_calculation_notes: kurz — Rechenweg wird deterministisch gerendert, nicht in Prosa nachgebaut
```

Pro Section liefert das Backend vor dem Prompt-Bau eine Capability-Angabe
(`{"section_id": "...", "supported": false, "reason_code": "..."}`) für Abschnitte ohne
vollständige deterministische Datengrundlage; ist eine Section nicht unterstützt, MUSS
`applicable=false` gesetzt sein (Validator siehe Korrektur 22A) — DeepSeek darf sie nicht selbst
erraten oder nachberechnen.

---

## Stabile UI-Labels

`section_id` bestimmt die Navigation über eine feste, im Frontend hinterlegte
`SECTION_UI_LABELS`-Tabelle — nicht der vom Modell gelieferte Freitext. `AnalysisSectionV3` behält
ein optionales `model_heading`-Feld für eine inhaltliche Zwischenüberschrift, das nie Navigation,
Deep-Link-Slug oder ARIA-Label bestimmt.

---

## Implementierungswellen

### Welle 0 — Vertrags- und Releaseentscheidungen

1. ADR: `pythagorean-v2` als künftiger Default für neue Profile (Web-Default-Wechsel erst Welle 5C).
2. ADR: strikt paralleler Stack `/api/v2/*` (Profile, Analysen, Meta) — keine geteilten Unions/Modelle mit V1, konsequent parallele Dateistruktur `*_v3.py` (Korrekturen 17–19).
3. ADR: `ProfileCalculationResultV4` direkt in `/api/v2/analyses/*` — **keine** `Literal`-Verschärfung der bestehenden Domainmodelle, keine Union (Korrektur 16).
4. ADR: Unveränderlichkeit von `de-v2.json`; `de-v3.json` als neues Bundle.
5. ADR: Trennung `AnalysisFactPackageV3` (transient, nicht persistiert) vs. `ProviderFactPackageV3` (Closed-Book-minimiert) (Korrektur 22C) sowie `AnalysisFactEntryV3` vs. Package (Korrektur 10).
6. ADR: `finish_reason`-Klassifikationsmatrix im parallelen V3-Provider-Stack inkl. Retry-/Abbruch-/Kapitel-Eskalationsstrategie (Korrektur 21).
7. ADR: API-Idempotenz über `request_id` für Bericht **und** Follow-up (Korrektur 23), `IdempotencyStoreV3`-Vertrag, Request-Context-Hash, Prüf-Reihenfolge vor Rate-Limit, TTL (1–6 h), 409-Konfliktverhalten.
8. ADR: Dependency-Wiring des parallelen Stacks (`provider_v3`, `circuit_breaker_v3`, `idempotency_store`, `v3_analysis_enabled`; Korrektur 24).
9. ADR: OpenAPI-Artifact-Strategie (`openapi/numra-api.json` + `openapi/contracts/v1-contract.json` inkl. Schema-Closure; Korrektur 25).
10. ADR: Gesamtgrößenbudget — `MAX_CANONICAL_REPORT_BYTES` als Formel aus dem Follow-up-Budget (Korrektur 26) inkl. Zwei-Korpus-Test (Golden + Maximalfälle).
11. ADR: Hash-/Signaturkanonisierung — exakte Projektionen für `generation_context_hash` und `report_content_hash`, Envelope-Reihenfolge (Korrektur 11).
12. Capability-Matrix der 18 Sections erstellen.
13. Report-Längenbudget je Section festlegen.
14. Golden-End-to-End-Testfall für Lukas über den vollständigen V2/V3-Graphen festlegen (Abnahmekriterium für Wellen 1–5C).
15. Mobile Darstellungsstrategie für 9 Reiter festlegen.
    Abnahme: alle Punkte als ADRs/Entscheidungsnotizen vorliegend, bevor Welle 1 beginnt.

### Welle 1 — API-Grundlage (noch keine aktive V2-Berichtserzeugung)

- `src/numerology_api/routes/profiles.py`: Guard `policy.version != PYTHAGOREAN_V1_VERSION → 422 METHOD_VERSION_MISMATCH`.
- Neu `src/numerology_api/routes/profiles_v2.py`: `POST /api/v2/profiles/calculate` → `calculate_profile_v2`, mit eigenem stabilem Guard `policy.version != "v2" → 422 METHOD_VERSION_MISMATCH` (Korrektur 18).
- Neu `src/numerology_api/routes/meta_v2.py`: `GET /api/v2/meta` mit `MetaResponseV2` (Korrektur 18, `endpoint_method_version="v2"`, `product_default_method_version="v1"`, `rollout_stage="disabled"` in dieser Welle) — `routes/meta.py` (V1) bleibt unverändert.
- Neu `src/numerology_api/analysis_runtime_v2.py`: `canonical_analysis_profile_v2()` (Korrektur 19).
- Dependency-Wiring-Interfaces: `provider_v3.py` (`LlmProviderV3`-Protocol, `ProviderResultV3`), `idempotency.py` (`IdempotencyStoreV3`-Protocol, `AcquireResultV3`, Status-Enums); `create_app` typisiert um `provider_v3`, `idempotency_store_v3` erweiterbar; `api.state.*` befüllen (Korrektur 24).
- V2-Settings und Dependency-Schnittstellen (`dependencies_v3.py` bzw. `ProviderRegistry`).
- OpenAPI-Grundvertrag: gemeinsames `openapi/numra-api.json`, V1-Contract-Snapshot `openapi/contracts/v1-contract.json` inkl. Schema-Closure; `scripts/export_openapi.py` und `apps/web/package.json` auf `numra-api.json` umstellen (Korrektur 25).
- `src/numerology_cli/main.py`: `--method-version`-Option.
- Abnahme: bestehende Suite grün, neue Tests in `tests/integration/test_http_api.py` (200 auf `/api/v2/profiles/calculate`, 422 auf `/api/v1/profiles/calculate` mit `version="v2"`, `/api/v1/analyses/report`+`/api/v1/meta` unverändert; V1-Pfad-Snapshot identisch). **Keine** aktive V2-Analyse-Pipeline in dieser Welle.

### Welle 2 — Fakten und Wissen

- Neu in `src/numerology_agent/models_v3.py`: `AnalysisFactEntryV3`, `AnalysisFactPackageV3`, `ProviderFactPackageV3` (Korrektur 10) — `models.py` bleibt unverändert.
- Neu: `build_analysis_fact_package_v3()`, `derive_provider_fact_package_v3()` (request-scoped, Korrektur 22C) — bestehende `_facts()`/`build_provider_payload()` in `service.py` bleiben unverändert und weiterhin von `AgentService` genutzt.
- Neu `src/numerology_knowledge/data/de-v3.json` (eigene `bundle_id`, `life_path_primary`/`life_path_secondary`-Kontexte); `de-v2.json` unverändert.
- Neu `numerology_interpretation/service_v3.py`: `compose_interpretation_for_profile_v4()` — Klassifikation aus `NumberModel`-Feldern, lädt `de-v3.json`; `service.py` bleibt unverändert.
- Capability-Matrix der 18 Sections (aus Welle 0, Punkt 12) als Datenmodell/Referenzdatei ablegen.
- Abnahme: `tests/unit/test_analysis_fact_package.py` (neu, `AnalysisFactEntryV3`/`AnalysisFactPackageV3`, keine Meisterzahl-Verkürzung, `ProviderFactPackageV3`-Minimierung, keine Persistenz standardmäßig), `tests/unit/test_knowledge_v3.py` (neu, eindeutige Treffer gegen `de-v3.json`), bestehende `test_agent.py`/`test_interpretation.py` unverändert grün.

### Welle 3 — Berichtserzeugung (V3-Report, Provider, Service, Prompts, Idempotenz, `/api/v2/analyses/*`)

- Neu in `src/numerology_agent/models_v3.py`: `AnalysisSectionV3`, `AnalysisDraftV3`, `AnalysisReportV3` (`schema_version="analysis-report-v3"`), `ProviderRequestV3`, `FollowUpDraftV3`, `AnalysisFollowUpV3`, `FollowUpProviderRequestV3` — inkl. Pflichtfeldern (`section_id`, `model_heading`), Längenbudgets, `applicable`-Validator (Korrektur 22A).
- Neu `src/numerology_agent/provider_v3.py`/`deepseek_v3.py`: `LlmProviderV3`, `ProviderResultV3` (mit `finish_reason`), `DeepSeekProviderV3` (paralleler V3-Provider, Korrektur 21, inkl. vollständiger `finish_reason`-Matrix) — `provider.py`/`deepseek.py` (V1) bleiben unverändert.
- Neu `src/numerology_agent/prompts_v3.py` (lädt `de-report-system-v3.md`/`de-report-task-v3.md`; Korrektur 20) — `prompts.py` bleibt unverändert.
- Neue Prompt-Dateien `de-report-system-v3.md`/`de-report-task-v3.md`: ersetzen die `pythagorean-v1`-Zwangsregel, listen die 18 Section-IDs mit festen UI-Labels, Pflichtfeldern, Längenbudgets, Capability-Hinweisen.
- Neu `src/numerology_agent/service_v3.py`: `AgentServiceV3` mit `_validate_draft_v3()` (Section-ID-Vollständigkeit/-Reihenfolge) und `finish_reason`-Strategie (Korrektur 21).
- Hash-/Signaturkanonisierung nach Korrektur 11 (exakte Projektionen + Envelope-Reihenfolge + Stabilitätstests).
- Neu `RedisIdempotencyStoreV3` (Korrektur 23, Implementierung): `acquire`/`complete`/`fail`, atomar via `SET NX`/Lua, Zustände `PENDING`/`COMPLETED`/`FAILED`, TTL 1–6 h, verschlüsselte Ablage, Request-Context-Hash-Konfliktprüfung; Prüf-Reihenfolge vor Rate-Limit (Interface aus Welle 1, Korrektur 24).
- Neu `src/numerology_api/routes/analyses_v2.py`: `POST /api/v2/analyses/report`/`follow-up`, Request-Modelle mit `generation_request_id`/`follow_up_request_id` und `profile: ProfileCalculationResultV4` direkt (Korrektur 16/17/23) — `routes/analyses.py` (V1) bleibt unverändert.
- Größenlimit `MAX_CANONICAL_REPORT_BYTES` und Follow-up-Request-Test (Korrektur 26).
- Rollback-Punkt: `/api/v2/analyses/*`-Router deaktivieren, ohne `AgentService`/V1-Pfad zu berühren.
- Abnahme: `tests/unit/test_agent_v3.py` (neu: fehlende/doppelte/unbekannte Section-ID, Längenbudget-Verstoß, `applicable=false`-mit-Claims → `ValidationError`; alle `finish_reason`-Fälle), `tests/unit/test_idempotency.py` (neu), `tests/integration/test_production_graph.py` erweitert um vollen 18-Section-Fixed-Provider-Test inkl. Idempotenz.

### Welle 4 — Web-Migration, Tab-UI, Storage-Versionierung, Offline-Zustände

- Neu `toProfilePresentationModel()`-Adapter (`apps/web/src/features/profile/presentation.ts`): bildet `ProfileCalculationResultV4` (und weiterhin V1/V3) auf ein einheitliches `ProfilePresentationModel` ab; `ResultsTabs`, `NumberAtlas.tsx`, `ProfileActions.tsx`, PDF-Export, Bibliotheksansicht konsumieren nur dieses Modell. Betroffene Dateien: `apps/web/src/api/schema.d.ts` (Regenerierung), `apps/web/src/api/types.ts`, `apps/web/src/api/client.ts`, `apps/web/src/App.tsx`, `apps/web/src/features/profile/NumberAtlas.tsx`, `apps/web/src/features/profile/ProfileActions.tsx`, `apps/web/src/features/export/profilePdf.ts`, `apps/web/src/storage/repository.ts`.
- Neu `ResultsTabs.tsx` (WAI-ARIA-APG-Tabs), `sectionMapping.ts` (18→9-Mapping mit fixer `SECTION_UI_LABELS`-Tabelle: Überblick←executive_overview; Lebensweg←life_path_and_purpose+birthday_and_attitude; Inneres Profil←inner_motivation+maturity_and_development; Ausdruck und Wirkung←expression_and_external_persona; Muster und Spannungen←number_harmonies+number_tensions+repetitions_and_missing_values; Lebensphasen←life_phases+personal_cycles+pinnacles+challenges; Schatten und Entwicklung←shadow_patterns+development_opportunities; Integration←practical_integration+final_synthesis; Rechenweg←method_and_calculation_notes).
- Mobile Darstellung: scrollbare Tab-Leiste mit Scroll-Indikator oder Dropdown/Accordion (Entscheidung Welle 0, Punkt 15).
- `ReportExperience.tsx`: flache Liste durch `ResultsTabs`+`sectionMapping` ersetzen; URL-Sync über `useSearchParams()`.
- Neu `PrintView.tsx` mit `@media print`: lineare Darstellung aller 18 Sections; `profilePdf.ts` konsumiert dasselbe Präsentationsmodell.
- `database.ts`/`repository.ts`: Dexie-Schema-Version 4 (`reportSchemaVersion`, `methodVersion`, `calculationHash`, `reportContentHash` auf `reports`); `saveReport()`-Exception entfernen, `add()` mit neuer `reportId` → Historie; `threads`/`notes` bekommen zusätzlich `reportId` (Bindung von Rückfragen/Notizen an konkrete Berichtsversion). Export/Import-Schema auf `3`.
- Neu `apps/web/src/pwa/offlineState.ts`: reaktiver `online`/`offline`-Listener, vier korrigierte Zustände.
- `AnalysisWizard.tsx`: `toRequest()` konfigurierbar (Default für neue Profile bleibt vorerst `v1`, Wechsel auf `v2` erst in Welle 5C gemäß `product_default_method_version`).
- Abnahme: Vitest (`ResultsTabs.test.tsx`, `sectionMapping.test.ts`, `repository.test.ts` inkl. `reportId`-Bindung), Playwright + `@axe-core/playwright` (A11y, Deep-Links, Druckansicht, Mobile).

### Welle 5A — DeepSeek-Konfigurationsevaluation (kein Default-Wechsel)

- Neu `scripts/eval_deepseek_config.py`: 5 Golden-Referenzprofile × 3 Läufe × 2 Varianten, neutrale Hypothesen:
  - **H1:** Thinking-High (Produktionskonfiguration) erzielt höhere Schema-/Referenztreue bei 18 Sections.
  - **H2:** Non-Thinking mit Temperatur 0.2 erzielt geringere sprachliche Varianz zwischen Wiederholungsläufen.
  - Gemessen: Zahlenkorrektheit, Kapitelabdeckung, `applicable`-Korrektheit, JSON-Schema-Treue, Wiederholungsvarianz, Längenbudget-Einhaltung, Trunkierungsrate, Kosten, Latenz, `finish_reason`-Häufigkeit je Variante; manuell: Referenztreue, Sprachqualität, Safety.
  - `max_output_tokens` anhand realer 18-Section-Tokenlänge neu kalibrieren (innerhalb `≤32_768`); konkreter `MAX_CANONICAL_REPORT_BYTES`-Wert (Korrektur 26) festlegen.
  - Hinweis: Im Thinking Mode werden Temperatur und `top_p` nicht unterstützt/ignoriert.
- Dokumentations-Update: `CLAUDE.md`, die sechs Auftrags-Artefakte (`docs/audit/...`, `docs/product/...`, `docs/architecture/...` ×2, `docs/plans/...`, `docs/evaluation/...`) als erster Schritt dieser Welle, gespeist aus Plan + Audit + Eval.
- Abnahme: Eval-Ausgabe als neutraler H1/H2-Nachweis; **kein** Default-Wechsel nach dem Eval.

### Welle 5B — Opt-in-Beta (V1 bleibt Default)

- V2 im `AnalysisWizard.tsx` manuell auswählbar, V1 bleibt Default (gemäß `product_default_method_version="v1"`); `rollout_stage="opt_in"`.
- Begrenzte Nutzergruppe (Canary).
- Telemetrie **ohne Inhaltslogging** (nur Metriken, keine Berichtsinhalte).

### Welle 5C — Default-Wechsel nur bei erfüllten Gates

`MetaResponseV2.product_default_method_version` auf `"v2"` heben, `rollout_stage="default"` setzen
und `AnalysisWizard.tsx`-Default auf `v2` umstellen (V1 bleibt wähl-/lesbar). Die
Umschaltung ist **nur** bei erfüllten Gates zulässig:

```text
schema_success_rate >= festgelegter Grenzwert
reference_integrity = 100 %
truncated_reports = 0
unknown_references = 0
PII_leakage = 0
provider_error_rate <= Grenzwert
P95_latency <= Grenzwert
cost_per_report <= Budget
rollback_test = PASS
```

---

## Migrationsstrategie

- **Web-App/IndexedDB:** `StoredProfileRecord.schemaVersion` additiv auf `2|3|4`; Dexie-v4-Upgrade befüllt neue `reports`-Spalten aus vorhandenem Payload wo möglich, sonst `undefined` (kein Datenverlust). `threads`/`notes` erhalten `reportId` additiv (Altdaten bleiben über `profileId` lesbar). Export/Import-Schema `2→3`. Kein automatisches Neuberechnen — Opt-in-Button.
- **Backend:** kein Breaking Change an `/api/v1/profiles/*`, `/api/v1/analyses/*`, `/api/v1/meta`. Einzige Verhaltensänderung: `version="v2"` an `/api/v1/profiles/calculate` → 422 statt stiller Falschberechnung (Bugfix, im Changelog vermerkt). Domainmodelle und V1-OpenAPI-Schemas bleiben unverändert (Korrektur 16).
- **Wissensbasis:** `de-v2.json` unverändert; `de-v3.json` eigenständig.

---

## Reihenfolge der Umsetzung

1. finalen Plan einfrieren
2. Welle-0-ADRs erstellen
3. API-/Schema-Snapshots erfassen (`openapi/numra-api.json`, `openapi/contracts/v1-contract.json`)
4. Implementierung der Wellen 1–5C beginnen
5. Changelog unter „Unreleased“ während der Umsetzung pflegen
6. README erst bei verfügbarer Beta (5B) oder produktivem Rollout (5C) aktualisieren

---

## Testplan (Übersicht)

| Ebene                    | Testdatei(en)                                                                          | Fokus                                                                                                                                                |
| ------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Berechnung               | `tests/golden/test_profile_golden_v2.py`, `tests/property/test_v2_determinism.py`      | unverändert grün                                                                                                                                     |
| API-Wiring + Idempotenz  | `tests/integration/test_http_api.py`                                                   | `/api/v2/profiles/*`+`/api/v2/meta` 200, `/api/v1/profiles/*`+`v2`-Policy → 422, `/api/v1/analyses/*`+`/api/v1/meta` unverändert; V1-Pfad-Snapshot   |
| Idempotenz               | `tests/unit/test_idempotency.py` (neu)                                                 | gleicher Key → gleicher `report_id`; anderer Hash → 409; kein zweiter Provider-Call; parallele Requests; Follow-up-Retry; Reihenfolge vor Rate-Limit |
| Fact Package             | `tests/unit/test_analysis_fact_package.py` (neu)                                       | `AnalysisFactEntryV3`/`AnalysisFactPackageV3`, keine Persistenz standardmäßig, `ProviderFactPackageV3`-Minimierung                                   |
| Interpretation/Knowledge | `tests/unit/test_knowledge_v3.py` (neu)                                                | eindeutige Treffer gegen `de-v3.json`                                                                                                                |
| Prompt/Provider          | `tests/unit/test_deepseek_provider_v3.py` (neu), `tests/unit/test_prompts_v3.py` (neu) | paralleler V3-Provider, vollständige `finish_reason`-Matrix, V3-Prompt-Loading                                                                       |
| Reportvalidierung        | `tests/unit/test_agent_v3.py` (neu)                                                    | Section-Vollständigkeit, `applicable`-Validator, Längenbudgets, Hash-Kanonisierung                                                                   |
| E2E Backend              | `tests/integration/test_production_graph.py` (erweitert)                               | voller V2/V3-Graph, `finish_reason`-Simulation, Idempotenz                                                                                           |
| Evaluation               | `scripts/eval_deepseek_config.py` (neu, außerhalb CI)                                  | H1 vs. H2                                                                                                                                            |
| Web Unit                 | `ResultsTabs.test.tsx`, `sectionMapping.test.ts` (neu)                                 | ARIA, Tastatur, feste UI-Labels                                                                                                                      |
| Web Storage              | `repository.test.ts`                                                                   | Berichtshistorie, `reportId`-Bindung, Export/Import-Rundtrip                                                                                         |
| Web A11y/Print/Mobile    | Playwright + axe-core                                                                  | Tab-Pattern, Druckansicht, Mobile                                                                                                                    |
| Golden E2E               | gemäß Welle 0, Punkt 14                                                                | Lukas über vollen V2/V3-Graphen                                                                                                                      |
| Wheel-Smoke              | `tests/deployment/test_wheel_resources.py` (neu)                                       | V3-Paketressourcen im installierten Wheel vorhanden; Loader lesen sie aus dem installierten Wheel                                                    |

## Wheel-Smoke-Test für Paket-Ressourcen

Neue `.md`- und `.json`-Paketdateien müssen auch im installierten Wheel verfügbar sein. Die
Paketstruktur wird zwar vollständig als Hatchling-Package gebaut, ein Wheel-Smoke-Test prüft trotzdem
explizit, dass `de-report-system-v3.md`, `de-report-task-v3.md` und `de-v3.json` im gebauten Wheel
vorhanden sind und der Loader (bzw. `prompts_v3.py`/`loader_v3.py`) sie aus dem installierten Wheel
lesen kann. Die Buildkonfiguration bündelt die Python-Pakete; die neuen V3-Ressourcen werden dabei
explizit als Package-Data berücksichtigt.

---

## Verifikation

- `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` und `--cov=src --cov-fail-under=85` bleiben grün nach jeder Welle.
- `uv run python scripts/export_openapi.py --check` nach Welle 1 (neue `/api/v2/*`-Pfade in `openapi/numra-api.json`, V1-Contract `openapi/contracts/v1-contract.json` inkl. Schema-Closure unverändert).
- `pnpm web:typecheck && pnpm web:test && pnpm web:e2e` nach Welle 4.
- Golden-Case Lukas Springer über den vollen V2/V3-Graphen: `40/4` primär nie überschrieben, `22/4` sekundär mit `held_master_value=22` im Provider-Payload und im finalen Bericht — als expliziter Test aus Welle 0, Punkt 14.
- `scripts/eval_deepseek_config.py`-Ausgabe als neutraler H1/H2-Nachweis; Default-Wechsel erst in 5C nach erfüllten Gates.
- Wheel-Smoke-Test nach Welle 3: V3-Ressourcen (`de-report-system-v3.md`, `de-report-task-v3.md`, `de-v3.json`) im installierten Wheel vorhanden und durch `prompts_v3.py`/`loader_v3.py` lesbar.

## Kritische Dateien

- `src/numerology_domain/_models/profile.py` (unverändert — kein Literal-Umbau, Korrektur 16)
- `src/numerology_api/app.py`, `dependencies.py`, `dependencies_v3.py` (neu) bzw. `ProviderRegistry`, `routes/profiles.py`, `routes/profiles_v2.py` (neu), `routes/analyses_v2.py` (neu), `routes/meta_v2.py` (neu), `analysis_runtime_v2.py` (neu), `http_models.py`, `idempotency.py` (neu, `IdempotencyStoreV3`-Interface)
- `src/numerology_agent/models.py` (unverändert), `models_v3.py` (neu), `prompts.py` (unverändert), `prompts_v3.py` (neu), `service.py` (unverändert), `service_v3.py` (neu), `provider.py` (unverändert), `provider_v3.py` (neu), `deepseek.py` (unverändert), `deepseek_v3.py` (neu), `prompt_templates/`
- `src/numerology_interpretation/service.py` (unverändert), `service_v3.py` (neu), `rules.py`
- `src/numerology_knowledge/loader.py` (unverändert), `models.py` (unverändert), `models_v3.py` (neu), `loader_v3.py` (neu), `data/de-v3.json` (neu)
- `openapi/numra-api.json` (neu, Gesamtdokument), `openapi/contracts/v1-contract.json` (neu), `scripts/export_openapi.py`, `apps/web/package.json`
- `apps/web/src/api/schema.d.ts`, `api/types.ts`, `api/client.ts`
- `apps/web/src/features/profile/presentation.ts` (neu), `features/results/ResultsTabs.tsx` (neu), `features/results/sectionMapping.ts` (neu)
- `apps/web/src/features/report/ReportExperience.tsx`, `features/profile/NumberAtlas.tsx`, `features/profile/ProfileActions.tsx`, `features/export/profilePdf.ts`
- `apps/web/src/storage/repository.ts`, `storage/database.ts`
- `apps/web/src/features/analysis/AnalysisWizard.tsx`, `App.tsx`
