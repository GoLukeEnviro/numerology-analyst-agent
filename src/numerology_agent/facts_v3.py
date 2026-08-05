"""V3 fact package builders — request-scoped, never persisted.

Extracts structured ``AnalysisFactEntryV3`` entries from a
``ProfileCalculationResultV4`` and derives the minimised
``ProviderFactPackageV3`` for the DeepSeek provider.
"""

from __future__ import annotations

from numerology_agent.models_v3 import (
    AnalysisFactEntryV3,
    AnalysisFactPackageV3,
    ProviderFactPackageV3,
)
from numerology_domain.models import ProfileCalculationResultV4


def build_analysis_fact_package_v3(
    profile: ProfileCalculationResultV4,
) -> AnalysisFactPackageV3:
    """Extract every deterministic calculation fact from a V4 profile.

    The returned package is request-scoped: it lives only for the duration
    of the current HTTP request and is never logged or persisted.
    """
    entries: list[AnalysisFactEntryV3] = []

    # --- Life paths (primary and secondary kept separate) ---
    for role, lp in (
        ("primary", profile.life_path_primary),
        ("secondary", profile.life_path_secondary),
    ):
        entries.append(
            AnalysisFactEntryV3(
                calculation_ref=f"life_path_{role}",
                result_context=f"life_path_{role}",
                role=role,  # type: ignore[arg-type]
                raw_total=lp.raw_total,
                reduction_chain=tuple(lp.reduction_chain),
                root_value=lp.root_value,
                held_master_value=lp.held_master_value,
                display_notation=lp.display_notation,
                is_master=lp.is_master,
                compound_classification=lp.compound_classification,
                karmic_occurrences=tuple(lp.karmic_occurrences),
                components=lp.components,
            )
        )

    # --- Single-value numbers ---
    _add_number_entry(entries, profile.birthday, "birthday")
    _add_number_entry(entries, profile.attitude, "attitude")
    _add_number_entry(entries, profile.maturity, "maturity")

    # --- Name-based numbers (core_name always present) ---
    if profile.core_name is not None:
        cn = profile.core_name
        _add_number_entry(entries, cn.expression, "expression")
        _add_number_entry(entries, cn.soul_urge, "soul_urge")
        _add_number_entry(entries, cn.personality, "personality")

    # --- Cycles ---
    for key, ctx in (
        ("personal_year", "personal_year"),
        ("personal_month", "personal_month"),
        ("personal_day", "personal_day"),
    ):
        nm = getattr(profile.cycles, key, None)
        if nm is not None:
            _add_number_entry(entries, nm, ctx)

    # --- Pinnacles ---
    for i, pn in enumerate(profile.pinnacles, start=1):
        _add_number_entry(entries, pn, f"pinnacle_{i}")

    # --- Challenges (root values only — no NumberModel) ---
    from numerology_domain.models import NumberResult

    for i, ch in enumerate(profile.challenges, start=1):
        if isinstance(ch, NumberResult):
            entries.append(
                AnalysisFactEntryV3(
                    calculation_ref=f"challenge_{i}",
                    result_context="challenge",
                    role="primary",
                    raw_total=ch._raw_total if hasattr(ch, "_raw_total") else ch.reduced_value,
                    reduction_chain=(),
                    root_value=ch.reduced_value,
                    display_notation=str(ch.reduced_value),
                    calculation_method="pinnacles_challenges_root",
                    method_version="v2",
                )
            )
        else:
            entries.append(
                AnalysisFactEntryV3(
                    calculation_ref=f"challenge_{i}",
                    result_context="challenge",
                    role="primary",
                    raw_total=ch,
                    reduction_chain=(),
                    root_value=ch,
                    display_notation=str(ch),
                    calculation_method="pinnacles_challenges_root",
                    method_version="v2",
                )
            )

    return AnalysisFactPackageV3(
        calculation_hash=profile.deterministic_hash,
        profile_schema_version=profile.schema_version,
        method_version="v2",
        entries=tuple(entries),
    )


def _add_number_entry(
    entries: list[AnalysisFactEntryV3],
    nm: object,
    context: str,
    role: str = "primary",
) -> None:
    """Add a fact entry from a NumberModel or NumberResult."""
    raw = getattr(nm, "raw_total", 0)
    chain = tuple(getattr(nm, "reduction_chain", ()))
    root = getattr(nm, "root_value", getattr(nm, "reduced_value", 0))
    held = getattr(nm, "held_master_value", None)
    notation = getattr(nm, "display_notation", str(root))
    is_m = getattr(nm, "is_master", False)
    cc = getattr(nm, "compound_classification", None)
    ko = tuple(getattr(nm, "karmic_occurrences", ()))
    cm = ""
    mv = "v2"
    comps = tuple(getattr(nm, "components", ()))

    entries.append(
        AnalysisFactEntryV3(
            calculation_ref=context,
            result_context=context,
            role=role,  # type: ignore[arg-type]
            raw_total=raw,
            reduction_chain=chain,
            root_value=root,
            held_master_value=held,
            display_notation=notation,
            is_master=is_m,
            compound_classification=cc,
            karmic_occurrences=ko,
            calculation_method=cm,
            method_version=mv,
            components=comps,
        )
    )


def derive_provider_fact_package_v3(
    package: AnalysisFactPackageV3,
) -> ProviderFactPackageV3:
    """Derive a minimised, closed-book fact package for the DeepSeek provider.

    Full names, letter chains, technical traces and audit metadata are
    excluded.  ``trace_ref`` is reduced to an opaque identifier.
    """
    entries: list[dict[str, object]] = []
    for entry in package.entries:
        entries.append(
            {
                "ref": entry.calculation_ref,
                "context": entry.result_context,
                "role": entry.role,
                "notation": entry.display_notation,
                "root": entry.root_value,
                "master": entry.held_master_value,
                "is_master": entry.is_master,
                "classification": entry.compound_classification,
            }
        )
    return ProviderFactPackageV3(
        calculation_hash=package.calculation_hash,
        method_version=package.method_version,
        entries=tuple(entries),
    )
