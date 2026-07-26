import { expect, test } from "@playwright/test";

test("calculates a complete profile from the guided flow", async ({ page }) => {
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

  await expect(page).toHaveURL(/\/profil\/[a-f0-9]{12}$/);
  await expect(page.getByRole("heading", { name: "Dein Zahlenatlas" })).toBeVisible();
  await expect(page.getByRole("table", { name: "Tabellarischer Zahlenatlas" })).toBeVisible();
  await expect(page.getByText("Persönliche Zyklen")).toBeVisible();
});
