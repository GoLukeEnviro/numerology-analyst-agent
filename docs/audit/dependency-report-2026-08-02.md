# Dependency Report – 2026-08-02

## Messkontext

| Feld | Wert |
|------|------|
| **Mess-SHA (origin/main zum Zeitpunkt)** | `21ba56ed0d918cea7c60090bcc50937adc16269a` |
| **Datum** | 2026-08-02 |
| **Ausgeführt** | `pip-audit` (Python), `pnpm audit` (Node), `pnpm outdated` (Node) |
| **Nicht ausgeführt** | `npm audit` außerhalb des pnpm-Workspace, SBOM-Generierung, License-Scan, Dependabot-Diff |
| **Hinweis** | „outdated“ bedeutet **nicht** automatisch „vulnerable“. Dieses Dokument mischt beide Dimensionen nicht. Upgrade-Empfehlungen unten sind **nicht** ungeprüft freigegeben — sie markieren nur bekannte Patch-Pfade. |

## Python-Pakete (via uv + pip-audit)

Quelle: `uv.lock` und `pip-audit` (Scan vom 2026-08-02 auf dem Mess-SHA oben).

| Paket | Version | CVE-Status | Entscheidung |
|-------|---------|------------|-------------|
| annotated-doc | 0.0.4 | Keine | jetzt ok |
| annotated-types | 0.8.0 | Keine | jetzt ok |
| anyio | 4.14.2 | Keine | jetzt ok |
| boolean-py | 5.0 | Keine | jetzt ok |
| cachecontrol | 0.14.4 | Keine | jetzt ok |
| certifi | 2026.7.22 | Keine | jetzt ok |
| charset-normalizer | 3.4.9 | Keine | jetzt ok |
| click | 8.4.2 | Keine | jetzt ok |
| colorama | 0.4.6 | Keine | jetzt ok |
| coverage | 7.15.2 | Keine | jetzt ok |
| cyclonedx-python-lib | 11.11.0 | Keine | jetzt ok |
| defusedxml | 0.7.1 | Keine | jetzt ok |
| fastapi | 0.140.0 | Keine | jetzt ok |
| filelock | 3.32.0 | Keine | jetzt ok |
| h11 | 0.16.0 | Keine | jetzt ok |
| httpcore | 1.0.9 | Keine | jetzt ok |
| httptools | 0.8.0 | Keine | jetzt ok |
| httpx | 0.28.1 | Keine | jetzt ok |
| hypothesis | 6.161.5 | Keine | jetzt ok |
| idna | 3.18 | Keine | jetzt ok |
| iniconfig | 2.3.0 | Keine | jetzt ok |
| librt | 0.13.0 | Keine | jetzt ok |
| license-expression | 30.4.4 | Keine | jetzt ok |
| markdown-it-py | 4.2.0 | Keine | jetzt ok |
| mdurl | 0.1.2 | Keine | jetzt ok |
| msgpack | 1.2.1 | Keine | jetzt ok |
| mypy | 1.20.2 | Keine | jetzt ok |
| mypy-extensions | 1.1.0 | Keine | jetzt ok |
| packageurl-python | 0.17.6 | Keine | jetzt ok |
| packaging | 26.2 | Keine | jetzt ok |
| pathspec | 1.1.1 | Keine | jetzt ok |
| pip | 26.1.2 | Keine | jetzt ok |
| pip-api | 0.0.34 | Keine | jetzt ok |
| pip-audit | 2.10.1 | Keine | jetzt ok |
| pip-requirements-parser | 32.0.1 | Keine | jetzt ok |
| platformdirs | 4.11.0 | Keine | jetzt ok |
| pluggy | 1.6.0 | Keine | jetzt ok |
| py-serializable | 2.1.0 | Keine | jetzt ok |
| pydantic | 2.13.4 | Keine | jetzt ok |
| pydantic-core | 2.46.4 | Keine | jetzt ok |
| pygments | 2.20.0 | Keine | jetzt ok |
| pyparsing | 3.3.2 | Keine | jetzt ok |
| pytest | 9.1.1 | Keine | jetzt ok |
| pytest-cov | 6.3.0 | Keine | jetzt ok |
| python-dotenv | 1.2.2 | Keine | jetzt ok |
| pyyaml | 6.0.3 | Keine | jetzt ok |
| redis | 7.4.1 | Keine | jetzt ok |
| requests | 2.34.2 | Keine | jetzt ok |
| rich | 15.0.0 | Keine | jetzt ok |
| ruff | 0.12.12 | Keine | jetzt ok |
| shellingham | 1.5.4 | Keine | jetzt ok |
| sortedcontainers | 2.4.0 | Keine | jetzt ok |
| starlette | 1.3.1 | Keine | jetzt ok |
| tomli | 2.4.1 | Keine | jetzt ok |
| tomli-w | 1.2.0 | Keine | jetzt ok |
| typer | 0.27.0 | Keine | jetzt ok |
| types-pyyaml | 6.0.12.20260724 | Keine | jetzt ok |
| typing-extensions | 4.16.0 | Keine | jetzt ok |
| typing-inspection | 0.4.2 | Keine | jetzt ok |
| urllib3 | 2.7.0 | Keine | jetzt ok |
| uvicorn | 0.51.0 | Keine | jetzt ok |
| watchfiles | 1.2.0 | Keine | jetzt ok |
| websockets | 16.1.1 | Keine | jetzt ok |

