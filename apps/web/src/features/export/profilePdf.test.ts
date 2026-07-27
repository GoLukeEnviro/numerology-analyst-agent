import { describe, expect, it } from "vitest";

import type { AnalysisReport, ProfileCalculationResult } from "../../api/types";
import { buildPdfLines, createProfilePdf } from "./profilePdf";

const profile = {
  deterministic_hash: "a".repeat(64),
  input_ref: { core_name: "Max Mustermann", as_of_date: "2026-07-26" },
  life_path_a: { reduced_value: 1, compound_notation: "37/10/1" },
  birthday: { reduced_value: 7, compound_notation: "25/7" },
  attitude: { reduced_value: 5, compound_notation: "12/3" },
  core_name: {
    expression: { reduced_value: 5, compound_notation: "50/5" },
    soul_urge: { reduced_value: 3, compound_notation: "21/3" },
    personality: { reduced_value: 2, compound_notation: "29/11/2" },
  },
  maturity: { reduced_value: 6, compound_notation: "6" },
  cycles: {
    personal_year: { reduced_value: 6 },
    personal_month: { reduced_value: 4 },
    personal_day: { reduced_value: 3 },
    pinnacles: [],
    challenges: [],
  },
  trace: { steps: [{ operation: "sum", result: 37 }] },
} as unknown as ProfileCalculationResult;

const report = {
  schema_version: "analysis-report-v1",
  summary: "Ein geprüfter Reflexionsbericht.",
  sections: [],
  limitations: ["Keine wissenschaftliche Persönlichkeitsdiagnostik."],
  suggestions: [],
  provenance: {
    provider: "deepseek",
    model: "deepseek-v4-pro",
    temperature: 0.2,
    top_p: 1,
    thinking: "enabled/high",
    effective_sampling: "provider_managed",
    reasoning_effort: "high",
    prompt_version: "numra-report-de-v1",
    knowledge_bundle: "numra-knowledge-de-v1",
    calculation_hash: "a".repeat(64),
    provider_fingerprint: null,
    prompt_tokens: 10,
    completion_tokens: 20,
  },
} satisfies AnalysisReport;

describe("Numra PDF export", () => {
  it("contains profile, claim boundary, trace, hash and provenance", () => {
    const text = buildPdfLines(profile, report).join("\n");

    expect(text).toContain("Max Mustermann");
    expect(text).toContain("Lebensweg: 1");
    expect(text).toContain("Berechnung / Tradition / Hypothese");
    expect(text).toContain("Keine wissenschaftliche Persönlichkeitsdiagnostik");
    expect(text).toContain("a".repeat(64));
    expect(text).toContain("deepseek-v4-pro");
    expect(text).toContain("Rechenweg");
  });

  it("creates a readable multi-page PDF byte stream", async () => {
    const bytes = await createProfilePdf(profile, report);

    expect(new TextDecoder().decode(bytes.slice(0, 5))).toBe("%PDF-");
    expect(bytes.byteLength).toBeGreaterThan(1_000);
  });
});
