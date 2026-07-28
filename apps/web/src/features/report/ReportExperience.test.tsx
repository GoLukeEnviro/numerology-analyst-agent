import "fake-indexeddb/auto";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, vi } from "vitest";

import { ApiProblem } from "../../api/client";
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
            schema_version: "analysis-report-v2",
            summary: "Reflexionsbericht",
            sections: [],
            limitations: [],
            suggestions: [],
            provenance: {
                provider: "deepseek",
                model: "contract-model",
                temperature: null,
                top_p: null,
                thinking: "enabled",
                effective_sampling: "provider_managed",
                reasoning_effort: "high",
                context_signature: "a".repeat(64),
                prompt_version: "numra-report-de-v2",
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
                profile={
                    {
                        deterministic_hash: "a".repeat(64),
                    } as ProfileCalculationResult
                }
                profileId="profile-1"
                requestReport={requestReport}
            />,
        );

        expect(screen.getByText(/DeepSeek/i)).toBeVisible();
        expect(
            screen.getByText(/weder Klarname noch vollständiges Geburtsdatum/i),
        ).toBeVisible();
        const button = screen.getByRole("button", {
            name: /Bericht erzeugen/i,
        });
        expect(button).toBeDisabled();

        await userEvent.click(
            screen.getByRole("checkbox", { name: /Übertragung ein/i }),
        );
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
                profile={
                    {
                        deterministic_hash: "b".repeat(64),
                    } as ProfileCalculationResult
                }
                profileId="profile-offline"
                requestReport={requestReport}
            />,
        );

        await userEvent.click(
            screen.getByRole("checkbox", { name: /Übertragung ein/i }),
        );
        await userEvent.click(
            screen.getByRole("button", { name: /Bericht erzeugen/i }),
        );

        expect(requestReport).not.toHaveBeenCalled();
        expect(screen.getByRole("alert")).toHaveTextContent(
            /Internetverbindung erforderlich/i,
        );
    });

    it("explains why a follow-up cannot be sent while offline", async () => {
        const report: AnalysisReport = {
            schema_version: "analysis-report-v2",
            summary: "Gespeicherter Bericht",
            sections: [],
            limitations: [],
            suggestions: [],
            provenance: {
                provider: "deepseek",
                model: "contract-model",
                temperature: null,
                top_p: null,
                thinking: "enabled",
                effective_sampling: "provider_managed",
                reasoning_effort: "high",
                context_signature: "a".repeat(64),
                prompt_version: "numra-report-de-v2",
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
                profile={
                    {
                        deterministic_hash: "c".repeat(64),
                    } as ProfileCalculationResult
                }
                profileId="profile-follow-up"
                requestReport={requestReport}
                requestFollowUp={requestFollowUp}
            />,
        );

        await userEvent.click(
            screen.getByRole("checkbox", { name: /Übertragung ein/i }),
        );
        await userEvent.click(
            screen.getByRole("button", { name: /Bericht erzeugen/i }),
        );
        await screen.findByText("Gespeicherter Bericht");
        await userEvent.type(
            screen.getByLabelText(/Deine Rückfrage/i),
            "Was bedeutet das?",
        );
        vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(false);
        await userEvent.click(
            screen.getByRole("button", { name: /Rückfrage senden/i }),
        );

        expect(requestFollowUp).not.toHaveBeenCalled();
        expect(screen.getByRole("alert")).toHaveTextContent(
            /Internetverbindung erforderlich/i,
        );
    });

    it("shows a server-quota message when the daily contingent is exhausted", async () => {
        const quotaError = new ApiProblem({
            title: "Kontingent überschritten",
            detail: "Tageskontingent erschöpft",
            code: "rate_limit_exceeded",
            correlation_id: "corr-quota",
        });
        const requestReport = vi.fn().mockRejectedValue(quotaError);

        render(
            <ReportExperience
                profile={
                    {
                        deterministic_hash: "d".repeat(64),
                    } as ProfileCalculationResult
                }
                profileId="profile-server-quota"
                requestReport={requestReport}
            />,
        );

        await userEvent.click(
            screen.getByRole("checkbox", { name: /Übertragung ein/i }),
        );
        await userEvent.click(
            screen.getByRole("button", { name: /Bericht erzeugen/i }),
        );

        expect(await screen.findByRole("alert")).toHaveTextContent(
            /tägliche Kontingent ist ausgeschöpft/i,
        );
        expect(
            screen.getByRole("button", { name: /Bericht erzeugen/i }),
        ).toBeEnabled();
    });

    it("requires fresh consent before a follow-up to a loaded local report", async () => {
        const report = {
            schema_version: "analysis-report-v2",
            summary: "Gespeicherter Bericht",
            sections: [],
            limitations: [],
            suggestions: [],
            provenance: {
                provider: "deepseek",
                model: "deepseek-v4-pro",
                temperature: null,
                top_p: null,
                thinking: "enabled",
                effective_sampling: "provider_managed",
                reasoning_effort: "high",
                context_signature: "a".repeat(64),
                prompt_version: "numra-report-de-v2",
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
                profile={
                    {
                        deterministic_hash: "e".repeat(64),
                    } as ProfileCalculationResult
                }
                profileId="saved-profile"
                requestFollowUp={requestFollowUp}
            />,
        );

        expect(await screen.findByText("Gespeicherter Bericht")).toBeVisible();
        const button = screen.getByRole("button", {
            name: /Rückfrage senden/i,
        });
        await userEvent.type(
            screen.getByLabelText(/Deine Rückfrage/i),
            "Was passt dazu?",
        );
        expect(button).toBeDisabled();
        await userEvent.click(
            screen.getByRole("checkbox", { name: /Rückfrage.*übertragen/i }),
        );
        expect(button).toBeEnabled();
    });

    it("does not clear busy when B starts immediately after A is cancelled (race guard)", async () => {
        const user = userEvent.setup();

        let rejectA!: (reason: DOMException) => void;
        let resolveB!: (value: AnalysisReport) => void;

        const reportB: AnalysisReport = {
            schema_version: "analysis-report-v2",
            summary: "Bericht B",
            sections: [],
            limitations: [],
            suggestions: [],
            provenance: {
                provider: "deepseek",
                model: "test-model",
                temperature: null,
                top_p: null,
                thinking: "enabled",
                effective_sampling: "provider_managed",
                reasoning_effort: "high",
                context_signature: "b".repeat(64),
                prompt_version: "numra-report-de-v2",
                knowledge_bundle: "numra-knowledge-de-v1",
                calculation_hash: "f".repeat(64),
                provider_fingerprint: "test",
                prompt_tokens: 1,
                completion_tokens: 1,
            },
        };

        const requestReport = vi.fn()
            .mockReturnValueOnce(
                new Promise<AnalysisReport>((_, reject) => {
                    rejectA = reject;
                }),
            )
            .mockReturnValueOnce(
                new Promise<AnalysisReport>((resolve) => {
                    resolveB = resolve;
                }),
            );

        render(
            <ReportExperience
                profile={{ deterministic_hash: "f".repeat(64) } as ProfileCalculationResult}
                profileId="race-guard-test"
                requestReport={requestReport}
            />,
        );

        await user.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));

        // Step 1: A starts (busy=true)
        await user.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));

        // Step 2: A is cancelled (cancelRequest: busy=false, abortRef=null)
        await user.click(screen.getByRole("button", { name: /Abbrechen/i }));

        // Step 3: B starts immediately (busy=true, new controller)
        await user.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));
        expect(screen.getByRole("button", { name: /Bericht wird geprüft/i })).toBeInTheDocument();

        // Step 4: A's promise settles late with AbortError
        rejectA(new DOMException("Aborted", "AbortError"));
        await Promise.resolve();
        await Promise.resolve();

        // Step 5 & 6: B is still busy — A's finally did NOT call setBusy(false)
        expect(screen.getByRole("button", { name: /Bericht wird geprüft/i })).toBeInTheDocument();

        // Step 7: B resolves — only B sets the final state
        resolveB(reportB);
        expect(await screen.findByText("Bericht B")).toBeVisible();
    });

    it("aborts the active request when the component is unmounted", async () => {
        let capturedSignal: AbortSignal | undefined;

        const requestReport = vi.fn().mockImplementation(
            (_req: unknown, _fetcher: unknown, signal: AbortSignal | undefined) => {
                capturedSignal = signal;
                return new Promise<AnalysisReport>(() => {
                    // never resolves — simulates in-flight request
                });
            },
        );

        const { unmount } = render(
            <ReportExperience
                profile={{ deterministic_hash: "g".repeat(64) } as ProfileCalculationResult}
                profileId="unmount-test"
                requestReport={requestReport}
            />,
        );

        await userEvent.click(screen.getByRole("checkbox", { name: /Übertragung ein/i }));
        await userEvent.click(screen.getByRole("button", { name: /Bericht erzeugen/i }));

        expect(capturedSignal?.aborted).toBe(false);

        unmount();

        expect(capturedSignal?.aborted).toBe(true);
    });
});
