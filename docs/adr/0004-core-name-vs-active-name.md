# ADR 0004: Geburtsname vs. aktueller Name — Zwei-Ebenen-Modell

> **Status:** Accepted
> **Entschieden am:** 2026-07-25
> **Entscheider:** Luke
> **Beziehung:** Leitet ab aus Master-Vertrag §3.1 („Namensänderungen und Geburtsname"), §6.1 (Personeneingabe: „vollständiger Name", „Geburtsname", „optional aktueller Name"), §6.2 (`namensbasis`). Implementiert V1 Minimal Scope §4.1.

---

## Kontext

Der Master-Implementierungsprompt nennt Namensbasis als Policy-Feld (§6.2: `namensbasis`) und „Namensänderungen und Geburtsname" als ausdrückliche Aufgabe (§3.1). Er spezifiziert jedoch **keinen Algorithmus**, wie Geburtsname und aktueller Name in Beziehung zueinander zu setzen sind.

Traditionelle numerologische Quellen sind hier **nicht einheitlich** (vgl. Professional Numerology Association, numerology.com, affinity-numerology.com):

- Manche Quellen verwenden **nur den Geburtsnamen** als autoritative Basis für das Kernprofil.
- Manche Quellen verwenden **nur den aktuell geführten Namen**, weil er die „energetische Schwingung der Gegenwart" repräsentiere.
- Manche Quellen verwenden einen **gewichteten Mix** (z. B. 60 % Geburtsname, 40 % aktueller Name).
- Manche Quellen berechnen **zwei separate Profile** und interpretieren den Übergang (Geburtsname = Potenzial, aktueller Name = Ausdruck).

Für V1 muss eine konkrete, deterministische, auditierbare Policy festgelegt werden, die:

1. Keine pseudo-universelle Regel vorgaukelt, wo keine existiert.
2. Beide Profile klar getrennt hält.
3. Den Nutzer nicht zwingt, eine fachliche Vorentscheidung zu treffen, die er nicht treffen kann.
4. Mit dem Master-Vertrag §2.2 (Aussageklassen-Trennung) verträglich ist — eine still vermischte Zahl wäre eine unerkannte `interpretive_hypothesis`.

---

## Entscheidung

Für `pythagorean-v1` gilt das folgende **Zwei-Ebenen-Modell**:

### 1. `core_name` = vollständiger Geburtsname

Der `core_name` ist der **vollständige Geburtsname** einer Person, wie bei der Geburt eingetragen. Er umfasst alle Vornamen, alle Nachnamen (inkl. Adelsprädikate, wenn Teil des Geburtsnamens), und ist die autoritative Basis für das **Kernprofil**.

### 2. `active_name` = aktuell geführter Name

Der `active_name` ist der Name, den die Person **aktuell führt**. Das kann identisch mit `core_name` sein (keine Namensänderung), oder abweichen durch:

- Heirat (ggf. neuer Nachname)
- Adoption
- Rechtliche Namensänderung
- Künstlername / Pseudonym (OFFEN: ob Pseudonyme in V1 als `active_name` gelten)

Der `active_name` ist die Basis für ein **Ergänzungsprofil**.

### 3. Kernprofil aus `core_name`

Das **Kernprofil** wird aus dem `core_name` berechnet. Es umfasst:

- Ausdrucks-/Schicksalszahl
- Seelenstrebenzahl
- Persönlichkeitszahl
- Reifezahl
- (Später, in `0.2.0+`: zugehörige Deutungshypothesen)

Das Kernprofil ist die „numerologische DNA" — es ist stabil über das Leben und stellt das Potenzial dar.

### 4. Ergänzungsprofil aus `active_name`

Das **Ergänzungsprofil** wird aus dem `active_name` berechnet, **falls** `active_name ≠ core_name`. Es umfasst die gleichen Zahlen (Ausdruck, Seelenstreben, Persönlichkeit, Reife), aber aus dem aktuell geführten Namen.

Das Ergänzungsprofil ist die „numerologische Gegenwart" — es zeigt, wie die Person aktuell erscheint und agiert.

### 5. Niemals beide still zusammenrechnen

