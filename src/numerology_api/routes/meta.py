"""Meta information route for the Numra API."""

from __future__ import annotations

from fastapi import APIRouter, Request

from numerology_api.dependencies import package_version
from numerology_api.http_models import MetaResponse
from numerology_domain.models import PROFILE_CALCULATION_RESULT_SCHEMA_VERSION
from numerology_knowledge.loader import load_knowledge_bundle

router = APIRouter(tags=["meta"])


@router.get("/api/v1/meta", response_model=MetaResponse)
async def meta(request: Request) -> MetaResponse:
    settings = request.app.state.settings
    return MetaResponse(
        package_version=package_version(),
        profile_schema_version=PROFILE_CALCULATION_RESULT_SCHEMA_VERSION,
        knowledge_bundle=load_knowledge_bundle().bundle_id,
        llm={
            "enabled": settings.llm_enabled,
            "provider": "deepseek" if settings.llm_enabled else None,
        },
    )
