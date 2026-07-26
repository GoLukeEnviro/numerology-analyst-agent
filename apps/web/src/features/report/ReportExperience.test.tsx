import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, vi } from "vitest";

import type { AnalysisReport, ProfileCalculationResult } from "../../api/types";
import { ReportExperience } from "./ReportExperience";

afterEach(() => {
  vi.restoreAllMocks();
});

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

  it("blocks a new report with a clear message while offline", async () => {
    const requestReport = vi.fn();
    vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(false);

    render(
      <ReportExperience
        profile={{ deterministic_hash: "b".repeat(64) } as ProfileCalculationResult}
        profileId="profile-offline"
        requestReport={requestReport}
      />,
    );

    await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
    await userEvent.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));

    expect(requestReport).not.toHaveBeenCalled();
    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(/Internetverbindung erforderlich/i);
  });

  it("explains why a follow-up cannot be sent while offline", async () => {
    const report: AnalysisReport = {
      schema_version: "analysis-report-v1",
      summary: "Gespeicherter Bericht",
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
        calculation_hash: "c".repeat(64),
        provider_fingerprint: "test",
        prompt_tokens: 10,
        completion_tokens: 10,
      },
    };
    const requestFollowUp = vi.fn();
    const requestReport = vi.fn().mockResolvedValue(report);

    render(
      <ReportExperience
        profile={{ deterministic_hash: "c".repeat(64) } as ProfileCalculationResult}
        profileId="profile-follow-up"
        requestReport={requestReport}
        requestFollowUp={requestFollowUp}
      />,
    );

    await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
    await userEvent.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));
    await screen.findByText("Gespeicherter Bericht");
    await userEvent.type(screen.getByLabelText(/Deine Rückfrage/i), "Was bedeutet das?");
    vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(false);
    await userEvent.click(screen.getByRole("button", { name: /Rückfrage senden/i }));

    expect(requestFollowUp).not.toHaveBeenCalled();
    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(/Internetverbindung erforderlich/i);
  });
});
