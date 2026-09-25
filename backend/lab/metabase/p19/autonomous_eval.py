"""Trajectory-invariant evaluator for the bounded P19 Luna canary."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProposalObservation(Frozen):
    call_index: int
    accepted: bool
    error_code: str | None = None
    aggregate_outcome: str | None = None
    candidate_ids: tuple[str, ...] = ()
    selected_grounding_ids: tuple[str, ...] = ()


class AuthorityObservation(Frozen):
    lower_authorities_unchanged: bool
    analytical_execution_calls: int = 0
    second_receipt_family_writes: int = 0
    second_evidence_authority_writes: int = 0
    second_claim_authority_writes: int = 0
    p17_graph_as_causal_writes: int = 0
    p18_direction_as_causal_writes: int = 0
    engine_changes_builds: int = 0
    sol_calls: int = 0
    c1_calls: int = 0
    multiple_material_provider_free_green: bool = True
    inconclusive_provider_free_green: bool = True


class AutonomousP19Observation(Frozen):
    manager_model: str
    manager_call_count: int
    max_manager_calls: int
    hypothesis_ids: tuple[str, ...]
    known_grounding_ids: tuple[str, ...]
    challenge_grounding_ids: tuple[str, ...]
    causal_identification_available: bool
    invented_numeric_fields: tuple[str, ...] = ()
    proposals: tuple[ProposalObservation, ...]
    final_assessment_id: str | None = None
    final_outcome: str | None = None
    final_candidate_ids: tuple[str, ...] = ()
    final_selected_grounding_ids: tuple[str, ...] = ()
    authority: AuthorityObservation


class EvaluationResult(Frozen):
    status: str
    gates: dict[str, bool]
    details: dict[str, object]

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")


TERMINAL_OUTCOMES = {
    "ROOT_CAUSE_ESTABLISHED",
    "MULTIPLE_MATERIAL_CONTRIBUTORS",
    "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
}


def evaluate_p19_canary(
    observation: AutonomousP19Observation,
) -> EvaluationResult:
    hypothesis_set = set(observation.hypothesis_ids)
    grounding_set = set(observation.known_grounding_ids)
    selected = set(observation.final_selected_grounding_ids)
    challenges = set(observation.challenge_grounding_ids)

    gates = {
        "real_luna_manager": (
            observation.manager_model == "openai/gpt-5.6-luna"
        ),
        "bounded_model_calls": (
            1
            <= observation.manager_call_count
            <= observation.max_manager_calls
            <= 2
        ),
        "bounded_proposal_history": (
            len(observation.proposals)
            == observation.manager_call_count
        ),
        "terminal_assessment_persisted": (
            observation.final_assessment_id is not None
            and observation.final_outcome in TERMINAL_OUTCOMES
        ),
        "all_alternatives_preserved": (
            set(observation.final_candidate_ids) == hypothesis_set
            and len(hypothesis_set) >= 2
        ),
        "legal_source_use": selected.issubset(grounding_set),
        "challenge_visibility": bool(challenges & selected),
        "no_unsupported_causal_promotion": (
            observation.causal_identification_available
            or observation.final_outcome != "ROOT_CAUSE_ESTABLISHED"
        ),
        "no_invented_numeric_confidence": (
            not observation.invented_numeric_fields
        ),
        "multiple_contributors_is_legal": (
            observation.authority.multiple_material_provider_free_green
        ),
        "inconclusive_is_legal": (
            observation.authority.inconclusive_provider_free_green
        ),
        "lower_authorities_unchanged": (
            observation.authority.lower_authorities_unchanged
        ),
        "p19_analytical_execution_zero": (
            observation.authority.analytical_execution_calls == 0
        ),
        "duplicate_receipt_authority_zero": (
            observation.authority.second_receipt_family_writes == 0
        ),
        "duplicate_evidence_authority_zero": (
            observation.authority.second_evidence_authority_writes == 0
        ),
        "duplicate_claim_authority_zero": (
            observation.authority.second_claim_authority_writes == 0
        ),
        "p17_graph_not_causal": (
            observation.authority.p17_graph_as_causal_writes == 0
        ),
        "p18_direction_not_causal": (
            observation.authority.p18_direction_as_causal_writes == 0
        ),
        "engine_unchanged": (
            observation.authority.engine_changes_builds == 0
        ),
        "sol_zero": observation.authority.sol_calls == 0,
        "c1_zero": observation.authority.c1_calls == 0,
    }
    status = "GREEN" if all(gates.values()) else "RED"
    details = {
        "accepted_proposal_count": sum(
            item.accepted for item in observation.proposals
        ),
        "rejected_error_codes": [
            item.error_code
            for item in observation.proposals
            if not item.accepted and item.error_code
        ],
        "final_outcome": observation.final_outcome,
        "hypothesis_count": len(hypothesis_set),
        "selected_grounding_count": len(selected),
        "challenge_grounding_count": len(challenges),
    }
    return EvaluationResult(
        status=status,
        gates=gates,
        details=details,
    )
