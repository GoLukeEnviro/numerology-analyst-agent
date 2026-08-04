#!/usr/bin/env sh
# Gegenstueck zu backup-config.sh: stellt ein verschluesseltes
# Konfigurations-Backup tatsaechlich wieder her, statt es nur zur
# Verifikation zu entschluesseln (OPS-001).
#
# Ablauf: entschluesseln -> in ein Staging-Verzeichnis extrahieren ->
# Mitgliederliste UND Rechte strukturell pruefen -> erst danach atomar
# (mv) in die Zielpfade installieren. Vor der vollstaendigen Verifikation
# wird nichts im Zielpfad angefasst.
#
# Usage: restore-config.sh /var/backups/numra/numra-config-<timestamp>.tar.gz.age
set -eu

backup_file=${1:?"Usage: restore-config.sh <backup.tar.gz.age>"}

: "${AGE_IDENTITY:?Set AGE_IDENTITY to the offline backup private key}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root to write the protected configuration." >&2
  exit 1
fi

command -v age >/dev/null
test -f "$backup_file"

# Erwartete Mitgliederliste - muss exakt zu backup-config.sh passen.
# Diese Liste hier explizit zu fuehren (statt sie aus der Backup-Datei
# abzuleiten) ist der strukturelle Vertrag: die Wiederherstellung
# akzeptiert nur bekannte Pfade, keine beliebigen Tar-Inhalte.
expected_numra_env=etc/numra/numra.env
expected_nginx_conf=etc/nginx/sites-available/numra

staging_dir=$(mktemp -d)
trap 'rm -rf "$staging_dir"' EXIT

age --decrypt --identity "$AGE_IDENTITY" "$backup_file" \
  | tar -xzf - -C "$staging_dir"

# Strukturelle Pruefung statt reinem "laesst sich lesen": exakt die
# erwarteten Dateien, nicht mehr und nicht weniger, beide nicht leer.
if [ ! -f "$staging_dir/$expected_numra_env" ]; then
  echo "Backup enthaelt kein $expected_numra_env - Restore abgebrochen." >&2
  exit 1
fi
if [ ! -f "$staging_dir/$expected_nginx_conf" ]; then
  echo "Backup enthaelt kein $expected_nginx_conf - Restore abgebrochen." >&2
  exit 1
fi
if [ ! -s "$staging_dir/$expected_numra_env" ]; then
  echo "$expected_numra_env im Backup ist leer - Restore abgebrochen." >&2
  exit 1
fi

member_count=$(find "$staging_dir" -type f | wc -l)
if [ "$member_count" -ne 2 ]; then
  echo "Backup enthaelt $member_count Dateien, erwartet genau 2 - Restore abgebrochen." >&2
  exit 1
fi

# Zielrechte werden explizit gesetzt, nicht aus dem Tar uebernommen -
# das Backup-Archiv ist keine vertrauenswuerdige Quelle fuer Permissions.
chmod 0600 "$staging_dir/$expected_numra_env"
chmod 0644 "$staging_dir/$expected_nginx_conf"
chown root:root "$staging_dir/$expected_numra_env" "$staging_dir/$expected_nginx_conf"

install -d -m 0755 /etc/nginx/sites-available

# Atomar installieren: mv innerhalb derselben Zielpartition (/etc) ist
# atomar. Ein fehlgeschlagener Restore hinterlaesst damit nie eine
# halb geschriebene Konfigurationsdatei.
mv "$staging_dir/$expected_numra_env" /etc/numra/numra.env
mv "$staging_dir/$expected_nginx_conf" /etc/nginx/sites-available/numra

echo "Restored configuration from: $backup_file"
echo "Restart the stack and re-run health/profile smoke checks now."
