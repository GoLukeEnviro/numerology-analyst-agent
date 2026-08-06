"""V2 meta information route for the Numra API.

Provides the capability contract independent of the V1 ``/api/v1/meta``
endpoint.  API capability and product rollout are separate axes:
``endpoint_method_version`` is always ``"v2"`` while
``product_default_method_version`` follows the actual rollout stage.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request

from numerology_api.dependencies import package_version
from numerology_api.http_models import LlmMeta, MetaResponseV2

router = APIRouter(tags=["meta-v2"])


@router.get("/api/v2/meta", response_model=MetaResponseV2)
async def meta_v2(request: Request) -> MetaResponseV2:
    settings = request.app.state.settings

    # rollout_stage and product_default_method_version will be updated
    # as the rollout progresses through waves 5B → 5C.
    rollout_stage: Literal["disabled", "opt_in", "canary", "default"]
    product_default: Literal["v1", "v2"]
    if getattr(settings, "v3_analysis_enabled", False):
        rollout_stage = "disabled"  # updated in 5B/5C
        product_default = "v1"  # updated in 5C
    else:
        rollout_stage = "disabled"
        product_default = "v1"

    return MetaResponseV2(
        endpoint_method_version="v2",
        supported_method_versions=("v2",),
        product_default_method_version=product_default,
        rollout_stage=rollout_stage,
        package_version=package_version(),
        supported_profile_schema_versions=("profile-calculation-result-v4",),
        supported_report_schema_versions=("analysis-report-v3",),
        supported_knowledge_bundles=("numra-knowledge-de-v3",),
        llm=LlmMeta(
            enabled=settings.llm_enabled,
            provider="deepseek" if settings.llm_enabled else None,
        ),
    )
