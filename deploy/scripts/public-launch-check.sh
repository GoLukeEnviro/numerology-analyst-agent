#!/usr/bin/env sh
set -eu

: "${NUMRA_DOMAIN:?Set NUMRA_DOMAIN to the final host name}"

repo_dir=${NUMRA_REPO_DIR:-/opt/numra/repository}
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}
legal_marker=/etc/numra/numra-legal-approved
llm_marker=/etc/numra/llm-transfer-approved

test -f "$env_file"
test "$(stat -c '%a' "$env_file")" = "600"
test -f "$legal_marker"
test "$(stat -c '%U:%G:%a' "$legal_marker")" = "root:root:600"

if grep -Fq "öffentlichen Launch gesperrt" "$repo_dir/apps/web/src/App.tsx"; then
  echo "The in-app imprint still contains the public-launch blocker." >&2
  exit 1
fi

if ! grep -Fxq "NUMRA_ALLOWED_ORIGINS=https://$NUMRA_DOMAIN" "$env_file"; then
  echo "NUMRA_ALLOWED_ORIGINS must exactly match the HTTPS domain." >&2
  exit 1
fi

if grep -Eiq '^NUMRA_LLM_ENABLED=true$' "$env_file"; then
  test -f "$llm_marker"
  test "$(stat -c '%U:%G:%a' "$llm_marker")" = "root:root:600"
fi

getent ahosts "$NUMRA_DOMAIN" >/dev/null
certbot certificates | grep -F "$NUMRA_DOMAIN" >/dev/null
curl --fail --silent --show-error "https://$NUMRA_DOMAIN/api/v1/health/ready" >/dev/null
curl --fail --silent --show-error --head "https://$NUMRA_DOMAIN/" \
  | grep -Eiq '^strict-transport-security:'

echo "Technical public-launch gates passed for $NUMRA_DOMAIN."
