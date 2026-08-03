# RemixIcon-Integration in apps/web

## Kontext

`apps/web` (React/Vite/TypeScript-PWA, Paketname `@numra/web`) hat aktuell
**keine** Icon-Library (kein `lucide-react`, `react-icons`, `heroicons` o.ä.)
und **keine** Icon-Nutzung im Code — reine Text-Buttons. Der User möchte
RemixIcon als Icon-Bibliothek einführen, um zukünftig Icons in der UI
verwenden zu können. Es handelt sich um ein greenfield-Setup ohne
Migrationsaufwand.

## Entscheidung: `@remixicon/react` statt Webfont-Paket (`remixicon`)

Begründung, spezifisch für dieses Repo:

- **PWA/Workbox** (`apps/web/vite.config.ts` hat `runtimeCaching: []` und
  keine eigenen `globPatterns`): Ohne eigene `globPatterns` precached Workbox
  standardmäßig das Glob `**/*.{js,wasm,css,html}` — Font-Dateien
  (`.woff2`/`.ttf`) des Webfont-Pakets werden dadurch **nicht** in den
  Precache aufgenommen, die
  zugehörige monolithische CSS-Datei aber schon. Das eigentliche Risiko wäre
  ein Offline-Zustand, in dem die CSS-Regeln geladen sind, die referenzierten
  Fonts aber fehlen und Icons nicht rendern. `@remixicon/react` vermeidet
  dieses Problem, da es reine SVG-basierte React-Komponenten (normales JS)
  liefert — keine Vite/PWA-Konfigänderung nötig.
- **Strict TypeScript** (`tsc -b`, kein `any`): `@remixicon/react` hat volle
  `.d.ts`-Typen pro Icon-Komponente. Das Webfont-Paket arbeitet mit
  String-Klassennamen (`className="ri-home-line"`) ohne Typsicherheit.
- **Tree-Shaking/Bundle-Size**: Der Named-ESM-Import ermöglicht Rollup
  grundsätzlich, ungenutzte Icon-Exports zu eliminieren — das ist aber eine
  zu verifizierende Build-Eigenschaft, keine allein aus der Importsyntax
  bewiesene Tatsache. Wird im Verifikationsschritt per Bundle-Größenvergleich
  geprüft. Die Webfont-CSS enthält dagegen immer alle ~3100 Icons ungekürzt.
- **Kein FOUC**: kein `@font-face`-Swap-Flash.
- **Lizenz**: Die Remix Icon License v1.0 (Stand 2026) erlaubt die Nutzung
  als funktionales UI-Element in Web-Apps ausdrücklich. Untersagt sind unter
  anderem die Weiterverteilung als eigenständige oder konkurrierende
  Icon-Bibliothek sowie die Nutzung als eigenes Logo, Markenzeichen oder
  primäre Markenidentität — der geplante PDF-Button ist unproblematisch.

## Umsetzung (minimal touch)

1. **Installation** (vom Repo-Root, pnpm-Workspace-Filter, exakte Version
   gepinnt — konsistent mit den übrigen exakt gepinnten Dependencies in
   `apps/web/package.json`):
   ```
   pnpm add --filter @numra/web -E @remixicon/react@4.9.0
   ```
   Fügt genau eine neue Runtime-Dependency zu `apps/web/package.json`
   `dependencies` hinzu (neben `dexie`, `pdfmake`, …) und aktualisiert
   `pnpm-lock.yaml`. Keine CSS-Importe, keine `vite.config.ts`-Änderung.

2. **Kein Wrapper-Modul.** Passend zur bestehenden flachen
   Vertical-Slice-Struktur (`apps/web/src/features/{profile,analysis,report,export}/`
   ohne gemeinsamen `components/ui`-Ordner) werden Icon-Komponenten direkt
   importiert:
   ```ts
   import { RiFilePdf2Line } from "@remixicon/react";
   ```
   Kein `src/components/icons.ts`-Barrel jetzt anlegen — dafür gibt es aktuell
   keinen Bedarf (z. B. erzwungene Default-Größe/-Farbe). Erst beim zweiten/
   dritten Verwendungsfall mit echtem Konsistenzbedarf einen dünnen Wrapper
   (`src/components/Icon.tsx`) einführen.

3. **Kein Workbox-Config-Change nötig** — bestätigt durch Review von
   `apps/web/vite.config.ts` und `apps/web/src/main.tsx` (einzige globale
   CSS-Importe: `./styles.css`, kein Font-Import).

4. **Konkretes Beispiel zum Nachweis der Integration** —
   [ProfileActions.tsx](apps/web/src/features/profile/ProfileActions.tsx):
   - Import ergänzen: `import { RiFilePdf2Line } from "@remixicon/react";`
   - Im "PDF exportieren"-Button (Zeile 79-81) das Icon vor dem Label
     einfügen:
     ```tsx
     <button className="button button-primary" type="button" disabled={exporting} onClick={exportPdf}>
       <RiFilePdf2Line size={18} aria-hidden="true" />
       {exporting ? "PDF wird erstellt …" : "PDF exportieren"}
     </button>
     ```
   - Selbstständiger, risikoarmer Touch an einer bereits flachen Feature-Datei
     — validiert Importauflösung, TypeScript-Kompatibilität, JSX-Kompilierung
     und Production-Build. Die sichtbare Darstellung wird in der manuellen
     Browserprüfung bestätigt; die Tree-Shaking-/Bundle-Auswirkung wird
     separat anhand des Production-Builds geprüft (siehe Verifikation).
   - Accessible Name: im Idle-Zustand bleibt er "PDF exportieren", während
     des bestehenden Exportzustands weiterhin "PDF wird erstellt …" — das
     dekorative Icon beeinflusst ihn wegen `aria-hidden="true"` nicht.

