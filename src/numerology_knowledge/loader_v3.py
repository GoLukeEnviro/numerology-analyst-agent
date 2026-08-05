"""V3 knowledge loader — loads ``de-v3.json`` with explicit bundle selection.

The V3 loader is intentionally separate from the V1/V2 ``load_knowledge_bundle``
to prevent accidental cross-version contamination.  Bundle selection is explicit
(via ``bundle_id``), not inferred from profile schema version.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from numerology_knowledge.models_v3 import KnowledgeBundleV3


@lru_cache(maxsize=2)
def load_knowledge_bundle_v3(
    locale: str = "de",
    bundle_id: str = "numra-knowledge-de-v3",
) -> KnowledgeBundleV3:
    """Load and validate the V3 knowledge bundle from package data.

    Bundle selection is explicit — never inferred from profile schema version.
    """
    if locale != "de":
        raise ValueError(f"unsupported knowledge bundle locale: {locale!r}")
    if bundle_id != "numra-knowledge-de-v3":
        raise ValueError(f"unsupported V3 knowledge bundle: {bundle_id!r}")
    resource = files("numerology_knowledge").joinpath("data", "de-v3.json")
    return KnowledgeBundleV3.model_validate_json(resource.read_text(encoding="utf-8"))
