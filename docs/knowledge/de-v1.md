# Numra-Wissenspaket Deutsch V1

Das Paket `numra-knowledge-de-v1` deckt die reduzierten Werte 0–9 sowie die
Meisterzahlen 11, 22 und 33 ab. Jeder Eintrag enthält:

- ausdrücklich traditionelle Symbolik,
- konditional formulierte Reflexionsfragen,
- kleine überprüfbare Handlungsvorschläge,
- mindestens eine nicht-numerologische Gegenhypothese,
- Referenzen auf Methoden- und Governance-Quellen.

Die Texte sind keine Diagnosen, Prognosen oder empirisch bestätigten
Persönlichkeitsaussagen. Die JSON-Datei unter
`src/numerology_knowledge/data/de-v1.json` ist die maschinenlesbare Source of
Truth. Änderungen erfordern eine neue Paketversion und aktualisierte
Vertragstests.

Die regelbasierte Interpretation verändert niemals berechnete Werte. Jeder Claim
verweist getrennt auf eine Berechnungsstelle und einen Wissenseintrag und trägt
eine der Aussageklassen `traditional_claim`, `interpretive_hypothesis` oder
`practical_suggestion`.
