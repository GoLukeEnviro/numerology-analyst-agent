#!/usr/bin/env sh
set -eu

: "${AGE_RECIPIENT:?Set AGE_RECIPIENT to the offline backup public key}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root to read the protected configuration." >&2
  exit 1
fi

command -v age >/dev/null
test -f /etc/numra/numra.env
test -f /etc/nginx/sites-available/numra

backup_dir=/var/backups/numra
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
output=$backup_dir/numra-config-$timestamp.tar.gz.age

install -d -m 0700 "$backup_dir"
(cd / && tar -czf - \
  etc/numra/numra.env \
  etc/nginx/sites-available/numra) \
  | age --encrypt --recipient "$AGE_RECIPIENT" --output "$output"
chmod 0600 "$output"
age --decrypt --identity "${AGE_IDENTITY:?Set AGE_IDENTITY for verification}" "$output" \
  | tar -tzf - >/dev/null

echo "Encrypted configuration backup verified: $output"
