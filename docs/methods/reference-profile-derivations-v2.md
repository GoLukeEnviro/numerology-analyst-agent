# Reference Profile Derivations V2

> Methode: `pythagorean-v2` · Umlaut-Policy: `de-expanded-v1` · PR #19
> Stand: 2026-07-28 · Alle Werte manuell verifiziert

Diese Datei dokumentiert die vollständige Herleitung aller fünf Referenzprofile
für den pythagoreischen V2-Berechnungsvertrag.  Sie ist die primäre Wahrheitsquelle
für die golden cases in `tests/golden/reference_profiles_v2.yaml`.

---

## V2 Methodenübersicht

### Lebensweg

| Rolle | Methode | Beschreibung |
|-------|---------|--------------|
| **primär** | `sum_all_birth_date_digits` | Alle 8 Ziffern YYYYMMDD summieren, dann reduzieren |
| **sekundär** | `component_then_sum` | Monat, Tag, Jahr getrennt reduzieren, Summe bilden |

Die sekundäre Methode **überschreibt niemals** den primären Wert.

### Personal-Jahr-Formel (V2-Korrektur)

```
PY = reduce(birth_month) + reduce(birth_day) + reduce(digit_sum(calendar_year))
```

Universaljahr = digit_sum des aktuellen Jahres, dann reduzieren (11/22/33 erhalten).

### Pinnacles / Challenges: Root-Werte

Meisterzahlen in den Geburtskomponenten werden für Pinnacles und Challenges
auf ihren Grundwert reduziert (z.B. Tag=11 → root=2).

```
m = root(birth_month)   d = root(birth_day)   y = root(digit_sum(birth_year))
P1=m+d  P2=d+y  P3=P1.root+P2.root  P4=m+y
C1=|d-m|  C2=|d-y|  C3=|C1.root-C2.root|  C4=|m-y|
```

### Karmische Herkunftstypen

| Typ | Bedeutung |
|-----|-----------|
| `direct_raw` | Der Raw-Total selbst ist eine karmische Schuldzahl (13/14/16/19) |
| `reduction_intermediate` | Eine Zwischenzahl in der Reduktionskette ist karmisch |
| `component_total` | Die Summe reduzierter Komponenten (Lebensweg B) ist karmisch |

### 44 ist keine klassische Meisterzahl

44 erscheint häufig (z.B. Persönlichkeit Lukas = 44/8), aber `is_master=False`.
Nur 11, 22, 33 sind klassische Meisterzahlen.

---

## 1. Lukas Springer — 18.07.1986

### Lebensweg

**Primär (sum_all_birth_date_digits):**
```
Datum: 18.07.1986 → 1+9+8+6+0+7+1+8 = 40 → 40/4
```

**Sekundär (component_then_sum):**
```
Monat=7(→7)  Tag=18(→9)  Jahr=1986→24(→6)
7 + 9 + 6 = 22 → 22/4  [Meisterzahl! held_master=22, root=4]
```

### Geburtstag & Einstellungszahl
- Geburtstag: 18 → 18/9
- Einstellungszahl: 7+18=25 → 25/7

### Namensberechnung (LUKAS SPRINGER, de-expanded-v1 unverändert)

```
L=3  U=3  K=2  A=1  S=1  |  S=1  P=7  R=9  I=9  N=5  G=7  E=5  R=9
LUKAS  = 10 → 10/1
SPRINGER = 52 → 52/7
Ausdruck = 62 → 62/8
```

Vokale: U(3)+A(1)+I(9)+E(5) = 18 → **18/9**
Konsonanten: L(3)+K(2)+S(1)+S(1)+P(7)+R(9)+N(5)+G(7)+R(9) = **44/8** (kein Meister!)
Reifezahl: lw.root(4) + expr.root(8) = 12 → **12/3**

### Persönliches Jahr 2026
```
reduce(7) + reduce(18) + reduce(digit_sum(2026)=10→1) = 7+9+1 = 17 → 17/8
```

### Pinnacles & Challenges
```
Roots: m=7  d=9  y=6
P1=16/7  P2=15/6  P3=13/4  P4=13/4
C1=|9-7|=2  C2=|9-6|=3  C3=|2-3|=1  C4=|7-6|=1
```

---

## 2. Stella Jane Witt — 18.04.2011

### Lebensweg
```
A: 2+0+1+1+0+4+1+8 = 17 → 17/8  (primär)
B: month=4  day=9  year=reduce(4)=4  sum=17 → 17/8  (beide stimmen überein)
```

### Geburtstag & Einstellungszahl
- Geburtstag: 18 → 18/9
- Einstellungszahl: 4+18=22 → **22/4** [Meisterzahl!]

### Namensberechnung (STELLA JANE WITT)
```
STELLA: S(1)+T(2)+E(5)+L(3)+L(3)+A(1) = 15
JANE:   J(1)+A(1)+N(5)+E(5) = 12
WITT:   W(5)+I(9)+T(2)+T(2) = 18
Ausdruck = 45 → 45/9
```

Vokale: E(5)+A(1) + A(1)+E(5) + I(9) = 21 → **21/3**
Konsonanten: S(1)+T(2)+L(3)+L(3) + J(1)+N(5) + W(5)+T(2)+T(2) = 24 → **24/6**
Reifezahl: 8+9=17 → **17/8**

### Persönliches Jahr 2026
```
reduce(4) + reduce(18) + reduce(10) = 4+9+1 = 14 → 14/5
```

---

## 3. Antoney Newton — 15.10.1995 · Y=Vokal (Referenzfall)

