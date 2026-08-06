# Mobile-Strategie: 9 Ergebnisreiter

> Stand: 2026-08-05

## Entscheidung

**Scrollbare Tab-Leiste mit horizontalem Overflow und Scroll-Indikator.**

## Begründung

- **Dropdown/Accordion** versteckt wichtige Navigation und erfordert zwei Interaktionen (Öffnen + Auswählen)
- **Wrap-Layout** (Tabs in mehreren Zeilen) verschwendet vertikalen Platz auf kleinen Screens
- **Scrollbare Leiste** ist das etablierte Pattern für viele Tabs auf Mobile (z. B. YouTube, App Store, Material Design)

## Implementierung

```tsx
<div role="tablist" aria-label="Ergebnisreiter" className="tab-scroll-container">
  <div className="tab-scroll-track">
    {tabs.map(tab => (
      <button role="tab" aria-selected={active === tab.id} ...>
        {tab.label}
      </button>
    ))}
  </div>
  {/* CSS-only Scroll-Indikator: linear-gradient an den Rändern */}
</div>
```

### CSS

```css
.tab-scroll-container {
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
  -webkit-overflow-scrolling: touch;
  /* Scroll-Indikator via mask-image oder pseudo-elements */
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 5%,
    black 95%,
    transparent 100%
  );
}
.tab-scroll-container::-webkit-scrollbar {
  display: none;
}
```

### Tastatur

- Pfeiltasten navigieren zwischen Tabs (horizontal)
- Home/End springen zum ersten/letzten Tab
- Scroll-Leiste scrollt mit, damit der fokussierte Tab sichtbar ist

## Desktop

Desktop-Ansicht verwendet dieselbe Komponente, aber ohne Scroll-Verhalten — alle 9 Tabs passen in eine Zeile bei ≥ 768px Viewport.

## Deep Links

- URL-Parameter: `?tab=lebensweg`
- Bei Direktaufruf: zum richtigen Tab scrollen
- Beim Tab-Wechsel: URL aktualisieren (replaceState, kein pushState)

## Keine LLM-Aufrufe

Tab-Wechsel sind rein clientseitig. Der Bericht wird einmal geladen und alle 18 Sections sind bereits im Client. Kein Reiterwechsel löst einen API-Call aus.
