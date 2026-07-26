# Numra Launch-Checkliste

Öffentliche Freigabe ist erst erlaubt, wenn jede Pflichtzeile nachweisbar
erfüllt ist. Diese Liste ersetzt keine Rechtsberatung.

## Betreiber und Recht

- [ ] Betreiberanschrift, Vertretungsangaben und Datenschutzkontakt sind
  vollständig, wahr und in `/impressum` sichtbar.
- [ ] Datenschutzinformation und Nutzungsbedingungen wurden für den konkreten
  Betreiber und Hostingstandort geprüft.
- [ ] Die Altersgrenze von 18 Jahren und die wissenschaftliche Aussagegrenze
  sind im gesamten Flow sichtbar.
- [ ] `/etc/numra/numra-legal-approved` wurde nach Freigabe als root:root mit
  Modus 0600 angelegt.
- [ ] Bei aktiviertem DeepSeek sind Drittlandtransfer, Vertragsgrundlage,
  Anbietertext und Einwilligung geprüft; erst dann existiert
  `/etc/numra/llm-transfer-approved`.
- [ ] Ohne diese LLM-Freigabe bleibt `NUMRA_LLM_ENABLED=false`.

## DNS, TLS und Netzwerk

- [ ] Der Betreiber hat Domain und TLS-Kontaktadresse bereitgestellt.
- [ ] DNS-A/AAAA zeigen ausschließlich auf den bestätigten Numra-VPS.
- [ ] Ports 80/443 sind für Nginx vorgesehen; Docker veröffentlicht nur
  `127.0.0.1:8080`.
- [ ] `enable-https.sh` war erfolgreich und `certbot renew --dry-run` ist grün.
- [ ] TLS-Scan, HTTPS-Redirect, HSTS, CSP und Security-Header sind geprüft.
- [ ] `/etc/numra/numra.env` enthält exakt die HTTPS-Origin und hat Modus 0600.

## Release und Betrieb

- [ ] Alle lokalen und GitHub-CI-Gates sind grün.
- [ ] API- und Web-Images tragen denselben vollständigen Commit-SHA.
- [ ] Live-/Ready-Healthchecks und echte Profilberechnung funktionieren.
- [ ] Logs enthalten nach einem Pflichtszenario weder Namen noch Geburtsdatum,
  Request-Body, Profilantwort oder LLM-Ausgabe.
- [ ] Verschlüsseltes Konfigurationsbackup wurde erstellt.
- [ ] Wiederherstellung wurde durch Entschlüsseln und Inhaltsprüfung validiert.
- [ ] Rollback auf den vorherigen Image-Tag wurde in Staging erfolgreich
  ausgeführt.

## Kontrollierter Launch

- [ ] Eine geschlossene Beta mit Einwilligung der Testpersonen ist abgeschlossen.
- [ ] Kritische und hohe Fehler sind behoben; verbleibende Risiken dokumentiert.
- [ ] PDF, lokale Speicherung, Sperren/Entsperren, Export/Import, Löschen und
  Offline-Neustart wurden auf Desktop, Android und iOS geprüft.
- [ ] `public-launch-check.sh` läuft ohne Ausnahme durch.
- [ ] Erst danach wird der Zugriff öffentlich kommuniziert.

## Standardbefehle

```sh
NUMRA_DOMAIN=example.org NUMRA_TLS_EMAIL=admin@example.org \
  sudo -E deploy/scripts/enable-https.sh

sudo deploy/scripts/release.sh FULL_40_CHARACTER_COMMIT_SHA
sudo deploy/scripts/rollback.sh

AGE_RECIPIENT=age1... AGE_IDENTITY=/root/numra-backup-key.txt \
  sudo -E deploy/scripts/backup-config.sh

NUMRA_DOMAIN=example.org sudo -E deploy/scripts/public-launch-check.sh
```

`example.org`, E-Mail und age-Schlüssel sind Dokumentationswerte und müssen
durch die echten, vom Betreiber bestätigten Angaben ersetzt werden.
