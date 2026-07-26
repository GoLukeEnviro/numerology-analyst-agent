# Pythagoreisches Vollprofil V1

Status: verbindliche Methodenspezifikation für `profile-calculation-result-v1`.

## Zahlen

- Lebensweg A: Summe aller Ziffern des Geburtsdatums, anschließend Reduktion.
- Lebensweg B: Monat, Tag und Jahresziffernsumme einzeln reduzieren, addieren und reduzieren.
- Geburtstagszahl: Kalendertag reduzieren.
- Einstellungszahl: Kalendermonat und ungekürzten Kalendertag addieren, dann reduzieren.
- Ausdruckszahl: Werte aller Buchstaben des jeweiligen Namens addieren.
- Seelenstrebenzahl: Werte aller als Vokal klassifizierten Buchstaben addieren.
- Persönlichkeitszahl: Werte aller als Konsonant klassifizierten Buchstaben addieren.
- Reifezahl: reduzierten Lebensweg A und reduzierte Ausdruckszahl des Geburtsnamens addieren
  und erneut reduzieren.

Die Meisterzahlen 11, 22 und 33 werden bei jeder Reduktion gehalten. Ein leerer
Vokal- oder Konsonantenanteil hat den expliziten Wert 0 und wird nicht interpretiert.

## Namen und Y

Leerzeichen und Bindestriche trennen Segmente und besitzen keinen Zahlenwert.
Geburtsname und aktiver Name werden nie vermischt. Für ein mehrdeutiges Y werden
die Varianten `y_as_consonant` und `y_as_vowel` vollständig ausgegeben; der
Audit-Trace setzt zugleich `disambiguation_required=true`.

## Determinismus

Der SHA-256-Hash umfasst Schema-Version, alle fachlichen Eingaben einschließlich
`as_of_date`, die vollständige Methodenpolicy, Ergebnisse und Audit-Trace.
`consent_given` und der Hash selbst sind ausgeschlossen.
