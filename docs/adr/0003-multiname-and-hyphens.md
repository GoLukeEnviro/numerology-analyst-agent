# ADR 0003: Mehrfachnamen und Bindestriche

> **Status:** Accepted
> **Entschieden am:** 2026-07-25
> **Entscheider:** Luke
> **Beziehung:** Leitet ab aus Master-Vertrag §3.1 (Behandlung von Bindestrichen und Mehrfachnamen), §6.1 (`normalisierungsentscheidungen`), §6.2 (`namensbasis`). Implementiert V1 Minimal Scope §4.1.

---

## Kontext

Der Master-Implementierungsprompt listet „Mehrfachnamen" als ausdrückliche Aufgabe (§3.1: „Behandlung von Umlauten, Akzenten, Bindestrichen und Mehrfachnamen") und fordert in den Kernberechnungen (§3.2) „Namenssegmente und Namensanteile". Er spezifiziert jedoch **keine konkrete Segmentierungs-Policy** für die Behandlung von:

- Vornamen (ein oder mehrere)
- Nachnamen (einfach oder doppelt)
- Bindestrichnamen (z. B. „Müller-Lüdenscheidt")
- Namenszusätzen (z. B. „van", „von", „de", „zu")
- Titeln (z. B. „Dr.", „Prof.", „Graf")
- Suffixen (z. B. „Jr.", „Sr.", „III")

Traditionelle numerologische Quellen sind hier uneinheitlich:

- Manche Quellen summieren **alle** Namensbestandteile zu einer Gesamtausdruckszahl.
- Manche Quellen ignorieren Titel und Suffixe.
- Manche Quellen behandeln Bindestriche als Trenner und summieren Segmente getrennt.
- Manche Quellen summieren nur Vornamen, nur Nachnamen oder nur die Initialen.

Für V1 muss eine konkrete, deterministische, auditierbare Policy festgelegt werden.

---

## Entscheidung

Für `pythagorean-v1` gilt die folgende 5-Punkte-Policy für Mehrfachnamen und Bindestriche:

### 1. Originalstruktur und Segmente erhalten

Der Originalname wird **strukturiert** gespeichert, nicht als flacher String. Die Struktur besteht aus Segmenten:

```yaml
name_segments:
  - type: "given_name"
    text: "Anna"
  - type: "given_name"
    text: "Maria"
  - type: "family_name"
    text: "Müller-Lüdenscheidt"
    sub_segments:
      - "Müller"
      - "Lüdenscheidt"
```

Leerzeichen und Bindestriche werden als Strukturinformation **erhalten**, nicht als flache Zeichenkette ineinandergeschmolzen. Die Struktur ist im `PersonInput.original_name_segments` autoritativ gespeichert.

### 2. Leerzeichen und Bindestriche bekommen keinen Zahlenwert

Bei der pythagoreischen Berechnung erhalten **Leerzeichen und Bindestriche keinen Zahlenwert**. Sie werden als Trenner behandelt und im `calculation_name` entweder entfernt oder als Nullwert markiert.

Begründung: Pythagoreisches Alphabet wertet A–Z (bzw. die 26 Basisbuchstaben nach ADR 0002). Leerzeichen und Bindestriche sind keine Buchstaben und erhalten keinen Wert. Jede andere Entscheidung wäre eine fachliche Willkür ohne traditionelle Basis.

### 3. Alle deklarierten Geburtsnamensegmente fließen in die Gesamtsumme ein

Alle Segmente, die zum **Geburtsnamen** (`core_name`, siehe ADR 0004) gehören, fließen in die **Gesamtsumme** für die Ausdrucks-/Schicksalszahl ein. Das schließt ein:

- Alle Vornamen (auch zweite und dritte Vornamen)
- Alle Nachnamen (auch doppelte Nachnamen)
- Bindestrichnamen-Segmente (beide Teile)
- Adelsprädikate („von", „zu", „de"), **sofern** sie als Teil des Geburtsnamens deklariert sind

Beispiel: „Anna Maria Müller-Lüdenscheidt" → Gesamtsumme aus „Anna" + „Maria" + „Müller" + „Lüdenscheidt".

### 4. Zusätzlich segmentierte Zwischenergebnisse ausgeben

Zusätzlich zur Gesamtsumme werden **segmentierte Zwischenergebnisse** ausgegeben. Für jedes Segment wird die Segmentzahl berechnet und im Trace dokumentiert:

```yaml
expression_number:
  total:
    raw_sum: 87
    reduced: 6
    master_number_detected: false
  segments:
    - segment: "Anna"
      raw_sum: 17
      reduced: 8
    - segment: "Maria"
      raw_sum: 28
      reduced: 1
    - segment: "Müller"  # bereits calculation_name: "Muller"
      raw_sum: 23
      reduced: 5
    - segment: "Lüdenscheidt"  # bereits calculation_name: "Ludenscheidt"
      raw_sum: 19
      reduced: 1
```

Die Gesamtsumme und die Segmentergebnisse werden **beide** ausgegeben, nicht nur die Gesamtsumme. Begründung: Traditionelle Quellen nutzen manchmal Segmentzahlen für zusätzliche Deutungen; der Nutzer soll beide Informationen haben.

### 5. Titel und Suffixe standardmäßig ausschließen, aber als Metadaten behalten

Titel (akademisch: „Dr.", „Prof.", „Dipl.-Ing."; Adel: „Graf", „Freiherr") und Suffixe („Jr.", „Sr.", „III") werden bei der **numerologischen Berechnung standardmäßig ausgeschlossen**. Sie werden jedoch als **Metadaten** im `PersonInput` gespeichert und im Trace referenziert:

```yaml
person_input:
  core_name:
    segments:
      - { type: "given_name", text: "Anna" }
      - { type: "family_name", text: "Müller" }
    titles: ["Dr."]
    suffixes: []
  # numerologisch gewertet: nur Anna + Müller
```

Begründung: Titel und Suffixe sind in der Regel **nicht** Teil des Geburtsnamens, sondern spätere Zuschreibungen. Numerologisch sind Geburtsnamen die autoritative Basis. Die numerologische Tradition behandelt Titel inkonsistent — der konservative Default ist „ausschließen", aber als Metadaten behalten macht die Information reversibel.

Eine optionale Policy `include_titles = true` kann in späteren Releases angeboten werden, ist aber nicht V1-Default.

---

## Konsequenzen

### Positiv

- **Vollständige Auditspur:** Jedes Segment, jede Summe, jede Reduktion ist nachvollziehbar. Gesamtsumme und Segmentergebnisse sind beide sichtbar.
- **Strukturinformation erhalten:** Leerzeichen und Bindestriche sind als Trenner dokumentiert, nicht still verschluckt.
- **Reversibilität:** Titel und Suffixe sind ausgeschlossen, aber als Metadaten behalten. Nutzer kann später entscheiden, sie einzubeziehen.
- **Deterministisch:** Gleicher Input + gleiche Policy → gleiche Segmentstruktur und gleiche Summen.
- **Mit ADR 0004 verträglich:** Die Segmentierung ist die Grundlage für die Trennung von `core_name` und `active_name`.

### Negativ

- **Komplexere Ausgabe:** Nutzer sehen nicht nur eine Zahl, sondern eine strukturierte Ausgabe mit Segmenten. Das muss in der CLI sauber kommuniziert werden.
- **Adelsprädikate sind heikel:** „von", „de", „van" sind manchmal Teil des Geburtsnamens (Deutschland, Niederlande), manchmal nicht. In V1 werden sie einbezogen, **sofern der Nutzer sie als Teil von `core_name` deklariert**. Das erfordert korrekte Nutzer-Eingabe.
- **Optional: Debug-Modus pro Segment.** Für Power-Nutzer wäre ein Debug-Modus wünschenswert, der jeden Buchstaben jedes Segments mit seinem Wert auflistet. In V1 nicht zwingend; kann später kommen.

### Folgeentscheidungen nötig

- OFFEN: Behandlung von Initialen (z. B. „J. R. R. Tolkien"). Sind Initialen ein vollständiger Buchstabe mit Wert, oder werden sie als Platzhalter behandelt? In V1 vermutlich: Initialen sind vollständige Buchstaben mit pythagoreischem Wert.
- OFFEN: Behandlung von „van"/„von"/„de" als optionale Policy (`include_noble_particles`).
- OFFEN: Numerische Werte für nichlateinische Namensbestandteile (z. B. chinesische Namen in Pinyin — werden nach ADR 0002 Akzent-entfernt, aber was ist mit „Q", „X", „Z" in Pinyin — die sind im pythagoreischen A–Z enthalten).

---

## Alternativen betrachtet

### Alternative 1: Nur Vornamen werten

- **Vorteil:** Sehr einfach.
- **Nachteil:** Fachlich unvollständig. Ausdrucks-/Schicksalszahl ist traditionell die Summe aller Namensbestandteile.
- **Status:** **Abgelehnt.**

### Alternative 2: Titel mitzählen (Default)

- **Vorteil:** Manche Traditionen tun das.
- **Nachteil:** Titel sind nicht Geburtsname. Verfälscht die numerologische Basis. Inkonsistent zwischen Nutzern (manche haben Titel, manche nicht).
- **Status:** **Abgelehnt als Default.** Optional in späteren Releases.

### Alternative 3: Suffixe mitzählen (Default)

- **Vorteil:** Manche Traditionen (insbes. US-amerikanische) tun das.
- **Nachteil:** Analog zu Titeln. Verfälscht Geburtsnamens-Basis.
- **Status:** **Abgelehnt als Default.** Optional in späteren Releases.

### Alternative 4: Nur Gesamtsumme, keine Segmentergebnisse

- **Vorteil:** Minimaler Output.
- **Nachteil:** Verliert die traditionelle Information über Segmentzahlen, die von manchen Deutungsschulen genutzt wird.
- **Status:** **Abgelehnt.** Segmentergebnisse sind zu wertvoll, um sie zu verwerfen.

### Alternative 5: Bindestriche als Trenner mit eigenem Zahlenwert

- **Vorteil:** Sehr explizite Behandlung.
- **Nachteil:** Es gibt keinen traditionellen pythagoreischen Zahlenwert für „-". Jede Wertzuweisung wäre eine Willkür.
- **Status:** **Abgelehnt.** Leerzeichen und Bindestriche bekommen keinen Zahlenwert.

### Alternative 6: Adelsprädikate immer ausschließen

- **Vorteil:** Einfachere Default-Regel.
- **Nachteil:** In Deutschland und den Niederlanden sind „von"/„van" oft Teil des Geburtsnamens. Ausschließen würde die numerologische Basis verfälschen.
- **Status:** **Abgelehnt.** Adelsprädikate werden einbezogen, wenn vom Nutzer als Teil von `core_name` deklariert.

---

## Verweise

- Master-Vertrag: `docs/governance/master-implementation-contract.md` §3.1, §3.2, §6.1, §6.2
- V1 Minimal Scope: `docs/v1-minimal-scope.md` §4.1, AC-6
- ADR 0001: `docs/adr/0001-y-rule-phonetic.md` (Y-Klassifikation je Segment)
- ADR 0002: `docs/adr/0002-unicode-umlaut-normalization-de-direct-v1.md` (Umlaut-Normalisierung je Segment)
- ADR 0004: `docs/adr/0004-core-name-vs-active-name.md` (Trennung von `core_name` und `active_name`)
- Methodenspezifikation (folgt): `docs/methods/pythagorean-v1.md`
