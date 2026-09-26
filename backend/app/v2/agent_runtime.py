"""Generic bounded process-control kernel for agent-style loops.

Day 6.5 scope is intentionally narrow: this module owns loop mechanics only.
It has no knowledge of semantic authority, Research contracts/ledgers, evidence truth,
query validity, database execution, or completion semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.v2.manager_progress import action_fingerprint, result_fingerprint


@dataclass(frozen=True)
class BoundedLoopBudget:
    max_model_turns: int = 4
    max_tool_calls: int = 8
    max_executions_per_action_state_pair: int = 1

    def __post_init__(self) -> None:
        if self.max_model_turns < 1:
            raise ValueError("max_model_turns must be >= 1")
        if self.max_tool_calls < 0:
            raise ValueError("max_tool_calls must be >= 0")
        if self.max_executions_per_action_state_pair < 1:
            raise ValueError(
                "max_executions_per_action_state_pair must be >= 1"
            )


@dataclass
class LoopCounters:
    model_turns: int = 0
    tool_calls: int = 0
    observations: int = 0


class LoopTerminalReason(StrEnum):
    COMPLETED = "COMPLETED"
    NO_PROGRESS = "NO_PROGRESS"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ActionReservation:
    allowed: bool
    action_fingerprint: str
    state_fingerprint: str
    terminal_reason: LoopTerminalReason | None = None


@dataclass(frozen=True)
class LoopObservation:
    action_fingerprint: str
    state_before: str
    state_after: str
    result_fingerprint: str


@dataclass
class ActionStateGuard:
    executions: dict[tuple[str, str], int] = field(default_factory=dict)

    def reserve(
        self,
        *,
        action_fingerprint: str,
        state_fingerprint: str,
        max_executions: int,
    ) -> bool:
        key = (action_fingerprint, state_fingerprint)
        current = self.executions.get(key, 0)
        if current >= max_executions:
            return False
        self.executions[key] = current + 1
        return True

    def execution_count(
        self,
        *,
        action_fingerprint: str,
        state_fingerprint: str,
    ) -> int:
        return self.executions.get(
            (action_fingerprint, state_fingerprint),
            0,
        )


class BoundedAgentRuntimeKernel:
    """Budgeted action/state execution guard with generic telemetry receipts."""

    def __init__(
        self,
        *,
        budget: BoundedLoopBudget | None = None,
    ) -> None:
        self.budget = budget or BoundedLoopBudget()
        self.counters = LoopCounters()
        self.guard = ActionStateGuard()
        self.observations: list[LoopObservation] = []
        self.terminal_reason: LoopTerminalReason | None = None

    @property
    def terminal(self) -> bool:
        return self.terminal_reason is not None

    def reserve_model_turn(
        self,
        *,
        action: Any,
        state_fingerprint: str,
    ) -> ActionReservation:
        return self._reserve(
            action=action,
            state_fingerprint=state_fingerprint,
            model_turns=1,
            tool_calls=0,
        )

    def reserve_tool_call(
        self,
        *,
        action: Any,
        state_fingerprint: str,
    ) -> ActionReservation:
        return self._reserve(
            action=action,
            state_fingerprint=state_fingerprint,
            model_turns=0,
            tool_calls=1,
        )

    def _reserve(
        self,
        *,
        action: Any,
        state_fingerprint: str,
        model_turns: int,
        tool_calls: int,
    ) -> ActionReservation:
        action_fp = action_fingerprint(action)

        if self.terminal_reason is not None:
            return ActionReservation(
                allowed=False,
                action_fingerprint=action_fp,
                state_fingerprint=state_fingerprint,
                terminal_reason=self.terminal_reason,
            )

        # Duplicate detection happens before budget accounting: a repeated action against
        # the same authoritative state is NO_PROGRESS, not another paid/charged turn.
        if not self.guard.reserve(
            action_fingerprint=action_fp,
            state_fingerprint=state_fingerprint,
            max_executions=self.budget.max_executions_per_action_state_pair,
        ):
            self.terminal_reason = LoopTerminalReason.NO_PROGRESS
            return ActionReservation(
                allowed=False,
                action_fingerprint=action_fp,
                state_fingerprint=state_fingerprint,
                terminal_reason=self.terminal_reason,
            )

        if (
            self.counters.model_turns + model_turns
            > self.budget.max_model_turns
            or self.counters.tool_calls + tool_calls
            > self.budget.max_tool_calls
        ):
            # Do not leave a rejected budget reservation in the action/state guard.
            key = (action_fp, state_fingerprint)
            count = self.guard.executions.get(key, 0)
            if count <= 1:
                self.guard.executions.pop(key, None)
            else:
                self.guard.executions[key] = count - 1
            self.terminal_reason = LoopTerminalReason.BUDGET_EXHAUSTED
            return ActionReservation(
                allowed=False,
                action_fingerprint=action_fp,
                state_fingerprint=state_fingerprint,
                terminal_reason=self.terminal_reason,
            )

        self.counters.model_turns += model_turns
        self.counters.tool_calls += tool_calls
        return ActionReservation(
            allowed=True,
            action_fingerprint=action_fp,
            state_fingerprint=state_fingerprint,
        )

    def observe(
        self,
        *,
        reservation: ActionReservation,
        result: Any,
        state_after: str,
    ) -> LoopObservation:
        if not reservation.allowed:
            raise ValueError("cannot observe a rejected action reservation")
        observation = LoopObservation(
            action_fingerprint=reservation.action_fingerprint,
            state_before=reservation.state_fingerprint,
            state_after=state_after,
            result_fingerprint=result_fingerprint(result),
        )
        self.observations.append(observation)
        self.counters.observations += 1
        return observation

    def terminate(self, reason: LoopTerminalReason) -> None:
        if self.terminal_reason is None:
            self.terminal_reason = reason

    def telemetry(self) -> dict[str, Any]:
        return {
            "model_turns": self.counters.model_turns,
            "tool_calls": self.counters.tool_calls,
            "observations": self.counters.observations,
            "terminal_reason": (
                self.terminal_reason.value
                if self.terminal_reason is not None
                else None
            ),
            "action_state_pairs": len(self.guard.executions),
        }
