"""Deterministic standard-vs-research decision over accepted typed authority."""

from __future__ import annotations

from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerCapabilityKey,
    ObligationPolarity,
    ObligationStatus,
    RepresentabilityDecision,
    RepresentabilityResult,
    UserObligationLedger,
)
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry


class RepresentabilityGate:
    def __init__(self, registry: ManagerCapabilityRegistry | None = None) -> None:
        self._registry = registry or ManagerCapabilityRegistry()

    def decide(
        self,
        *,
        contract: AcceptedTurnContract,
        ledger: UserObligationLedger,
    ) -> RepresentabilityResult:
        if contract.lineage_id != ledger.lineage_id or contract.version != ledger.version:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("contract/ledger lineage mismatch",),
            )

        if contract.unresolved_ids:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.CLARIFICATION_REQUIRED,
                reasons=("accepted contract still contains unresolved obligations",),
            )

        active = [
            item
            for item in ledger.items
            if item.status != ObligationStatus.SUPERSEDED
            and item.polarity == ObligationPolarity.REQUIRED
        ]
        if any(item.status == ObligationStatus.NEEDS_CLARIFICATION for item in active):
            return RepresentabilityResult(
                decision=RepresentabilityDecision.CLARIFICATION_REQUIRED,
                reasons=("active obligation requires clarification",),
            )
        if any(item.status == ObligationStatus.UNSUPPORTED for item in active):
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("active obligation is unsupported",),
            )

        standard: list[ManagerCapabilityKey] = []
        research: list[ManagerCapabilityKey] = []
        executable_count = 0
        for item in active:
            spec = self._registry.get(item.capability_key)
            if not spec.executable:
                continue
            executable_count += 1
            if spec.lane == ManagerCapabilityLane.RESEARCH:
                research.append(item.capability_key)
            elif spec.lane == ManagerCapabilityLane.STANDARD:
                standard.append(item.capability_key)

        if research:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.RESEARCH_REQUIRED,
                reasons=("at least one accepted obligation requires research orchestration",),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
                research_capability_keys=tuple(dict.fromkeys(research)),
            )

        if executable_count and len(standard) == executable_count:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.STANDARD_LOSSLESS,
                reasons=("all executable accepted obligations are standard Core capabilities",),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
            )

        return RepresentabilityResult(
            decision=RepresentabilityDecision.UNSUPPORTED,
            reasons=("accepted contract has no executable analytical capability",),
        )
