"""Load immutable bundled knowledge without network or runtime mutation."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from numerology_knowledge.models import KnowledgeBundle


@lru_cache(maxsize=4)
def load_knowledge_bundle(locale: str = "de", version: str = "v1") -> KnowledgeBundle:
    """Load and validate a supported knowledge bundle from package data."""
    if (locale, version) != ("de", "v1"):
        raise ValueError(f"unsupported knowledge bundle: locale={locale!r}, version={version!r}")
    resource = files("numerology_knowledge").joinpath("data", "de-v1.json")
    return KnowledgeBundle.model_validate_json(resource.read_text(encoding="utf-8"))
