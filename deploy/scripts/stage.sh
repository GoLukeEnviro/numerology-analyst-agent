#!/usr/bin/env sh
set -eu

repo_dir=${NUMRA_REPO_DIR:-/opt/numra/repository}
env_file=${NUMRA_ENV_FILE:-/etc/numra/numra.env}

if [ ! -f "$env_file" ]; then
  echo "Missing environment file: $env_file" >&2
  exit 1
fi

if [ "$(stat -c '%a' "$env_file")" != "600" ]; then
  echo "Environment file must have mode 0600: $env_file" >&2
  exit 1
fi

cd "$repo_dir"
image_tag=$(git rev-parse --verify HEAD)
export NUMRA_IMAGE_TAG=$image_tag

docker compose --env-file "$env_file" config --quiet
docker compose --env-file "$env_file" build --pull
docker compose --env-file "$env_file" up -d --wait
docker compose ps

echo "Private staging is available only at 127.0.0.1:8080."
echo "Use an SSH tunnel; do not open a public firewall port."