**Strikte Regel:** `core_name` und `active_name` werden **niemals** still in eine einzige Zahl zusammengerechnet. Es gibt keinen Default-Mix, kein gewichtetes Mittel, keine implizite Verschmelzung.

Jede Zahl im Ergebnis ist explizit einem Profil zugeordnet:

```yaml
profile:
  core_profile:  # aus core_name
    expression_number: { raw_sum: 87, reduced: 6, ... }
    soul_urge_number: { ... }
    personality_number: { ... }
    maturity_number: { ... }
  active_profile:  # aus active_name, nur wenn abweichend
    expression_number: { raw_sum: 75, reduced: 3, ... }
    soul_urge_number: { ... }
    personality_number: { ... }
    maturity_number: { ... }
  note: "Kernprofil aus Geburtsname; Ergänzungsprofil aus aktiv geführtem Namen. Keine Vermischung."
```

Der Trace dokumentiert für jede Zahl, aus welchem Namen sie stammt.

### Kodierung im Domain-Modell

`name_basis` ist ein Pflichtfeld in `MethodPolicy` mit Werten:

- `core_name_only` — nur Kernprofil aus `core_name`
- `active_name_only` — nur Ergänzungsprofil aus `active_name`
- `both_separate` (Default in `0.1.0`) — beide Profile getrennt ausgeben

Es gibt **keinen** Wert wie `mixed` oder `weighted` — das ist bewusst. Ein gewichteter Mix ist eine fachliche Willkür ohne traditionelle Basis und würde die Aussageklassen-Trennung verletzen.

### `maturity_number` (Reifezahl) — Sonderbehandlung

Die Reifezahl wird traditionell aus einer Kombination von Lebensweg (aus Geburtsdatum) und Ausdruckszahl (aus Name) berechnet. Im Zwei-Ebenen-Modell ergibt das:

- `core_profile.maturity_number` = Kombination(Lebensweg, core_name_expression)
- `active_profile.maturity_number` = Kombination(Lebensweg, active_name_expression)

Beide Reifezahlen werden separat ausgewiesen. Der Lebensweg (aus Geburtsdatum) ist identisch für beide Profile, da das Geburtsdatum sich nicht ändert.

---

## Konsequenzen

### Positiv

