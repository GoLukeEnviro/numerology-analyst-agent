# Numra RC2 — Private Staging Acceptance (2026-08-02)

> **Verdict: BLOCKED — NOT_EXECUTED**  
> Dieses Dokument beweist **nicht** Deploy/Restore/Rollback. Es beweist den
> Preflight-Stopp: kein genehmigter Numra-Staging-Host.

## 1. Infrastrukturentscheidung

| Anforderung | Ergebnis |
|-------------|----------|
| Separater Numra-Staging-VPS | **nicht zugewiesen** |
| Betreiber-bestätigter SSH-Alias | **fehlt** |
| Inventar | `docs/operations/vps-inventory-2026-07-26.md` (lesend, 2026-07-26): kein Alias eindeutig als Numra-VPS markiert |
| Shared Hermes/Trading-Host | **nicht verwendet** (Orchestrierungsregel: Isolation nicht bewiesen → fail closed) |

## 2. Staging Preflight

```text
HOST_ALIAS=
HOST_OS=
CPU=
RAM=
FREE_DISK=
DOCKER_VERSION=
COMPOSE_VERSION=
FIREWALL=
TAILSCALE=
DEPLOY_PATH=
DEPLOY_SHA=
API_IMAGE_DIGEST=
WEB_IMAGE_DIGEST=
PREFLIGHT_STATUS=BLOCKED_NO_APPROVED_HOST
```

**Operator-Aktion (einziger Entblocker):**

1. Genau einen SSH-Alias als Numra-Stagingziel benennen.
2. `deploy/scripts/preflight.sh` rein lesend ausführen.
3. Deterministisches Deploy mit `NUMRA_LLM_ENABLED=false` am gepinnten main/RC2-SHA.
4. Dieses Dokument mit konkreten SHAs/Digests und PASS-Zeilen aktualisieren.

## 3. Stufe 1 — Deterministischer Stack

```text
NUMRA_LLM_ENABLED=false
DEPLOY_STATUS=NOT_EXECUTED
HEALTH_LIVE=NOT_EXECUTED
HEALTH_READY=NOT_EXECUTED
PROFILE_CALCULATION=NOT_EXECUTED
```

**Lokaler Ersatz (kein Staging-Ersatz):** Docker-Compose-Smoke auf dem
Entwickler-Rechner 2026-08-02 gegen Images gebaut von main `5976ae2…`:

- `docker compose build` PASS  
- health live/ready PASS  
- `POST /api/v1/profiles/calculate` PASS (synthetisches Profil)  

Das erfüllt **nicht** Kriterium „private staging host“.

## 4. Stufe 2 — Backup und Restore

```text
BACKUP_CREATE=NOT_EXECUTED
BACKUP_VALIDATE=NOT_EXECUTED
RESTORE=NOT_EXECUTED
RESTORE_RE_SMOKE=NOT_EXECUTED
NOTE=Scripts under deploy/scripts/ exist; existence ≠ execution
```

## 5. Stufe 3 — Rollback-Rehearsal

```text
ROLLBACK_REHEARSAL_HOST=NOT_EXECUTED
BASELINE_SMOKE=NOT_EXECUTED
CANDIDATE_SMOKE=NOT_EXECUTED
ROLLBACK_SMOKE=NOT_EXECUTED
REDEPLOY_SMOKE=NOT_EXECUTED
```

### 5b. Lokaler Docker-Mechanik-Nachweis (kein Host-Ersatz)

Auf dem Entwickler-PC (Docker Desktop) mit **echten** Skripten
`deploy/scripts/rollback-rehearsal.sh` / `rollback.sh` (SHA-Tag-Vertrag
korrigiert, Health-Retry):

```text
LOCAL_DOCKER_ROLLBACK=PASS
BASELINE_TAG=7f9795c807f06c721a8c67c32823e8897de7f359
RC_TAG=8b0c711e510ebfb19f5cc814edab9d08e005c4eb
AFTER_ROLLBACK_CURRENT=7f9795c807f06c721a8c67c32823e8897de7f359
HEALTH_AFTER_ROLLBACK=PASS
PROFILE_AFTER_ROLLBACK=PASS
NUMRA_LLM_ENABLED=false
CLASSIFICATION=local_mechanics_only_not_private_staging_host
```

Dieser Nachweis **ersetzt nicht** AC3 Private Staging Host.

## 6. Stufe 4 — LLM/Provider-Smoke

```text
LEGAL_APPROVAL=NOT_CONFIRMED
TRANSFER_APPROVAL=NOT_CONFIRMED
SECRET_PROVISIONED=NO
REAL_PROVIDER_SMOKE=BLOCKED_LEGAL
LLM_STAGING=BLOCKED_LEGAL
```

## 7. Gate-Zusammenfassung

```text
PRIVATE_STAGING=BLOCKED
RESTORE=NOT_EXECUTED
ROLLBACK=NOT_EXECUTED
RC2_RELEASE_ALLOWED=NO
FAKE_PASS=NO
NEXT=operator_assigns_numra_staging_host
```

## 8. Issue-Bezug

- Epic #37  
- #39 Private staging  
- #40 Backup restore and rollback  
- #41 Provider smoke (legal blocked)  
