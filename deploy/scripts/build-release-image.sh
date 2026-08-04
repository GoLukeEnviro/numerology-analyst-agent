#!/usr/bin/env sh
# Baut die Release-Images GENAU EINMAL, getaggt mit dem Commit-SHA. Das
# ist die Gegenseite von release.sh (OPS-002): release.sh baut nicht
# mehr auf dem Zielhost, sondern deployt ein bereits gebautes Image.
#
# Vorgesehener Ausfuehrungsort: CI oder eine dedizierte Build-Maschine,
# NICHT der Staging-/Produktionshost selbst - genau das war der Befund.
#
# Ausgabe: Commit-SHA, Content-ID/Digest je Image (api, web) und,
# sofern NUMRA_IMAGE_SAVE_DIR gesetzt ist, ein "docker save"-Tarball je
# Image zum Transport auf den Zielhost (docker load dort vor release.sh).
set -eu

release_sha=${1:-$(git rev-parse --verify HEAD)}
repo_dir=${NUMRA_REPO_DIR:-$(git rev-parse --show-toplevel)}
save_dir=${NUMRA_IMAGE_SAVE_DIR:-}

if ! printf '%s' "$release_sha" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "Usage: build-release-image.sh FULL_40_CHARACTER_COMMIT_SHA" >&2
  exit 1
fi

cd "$repo_dir"
git cat-file -e "$release_sha^{commit}"

export NUMRA_IMAGE_TAG=$release_sha
docker compose config --quiet
docker compose build --pull

# Content-ID (".Id") ist auch ohne Registry ein stabiler, inhaltsbasierter
# Identifikator - im Gegensatz zum veraenderlichen Tag. Sobald eine
# Registry eingerichtet ist, sollte zusaetzlich RepoDigests geprueft und
# gegen .Id abgeglichen werden.
api_digest=$(docker image inspect "numra-api:$release_sha" --format '{{.Id}}')
web_digest=$(docker image inspect "numra-web:$release_sha" --format '{{.Id}}')

echo "Built immutable image tag: $release_sha"
echo "api image digest (.Id): $api_digest"
echo "web image digest (.Id): $web_digest"

if [ -n "$save_dir" ]; then
  install -d -m 0755 "$save_dir"
  docker save "numra-api:$release_sha" -o "$save_dir/numra-api-$release_sha.tar"
  docker save "numra-web:$release_sha" -o "$save_dir/numra-web-$release_sha.tar"
  echo "Saved tarballs under: $save_dir"
  echo "Transfer both files to the target host, then: docker load -i <file>"
fi
