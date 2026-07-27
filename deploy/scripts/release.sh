#!/usr/bin/env sh
set -eu

release_sha=${1:-}
repo_dir=${NUMRA_REPO_DIR:-/opt/numra/repository}
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}
release_dir=/opt/numra/releases
current_file=/opt/numra/releases/current
previous_file=/opt/numra/releases/previous

if ! printf '%s' "$release_sha" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "Usage: release.sh FULL_40_CHARACTER_COMMIT_SHA" >&2
  exit 1
fi

cd "$repo_dir"
git diff --quiet
git diff --cached --quiet
git cat-file -e "$release_sha^{commit}"
git checkout --detach "$release_sha"
test "$(git rev-parse --verify HEAD)" = "$release_sha"
test -f "$env_file"
test "$(stat -c '%a' "$env_file")" = "600"

install -d -m 0755 "$release_dir"
old_release=
if [ -f "$current_file" ]; then
  old_release=$(cat "$current_file")
fi

export NUMRA_IMAGE_TAG=$release_sha
docker compose --env-file "$env_file" config --quiet
docker compose --env-file "$env_file" build --pull
docker compose --env-file "$env_file" up -d --wait --wait-timeout 60
curl --fail --silent --show-error http://127.0.0.1:8080/api/v1/health/ready

if [ -n "$old_release" ] && [ "$old_release" != "$release_sha" ]; then
  printf '%s\n' "$old_release" >"$previous_file.tmp"
  mv "$previous_file.tmp" "$previous_file"
fi
printf '%s\n' "$release_sha" >"$current_file.tmp"
mv "$current_file.tmp" "$current_file"

echo "Released immutable image tag: $release_sha"
