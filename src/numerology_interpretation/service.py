"""Compose deterministic interpretations from profile facts and bundled knowledge."""

from __future__ import annotations

from numerology_domain.enums import ClaimType
from numerology_domain.models import ProfileCalculationResult
from numerology_interpretation.models import (
    ComposerObservationRecord,
    InterpretationClaim,
    InterpretationResult,
    InterpretationSection,
)
from numerology_interpretation.rules import ComposerObservation, compose_observations
from numerology_knowledge.loader import load_knowledge_bundle
from numerology_knowledge.models import KnowledgeBundleV2, KnowledgeEntryV2, ResultContext
from numerology_safety.validation import assert_claims_safe

# Mapping from subject name suffix to ResultContext for context-sensitive lookup.
_SUFFIX_TO_CONTEXT: dict[str, ResultContext] = {
    "expression": "expression",
    "soul_urge": "soul_urge",
    "personality": "personality",
    "maturity": "maturity",
}

_DIRECT_CONTEXT: dict[str, ResultContext] = {
    "life_path": "life_path",
    "birthday": "birthday",
    "attitude": "attitude",
    "personal_year": "personal_year",
}


def _subject_to_result_context(subject: str) -> ResultContext | None:
    """Derive a ResultContext from a subject string."""
    if subject in _DIRECT_CONTEXT:
        return _DIRECT_CONTEXT[subject]
    # Name-based subjects like "core_expression", "active_soul_urge".
    for suffix, ctx in _SUFFIX_TO_CONTEXT.items():
        if subject.endswith(f"_{suffix}"):
            return ctx
    return None


def _entry_for_context(
    bundle: KnowledgeBundleV2, number: int, context: ResultContext | None
) -> KnowledgeEntryV2:
    """Context-sensitive entry lookup with graceful fallback to number-only."""
    if context is not None:
        try:
            return bundle.entry_for(number, context=context)
        except ValueError:
            pass
    return bundle.entry_for(number)


def _obs_context_to_result_context(ctx: str) -> ResultContext | None:
    """Convert a ComposerObservation context string to a ResultContext.

    Observation contexts use dot-notation for name-based values (e.g.
    ``"core.expression"``) while ResultContext uses the bare suffix.
    """
    if "." in ctx:
        suffix = ctx.split(".")[-1]
        return _SUFFIX_TO_CONTEXT.get(suffix)
    return _DIRECT_CONTEXT.get(ctx)


def _build_observation_record(
    obs: ComposerObservation,
    bundle: KnowledgeBundleV2,
) -> ComposerObservationRecord:
    ctx_a = _obs_context_to_result_context(obs.context_a)
    ctx_b = _obs_context_to_result_context(obs.context_b)
    entry_a = _entry_for_context(bundle, obs.number_a, ctx_a)
    entry_b = _entry_for_context(bundle, obs.number_b, ctx_b)
    # Use first counter_hypothesis as a representative cross-reference.
    ch_a = entry_a.counter_hypotheses[0] if entry_a.counter_hypotheses else None
    return ComposerObservationRecord(
        composer_rule_id=obs.rule_id,
        relation=obs.relation,
        calculation_refs=(obs.context_a, obs.context_b),
        knowledge_refs=(entry_a.stable_id, entry_b.stable_id),
        uncertainty=entry_a.uncertainty,
        counter_hypothesis=ch_a,
        description=obs.description,
    )


def compose_interpretation(profile: ProfileCalculationResult) -> InterpretationResult:
    """Resolve selected profile values without generating or changing calculations."""
    bundle = load_knowledge_bundle(profile.input_ref.locale.value, "v2")
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
        context = _subject_to_result_context(subject)
        entry = _entry_for_context(bundle, number, context)
        knowledge_ref = entry.stable_id
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

    # Composer observations: relationship analysis across profile numbers.
    raw_observations = compose_observations(profile)
    observation_records = tuple(_build_observation_record(obs, bundle) for obs in raw_observations)

    return InterpretationResult(
        knowledge_bundle=bundle.bundle_id,
        calculation_hash=profile.deterministic_hash,
        scientific_position=bundle.scientific_position,
        sections=tuple(sections),
        observations=observation_records,
    )
