"""Completion truth for Day 6.5 Manager research.

Evidence presence is not a verdict. Only explicit VERIFIED USER_MUST obligations can
produce VERIFIED_COMPLETE.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.manager_models import (
    ObligationStatus,
    ResearchRunTerminal,
    UserObligationLedger,
)


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

    def evaluate(self, ledger: UserObligationLedger) -> CompletionGateResult:
        must = ledger.active_user_must
        if not must:
            return CompletionGateResult(
                allowed=False,
                terminal=ResearchRunTerminal.FAILED,
                reasons=("no active USER_MUST obligation",),
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
