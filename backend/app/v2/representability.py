"""Deterministic representability proof over accepted typed authority.

STANDARD_LOSSLESS means one concrete StandardProjection can represent every active
standard executable obligation without dropping capability-specific requirements.
Capability lane membership alone is never sufficient.
"""

from __future__ import annotations

from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerCapabilityKey,
    ObligationPolarity,
    ObligationStatus,
    RepresentabilityDecision,
    RepresentabilityResult,
    StandardProjection,
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
        projection: StandardProjection | None = None,
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

        executable = []
        standard: list[ManagerCapabilityKey] = []
        research: list[ManagerCapabilityKey] = []
        for item in active:
            spec = self._registry.get(item.capability_key)
            if not spec.executable:
                continue
            executable.append(item)
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

        if not executable:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("accepted contract has no executable analytical capability",),
            )

        if projection is None:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.RESEARCH_REQUIRED,
                reasons=("complete StandardProjection proof has not been supplied yet",),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
            )

        return self._prove_standard_projection(
            contract=contract,
            executable=tuple(executable),
            standard=tuple(standard),
            projection=projection,
        )

    def _prove_standard_projection(
        self,
        *,
        contract: AcceptedTurnContract,
        executable,
        standard: tuple[ManagerCapabilityKey, ...],
        projection: StandardProjection,
    ) -> RepresentabilityResult:
        reasons: list[str] = []
        expected_ids = {item.obligation_id for item in executable}
        supplied_ids = set(projection.obligation_ids)

        unknown = supplied_ids - set(contract.obligation_ids)
        if unknown:
            reasons.append("projection references obligations outside accepted contract: " + ", ".join(sorted(unknown)))

        missing = expected_ids - supplied_ids
        if missing:
            reasons.append("projection drops executable obligations: " + ", ".join(sorted(missing)))

        if not projection.metric_handles:
            reasons.append("standard projection requires at least one metric handle")

        for item in executable:
            if item.obligation_id not in supplied_ids:
                continue
            capability = item.capability_key
            if capability == ManagerCapabilityKey.PERFORMANCE:
                if not projection.metric_handles:
                    reasons.append(f"{item.obligation_id}: performance requires metric")
            elif capability == ManagerCapabilityKey.BREAKDOWN:
                if not projection.metric_handles or not projection.dimension_handles:
                    reasons.append(f"{item.obligation_id}: breakdown requires metric + dimension")
            elif capability == ManagerCapabilityKey.RANKING:
                if (
                    len(projection.metric_handles) != 1
                    or not projection.dimension_handles
                    or projection.ranking_direction is None
                    or projection.limit is None
                ):
                    reasons.append(
                        f"{item.obligation_id}: ranking requires one metric + dimension + direction + limit"
                    )
            elif capability == ManagerCapabilityKey.COMPARISON:
                if not projection.metric_handles or projection.comparison_handle is None:
                    reasons.append(
                        f"{item.obligation_id}: comparison requires metric + governed comparison handle"
                    )
            else:
                reasons.append(
                    f"{item.obligation_id}: capability is not standard-projectable: {capability.value}"
                )

        if reasons:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.RESEARCH_REQUIRED,
                reasons=tuple(dict.fromkeys(reasons)),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
            )

        return RepresentabilityResult(
            decision=RepresentabilityDecision.STANDARD_LOSSLESS,
            reasons=("one complete StandardProjection covers every executable standard obligation",),
            standard_capability_keys=tuple(dict.fromkeys(standard)),
            standard_projection=projection,
        )
