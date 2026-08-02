#!/usr/bin/env sh
set -eu

repo_dir=${NUMRA_REPO_DIR:-/opt/numra/repository}
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}
release_dir=${NUMRA_RELEASE_DIR:-/opt/numra/releases}
current_file=$release_dir/current
previous_file=$release_dir/previous

test -f "$current_file"
test -f "$previous_file"
current_release=$(cat "$current_file")
previous_release=$(cat "$previous_file")

if ! printf '%s' "$previous_release" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "Previous release marker is invalid." >&2
  exit 1
fi

docker image inspect "numra-api:$previous_release" >/dev/null
docker image inspect "numra-web:$previous_release" >/dev/null

cd "$repo_dir"
export NUMRA_IMAGE_TAG=$previous_release
docker compose --env-file "$env_file" config --quiet
docker compose --env-file "$env_file" up -d --no-build --wait --wait-timeout 90

# Gateway can report compose-healthy slightly before curl succeeds; retry.
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
  echo "Health check failed after rollback to $previous_release" >&2
  exit 1
fi

printf '%s\n' "$current_release" >"$previous_file.tmp"
mv "$previous_file.tmp" "$previous_file"
printf '%s\n' "$previous_release" >"$current_file.tmp"
mv "$current_file.tmp" "$current_file"

echo "Rolled back to immutable image tag: $previous_release"
