#!/usr/bin/env sh
# Provider-Smoke: prueft ausschliesslich die DeepSeek-Erreichbarkeit und den
# konfigurierten API-Key direkt gegen den Provider — OHNE den eigenen Numra-
# Stack. Fuer den Ende-zu-Ende-Test durch Gateway/FastAPI/Redis/Agent siehe
# deploy/scripts/api-smoke.sh.
#
# Dieses Skript sendet KEINE Profildaten und KEINE echten Nutzerinhalte an
# DeepSeek; es ruft nur einen minimalen, nicht-identifizierenden Chat-Request
# ab, um Netzwerkpfad, Key-Gueltigkeit und Modellverfuegbarkeit zu pruefen.
set -eu

: "${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY muss gesetzt sein}"
base_url=${DEEPSEEK_BASE_URL:-https://api.deepseek.com}
model=${DEEPSEEK_MODEL:-deepseek-v4-pro}

echo "Provider-Smoke gegen $base_url (Modell: $model)"

http_status=$(curl --silent --show-error --output /tmp/provider-smoke-response.json \
  --write-out "%{http_code}" \
  -X POST "$base_url/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"model": "%s", "max_tokens": 8, "messages": [{"role": "user", "content": "ping"}]}' "$model")")

if [ "$http_status" != "200" ]; then
  echo "DeepSeek antwortete mit HTTP $http_status:" >&2
  cat /tmp/provider-smoke-response.json >&2
  rm -f /tmp/provider-smoke-response.json
  exit 1
fi

rm -f /tmp/provider-smoke-response.json
echo "Provider-Smoke erfolgreich: DeepSeek ist erreichbar, Key und Modell gueltig."
