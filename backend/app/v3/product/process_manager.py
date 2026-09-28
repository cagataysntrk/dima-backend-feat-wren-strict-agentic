"""Deterministic Core-B Product process-manager callability.

No analytical or epistemic truth is created here. The manager projects sealed
P17 state into exactly one next legal owner or a governed terminal.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

from app.v3.root_cause_candidate_contract import RootCauseCandidateSemantics


class ProductProcessPurpose(StrEnum):
    RELATIONSHIP = "RELATIONSHIP"
    ROOT_CAUSE = "ROOT_CAUSE"
    ADAPTIVE_INVESTIGATION = "ADAPTIVE_INVESTIGATION"

class ProductProcessNext(StrEnum):
    P17 = "P17"
    P18 = "P18"
    P19 = "P19"
    COMPLETE = "COMPLETE"
    TERMINAL = "TERMINAL"


class P19EligibilityDecision(StrEnum):
    CALL_P19 = "CALL_P19"
    NEED_MORE_EVIDENCE = "NEED_MORE_EVIDENCE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class RootCauseCandidate:
    claim_id: str
    semantics: RootCauseCandidateSemantics
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.claim_id:
            raise ValueError("root-cause candidate claim identity must be non-empty")
        if not self.evidence_refs:
            raise ValueError("root-cause candidate requires governed Evidence refs")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("root-cause candidate Evidence refs must be unique")

    @property
    def mechanism_identity(self) -> tuple[str, str]:
        return self.semantics.mechanism_identity

@dataclass(frozen=True)
class ProductProcessObservation:
    claim_ids: tuple[str, ...] = ()
    completed_step_ids: tuple[str, ...] = ()
    terminal_stop_reason: str | None = None
    remaining_reasoning_steps: int = 0
    scoped_move_available: bool = False
    downstream_ref_present: bool = False
    root_cause_candidates: tuple[RootCauseCandidate, ...] = ()

    def __post_init__(self) -> None:
        if self.remaining_reasoning_steps < 0:
            raise ValueError("remaining_reasoning_steps must be non-negative")
        if len(self.claim_ids) != len(set(self.claim_ids)):
            raise ValueError("claim_ids must be unique")
        if len(self.completed_step_ids) != len(set(self.completed_step_ids)):
            raise ValueError("completed_step_ids must be unique")
        candidate_ids = tuple(item.claim_id for item in self.root_cause_candidates)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("root-cause candidate claim ids must be unique")

def p19_eligibility(
    observation: ProductProcessObservation,
) -> P19EligibilityDecision:
    """Single executable P19 callability predicate for V1.

    Candidate distinctness is exact typed mechanism/relation identity only.
    Human-readable claim wording and similarity heuristics are non-authoritative.
    """
    eligible = tuple(
        item
        for item in observation.root_cause_candidates
        if item.evidence_refs
    )
    distinct = {item.mechanism_identity for item in eligible}
    if len(distinct) >= 2:
        return P19EligibilityDecision.CALL_P19
    if (
        observation.terminal_stop_reason is None
        and observation.remaining_reasoning_steps > 0
        and observation.scoped_move_available
    ):
        return P19EligibilityDecision.NEED_MORE_EVIDENCE
    return P19EligibilityDecision.INCONCLUSIVE


class ProductProcessError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail

def decide_next_owner(
    purpose: ProductProcessPurpose,
    observation: ProductProcessObservation,
) -> ProductProcessNext:
    if observation.downstream_ref_present:
        return ProductProcessNext.COMPLETE

    if purpose == ProductProcessPurpose.RELATIONSHIP:
        if observation.claim_ids and observation.completed_step_ids:
            return ProductProcessNext.P18
    elif purpose == ProductProcessPurpose.ROOT_CAUSE:
        eligibility = p19_eligibility(observation)
        if eligibility == P19EligibilityDecision.CALL_P19:
            return ProductProcessNext.P19
        if eligibility == P19EligibilityDecision.INCONCLUSIVE:
            return ProductProcessNext.TERMINAL
    elif purpose == ProductProcessPurpose.ADAPTIVE_INVESTIGATION:
        if observation.completed_step_ids:
            return ProductProcessNext.COMPLETE
    else:
        raise ValueError(f"unsupported Product process purpose: {purpose}")

    if observation.terminal_stop_reason is not None:
        return ProductProcessNext.TERMINAL
    if observation.remaining_reasoning_steps <= 0:
        return ProductProcessNext.TERMINAL
    if not observation.scoped_move_available:
        return ProductProcessNext.TERMINAL
    return ProductProcessNext.P17
