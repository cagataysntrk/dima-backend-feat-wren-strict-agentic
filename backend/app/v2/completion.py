"""Completion truth for Day 6.5 Manager research.

Evidence presence is not a verdict. Only explicit VERIFIED USER_MUST obligations can
produce VERIFIED_COMPLETE.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityRegistry,
)
from app.v2.models import FrozenModel
from app.v2.manager_models import (
    ObligationStatus,
    ResearchRunTerminal,
    UserObligationLedger,
)


class CompletionGapReceipt(FrozenModel):
    """Deterministic non-completion diagnostics; never a second completion authority."""

    unfulfilled_user_must_ids: tuple[str, ...] = ()
    unresolved_directives: tuple[str, ...] = ()
    open_hypothesis_ids: tuple[str, ...] = ()
    required_next_test_or_accounting_gaps: tuple[str, ...] = ()
    failed_or_blocked_task_ids: tuple[str, ...] = ()
    remaining_research_turns: int
    remaining_query_budget: int
    completion_gate_reasons: tuple[str, ...] = ()
    missing_completion_predicates: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompletionGateResult:
    allowed: bool
    terminal: ResearchRunTerminal | None
    reasons: tuple[str, ...] = ()


class CompletionGate:
    _PARTIAL_TERMINALS = {
        ObligationStatus.BLOCKED_DATA_GAP,
        ObligationStatus.LIMITED,
        ObligationStatus.UNSUPPORTED,
    }

    def __init__(
        self,
        *,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._capabilities = capabilities or ManagerCapabilityRegistry()

    def _completion_relevant_user_must(
        self,
        ledger: UserObligationLedger,
    ):
        """Project analytical completion owners without deleting accepted authority.

        PRESENTATION obligations (REPORT/TABLE/CHART/EXPLAIN) remain intact in the
        accepted ledger. They are deliverables owned by the Product presentation layer
        after Research completes, so waiting for Research to mark them VERIFIED would
        create an ownership cycle. All other active USER_MUST obligations retain the
        existing terminal requirements.
        """
        return tuple(
            item
            for item in ledger.active_user_must
            if self._capabilities.get(item.capability_key).execution_mode
            != ManagerCapabilityExecutionMode.PRESENTATION
        )

    def evaluate(self, ledger: UserObligationLedger) -> CompletionGateResult:
        must = self._completion_relevant_user_must(ledger)
        if not must:
            return CompletionGateResult(
                allowed=False,
                terminal=ResearchRunTerminal.FAILED,
                reasons=("no completion-relevant analytical USER_MUST obligation",),
            )

        if all(item.status == ObligationStatus.VERIFIED for item in must):
            return CompletionGateResult(
                allowed=True,
                terminal=ResearchRunTerminal.VERIFIED_COMPLETE,
            )

        unaccounted = tuple(
            item.obligation_id
            for item in must
            if item.status not in ({ObligationStatus.VERIFIED} | self._PARTIAL_TERMINALS)
        )
        if unaccounted:
            return CompletionGateResult(
                allowed=False,
                terminal=None,
                reasons=(
                    "active USER_MUST obligations are not terminal: "
                    + ", ".join(unaccounted),
                ),
            )

        return CompletionGateResult(
            allowed=True,
            terminal=ResearchRunTerminal.PARTIAL,
            reasons=("at least one USER_MUST is blocked/limited/unsupported",),
        )
