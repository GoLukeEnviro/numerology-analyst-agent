# ADR 0001: Y-Regel — phonetische Klassifikation

> **Status:** Accepted
> **Entschieden am:** 2026-07-25
> **Entscheider:** Luke
> **Beziehung:** Leitet ab aus Master-Vertrag §3.1 („Behandlung des Buchstabens Y"), §6.2 (`y-regel`). Implementiert V1 Minimal Scope §4.1, AC-4, AC-18.

---

## Kontext

Der Master-Implementierungsprompt nennt die Y-Regel als ausdrückliche Policy-Aufgabe (§3.1: „Behandlung des Buchstabens Y") und fordert sie als Pflichtfeld in der Methodenkonfiguration (§6.2: `y-regel`). Er spezifiziert jedoch **keinen Algorithmus**, wie Y im pythagoreischen System zu klassifizieren ist.

Das Problem: Der Buchstabe **Y** ist im Deutschen und Englischen phonetisch mehrdeutig. Er kann als **Vokal** oder als **Konsonant** fungieren, abhängig von Kontext und Aussprache.

### Beispiele für Y als Vokal

- „Bryan" /aɪ/ (Diphthong, Y ist vokalisch)
- „Lydia" /ɪ/ (kurzes i, Y ist vokalisch)
- „Pyramid" /ɪ/ (Y ist vokalisch)
- „Mystery" /ɪ/ ... /i/ (Y ist vokalisch)
- „Gym" /ɪ/ (Y ist vokalisch)
- „Rhythm" /ɪ/ ... /ə/ (Y ist vokalisch)
- Deutsch: „Lyrik", „System", „Symphonie", „Analyse" — Y ist vokalisch

### Beispiele für Y als Konsonant

- „Yes" /j/ (Y ist konsonantisch, englisches „j")
- „Yellow" /j/ (Y ist konsonantisch)
- „Yoga" /j/ (Y ist konsonantisch)
- „Boy" /j/ in der Aussprache mancher Sprecher (aber meist Diphthong ohne klares /j/)
- Deutsch: „Yacht", „Yeti" — Y ist konsonantisch

### Traditionelle Quellen sind uneinheitlich

Eine Stichprobe traditioneller numerologischer Quellen (z. B. affinity-numerology.com, numerology.com, tokenrock.com, verschiedenen deutschsprachigen Numerologie-Portalen) zeigt:

- Manche Quellen behandeln Y **immer** als Konsonant.
- Manche Quellen behandeln Y **immer** als Vokal.
- Manche Quellen entscheiden **kontextabhängig** nach Aussprache, aber oft ohne klaren Algorithmus.
- Manche Quellen überlassen die Entscheidung dem Numerologen (Nutzer-Eingabe).

Für V1 muss eine konkrete, deterministische, auditierbare Policy festgelegt werden, die mit dem Master-Vertrag §2.4 (Determinismus vor LLM) verträglich ist.

---

## Entscheidung

Für `pythagorean-v1` gilt `y_mode = phonetic` mit den folgenden drei Fällen:

### Fall 1 — Eindeutig vokalisch

Wenn Y in einem Namen **eindeutig vokalisch** ausgesprochen wird (Y fungiert als Vokal im Silbenkern, kein nachfolgender Vokal in derselben Silbe), wird Y als **Vokal** klassifiziert.

Beispiele: „Bryan", „Lydia", „Gym", „Mystery", „Rhythm", „Pyramid", „Lyrik", „System".

→ Y fließt in die **Seelenstrebenzahl** (Vokalsumme) ein, nicht in die Persönlichkeitszahl (Konsonantensumme).

### Fall 2 — Eindeutig konsonantisch

Wenn Y am Wort- oder Silbenanfang steht und **eindeutig konsonantisch** ausgesprochen wird (Y fungiert als /j/-Laut, gefolgt von einem Vokal), wird Y als **Konsonant** klassifiziert.

Beispiele: „Yes", „Yellow", „Yoga", „Yacht", „Yeti".

→ Y fließt in die **Persönlichkeitszahl** (Konsonantensumme) ein, nicht in die Seelenstrebenzahl.

### Fall 3 — Mehrdeutig (Unklar)

Wenn Y in einem Kontext steht, der **mehrdeutig** ist (weder eindeutig vokalisch noch eindeutig konsonantisch nach den obigen Regeln), oder wenn die Aussprache selbst mehrdeutig ist (z. B. Eigennamen mit mehreren anerkannten Aussprachen), gilt:

- **Kein Raten.**
- Zwei gültige Optionen:
  - **Option A:** Nutzerentscheidung erforderlich. Die Berechnung wird angehalten, der Nutzer wird aufgefordert, Y als Vokal oder Konsonant zu klassifizieren.
  - **Option B:** Beide Varianten werden ausgegeben. Es werden zwei vollständige Berechnungen durchgeführt (einmal Y als Vokal, einmal Y als Konsonant) und beide Ergebnisse ausgewiesen.

Welche Option in `0.1.0` Default ist, bleibt als OFFEN markiert (siehe Abschnitt „OFFEN-Punkte").

Das Ergebnis der Mehrdeutigkeit wird im Trace als `disambiguation_required: true` markiert (V1 Minimal Scope AC-18).

### Heuristik für die automatische Klassifikation (Fall 1 vs. Fall 2)

Für die meisten Fälle reicht eine einfache Heuristik, um Fall 1 vs. Fall 2 zu unterscheiden:

- **Y ist eindeutig konsonantisch (Fall 2):** Y steht am Wortanfang oder direkt nach einem Konsonanten am Silbenanfang **und** wird von einem Vokal gefolgt. Beispiel: „Yellow" — Y am Anfang, gefolgt von „e" → konsonantisch.
- **Y ist eindeutig vokalisch (Fall 1):** Y steht in der Mitte oder am Ende eines Worts und wird nicht von einem Vokal gefolgt (oder bildet selbst den Silbenkern). Beispiel: „Gym" — Y in der Mitte, gefolgt von Konsonant → vokalisch.

Diese Heuristik ist nicht perfekt — Eigennamen, Fremdwörter, Diphthonge können sie täuschen. Solche Fälle fallen in Fall 3.

### Kodierung im Domain-Modell

`y_mode` ist ein Pflichtfeld in `MethodPolicy`:

- `phonetic` (V1-Default) — die in diesem ADR spezifizierte 3-Fall-Policy
- `always_vowel` — Y wird immer als Vokal klassifiziert (konfigurierbar, aber nicht V1-Default)
- `always_consonant` — Y wird immer als Konsonant klassifiziert (konfigurierbar, aber nicht V1-Default)
- `user_fixed` — Y-Klassifikation wird vorab vom Nutzer pro Vorkommen festgelegt (konfigurierbar, aber nicht V1-Default)

Für `0.1.0` ist `y_mode = phonetic` der dokumentierte kanonische Default.

---

## Konsequenzen

### Positiv

- **Deterministisch für die klaren Fälle (1 und 2):** Gleicher Input → gleiche Y-Klassifikation → gleiche Zahl. Kein Raten.
- **Mehrdeutige Fälle werden transparent markiert:** Weder still geraten noch verheimlicht. Trace dokumentiert `disambiguation_required: true`.
- **Auditierbar:** Jede Y-Entscheidung ist im Trace nachvollziehbar (welcher Fall, welche Heuristik, welche Entscheidung).
- **Mit Master-Vertrag §2.4 verträglich:** Klassifikation erfolgt deterministisch ohne LLM. Heuristik ist regelbasiert.
- **Erweiterbar:** Spätere Releases können eine phonetische Bibliothek (z. B. IPA-basiert) für feinkörnigere Klassifikation nutzen, ohne die Policy-Struktur zu verändern.
- **Optionen für Mehrdeutigkeit:** Weder Nutzer-Entscheidung noch Mehrfachausgabe wird erzwungen — beide bleiben gültige Wege, je nach UX-Präferenz.

### Negativ

- **Heuristik nicht perfekt:** Einige Eigennamen und Diphthong-Fälle werden fehlerhaft oder mehrdeutig klassifiziert. Das ist akzeptiert, weil die Mehrdeutigkeit explizit markiert wird.
- **Option A vs. Option B muss noch entschieden werden:** Ob Mehrdeutigkeit in `0.1.0` Default Nutzer-Entscheidung oder Mehrfachausgabe ist, bleibt OFFEN (siehe unten).
- **Phonetische Bibliothek nicht in `0.1.0`:** Eine IPA-basierte Klassifikation wäre robuster, erfordert aber eine Abhängigkeit (z. B. `epitran`, `g2p-en`) und ist nicht determinismus-kritisch genug, um in `0.1.0` zu rechtfertigen.
- **Sprachliche Variation:** Ein Name wie „Bryan" kann je nach Sprecher variieren. Die Heuristik geht von einer kanonischen Aussprache aus.

### Auswirkungen auf Kernzahlen

Y-Klassifikation beeinflusst direkt:

- **Seelenstrebenzahl** (Vokalsumme): Wenn Y vokalisch, geht es hier ein.
- **Persönlichkeitszahl** (Konsonantensumme): Wenn Y konsonantisch, geht es hier ein.
- **Ausdrucks-/Schicksalszahl** (Summe aller Buchstaben): **Unabhängig** von Y-Klassifikation — alle Buchstaben fließen ein, unabhängig von vokalisch/konsonantisch.

→ Die Konsistenzprüfung „Ausdrucks-Rohsumme = Vokalsumme + Konsonantensumme" (Master-Vertrag Phase 4) bleibt gültig, egal wie Y klassifiziert wird.

---

## Alternativen betrachtet

### Alternative 1: Y immer als Vokal (`y_mode = always_vowel`)

- **Vorteil:** Maximale Determinismus, kein Mehrdeutigkeits-Fall. Sehr einfach zu implementieren.
- **Nachteil:** **Fachlich falsch** für viele Namen („Yoga", „Yellow", „Yacht"). Würde Seelenstrebenzahl und Persönlichkeitszahl systematisch verfälschen.
- **Status:** **Abgelehnt als V1-Default.** Als konfigurierbare Option in `MethodPolicy` verfügbar.

### Alternative 2: Y immer als Konsonant (`y_mode = always_consonant`)

- **Vorteil:** Maximale Determinismus, kein Mehrdeutigkeits-Fall. Sehr einfach zu implementieren.
- **Nachteil:** **Fachlich falsch** für viele Namen („Bryan", „Lydia", „Gym", „System"). Würde Seelenstrebenzahl und Persönlichkeitszahl systematisch verfälschen.
- **Status:** **Abgelehnt als V1-Default.** Als konfigurierbare Option in `MethodPolicy` verfügbar.

### Alternative 3: Y vom Nutzer vorab festlegen (`y_mode = user_fixed`)

- **Vorteil:** Keine Mehrdeutigkeit zur Laufzeit. Nutzer hat volle Kontrolle.
- **Nachteil:** Verschiebt eine fachliche Entscheidung auf den Nutzer, der sie oft nicht treffen kann („Wie spreche ich meinen Namen numerologisch korrekt aus?"). UX-lastig, fehleranfällig.
- **Status:** **Abgelehnt als V1-Default.** Als konfigurierbare Option verfügbar; kann auch als Input zu Option A in Fall 3 dienen.

### Alternative 4: LLM-basierte phonetische Klassifikation

- **Vorteil:** Potenziell feinkörnigste Klassifikation, kann mit Kontext umgehen.
- **Nachteil:** **Harter Verstoß** gegen Master-Vertrag §2.4 (Determinismus vor LLM) und Copilot-Instructions („Kein LLM-Aufruf im Rechenkern"). Nicht deterministisch, nicht reproduzierbar, erfordert Netzwerkzugriff.
- **Status:** **Kategorisch abgelehnt.**

### Alternative 5: IPA-basierte phonetische Bibliothek

- **Vorteil:** Deterministisch, robust, fachlich fundiert.
- **Nachteil:** Zusätzliche Abhängigkeit (z. B. `epitran`, `g2p-en`, oder ein Wörterbuch). Erschwert Reproduzierbarkeit, erweitert die Angriffsfläche. Übertrieben für `0.1.0`.
- **Status:** **Aufgeschoben** für ein späteres Release (z. B. `0.3.0` oder `0.4.0`). Die Heuristik in `0.1.0` ist pragmatisch und deterministisch.

---

## OFFEN-Punkte (für Luke zu klären)

- **OFFEN-1:** Bei Y-Mehrdeutigkeit (Fall 3) — Default in `0.1.0` ist **Option A (Nutzerentscheidung)** oder **Option B (Mehrfachausgabe)**? Empfehlung des Autors: Option B (Mehrfachausgabe) als `0.1.0`-Default, weil sie kein UX-Blocker ist und beide fachlich gültigen Ergebnisse zeigt. Luke muss final entscheiden.
- **OFFEN-2:** Wie wird „Y am Wortende" behandelt, wenn es auf einen Konsonanten folgt (z. B. „Python"? —— nein, da ist Y am Anfang und konsonantisch; eher „Rhythm" — Y vokalisch). Klärung der Heuristik-Feinheiten.
- **OFFEN-3:** Diphthong-Behandlung (z. B. „Bay", „Day"). Y ist am Ende, aber als Teil eines Diphthongs. Ist Y vokalisch (Teil des Diphthongs) oder konsonantisch? Empfehlung: vokalisch.
- **OFFEN-4:** Fremdsprachige Namen (z. B. spanisch „Yves" vs. englisch „Yves"). Welche Aussprache gilt? Empfehlung: kanonische Aussprache der Sprache des Namens (Locale).

---

## Verweise

- Master-Vertrag: `docs/governance/master-implementation-contract.md` §3.1, §6.2
- V1 Minimal Scope: `docs/v1-minimal-scope.md` §4.1, AC-4, AC-18
- ADR 0002: `docs/adr/0002-unicode-umlaut-normalization-de-direct-v1.md` (Umlaute, Akzente — separate Policy)
- ADR 0003: `docs/adr/0003-multiname-and-hyphens.md` (Mehrfachnamen, Bindestriche)
- Methodenspezifikation (folgt): `docs/methods/pythagorean-v1.md`
- Traditioneller Vergleich: affinity-numerology.com, numerology.com (Behandlung von Y)
