"""Deterministic StandardProjection compiler for Day 6.5.

The compiler consumes only already-valid atomic obligations plus Resolver-issued opaque
SemanticHandles. Semantic correctness belongs to CapabilityBindingValidator; this module
only decides whether valid obligations can be losslessly merged into one Core request.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.capability_bindings import CapabilityBinding, CapabilityBindingValidator
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
    """Merge validated standard obligations into one opaque Core projection."""

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._handles = semantic_handles
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._bindings = CapabilityBindingValidator(
            semantic_handles=semantic_handles,
            capabilities=self._capabilities,
        )

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

        if (
            contract.lineage_id != ledger.lineage_id
            or contract.version != ledger.version
        ):
            return StandardProjectionCompileResult(
                projection=None,
                reasons=("contract/ledger lineage mismatch",),
            )
        if contract.context_version != context_version:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=("contract/context version mismatch",),
            )

        authority_ids = {
            *contract.obligation_ids,
            *contract.exclusion_ids,
        }
        authoritative_items = [
            item
            for item in ledger.items
            if item.status != ObligationStatus.SUPERSEDED
            and item.obligation_id in authority_ids
        ]

        bindings: dict[str, CapabilityBinding] = {}
        for item in authoritative_items:
            result = self._bindings.validate(
                item,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )
            if not result.valid:
                reasons.extend(
                    f"{item.obligation_id}: {reason}" for reason in result.reasons
                )
            elif result.binding is not None:
                bindings[item.obligation_id] = result.binding

        active_required = [
            item
            for item in authoritative_items
            if item.polarity == ObligationPolarity.REQUIRED
            and item.obligation_id in set(contract.obligation_ids)
        ]

        executable = []
        for item in active_required:
            spec = self._capabilities.get(item.capability_key)
            if not spec.executable:
                continue
            executable.append(item)
            if spec.lane != ManagerCapabilityLane.STANDARD:
                reasons.append(
                    f"{item.obligation_id}: capability "
                    f"{item.capability_key.value} is not standard"
                )

        if not executable:
            reasons.append("accepted contract has no executable standard obligation")

        # Never union fields from an invalid obligation. This blocks cross-obligation
        # semantic laundering where one malformed atom could be completed by another.
        if reasons:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=tuple(dict.fromkeys(reasons)),
            )

        metrics: list[str] = []
        dimensions: list[str] = []
        filters: list[str] = []
        periods: list[str] = []
        comparisons: list[str] = []
        ranking_pairs: list[tuple[str, int]] = []

        for item in executable:
            binding = bindings[item.obligation_id]
            metrics.extend(binding.refs("metric"))
            dimensions.extend(binding.refs("dimension"))
            filters.extend(binding.refs("filter"))
            periods.extend(binding.refs("period"))
            comparisons.extend(binding.refs("comparison"))

            if item.capability_key == ManagerCapabilityKey.RANKING:
                # Atomic binding validation already proves these exist.
                ranking_pairs.append(
                    (str(item.ranking_direction), int(item.ranking_limit))
                )

        metric_handles = self._unique(metrics)
        dimension_handles = self._unique(dimensions)
        filter_handles = self._unique(filters)
        period_handles = self._unique(periods)
        comparison_handles = self._unique(comparisons)
        unique_ranking = tuple(dict.fromkeys(ranking_pairs))

        merge_reasons: list[str] = []
        if not metric_handles:
            merge_reasons.append(
                "standard projection requires at least one metric handle"
            )
        if len(period_handles) > 1:
            merge_reasons.append(
                "single StandardProjection cannot carry multiple period handles"
            )
        if len(comparison_handles) > 1:
            merge_reasons.append(
                "single StandardProjection cannot carry multiple comparison handles"
            )
        if len(unique_ranking) > 1:
            merge_reasons.append(
                "single StandardProjection cannot carry conflicting ranking parameters"
            )

        if merge_reasons:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=tuple(dict.fromkeys(merge_reasons)),
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
