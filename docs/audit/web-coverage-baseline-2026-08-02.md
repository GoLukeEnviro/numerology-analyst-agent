# Frontend Coverage Baseline – 2026-08-02

Gemessen mit `vitest run --coverage` (Provider: v8, `@vitest/coverage-v8@4.1.10`, Vitest `4.1.10`) im Workspace `apps/web`.

- Testlauf: 11 Test-Dateien, 43 Tests – alle grün
- Scope: `src/**/*.{ts,tsx}` (exkl. `src/api/schema.d.ts`, `src/vite-env.d.ts`, `src/test/**`, `src/**/*.test.{ts,tsx}`)

## Statements: 69.48% (428/616)
## Branches: 59.39% (237/399)
## Functions: 62% (142/229)
## Lines: 73.95% (406/549)

## Kritische ungetestete Module

| Modul | Statements | Branches | Functions | Lines | Anmerkung |
|-------|-----------:|---------:|----------:|------:|-----------|
| `src/main.tsx` | 0% | 0% | 100% | 0% | Bootstrap-Einstieg, nicht unit-getestet |
| `src/api/types.ts` | 0% | 0% | 0% | 0% | Reine Typ-Deklarationen |
| `src/features/analysis/notes-utils.ts` | 0% | 0% | 0% | 0% | Kein Test vorhanden |
| `src/features/profile/ProfileActions.tsx` | 33.33% | 30% | 13.33% | 36.36% | Export-/Lösch-Aktionen weitgehend ungetestet |
| `src/App.tsx` | 55.73% | 49.33% | 40.98% | 61.16% | Große Root-Komponente, viele Routen/Pfade ungetestet |
| `src/features/report/ReportExperience.tsx` | 58.97% | 48.71% | 44.11% | 66.66% | Fehler- und Offline-Pfade teilweise abgedeckt |
| `src/features/export/profilePdf.ts` | 56.81% | 50% | 54.54% | 58.53% | PDF-Aufbau teilweise ungetestet |
| `src/storage/database.ts` | 60% | 100% | 33.33% | 60% | IndexedDB-Schema-Migrationen ungetestet |

## Nächste Schritte

1. Thresholds in `apps/web/vite.config.ts` auf die gemessenen Werte setzen (Gate).
2. Gezielte Tests für die kritischen Module (`main.tsx`, `notes-utils.ts`, `ProfileActions.tsx`, `App.tsx`-Routen) ergänzen, um die Coverage schrittweise zu erhöhen.
