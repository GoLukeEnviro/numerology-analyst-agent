# ADR 0014: Kontrollierter öffentlicher Launch

- Status: akzeptiert
- Datum: 2026-07-26

## Entscheidung

Der öffentliche Launch ist kein impliziter Nebeneffekt eines Containerstarts.
Er besteht aus getrennten, fail-closed Gates:

1. Betreiber bestätigt Ziel-VPS, Domain, TLS-Kontakt und echte
   Impressums-/Datenschutzangaben.
2. DNS A/AAAA wird vor Certbot geprüft.
3. Ein HTTP-Bootstrap stellt nur die ACME-Challenge bereit.
4. Erst nach erfolgreichem Zertifikatstest aktiviert Host-Nginx HTTPS,
   Redirect, Security-Header und HSTS.
5. Releases werden ausschließlich mit vollständigem Commit-SHA gebaut und
   markiert.
6. Der vorherige Image-Tag bleibt für einen getesteten Rollback vorhanden.
7. Deployment-Secrets und Nginx-Konfiguration werden nur als
   age-verschlüsselter Stream gesichert; es entsteht kein Klartextarchiv.
8. `public-launch-check.sh` verweigert die Freigabe bei fehlender
   Rechtsfreigabe, fortbestehendem Impressumsblocker, falscher Origin, fehlendem
   Zertifikat oder unbestätigtem LLM-Transfer.

## Folgen

- Private Staging-Deployments bleiben ohne Domain über SSH-Tunnel möglich.
- HTTPS allein bedeutet noch keine öffentliche Freigabe.
- DeepSeek kann unabhängig vom deterministischen Produkt deaktiviert bleiben.
- Betreiberangaben und juristische Freigaben werden nie durch Code-Platzhalter
  oder erfundene Daten ersetzt.
- Eine geschlossene Beta, Backup-Verifikation und Rollback-Probe sind
  Pflichtbestandteile der Launch-Checkliste.
