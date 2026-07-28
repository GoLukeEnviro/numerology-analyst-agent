# Inspector Feedback — Iteration 3

**Inspection Date:** 2026-07-28  
**Inspected Commit:** `87349e9` (fix/rc1-core-integration-closure)  
**Builder Changes:** Prompt-, Knowledge- und Composer-Funktionen in Produktionspfade integrieren  
**Inspector:** Claude:Haiku-4.5

---

## Verdict: **PASS**

**Reason:** All 13 acceptance criteria met. All quality gates green. Integration architecture verified via tests. Prompts bundled in wheel, loaded via importlib.resources. Composition pipeline complete: system_prompt + report_task_prompt → deepseek → analysis + compose_observations + entry_for(context) → InterpretationResult.observations.

---

## Acceptance Criteria Check

### Prompt Integration (KRITISCH) ✓

#### 1. Production Path Usage
- [x] `system_prompt()` used in `deepseek.py::_build_request_body` (line ~132) ✓
- [x] `report_task_prompt()` used in `deepseek.py::_build_request_body` (line ~134) ✓
- [x] `importlib.resources` via `load_prompt()` in `prompts.py` ✓
- [x] No hardcoded prompts in `deepseek.py` ✓

#### 2. Wheel Package Data
- [x] `uv build` succeeds ✓
- [x] Wheel contains all prompt templates:
  - `numerology_agent/prompt_templates/system/de-report-system.md`
  - `numerology_agent/prompt_templates/tasks/de-report-task.md`
  - `numerology_agent/prompt_templates/tasks/de-follow-up-task.md`
  - `numerology_agent/prompt_templates/eval/de-report-eval.md`
- [x] Test `test_wheel_contains_prompt_templates()` verifies packaging ✓

#### 3. Docker Container
- [x] Dockerfile builds wheel (`uv build`) and installs it ✓
- [x] Package data automatically included (Hatchling standard) ✓

### Composer Integration ✓

#### 4. compose_observations() in compose_interpretation()
- [x] Imported from `numerology_interpretation.rules` (line 13) ✓
- [x] Called in `compose_interpretation()` (line 166): `raw_observations = compose_observations(profile)` ✓
- [x] Results wrapped in `observation_records` (line 167) ✓
- [x] Attached to `InterpretationResult.observations` (line 175) ✓

#### 5. Observation Fields
- [x] Each `ComposerObservationRecord` (models.py) contains:
  - `composer_rule_id` ✓
  - `relation` (Literal["resonance", "tension"]) ✓
  - `calculation_refs` (tuple[str, str]) ✓
  - `knowledge_refs` (tuple[str, str]) ✓
  - `uncertainty` (str | None) ✓
  - `counter_hypothesis` (str | None) ✓

### Knowledge Resolver ✓

#### 6. Context-Aware entry_for()
- [x] `_entry_for_context(bundle, number, context)` defined (line 45) ✓
- [x] Calls `bundle.entry_for(number, context=context)` with context parameter (line 49) ✓
- [x] Used in `compose_interpretation()` (line 132) and `_build_observation_record()` (line 75–76) ✓
- [x] Test `test_knowledge_bundle_entry_for_with_context()` verifies context sensitivity ✓

#### 7. Stable ID for knowledge_ref
- [x] `compose_interpretation()` uses `entry.stable_id` (line 143) ✓
- [x] `_build_observation_record()` uses `entry_a.stable_id, entry_b.stable_id` (line 81) ✓
- [x] All claim objects get `knowledge_ref=knowledge_ref` (line 144) ✓
- [x] Test `test_knowledge_ref_uses_stable_id()` verifies format (de.pythagorean.*) ✓

### CI & Schema ✓

#### 8. validate_knowledge.py in CI
- [x] `.github/workflows/ci.yml` line ~34: `uv run python scripts/validate_knowledge.py` ✓
- [x] Marked as required check (no allow-failure) ✓

#### 9. Schema Files
- [x] `src/numerology_api/schemas/knowledge-bundle-v2.schema.json` exists ✓
- [x] `export_schemas.py --check` PASS ✓
- [x] Schema exported in git (version controlled) ✓

### Integration Tests ✓

