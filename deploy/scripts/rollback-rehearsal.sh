#!/usr/bin/env sh
# Rollback-Rehearsal: deployt zwei tatsaechlich gebaute, tatsaechlich
# gestartete Releases nacheinander und fuehrt danach den echten
# deploy/scripts/rollback.sh end-to-end aus — inklusive Health-Verifikation
# vor und nach dem Rollback. Beweist die Rollback-Mechanik selbst (Image-
# Swap, Release-Marker-Update, Health-Check), nicht dass sich der Code
# zwischen Baseline und RC inhaltlich unterscheidet.
#
# Voraussetzung: numra.env existiert (siehe deploy/scripts/stage.sh), Docker
# laeuft, Schreibrechte auf NUMRA_RELEASE_DIR (Default /opt/numra/releases).
#
# Image-Tags MUeSSEN exakt 40 Hex-Zeichen sein (Vertrag von rollback.sh).
# Deshalb werden git-SHAs verwendet, nicht Zeitstempel-Strings.
set -eu

release_dir=${NUMRA_RELEASE_DIR:-/opt/numra/releases}
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}
repo_dir=${NUMRA_REPO_DIR:-$(git rev-parse --show-toplevel)}

if [ ! -f "$env_file" ]; then
  echo "Fehlende Env-Datei: $env_file (siehe deploy/scripts/stage.sh)" >&2
  exit 1
fi

cd "$repo_dir"

# Zwei gueltige 40-Hex-Tags: optional per Env, sonst HEAD und HEAD~1.
# Der Build nutzt den aktuellen Working Tree; die Tags erfuellen den
# rollback.sh-SHA-Vertrag und markieren zwei Image-Identitaeten.
baseline_tag=${NUMRA_REHEARSAL_BASELINE_TAG:-$(git rev-parse --verify HEAD~1)}
rc_tag=${NUMRA_REHEARSAL_RC_TAG:-$(git rev-parse --verify HEAD)}

if ! printf '%s' "$baseline_tag" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "Baseline-Tag muss 40 Hex-Zeichen sein (rollback.sh-Vertrag): $baseline_tag" >&2
  exit 1
fi
if ! printf '%s' "$rc_tag" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "RC-Tag muss 40 Hex-Zeichen sein (rollback.sh-Vertrag): $rc_tag" >&2
  exit 1
fi
if [ "$baseline_tag" = "$rc_tag" ]; then
  echo "Baseline- und RC-Tag muessen verschieden sein." >&2
  exit 1
fi

mkdir -p "$release_dir"

echo "== Baseline-Release bauen und deployen ($baseline_tag) =="
export NUMRA_IMAGE_TAG=$baseline_tag
docker compose --env-file "$env_file" build
docker compose --env-file "$env_file" up -d --wait --wait-timeout 90
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready
printf '%s\n' "$baseline_tag" >"$release_dir/current"
printf '%s\n' "$baseline_tag" >"$release_dir/previous"
echo "Baseline live: $baseline_tag"

echo "== RC-Release bauen und deployen ($rc_tag) =="
export NUMRA_IMAGE_TAG=$rc_tag
docker compose --env-file "$env_file" build
docker compose --env-file "$env_file" up -d --wait --wait-timeout 90
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready
printf '%s\n' "$rc_tag" >"$release_dir/current"
printf '%s\n' "$baseline_tag" >"$release_dir/previous"
echo "RC live: $rc_tag (previous: $baseline_tag)"

echo "== Rollback ausfuehren =="
NUMRA_ENV_FILE="$env_file" \
  NUMRA_REPO_DIR="$repo_dir" \
  NUMRA_RELEASE_DIR="$release_dir" \
  sh "$repo_dir/deploy/scripts/rollback.sh"

health_ok=0
i=0
while [ "$i" -lt 20 ]; do
  if curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready >/dev/null; then
    health_ok=1
    break
  fi
  i=$((i + 1))
  sleep 2
done
if [ "$health_ok" -ne 1 ]; then
  echo "Health nach Rollback fehlgeschlagen." >&2
  exit 1
fi

after_rollback=$(cat "$release_dir/current")
if [ "$after_rollback" != "$baseline_tag" ]; then
  echo "Rollback-Rehearsal FEHLGESCHLAGEN: current=$after_rollback, erwartet=$baseline_tag" >&2
  exit 1
fi

echo "Rollback-Rehearsal erfolgreich: $rc_tag -> $baseline_tag, Health nach Rollback bestaetigt."
