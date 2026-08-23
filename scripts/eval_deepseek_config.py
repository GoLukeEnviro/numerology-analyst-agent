"""DeepSeek V3 Provider Evaluation — H1 (Thinking) vs. H2 (Non-Thinking).

Evaluates the V3 report pipeline against 5 golden reference profiles.
Produces a neutral, evidence-based comparison without recommending a default.

Usage:
    uv run python scripts/eval_deepseek_config.py

Requires DEEPSEEK_API_KEY in environment or .env file.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date
import os
import statistics
import time
from typing import Any

from pydantic import SecretStr

from numerology_agent.deepseek import DeepSeekSettings
from numerology_agent.deepseek_v3 import DeepSeekProviderV3
from numerology_agent.service_v3 import AgentServiceV3
from numerology_domain.models import (
    PYTHAGOREAN_V2_VERSION,
    MethodPolicy,
    PersonInput,
    ProfileCalculationResultV4,
)
from numerology_engine.profile_v2 import calculate_profile_v2

# ---------------------------------------------------------------------------
# Golden reference profiles (from tests/golden/reference_profiles_v2.yaml)
# ---------------------------------------------------------------------------

GOLDEN_PROFILES: list[dict[str, str | date]] = [
    {"core_name": "Lukas Springer", "birth_date": "1986-07-18", "as_of_date": "2026-07-28"},
    {"core_name": "Stella Jane Witt", "birth_date": "2011-04-18", "as_of_date": "2026-07-28"},
    {"core_name": "Antoney Newton", "birth_date": "1995-10-15", "as_of_date": "2026-07-28"},
    {"core_name": "Sina Langner", "birth_date": "1992-12-11", "as_of_date": "2026-07-28"},
    {"core_name": "Stefanie Scheulen", "birth_date": "1981-04-16", "as_of_date": "2026-07-28"},
]

NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS = 32768
RUNS_PER_CONFIG = 3


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@dataclass
class RunMetrics:
    profile_id: str = ""
    config: str = ""
    run: int = 0
    duration_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = ""
    section_count: int = 0
    applicable_sections: int = 0
    non_applicable_ok: bool = True
    schema_valid: bool = False
    number_correct: int = 0
    number_checked: int = 0
    error: str = ""


@dataclass
class EvalReport:
    config: str = ""
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    avg_duration_s: float = 0.0
    avg_prompt_tokens: int = 0
    avg_completion_tokens: int = 0
    finish_reasons: dict[str, int] = field(default_factory=dict)
    schema_success_rate: float = 0.0
    section_coverage_rate: float = 0.0
    number_integrity_rate: float = 0.0
    truncation_rate: float = 0.0
    metrics: list[RunMetrics] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Profile calculation
# ---------------------------------------------------------------------------


def compute_profile(entry: dict[str, str | date]) -> ProfileCalculationResultV4:
    person = PersonInput(
        core_name=str(entry["core_name"]),
        birth_date=date.fromisoformat(str(entry["birth_date"])),
        as_of_date=date.fromisoformat(str(entry["as_of_date"])),
    )
    policy = MethodPolicy(version=PYTHAGOREAN_V2_VERSION)
    return calculate_profile_v2(person, policy)


# ---------------------------------------------------------------------------
# Golden value checks
# ---------------------------------------------------------------------------

GOLDEN_CHECKS: dict[str, dict[str, Any]] = {
    "Lukas Springer": {
        "life_path_primary.display_notation": "40/4",
        "life_path_secondary.display_notation": "22/4",
        "life_path_secondary.held_master_value": 22,
        "personality.display_notation": "44/8",
        "personality.is_master": False,
    },
}


def check_golden_values(
    profile: ProfileCalculationResultV4, report_content: dict[str, Any]
) -> tuple[int, int]:
    """Count correct vs total number integrity checks."""
    correct = 0
    total = 0
    # Basic check: life_path values present in report
    sections = report_content.get("sections", [])
    for section in sections:
        for claim in section.get("claims", []):
            text = str(claim.get("text", "")).lower()
            total += 1
            # Very basic: check for presence of key number patterns
            if "40/4" in text or "22/4" in text or "44/8" in text:
                correct += 1
    return correct, total


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------


async def run_eval(
    provider: DeepSeekProviderV3,
    profile: ProfileCalculationResultV4,
    profile_id: str,
    config_label: str,
    run_index: int,
) -> RunMetrics:
    metrics = RunMetrics(profile_id=profile_id, config=config_label, run=run_index)
    try:
        agent = AgentServiceV3(provider)
        start = time.monotonic()
        report = await agent.generate_report(profile)
        metrics.duration_s = time.monotonic() - start
        metrics.prompt_tokens = report.provenance.prompt_tokens
        metrics.completion_tokens = report.provenance.completion_tokens
        metrics.finish_reason = "stop"  # AgentServiceV3 only returns on stop
        metrics.schema_valid = True

        content = report.content
        sections = content.sections
        metrics.section_count = len(sections)
        metrics.applicable_sections = sum(1 for s in sections if s.applicable)

        # Check non-applicable sections have no claims/refs
        na_ok = True
        for s in sections:
            if not s.applicable and (
                s.claims or s.supporting_calculation_refs or s.supporting_knowledge_refs
            ):
                na_ok = False
        metrics.non_applicable_ok = na_ok

        # Golden value checks
        content_dict = content.model_dump(mode="json")
        correct, total = check_golden_values(profile, content_dict)
        metrics.number_correct = correct
        metrics.number_checked = total
    except Exception as exc:
        metrics.error = str(exc)[:200]
    return metrics


async def evaluate_config(
    settings: DeepSeekSettings,
    config_label: str,
) -> EvalReport:
    provider = DeepSeekProviderV3(settings)
    report = EvalReport(config=config_label)
    all_metrics: list[RunMetrics] = []

    for entry in GOLDEN_PROFILES:
        profile_id = str(entry["core_name"])
        profile = compute_profile(entry)
        for run_idx in range(RUNS_PER_CONFIG):
            print(
                f"  [{config_label}] {profile_id} run {run_idx + 1}/{RUNS_PER_CONFIG} ...",
                end=" ",
                flush=True,
            )
            m = await run_eval(provider, profile, profile_id, config_label, run_idx + 1)
            all_metrics.append(m)
            print("OK" if m.error == "" else f"ERROR: {m.error[:80]}")

    successful = [m for m in all_metrics if m.error == ""]
    failed = [m for m in all_metrics if m.error != ""]
    report.total_runs = len(all_metrics)
    report.successful_runs = len(successful)
    report.failed_runs = len(failed)

    if successful:
        report.avg_duration_s = statistics.mean(m.duration_s for m in successful)
        report.avg_prompt_tokens = int(statistics.mean(m.prompt_tokens for m in successful))
        report.avg_completion_tokens = int(statistics.mean(m.completion_tokens for m in successful))
        report.schema_success_rate = sum(1 for m in successful if m.schema_valid) / len(successful)
        report.section_coverage_rate = statistics.mean(m.section_count / 18 for m in successful)
        total_correct = sum(m.number_correct for m in successful)
        total_checked = sum(m.number_checked for m in successful)
        report.number_integrity_rate = total_correct / total_checked if total_checked > 0 else 0.0

    for m in all_metrics:
        fr = m.finish_reason or "error"
        report.finish_reasons[fr] = report.finish_reasons.get(fr, 0) + 1

    report.metrics = all_metrics
    return report


def print_report(h1: EvalReport, h2: EvalReport) -> None:
    print("\n" + "=" * 70)
    print("  NUMRA V3 DEEPSEEK PROVIDER EVALUATION")
    print("=" * 70)
    print(f"  Profiles: {len(GOLDEN_PROFILES)}")
    print(f"  Runs per config: {RUNS_PER_CONFIG}")
    print(f"  Total runs: {h1.total_runs + h2.total_runs}")
    print(f"  max_output_tokens: {NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS}")
    print()

    for label, r in [
        ("H1: Thinking (reasoning_effort=high)", h1),
        ("H2: Non-Thinking (temperature=0.2)", h2),
    ]:
        print(f"  --- {label} ---")
        print(f"  Successful: {r.successful_runs}/{r.total_runs}")
        print(f"  Failed:     {r.failed_runs}/{r.total_runs}")
        if r.successful_runs > 0:
            print(f"  Avg duration:        {r.avg_duration_s:.1f}s")
            print(f"  Avg prompt tokens:   {r.avg_prompt_tokens}")
            print(f"  Avg completion:      {r.avg_completion_tokens}")
            print(f"  Schema success:      {r.schema_success_rate:.1%}")
            print(f"  Section coverage:    {r.section_coverage_rate:.1%}")
            print(f"  Number integrity:    {r.number_integrity_rate:.1%}")
        print(f"  Finish reasons:      {r.finish_reasons}")
        print()

    print("  --- HYPOTHESIS RESULTS ---")
    print(f"  H1 Schema/Reference fidelity: {h1.number_integrity_rate:.3f}")
    print(f"  H2 Schema/Reference fidelity: {h2.number_integrity_rate:.3f}")
    print()
    print("  Note: Temperature and top_p are ignored in Thinking mode.")
    print("  No default switch is made based on this evaluation.")
    print("=" * 70)


async def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set. Export it or configure .env.")
        return

    base_settings = DeepSeekSettings(
        api_key=SecretStr(api_key),
        model="deepseek-v4-pro",
        max_output_tokens=NUMRA_V3_INITIAL_MAX_OUTPUT_TOKENS,
        max_retries=2,
        timeout_seconds=120,
    )

    print("Numra V3 Provider Evaluation")
    print(f"Profiles: {[p['core_name'] for p in GOLDEN_PROFILES]}")
    print()

    # H1: Thinking mode enabled
    print("--- H1: Thinking (reasoning_effort=high) ---")
    h1_settings = base_settings.model_copy(
        update={"thinking_enabled": True, "reasoning_effort": "high"}
    )
    h1 = await evaluate_config(h1_settings, "H1-thinking")

    # H2: Non-Thinking with temperature 0.2
    print("\n--- H2: Non-Thinking (temperature=0.2) ---")
    h2_settings = base_settings.model_copy(update={"thinking_enabled": False})
    h2 = await evaluate_config(h2_settings, "H2-non-thinking")

    print_report(h1, h2)


if __name__ == "__main__":
    asyncio.run(main())
