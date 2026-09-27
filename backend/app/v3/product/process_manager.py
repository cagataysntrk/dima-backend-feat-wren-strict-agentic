"""Deterministic Core-B Product process-manager callability.

No analytical or epistemic truth is created here. The manager projects sealed
P17 state into exactly one next legal owner or a governed terminal.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

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

@dataclass(frozen=True)
class ProductProcessObservation:
    claim_ids: tuple[str, ...] = ()
    completed_step_ids: tuple[str, ...] = ()
    terminal_stop_reason: str | None = None
    remaining_reasoning_steps: int = 0
    scoped_move_available: bool = False
    downstream_ref_present: bool = False

    def __post_init__(self) -> None:
        if self.remaining_reasoning_steps < 0:
            raise ValueError("remaining_reasoning_steps must be non-negative")
        if len(self.claim_ids) != len(set(self.claim_ids)):
            raise ValueError("claim_ids must be unique")
        if len(self.completed_step_ids) != len(set(self.completed_step_ids)):
            raise ValueError("completed_step_ids must be unique")

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
        if len(observation.claim_ids) >= 2:
            return ProductProcessNext.P19
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
