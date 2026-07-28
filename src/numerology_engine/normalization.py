"""Name normalization engine (ADR 0002 - policy ``de-direct-v1``).

Two layers are kept strictly separate, as the ADR demands:

* **Layer A - Unicode NFC**: a *technical* canonicalization. ``"Ä"`` encoded
  as a single codepoint (U+00C4) and as ``"A" + combining diaeresis`` must
  become byte-identical.
* **Layer B - semantic policy**: ``de-direct-v1`` replaces Ä→A, Ö→O, Ü→U,
  ß→SS and strips diacritical accents (é→e, ñ→n, ç→c). This is *not* what
  NFC does - confusing the two is the implementation error ADR 0002 warns
  about.

The original name is never overwritten: callers receive a
``calculation_name`` plus the ordered :class:`NormalizationStep` audit
trail. The Walking Skeleton computes the ``calculation_name`` as a
reusable foundation, even though Life Path A/B does not consume it yet.
"""

from __future__ import annotations

import unicodedata

from numerology_domain.enums import Locale, UmlautPolicy
from numerology_domain.exceptions import NormalizationError, PolicyError
from numerology_domain.models import NormalizationStep

# de-direct-v1 replacement table (ADR 0002 §4). Applied AFTER NFC so that
# both single-codepoint and decomposed umlauts resolve identically. Both the
# upper- and lower-case forms are mapped; the output is the upper-case base
# letter because the calculation name is upper-cased anyway (next step), and
# ADR 0002 lists the canonical upper-case targets. ß → SS expands to two chars.
_DE_DIRECT_MAP: dict[str, str] = {
    "Ä": "A",
    "Ö": "O",
    "Ü": "U",
    "ß": "SS",
    "ä": "A",
    "ö": "O",
    "ü": "U",
}

# de-expanded-v1 replacement table (PR #19).
# Umlauts are expanded phonetically: Ä→AE, Ö→OE, Ü→UE, ß→SS.
# Accents are stripped transparently afterwards (same as de-direct-v1).
# The two policies MUST NEVER be mixed in one calculation (ADR 0002 §7).
_DE_EXPANDED_MAP: dict[str, str] = {
    "Ä": "AE",
    "Ö": "OE",
    "Ü": "UE",
    "ß": "SS",
    "ä": "AE",
    "ö": "OE",
    "ü": "UE",
}

# Combining diacritical marks range stripped after NFD decomposition
# (ADR 0002 §5). Covers common Latin combining marks.
_COMBINING_RANGE_START = 0x0300
_COMBINING_RANGE_END = 0x0362


def _to_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _strip_accents(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(
        ch for ch in nfd if not (_COMBINING_RANGE_START <= ord(ch) <= _COMBINING_RANGE_END)
    )


def _apply_de_direct(text: str) -> tuple[str, list[NormalizationStep]]:
    """Apply the de-direct-v1 umlaut table, recording each transformation."""
    steps: list[NormalizationStep] = []
    # NFC guarantees single-codepoint umlauts, so a direct per-char scan is
    # deterministic and order-preserving. ß → SS expands one char into two.
    out_chars: list[str] = []
    for idx, ch in enumerate(text):
        if ch in _DE_DIRECT_MAP:
            replacement = _DE_DIRECT_MAP[ch]
            steps.append(
                NormalizationStep(
                    step="umlaut_policy_de_direct_v1",
                    input=ch,
                    output=replacement,
                    note=f"position={idx}",
                )
            )
            out_chars.append(replacement)
        else:
            out_chars.append(ch)
    return "".join(out_chars), steps


def _apply_de_expanded(text: str) -> tuple[str, list[NormalizationStep]]:
    """Apply the de-expanded-v1 umlaut table (PR #19).

    Ä→AE, Ö→OE, Ü→UE, ß→SS.  Accents are stripped in the subsequent step
    (shared with de-direct-v1).  Mixed use of the two policies is forbidden
    (ADR 0002 §7).
    """
    steps: list[NormalizationStep] = []
    out_chars: list[str] = []
    for idx, ch in enumerate(text):
        if ch in _DE_EXPANDED_MAP:
            replacement = _DE_EXPANDED_MAP[ch]
            steps.append(
                NormalizationStep(
                    step="umlaut_policy_de_expanded_v1",
                    input=ch,
                    output=replacement,
                    note=f"position={idx}",
                )
            )
            out_chars.append(replacement)
        else:
            out_chars.append(ch)
    return "".join(out_chars), steps


def normalize_name(
    original: str,
    *,
    umlaut_policy: UmlautPolicy = UmlautPolicy.DE_DIRECT_V1,
    locale: Locale = Locale.DE,
) -> tuple[str, tuple[NormalizationStep, ...]]:
    """Normalize a name to its pythagorean ``calculation_name``.

    Returns the ``calculation_name`` and the ordered normalization audit
    trail. The original name is preserved by the caller (``PersonInput``).

    Supported policies: ``de-direct-v1`` (Ä→A, Ö→O, Ü→U) and
    ``de-expanded-v1`` (Ä→AE, Ö→OE, Ü→UE). Mixing them is forbidden
    (ADR 0002 §7). PR #19 activates ``de-expanded-v1``.

    Raises :class:`PolicyError` for an unsupported policy/locale mix, and
    :class:`NormalizationError` for empty input.
    """
    if original is None or not original.strip():
        raise NormalizationError("cannot normalize an empty name")

    if locale is not Locale.DE:
        # Only de is implemented in 0.1.0. Other locales are extension points.
        raise PolicyError(f"locale {locale.value!r} has no normalization policy in 0.1.0; use 'de'")

    audit: list[NormalizationStep] = []

    # Step 1 - NFC (technical canonicalization).
    nfc = _to_nfc(original)
    audit.append(
        NormalizationStep(
            step="unicode_nfc",
            input=original,
            output=nfc,
            note="identical" if nfc == original else "re-composed",
        )
    )

    # Step 2 - umlaut policy replacement (semantic, layer B).
    if umlaut_policy is UmlautPolicy.DE_EXPANDED_V1:
        after_umlaut, umlaut_steps = _apply_de_expanded(nfc)
    else:
        # DE_DIRECT_V1 is the default and the only other supported policy.
        after_umlaut, umlaut_steps = _apply_de_direct(nfc)
    audit.extend(umlaut_steps)

    # Step 3 - accent stripping (separate operation from the umlaut policy).
    after_accents = _strip_accents(after_umlaut)
    audit.append(
        NormalizationStep(
            step="accent_removal",
            input=after_umlaut,
            output=after_accents,
            note="no accents" if after_accents == after_umlaut else "diacritics stripped",
        )
    )

    # Step 4 - uppercase for the calculation alphabet (A-Z). Spaces and
    # hyphens are preserved as separators (ADR 0003 §2: they carry no
    # numeric value but keep structural information).
    calculation_name = after_accents.upper()
    audit.append(
        NormalizationStep(
            step="uppercase",
            input=after_accents,
            output=calculation_name,
            note="A-Z pythagorean base",
        )
    )

    return calculation_name, tuple(audit)
