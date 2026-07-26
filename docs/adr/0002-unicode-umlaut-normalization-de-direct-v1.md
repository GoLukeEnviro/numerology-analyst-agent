# ADR 0002: Unicode-Normalisierung und deutsche Umlaut-Policy `de-direct-v1`

> **Status:** Accepted
> **Entschieden am:** 2026-07-25
> **Entscheider:** Luke
> **Beziehung:** Leitet ab aus Master-Vertrag §3.1 (Behandlung von Umlauten, Akzenten, Bindestrichen und Mehrfachnamen), §6.1 (`normalisierungsentscheidungen`), §6.2 (`normalisierungsregeln`). Implementiert V1 Minimal Scope §4.1.

---

## Kontext

Der Master-Implementierungsprompt benennt Normalisierung als Pflichtbestandteil der pythagoreischen Methodenspezifikation (§3.1, §6.1, §6.2). Er spezifiziert jedoch **keine konkrete Policy** für Umlaute, Akzente und Sonderzeichen.

Zwei separate Ebenen müssen unterschieden werden, die oft verwechselt werden:

### Ebene A — Unicode-Normalisierung (technisch)

Unicode-Kanonisierung (NFC, NFD, NFKC, NFKD nach Unicode TR15) ist eine **technische Normalisierung**, die Kompositions- und Dekompositionsformen vereinheitlicht. Beispiel: „Ä" kann als ein Codepoint (U+00C4) oder als „A" + kombinierendes Trema (U+0041 U+0308) kodiert sein. NFC vereinheitlicht das auf die zusammengesetzte Form. NFC verändert aber **nicht** den Zeicheninhalt — „Ä" bleibt „Ä".

### Ebene B — Numerologische Fachregel (semantisch)

Die numerologische Fachregel entscheidet, **welchen Zahlenwert** ein Zeichen erhält. Für „Ä" gibt es fachlich mehrere Traditionen:

