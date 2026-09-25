"""Trajectory-invariant evaluator for DMP-DEC-0050 P17 autonomy certification.

This module evaluates authority, lineage, evidence-feedback and bounded-outcome
invariants. It intentionally does not encode one expected investigation sequence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


STOP_INTENTS = {"STOP_BRANCH", "STOP_INVESTIGATION"}
CANDIDATE_INTENTS = {"EXPLORE_ALTERNATIVES"}
CANDIDATE_TARGETS = {"ALTERNATIVE", "EXPLANATION"}
NATIVE_TEST_INTENTS = {
    "INVESTIGATE_GAP",
    "TEST_DISCRIMINATING_EVIDENCE",
    "SEEK_COUNTER_EVIDENCE",
}
DEEPENING_INTENTS = {
    "DEEPEN_EXPLANATION",
    "TEST_DISCRIMINATING_EVIDENCE",
    "SEEK_COUNTER_EVIDENCE",
    "REPLAN",
}
NO_GAIN_STOPS = {
    "NO_MEANINGFUL_GAIN",
    "NO_NEW_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
    "DATA_UNAVAILABLE",
    "ROOT_EXTERNAL_TO_AVAILABLE_DATA",
    "CAUSAL_IDENTIFICATION_LIMIT",
    "INCONCLUSIVE",
}


@dataclass(frozen=True)
class TurnObservation:
    index: int
    manager_called: bool
    guidance_used: bool
    step_id: str
    parent_step_id: str | None
    branch_id: str
    depth: int
    intent: str
    target_kind: str
    objective_key: str
    stop_reason: str | None = None
    stop_scope: str | None = None
    before_evidence_refs: tuple[str, ...] = ()
    after_evidence_refs: tuple[str, ...] = ()
    native_execution_refs: tuple[str, ...] = ()
    material_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AuthorityObservation:
    p14_authority_immutable: bool
    p16_claim_authority_preserved: bool
    all_native_occurrences_verified: bool
    all_followup_lineage_valid: bool
    p13_hot_path_attestation_calls: int = 0
    second_native_executor_calls: int = 0
    second_receipt_family_writes: int = 0
    second_claim_authority_writes: int = 0
    p19_truth_promotions: int = 0
    dima_python_analytics_calls: int = 0
    wren_fallback_calls: int = 0
    raw_sql_fallback_calls: int = 0
    admin_analytical_fallback_calls: int = 0


@dataclass(frozen=True)
class AutonomousCanaryObservation:
    manager_model: str
    manager_call_count: int
    max_reasoning_steps: int
    native_followup_count: int
    max_followup_native_turns: int
    max_observed_depth: int
    terminal_stop_reason: str | None
    open_branch_ids: tuple[str, ...]
    stopped_branch_ids: tuple[str, ...]
    turns: tuple[TurnObservation, ...]
    authority: AuthorityObservation


@dataclass(frozen=True)
class EvaluationResult:
    status: str
    gates: dict[str, bool]
    details: dict[str, object]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "gates": dict(self.gates),
            "details": dict(self.details),
        }


def _candidate_turns(
    turns: Iterable[TurnObservation],
) -> tuple[TurnObservation, ...]:
    return tuple(
        turn
        for turn in turns
        if turn.manager_called
        and (
            turn.intent in CANDIDATE_INTENTS
            or turn.target_kind in CANDIDATE_TARGETS
        )
        and turn.stop_scope is None
    )


def _lineage_is_legal(turns: tuple[TurnObservation, ...]) -> bool:
    prior: dict[str, TurnObservation] = {}
    for turn in turns:
        if turn.parent_step_id is None:
            if turn.depth != 0:
                return False
        else:
            parent = prior.get(turn.parent_step_id)
            if parent is None:
                return False
            expected_depth = (
                parent.depth
                if turn.intent in STOP_INTENTS
                else parent.depth + 1
            )
            if turn.depth != expected_depth:
                return False
            if (
                turn.intent != "EXPLORE_ALTERNATIVES"
                and turn.branch_id != parent.branch_id
            ):
                return False
        if turn.step_id in prior:
            return False
        prior[turn.step_id] = turn
    return True


def _evidence_feedback(
    turns: tuple[TurnObservation, ...],
) -> tuple[bool, tuple[str, ...]]:
    fed_back: set[str] = set()
    for idx, turn in enumerate(turns):
        produced = set(turn.evidence_refs)
        if not produced:
            continue
        for later in turns[idx + 1 :]:
            if not later.manager_called:
                continue
            seen = produced.intersection(later.before_evidence_refs)
            fed_back.update(seen)
    return bool(fed_back), tuple(sorted(fed_back))


def _candidate_branch_ids(
    turns: tuple[TurnObservation, ...],
) -> tuple[str, ...]:
    by_branch: dict[str, set[str]] = {}
    for turn in _candidate_turns(turns):
        by_branch.setdefault(turn.branch_id, set()).add(turn.objective_key)
    return tuple(sorted(by_branch))


def _materially_distinct_alternatives(
    turns: tuple[TurnObservation, ...],
) -> bool:
    distinct = {
        (turn.branch_id, turn.objective_key)
        for turn in _candidate_turns(turns)
    }
    branches = {branch for branch, _ in distinct}
    objectives = {objective for _, objective in distinct}
    return len(branches) >= 2 and len(objectives) >= 2


def _candidate_native_test(
    turns: tuple[TurnObservation, ...],
    candidate_branches: set[str],
) -> bool:
    return any(
        turn.manager_called
        and turn.branch_id in candidate_branches
        and turn.intent in NATIVE_TEST_INTENTS
        and bool(turn.native_execution_refs)
        and bool(turn.evidence_refs)
        for turn in turns
    )


def _alternative_outcome(
    turns: tuple[TurnObservation, ...],
    candidate_branches: set[str],
) -> tuple[bool, dict[str, tuple[str, ...]]]:
    stopped = {
        turn.branch_id
        for turn in turns
        if turn.intent == "STOP_BRANCH"
        and turn.stop_reason is not None
        and turn.branch_id in candidate_branches
    }
    challenged = {
        turn.branch_id
        for turn in turns
        if turn.intent == "SEEK_COUNTER_EVIDENCE"
        and turn.branch_id in candidate_branches
    }
    retained: set[str] = set()
    first_index: dict[str, int] = {}
    for turn in turns:
        if turn.branch_id in candidate_branches:
            first_index.setdefault(turn.branch_id, turn.index)
    for turn in turns:
        if (
            turn.manager_called
            and turn.branch_id in candidate_branches
            and turn.index > first_index.get(turn.branch_id, turn.index)
            and turn.intent not in STOP_INTENTS
        ):
            retained.add(turn.branch_id)
    ok = bool(stopped or challenged or retained)
    return ok, {
        "stopped": tuple(sorted(stopped)),
        "challenged": tuple(sorted(challenged)),
        "retained": tuple(sorted(retained)),
    }


def _meaningful_recursive_depth_or_supported_stop(
    turns: tuple[TurnObservation, ...],
) -> bool:
    by_id = {turn.step_id: turn for turn in turns}
    for turn in turns:
        if not turn.manager_called or turn.parent_step_id is None:
            continue
        parent = by_id.get(turn.parent_step_id)
        if (
            parent is not None
            and turn.intent in DEEPENING_INTENTS
            and turn.depth > parent.depth
        ):
            return True
    return any(
        turn.manager_called
        and turn.intent in STOP_INTENTS
        and turn.stop_reason in NO_GAIN_STOPS
        for turn in turns
    )


def evaluate_autonomous_canary(
    observation: AutonomousCanaryObservation,
) -> EvaluationResult:
    turns = observation.turns
    candidate_branches = set(_candidate_branch_ids(turns))
    feedback_ok, feedback_refs = _evidence_feedback(turns)
    outcome_ok, outcomes = _alternative_outcome(turns, candidate_branches)
    authority = observation.authority

    gates = {
        "real_autonomous_manager_path": (
            observation.manager_call_count > 0
            and all(
                not turn.guidance_used
                for turn in turns
                if turn.manager_called
            )
        ),
        "trajectory_lineage_legal": _lineage_is_legal(turns),
        "materially_distinct_alternatives_considered": (
            _materially_distinct_alternatives(turns)
        ),
        "candidate_received_native_analytical_test": (
            _candidate_native_test(turns, candidate_branches)
        ),
        "new_evidence_entered_later_manager_snapshot": feedback_ok,
        "later_manager_choice_after_new_evidence": feedback_ok,
        "alternative_challenged_retained_or_stopped": outcome_ok,
        "meaningful_recursive_depth_or_supported_stop": (
            _meaningful_recursive_depth_or_supported_stop(turns)
        ),
        "p14_authority_immutable": authority.p14_authority_immutable,
        "p16_sole_claim_authority": (
            authority.p16_claim_authority_preserved
            and authority.second_claim_authority_writes == 0
            and authority.p19_truth_promotions == 0
        ),
        "native_analytics_only": (
            authority.all_native_occurrences_verified
            and authority.second_native_executor_calls == 0
            and authority.dima_python_analytics_calls == 0
            and authority.wren_fallback_calls == 0
            and authority.raw_sql_fallback_calls == 0
            and authority.admin_analytical_fallback_calls == 0
        ),
        "followup_lineage_valid": authority.all_followup_lineage_valid,
        "single_receipt_family": authority.second_receipt_family_writes == 0,
        "p13_hot_path_attestation_zero": (
            authority.p13_hot_path_attestation_calls == 0
        ),
        "bounded_reasoning": (
            observation.manager_call_count <= observation.max_reasoning_steps
        ),
        "bounded_native_followups": (
            observation.native_followup_count
            <= observation.max_followup_native_turns
        ),
        "bounded_termination": observation.terminal_stop_reason is not None,
    }
    details = {
        "candidate_branch_ids": tuple(sorted(candidate_branches)),
        "feedback_evidence_refs": feedback_refs,
        "branch_outcomes": outcomes,
        "observed_manager_calls": observation.manager_call_count,
        "observed_native_followups": observation.native_followup_count,
        "observed_max_depth": observation.max_observed_depth,
        "terminal_stop_reason": observation.terminal_stop_reason,
    }
    return EvaluationResult(
        status="GREEN" if all(gates.values()) else "RED",
        gates=gates,
        details=details,
    )
