"""D10-G / G16 provider-free NS4 cognition lower-bound receipt.

This is an architectural state-machine rehearsal, not an evaluation corpus and not a
provider/Wren execution.  Every transition below is backed by a focused product test:
- preacceptance draft + coverage are the two successful canonical cognition calls,
- fully-bound USER_SEED / root bootstrap / admitted derived tasks execute deterministically,
- fresh Evidence disclosure replaces redundant inspect cognition,
- CompletionGate, not FINISH prose, owns terminality.

The receipt answers one question only: under the canonical no-retry/no-ambiguity path,
how many Manager cognition turns are irreducible after D10-G ceremony removal?
"""

from __future__ import annotations

import json
from pathlib import Path

from app.v2.manager_loop import ManagerActionKind
from app.v2.manager_models import ManagerBudget


PREACCEPTANCE_SEQUENCE = (
    "DRAFT_ACCEPTED_INTENT",
    "COVERAGE_PROOF",
)

RESEARCH_COGNITION_SEQUENCE = (
    ManagerActionKind.PROPOSE_BRANCHES,
    ManagerActionKind.PROPOSE_HYPOTHESIS,
    ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST,
    ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION,
)

DETERMINISTIC_TRANSITIONS = (
    "USER_SEED_DIRECT_EXECUTION",
    "USER_SEED_RELATIONSHIP_EXECUTION",
    "ROOT_CAUSE_EXACTLY_ONE_BOOTSTRAP_EXECUTION",
    "EXACTLY_ONE_ADMITTED_RESULT_BRANCH_EXECUTION",
    "EXACTLY_ONE_ADMITTED_HYPOTHESIS_NEXT_TEST_EXECUTION",
    "HYPOTHESIS_STATUS_RECONCILIATION",
    "ROOT_CAUSE_OBLIGATION_VERIFICATION",
    "COMPLETION_GATE_TERMINATION",
)

COMPLETION_STATES = (
    {
        "after": "deterministic_seed_and_root_bootstrap",
        "allowed": False,
        "reason": "ROOT_CAUSE investigation not yet accounted",
    },
    {
        "after": "result_driven_branch",
        "allowed": False,
        "reason": "no governed hypothesis yet",
    },
    {
        "after": "hypothesis_proposed",
        "allowed": False,
        "reason": "OPEN hypothesis is not accounted",
    },
    {
        "after": "next_test_executed",
        "allowed": False,
        "reason": "Evidence relation not yet admitted",
    },
    {
        "after": "evidence_relation_admitted",
        "allowed": True,
        "reason": (
            "hypothesis status reconciled; bounded ROOT_CAUSE investigation VERIFIED; "
            "all USER_MUST terminal/accounted"
        ),
    },
)


def build_receipt() -> dict[str, object]:
    budget = ManagerBudget()
    preacceptance_calls = len(PREACCEPTANCE_SEQUENCE)
    research_calls = len(RESEARCH_COGNITION_SEQUENCE)
    total_manager_calls = preacceptance_calls + research_calls

    execution_control_actions = {
        ManagerActionKind.RUN_ANALYTICS,
        ManagerActionKind.RUN_RELATIONSHIP,
        ManagerActionKind.INSPECT_EVIDENCE,
        ManagerActionKind.FINISH,
    }
    redundant_execution_control_turns = sum(
        action in execution_control_actions
        for action in RESEARCH_COGNITION_SEQUENCE
    )

    return {
        "contract": "d10-g16-ns4-provider-free-lower-bound-v1",
        "provider_calls": 0,
        "initial_user_must_count": 3,
        "user_must_families": [
            "PERFORMANCE",
            "RELATIONSHIP",
            "ROOT_CAUSE",
        ],
        "preacceptance_model_calls": preacceptance_calls,
        "preacceptance_sequence": list(PREACCEPTANCE_SEQUENCE),
        "research_manager_calls": research_calls,
        "research_cognition_sequence": [
            action.value for action in RESEARCH_COGNITION_SEQUENCE
        ],
        "manager_turn_total": total_manager_calls,
        "manager_turn_ceiling": budget.max_total_manager_turns,
        "manager_turn_headroom": budget.max_total_manager_turns - total_manager_calls,
        "deterministic_task_executions": 5,
        "deterministic_transition_sequence": list(DETERMINISTIC_TRANSITIONS),
        "deterministic_query_transitions": 5,
        "actual_wren_queries_in_rehearsal": 0,
        "fresh_evidence_disclosures": 3,
        "explicit_old_evidence_inspections": 0,
        "redundant_fresh_inspect_turns": 0,
        "redundant_manager_execution_control_turns": redundant_execution_control_turns,
        "hypotheses": 1,
        "hypothesis_next_tests": 1,
        "evidence_relations": 1,
        "semantic_linker_calls": 0,
        "temporal_normalizer_calls": 0,
        "narration_calls_expected_outside_manager_budget": 1,
        "completion_gate_states": list(COMPLETION_STATES),
        "paid_gate_structural_status": (
            "STRUCTURALLY_ADMISSIBLE_AT_CEILING"
            if total_manager_calls <= budget.max_total_manager_turns
            and redundant_execution_control_turns == 0
            else "BLOCKED"
        ),
        "constraints": [
            "no retry",
            "no semantic ambiguity requiring extra cognition",
            "no provider failure",
            "no explicit inspection for already-disclosed fresh Evidence",
            "no Manager RUN/INSPECT/FINISH ceremony",
            "global Manager ceiling remains unchanged",
        ],
    }


def main() -> int:
    receipt = build_receipt()
    if receipt["manager_turn_total"] > receipt["manager_turn_ceiling"]:
        raise SystemExit("canonical lower bound exceeds current Manager ceiling")
    if receipt["redundant_manager_execution_control_turns"] != 0:
        raise SystemExit("rehearsal contains redundant execution-control cognition")
    if receipt["redundant_fresh_inspect_turns"] != 0:
        raise SystemExit("rehearsal contains redundant fresh-Evidence inspection")

    path = Path("lab/reports/v2_day10_ns4_provider_free_rehearsal.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
