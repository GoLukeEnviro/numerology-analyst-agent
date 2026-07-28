#!/usr/bin/env sh
# API-Staging-Smoke: prueft den eigenen deployten Stack Ende-zu-Ende
# (Gateway -> FastAPI -> Redis -> Agent -> DeepSeek), NICHT die
# DeepSeek-Erreichbarkeit isoliert. Fuer eine reine Provider-Pruefung ohne
# den eigenen Stack siehe deploy/scripts/provider-smoke.sh.
#
# Voraussetzung: der Stack laeuft bereits mit aktivem LLM-Pfad und einem
# echten DeepSeek-Key (docker compose -f compose.yaml -f
# compose.llm-staging.yaml up -d --wait, NUMRA_LLM_ENABLED=true,
# DEEPSEEK_API_KEY gesetzt). Ohne aktives LLM liefert
# /api/v1/analyses/report absichtlich 503 (LLM_FEATURE_DISABLED) und dieses
# Skript schlaegt fehl — das ist erwartet, kein Skriptfehler.
set -eu

base_url=${NUMRA_BASE_URL:-http://127.0.0.1:8080}

echo "API-Smoke gegen $base_url"

curl --fail --silent --show-error "$base_url/" >/dev/null
echo "  gateway: erreichbar"

curl --fail --silent --show-error "$base_url/api/v1/health/live" >/dev/null
echo "  api/health/live: ok"

curl --fail --silent --show-error "$base_url/api/v1/health/ready" >/dev/null
echo "  api/health/ready: ok (redis + agent-abhaengigkeiten erreichbar)"

device_id="api-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
profile_response=$(curl --fail --silent --show-error \
  -X POST "$base_url/api/v1/profiles/calculate" \
  -H "Content-Type: application/json" \
  -d '{
        "person": {
          "core_name": "Numra Staging Smoke",
          "active_name": null,
          "birth_date": "1990-04-12",
          "as_of_date": "2026-07-28",
          "locale": "de",
          "consent_given": false
        },
        "policy": {
          "system": "pythagorean",
          "version": "v1",
          "y_mode": "phonetic",
          "umlaut_policy": "de-direct-v1",
          "name_basis": "both_separate",
          "date_method": "both",
          "locale": "de",
          "master_numbers": [11, 22, 33]
        }
      }')
echo "  api/v1/profiles/calculate: ok"

report_payload=$(printf '{"consent": true, "device_id": "%s", "profile": %s}' \
  "$device_id" "$profile_response")

curl --fail --silent --show-error \
  -X POST "$base_url/api/v1/analyses/report" \
  -H "Content-Type: application/json" \
  -d "$report_payload" >/dev/null
echo "  api/v1/analyses/report: ok"

echo "API-Smoke erfolgreich: Gateway, FastAPI, Redis und Agent-Pfad erreichbar."
