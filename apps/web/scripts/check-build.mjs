import { gzipSync } from "node:zlib";
import { readFile, readdir } from "node:fs/promises";
import path from "node:path";

const dist = path.resolve("dist");
const html = await readFile(path.join(dist, "index.html"), "utf8");
const files = await readdir(path.join(dist, "assets"));
const initialMatch = html.match(/<script[^>]+src="\/assets\/([^"]+\.js)"/);

if (!initialMatch) throw new Error("Initiales JavaScript-Bundle wurde nicht gefunden.");
const initialFile = initialMatch[1];
const initialBytes = await readFile(path.join(dist, "assets", initialFile));
const initialGzip = gzipSync(initialBytes).byteLength;
const initialBudget = 160 * 1024;
if (initialGzip > initialBudget) {
  throw new Error(`Initiales JavaScript ${initialGzip} B überschreitet Budget ${initialBudget} B.`);
}

for (const lazyName of ["profilePdf", "ExpertDetails"]) {
  const chunk = files.find((file) => file.startsWith(`${lazyName}-`) && file.endsWith(".js"));
  if (!chunk) throw new Error(`Lazy Chunk ${lazyName} fehlt.`);
  if (html.includes(chunk)) throw new Error(`${lazyName} darf nicht initial geladen werden.`);
}

const manifest = JSON.parse(await readFile(path.join(dist, "manifest.webmanifest"), "utf8"));
const icons = Array.isArray(manifest.icons) ? manifest.icons : [];
if (!icons.some((icon) => icon.sizes === "192x192")) throw new Error("192x192 PWA-Icon fehlt.");
if (!icons.some((icon) => String(icon.purpose).includes("maskable"))) {
  throw new Error("Maskable PWA-Icon fehlt.");
}

const serviceWorker = await readFile(path.join(dist, "sw.js"), "utf8");
if (serviceWorker.includes("/api/v1/") || serviceWorker.includes('method:"POST"')) {
  throw new Error("Service Worker darf API-POSTs oder API-Antworten nicht cachen.");
}

console.log(`Build-Budget erfüllt: initial ${initialGzip} / ${initialBudget} Bytes gzip.`);

// Coverage-Gate: validiert das json-summary-Artefakt aus `vitest run --coverage`
// gegen die gemessene Baseline vom 2026-08-02 (docs/audit/web-coverage-baseline-2026-08-02.md).
// Die Schwellenwerte sind identisch zu `coverage.thresholds` in vite.config.ts.
const coverageThresholds = {
  statements: 69.48,
  branches: 59.39,
  functions: 62,
  lines: 73.95,
};

const coverageSummaryPath = path.resolve("coverage", "coverage-summary.json");
let coverageSummary;
try {
  coverageSummary = JSON.parse(await readFile(coverageSummaryPath, "utf8"));
} catch {
  throw new Error(
    `Coverage-Summary fehlt unter ${coverageSummaryPath}. ` +
      "Bitte zuerst `pnpm web:coverage` ausführen.",
  );
}

const total = coverageSummary.total;
if (!total) throw new Error("Coverage-Summary enthält keinen Gesamtwert.");

const pct = (key) => Number(total[key]?.pct ?? NaN);
const measured = {
  statements: pct("statements"),
  branches: pct("branches"),
  functions: pct("functions"),
  lines: pct("lines"),
};

for (const key of Object.keys(coverageThresholds)) {
  const threshold = coverageThresholds[key];
  const value = measured[key];
  if (!Number.isFinite(value)) {
    throw new Error(`Coverage-Metrik "${key}" fehlt in der Summary.`);
  }
  if (value < threshold) {
    throw new Error(
      `Coverage-Gate verletzt: ${key} ${value}% < Schwellenwert ${threshold}%.`,
    );
  }
}

console.log(
  `Coverage-Gate erfüllt: Statements ${measured.statements}%, Branches ${measured.branches}%, ` +
    `Functions ${measured.functions}%, Lines ${measured.lines}%.`,
);
