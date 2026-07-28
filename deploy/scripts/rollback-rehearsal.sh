#!/usr/bin/env sh
# Rollback-Rehearsal: deployt zwei tatsaechlich gebaute, tatsaechlich
# gestartete Releases nacheinander und fuehrt danach den echten
# deploy/scripts/rollback.sh end-to-end aus — inklusive Health-Verifikation
# vor und nach dem Rollback. Beweist die Rollback-Mechanik selbst (Image-
# Swap, Release-Marker-Update, Health-Check), nicht dass sich der Code
# zwischen Baseline und RC inhaltlich unterscheidet.
#
# Voraussetzung: /etc/numra/numra.env existiert bereits (siehe
# deploy/scripts/stage.sh), Docker laeuft, Schreibrechte auf
# /opt/numra/releases (z.B. via sudo).
set -eu

release_dir=/opt/numra/releases
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}
repo_dir=${NUMRA_REPO_DIR:-$(git rev-parse --show-toplevel)}

if [ ! -f "$env_file" ]; then
  echo "Fehlende Env-Datei: $env_file (siehe deploy/scripts/stage.sh)" >&2
  exit 1
fi

baseline_tag="rehearsal-baseline-$(date -u +%Y%m%dT%H%M%SZ)"
sleep 1
rc_tag="rehearsal-rc-$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$release_dir"
cd "$repo_dir"

echo "== Baseline-Release bauen und deployen ($baseline_tag) =="
export NUMRA_IMAGE_TAG=$baseline_tag
docker compose --env-file "$env_file" build
docker compose --env-file "$env_file" up -d --wait --wait-timeout 60
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready
printf '%s\n' "$baseline_tag" >"$release_dir/current"
printf '%s\n' "$baseline_tag" >"$release_dir/previous"
echo "Baseline live: $baseline_tag"

echo "== RC-Release bauen und deployen ($rc_tag) =="
export NUMRA_IMAGE_TAG=$rc_tag
docker compose --env-file "$env_file" build
docker compose --env-file "$env_file" up -d --wait --wait-timeout 60
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready
printf '%s\n' "$rc_tag" >"$release_dir/current"
printf '%s\n' "$baseline_tag" >"$release_dir/previous"
echo "RC live: $rc_tag (previous: $baseline_tag)"

echo "== Rollback ausfuehren =="
NUMRA_ENV_FILE="$env_file" NUMRA_REPO_DIR="$repo_dir" sh "$repo_dir/deploy/scripts/rollback.sh"
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready

after_rollback=$(cat "$release_dir/current")
if [ "$after_rollback" != "$baseline_tag" ]; then
  echo "Rollback-Rehearsal FEHLGESCHLAGEN: current=$after_rollback, erwartet=$baseline_tag" >&2
  exit 1
fi

echo "Rollback-Rehearsal erfolgreich: $rc_tag -> $baseline_tag, Health nach Rollback bestaetigt."
