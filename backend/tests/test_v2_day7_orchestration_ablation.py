"""Provider-free contract for Day7 FREE_COGNITION vs GOVERNED shadow ablation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

import lab.v2_day7_orchestration_ablation as ablation


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day7_orchestration_ablation.yaml"
MICRO_WORKFLOW = ROOT.parent / ".github" / "workflows" / "v2-day7-orchestration-micro.yml"
LIVE_WORKFLOW = ROOT.parent / ".github" / "workflows" / "v2-day7-live-sol.yml"


class _NeverCalledLLM:
    def structured_json(self, *args, **kwargs):
        raise AssertionError("typed fixture construction must not call a model")


def test_ablation_manifest_is_small_shared_authority_workers1():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = list(doc["cases"])
    assert doc["policy"]["workers"] == 1
    assert doc["policy"]["manager_model"] == "openai/gpt-5.6-sol"
    assert doc["policy"]["accepted_authority"] == "typed_fixture_shared_per_case"
    assert doc["policy"]["semantic_linker_calls"] == 0
    assert doc["policy"]["temporal_model_calls"] == 0
    assert doc["policy"]["frozen13_rerun"] is False
    assert doc["policy"]["hard_trust_plane_shared"] is True
    assert 8 <= len(cases) <= 12
    assert len({case["id"] for case in cases}) == len(cases)


def test_free_schema_removes_only_preacceptance_and_explicit_inspect_actions():
    encoded = json.dumps(ablation._free_action_schema(), ensure_ascii=False)
    assert '"propose_acceptance"' not in encoded
    assert '"inspect_evidence"' not in encoded
    for action in (
        "resolve_semantics",
        "propose_branches",
        "run_analytics",
        "run_relationship",
        "request_clarification",
        "finish",
    ):
        assert f'"{action}"' in encoded


def test_same_case_builds_exact_same_accepted_authority_in_both_arms():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    case = doc["cases"][0]
    llm = _NeverCalledLLM()

    free = ablation._build_case_runtime(
        case=case,
        arm="FREE_COGNITION",
        llm=llm,
    )
    governed = ablation._build_case_runtime(
        case=case,
        arm="GOVERNED_ORCHESTRATION",
        llm=llm,
    )

    assert free["contract_id"] == governed["contract_id"]

    free_contract = free["runtime"].accepted_contract.model_dump(mode="json")
    governed_contract = governed["runtime"].accepted_contract.model_dump(mode="json")
    free_contract.pop("accepted_at_iso")
    governed_contract.pop("accepted_at_iso")
    assert free_contract == governed_contract
    assert free["runtime"].ledger == governed["runtime"].ledger


def test_ablation_keeps_governed_execution_substrate_in_both_arms():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    case = next(item for item in doc["cases"] if item["id"] == "relationship-safe")
    llm = _NeverCalledLLM()

    free = ablation._build_case_runtime(
        case=case,
        arm="FREE_COGNITION",
        llm=llm,
    )
    governed = ablation._build_case_runtime(
        case=case,
        arm="GOVERNED_ORCHESTRATION",
        llm=llm,
    )

    assert type(free["executor"]) is type(governed["executor"])
    assert type(free["service"]) is type(governed["service"])
    assert free["runtime"].budget == governed["runtime"].budget


class _OneCallLLM:
    def __init__(self) -> None:
        self.calls = 0

    def structured_json(self, *args, **kwargs):
        self.calls += 1
        return "{}"


def test_micro_ablation_requires_explicit_case_selection_and_preserves_requested_order():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))

    selected = ablation._select_cases(
        doc,
        ["adaptive-material,stable-no-extra-branch"],
    )

    assert [case["id"] for case in selected] == [
        "adaptive-material",
        "stable-no-extra-branch",
    ]

    try:
        ablation._select_cases(doc, [])
    except ValueError as exc:
        assert "explicit --case-id is required" in str(exc)
    else:
        raise AssertionError("broad default ablation must be rejected")


def test_ablation_paid_call_guard_stops_before_next_provider_request():
    inner = _OneCallLLM()
    guard = ablation.PaidCallGuard(1)
    counting = ablation.CountingLLM(inner, call_guard=guard)

    counting.structured_json("system", "user")

    assert inner.calls == 1
    assert counting.calls == 1
    assert guard.used == 1
    assert guard.exhausted is False

    try:
        counting.structured_json("system", "user")
    except ablation.EvalBudgetExhausted:
        pass
    else:
        raise AssertionError("second provider call must be blocked before execution")

    assert inner.calls == 1
    assert counting.calls == 1
    assert guard.used == 1
    assert guard.exhausted is True


def test_ablation_dry_run_receipt_declares_scope_and_cost_before_provider_use():
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = ablation._select_cases(
        doc,
        ["adaptive-material", "stable-no-extra-branch"],
    )

    receipt = ablation._dry_run_receipt(
        cases=cases,
        max_model_calls=20,
    )

    assert receipt == {
        "kind": "dima_v2_day7_orchestration_shadow_ablation_dry_run",
        "selected_case_ids": ["adaptive-material", "stable-no-extra-branch"],
        "selected_cases": 2,
        "arms": ["FREE_COGNITION", "GOVERNED_ORCHESTRATION"],
        "maximum_loop_records": 4,
        "configured_manager_hard_turn_cap": 6,
        "model_calls_budget": 20,
        "provider_requests_made": 0,
    }


def test_paid_day7_workflows_require_explicit_scope_and_budget():
    micro = MICRO_WORKFLOW.read_text(encoding="utf-8")
    live = LIVE_WORKFLOW.read_text(encoding="utf-8")

    assert '"on":\n  workflow_dispatch:' in micro
    assert "\n  push:" not in micro
    assert "confirm_micro_ablation" in micro
    assert "max_model_calls" in micro
    assert "--case-id adaptive-material" in micro
    assert "--case-id stable-no-extra-branch" in micro
    assert "--max-model-calls" in micro
    assert "--dry-run" in micro
    assert "budget < 1 || budget > 16" in micro

    assert '"on":\n  workflow_dispatch:' in live
    assert "\n  push:" not in live
    assert "full_corpus" in live
    assert "confirm_expensive_run" in live
    assert "FROZEN13" in live
    assert "blank case_ids cannot run a broad paid corpus" in live
    assert "--max-model-calls" in live


def test_current_day7_single_case_paid_workflows_are_manual_only():
    workflow_dir = ROOT.parent / ".github" / "workflows"
    names = [
        "v2-day7-adaptive-material-once.yml",
        "v2-day7-insufficient-evidence-once.yml",
        "v2-day7-stable-no-extra-branch-once.yml",
        "v2-day7-frozen13-once.yml",
        "v2-day7-live-sol-once.yml",
    ]

    for name in names:
        content = (workflow_dir / name).read_text(encoding="utf-8")
        assert '"on":\n  workflow_dispatch:' in content
        assert "\n  push:" not in content
