/**
 * Section mapping — 18 report sections → 9 UI tabs.
 *
 * Fixed UI labels, never derived from model output.
 * The ``section_id`` determines navigation, not free-text headings.
 */

export const SECTION_UI_LABELS: Record<string, string> = {
    executive_overview: "Überblick",
    life_path_and_purpose: "Lebensweg",
    birthday_and_attitude: "Lebensweg",
    inner_motivation: "Inneres Profil",
    expression_and_external_persona: "Ausdruck und Wirkung",
    maturity_and_development: "Inneres Profil",
    number_harmonies: "Muster und Spannungen",
    number_tensions: "Muster und Spannungen",
    repetitions_and_missing_values: "Muster und Spannungen",
    life_phases: "Lebensphasen",
    personal_cycles: "Lebensphasen",
    pinnacles: "Lebensphasen",
    challenges: "Lebensphasen",
    shadow_patterns: "Schatten und Entwicklung",
    development_opportunities: "Schatten und Entwicklung",
    practical_integration: "Integration",
    final_synthesis: "Integration",
    method_and_calculation_notes: "Rechenweg",
};

export interface TabGroup {
    tabId: string;
    label: string;
    sectionIds: string[];
}

export const TAB_GROUPS: TabGroup[] = [
    {
        tabId: "ueberblick",
        label: "Überblick",
        sectionIds: ["executive_overview"],
    },
    {
        tabId: "lebensweg",
        label: "Lebensweg",
        sectionIds: ["life_path_and_purpose", "birthday_and_attitude"],
    },
    {
        tabId: "inneres-profil",
        label: "Inneres Profil",
        sectionIds: ["inner_motivation", "maturity_and_development"],
    },
    {
        tabId: "ausdruck-wirkung",
        label: "Ausdruck und Wirkung",
        sectionIds: ["expression_and_external_persona"],
    },
    {
        tabId: "muster-spannungen",
        label: "Muster und Spannungen",
        sectionIds: [
            "number_harmonies",
            "number_tensions",
            "repetitions_and_missing_values",
        ],
    },
    {
        tabId: "lebensphasen",
        label: "Lebensphasen",
        sectionIds: [
            "life_phases",
            "personal_cycles",
            "pinnacles",
            "challenges",
        ],
    },
    {
        tabId: "schatten-entwicklung",
        label: "Schatten und Entwicklung",
        sectionIds: ["shadow_patterns", "development_opportunities"],
    },
    {
        tabId: "integration",
        label: "Integration",
        sectionIds: ["practical_integration", "final_synthesis"],
    },
    {
        tabId: "rechenweg",
        label: "Rechenweg",
        sectionIds: ["method_and_calculation_notes"],
    },
];

export interface SectionLike {
    section_id: string;
    applicable: boolean;
    model_heading?: string | null;
    summary?: string;
    claims?: Array<{
        claim_id?: string;
        claim_type?: string;
        text: string;
        calculation_refs?: string[];
        knowledge_refs?: string[];
        uncertainty?: string | null;
    }>;
    supporting_calculation_refs?: string[];
    supporting_knowledge_refs?: string[];
    counter_hypotheses?: string[];
    reflection_questions?: string[];
    practical_options?: string[];
    limitations?: string[];
}

export function sectionsByTab(
    sections: SectionLike[],
): Map<string, SectionLike[]> {
    const map = new Map<string, SectionLike[]>();
    for (const tab of TAB_GROUPS) {
        const matched = sections.filter((s) =>
            tab.sectionIds.includes(s.section_id),
        );
        if (matched.length > 0) map.set(tab.tabId, matched);
    }
    return map;
}

export function tabForSectionId(sectionId: string): string | undefined {
    for (const tab of TAB_GROUPS) {
        if (tab.sectionIds.includes(sectionId)) return tab.tabId;
    }
    return undefined;
}
