from __future__ import annotations

from lab.metabase.p17.autonomous_eval import (
    AuthorityObservation,
    AutonomousCanaryObservation,
    TurnObservation,
    evaluate_autonomous_canary,
)


def _authority(**overrides) -> AuthorityObservation:
    values = {
        "p14_authority_immutable": True,
        "p16_claim_authority_preserved": True,
        "all_native_occurrences_verified": True,
        "all_followup_lineage_valid": True,
    }
    values.update(overrides)
    return AuthorityObservation(**values)


def _turn(
    index: int,
    step_id: str,
    *,
    parent: str | None,
    branch: str,
    depth: int,
    intent: str,
    target_kind: str = "GAP",
    objective: str,
    stop_reason: str | None = None,
    stop_scope: str | None = None,
    before_evidence: tuple[str, ...] = (),
    evidence: tuple[str, ...] = (),
    native: tuple[str, ...] = (),
    manager_called: bool = True,
    guidance_used: bool = False,
) -> TurnObservation:
    return TurnObservation(
        index=index,
        manager_called=manager_called,
        guidance_used=guidance_used,
        step_id=step_id,
        parent_step_id=parent,
        branch_id=branch,
        depth=depth,
        intent=intent,
        target_kind=target_kind,
        objective_key=objective,
        stop_reason=stop_reason,
        stop_scope=stop_scope,
        before_evidence_refs=before_evidence,
        after_evidence_refs=tuple(sorted(set(before_evidence) | set(evidence))),
        native_execution_refs=native,
        evidence_refs=evidence,
    )


def _observation(
    turns: tuple[TurnObservation, ...],
    *,
    authority: AuthorityObservation | None = None,
    manager_call_count: int | None = None,
    native_followup_count: int | None = None,
    max_depth: int | None = None,
    terminal: str = "INCONCLUSIVE",
) -> AutonomousCanaryObservation:
    return AutonomousCanaryObservation(
        manager_model="openai/gpt-5.6-luna",
        manager_call_count=(
            manager_call_count
            if manager_call_count is not None
            else sum(x.manager_called for x in turns)
        ),
        max_reasoning_steps=8,
        native_followup_count=(
            native_followup_count
            if native_followup_count is not None
            else sum(bool(x.native_execution_refs) for x in turns)
        ),
        max_followup_native_turns=4,
        max_observed_depth=(
            max_depth
            if max_depth is not None
            else max((x.depth for x in turns), default=0)
        ),
        terminal_stop_reason=terminal,
        open_branch_ids=(),
        stopped_branch_ids=tuple(
            sorted(
                {
                    x.branch_id
                    for x in turns
                    if x.intent == "STOP_BRANCH"
                }
            )
        ),
        turns=turns,
        authority=authority or _authority(),
    )


def _trajectory_a() -> tuple[TurnObservation, ...]:
    return (
        _turn(
            0, "root", parent=None, branch="root", depth=0,
            intent="INVESTIGATE_GAP", objective="gap",
            native=("n0",), evidence=("e0",),
        ),
        _turn(
            1, "a", parent="root", branch="a", depth=1,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.a", before_evidence=("e0",),
        ),
        _turn(
            2, "b", parent="root", branch="b", depth=1,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.b", before_evidence=("e0",),
        ),
        _turn(
            3, "test-b", parent="b", branch="b", depth=2,
            intent="TEST_DISCRIMINATING_EVIDENCE", objective="test.b",
            before_evidence=("e0",), native=("n1",), evidence=("e1",),
        ),
        _turn(
            4, "deep-b", parent="test-b", branch="b", depth=3,
            intent="DEEPEN_EXPLANATION", target_kind="EXPLANATION",
            objective="deepen.b", before_evidence=("e0", "e1"),
        ),
        _turn(
            5, "stop-a", parent="a", branch="a", depth=1,
            intent="STOP_BRANCH", target_kind="ALTERNATIVE",
            objective="stop.a", before_evidence=("e0", "e1"),
            stop_reason="NO_MEANINGFUL_GAIN", stop_scope="BRANCH",
        ),
        _turn(
            6, "stop-all", parent="deep-b", branch="b", depth=3,
            intent="STOP_INVESTIGATION", objective="stop.all",
            before_evidence=("e0", "e1"),
            stop_reason="INCONCLUSIVE", stop_scope="INVESTIGATION",
        ),
    )