**Gesamt: 64 Python-Pakete, 0 CVEs (pip-audit: "No known vulnerabilities found")**

---

## Node-Pakete (via pnpm)

Quelle: `pnpm-lock.yaml`, `pnpm audit`, `pnpm outdated`.

### Prod-Dependencies (@numra/web)

| Paket | Version | CVE-Status | Entscheidung |
|-------|---------|------------|-------------|
| dexie | 4.4.4 | Keine | jetzt ok |
| pdfmake | 0.3.11 | Keine | jetzt ok |
| react | 19.2.8 | Keine | jetzt ok |
| react-dom | 19.2.8 | Keine | jetzt ok |
| react-hook-form | 7.83.0 | Keine | jetzt ok |
| react-router-dom | 7.18.1 | **GHSA-qwww-vcr4-c8h2 (HIGH)** | später – Patch auf >=8.3.0 erforderlich |
| workbox-window | 7.4.1 | Keine | jetzt ok |
| zod | 4.4.3 | Keine | jetzt ok |

### Dev-Dependencies (@numra/web)

| Paket | Version | CVE-Status | Entscheidung |
|-------|---------|------------|-------------|
| @axe-core/playwright | 4.12.1 | Keine | jetzt ok |
| @eslint/js | 10.0.1 | Keine | jetzt ok |
| @playwright/test | 1.62.0 | Keine | jetzt ok |
| @testing-library/jest-dom | 7.0.0 | Keine | jetzt ok |
| @testing-library/react | 16.3.2 | Keine | jetzt ok |
| @testing-library/user-event | 14.6.1 | Keine | jetzt ok |
| @types/node | 26.1.1 | Keine | jetzt ok |
| @types/pdfmake | 0.3.3 | Keine | jetzt ok |
| @types/react | 19.2.17 | Keine | jetzt ok |
| @types/react-dom | 19.2.3 | Keine | jetzt ok |
| @vitejs/plugin-react | 6.0.4 | Keine | jetzt ok |
| eslint | 10.8.0 | Keine | jetzt ok |
| fake-indexeddb | 6.2.5 | Keine | jetzt ok |
| globals | 17.7.0 | Keine | jetzt ok |
| jsdom | 29.1.1 | Keine | jetzt ok |
| openapi-typescript | 7.13.0 | Keine | jetzt ok |
| typescript | 5.9.3 | Keine | jetzt ok |
| typescript-eslint | 8.65.0 | Keine | jetzt ok |
| vite | 8.1.5 | Keine | jetzt ok |
| vite-plugin-pwa | 1.3.0 | Keine | jetzt ok |
| vitest | 4.1.10 | Keine | jetzt ok |

**Gesamt: 29 Node-Pakete (8 prod + 21 dev), 1 HIGH CVE (react-router via react-router-dom)**

---

## CVEs im Detail

### GHSA-qwww-vcr4-c8h2 – react-router (HIGH)

- **Betroffene Versionen:** >=7.12.0 <8.3.0
- **Installierte Version:** 7.18.1 (via react-router-dom)
- **Beschreibung:** RSC Mode CSRF Bypass Allows Action Execution Before 400 Response
- **Status:** In `pnpm.auditConfig.ignoreCves` bereits aufgelistet – bewusst akzeptiert
- **Empfehlung:** Upgrade auf react-router-dom >=8.3.0 bei nächster Major-Release-Planung

---

## Zusammenfassung

| Kategorie | Anzahl | CVEs |
|-----------|--------|------|
| Python runtime | 64 | 0 |
| Node runtime | 555 (total, inkl. transitive) | 1 HIGH (ignoriert) |
| Node prod direct | 8 | 1 HIGH |
| Node dev direct | 21 | 0 |

**DEPENDENCY_AUDITS: PASS (mit dokumentierter Ausnahme)**

Kein „Alles grün“-Status: Node weist 1 bewusst akzeptiertes HIGH (GHSA-qwww-vcr4-c8h2) auf; Python ist CVE-frei laut `pip-audit` zum Messzeitpunkt. Keine automatische Freigabe von Major-Upgrades.
