"""Provider-free contract for Day7 FREE_COGNITION vs GOVERNED shadow ablation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

import lab.v2_day7_orchestration_ablation as ablation


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day7_orchestration_ablation.yaml"


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
    assert free["runtime"].accepted_contract == governed["runtime"].accepted_contract
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
