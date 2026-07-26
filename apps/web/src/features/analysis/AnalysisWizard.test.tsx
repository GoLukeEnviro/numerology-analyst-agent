import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { AnalysisWizard } from "./AnalysisWizard";
import type { ProfileCalculationResult } from "../../api/types";

describe("AnalysisWizard", () => {
  it("guides the user through data, review and calculation", async () => {
    const user = userEvent.setup();
    const result = { deterministic_hash: "b".repeat(64) } as ProfileCalculationResult;
    const calculate = vi.fn().mockResolvedValue(result);
    const onComplete = vi.fn();

    render(<AnalysisWizard calculate={calculate} onComplete={onComplete} />);

    expect(screen.getByRole("heading", { name: "Deine Ausgangsdaten" })).toBeVisible();
    await user.type(screen.getByLabelText("Vollständiger Geburtsname"), "Max Mustermann");
    await user.type(screen.getByLabelText("Geburtsdatum"), "1985-07-25");
    await user.type(screen.getByLabelText("Berechnungsdatum"), "2026-07-26");
    await user.click(screen.getByLabelText(/mindestens 18 Jahre alt/i));
    await user.click(screen.getByRole("button", { name: "Eingaben prüfen" }));

    expect(screen.getByRole("heading", { name: "Prüfen und freigeben" })).toBeVisible();
    expect(screen.getByText("Max Mustermann")).toBeVisible();
    await user.click(screen.getByLabelText(/symbolische reflexionsmethode/i));
    await user.click(screen.getByRole("button", { name: "Profil berechnen" }));

    expect(calculate).toHaveBeenCalledOnce();
    expect(onComplete).toHaveBeenCalledWith(result);
  });

  it("blocks calculation while offline", () => {
    render(
      <AnalysisWizard
        calculate={vi.fn()}
        onComplete={vi.fn()}
        online={false}
      />,
    );

    expect(screen.getByText(/offline keine neue berechnung/i)).toBeVisible();
  });
});
