# Optionaler DeepSeek-Betrieb

Die deterministische Berechnung und die lokale Bibliothek funktionieren ohne
LLM. Der Provider ist standardmäßig deaktiviert.

## Konfiguration

```bash
# Operational settings (NUMRA_ prefix — unchanged)
NUMRA_LLM_ENABLED=false
NUMRA_REDIS_URL=redis://redis:6379/0
NUMRA_RATE_LIMIT_HMAC_SECRET=

# DeepSeek provider settings (DEEPSEEK_ prefix preferred)
# NUMRA_DEEPSEEK_* variables remain as a deprecated fallback (logs a warning
# without secrets) but DEEPSEEK_* is the canonical name going forward.
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_THINKING_ENABLED=true
DEEPSEEK_REASONING_EFFORT=high
DEEPSEEK_MAX_OUTPUT_TOKENS=8192
DEEPSEEK_MAX_RETRIES=3
```

Erst wenn `NUMRA_LLM_ENABLED=true` gesetzt wird, sind API-Schlüssel und ein
zufälliges HMAC-Secret zwingend. Das Secret sollte mindestens 32 zufällige
Bytes besitzen. API und Provider starten bei fehlender Konfiguration
absichtlich nicht.

## Datenschutzgrenze

An den Provider gehen ausschließlich der deterministische Profilhash,
Berechnungsreferenzen und Zahlen, Aussageklassen sowie die notwendigen Auszüge
aus `numra-knowledge-de-v1`. Klarname, aktiver Name, Geburtsdatum und
`input_ref` werden nicht in den Provider-Payload aufgenommen. Rückfragen werden
vor dem Provider-Aufruf auf Prompt-Injection, bekannte Profilnamen und
vollständige Datumsformen geprüft. Der vorhandene Bericht wird erneut an
Profilhash, Rechenwerte, Wissensreferenzen und Safety-Regeln gebunden; seine
serverseitige HMAC-Signatur muss gültig sein und seine Provenienz wird nicht
an den Provider weitergereicht. Erkannt werden vollständige Namen,
Namensbestandteile sowie numerische und deutsche Geburtsdatumsvarianten.
Eine Rotation von `NUMRA_RATE_LIMIT_HMAC_SECRET` macht bewusst auch ältere
lokale Berichte für neue Rückfragen ungültig; sie bleiben lokal lesbar.

Provider-Ausgaben werden nur nach JSON-Schema-, Rechenwert-, Wissensreferenz-
und Safety-Validierung zurückgegeben. Leere oder ungültige Antworten werden
genau einmal wiederholt. Request-Bodies und Provider-Ausgaben dürfen niemals
protokolliert werden.

Der OpenAI-kompatible V4-Pro-Aufruf verwendet JSON Output, maximal 8.192
Ausgabetokens, `thinking.type=enabled` und `reasoning_effort=high`. Sampling-
Parameter (`temperature`/`top_p`) werden **nicht** mehr gesendet, da sie im
Thinking-Modus wirkungslos sind. Die Provenienz weist stattdessen
`effective_sampling=provider_managed`, `temperature=null`, `top_p=null` und
`reasoning_effort=high` aus.

### Provider-Retry und Circuit-Breaker

Transiente Fehler (Netzwerk, Timeout, HTTP 429/502/503/504) werden mit
exponentiellem Backoff und Jitter bis zu `DEEPSEEK_MAX_RETRIES`-mal
wiederholt. Harte Fehler (HTTP 400/401/403, ungültiger Key, unbekanntes
Modell) führen sofort zu einem Fail-Closed ohne Retry. Ein Circuit-Breaker
öffnet nach fünf aufeinanderfolgenden Fehlern und sperrt Aufrufe für 60
Sekunden; ein Probe-Aufruf im HALF_OPEN-Zustand testet die Wiederherstellung.

### `reasoning_content`-Hygiene

Der DeepSeek-Thinking-Trace (`reasoning_content`) wird **niemals** aus der
API-Antwort extrahiert. Er taucht nicht in `ProviderResult`, Berichten,
Exporten, Logs oder API-Antworten auf. Alle Aufrufe sind One-Shot ohne
Tool-Calls.

## Kontingente

- ein Bericht pro Gerät und Tag,
- zwei Rückfragen pro Gerät und Tag,
- zusätzlich 20 Provider-Aufrufe pro pseudonymisierter IP und Tag.

Redis erhält ausschließlich HMAC-Schlüssel mit Ablaufzeit. Roh-IP-Adressen,
Profile und Gespräche werden nicht gespeichert. Der öffentliche Host-Proxy
ersetzt eingehende `X-Forwarded-For`-Werte, und Uvicorn vertraut ausschließlich
der fest adressierten internen Gateway-Adresse `172.30.0.10`.