- `de-direct-v1`: Ä→A, Ö→O, Ü→U, ß→SS (direkte Ersetzung,„Ä" zählt wie „A")
- `de-expanded-v1`: Ä→AE, Ö→OE, Ü→UE, ß→SS (Expandierte Form,„Ä" zählt wie „A" + „E")
- Andere Traditionen (z. B. Ä als eigener Buchstabe mit eigenem Wert)

**Ebene A und Ebene B sind unterschiedliche Operationen.** Unicode-NFC allein ist **keine** numerologische Fachregel — das ist ein häufiger Implementierungsfehler (vgl. Unicode TR15 §1: „Normalization does not guarantee semantic identity").

Für V1 muss eine konkrete, deterministische, auditierbare Policy festgelegt werden, die beide Ebenen sauber trennt.

---

## Entscheidung

Für `pythagorean-v1` mit `locale=de` gilt die folgende 7-Punkte-Policy:

### 1. Originalname unverändert speichern

Der Originalname (inkl. Umlaute, Akzente, Sonderzeichen) wird **unverändert** im `PersonInput` gespeichert. Er ist die autoritative Eingabe und wird nie überschrieben.

### 2. Unicode-NFC für Speicherung und Vergleich

Vor jeder Verarbeitung wird der Originalname nach **Unicode-NFC** normalisiert (technische Ebene A). Das stellt sicher, dass visuell identische Eingaben mit unterschiedlicher Kodierung (z. B. „Ä" als U+00C4 vs. „A"+U+0308) identisch behandelt werden. NFC ist die kanonische Kompositionsform und Standard für Speicherung.

### 3. Separates `calculation_name` erzeugen

Aus dem NFC-normalisierten Originalnamen wird ein **separater** `calculation_name` abgeleitet. Der `calculation_name` ist die Zeichenkette, die tatsächlich in die pythagoreische Berechnung eingeht. Originalname und `calculation_name` sind **zwei separate Felder** — niemals dasselbe.

### 4. Deutsche Policy `de-direct-v1`

Für die Ableitung des `calculation_name` gilt (semantische Ebene B):

| Original | calculation_name |
|---|---|
| Ä | A |
| Ö | O |
| Ü | U |
| ß | SS |

Dies ist die **Default-Policy** für `locale=de` in `0.1.0`. Sie muss in `MethodPolicy` explizit gesetzt werden (`umlaut_policy = de-direct-v1`), keine stillen Defaults (Master-Vertrag §6.2).

### 5. Akzente im `calculation_name` entfernen

Zusätzlich zu `de-direct-v1` werden **diakritische Akzente** im `calculation_name` entfernt (z. B. é→e, à→a, ñ→n, ç→c). Das ist eine separate Operation von `de-direct-v1`. Begründung: Pythagoreisches Alphabet ist A–Z ohne Akzente; ein pythagoreischer Standard wertet nur die 26 Basisbuchstaben aus.

Die Akzent-Entfernung erfolgt nach Unicode-Dekomposition (NFD) + Entfernen der Kombinierungszeichen (U+0300–U+0362 etc.). Dies ist deterministisch und wird im Trace dokumentiert.

### 6. Jede Transformation in der Auditspur dokumentieren

Jede einzelne Transformation — NFC-Normalisierung, `de-direct-v1`-Ersetzung, Akzent-Entfernung — wird im Audit-Trace dokumentiert:

```yaml
normalization_steps:
  - step: "unicode_nfc"
    input: "Müller"
    output: "Müller"
    note: "Bereits NFC-kompatibel"
  - step: "umlaut_policy_de_direct_v1"
    input: "Müller"
    output: "Muller"
    transformations:
      - { original: "ü", replacement: "u", position: 1 }
  - step: "accent_removal"
    input: "Muller"
    output: "Muller"
    note: "Keine Akzente vorhanden"
  - step: "final_calculation_name"
    output: "Muller"
```

Der Originalname bleibt im `PersonInput.original_name` unverändert erhalten und referenziert im Trace.

### 7. Alternative Policy `de-expanded-v1` später optional

Eine alternative Umlaut-Policy `de-expanded-v1` (Ä→AE, Ö→OE, Ü→UE, ß→SS) wird als **bekannte, aber nicht in V1 aktivierte** Policy dokumentiert. Sie kann in späteren Releases als optionale Policy angeboten werden.

**Strikte Regel:** `de-direct-v1` und `de-expanded-v1` dürfen **niemals gemischt** werden (innerhalb einer Berechnung oder innerhalb eines Releases). Eine Berechnung verwendet genau eine Umlaut-Policy, die in `MethodPolicy` explizit gesetzt ist.

---

## Konsequenzen

### Positiv

- **Deterministisch:** Gleicher Input → gleicher `calculation_name` → gleiche Zahl. Kein Raten.
- **Vollständig nachvollziehbar:** Jede Transformation ist im Trace dokumentiert, mit Original, Output, Position, Begründung.
- **Originalname bleibt autoritativ:** Der Nutzer sieht seinen eingegebenen Namen unversehrt; der `calculation_name` ist transparent abgeleitet, nie verdeckt.
- **Ebenen sauber getrennt:** Unicode-NFC (technisch) und numerologische Fachregel (semantisch) werden nicht verwechselt. Vermeidet den typischen Implementierungsfehler „NFC reicht als Normalisierung".
- **Strikt separate Policies:** Kein Vermischen von `de-direct-v1` und `de-expanded-v1`. Vermeidet fachliche Verunreinigung (Master-Vertrag §3.1: „Streitige Varianten sind dokumentiert und nicht still vermischt").
- **Sprachen-erweiterbar:** Andere Locales (en, fr, es) können später eigene Umlaut-/Akzent-Policies definieren, ohne `de-direct-v1` zu berühren.

### Negativ

- **`de-direct-v1` ist eine Traditionswahl, nicht universell:** Manche numerologischen Schulen bevorzugen `de-expanded-v1`. Die Wahl für `de-direct-v1` als V1-Default ist pragmatisch (einfacher, häufiger in populären Quellen), nicht dogmatisch.
- **Akzent-Entfernung kann Informationen verlieren:** „José" → „Jose", „François" → „Francois". Das ist fachlich korrekt für pythagoreisches A–Z, aber für Nutzer nicht offensichtlich. Kommunikation via Trace.
- **SS-Expansion bei ß:** ß→SS ergibt zwei Zeichen, die beide numerologisch gewertet werden. Das kann unerwartete Summen erzeugen. Im Trace nachvollziehbar, aber für Nutzer überraschend.
- **Y bleibt unberührt:** Y wird nicht durch Umlaut-Policy verändert — es fällt unter ADR 0001 (`y_mode = phonetic`).

### Folgeentscheidungen nötig

- OFFEN: Akzent-Entfernung für nicht-lateinische Schriftsysteme (kyrillisch, griechisch) — für V1 nicht relevant, aber für später.
- OFFEN: Behandlung von Ligaturen (z. B. Æ, Œ) — in V1 nicht enthalten, muss später spezifiziert werden.

---

## Alternativen betrachtet

### Alternative 1: `de-expanded-v1` als Default (Ä→AE, Ö→OE, Ü→UE, ß→SS)

- **Vorteil:** Bewahrt die lautliche Komplexität („Ä" ≈ „AE"). Von manchen Traditionen bevorzugt.
- **Nachteil:** Komplexer, erzeugt längere calculation_names, kann unerwartete Summen erzeugen. Für V1 nicht der häufigste Standard.
- **Status:** **Abgelehnt als V1-Default.** Als **spätere optionale Policy** vorgesehen (`de-expanded-v1`).

### Alternative 2: Nur Unicode-NFC, keine semantische Fachregel

- **Vorteil:** Minimaler Implementierungsaufwand.
- **Nachteil:** **Fachlich falsch.** NFC erhält „Ä" als „Ä", aber das pythagoreische Alphabet hat keinen Wert für „Ä". Entweder fällt „Ä" still heraus, oder es wird implizit als „A" gewertet — beides ist eine unerkannte semantische Entscheidung.
- **Status:** **Kategorisch abgelehnt.** Verwechselt die beiden Ebenen (technisch vs. semantisch).

### Alternative 3: Umlaute als eigene Buchstaben mit eigenen Werten

- **Vorteil:** Sehr detailliert, kann某些 Traditionen abbilden.
- **Nachteil:** Es gibt keinen kanonischen pythagoreischen Wert für „Ä", „Ö", „Ü". Das würde eine eigene Fachentscheidung erfordern, die nicht traditionell abgesichert ist. Pythagoreisches Standardalphabet ist A–Z.
- **Status:** **Abgelehnt** für pythagoreische Methode. Könnte in späteren Methoden (z. B. germanische Runen-Numerologie) relevant werden.

### Alternative 4: Vollständige ASCII-Folding (z. B. `unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')`)

- **Vorteil:** Sehr einfach, eine Zeile Code.
- **Nachteil:** Verliert Kontrolle über die Transformation. ß würde zu „SS" oder zu „s" je nach Normalisierungsform. Umlaute würden zu Basizeichen ohne Dokumentation. Nicht auditierbar. Akzente würden verloren gehen ohne Trace.
- **Status:** **Abgelehnt.** Nicht deterministisch genug in der Semantik, nicht auditierbar.

### Alternative 5: Gemischte Policies je nach Buchstabe (z. B. Ä→A aber Ü→UE)

- **Vorteil:** Spezielle Fachentscheidungen möglich.
- **Nachteil:** **Harter Verstoß** gegen die Strikt-Getrennt-Regel. Erzeugt nicht-nachvollziehbare Mischformen.
- **Status:** **Kategorisch abgelehnt.**

---

## Verweise

- Master-Vertrag: `docs/governance/master-implementation-contract.md` §3.1, §6.1, §6.2
- V1 Minimal Scope: `docs/v1-minimal-scope.md` §4.1, AC-5
- Unicode TR15: https://www.unicode.org/reports/tr15/ (kanonische Normalisierungsformen)
- ADR 0001: `docs/adr/0001-y-rule-phonetic.md` (Y bleibt unberührt)
- ADR 0003: `docs/adr/0003-multiname-and-hyphens.md` (Mehrfachnamen, Leerzeichen, Bindestriche)
- Methodenspezifikation (folgt): `docs/methods/pythagorean-v1.md`
