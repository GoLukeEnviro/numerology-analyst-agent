import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import type { AnalysisReport, ProfileCalculationResult } from "../../api/types";
import { ReportExperience } from "./ReportExperience";

describe("ReportExperience", () => {
  it("shows the provider boundary and requires separate consent", async () => {
    const report: AnalysisReport = {
      schema_version: "analysis-report-v1",
      summary: "Reflexionsbericht",
      sections: [],
      limitations: [],
      suggestions: [],
      provenance: {
        provider: "deepseek",
        model: "contract-model",
        temperature: 0.2,
        top_p: 1,
        thinking: "enabled/high",
        prompt_version: "numra-report-de-v1",
        knowledge_bundle: "numra-knowledge-de-v1",
        calculation_hash: "a".repeat(64),
        provider_fingerprint: "test",
        prompt_tokens: 10,
        completion_tokens: 10,
      },
    };
    const requestReport = vi.fn().mockResolvedValue(report);
    render(
      <ReportExperience
        profile={{ deterministic_hash: "a".repeat(64) } as ProfileCalculationResult}
        profileId="profile-1"
        requestReport={requestReport}
      />,
    );

    expect(screen.getByText(/DeepSeek/i)).toBeVisible();
    expect(screen.getByText(/weder Klarname noch vollständiges Geburtsdatum/i)).toBeVisible();
    const button = screen.getByRole("button", { name: /Bericht erzeugen/i });
    expect(button).toBeDisabled();

    await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
    expect(button).toBeEnabled();
    await userEvent.click(button);
    expect(requestReport).toHaveBeenCalledOnce();
    expect(await screen.findByText("Reflexionsbericht")).toBeVisible();
  });
});