### Lebensweg
```
A: 1+9+9+5+1+0+1+5 = 31 → 31/4  (primär)
B: month=reduce(10)=1  day=reduce(15)=6  year=reduce(24)=6
   sum=1+6+6=13 → 13/4  [13=karmisch! origin_type=component_total]
```

### Geburtstag & Einstellungszahl
- Geburtstag: 15 → 15/6
- Einstellungszahl: 10+15=25 → 25/7

### Y-Klassifikation

Y im Namen "ANTONEY" (Position 6 in ANTONEYNEWTON):
- previous = E (Vokal), following = N (Konsonant)
- Phonetische Regel: `index>0 AND following NOT in VOWELS` → **vowel** (decision_source=phonetic_rule)

### Namensberechnung (ANTONEY NEWTON, Y=Vokal)
```
ANTONEY: A(1)+N(5)+T(2)+O(6)+N(5)+E(5)+Y(7) = 31
NEWTON:  N(5)+E(5)+W(5)+T(2)+O(6)+N(5) = 28
Ausdruck = 59 → 14 → 5  → 59/14/5  [14=karmisch! origin_type=reduction_intermediate]
```

Vokale (Y=Vokal):
- ANTONEY: A(1)+O(6)+E(5)+Y(7) = 19
- NEWTON:  E(5)+O(6) = 11 [Meisterzahl! gehalten]
- Gesamt: 19+11=30 → **30/3**

Konsonanten (Y als Vokal gezählt):
- ANTONEY: N(5)+T(2)+N(5) = 12
- NEWTON:  N(5)+W(5)+T(2)+N(5) = 17
- Gesamt: 29 → 11 → 2 → **29/11/2** [Meisterzahl!]

Reifezahl: lw.root(4) + expr.root(5) = **9**

### Persönliches Jahr 2026
```
reduce(10)=1 + reduce(15)=6 + reduce(10)=1 = 8
```

---

## 4. Sina Langner — 11.12.1992

### Lebensweg
```
A: 1+9+9+2+1+2+1+1 = 26 → 26/8  (primär)
B: month=reduce(12)=3  day=reduce(11)=11(Meister!)  year=reduce(21)=3
   sum=3+11+3=17 → 17/8
```

### Geburtstag & Einstellungszahl
- Geburtstag: 11 → **11/2** [Meisterzahl!]
- Einstellungszahl: 12+11=23 → 23/5

> Hinweis: Bei Pinnacles/Challenges wird Tag-root=2 verwendet (Meister auf Root reduziert).

### Namensberechnung (SINA LANGNER)
```
SINA:    S(1)+I(9)+N(5)+A(1) = 16
LANGNER: L(3)+A(1)+N(5)+G(7)+N(5)+E(5)+R(9) = 35
Ausdruck = 51 → 51/6
```

Vokale: I(9)+A(1) + A(1)+E(5) = 16 → **16/7**
Konsonanten: S(1)+N(5) + L(3)+N(5)+G(7)+N(5)+R(9) = 35 → **35/8**
Reifezahl: 8+6=14 → **14/5**

### Persönliches Jahr 2026
```
reduce(12)=3 + reduce(11)=11 + reduce(10)=1 = 15 → 15/6
```
(Persönliches Jahr hält Meisterzahlen aus dem Geburtstag)

---

## 5. Stefanie Scheulen — 16.04.1981

### Lebensweg
```
A: 1+9+8+1+0+4+1+6 = 30 → 30/3  (primär)
B: month=4  day=reduce(16)=7  year=reduce(19→10→1)=1  sum=12 → 12/3
```

### Geburtstag & Einstellungszahl
- Geburtstag: 16 → **16/7** [16=karmisch! origin_type=direct_raw]
- Einstellungszahl: 4+16=20 → 20/2

### Namensberechnung (STEFANIE SCHEULEN, de-expanded-v1)

Kein Umlaut im Namen → de-expanded-v1 = de-direct-v1 für dieses Profil.

```
STEFANIE: S(1)+T(2)+E(5)+F(6)+A(1)+N(5)+I(9)+E(5) = 34
SCHEULEN: S(1)+C(3)+H(8)+E(5)+U(3)+L(3)+E(5)+N(5) = 33
Ausdruck = 67 → 13 → 4  → 67/13/4  [13=karmisch! origin_type=reduction_intermediate]
```

Vokale:
- STEFANIE: E(5)+A(1)+I(9)+E(5) = 20
- SCHEULEN: E(5)+U(3)+E(5) = 13
- Gesamt: 33 → **33/6** [Meisterzahl!]

Konsonanten:
- STEFANIE: S(1)+T(2)+F(6)+N(5) = 14
- SCHEULEN: S(1)+C(3)+H(8)+L(3)+N(5) = 20
- Gesamt: 34 → **34/7**

Reifezahl: lw.root(3) + expr.root(4) = **7**

### Persönliches Jahr 2026
```
reduce(4)=4 + reduce(16)=7 + reduce(10)=1 = 12 → 12/3
```

---

## Umlaut-Policy: de-expanded-v1

| Zeichen | de-direct-v1 | de-expanded-v1 |
|---------|--------------|----------------|
| Ä, ä    | A            | AE             |
| Ö, ö    | O            | OE             |
| Ü, ü    | U            | UE             |
| ß       | SS           | SS             |

**Beispiel:** "Müller" → de-direct-v1: MULLER · de-expanded-v1: MUELLER

Die beiden Policies dürfen innerhalb einer Berechnung NICHT gemischt werden (ADR 0002 §7).
