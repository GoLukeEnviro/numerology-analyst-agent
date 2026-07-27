# Datenschutz- und Logging-Vertrag

## Verarbeitete Daten

Für die Berechnung verarbeitet Numra Geburtsname, optional aktiven Namen,
Geburtsdatum, explizites Berechnungsdatum und Methodenpolicy flüchtig. Eine
dauerhafte Speicherung findet nur nach Opt-in im Browser statt.

Der optionale LLM-Pfad erhält ausschließlich:

- deterministische Zahlen und deren stabile Referenzen,
- Berechnungshash und Aussageklassen,
- freigegebene Auszüge aus dem versionierten Wissenspaket,
- bei einer Rückfrage den vom Nutzer eingegebenen Rückfragetext.

Klarname und vollständiges Geburtsdatum sind im Provider-Payload verboten.

## Verbotene serverseitige Persistenz

- keine Profil-, Verlaufs-, Notiz- oder Benutzer-Datenbank
- keine Request- oder Response-Bodies in Access-, Error- oder Proxy-Logs
- keine LLM-Prompts oder LLM-Ausgaben in Logs oder Traces
- keine API-POST-Antworten in Browser-, Service-Worker- oder Proxy-Caches
- keine Nutzerprofile in Backups

Redis darf nur aus HMAC-pseudonymisierten, ablaufenden Quoten-Schlüsseln und
Zählern bestehen.

## Zulässige Betriebsmetadaten

Access-Logs dürfen ausschließlich HTTP-Methode, Pfad ohne Querystring,
Statuscode, validierte Korrelations-ID und Laufzeit enthalten. Unerwartete
Fehler dürfen nur mit ihrer Klassenbezeichnung protokolliert werden; Nachricht,
Stacktrace und Nutzdaten bleiben aus dem Produktionslog entfernt.

## Lokale Kontrolle

Profile, Berichte, Rückfragen und Notizen können lokal verschlüsselt, als
verschlüsseltes Archiv exportiert und vollständig gelöscht werden. Der
Schlüssel bleibt nur im Arbeitsspeicher und wird nach Inaktivität verworfen.
Verlorene Passphrasen oder nicht exportierte Gerätedaten sind nicht
wiederherstellbar.

## Launch-Gate

DeepSeek bleibt deaktiviert, bis Betreiber und Rechtsberatung Anbieter,
Verarbeitungsland, Drittlandtransfer, Vertragsgrundlage und den angezeigten
Einwilligungstext bestätigt haben. Die gesamte deterministische Anwendung bleibt
ohne LLM nutzbar.

