"""V3 interpretation service for ProfileCalculationResultV4.

Parallel to ``service.py`` (V1/V3 profiles).  Uses V4-specific ``NumberModel``
fields (not ``.reduced_value``) and loads ``de-v3.json``.
"""

from __future__ import annotations

from numerology_domain.enums import ClaimType
from numerology_domain.models import ProfileCalculationResultV4
from numerology_interpretation.models import (
    InterpretationClaim,
    InterpretationResult,
    InterpretationSection,
)
from numerology_knowledge.loader_v3 import load_knowledge_bundle_v3
from numerology_knowledge.models_v3 import KnowledgeBundleV3, KnowledgeEntryV3, ResultContextV3
from numerology_safety.validation import assert_claims_safe


def _make_claim(
    entry: KnowledgeEntryV3,
    calculation_ref: str,
    knowledge_ref: str,
    claim_index: int = 0,
) -> InterpretationClaim:
    text = entry.traditional_claims[claim_index] if entry.traditional_claims else entry.title
    return InterpretationClaim(
        claim_type=ClaimType.TRADITIONAL_CLAIM,
        text=text,
        calculation_ref=calculation_ref,
        knowledge_ref=knowledge_ref,
        composer_rule_id=None,
    )


def compose_interpretation_for_profile_v4(
    profile: ProfileCalculationResultV4,
) -> InterpretationResult:
    """Build a structured interpretation from a V4 profile using V3 knowledge.

    Reads ``is_master``, ``compound_classification``, ``held_master_value``
    and other ``NumberModel`` fields directly — never uses the flat
    ``.reduced_value`` of the V1 era.
    """
    bundle = load_knowledge_bundle_v3()
    sections: list[InterpretationSection] = []

    # --- Life paths (kept separate: primary and secondary) ---
    sections.extend(
        _section_for_number_model(
            bundle,
            profile.life_path_primary,
            calculation_ref="life_path_primary",
            context="life_path_primary",
            subject="Lebensweg (primär)",
        )
    )
    sections.extend(
        _section_for_number_model(
            bundle,
            profile.life_path_secondary,
            calculation_ref="life_path_secondary",
            context="life_path_secondary",
            subject="Lebensweg (sekundär)",
        )
    )

    # --- Single-value numbers ---
    sections.extend(
        _section_for_number_model(bundle, profile.birthday, "birthday", "birthday", "Geburtstag")
    )
    sections.extend(
        _section_for_number_model(
            bundle, profile.attitude, "attitude", "attitude", "Einstellung"
        )
    )
    sections.extend(
        _section_for_number_model(bundle, profile.maturity, "maturity", "maturity", "Reife")
    )

    # --- Name-based numbers ---
    if profile.core_name is not None:
        cn = profile.core_name
        sections.extend(
            _section_for_number_model(
                bundle, cn.expression, "expression", "expression", "Ausdruck"
            )
        )
        sections.extend(
            _section_for_number_model(
                bundle, cn.soul_urge, "soul_urge", "soul_urge", "Seelenstreben"
            )
        )
        sections.extend(
            _section_for_number_model(
                bundle, cn.personality, "personality", "personality", "Persönlichkeit"
            )
        )

    # --- Cycles ---
    for key, ctx, label in (
        ("personal_year", "personal_year", "Persönliches Jahr"),
        ("personal_month", "personal_month", "Persönlicher Monat"),
        ("personal_day", "personal_day", "Persönlicher Tag"),
    ):
        nm = getattr(profile.cycles, key, None)
        if nm is not None:
            sections.extend(
                _section_for_number_model(bundle, nm, key, ctx, label)  # type: ignore[arg-type]
            )

    # --- Pinnacles ---
    for i, pn in enumerate(profile.pinnacles, start=1):
        sections.extend(
            _section_for_number_model(
                bundle, pn, f"pinnacle_{i}", "pinnacle", f"Pinnacle {i}"
            )
        )

    # Collect claims and validate
    all_claims: list[InterpretationClaim] = []
    for section in sections:
        all_claims.extend(section.claims)
    assert_claims_safe(tuple(all_claims))

    return InterpretationResult(sections=tuple(sections))


def _section_for_number_model(
    bundle: KnowledgeBundleV3,
    nm: object,
    calculation_ref: str,
    context: ResultContextV3,
    subject: str,
) -> list[InterpretationSection]:
    """Create interpretation sections for a single NumberModel."""
    sections: list[InterpretationSection] = []
    root = getattr(nm, "root_value", getattr(nm, "reduced_value", None))
    classification = _to_entry_classification(nm)

    if root is None:
        return sections

    try:
        entry = bundle.entry_for(root, classification=classification, context=context)
    except ValueError:
        # If context-specific lookup fails, try without context.
        try:
            entry = bundle.entry_for(root, classification=classification)
        except ValueError:
            # Fallback: number-only lookup.
            try:
                entry = bundle.entry_for(root)
            except ValueError:
                return sections

    claims: list[InterpretationClaim] = []
    for i in range(min(len(entry.traditional_claims), 3)):
        claims.append(_make_claim(entry, calculation_ref, entry.stable_id, i))

    sections.append(
        InterpretationSection(
            subject=subject,
            number=root,
            title=entry.title,
            claims=tuple(claims),
            counter_hypotheses=entry.counter_hypotheses,
            knowledge_refs=entry.source_refs,
        )
    )
    return sections


def _to_entry_classification(nm: object) -> str | None:
    """Map NumberModel fields to EntryClassification."""
    is_m = getattr(nm, "is_master", False)
    cc = getattr(nm, "compound_classification", None)
    ko = getattr(nm, "karmic_occurrences", ())

    if is_m:
        return "master"
    if ko and len(ko) > 0:
        return "karmic_debt"
    if cc == "compound" or (getattr(nm, "raw_total", 0) >= 10):
        return "compound"
    return "single"
