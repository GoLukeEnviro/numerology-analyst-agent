#!/usr/bin/env sh
set -eu

: "${NUMRA_DOMAIN:?Set NUMRA_DOMAIN to the final host name}"
: "${NUMRA_TLS_EMAIL:?Set NUMRA_TLS_EMAIL for Let's Encrypt notices}"

repo_dir=${NUMRA_REPO_DIR:-/opt/numra/repository}
available=/etc/nginx/sites-available/numra
enabled=/etc/nginx/sites-enabled/numra

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root so Nginx and Certbot files keep correct ownership." >&2
  exit 1
fi

if ! printf '%s' "$NUMRA_DOMAIN" | grep -Eq '^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$'; then
  echo "NUMRA_DOMAIN is not a valid DNS host name." >&2
  exit 1
fi

if ! printf '%s' "$NUMRA_TLS_EMAIL" | grep -Eq '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'; then
  echo "NUMRA_TLS_EMAIL is not a valid contact address." >&2
  exit 1
fi

command -v nginx >/dev/null
command -v certbot >/dev/null
getent ahosts "$NUMRA_DOMAIN" >/dev/null
test -f "$repo_dir/deploy/nginx/numra-http.conf.template"
test -f "$repo_dir/deploy/nginx/numra-https.conf.template"

install -d -m 0755 /var/www/certbot
sed "s/\${NUMRA_DOMAIN}/$NUMRA_DOMAIN/g" \
  "$repo_dir/deploy/nginx/numra-http.conf.template" >"$available"
ln -sfn "$available" "$enabled"
nginx -t
systemctl reload nginx

certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --domain "$NUMRA_DOMAIN" \
  --email "$NUMRA_TLS_EMAIL" \
  --agree-tos \
  --no-eff-email \
  --non-interactive

sed "s/\${NUMRA_DOMAIN}/$NUMRA_DOMAIN/g" \
  "$repo_dir/deploy/nginx/numra-https.conf.template" >"$available"
nginx -t
systemctl reload nginx
certbot renew --dry-run

curl --fail --silent --show-error "https://$NUMRA_DOMAIN/api/v1/health/live"
echo "HTTPS is active. Public launch still requires public-launch-check.sh."
