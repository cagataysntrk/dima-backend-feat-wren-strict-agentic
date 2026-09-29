"""Core-B Closure Sentinel v2 owner-legality evaluator.

V1 receipts remain historical. V2 judges whether the next sealed owner was
legally callable, not whether Product forced a desired artifact into existence.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.v3.product.process_manager import (
    ProductProcessNext,
    ProductProcessObservation,
    ProductProcessPurpose,
    decide_next_owner,
)


@dataclass(frozen=True)
class ClosureV2Decision:
    passed: bool
    classification: str
    expected_next_owner: str
    downstream_owner_present: bool


def evaluate_owner_legality(
    *,
    purpose: ProductProcessPurpose,
    observation: ProductProcessObservation,
    downstream_owner_present: bool,
    security_valid: bool = True,
    silent_wrong: bool = False,
    causal_overclaim: bool = False,
    fabricated_claim: bool = False,
) -> ClosureV2Decision:
    if not security_valid:
        return ClosureV2Decision(False, "SECURITY_VIOLATION", "FAIL_CLOSED", downstream_owner_present)
    if silent_wrong:
        return ClosureV2Decision(False, "SILENT_WRONG", "FAIL_CLOSED", downstream_owner_present)
    if causal_overclaim:
        return ClosureV2Decision(False, "UNSUPPORTED_CAUSAL_PROMOTION", "FAIL_CLOSED", downstream_owner_present)
    if fabricated_claim:
        return ClosureV2Decision(False, "FABRICATED_CLAIM", "FAIL_CLOSED", downstream_owner_present)

    state_only = ProductProcessObservation(
        claim_ids=observation.claim_ids,
        completed_step_ids=observation.completed_step_ids,
        terminal_stop_reason=observation.terminal_stop_reason,
        remaining_reasoning_steps=observation.remaining_reasoning_steps,
        scoped_move_available=observation.scoped_move_available,
        downstream_ref_present=False,
        root_cause_candidates=observation.root_cause_candidates,
    )
    expected = decide_next_owner(purpose, state_only)
    expected_value = expected.value

    required = (
        ProductProcessNext.P18
        if purpose == ProductProcessPurpose.RELATIONSHIP
        else ProductProcessNext.P19
        if purpose == ProductProcessPurpose.ROOT_CAUSE
        else ProductProcessNext.COMPLETE
    )

    if expected == required:
        if downstream_owner_present:
            return ClosureV2Decision(
                True,
                "DOWNSTREAM_OWNER_GENUINELY_INVOKED",
                expected_value,
                True,
            )
        return ClosureV2Decision(
            False,
            "CALLABLE_OWNER_NOT_INVOKED",
            expected_value,
            False,
        )

    if downstream_owner_present:
        return ClosureV2Decision(
            False,
            "DOWNSTREAM_OWNER_INVOKED_WHILE_UNCALLABLE",
            expected_value,
            True,
        )

    if expected == ProductProcessNext.TERMINAL:
        return ClosureV2Decision(
            True,
            "GOVERNED_LIMITATION",
            expected_value,
            False,
        )

    return ClosureV2Decision(
        False,
        "PROCESS_LEFT_NONTERMINAL",
        expected_value,
        False,
    )
