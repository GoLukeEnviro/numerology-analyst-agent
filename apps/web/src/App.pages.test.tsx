import "fake-indexeddb/auto";

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, vi } from "vitest";

import type { LocalProfile } from "./storage/repository";
import { localProfiles } from "./storage/repository";
import type { ProfileCalculationResult } from "./api/types";

afterEach(() => {
  window.history.pushState({}, "", "/");
  cleanup();
  vi.restoreAllMocks();
});

async function renderApp(path: string) {
  window.history.pushState({}, "", path);
  const { App } = await import("./App");
  render(<App />);
}

describe("NewAnalysisPage (/analyse/neu)", () => {
  it("renders the analysis wizard with the data input step", async () => {
    await renderApp("/analyse/neu");

    expect(screen.getByRole("heading", { name: "Deine Ausgangsdaten" })).toBeVisible();
    expect(screen.getByLabelText(/Vollständiger Geburtsname/i)).toBeVisible();
  });
});

describe("ProfilePage (/profil/:id)", () => {
  it("shows an empty state when the profile is not in session or local storage", async () => {
    await renderApp("/profil/unknown-id-12345");

    expect(
      await screen.findByText(/lokales Profil wird geladen|nicht lokal verfügbar/i),
    ).toBeInTheDocument();
  });

  it("loads a profile from session storage", async () => {
    const mockProfile = {
      deterministic_hash: "a".repeat(64),
      schema_version: "profile-calculation-result-v3",
      input_ref: { core_name: "Max Mustermann", as_of_date: "2026-01-01" },
      policy: { system: "pythagorean", version: "v1" },
      core_name: {
        expression: { reduced_value: 3, compound_notation: "3" },
        soul_urge: { reduced_value: 5, compound_notation: "5" },
        personality: { reduced_value: 7, compound_notation: "7" },
      },
      active_name: null,
      life_path_a: { reduced_value: 1, compound_notation: "1" },
      birthday: { reduced_value: 2, compound_notation: "2" },
      attitude: { reduced_value: 4, compound_notation: "4" },
      maturity: { reduced_value: 6, compound_notation: "6" },
      cycles: {
        personal_year: { reduced_value: 8 },
        personal_month: { reduced_value: 9 },
        personal_day: { reduced_value: 1 },
        pinnacles: [],
        challenges: [],
      },
    };
    const id = mockProfile.deterministic_hash.slice(0, 16);
    sessionStorage.setItem(`numra:session:${id}`, JSON.stringify(mockProfile));

    await renderApp(`/profil/${id}`);

    expect(screen.getByRole("heading", { name: "Max Mustermann" })).toBeVisible();
    sessionStorage.removeItem(`numra:session:${id}`);
  });
});

describe("ReportPage (/profil/:id/bericht)", () => {
  it("shows an empty state when no profile is available", async () => {
    await renderApp("/profil/no-profile/bericht");

    expect(
      await screen.findByText(/Öffne oder speichere zuerst ein Profil/i),
    ).toBeVisible();
  });
});

describe("LibraryPage (/bibliothek)", () => {
  it("renders the library heading and empty state", async () => {
    vi.spyOn(localProfiles, "listProfiles").mockResolvedValue([]);

    await renderApp("/bibliothek");

    expect(screen.getByRole("heading", { name: "Deine Bibliothek" })).toBeVisible();
    expect(
      await screen.findByText(/noch keine Profile lokal gespeichert/i),
    ).toBeVisible();
  });

  it("renders saved profiles", async () => {
    vi.spyOn(localProfiles, "listProfiles").mockResolvedValue([
      {
        id: "profile-abc123",
        name: "Anna Beispiel",
        calculationHash: "a".repeat(64),
        createdAt: 1_705_276_800_000,
        updatedAt: 1_705_276_800_000,
        protected: false,
        profile: {} as ProfileCalculationResult,
      } satisfies LocalProfile,
    ]);

    await renderApp("/bibliothek");

    expect(await screen.findByText("Anna Beispiel")).toBeVisible();
  });
});

describe("SettingsPage (/einstellungen)", () => {
  it("renders the settings page with key sections", async () => {
    await renderApp("/einstellungen");

    expect(screen.getByRole("heading", { name: "Einstellungen" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Passphraseschutz" })).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "Alle lokalen Daten löschen" }),
    ).toBeVisible();
  });
});
