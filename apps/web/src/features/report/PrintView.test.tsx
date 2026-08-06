import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PrintView } from "./PrintView";
import { TAB_GROUPS, type SectionLike } from "./sectionMapping";

function allSections(): SectionLike[] {
    return TAB_GROUPS.flatMap((tab) =>
        tab.sectionIds.map((section_id) => ({
            section_id,
            applicable: true,
            model_heading: `Modell ${section_id}`,
            summary: `Zusammenfassung ${section_id}`,
            claims: [
                {
                    claim_id: `claim-${section_id}`,
                    claim_type: "calculation_fact",
                    text: `Aussage ${section_id}`,
                    uncertainty: "Unsicher",
                },
            ],
            counter_hypotheses: [`Gegenhypothese ${section_id}`],
            reflection_questions: [`Frage ${section_id}`],
            practical_options: [`Option ${section_id}`],
            limitations: [`Grenze ${section_id}`],
        })),
    );
}

describe("PrintView", () => {
    it("renders all 18 sections in linear order with headings", () => {
        render(
            <PrintView
                sections={allSections()}
                summary="Gesamtzusammenfassung"
                globalLimitations={["Wissenschaftliche Grenze 1"]}
            />,
        );

        expect(screen.getByText("Numra Analysebericht")).toBeInTheDocument();
        expect(screen.getByText("Gesamtzusammenfassung")).toBeInTheDocument();
        expect(
            screen.getAllByRole("heading", { level: 3, hidden: true }),
        ).toHaveLength(20); // 18 sections + summary + global limitations
        expect(screen.getByText("Aussage executive_overview")).toBeInTheDocument();
        expect(
            screen.getByText("Aussage method_and_calculation_notes"),
        ).toBeInTheDocument();
    });

    it("renders claims, counter-hypotheses, questions, options and limitations", () => {
        render(
            <PrintView
                sections={allSections()}
                summary="S"
                globalLimitations={[]}
            />,
        );

        expect(
            screen.getByText(/Gegenhypothese pinnacles/),
        ).toBeInTheDocument();
        expect(screen.getByText(/Frage pinnacles/)).toBeInTheDocument();
        expect(screen.getByText(/Option pinnacles/)).toBeInTheDocument();
        expect(screen.getByText(/Grenze pinnacles/)).toBeInTheDocument();
        expect(screen.getAllByText(/Unsicher/).length).toBeGreaterThan(0);
    });

    it("marks non-applicable sections without rendering their content", () => {
        const sections: SectionLike[] = [
            {
                section_id: "pinnacles",
                applicable: false,
                summary: "Nicht anwendbar",
            },
        ];
        render(
            <PrintView sections={sections} summary="S" globalLimitations={[]} />,
        );

        expect(
            screen.getByText(/Dieser Abschnitt ist für dieses Profil nicht anwendbar/i),
        ).toBeInTheDocument();
        expect(screen.queryByText("Nicht anwendbar")).toBeNull();
    });

    it("renders global limitations only when present", () => {
        const { rerender } = render(
            <PrintView sections={[]} summary="S" globalLimitations={[]} />,
        );
        expect(
            screen.queryByText("Wissenschaftliche Grenzen"),
        ).toBeNull();

        rerender(
            <PrintView
                sections={[]}
                summary="S"
                globalLimitations={["Grenze A", "Grenze B"]}
            />,
        );
        expect(screen.getByText("Wissenschaftliche Grenzen")).toBeInTheDocument();
        expect(screen.getByText("Grenze A")).toBeInTheDocument();
        expect(screen.getByText("Grenze B")).toBeInTheDocument();
    });

    it("falls back to the raw section id when no UI label exists", () => {
        const sections: SectionLike[] = [
            { section_id: "custom_unknown_section", applicable: true },
        ];
        render(
            <PrintView sections={sections} summary="S" globalLimitations={[]} />,
        );

        expect(screen.getByText("custom_unknown_section")).toBeInTheDocument();
    });
});
