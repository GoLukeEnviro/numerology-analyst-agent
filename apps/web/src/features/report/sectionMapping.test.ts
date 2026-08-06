import { describe, expect, it } from "vitest";

import {
    SECTION_UI_LABELS,
    TAB_GROUPS,
    sectionsByTab,
    tabForSectionId,
} from "./sectionMapping";

const ALL_18_SECTION_IDS = [
    "executive_overview",
    "life_path_and_purpose",
    "birthday_and_attitude",
    "inner_motivation",
    "expression_and_external_persona",
    "maturity_and_development",
    "number_harmonies",
    "number_tensions",
    "repetitions_and_missing_values",
    "life_phases",
    "personal_cycles",
    "pinnacles",
    "challenges",
    "shadow_patterns",
    "development_opportunities",
    "practical_integration",
    "final_synthesis",
    "method_and_calculation_notes",
];

describe("sectionMapping", () => {
    it("defines exactly nine UI tabs", () => {
        expect(TAB_GROUPS).toHaveLength(9);
    });

    it("covers all 18 report sections exactly once across the tabs", () => {
        const mapped = TAB_GROUPS.flatMap((tab) => tab.sectionIds);
        expect(mapped).toHaveLength(18);
        expect(new Set(mapped).size).toBe(18);
        expect(mapped.sort()).toEqual([...ALL_18_SECTION_IDS].sort());
    });

    it("provides a fixed UI label for every section id", () => {
        for (const sectionId of ALL_18_SECTION_IDS) {
            expect(SECTION_UI_LABELS[sectionId]).toBeTruthy();
        }
    });

    it("groups sections by tab and skips empty tabs", () => {
        const sections = ALL_18_SECTION_IDS.map((section_id) => ({
            section_id,
            applicable: true,
        }));
        const map = sectionsByTab(sections);

        expect(map.size).toBe(9);
        expect(map.get("ueberblick")?.map((s) => s.section_id)).toEqual([
            "executive_overview",
        ]);
        expect(map.get("lebensphasen")?.map((s) => s.section_id)).toEqual([
            "life_phases",
            "personal_cycles",
            "pinnacles",
            "challenges",
        ]);
    });

    it("returns undefined for unknown section ids", () => {
        expect(tabForSectionId("does_not_exist")).toBeUndefined();
        expect(tabForSectionId("pinnacles")).toBe("lebensphasen");
    });
});