#### 10. Architecture Test — Production Graph
- [x] `tests/integration/test_production_graph.py` created ✓
- [x] Tests prove:
  - `test_system_prompt_importable_from_package()` — system_prompt() from package data ✓
  - `test_report_task_prompt_importable_from_package()` — report_task_prompt() from package data ✓
  - `test_compose_observations_callable_from_profile()` — compose_observations() accessible ✓
  - `test_knowledge_bundle_entry_for_with_context()` — entry_for(number, context=...) works ✓
  - `test_circuit_breaker_reachable_via_agent_service()` — CircuitBreaker via AgentService ✓
  - `test_compose_observations_in_interpretation_result()` — observations in result ✓
  - `test_entry_for_context_returns_context_aware_entry()` — context selection verified ✓
  - `test_knowledge_ref_uses_stable_id()` — stable_id format enforced ✓
  - `test_circuit_breaker_opens_after_threshold()` — CircuitBreaker behavior ✓
  - `test_wheel_contains_prompt_templates()` — Wheel smoke test ✓

### Quality Gates ✓

#### 11. All Python Gates GREEN
- [x] `uv run ruff format --check .` — **PASS** ✓
- [x] `uv run ruff check .` — **PASS** ✓
- [x] `uv run mypy src tests scripts` — **PASS** (89 source files) ✓
- [x] `uv run pytest` — **PASS** (414 passed, 1 skipped) ✓
- [x] `uv run pytest --cov=src/numerology_engine --cov-fail-under=95` — **PASS** (98.51%) ✓
- [x] `uv run pytest --cov=src --cov-fail-under=85` — **PASS** (93.51%) ✓
- [x] `uv run python scripts/validate_knowledge.py` — **PASS** (2 bundles validated) ✓
- [x] `uv run python scripts/export_schemas.py --check` — **PASS** ✓
- [x] `uv run python scripts/export_openapi.py --check` — **PASS** ✓
- [x] `uv run python scripts/generate_examples.py --check` — **PASS** ✓

### Architecture ✓

#### 12. Determinism: No Network/LLM in engine
- [x] grep in `src/numerology_engine/` for `openai|anthropic|requests|httpx|deepseek|llm|api|network|http` — **NONE FOUND** ✓
- [x] Engine remains pure calculation, no external dependencies ✓

#### 13. No Circular Imports
- [x] Import chain executes without errors: domain → engine → knowledge → interpretation → safety → agent → api → cli ✓
- [x] `ruff.lint.isort` enforces `known-first-party` ordering ✓
- [x] Test: `python -c "from numerology_domain import *; from numerology_engine import *; ..."` — **OK** ✓

---

## Integration Flow Verification

The complete production pipeline is now wired:

```
PersonInput (from CLI/API)
  ↓ (calculate_profile)
ProfileCalculationResult
  ├→ compose_interpretation()
  │   ├→ load_knowledge_bundle("de", "v2")
  │   ├→ entry_for(number, context=ctx)  [context-aware]
  │   ├→ compose_observations(profile)   [relationship rules]
  │   └→ InterpretationResult
  │       ├→ sections[InterpretationSection]
  │       │   └→ claims[InterpretationClaim]
  │       │       ├→ knowledge_ref = entry.stable_id ✓
  │       │       ├→ calculation_ref ✓
  │       └→ observations[ComposerObservationRecord]
  │           ├→ composer_rule_id ✓
  │           ├→ knowledge_refs = (entry_a.stable_id, entry_b.stable_id) ✓
  │
  └→ generate_report() [Agent]
      ├→ system_prompt() [from importlib.resources] ✓
      ├→ report_task_prompt() [from importlib.resources] ✓
      ├→ deepseek.complete(payload, schema)
      └→ AgentResult with CircuitBreaker resilience ✓
```

**All junctions verified by tests.**

---

## Code Quality & Test Coverage

| Component | Coverage |
|-----------|----------|
| numerology_engine | **98.51%** (Gate: ≥95%) ✓ |
| src (total) | **93.51%** (Gate: ≥85%) ✓ |
| test_production_graph | **10 tests** — all PASS ✓ |

---

## Summary

✅ **All 13 acceptance criteria MET**  
✅ **All 10 quality gates GREEN**  
✅ **Production graph wired and tested**  
✅ **Determinism preserved (no LLM/network in engine)**  
✅ **No circular imports**  

**Ready for merge to main.**
