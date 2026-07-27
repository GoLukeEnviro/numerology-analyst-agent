import "fake-indexeddb/auto";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, vi } from "vitest";

import type { AnalysisReport, ProfileCalculationResult } from "../../api/types";
import { localProfiles } from "../../storage/repository";
import { ReportExperience } from "./ReportExperience";

afterEach(() => {
  localStorage.clear();
  vi.useRealTimers();
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
        effective_sampling: "provider_managed",
        reasoning_effort: "high",
        context_signature: "a".repeat(64),
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
        effective_sampling: "provider_managed",
        reasoning_effort: "high",
        context_signature: "a".repeat(64),
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

  it("resets the local report quota on the next calendar day", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-07-25T12:00:00+02:00"));
    const report = {
      schema_version: "analysis-report-v1",
      summary: "Tagesbericht",
      sections: [],
      limitations: [],
      suggestions: [],
      provenance: {
        provider: "deepseek",
        model: "deepseek-v4-pro",
        temperature: 0.2,
        top_p: 1,
        thinking: "enabled/high",
        effective_sampling: "provider_managed",
        reasoning_effort: "high",
        context_signature: "a".repeat(64),
        prompt_version: "numra-report-de-v1",
        knowledge_bundle: "numra-knowledge-de-v1",
        calculation_hash: "d".repeat(64),
        provider_fingerprint: "test",
        prompt_tokens: 10,
        completion_tokens: 10,
      },
    } satisfies AnalysisReport;
    const profile = {
      deterministic_hash: "d".repeat(64),
    } as ProfileCalculationResult;
    const first = render(
      <ReportExperience
        profile={profile}
        profileId="profile-daily-quota"
        requestReport={vi.fn().mockResolvedValue(report)}
      />,
    );

    await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
    await userEvent.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));
    await screen.findByText("Tagesbericht");
    first.unmount();

    vi.setSystemTime(new Date("2026-07-26T12:00:00+02:00"));
    render(
      <ReportExperience
        profile={profile}
        profileId="profile-daily-quota"
        requestReport={vi.fn().mockResolvedValue(report)}
      />,
    );

    await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
    expect(screen.getByRole("button", { name: /Bericht erzeugen/i })).toBeEnabled();
  });

  it("requires fresh consent before a follow-up to a loaded local report", async () => {
    const report = {
      schema_version: "analysis-report-v1",
      summary: "Gespeicherter Bericht",
      sections: [],
      limitations: [],
      suggestions: [],
      provenance: {
        provider: "deepseek",
        model: "deepseek-v4-pro",
        temperature: 0.2,
        top_p: 1,
        thinking: "enabled/high",
        effective_sampling: "provider_managed",
        reasoning_effort: "high",
        context_signature: "a".repeat(64),
        prompt_version: "numra-report-de-v1",
        knowledge_bundle: "numra-knowledge-de-v1",
        calculation_hash: "e".repeat(64),
        provider_fingerprint: "test",
        prompt_tokens: 10,
        completion_tokens: 10,
      },
    } satisfies AnalysisReport;
    vi.spyOn(localProfiles, "getReport").mockResolvedValue(report);
    vi.spyOn(localProfiles, "listFollowUps").mockResolvedValue([]);
    const requestFollowUp = vi.fn();

    render(
      <ReportExperience
        profile={{ deterministic_hash: "e".repeat(64) } as ProfileCalculationResult}
        profileId="saved-profile"
        requestFollowUp={requestFollowUp}
      />,
    );

    expect(await screen.findByText("Gespeicherter Bericht")).toBeVisible();
    const button = screen.getByRole("button", { name: /Rückfrage senden/i });
    await userEvent.type(screen.getByLabelText(/Deine Rückfrage/i), "Was passt dazu?");
    expect(button).toBeDisabled();
    await userEvent.click(screen.getByRole("checkbox", { name: /Rückfrage.*übertragen/i }));
    expect(button).toBeEnabled();
  });
});
