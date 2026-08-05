/**
 * PrintView — linear print rendering of all 18 report sections.
 *
 * Activated via ``@media print``.  Sections are rendered as a flat,
 * accessible list with headings, claims, counter-hypotheses, questions,
 * options and limitations — suitable for PDF export or physical print.
 */
import type { SectionLike } from "./sectionMapping";
import { SECTION_UI_LABELS } from "./sectionMapping";

interface PrintViewProps {
    sections: SectionLike[];
    summary: string;
    globalLimitations: string[];
}

export function PrintView({
    sections,
    summary,
    globalLimitations,
}: PrintViewProps) {
    return (
        <div className="print-view" aria-hidden="true">
            <header className="print-header">
                <h2>Numra Analysebericht</h2>
            </header>
            <section className="print-summary">
                <h3>Zusammenfassung</h3>
                <p>{summary}</p>
            </section>
            {sections.map((section) => (
                <section key={section.section_id} className="print-section">
                    <h3>
                        {SECTION_UI_LABELS[section.section_id] ||
                            section.section_id}
                        {section.model_heading
                            ? ` — ${section.model_heading}`
                            : ""}
                    </h3>
                    {!section.applicable && (
                        <p className="print-na">
                            Dieser Abschnitt ist für dieses Profil nicht
                            anwendbar.
                        </p>
                    )}
                    {section.applicable && (
                        <>
                            {section.summary && (
                                <p className="print-section-summary">
                                    {section.summary}
                                </p>
                            )}
                            {section.claims?.map((claim, i) => (
                                <div
                                    key={claim.claim_id || i}
                                    className="print-claim"
                                >
                                    <p className="print-claim-text">
                                        {claim.text}
                                    </p>
                                    {claim.uncertainty && (
                                        <p className="print-uncertainty">
                                            ⚠ {claim.uncertainty}
                                        </p>
                                    )}
                                </div>
                            ))}
                            {section.counter_hypotheses?.map((h, i) => (
                                <p key={i} className="print-counter">
                                    ↔ {h}
                                </p>
                            ))}
                            {section.reflection_questions?.map((q, i) => (
                                <p key={i} className="print-question">
                                    ? {q}
                                </p>
                            ))}
                            {section.practical_options?.map((o, i) => (
                                <p key={i} className="print-option">
                                    → {o}
                                </p>
                            ))}
                            {section.limitations?.map((l, i) => (
                                <p key={i} className="print-limitation">
                                    ℹ {l}
                                </p>
                            ))}
                        </>
                    )}
                </section>
            ))}
            {globalLimitations.length > 0 && (
                <section className="print-global-limitations">
                    <h3>Wissenschaftliche Grenzen</h3>
                    {globalLimitations.map((lim, i) => (
                        <p key={i}>{lim}</p>
                    ))}
                </section>
            )}
        </div>
    );
}
