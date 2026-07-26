# VPS-Inventarisierung für Numra

Datum: 2026-07-26
Modus: ausschließlich lesend

## Ergebnis

In der lokalen SSH-Konfiguration ist kein Ziel eindeutig als Numra-VPS
gekennzeichnet. Es existieren mehrere fachfremde beziehungsweise generische
Aliase, aus denen weder die vorgesehene Numra-Rolle noch die im Projektplan
genannten Ressourcen zweifelsfrei hervorgehen.

Deshalb wurde keine SSH-Verbindung aufgebaut und kein entfernter Befehl
ausgeführt. Insbesondere wurden keine Verzeichnisse, Benutzer, Firewallregeln,
Container oder Pakete auf einem VPS verändert.

## Benötigte Betreiberbestätigung

Vor der ersten Inventarisierung muss der Betreiber genau einen SSH-Alias als
Numra-Stagingziel benennen. Danach führt
`deploy/scripts/preflight.sh` ausschließlich folgende lesende Prüfungen aus:

- Distribution, Kernel und Architektur
- CPU- und Arbeitsspeicher
- freier Speicher unter `/opt`
- Docker- und Compose-Version
- Listener auf 80, 443 und 8080

Das Standardziel wird nur akzeptiert, wenn Docker unterstützt wird, mindestens
40 GiB frei sind und `127.0.0.1:8080` verwendet werden kann. Andernfalls ist
das alternative Ziel ebenfalls erst nach ausdrücklicher Zuordnung zu prüfen.
