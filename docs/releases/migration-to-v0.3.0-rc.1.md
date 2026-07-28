# Migration zu v0.3.0-rc.1

> **Zielgruppe:** Betreiber und Entwickler, die von ≤0.1.5 auf 0.3.0-rc.1 migrieren.

## Zusammenfassung

0.3.0-rc.1 ist ein kumulativer Release Candidate. Die Versionsnummer springt
von 0.1.5 auf 0.3.0rc1 (SemVer), weil ADR 0015 die kumulative Release-
Normalisierung auf 0.3.0rc1 festlegt. Die Änderungen sind abwärtskompatibel:
alle V1-Strukturen bleiben lesbar, neue Erzeugung erfolgt ausschließlich in V2.

## Schritte

### 1. Code aktualisieren

```bash
git pull origin main
uv sync --locked --all-groups
pnpm install --frozen-lockfile
```

### 2. Umgebungsvariablen migrieren

Die `NUMRA_DEEPSEEK_*`-Variablen wurden durch `DEEPSEEK_*` ersetzt. Die alten
Namen bleiben als Fallback gültig, loggen aber eine Deprecation-Warning.

```bash
# Alt (funktioniert noch, warnt):
NUMRA_DEEPSEEK_API_KEY=sk-...
NUMRA_DEEPSEEK_BASE_URL=https://api.deepseek.com
NUMRA_DEEPSEEK_MODEL=deepseek-v4-pro

# Neu (bevorzugt):
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_THINKING_ENABLED=true
DEEPSEEK_REASONING_EFFORT=high
DEEPSEEK_MAX_OUTPUT_TOKENS=8192
DEEPSEEK_MAX_RETRIES=3
```

Operationale Variablen (`NUMRA_LLM_ENABLED`, `NUMRA_REDIS_URL`,
`NUMRA_RATE_LIMIT_HMAC_SECRET`, `NUMRA_ENVIRONMENT`, `NUMRA_ALLOWED_ORIGINS`,
`NUMRA_MAX_REQUEST_BODY_BYTES`) bleiben unter dem `NUMRA_`-Präfix.

### 3. Knowledge-Bundle

Der Standard-Knowledge-Bundle ist jetzt `numra-knowledge-de-v2` (V1 bleibt
über `load_knowledge_bundle("de", "v1")` ladbar). Wenn Sie V1-spezifische
Referenzen in lokalen Daten haben, bleiben diese gültig.

### 4. API-Verträge

Neu erzeugte Berichte tragen `schema_version: "analysis-report-v2"`. Die
OpenAPI-Spec wurde aktualisiert. Regenerieren Sie generierte Clients:

```bash
uv run python scripts/export_openapi.py
pnpm web:generate-api
```

### 5. DeepSeek-Konfiguration

Im Thinking-Modus werden `temperature` und `top_p` nicht mehr gesendet. Die
Provenance trägt stattdessen `temperature: null`, `top_p: null`,
`effective_sampling: "provider_managed"`.

### 6. Container-Update

```bash
docker compose build
docker compose up -d --wait
curl --fail http://127.0.0.1:8080/api/v1/health/ready
```

## Rollback

Bei Problemen kann auf den vorherigen Stand (0.1.5) zurückgekehrt werden:

```bash
git checkout <voriger-stand>
uv sync --locked --all-groups
docker compose build && docker compose up -d --wait
```

Lokale Daten (IndexedDB) bleiben kompatibel — V2-Berichte sind ein Superset
der V1-Struktur.
