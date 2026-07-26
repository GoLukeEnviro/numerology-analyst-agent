# Numra Deployment

Dieser Stack ist für ein privates Staging auf einem Linux-VPS vorbereitet.
`gateway` bindet ausschließlich an `127.0.0.1:8080`; `api` und `redis` besitzen
keinen Host-Port. **Kein öffentlicher Launch** erfolgt vor Betreiberangaben,
Domain, HTTPS, rechtlicher DeepSeek-Prüfung und Schritt 12.

## Zielhost nur lesend prüfen

Erst wenn der Betreiber einen SSH-Alias eindeutig als Numra-Ziel bestätigt:

```sh
ssh ALIAS 'sh -s' < deploy/scripts/preflight.sh
```

Der Befehl verändert den Host nicht. Freigabekriterien sind Ubuntu 24.04 LTS
oder eine ausdrücklich akzeptierte Alternative, mindestens 40 GiB freier
Speicher, Docker mit Compose und ein freier Loopback-Port 8080.

## Verzeichnis und Secrets vorbereiten

Diese Befehle sind erst nach bestätigtem Zielhost auszuführen:

```sh
sudo install -d -m 0755 /opt/numra/repository
sudo install -d -m 0700 /etc/numra
sudo install -m 0600 deploy/numra.env.example /etc/numra/numra.env
sudo editor /etc/numra/numra.env
sudo chown root:root /etc/numra/numra.env
sudo chmod 0600 /etc/numra/numra.env
```

Für aktiviertes LLM muss `NUMRA_RATE_LIMIT_HMAC_SECRET` mindestens 32 zufällige
Bytes enthalten, zum Beispiel erzeugt mit `openssl rand -hex 32`. Der
DeepSeek-Schlüssel wird nie in Git, Compose oder ein Image geschrieben.

## Stack validieren und starten

```sh
cd /opt/numra/repository
export NUMRA_IMAGE_TAG="$(git rev-parse --verify HEAD)"
docker compose --env-file /etc/numra/numra.env config --quiet
NUMRA_REPO_DIR="$PWD" deploy/scripts/stage.sh
curl --fail --silent http://127.0.0.1:8080/api/v1/health/ready
```

Redis ist absichtlich flüchtig und enthält nur ablaufende Quoten. Es gibt keine
serverseitige Profilablage und deshalb auch kein Profilbackup.

## Privates Staging öffnen

Auf dem eigenen Rechner:

```sh
ssh -L 8080:127.0.0.1:8080 ALIAS
```

Danach ist Numra unter `http://localhost:8080` erreichbar. Die Origin in
`/etc/numra/numra.env` muss für dieses Staging
`NUMRA_ALLOWED_ORIGINS=http://localhost:8080` bleiben.

## Diagnose ohne Nutzdaten

```sh
docker compose ps
docker compose logs --since=10m api gateway redis
curl --fail --silent http://127.0.0.1:8080/api/v1/health/live
curl --fail --silent http://127.0.0.1:8080/api/v1/health/ready
```

Gateway-Access-Logs und Uvicorn-Access-Logs sind deaktiviert. Fehlerdiagnose
verwendet Status, Healthchecks und Korrelations-IDs, nie Request-Bodies.
