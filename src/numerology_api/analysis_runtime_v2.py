"""V2 analysis runtime — server-side profile re-validation for /api/v2/analyses/*.

Mirrors ``analysis_runtime.py`` for the V1 path but uses the existing
``calculate_profile_v2`` engine.  The re-validated canonical profile
prevents clients from submitting a falsified ``ProfileCalculationResultV4``
to manipulate the agent.
"""

from __future__ import annotations

from numerology_domain.models import ProfileCalculationResultV4
from numerology_engine.profile_v2 import calculate_profile_v2


def canonical_analysis_profile_v2(
    profile: ProfileCalculationResultV4,
) -> ProfileCalculationResultV4 | None:
    """Re-calculate the canonical V4 profile and verify the submitted one matches.

    Returns the canonical profile if it matches byte-for-byte, or ``None``
    if the submitted profile does not match the canonical calculation.
    """
    canonical = calculate_profile_v2(profile.input_ref, profile.policy)
    if profile != canonical:
        return None
    return canonical
