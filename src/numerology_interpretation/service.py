"""Compose deterministic interpretations from profile facts and bundled knowledge."""

from __future__ import annotations

from numerology_domain.enums import ClaimType
from numerology_domain.models import ProfileCalculationResult
from numerology_interpretation.models import (
    InterpretationClaim,
    InterpretationResult,
    InterpretationSection,
)
from numerology_knowledge.loader import load_knowledge_bundle
from numerology_safety.validation import assert_claims_safe


def compose_interpretation(profile: ProfileCalculationResult) -> InterpretationResult:
    """Resolve selected profile values without generating or changing calculations."""
    bundle = load_knowledge_bundle(profile.input_ref.locale.value, "v1")
    name_profiles = tuple(
        names for names in (profile.core_name, profile.active_name) if names is not None
    )
    if not name_profiles:
        raise ValueError("profile contains no selected name profile")
    values = [
        ("life_path", profile.life_path_a.reduced_value, "life_path_a"),
        ("birthday", profile.birthday.reduced_value, "birthday"),
        ("attitude", profile.attitude.reduced_value, "attitude"),
        ("personal_year", profile.cycles.personal_year.reduced_value, "cycles.personal_year"),
    ]
    for names in name_profiles:
        values.extend(
            (
                (
                    f"{names.basis}_expression",
                    names.expression.reduced_value,
                    f"{names.basis}.expression",
                ),
                (
                    f"{names.basis}_soul_urge",
                    names.soul_urge.reduced_value,
                    f"{names.basis}.soul_urge",
                ),
                (
                    f"{names.basis}_personality",
                    names.personality.reduced_value,
                    f"{names.basis}.personality",
                ),
                (
                    f"{names.basis}_maturity",
                    names.maturity.reduced_value,
                    f"{names.basis}.maturity",
                ),
            )
        )
    sections: list[InterpretationSection] = []
    for subject, number, calculation_ref in values:
        entry = bundle.entry_for(number)
        knowledge_ref = f"{bundle.bundle_id}:number:{number}"
        claims = (
            InterpretationClaim(
                claim_type=ClaimType.TRADITIONAL_CLAIM,
                text=entry.traditional_claims[0],
                calculation_ref=calculation_ref,
                knowledge_ref=knowledge_ref,
            ),
            InterpretationClaim(
                claim_type=ClaimType.INTERPRETIVE_HYPOTHESIS,
                text=entry.reflection_prompts[0],
                calculation_ref=calculation_ref,
                knowledge_ref=knowledge_ref,
            ),
            InterpretationClaim(
                claim_type=ClaimType.PRACTICAL_SUGGESTION,
                text=entry.practical_suggestions[0],
                calculation_ref=calculation_ref,
                knowledge_ref=knowledge_ref,
            ),
        )
        assert_claims_safe(claims)
        sections.append(
            InterpretationSection(
                subject=subject,
                number=number,
                title=entry.title,
                claims=claims,
                counter_hypotheses=entry.counter_hypotheses,
            )
        )
    return InterpretationResult(
        knowledge_bundle=bundle.bundle_id,
        calculation_hash=profile.deterministic_hash,
        scientific_position=bundle.scientific_position,
        sections=tuple(sections),
    )
