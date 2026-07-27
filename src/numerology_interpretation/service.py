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
    values = (
        ("life_path", profile.life_path_a.reduced_value, "life_path_a"),
        ("birthday", profile.birthday.reduced_value, "birthday"),
        ("attitude", profile.attitude.reduced_value, "attitude"),
        ("expression", profile.core_name.expression.reduced_value, "core_name.expression"),
        ("soul_urge", profile.core_name.soul_urge.reduced_value, "core_name.soul_urge"),
        ("personality", profile.core_name.personality.reduced_value, "core_name.personality"),
        ("maturity", profile.maturity.reduced_value, "maturity"),
        ("personal_year", profile.cycles.personal_year.reduced_value, "cycles.personal_year"),
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
