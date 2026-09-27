"""Capability-specific obligation execution proof for Day 6.5.

A verified query is only evidence. An obligation becomes VERIFIED only when the actual
AnalyticsIR + sealed QueryContracts prove the capability-specific user promise.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.manager_models import ManagerCapabilityKey, ObligationLedgerItem, StandardProjection
from app.v2.models import AnalyticsIR, EvidenceArtifact


@dataclass(frozen=True)
class ObligationExecutionProof:
    obligation_id: str
    capability_key: ManagerCapabilityKey
    verified: bool
    reasons: tuple[str, ...]


class StandardObligationVerifier:
    def verify(
        self,
        *,
        obligation: ObligationLedgerItem,
        projection: StandardProjection,
        ir: AnalyticsIR,
        evidence: EvidenceArtifact,
    ) -> ObligationExecutionProof:
        reasons: list[str] = []

        if obligation.obligation_id not in projection.obligation_ids:
            reasons.append("obligation is not included in executed StandardProjection")

        projection_handles = {
            *projection.metric_handles,
            *projection.dimension_handles,
            *projection.filter_handles,
            *(() if projection.period_handle is None else (projection.period_handle,)),
            *(() if projection.comparison_handle is None else (projection.comparison_handle,)),
        }
        missing_bound_handles = set(obligation.semantic_handle_refs) - projection_handles
        if missing_bound_handles:
            reasons.append(
                "executed projection does not include obligation semantic bindings: "
                + ", ".join(sorted(missing_bound_handles))
            )
        if not evidence.verified:
            reasons.append("EvidenceArtifact is not verified")
        if not evidence.query_contract_refs:
            reasons.append("sealed QueryContract reference is missing")

        capability = obligation.capability_key
        if capability == ManagerCapabilityKey.PERFORMANCE:
            if not ir.metrics:
                reasons.append("performance execution has no metric")
        elif capability == ManagerCapabilityKey.BREAKDOWN:
            if not ir.metrics or not ir.dimensions:
                reasons.append("breakdown execution requires metric + dimension")
        elif capability == ManagerCapabilityKey.RANKING:
            if (
                len(ir.metrics) != 1
                or not ir.dimensions
                or ir.ranking is None
                or projection.ranking_direction is None
                or projection.limit is None
            ):
                reasons.append(
                    "ranking execution requires one metric + dimension + ranking direction + limit"
                )
            elif (
                ir.ranking.direction != projection.ranking_direction
                or ir.ranking.limit != projection.limit
            ):
                reasons.append("executed ranking does not match StandardProjection")
        elif capability == ManagerCapabilityKey.COMPARISON:
            if ir.comparison is None or projection.comparison_handle is None:
                reasons.append("comparison execution lacks governed comparison representation")
        else:
            reasons.append(f"capability is not standard-verifiable: {capability.value}")

        return ObligationExecutionProof(
            obligation_id=obligation.obligation_id,
            capability_key=capability,
            verified=not reasons,
            reasons=tuple(reasons),
        )
