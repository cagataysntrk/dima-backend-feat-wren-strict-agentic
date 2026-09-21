"""Deterministic StandardProjection compiler for Day 6.5.

This compiler consumes only accepted typed authority plus Resolver-issued opaque
SemanticHandles. It never reads raw user text and never inspects canonical semantic
targets. A projection exists only when one lossless Core-shaped standard request can be
assembled from the accepted contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerCapabilityKey,
    ObligationPolarity,
    ObligationStatus,
    StandardProjection,
    UserObligationLedger,
)
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.semantic_handles import SemanticHandleRegistry


class StandardProjectionCompileError(RuntimeError):
    pass


@dataclass(frozen=True)
class StandardProjectionCompileResult:
    projection: StandardProjection | None
    reasons: tuple[str, ...] = ()

    @property
    def compiled(self) -> bool:
        return self.projection is not None


class StandardProjectionCompiler:
    """Compile accepted standard authority into a single opaque Core projection."""

    _KINDS = {
        "metric": "metric",
        "dimension": "dimension",
        "filter": "filter",
        "period": "period",
        "time": "period",  # defensive compatibility; Resolver currently emits period.
        "comparison": "comparison",
    }

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._handles = semantic_handles
        self._capabilities = capabilities or ManagerCapabilityRegistry()

    @staticmethod
    def _unique(values: list[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(values))

    def compile(
        self,
        *,
        contract: AcceptedTurnContract,
        ledger: UserObligationLedger,
        tenant_binding: str,
        context_version: str,
    ) -> StandardProjectionCompileResult:
        reasons: list[str] = []

        if contract.lineage_id != ledger.lineage_id or contract.version != ledger.version:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=("contract/ledger lineage mismatch",),
            )
        if contract.context_version != context_version:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=("contract/context version mismatch",),
            )

        active = [
            item
            for item in ledger.items
            if item.status != ObligationStatus.SUPERSEDED
            and item.polarity == ObligationPolarity.REQUIRED
            and item.obligation_id in set(contract.obligation_ids)
        ]
        executable = []
        for item in active:
            spec = self._capabilities.get(item.capability_key)
            if not spec.executable:
                continue
            executable.append(item)
            if spec.lane != ManagerCapabilityLane.STANDARD:
                reasons.append(
                    f"{item.obligation_id}: capability {item.capability_key.value} is not standard"
                )

        if not executable:
            reasons.append("accepted contract has no executable standard obligation")

        metrics: list[str] = []
        dimensions: list[str] = []
        filters: list[str] = []
        periods: list[str] = []
        comparisons: list[str] = []
        ranking_pairs: list[tuple[str, int]] = []

        for item in executable:
            for handle_id in item.semantic_handle_refs:
                try:
                    handle = self._handles.validate(
                        handle_id,
                        tenant_binding=tenant_binding,
                        context_version=context_version,
                    )
                except (KeyError, ValueError) as exc:
                    reasons.append(
                        f"{item.obligation_id}: invalid semantic handle {handle_id}: {exc}"
                    )
                    continue

                kind = self._KINDS.get(handle.target_kind)
                if kind == "metric":
                    metrics.append(handle_id)
                elif kind == "dimension":
                    dimensions.append(handle_id)
                elif kind == "filter":
                    filters.append(handle_id)
                elif kind == "period":
                    periods.append(handle_id)
                elif kind == "comparison":
                    comparisons.append(handle_id)
                else:
                    reasons.append(
                        f"{item.obligation_id}: unsupported semantic handle kind "
                        f"{handle.target_kind}"
                    )

            if item.capability_key == ManagerCapabilityKey.RANKING:
                if item.ranking_direction is None or item.ranking_limit is None:
                    reasons.append(
                        f"{item.obligation_id}: accepted ranking authority lacks direction/limit"
                    )
                else:
                    ranking_pairs.append(
                        (item.ranking_direction, int(item.ranking_limit))
                    )
            elif item.ranking_direction is not None or item.ranking_limit is not None:
                reasons.append(
                    f"{item.obligation_id}: non-ranking obligation carries ranking parameters"
                )

        metric_handles = self._unique(metrics)
        dimension_handles = self._unique(dimensions)
        filter_handles = self._unique(filters)
        period_handles = self._unique(periods)
        comparison_handles = self._unique(comparisons)
        unique_ranking = tuple(dict.fromkeys(ranking_pairs))

        if not metric_handles:
            reasons.append("standard projection requires at least one metric handle")
        if len(period_handles) > 1:
            reasons.append("single StandardProjection cannot carry multiple period handles")
        if len(comparison_handles) > 1:
            reasons.append(
                "single StandardProjection cannot carry multiple comparison handles"
            )
        if len(unique_ranking) > 1:
            reasons.append(
                "single StandardProjection cannot carry conflicting ranking parameters"
            )

        if reasons:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=tuple(dict.fromkeys(reasons)),
            )

        ranking_direction = unique_ranking[0][0] if unique_ranking else None
        ranking_limit = unique_ranking[0][1] if unique_ranking else None

        try:
            projection = StandardProjection(
                obligation_ids=tuple(item.obligation_id for item in executable),
                metric_handles=metric_handles,
                dimension_handles=dimension_handles,
                filter_handles=filter_handles,
                period_handle=period_handles[0] if period_handles else None,
                comparison_handle=(
                    comparison_handles[0] if comparison_handles else None
                ),
                ranking_direction=ranking_direction,
                limit=ranking_limit,
            )
        except ValueError as exc:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=(f"invalid StandardProjection: {exc}",),
            )

        return StandardProjectionCompileResult(projection=projection)
