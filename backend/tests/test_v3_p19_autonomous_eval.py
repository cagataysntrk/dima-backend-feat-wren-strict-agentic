from __future__ import annotations

from lab.metabase.p19.autonomous_eval import (
    AuthorityObservation,
    AutonomousP19Observation,
    ProposalObservation,
    evaluate_p19_canary,
)


HYPOTHESES = (
    "p19h_" + "a" * 24,
    "p19h_" + "b" * 24,
)
GROUNDINGS = (
    "p19g_" + "1" * 24,
    "p19g_" + "2" * 24,
    "p19g_" + "3" * 24,
    "p19g_" + "4" * 24,
)
CHALLENGE = GROUNDINGS[-1]


def authority(**updates):
    data = {
        "lower_authorities_unchanged": True,
        "analytical_execution_calls": 0,
        "second_receipt_family_writes": 0,
        "second_evidence_authority_writes": 0,
        "second_claim_authority_writes": 0,
        "p17_graph_as_causal_writes": 0,
        "p18_direction_as_causal_writes": 0,
        "engine_changes_builds": 0,
        "sol_calls": 0,
        "c1_calls": 0,
        "multiple_material_provider_free_green": True,
        "inconclusive_provider_free_green": True,
    }
    data.update(updates)
    return AuthorityObservation(**data)


def observation(
    *,
    outcome="MULTIPLE_MATERIAL_CONTRIBUTORS",
    calls=1,
    proposals=None,
    candidate_ids=HYPOTHESES,
    selected=GROUNDINGS,
    causal_identification=False,
    invented_numeric=(),
    auth=None,
):
    if proposals is None:
        proposals = (
            ProposalObservation(
                call_index=1,
                accepted=True,
                aggregate_outcome=outcome,
                candidate_ids=HYPOTHESES,
                selected_grounding_ids=GROUNDINGS,
            ),
        )
    return AutonomousP19Observation(
        manager_model="openai/gpt-5.6-luna",
        manager_call_count=calls,
        max_manager_calls=2,
        hypothesis_ids=HYPOTHESES,
        known_grounding_ids=GROUNDINGS,
        challenge_grounding_ids=(CHALLENGE,),
        causal_identification_available=causal_identification,
        invented_numeric_fields=invented_numeric,
        proposals=proposals,
        final_assessment_id="p19a_" + "f" * 24,
        final_outcome=outcome,
        final_candidate_ids=candidate_ids,
        final_selected_grounding_ids=selected,
        authority=auth or authority(),
    )


def test_multiple_material_contributors_trajectory_is_green():
    result = evaluate_p19_canary(observation())
    assert result.status == "GREEN"
    assert all(result.gates.values())


def test_inconclusive_trajectory_is_equally_green():
    result = evaluate_p19_canary(
        observation(outcome="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED")
    )
    assert result.status == "GREEN"


def test_rejected_unsupported_root_then_legal_inconclusive_is_green():
    proposals = (
        ProposalObservation(
            call_index=1,
            accepted=False,
            error_code="P19_CAUSAL_PROMOTION_GATE_FAILED",
            aggregate_outcome="ROOT_CAUSE_ESTABLISHED",
            candidate_ids=HYPOTHESES,
            selected_grounding_ids=GROUNDINGS,
        ),
        ProposalObservation(
            call_index=2,
            accepted=True,
            aggregate_outcome="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
            candidate_ids=HYPOTHESES,
            selected_grounding_ids=GROUNDINGS,
        ),
    )
    result = evaluate_p19_canary(
        observation(
            outcome="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
            calls=2,
            proposals=proposals,
        )
    )
    assert result.status == "GREEN"
    assert result.details["rejected_error_codes"] == [
        "P19_CAUSAL_PROMOTION_GATE_FAILED"
    ]


def test_unsupported_root_cause_is_red_when_no_causal_identification_exists():
    result = evaluate_p19_canary(
        observation(outcome="ROOT_CAUSE_ESTABLISHED")
    )
    assert result.status == "RED"
    assert result.gates["no_unsupported_causal_promotion"] is False


def test_hidden_challenge_is_red():
    result = evaluate_p19_canary(
        observation(selected=GROUNDINGS[:-1])
    )
    assert result.status == "RED"
    assert result.gates["challenge_visibility"] is False


def test_foreign_grounding_is_red():
    result = evaluate_p19_canary(
        observation(selected=GROUNDINGS + ("p19g_" + "9" * 24,))
    )
    assert result.status == "RED"
    assert result.gates["legal_source_use"] is False


def test_dropping_competing_hypothesis_is_red():
    result = evaluate_p19_canary(
        observation(candidate_ids=(HYPOTHESES[0],))
    )
    assert result.status == "RED"
    assert result.gates["all_alternatives_preserved"] is False


def test_invented_numeric_confidence_is_red():
    result = evaluate_p19_canary(
        observation(invented_numeric=("confidence_percent",))
    )
    assert result.status == "RED"
    assert result.gates["no_invented_numeric_confidence"] is False


def test_any_analytical_execution_or_duplicate_authority_is_red():
    result = evaluate_p19_canary(
        observation(
            auth=authority(
                analytical_execution_calls=1,
                second_receipt_family_writes=1,
            )
        )
    )
    assert result.status == "RED"
    assert result.gates["p19_analytical_execution_zero"] is False
    assert result.gates["duplicate_receipt_authority_zero"] is False
