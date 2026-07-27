"""Rule-based interpretation composer for number relationships.

Each rule identifies a relationship between two (or more) profile numbers and
produces a non-judgmental observation — either ``"resonance"`` (reinforcing) or
``"tension"`` (contrasting). Rules NEVER diagnose, predict, or assign identity.

Rules are deterministic and side-effect free. They take profile facts and
return a list of :class:`ComposerObservation` instances that the interpretation
service can attach to claims via ``composer_rule_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from numerology_domain.models import ProfileCalculationResult

RelationType = Literal["resonance", "tension"]


@dataclass(frozen=True)
class ComposerObservation:
    """A non-judgmental relationship observation between profile numbers."""

    rule_id: str
    relation: RelationType
    number_a: int
    number_b: int
    context_a: str
    context_b: str
    description: str


def _name_numbers(profile: ProfileCalculationResult) -> list[tuple[str, int]]:
    """Extract (context, reduced_value) pairs from the profile."""
    pairs: list[tuple[str, int]] = [
        ("life_path", profile.life_path_a.reduced_value),
        ("birthday", profile.birthday.reduced_value),
        ("attitude", profile.attitude.reduced_value),
        ("personal_year", profile.cycles.personal_year.reduced_value),
    ]
    for names in (profile.core_name, profile.active_name):
        if names is None:
            continue
        pairs.extend(
            (
                (f"{names.basis}.expression", names.expression.reduced_value),
                (f"{names.basis}.soul_urge", names.soul_urge.reduced_value),
                (f"{names.basis}.personality", names.personality.reduced_value),
                (f"{names.basis}.maturity", names.maturity.reduced_value),
            )
        )
    return pairs


def _reinforcement(
    profile: ProfileCalculationResult,
) -> list[ComposerObservation]:
    """Same number appearing in multiple contexts reinforces a theme."""
    pairs = _name_numbers(profile)
    by_number: dict[int, list[tuple[str, int]]] = {}
    for context, number in pairs:
        by_number.setdefault(number, []).append((context, number))
    observations: list[ComposerObservation] = []
    for number, occurrences in by_number.items():
        if len(occurrences) >= 2:
            ctx_a, _ = occurrences[0]
            ctx_b, _ = occurrences[1]
            observations.append(
                ComposerObservation(
                    rule_id="reinforcement",
                    relation="resonance",
                    number_a=number,
                    number_b=number,
                    context_a=ctx_a,
                    context_b=ctx_b,
                    description=(
                        f"Der Wert {number} erscheint in mehreren Bereichen "
                        f"({ctx_a}, {ctx_b}) — dies kann ein wiederkehrendes Thema andeuten."
                    ),
                )
            )
    return observations


def _tension(
    profile: ProfileCalculationResult,
) -> list[ComposerObservation]:
    """Numbers with contrasting archetypal qualities may create productive tension."""
    pairs = _name_numbers(profile)
    # Pairs of numbers traditionally seen as contrasting (non-judgmental).
    contrast_pairs: dict[tuple[int, int], str] = {
        (1, 2): "Eigenständigkeit und Zusammenarbeit",
        (4, 5): "Stabilität und Wandel",
        (3, 4): "Ausdruck und Struktur",
        (7, 3): "Vertiefung und Äußerung",
        (8, 9): "Gestaltung und Loslassen",
    }
    observations: list[ComposerObservation] = []
    seen: set[frozenset[str]] = set()
    for i, (ctx_a, num_a) in enumerate(pairs):
        for ctx_b, num_b in pairs[i + 1 :]:
            key = frozenset({ctx_a, ctx_b})
            if key in seen:
                continue
            contrast = contrast_pairs.get((num_a, num_b)) or contrast_pairs.get((num_b, num_a))
            if contrast is not None:
                seen.add(key)
                observations.append(
                    ComposerObservation(
                        rule_id="tension",
                        relation="tension",
                        number_a=num_a,
                        number_b=num_b,
                        context_a=ctx_a,
                        context_b=ctx_b,
                        description=(
                            f"{ctx_a} ({num_a}) und {ctx_b} ({num_b}) könnten "
                            f"einander ergänzen: {contrast}."
                        ),
                    )
                )
    return observations


def _core_vs_active(
    profile: ProfileCalculationResult,
) -> list[ComposerObservation]:
    """Compare the core name and active name expression numbers."""
    core = profile.core_name
    active = profile.active_name
    if core is None or active is None:
        return []
    core_exp = core.expression.reduced_value
    active_exp = active.expression.reduced_value
    if core_exp == active_exp:
        return [
            ComposerObservation(
                rule_id="core_vs_active",
                relation="resonance",
                number_a=core_exp,
                number_b=active_exp,
                context_a="core.expression",
                context_b="active.expression",
                description=(
                    f"Kernname und aktiver Name teilen den Ausdruckswert {core_exp} — "
                    "dies kann eine innere Übereinstimmung andeuten."
                ),
            )
        ]
    return [
        ComposerObservation(
            rule_id="core_vs_active",
            relation="tension",
            number_a=core_exp,
            number_b=active_exp,
            context_a="core.expression",
            context_b="active.expression",
            description=(
                f"Kernname ({core_exp}) und aktiver Name ({active_exp}) unterscheiden "
                "sich im Ausdruck — dies kann eine spannende Entwicklungsbewegung anregen."
            ),
        )
    ]


def _maturity_alignment(
    profile: ProfileCalculationResult,
) -> list[ComposerObservation]:
    """The maturity number aligns with or complements the life path."""
    life_path = profile.life_path_a.reduced_value
    observations: list[ComposerObservation] = []
    for names in (profile.core_name, profile.active_name):
        if names is None:
            continue
        maturity = names.maturity.reduced_value
        if maturity == life_path:
            observations.append(
                ComposerObservation(
                    rule_id="maturity_alignment",
                    relation="resonance",
                    number_a=life_path,
                    number_b=maturity,
                    context_a="life_path",
                    context_b=f"{names.basis}.maturity",
                    description=(
                        f"Lebensweg ({life_path}) und Reifezahl ({maturity}) stimmen überein "
                        "— dies kann eine klare Entwicklungsrichtung andeuten."
                    ),
                )
            )
    return observations


def compose_observations(profile: ProfileCalculationResult) -> list[ComposerObservation]:
    """Run all composer rules and return observations."""
    observations: list[ComposerObservation] = []
    observations.extend(_reinforcement(profile))
    observations.extend(_tension(profile))
    observations.extend(_core_vs_active(profile))
    observations.extend(_maturity_alignment(profile))
    return observations
