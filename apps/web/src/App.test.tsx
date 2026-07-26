import { render, screen } from "@testing-library/react";

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
});
