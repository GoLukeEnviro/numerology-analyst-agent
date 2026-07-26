"""Rule-based interpretation and provenance tests."""

from __future__ import annotations

from datetime import date

import pytest

from numerology_domain.enums import ClaimType
from numerology_domain.models import MethodPolicy, PersonInput
from numerology_engine.profile import calculate_profile
from numerology_interpretation.service import compose_interpretation


@pytest.mark.unit
def test_interpretation_references_calculation_and_knowledge() -> None:
    profile = calculate_profile(
        PersonInput(
            core_name="Max Mustermann",
            birth_date=date(1985, 7, 25),
            as_of_date=date(2026, 7, 26),
        ),
        MethodPolicy(),
    )

    interpretation = compose_interpretation(profile)

    assert interpretation.knowledge_bundle == "numra-knowledge-de-v1"
    assert interpretation.calculation_hash == profile.deterministic_hash
    assert {section.subject for section in interpretation.sections} >= {
        "life_path",
        "expression",
        "personal_year",
    }
    assert all(
        claim.calculation_ref for section in interpretation.sections for claim in section.claims
    )
    assert all(
        claim.knowledge_ref for section in interpretation.sections for claim in section.claims
    )
    assert {
        claim.claim_type for section in interpretation.sections for claim in section.claims
    } <= {
        ClaimType.TRADITIONAL_CLAIM,
        ClaimType.INTERPRETIVE_HYPOTHESIS,
        ClaimType.PRACTICAL_SUGGESTION,
    }
