"""Load immutable bundled knowledge without network or runtime mutation.

V2 is the canonical/default bundle. V1 remains loadable for migration/import.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Literal, overload

from numerology_knowledge.models import KnowledgeBundle, KnowledgeBundleV2


@overload
def load_knowledge_bundle(locale: str = ..., version: Literal["v2"] = ...) -> KnowledgeBundleV2: ...


@overload
def load_knowledge_bundle(locale: str = ..., version: Literal["v1"] = ...) -> KnowledgeBundle: ...


@overload
def load_knowledge_bundle(
    locale: str = ..., version: str = ...
) -> KnowledgeBundleV2 | KnowledgeBundle: ...


@lru_cache(maxsize=4)
def load_knowledge_bundle(
    locale: str = "de", version: str = "v2"
) -> KnowledgeBundleV2 | KnowledgeBundle:
    """Load and validate a supported knowledge bundle from package data.

    V2 (default) returns :class:`KnowledgeBundleV2`; V1 returns the legacy
    :class:`KnowledgeBundle` for migration/import.
    """
    if locale != "de":
        raise ValueError(f"unsupported knowledge bundle locale: {locale!r}")
    if version == "v2":
        resource = files("numerology_knowledge").joinpath("data", "de-v2.json")
        return KnowledgeBundleV2.model_validate_json(resource.read_text(encoding="utf-8"))
    if version == "v1":
        resource = files("numerology_knowledge").joinpath("data", "de-v1.json")
        return KnowledgeBundle.model_validate_json(resource.read_text(encoding="utf-8"))
    raise ValueError(f"unsupported knowledge bundle version: {version!r}")
