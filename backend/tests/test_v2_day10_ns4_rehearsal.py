"""G16 provider-free NS4 cognition lower-bound receipt."""

from app.v2.manager_loop import ManagerActionKind
from lab.v2_day10_ns4_provider_free_rehearsal import build_receipt


def test_ns4_lower_bound_fits_existing_six_turn_ceiling_without_ceremony():
    receipt = build_receipt()

    assert receipt["provider_calls"] == 0
    assert receipt["preacceptance_model_calls"] == 2
    assert receipt["research_manager_calls"] == 4
    assert receipt["manager_turn_total"] == 6
    assert receipt["manager_turn_ceiling"] == 6
    assert receipt["manager_turn_headroom"] == 0

    assert receipt["fresh_evidence_disclosures"] == 3
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

    states = receipt["completion_gate_states"]
    assert [item["allowed"] for item in states] == [
        False,
        False,
        False,
        False,
        True,
    ]
    assert receipt["paid_gate_structural_status"] == "STRUCTURALLY_ADMISSIBLE_AT_CEILING"
