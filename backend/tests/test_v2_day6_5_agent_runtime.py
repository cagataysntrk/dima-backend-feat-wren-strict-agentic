"""Provider-free invariants for the generic bounded runtime kernel."""

from __future__ import annotations

import ast
import inspect

import app.v2.agent_runtime as agent_runtime
from app.v2.agent_runtime import (
    BoundedAgentRuntimeKernel,
    BoundedLoopBudget,
    LoopTerminalReason,
)


def test_kernel_has_no_research_domain_imports():
    tree = ast.parse(inspect.getsource(agent_runtime))
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden = {
        "app.v2.manager_models",
        "app.v2.manager_runtime",
        "app.v2.manager_loop",
        "app.v2.manager_tools",
        "app.v2.manager_preacceptance",
        "app.v2.acceptance",
        "app.v2.evidence",
        "app.v2.completion",
    }
    assert imported_modules.isdisjoint(forbidden)


def test_same_action_same_state_is_no_progress_without_extra_turn():
    runtime = BoundedAgentRuntimeKernel(
        budget=BoundedLoopBudget(max_model_turns=4, max_tool_calls=8)
    )
    action = {"kind": "PROPOSE", "payload": {"x": 1}}

    first = runtime.reserve_model_turn(
        action=action,
        state_fingerprint="state-a",
    )
    assert first.allowed is True
    assert runtime.counters.model_turns == 1

    duplicate = runtime.reserve_model_turn(
        action=action,
        state_fingerprint="state-a",
    )
    assert duplicate.allowed is False
    assert duplicate.terminal_reason == LoopTerminalReason.NO_PROGRESS
    assert runtime.counters.model_turns == 1


def test_same_action_can_run_again_after_authoritative_state_changes():
    runtime = BoundedAgentRuntimeKernel()
    action = {"kind": "INSPECT", "candidate": "cand-1"}

    first = runtime.reserve_model_turn(
        action=action,
        state_fingerprint="state-a",
    )
    second = runtime.reserve_model_turn(
        action=action,
        state_fingerprint="state-b",
    )

    assert first.allowed is True
    assert second.allowed is True
    assert runtime.counters.model_turns == 2


def test_model_turn_budget_fails_closed_without_incrementing_counter():
    runtime = BoundedAgentRuntimeKernel(
        budget=BoundedLoopBudget(max_model_turns=1, max_tool_calls=8)
    )

    assert runtime.reserve_model_turn(
        action={"kind": "A"},
        state_fingerprint="state-a",
    ).allowed

    rejected = runtime.reserve_model_turn(
        action={"kind": "B"},
        state_fingerprint="state-a",
    )

    assert rejected.allowed is False
    assert rejected.terminal_reason == LoopTerminalReason.BUDGET_EXHAUSTED
    assert runtime.counters.model_turns == 1


def test_tool_budget_is_separate_from_model_turn_budget():
    runtime = BoundedAgentRuntimeKernel(
        budget=BoundedLoopBudget(max_model_turns=4, max_tool_calls=1)
    )

    first = runtime.reserve_tool_call(
        action={"tool": "resolve"},
        state_fingerprint="state-a",
    )
    rejected = runtime.reserve_tool_call(
        action={"tool": "inspect"},
        state_fingerprint="state-a",
    )

    assert first.allowed is True
    assert rejected.allowed is False
    assert rejected.terminal_reason == LoopTerminalReason.BUDGET_EXHAUSTED
    assert runtime.counters.tool_calls == 1
    assert runtime.counters.model_turns == 0


def test_observation_receipt_is_generic_and_counted():
    runtime = BoundedAgentRuntimeKernel()
    reservation = runtime.reserve_model_turn(
        action={"kind": "PROPOSE"},
        state_fingerprint="state-before",
    )

    observation = runtime.observe(
        reservation=reservation,
        result={"status": "VALIDATION_ERROR"},
        state_after="state-after",
    )

    assert observation.state_before == "state-before"
    assert observation.state_after == "state-after"
    assert observation.action_fingerprint.startswith("act_")
    assert observation.result_fingerprint.startswith("res_")
    assert runtime.counters.observations == 1
    assert runtime.telemetry()["action_state_pairs"] == 1
