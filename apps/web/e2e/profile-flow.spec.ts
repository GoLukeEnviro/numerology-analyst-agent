import { readFile } from "node:fs/promises";

import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

async function expectNoWcagViolations(page: Page): Promise<void> {
  const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
  expect(
    results.violations,
    JSON.stringify(
      results.violations.map(({ id, impact, nodes }) => ({
        id,
        impact,
        targets: nodes.map((node) => node.target),
      })),
      null,
      2,
    ),
  ).toEqual([]);
}

async function completeAnalysis(page: Page): Promise<void> {
  await page.goto("/analyse/neu");
  await expect(page.getByRole("heading", { name: "Deine Ausgangsdaten" })).toBeVisible();

  await page.getByLabel("Vollständiger Geburtsname").fill("Max Mustermann");
  await page.getByLabel("Aktuell verwendeter Name optional").fill("Max Power");
  await page.getByLabel("Geburtsdatum").fill("1985-07-25");
  await page.getByLabel("Berechnungsdatum").fill("2026-07-26");
  await page.getByLabel(/mindestens 18 Jahre alt/i).check();
  await page.getByRole("button", { name: "Eingaben prüfen" }).click();

  await expect(page.getByRole("heading", { name: "Prüfen und freigeben" })).toBeVisible();
  await page.getByLabel(/symbolische Reflexionsmethode/i).check();
  await page.getByRole("button", { name: "Profil berechnen" }).click();
}

test("calculates, stores and exports a complete profile", async ({ page }, testInfo) => {
  await completeAnalysis(page);

  await expect(page).toHaveURL(/\/profil\/[a-f0-9]{16}$/);
  await expect(page.getByRole("heading", { name: "Dein Zahlenatlas" })).toBeVisible();
  await expect(page.getByRole("table", { name: "Tabellarischer Zahlenatlas" })).toBeVisible();
  await expect(page.getByText("Persönliche Zyklen")).toBeVisible();

  await page.getByRole("button", { name: "Lokal speichern", exact: true }).click();
  await expect(page.getByText(/Profil dauerhaft.+gespeichert/)).toBeVisible();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "PDF exportieren" }).click();
  const download = await downloadEvent;
  await download.saveAs(testInfo.outputPath("numra-profile.pdf"));
  const path = await download.path();
  expect(path).not.toBeNull();
  if (path === null) throw new Error("PDF download path is unavailable");
  const bytes = await readFile(path);
  expect(bytes.subarray(0, 5).toString()).toBe("%PDF-");
  expect(bytes.byteLength).toBeGreaterThan(1_000);
});

test("keeps a saved profile readable after a browser restart", async ({ page }) => {
  await completeAnalysis(page);
  await page.getByRole("button", { name: "Lokal speichern", exact: true }).click();
  await expect(page.getByText(/Profil dauerhaft.+gespeichert/)).toBeVisible();
  await page.goto("/bibliothek");
  await page.getByRole("link", { name: "Max Mustermann" }).click();
  await page.reload();

  await expect(page.getByRole("heading", { name: "Max Mustermann" })).toBeVisible();
});

test("keeps a saved profile readable after an offline restart", async ({
  page,
  context,
  browserName,
}) => {
  test.skip(
    browserName === "webkit",
    "Playwright WebKit blocks offline reload in Web Inspector before the service worker.",
  );
  await completeAnalysis(page);
  await page.getByRole("button", { name: "Lokal speichern", exact: true }).click();
  await expect(page.getByText(/Profil dauerhaft.+gespeichert/)).toBeVisible();
  await page.goto("/bibliothek");
  await page.getByRole("link", { name: "Max Mustermann" }).click();
  await page.waitForFunction(() => "serviceWorker" in navigator && navigator.serviceWorker.controller);

  await context.setOffline(true);
  await page.reload();

  await expect(page.getByRole("heading", { name: "Max Mustermann" })).toBeVisible();
});

test("persists the light theme and explains installation", async ({ page }) => {
  await page.goto("/einstellungen");
  await page.getByRole("button", { name: "Light Atlas" }).click();
  await page.reload();

  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page.getByText(/iPhone und iPad/)).toBeVisible();
});

test("has no automated WCAG 2.2 AA violations in the primary flow", async ({ page }) => {
  test.setTimeout(90_000);
  // Die Startseite animiert .reveal-Elemente (700 ms). axe misst sonst den
  // Button in einem teiltransparenten Zwischenzustand (falscher Kontrast).
  // reducedMotion reduziert alle Animationen auf 0.01 ms (bestehende CSS-Regel).
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expectNoWcagViolations(page);

  await page.goto("/analyse/neu");
  await expectNoWcagViolations(page);

  await completeAnalysis(page);
  await expect(page.getByRole("heading", { name: "Dein Zahlenatlas" })).toBeVisible();
  await expectNoWcagViolations(page);
});
