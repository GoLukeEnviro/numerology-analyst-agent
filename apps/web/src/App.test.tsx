import { cleanup, render, screen } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  window.history.pushState({}, "", "/");
  cleanup();
});

describe("Numra application shell", () => {
  it("introduces the product and its evidence boundary", async () => {
    const { App } = await import("./App");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Numerologie. Nachvollziehbar." })).toBeVisible();
    expect(
      screen.getByText(/keine wissenschaftlich validierte persönlichkeitsdiagnostik/i),
    ).toBeVisible();
    expect(screen.getByRole("link", { name: "Analyse starten" })).toHaveAttribute(
      "href",
      "/analyse/neu",
    );
  });

  it.each([
    ["/wissen", "Methode und Aussagegrenzen", /keine wissenschaftlich bestätigte/i],
    ["/datenschutz", "Datenschutz", /keine serverseitige Profilhistorie/i],
    ["/impressum", "Impressum", /öffentlichen Launch gesperrt/i],
    ["/nutzungsbedingungen", "Nutzungsbedingungen", /mindestens 18 Jahre/i],
  ])("renders the launch-critical page %s", async (path, heading, evidence) => {
    window.history.pushState({}, "", path);
    const { App } = await import("./App");

    render(<App />);

    expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    expect(screen.getByText(evidence)).toBeVisible();
  });
});
