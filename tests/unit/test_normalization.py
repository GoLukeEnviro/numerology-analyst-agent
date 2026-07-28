"""Unit tests for the name normalization engine (ADR 0002 — de-direct-v1)."""

from __future__ import annotations

import pytest

from numerology_domain.enums import Locale, UmlautPolicy
from numerology_domain.exceptions import NormalizationError, PolicyError
from numerology_engine.normalization import normalize_name


class TestDeDirectV1:
    def test_plain_ascii_passes_through(self) -> None:
        calc, steps = normalize_name("Max")
        assert calc == "MAX"
        step_kinds = [s.step for s in steps]
        assert "unicode_nfc" in step_kinds
        assert "uppercase" in step_kinds

    def test_a_umlaut_replaced(self) -> None:
        calc, steps = normalize_name("Müller")
        assert calc == "MULLER"
        # The umlaut replacement must be audited.
        umlaut_steps = [s for s in steps if s.step == "umlaut_policy_de_direct_v1"]
        assert any(s.input == "ü" and s.output == "U" for s in umlaut_steps)

    @pytest.mark.parametrize("orig,expected", [("Ä", "A"), ("Ö", "O"), ("Ü", "U"), ("ß", "SS")])
    def test_each_umlaut_rule(self, orig: str, expected: str) -> None:
        calc, _ = normalize_name(orig)
        assert calc == expected

    def test_eszett_expands_to_two_chars(self) -> None:
        calc, _ = normalize_name("Straße")
        assert calc == "STRASSE"

    def test_accents_stripped(self) -> None:
        calc, _ = normalize_name("José")
        assert calc == "JOSE"
        calc2, _ = normalize_name("François")
        assert calc2 == "FRANCOIS"

    def test_nfc_normalizes_decomposed_input(self) -> None:
        # "Ä" as A + combining diaeresis (NFD form) must match the single-codepoint form.
        decomposed = "A\u0308"  # Ä decomposed
        single = "Ä"
        calc_dec, _ = normalize_name(decomposed)
        calc_single, _ = normalize_name(single)
        assert calc_dec == calc_single == "A"


class TestNormalizationErrors:
    def test_empty_name_rejected(self) -> None:
        with pytest.raises(NormalizationError):
            normalize_name("   ")

    def test_de_expanded_policy_now_active(self) -> None:
        """PR #19: de-expanded-v1 ist nun implementiert (kein PolicyError mehr)."""
        normalized, steps = normalize_name("Müller", umlaut_policy=UmlautPolicy.DE_EXPANDED_V1)
        assert "UE" in normalized  # ü → UE
        step_ids = [s.step for s in steps]
        assert "umlaut_policy_de_expanded_v1" in step_ids

    def test_non_german_locale_not_supported(self) -> None:
        with pytest.raises(PolicyError):
            normalize_name("Max", locale=Locale.EN)


class TestAuditTrailCompleteness:
    def test_every_step_recorded_in_order(self) -> None:
        _, steps = normalize_name("Müller")
        # Expected ordered steps: nfc -> umlaut (ü) -> accent_removal -> uppercase
        kinds = [s.step for s in steps]
        assert kinds[0] == "unicode_nfc"
        assert kinds[-1] == "uppercase"
        # Accent removal runs even when it is a no-op (recorded for completeness).
        assert "accent_removal" in kinds

    def test_original_preserved_by_caller_contract(self) -> None:
        # The function never mutates its input; the caller (PersonInput) keeps
        # the original. We assert the round-trip: same input ⇒ same output.
        calc_a, _ = normalize_name("Österreich")
        calc_b, _ = normalize_name("Österreich")
        assert calc_a == calc_b == "OSTERREICH"
