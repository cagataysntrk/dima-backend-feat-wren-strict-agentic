"""Provider-free contract for the single authorized Day8 live Sol sentinel."""

from __future__ import annotations

from lab.v2_day8_root_cause_live_sol import (
    LIVE_MANAGER_MODEL,
    MAX_AUTHORIZED_MODEL_CALLS,
    SCENARIO_COUNT,
    ScriptedSentinelLLM,
    _provider_failure_class,
    run_scenario,
)
from app.v2.manager_models import ManagerCapabilityKey
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)
from app.v2.models import HypothesisNextTestProposal, ResearchTaskKind


def test_day8_live_policy_is_one_scenario_workers_one_and_sol_only():
    assert SCENARIO_COUNT == 1
    assert MAX_AUTHORIZED_MODEL_CALLS == 8
    assert LIVE_MANAGER_MODEL == "openai/gpt-5.6-sol"


def test_provider_free_scripted_sentinel_proves_the_live_state_machine():
    llm = ScriptedSentinelLLM()
    result = run_scenario(llm)

    assert result["status"] == "pass"
    assert llm.calls == 5
    assert result["action_sequence"] == [
        "propose_hypothesis",
        "propose_hypothesis_next_test",
        "run_analytics",
        "inspect_evidence",
        "propose_hypothesis_evidence_relation",
    ]
    assert result["followup_verified"] is True
    assert result["followup_inspected"] is True
    assert result["relation"] in {"SUPPORTS", "CONTRADICTS"}
    assert result["confirmed_cause_allowed"] is False
    assert result["confirmed_cause_code"] == "CAUSAL_NOT_IDENTIFIED"
    assert result["synthetic_governed_query_calls"] == 2
    assert result["query_contract_count"] == 2
    assert result["next_test_rejection_count"] == 0


def test_live_harness_rejects_inapplicable_proposal_and_allows_bounded_replan():
    llm = ScriptedSentinelLLM(reject_next_test_once=True)
    result = run_scenario(llm)

    assert result["status"] == "pass"
    assert llm.calls == 6
    assert result["next_test_rejection_count"] == 1
    assert "TREND" in result["next_test_rejections"][0]
    assert result["action_sequence"][:3] == [
        "propose_hypothesis",
        "propose_hypothesis_next_test",
        "propose_hypothesis_next_test",
    ]
    assert result["followup_verified"] is True
    assert result["followup_inspected"] is True
    assert result["confirmed_cause_allowed"] is False


def test_live_sentinel_preserves_root_cause_authority_invariants():
    spec = ManagerCapabilityRegistry().get(ManagerCapabilityKey.ROOT_CAUSE)

    assert spec.execution_mode == ManagerCapabilityExecutionMode.ORCHESTRATED
    assert spec.executable is False
    assert not hasattr(ResearchTaskKind, "ROOT_CAUSE")
    assert "task_id" not in HypothesisNextTestProposal.model_fields


def test_live_provider_failure_classifier_does_not_turn_transport_into_behavior():
    assert _provider_failure_class("429 Client Error: Too Many Requests") == "PROVIDER_QUOTA_FAILURE"
    assert _provider_failure_class("401 Client Error: Unauthorized") == "PROVIDER_AUTH_FAILURE"
    assert _provider_failure_class("503 Server Error: Service Unavailable") == "PROVIDER_UNAVAILABLE"
    assert _provider_failure_class("expected propose_hypothesis first") is None
