"""Research-level obligation ledger transitions for Day 6.5.

User obligations are immutable promises. Agent-derived investigations may be added as
children, but can never replace/promote/mutate USER_MUST obligations.
"""

from __future__ import annotations

from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserObligationLedger,
)


class ObligationLedgerError(RuntimeError):
    pass


class UserObligationLedgerService:
    _STARTABLE = {
        ObligationStatus.ACCEPTED,
        ObligationStatus.READY,
    }
    _TERMINAL = {
        ObligationStatus.VERIFIED,
        ObligationStatus.BLOCKED_DATA_GAP,
        ObligationStatus.LIMITED,
        ObligationStatus.UNSUPPORTED,
        ObligationStatus.SUPERSEDED,
    }

    @staticmethod
    def _replace(
        ledger: UserObligationLedger,
        obligation_id: str,
        item: ObligationLedgerItem,
    ) -> UserObligationLedger:
        found = False
        out = []
        for current in ledger.items:
            if current.obligation_id == obligation_id:
                found = True
                out.append(item)
            else:
                out.append(current)
        if not found:
            raise ObligationLedgerError(f"unknown obligation: {obligation_id}")
        return ledger.model_copy(update={"items": tuple(out)})

    @staticmethod
    def get(ledger: UserObligationLedger, obligation_id: str) -> ObligationLedgerItem:
        try:
            return next(item for item in ledger.items if item.obligation_id == obligation_id)
        except StopIteration as exc:
            raise ObligationLedgerError(f"unknown obligation: {obligation_id}") from exc

    def start(
        self,
        ledger: UserObligationLedger,
        obligation_id: str,
    ) -> UserObligationLedger:
        item = self.get(ledger, obligation_id)
        if item.status not in self._STARTABLE:
            raise ObligationLedgerError(
                f"obligation {obligation_id} cannot start from {item.status.value}"
            )
        return self._replace(
            ledger,
            obligation_id,
            item.model_copy(update={"status": ObligationStatus.IN_PROGRESS}),
        )

    def verify(
        self,
        ledger: UserObligationLedger,
        obligation_id: str,
        *,
        evidence_refs: tuple[str, ...],
        verdict: str,
    ) -> UserObligationLedger:
        if not evidence_refs:
            raise ObligationLedgerError("VERIFIED requires evidence refs")
        if not verdict.strip():
            raise ObligationLedgerError("VERIFIED requires deterministic verdict")
        item = self.get(ledger, obligation_id)
        if item.polarity == ObligationPolarity.EXCLUDED:
            raise ObligationLedgerError("excluded obligation cannot become VERIFIED")
        if item.status in self._TERMINAL and item.status != ObligationStatus.VERIFIED:
            raise ObligationLedgerError(
                f"terminal obligation {obligation_id} cannot become VERIFIED"
            )
        return self._replace(
            ledger,
            obligation_id,
            item.model_copy(
                update={
                    "status": ObligationStatus.VERIFIED,
                    "evidence_refs": tuple(dict.fromkeys((*item.evidence_refs, *evidence_refs))),
                    "verdict": verdict,
                    "blocker": None,
                }
            ),
        )

    def block(
        self,
        ledger: UserObligationLedger,
        obligation_id: str,
        *,
        status: ObligationStatus,
        reason: str,
        evidence_refs: tuple[str, ...] = (),
    ) -> UserObligationLedger:
        if status not in {
            ObligationStatus.BLOCKED_DATA_GAP,
            ObligationStatus.LIMITED,
            ObligationStatus.UNSUPPORTED,
        }:
            raise ObligationLedgerError("invalid blocking terminal status")
        item = self.get(ledger, obligation_id)
        if item.status == ObligationStatus.VERIFIED:
            raise ObligationLedgerError("verified obligation cannot be downgraded")
        return self._replace(
            ledger,
            obligation_id,
            item.model_copy(
                update={
                    "status": status,
                    "blocker": reason,
                    "evidence_refs": tuple(dict.fromkeys((*item.evidence_refs, *evidence_refs))),
                }
            ),
        )

    def add_agent_derived(
        self,
        ledger: UserObligationLedger,
        *,
        obligation_id: str,
        parent_obligation_id: str,
        capability_key: ManagerCapabilityKey,
        source_refs: tuple[str, ...],
        semantic_handle_refs: tuple[str, ...] = (),
    ) -> UserObligationLedger:
        if any(item.obligation_id == obligation_id for item in ledger.items):
            raise ObligationLedgerError(f"duplicate obligation id: {obligation_id}")
        parent = self.get(ledger, parent_obligation_id)
        if parent.status == ObligationStatus.SUPERSEDED:
            raise ObligationLedgerError("derived task cannot attach to superseded parent")

        derived = ObligationLedgerItem(
            obligation_id=obligation_id,
            capability_key=capability_key,
            origin=ObligationOrigin.AGENT_DERIVED,
            parent_obligation_id=parent_obligation_id,
            priority=ObligationPriority.SHOULD,
            polarity=ObligationPolarity.REQUIRED,
            status=ObligationStatus.READY,
            source_refs=source_refs or parent.source_refs,
            semantic_handle_refs=semantic_handle_refs,
            introduced_in_version=ledger.version,
        )
        return ledger.model_copy(update={"items": (*ledger.items, derived)})
