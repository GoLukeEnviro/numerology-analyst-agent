# ADR 0011: PWA-Cache, Theme-Start und PDF-Export

- Status: akzeptiert
- Datum: 2026-07-26

## Kontext

Numra muss installierbar sein und lokal gespeicherte Profile auch nach einem
Offline-Neustart anzeigen. Gleichzeitig enthalten Berechnungs- und
Analyseantworten personenbezogene beziehungsweise aus personenbezogenen Daten
abgeleitete Inhalte. Diese Antworten dürfen nicht versehentlich in einem
gemeinsam verwalteten HTTP-Cache landen. Der PDF-Export soll vollständig lokal
arbeiten und die initiale Anwendung nicht unnötig vergrößern.

## Entscheidung

1. Workbox precached ausschließlich versionierte App-Assets. API-Routen,
   API-POSTs und deren Antworten werden weder durch Runtime-Caching noch durch
   Precache-Regeln gespeichert.
2. Dauerhafte Profildaten, Berichte, Rückfragen und Notizen liegen nur in der
   explizit gewählten, optional verschlüsselten IndexedDB-Ablage.
3. Der PDF-Generator wird erst bei einem Export dynamisch geladen. Sein großes
   JavaScript-Bundle ist aus dem Service-Worker-Precache ausgeschlossen.
4. Der PDF-Export läuft vollständig im Browser und überträgt keine Inhalte.
   Das Dokument enthält Aussagegrenzen, Rechenweg, Berechnungshash und – falls
   vorhanden – die Provenienz des Berichts.
5. Das gewählte Dark- oder Light-Theme wird durch ein kleines, statisches
   Skript vor React angewendet. So entsteht beim Start kein sichtbarer
   Farbwechsel; die Anwendung bleibt auch ohne JavaScript lesbar.
6. PWA-Updates werden nicht ungefragt aktiviert. Die Oberfläche informiert über
   eine wartende Version und lässt den Nutzer den Neustart bewusst auslösen.
7. Installationshinweise unterscheiden Desktop/Android und iOS, weil iOS keine
   standardisierte Browser-Installationsaufforderung bereitstellt.

## Folgen

- Ein kompromittierter oder gemeinsam genutzter HTTP-Cache enthält keine
  Profilantworten.
- Offline verfügbar sind die App-Shell und lokal gespeicherte Inhalte; neue
  Berechnungen, Berichte und Rückfragen erklären verständlich, dass eine
  Internetverbindung erforderlich ist.
- Der initiale JavaScript-Download bleibt innerhalb des festgelegten Budgets.
- Änderungen an Cache-Regeln, PDF-Lazy-Loading oder Updateverhalten werden in
  CI durch Build- und Browserprüfungen abgesichert.
