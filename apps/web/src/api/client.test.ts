import { describe, expect, it, vi } from "vitest";

import { calculateProfile } from "./client";
import type { ProfileCalculationRequest } from "./types";

const request: ProfileCalculationRequest = {
  person: {
    core_name: "Max Mustermann",
    active_name: null,
    birth_date: "1985-07-25",
    as_of_date: "2026-07-26",
    locale: "de",
    consent_given: false,
  },
  policy: {
    system: "pythagorean",
    version: "v1",
    y_mode: "phonetic",
    umlaut_policy: "de-direct-v1",
    name_basis: "both_separate",
    date_method: "both",
    locale: "de",
    master_numbers: [11, 22, 33],
  },
};

describe("calculateProfile", () => {
  it("posts the generated OpenAPI request contract", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ deterministic_hash: "a".repeat(64) }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await calculateProfile(request, fetcher);

    expect(fetcher).toHaveBeenCalledWith(
      "/api/v1/profiles/calculate",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(request),
      }),
    );
  });

  it("turns problem details into a typed error", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(
        JSON.stringify({
          title: "Request validation failed",
          detail: "Invalid input",
          code: "REQUEST_VALIDATION_FAILED",
          correlation_id: "corr-1",
        }),
        { status: 422, headers: { "Content-Type": "application/problem+json" } },
      ),
    );

    await expect(calculateProfile(request, fetcher)).rejects.toEqual(
      expect.objectContaining({
        name: "ApiProblem",
        message: "Invalid input",
        code: "REQUEST_VALIDATION_FAILED",
        correlationId: "corr-1",
      }),
    );
  });
});