- **Keine pseudo-universelle Regel:** Das Modell behauptet nicht, eine „richtige" Antwort zu haben, wo keine existiert. Es respektiert die Uneinheitlichkeit der Tradition.
- **Nutzer sieht beide Profile klar getrennt:** Weder Geburtsname noch aktueller Name wird versteckt. Beide sind sichtbar, beide sind auditierbar.
- **Mit Master-Vertrag §2.2 verträglich:** Keine still vermischte Zahl, keine unerkannte `interpretive_hypothesis`. Jede Zahl hat einen klaren Ursprung.
- **Deterministisch:** Gleicher Input (zwei Namen) → zwei Profile, beide deterministisch berechenbar.
- **Erweiterbar:** Spätere Releases können Deutungs-Hypothesen über die Beziehung zwischen Kern- und Ergänzungsprofil hinzufügen (z. B. „wenn active_expression vs. core_expression auf eine Entwicklungsaufgabe hinweist"). Solche Hypothesen sind dann aber klar als `interpretive_hypothesis` klassifiziert.
- **Stabil über Lebensphasen:** Das Kernprofil ändert sich nicht durch Heirat — es bleibt die autoritative Basis.

### Negativ

- **Komplexere Ausgabe:** Nutzer sehen potenziell zwei Profile statt eines. Das muss in der CLI sauber kommuniziert werden („Kernprofil" vs. „Ergänzungsprofil").
- **Entscheidung über `name_basis` erforderlich:** Nutzer müssen wissen, welche Profile sie sehen wollen. Default `both_separate` ist pragmatisch, kann aber Nutzer überfordern, die nur eine Zahl erwarten.
- **Pseudonyme sind OFFEN.** Künstlername, Ordensname, Spitzname — fallen die unter `active_name`? Master-Vertrag schweigt. Klärung nötig (siehe OFFEN unten).
- **Reifezahl verdoppelt sich.** Wenn `active_name ≠ core_name`, gibt es zwei Reifezahlen. Das ist fachlich korrekt, aber Output-Komplexität steigt.

### Folgeentscheidungen nötig

- OFFEN: Behandlung von Pseudonymen / Künstlernamen / Spitznamen als `active_name`. Vermutung: ja, aber erst in `0.2.0+`, wenn Interpretation existiert. In `0.1.0`: nur rechtlich geführte Namen als `active_name`.
- OFFEN: Anzeige-Reihenfolge (Kern- oder Ergänzungsprofil zuerst?). Default: Kernprofil zuerst (Geburtsname als Basis).
- OFFEN: Wie wird mit mehreren historischen `active_name` umgegangen (z. B. Name nach erster Ehe, Name nach zweiter Ehe)? In V1 nur ein `active_name`. Später: Liste von Phasen.

---

## Alternativen betrachtet

### Alternative 1: Nur Geburtsname (`name_basis = core_name_only`)

- **Vorteil:** Maximale Stabilität, deterministisch, traditionell gut begründet (Geburtsname als „essentielle Schwingung").
- **Nachteil:** Ignoriert die Lebensrealität vieler Menschen (Ehe, Adoption, rechtliche Änderung). Verfehlt die Gegenwarts-Relevanz.
- **Status:** **Abgelehnt als alleinige V1-Default-Regel.** Als optionale `name_basis` verfügbar.

### Alternative 2: Nur aktueller Name (`name_basis = active_name_only`)

- **Vorteil:** Spiegelt die Gegenwart, von manchen modernen Traditionen bevorzugt.
- **Nachteil:** Verwirft die traditionell zentrale Rolle des Geburtsnamens. Verliert Stabilität über Lebensphasen.
- **Status:** **Abgelehnt als alleinige V1-Default-Regel.** Als optionale `name_basis` verfügbar.

### Alternative 3: Gewichtetes Mittel (z. B. 60 % core, 40 % active)

- **Vorteil:** Scheint „das Beste aus beiden Welten" zu sein.
- **Nachteil:** **Fachliche Willkür.** Es gibt keine traditionelle Basis für eine spezifische Gewichtung. Eine Zahl wie „5.4" ist numerologisch sinnlos (pythagoreische Zahlen sind ganzzahlig 1–9 plus Meisterzahlen). Selbst eine gerundete Zahl wäre eine unerkannte `interpretive_hypothesis`, die vorgaukelt, eine Berechnung zu sein.
- **Status:** **Kategorisch abgelehnt.** Verletzt Master-Vertrag §2.2 und §2.4.

### Alternative 4: Verschmolzene Summe (Buchstaben beider Namen zusammen addieren)

- **Vorteil:** Einfach.
- **Nachteil:** **Fachlich unsinnig.** Buchstaben doppelter Namen (Anna Müller + Anna Schneider = 2× Anna, 1× Müller, 1× Schneider) würden inkonsistente Summen ergeben. Keine traditionelle Basis.
- **Status:** **Kategorisch abgelehnt.**

### Alternative 5: Nutzer wählt vorab (ein Profil oder anderes)

- **Vorteil:** Maximale Nutzer-Kontrolle.
- **Nachteil:** Verschiebt eine fachliche Entscheidung auf Nutzer, der sie oft nicht treffen kann.„Welcher Name ist richtig?" ist eine fachliche Frage, die das System nicht dem Nutzer aufbürden sollte.
- **Status:** **Abgelehnt als Default.** Der Default `both_separate` ist transparenter.

---

## Verweise

- Master-Vertrag: `docs/governance/master-implementation-contract.md` §3.1, §6.1, §6.2
- V1 Minimal Scope: `docs/v1-minimal-scope.md` §4.1, AC-7
- ADR 0001: `docs/adr/0001-y-rule-phonetic.md` (Y-Klassifikation gilt pro Name)
- ADR 0002: `docs/adr/0002-unicode-umlaut-normalization-de-direct-v1.md` (Umlaut-Normalisierung gilt pro Name)
- ADR 0003: `docs/adr/0003-multiname-and-hyphens.md` (Segmentierung gilt pro Name)
- Methodenspezifikation (folgt): `docs/methods/pythagorean-v1.md`
- Traditioneller Vergleich: Professional Numerology Association (Publikationen zur Namensbasis)
