"""G16 provider-free NS4 runtime-observed cognition receipt."""

from app.v2.manager_loop import ManagerActionKind
from lab.v2_day10_ns4_provider_free_rehearsal import run_rehearsal


def test_ns4_runtime_rehearsal_fits_existing_six_turn_ceiling_without_ceremony():
    receipt = run_rehearsal()

    assert receipt["provider_calls"] == 0
    assert receipt["directive_count"] == 1
    assert receipt["directive_id"] == "R_ADAPT_ROOT"
    assert receipt["directive_type"] == "ADAPT_ON_EVIDENCE"
    assert receipt["directive_final_status"] == "APPLIED"
    assert receipt["directive_accounting_evidence_ref"]
    assert receipt["directive_branch_task_refs"]
    assert receipt["preacceptance_model_calls"] == 2
    assert receipt["research_manager_calls"] == 4
    assert receipt["manager_turn_total"] == 6
    assert receipt["manager_turn_ceiling"] == 6
    assert receipt["manager_turn_headroom"] == 0

    assert receipt["deterministic_task_executions"] == 5
    assert receipt["synthetic_query_calls"] == 5
    assert receipt["actual_wren_queries_in_rehearsal"] == 0
    assert receipt["explicit_old_evidence_inspections"] == 0
    assert receipt["redundant_fresh_inspect_turns"] == 0
    assert receipt["redundant_manager_execution_control_turns"] == 0

    cognition = tuple(receipt["research_cognition_sequence"])
    assert cognition == (
        ManagerActionKind.PROPOSE_BRANCHES.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION.value,
    )
    assert ManagerActionKind.RUN_ANALYTICS.value not in cognition
    assert ManagerActionKind.RUN_RELATIONSHIP.value not in cognition
    assert ManagerActionKind.INSPECT_EVIDENCE.value not in cognition
    assert ManagerActionKind.FINISH.value not in cognition

    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["candidate_finding_count"] == 1
    assert receipt["confirmed_cause_count"] == 0
    assert receipt["report_statement_injection_absent"] is True
    assert receipt["paid_gate_structural_status"] == "STRUCTURALLY_ADMISSIBLE_AT_CEILING"
