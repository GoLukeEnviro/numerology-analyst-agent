# Numra RC2 Private Staging Acceptance — VORLAGE

> **Status:** BLOCKED — kein genehmigter Staging-Host
> **Issue:** #39
> **Epic:** #37
> **Vorlage erstellt:** 2026-08-06

---

## Host-Preflight

- [ ] Host-Alias dokumentiert in `~/.ssh/config` und `docs/operations/vps-inventory-*.md`
- [ ] `deploy/scripts/preflight.sh` ausgeführt → PASS
- [ ] `/etc/numra/numra.env` angelegt (basierend auf `deploy/numra.env.example`)

```
Host-Alias:
OS:
Kernel:
Docker-Version:
Compose-Version:
Freier Speicher /opt:
```

---

## Deployment

- [ ] Ziel-SHA: ****\_\_\_****
- [ ] Image gebaut mit `deploy/scripts/build-release-image.sh`
- [ ] Image transferiert zum Host (`docker save` → `scp` → `docker load`)
- [ ] `deploy/scripts/release.sh <SHA>` ausgeführt

```
Ausgeführt am:
Image-Digest API:
Image-Digest Web:
```

---

## Smoke-Tests (NUMRA_LLM_ENABLED=false)

- [ ] `GET /` → 200 oder Redirect
- [ ] `GET /api/v1/health/live` → `{"status":"ok"}`
- [ ] `GET /api/v1/health/ready` → `{"status":"ready"}`
- [ ] `POST /api/v1/profiles/calculate` → 200, gültiges Profil

```json
{
  "person": {
    "core_name": "Max Mustermann",
    "birth_date": "1985-07-25",
    "as_of_date": "2026-08-06"
  },
  "policy": {
    "system": "pythagorean",
    "version": "v1"
  }
}
```

---

## Akzeptanz

- [ ] Alle Health-Checks grün
- [ ] Profilberechnung erfolgreich
- [ ] Keine Fehler in `docker compose logs`
- [ ] Release-Marker unter `/opt/numra/releases/current` vorhanden

---

## Go/No-Go

- [ ] **GO** — Staging-Deployment erfolgreich, RC2-Kandidat bereit
- [ ] **NO-GO** — Deployment fehlgeschlagen, siehe Fehlerprotokoll
- [ ] **BLOCKED** — Host nicht verfügbar (diesen Status nicht fälschen)
