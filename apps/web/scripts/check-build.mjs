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
