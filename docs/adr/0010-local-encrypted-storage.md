# ADR 0010: Lokale, optional verschlüsselte Profilspeicherung

- Status: angenommen
- Datum: 2026-07-26

## Kontext

Numra verarbeitet Namen und Geburtsdaten, soll jedoch weder Konten noch eine
serverseitige Profilhistorie führen. Dauerhafte Speicherung muss ausdrücklich
gewählt werden, offline funktionieren und vollständig durch die nutzende Person
kontrollierbar bleiben.

## Entscheidung

Profile, Berechnungsläufe, Berichte, Gespräche und Notizen werden ausschließlich
in einer versionierten IndexedDB gespeichert. Dexie kapselt Schema und
Migrationen. Die Anwendung speichert ein Profil erst nach einer ausdrücklichen
Aktion.

Der optionale Tresor verwendet PBKDF2-HMAC-SHA256 mit einem zufälligen Salt und
600.000 Iterationen sowie AES-GCM-256 mit einer neuen 96-Bit-IV pro Payload. Der
abgeleitete Schlüssel bleibt nur im Arbeitsspeicher und wird nach 15 Minuten
Inaktivität verworfen. Nach einem Neustart darf ein vorhandener Tresor niemals
auf unverschlüsselte Speicherung zurückfallen.

Mehrprofil-Exporte sind ebenfalls mit PBKDF2 und AES-GCM authentifiziert
verschlüsselt. Vollständiges Löschen entfernt alle sechs lokalen Tabellen
einschließlich Tresormetadaten.

## Folgen

- Ohne Passphrase gibt es keine Wiederherstellung geschützter Daten.
- Geräteübergreifende Synchronisierung ist nicht Teil von V1.
- Offline-Lesezugriff benötigt einen entsperrten Tresor.
- Änderungen am IndexedDB-Schema benötigen explizite, getestete Migrationen.
- Cache Storage nimmt niemals API-POST-Antworten oder Profildaten auf.
