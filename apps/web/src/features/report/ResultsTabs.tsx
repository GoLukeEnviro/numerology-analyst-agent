/**
 * ResultsTabs — WAI-ARIA-APG conformant tab panel for 9 report tabs.
 *
 * - Keyboard: Arrow keys navigate, Home/End jump to first/last.
 * - Deep links: ``?tab=<tabId>`` via ``useSearchParams``.
 * - No LLM calls on tab switch — all sections are already loaded.
 * - Mobile: horizontally scrollable tab list with CSS scroll indicator.
 */
import { RiArrowLeftSLine, RiArrowRightSLine } from "@remixicon/react";
import { useCallback, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";

import { TAB_GROUPS, type SectionLike } from "./sectionMapping";

interface ResultsTabsProps {
    sections: SectionLike[];
    renderSection: (section: SectionLike) => React.ReactNode;
}

export function ResultsTabs({ sections, renderSection }: ResultsTabsProps) {
    const [searchParams, setSearchParams] = useSearchParams();
    const requestedTab = searchParams.get("tab");
    const activeTab = TAB_GROUPS.some((t) => t.tabId === requestedTab)
        ? (requestedTab as string)
        : TAB_GROUPS[0].tabId;
    const tabListRef = useRef<HTMLDivElement>(null);
    const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

    const setTab = useCallback(
        (tabId: string) => {
            setSearchParams({ tab: tabId }, { replace: true });
        },
        [setSearchParams],
    );

    const focusTab = useCallback((index: number) => {
        const id = TAB_GROUPS[index]?.tabId;
        if (id) {
            tabRefs.current.get(id)?.focus();
        }
    }, []);

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            const currentIndex = TAB_GROUPS.findIndex(
                (t) => t.tabId === activeTab,
            );
            let nextIndex: number;
            switch (e.key) {
                case "ArrowRight":
                    nextIndex = (currentIndex + 1) % TAB_GROUPS.length;
                    break;
                case "ArrowLeft":
                    nextIndex =
                        (currentIndex - 1 + TAB_GROUPS.length) %
                        TAB_GROUPS.length;
                    break;
                case "Home":
                    nextIndex = 0;
                    break;
                case "End":
                    nextIndex = TAB_GROUPS.length - 1;
                    break;
                default:
                    return;
            }
            e.preventDefault();
            focusTab(nextIndex);
            setTab(TAB_GROUPS[nextIndex].tabId);
        },
        [activeTab, focusTab, setTab],
    );

    useEffect(() => {
        const el = tabRefs.current.get(activeTab);
        if (el) {
            el.scrollIntoView({
                behavior: "smooth",
                block: "nearest",
                inline: "center",
            });
        }
    }, [activeTab]);

    const activeSections = sections.filter((s) =>
        TAB_GROUPS.find((t) => t.tabId === activeTab)?.sectionIds.includes(
            s.section_id,
        ),
    );

    return (
        <div className="results-tabs">
            <div className="tab-scroll-container" ref={tabListRef}>
                <div
                    className="tab-scroll-track"
                    role="tablist"
                    aria-label="Ergebnisreiter"
                    onKeyDown={handleKeyDown}
                >
                    {TAB_GROUPS.map((tab) => (
                        <button
                            key={tab.tabId}
                            ref={(el) => {
                                if (el) tabRefs.current.set(tab.tabId, el);
                            }}
                            role="tab"
                            id={`tab-${tab.tabId}`}
                            aria-selected={activeTab === tab.tabId}
                            aria-controls={`panel-${tab.tabId}`}
                            tabIndex={activeTab === tab.tabId ? 0 : -1}
                            className={`tab-button ${activeTab === tab.tabId ? "tab-active" : ""}`}
                            onClick={() => setTab(tab.tabId)}
                        >
                            <RiArrowLeftSLine className="tab-scroll-hint tab-scroll-hint--left" />
                            {tab.label}
                            <RiArrowRightSLine className="tab-scroll-hint tab-scroll-hint--right" />
                        </button>
                    ))}
                </div>
            </div>
            {activeSections.map((section) => (
                <div
                    key={section.section_id}
                    role="tabpanel"
                    id={`panel-${activeTab}`}
                    aria-labelledby={`tab-${activeTab}`}
                    tabIndex={0}
                    className="tab-panel"
                >
                    {renderSection(section)}
                </div>
            ))}
        </div>
    );
}
