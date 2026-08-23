import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeAll, describe, expect, it, vi } from "vitest";

import { ResultsTabs } from "./ResultsTabs";
import { TAB_GROUPS, type SectionLike } from "./sectionMapping";

beforeAll(() => {
    // jsdom does not implement scrollIntoView.
    Element.prototype.scrollIntoView = vi.fn();
});

function sectionsForAllTabs(): SectionLike[] {
    return TAB_GROUPS.flatMap((tab) =>
        tab.sectionIds.map((section_id) => ({
            section_id,
            applicable: true,
            summary: `Inhalt ${section_id}`,
        })),
    );
}

function renderTabs(initialPath = "/profil/p1/bericht") {
    return render(
        <MemoryRouter initialEntries={[initialPath]}>
            <ResultsTabs
                sections={sectionsForAllTabs()}
                renderSection={(section) => (
                    <p data-testid={`section-${section.section_id}`}>
                        {section.summary}
                    </p>
                )}
            />
        </MemoryRouter>,
    );
}

describe("ResultsTabs", () => {
    it("renders a tablist with nine tabs and WAI-ARIA roles", () => {
        renderTabs();

        const tablist = screen.getByRole("tablist", {
            name: "Ergebnisreiter",
        });
        expect(tablist).toBeInTheDocument();
        expect(screen.getAllByRole("tab")).toHaveLength(9);
        expect(screen.getAllByRole("tabpanel")).toHaveLength(1);
    });

    it("marks the active tab with aria-selected and roving tabindex", () => {
        renderTabs();

        const firstTab = screen.getByRole("tab", { name: /Überblick/i });
        expect(firstTab).toHaveAttribute("aria-selected", "true");
        expect(firstTab).toHaveAttribute("tabindex", "0");
        expect(firstTab).toHaveAttribute(
            "aria-controls",
            "panel-ueberblick",
        );

        const secondTab = screen.getByRole("tab", { name: /Lebensweg/i });
        expect(secondTab).toHaveAttribute("aria-selected", "false");
        expect(secondTab).toHaveAttribute("tabindex", "-1");
    });

    it("switches the active tab on click and shows the matching sections", async () => {
        const user = userEvent.setup();
        renderTabs();

        await user.click(screen.getByRole("tab", { name: /Lebensphasen/i }));

        expect(
            screen.getByRole("tab", { name: /Lebensphasen/i }),
        ).toHaveAttribute("aria-selected", "true");
        expect(screen.getByTestId("section-pinnacles")).toBeInTheDocument();
        expect(screen.getByTestId("section-challenges")).toBeInTheDocument();
        expect(screen.queryByTestId("section-executive_overview")).toBeNull();
    });

    it("supports arrow-key navigation with focus management", async () => {
        const user = userEvent.setup();
        renderTabs();

        const firstTab = screen.getByRole("tab", { name: /Überblick/i });
        firstTab.focus();
        await user.keyboard("{ArrowRight}");

        const secondTab = screen.getByRole("tab", { name: /Lebensweg/i });
        expect(secondTab).toHaveAttribute("aria-selected", "true");
        expect(secondTab).toHaveFocus();
    });

    it("wraps around with ArrowLeft and jumps with Home/End", async () => {
        const user = userEvent.setup();
        renderTabs();

        const firstTab = screen.getByRole("tab", { name: /Überblick/i });
        firstTab.focus();
        await user.keyboard("{ArrowLeft}");

        const lastTab = screen.getByRole("tab", { name: /Rechenweg/i });
        expect(lastTab).toHaveAttribute("aria-selected", "true");
        expect(lastTab).toHaveFocus();

        await user.keyboard("{Home}");
        expect(
            screen.getByRole("tab", { name: /Überblick/i }),
        ).toHaveAttribute("aria-selected", "true");

        await user.keyboard("{End}");
        expect(lastTab).toHaveAttribute("aria-selected", "true");
    });

    it("honours deep links via ?tab= and keeps the tab on refresh", () => {
        renderTabs("/profil/p1/bericht?tab=rechenweg");

        expect(
            screen.getByRole("tab", { name: /Rechenweg/i }),
        ).toHaveAttribute("aria-selected", "true");
        expect(
            screen.getByTestId("section-method_and_calculation_notes"),
        ).toBeInTheDocument();
    });

    it("falls back to the first tab for an unknown deep link", () => {
        renderTabs("/profil/p1/bericht?tab=unbekannt");

        expect(
            screen.getByRole("tab", { name: /Überblick/i }),
        ).toHaveAttribute("aria-selected", "true");
    });
});