## Externes Launch-Gate

Ein Live-Smoke-Test wird erst mit einem echten API-Schlüssel ausgeführt. Vor
Aktivierung müssen Betreiber außerdem Drittlandtransfer, Vertragsgrundlage,
Provider-Datenschutzbedingungen und die sichtbare Einwilligung rechtlich
freigeben. Ohne diese Freigaben bleibt `NUMRA_LLM_ENABLED=false`.

## Staging-Deployment mit aktivem LLM-Pfad

Die Basis-`compose.yaml` liefert den LLM-Pfad standardmäßig deaktiviert aus
(`NUMRA_LLM_ENABLED=false`) und mountet keine Runtime-Marker. Für privates
Staging mit aktivem DeepSeek-Pfad kommt das additive Override
`compose.llm-staging.yaml` hinzu:

```bash
docker compose -f compose.yaml -f compose.llm-staging.yaml up -d --wait
```

Voraussetzungen auf dem Host, bevor der LLM-Pfad startet:

- `/etc/numra/numra-legal-approved` und `/etc/numra/llm-transfer-approved`
  existieren, gehören `root:root` und haben Modus `0600`.
- `DEEPSEEK_API_KEY` und `NUMRA_RATE_LIMIT_HMAC_SECRET` sind über die
  Shell-Umgebung bzw. `--env-file` gesetzt (siehe `deploy/scripts/stage.sh`).

Der API-Container läuft als Nicht-root-UID `10001`. `runtime_gate.py` prüft
Existenz, Eigentümer und Modus der Marker-Dateien ausschließlich über
`stat()` — das erfordert nur Traversierungsrechte auf `/etc/numra`, kein
Leserecht auf den Dateiinhalt selbst, und funktioniert deshalb auch für den
nicht-privilegierten Containerprozess. Fehlen die Marker oder stimmen
Eigentümer/Modus nicht, verweigert `create_app()` den Start des gesamten
API-Containers (Healthcheck bleibt rot).

## Provider-Smoke vs. API-Staging-Smoke

Zwei unterschiedliche Prüfungen mit unterschiedlichem Zweck — nicht
austauschbar:

| | `deploy/scripts/provider-smoke.sh` | `deploy/scripts/api-smoke.sh` |
|---|---|---|
| Prüft | Nur DeepSeek direkt (Netzwerk, Key, Modell) | Den eigenen Stack Ende-zu-Ende (Gateway → FastAPI → Redis → Agent → DeepSeek) |
| Braucht laufenden Numra-Stack | Nein | Ja, mit `compose.llm-staging.yaml` und aktivem LLM-Pfad |
| Braucht echten `DEEPSEEK_API_KEY` | Ja | Ja |
| Sendet Nutzerdaten | Nein (Minimal-Ping) | Ja (Smoke-Testprofil, keine echten Personendaten) |

Zusätzlich existiert `deploy/scripts/deepseek-smoke.ps1` als Windows-Äquivalent
zu `api-smoke.sh` für Betreiber ohne POSIX-Shell.

## Staging-Checkliste

Vor jedem privaten Staging-Deployment mit aktivem LLM-Pfad:

1. `docker compose -f compose.yaml -f compose.llm-staging.yaml config --quiet`
2. Runtime-Marker auf dem Host geprüft (Existenz, `root:root`, `0600`)
3. `deploy/scripts/stage.sh` — baut, deployt, wartet auf Health
4. `deploy/scripts/provider-smoke.sh` — DeepSeek isoliert erreichbar
5. `deploy/scripts/api-smoke.sh` — eigener Stack Ende-zu-Ende erreichbar
6. Keine öffentlichen Ports (`docker compose ps` — nur `127.0.0.1:8080`)
7. Kein Docker-Socket-Mount in irgendeinem Service
8. Ressourcenlimits aktiv (`docker compose config` zeigt `deploy.resources.limits` für alle drei Services)

## Rollback-Rehearsal

`deploy/scripts/rollback.sh` erwartet zwei bereits deployte, immutable
Image-Tags (`current`/`previous` unter `/opt/numra/releases/`).
`deploy/scripts/rollback-rehearsal.sh` führt den vollständigen Rollback-Test
lokal aus zwei tatsächlich gebauten Releases durch: Baseline deployen, RC
deployen, Health-Smoke, Rollback, erneuter Health-Smoke. Kein Schritt
überspringt die Health-Prüfung.