def _trajectory_b() -> tuple[TurnObservation, ...]:
    return (
        _turn(
            0, "root", parent=None, branch="root", depth=0,
            intent="INVESTIGATE_GAP", objective="gap",
            native=("n0",), evidence=("e0",),
        ),
        _turn(
            1, "a", parent="root", branch="a", depth=1,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.a", before_evidence=("e0",),
        ),
        _turn(
            2, "b", parent="root", branch="b", depth=1,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.b", before_evidence=("e0",),
        ),
        _turn(
            3, "test-a", parent="a", branch="a", depth=2,
            intent="TEST_DISCRIMINATING_EVIDENCE", objective="test.a",
            before_evidence=("e0",), native=("n1",), evidence=("e1",),
        ),
        _turn(
            4, "counter-a", parent="test-a", branch="a", depth=3,
            intent="SEEK_COUNTER_EVIDENCE", objective="counter.a",
            before_evidence=("e0", "e1"), native=("n2",), evidence=("e2",),
        ),
        _turn(
            5, "replan-b", parent="b", branch="b", depth=2,
            intent="REPLAN", objective="replan.b",
            before_evidence=("e0", "e1", "e2"),
        ),
        _turn(
            6, "stop-all", parent="replan-b", branch="b", depth=2,
            intent="STOP_INVESTIGATION", objective="stop.all",
            before_evidence=("e0", "e1", "e2"),
            stop_reason="INCONCLUSIVE", stop_scope="INVESTIGATION",
        ),
    )


def _short_trajectory() -> tuple[TurnObservation, ...]:
    return (
        _turn(
            0, "a", parent=None, branch="a", depth=0,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.a",
        ),
        _turn(
            1, "b", parent=None, branch="b", depth=0,
            intent="EXPLORE_ALTERNATIVES", target_kind="ALTERNATIVE",
            objective="alternative.b",
        ),
        _turn(
            2, "test-a", parent="a", branch="a", depth=1,
            intent="TEST_DISCRIMINATING_EVIDENCE", objective="test.a",
            native=("n1",), evidence=("e1",),
        ),
        _turn(
            3, "stop-all", parent="test-a", branch="a", depth=1,
            intent="STOP_INVESTIGATION", objective="stop.all",
            before_evidence=("e1",),
            stop_reason="NO_MEANINGFUL_GAIN", stop_scope="INVESTIGATION",
        ),
    )


def test_trajectory_invariant_evaluator_accepts_legal_path_a():
    result = evaluate_autonomous_canary(_observation(_trajectory_a()))
    assert result.status == "GREEN"
    assert all(result.gates.values())


def test_trajectory_invariant_evaluator_accepts_materially_different_path_b():
    result = evaluate_autonomous_canary(_observation(_trajectory_b()))
    assert result.status == "GREEN"
    assert all(result.gates.values())


def test_trajectory_invariant_evaluator_accepts_short_no_gain_stop():
    result = evaluate_autonomous_canary(_observation(_short_trajectory()))
    assert result.status == "GREEN"
    assert result.details["observed_manager_calls"] == 4
    assert result.details["observed_max_depth"] == 1


def test_cross_branch_parent_mismatch_is_red():
    turns = list(_trajectory_a())
    turns[3] = _turn(
        3, "test-b", parent="b", branch="a", depth=2,
        intent="TEST_DISCRIMINATING_EVIDENCE", objective="test.b",
        before_evidence=("e0",), native=("n1",), evidence=("e1",),
    )
    result = evaluate_autonomous_canary(_observation(tuple(turns)))
    assert result.status == "RED"
    assert result.gates["trajectory_lineage_legal"] is False


def test_p19_causal_truth_promotion_is_red():
    result = evaluate_autonomous_canary(
        _observation(
            _trajectory_a(),
            authority=_authority(p19_truth_promotions=1),
        )
    )
    assert result.status == "RED"
    assert result.gates["p16_sole_claim_authority"] is False


def test_dima_python_analytics_is_red():
    result = evaluate_autonomous_canary(
        _observation(
            _trajectory_a(),
            authority=_authority(dima_python_analytics_calls=1),
        )
    )
    assert result.status == "RED"
    assert result.gates["native_analytics_only"] is False


def test_guided_screenplay_manager_path_is_not_autonomous():
    turns = list(_trajectory_a())
    turns[1] = TurnObservation(
        **{
            **turns[1].to_dict(),
            "guidance_used": True,
        }
    )
    result = evaluate_autonomous_canary(_observation(tuple(turns)))
    assert result.status == "RED"
    assert result.gates["real_autonomous_manager_path"] is False
