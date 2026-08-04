# Rollback-Rehearsal — lokaler Nachweis (2026-08-04)

> **Zweck:** ENG-01 verlangt neben dem gemergten SHA-Tag-Fix (`aa3c2c8`, PR #51)
> zusaetzlich, dass die Rehearsal-Mechanik "lokal/remote geuebt" ist. Dieser
> Lauf belegt die lokale Uebung; der Host-Lauf (A4.4) bleibt eigenstaendig
> erforderlich und ersetzt diesen Nachweis nicht.
> **Umgebung:** lokaler Docker Desktop unter Windows, keine echte
> Numra-Staging-Infrastruktur. `NUMRA_LLM_ENABLED=false` durchgehend.

## Ablauf und Ergebnis

```text
Kommando: sh deploy/scripts/rollback-rehearsal.sh
NUMRA_ENV_FILE=<scratchpad>/numra-rehearsal.env
NUMRA_RELEASE_DIR=<scratchpad>/releases
NUMRA_REPO_DIR=<Worktree-Root>

Baseline-SHA: cfa3f8412984e0ec21499fe3f6d2fec851c394d8
RC-SHA:       0b14271ab9be71d861a27a43a8a6dc050812b730

1. Baseline gebaut und deployed        -> health/ready PASS
2. RC-Release gebaut und deployed      -> health/ready PASS
3. deploy/scripts/rollback.sh ausgefuehrt
4. Health-Polling nach Rollback        -> PASS (20 Versuche, alle 2s)
5. release_dir/current == Baseline-SHA -> bestaetigt

Ergebnis: "Rollback-Rehearsal erfolgreich: 0b14271... -> cfa3f841...,
Health nach Rollback bestaetigt."
Exitcode: 0
```

Vollstaendiges Kommando-Log: `<scratchpad>/rollback-rehearsal.log` (nicht im
Repository — Scratchpad-Artefakt dieser Session, siehe Wiederholbarkeit unten).

## Zusaetzlich verifiziert: Restore-Mechanik (OPS-001)

Ergaenzend zur Rollback-Uebung wurde die Kernlogik von
`deploy/scripts/restore-config.sh` (encrypt → decrypt → strukturelle
Pruefung → atomarer `mv`) mit einem lokal erzeugten `age`-Schluesselpaar
end-to-end durchgespielt (Zielpfade auf ein Scratch-Verzeichnis umgebogen,
da echte `/etc`-Pfade Root auf einem Linux-Host voraussetzen):

```text
Verschluesseln (age --encrypt) -> Entschluesseln (age --decrypt) ->
tar -xzf -> Mitgliederzahl == 2 (erwartet) -> beide Dateien nicht leer ->
chmod/chown -> atomarer mv in Zielpfade

Ergebnis: numra.env und nginx-Konfiguration nach dem vollstaendigen
Zyklus byte-identisch mit dem Original.
```

**Bekannte Einschraenkung dieses lokalen Laufs:** `chmod 0600` zeigt unter
Git Bash auf NTFS nicht die erwartete Wirkung (`stat` meldet weiterhin
`644`) — das ist eine Windows-Dateisystem-Einschraenkung, keine
Fehlfunktion des Skripts. Auf dem Ziel-Linux-Host (ext4, echtes POSIX)
greift `chmod 0600` korrekt; das ist Teil des in A4.4 verlangten
Host-Nachweises und wird dort erneut geprueft.

## Was dieser Lauf beweist und was nicht

| Beweist | Beweist NICHT |
|---|---|
| Rollback-Mechanik selbst (Image-Swap, Release-Marker, Health-Check) funktioniert | Dass sich Baseline- und RC-Code inhaltlich unterscheiden (beide aus demselben Working Tree gebaut, siehe Kommentar in `rollback-rehearsal.sh`) |
| Restore-Kernlogik (Entschluesseln, strukturelle Pruefung, atomare Installation) ist korrekt | Verhalten auf dem echten Zielhost (Berechtigungen, `/etc`-Pfade, systemd/Nginx-Neustart) |
| Beide Skripte sind end-to-end lauffaehig, nicht nur syntaktisch gueltig | Bedingung 3 und 4 der Committee-Gates (die verlangen ausdruecklich den Host-Nachweis, siehe `docs/committee/rc2-release-decision.md`) |

## Wiederholbarkeit

Kein Repository-Artefakt dieses Laufs verbleibt außerhalb dieser
Protokolldatei — Env-Datei, Release-Marker, gebaute Images und das
`age`-Testschluesselpaar lagen im Session-Scratchpad und wurden nach dem
Lauf entfernt (`docker compose down`, `docker image rm` fuer beide
SHA-Tag-Paare). Zur Wiederholung: `deploy/scripts/rollback-rehearsal.sh`
mit denselben drei Env-Overrides gegen einen frischen, leeren
`NUMRA_RELEASE_DIR` starten.