## Betroffene Dateien

- `apps/web/package.json` — neue Dependency `@remixicon/react@4.9.0` (exakt gepinnt)
- `pnpm-lock.yaml` — Lockfile-Update
- `apps/web/src/features/profile/ProfileActions.tsx` — Icon im PDF-Export-Button

Keine Änderungen an: `apps/web/vite.config.ts`, `apps/web/src/main.tsx`,
`apps/web/src/styles.css` (nur zur Verifikation gelesen, kein Anpassungsbedarf).

## Verifikation

Chronologische Reihenfolge (verbindlich — die Baseline-Erfassung muss vor
jeder Mutation stehen, sonst ist der Vorher-/Nachher-Vergleich ungültig):

### 0. Baseline vor jeder Mutation (auf sauberem Checkout, vor Installation)

```bash
rm -rf apps/web/dist && pnpm --filter @numra/web build
find apps/web/dist/assets -maxdepth 1 -type f -name '*.js' -printf '%s\t%f\n' \
  | sort -n > /tmp/numra-assets-before.tsv
```

### 1. Installation und Codeänderung

```bash
pnpm add --filter @numra/web -E @remixicon/react@4.9.0
```

Danach die Codeänderung aus Schritt 4 der Umsetzung (`ProfileActions.tsx`).

### 2. Statische und funktionale Gates (Reihenfolge relevant)

`check:build` (`scripts/check-build.mjs`) liest zwingend
`coverage/coverage-summary.json` — diese Datei entsteht nur durch
`pnpm coverage` (`vitest run --coverage`), nicht durch `pnpm test`. Deshalb
muss `coverage` vor `build`/`check:build` laufen:

```bash
pnpm --filter @numra/web typecheck
pnpm --filter @numra/web lint
pnpm --filter @numra/web coverage    # erzeugt coverage-summary.json, führt Tests inkl. aus
pnpm --filter @numra/web build
pnpm --filter @numra/web check:build # scripts/check-build.mjs — prüft u.a. gzip-Budget 160 KiB fürs initiale JS-Bundle
```

### 3. Bundle-/PWA-Nachweis als echtes Fail-Gate (kein reines `find`-Listing)

```bash
unexpected_fonts="$(
  find apps/web/dist -type f \
    \( \
      -name '*.woff' -o \
      -name '*.woff2' -o \
      -name '*.ttf' -o \
      -name '*.otf' -o \
      -name '*.eot' \
    \) \
    -print
)"
if [ -n "$unexpected_fonts" ]; then
  printf 'Unerwartete Font-Assets gefunden:\n%s\n' "$unexpected_fonts" >&2
  exit 1
fi
```

### 4. Nachher-Messung und Vorher-/Nachher-Bundle-**Inspektion**

Diagnose, kein hartes Gate — Vite vergibt Content-Hashes in Dateinamen,
daher ist ein Datei-Diff nur orientierend; der eigentliche harte
Bundle-Guard ist `check:build` mit dem gzip-Budget von 160 KiB fürs
initiale JS-Bundle. Der `build`-Schritt aus Abschnitt 2 hat `dist` bereits
neu erzeugt:

```bash
find apps/web/dist/assets -maxdepth 1 -type f -name '*.js' -printf '%s\t%f\n' \
  | sort -n > /tmp/numra-assets-after.tsv

# diff liefert Exit-Code 1 bei erwarteten Unterschieden (kein Fehler),
# nur Exit-Code >1 ist ein echter Ausführungsfehler
diff_status=0
diff -u /tmp/numra-assets-before.tsv /tmp/numra-assets-after.tsv \
  > /tmp/numra-assets.diff || diff_status=$?
if [ "$diff_status" -gt 1 ]; then
  echo "Bundle-Diff konnte nicht erstellt werden." >&2
  exit "$diff_status"
fi
cat /tmp/numra-assets.diff
```

### 5. Produktionsnahe Browserprüfung (da `pnpm dev` den Service Worker mangels
`devOptions.enabled` in `vite.config.ts` nicht aktiviert; alten Service
Worker/Cache vorher entfernen, um verfälschte Ergebnisse zu vermeiden):

```bash
pnpm --filter @numra/web preview
```

In DevTools > Application > Storage: "Clear site data" ausführen (oder
sauberes Browserprofil verwenden), Seite einmal online laden und auf
Service-Worker-Aktivierung warten, neu laden, Offline-Modus aktivieren und
erneut laden.

Erwartung:
- keine unerwarteten Font-Assets im Build (Fail-Gate oben grün),
- `check:build` bleibt innerhalb des bestehenden gzip-Budgets von 160 KiB
  fürs initiale JS-Bundle; die Vorher-/Nachher-Inspektion zeigt keine
  unverhältnismäßige zusätzliche JS-Datei,
- im Idle-Zustand bleibt der Accessible Name "PDF exportieren", während des
  Exports weiterhin "PDF wird erstellt …" — das dekorative Icon beeinflusst
  ihn wegen `aria-hidden="true"` nicht,
- im Preview (nach Cache-Clear): Icon sichtbar, Service Worker aktiviert,
  Offline-Reload funktioniert unverändert.
