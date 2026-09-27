"""Deterministic StandardProjection compiler for Day 6.5.

The compiler consumes already-grounded standard binding atoms plus Resolver/BindingGate-issued
opaque SemanticHandles. It does not infer user language and does not create semantic authority.

The legacy Research wrapper remains supported so existing AcceptedTurnContract + UOL behavior
is preserved while StandardBuilder uses the lightweight bound-input path.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.v2.capability_bindings import (
    BoundObligation,
    CapabilityBinding,
    CapabilityBindingValidator,
)
from app.v2.manager_models import (
    AcceptedTurnContract,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationLedgerItem,
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


@dataclass(frozen=True)
class StandardProjectionInput:
    """Lightweight accepted/bound input for StandardBuilder.

    This is intentionally not a second research contract. It is only the set of atomic
    standard obligations that the deterministic compiler must merge into one projection.
    """

    authority_ids: tuple[str, ...]
    items: tuple[BoundObligation, ...]
    context_version: str


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

    @staticmethod
    def _active(item: BoundObligation) -> bool:
        status = getattr(item, "status", None)
        return status != ObligationStatus.SUPERSEDED

    def compile_bound(
        self,
        *,
        obligations: tuple[CandidateObligation, ...],
        tenant_binding: str,
        context_version: str,
    ) -> StandardProjectionCompileResult:
        """Compile a lightweight StandardBuilder proposal without Research UOL machinery."""
        return self.compile_input(
            standard_input=StandardProjectionInput(
                authority_ids=tuple(item.obligation_id for item in obligations),
                items=obligations,
                context_version=context_version,
            ),
            tenant_binding=tenant_binding,
            context_version=context_version,
        )

    def compile(
        self,
        *,
        contract: AcceptedTurnContract,
        ledger: UserObligationLedger,
        tenant_binding: str,
        context_version: str,
    ) -> StandardProjectionCompileResult:
        """Compatibility wrapper for the existing Research authority path."""
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

        return self.compile_input(
            standard_input=StandardProjectionInput(
                authority_ids=tuple(
                    dict.fromkeys(
                        (*contract.obligation_ids, *contract.exclusion_ids)
                    )
                ),
                items=ledger.items,
                context_version=contract.context_version,
            ),
            tenant_binding=tenant_binding,
            context_version=context_version,
        )

    def compile_input(
        self,
        *,
        standard_input: StandardProjectionInput,
        tenant_binding: str,
        context_version: str,
    ) -> StandardProjectionCompileResult:
        reasons: list[str] = []

        if standard_input.context_version != context_version:
            return StandardProjectionCompileResult(
                projection=None,
                reasons=("standard input/context version mismatch",),
            )

        item_by_id: dict[str, BoundObligation] = {}
        duplicate_ids: set[str] = set()
        for item in standard_input.items:
            if not self._active(item):
                continue
            if item.obligation_id in item_by_id:
                duplicate_ids.add(item.obligation_id)
            item_by_id[item.obligation_id] = item

        if duplicate_ids:
            reasons.append(
                "duplicate standard obligation ids: "
                + ", ".join(sorted(duplicate_ids))
            )

        authority_ids = tuple(dict.fromkeys(standard_input.authority_ids))
        missing_ids = set(authority_ids) - set(item_by_id)
        if missing_ids:
            reasons.append(
                "standard authority references missing obligation atoms: "
                + ", ".join(sorted(missing_ids))
            )

        authoritative_items = [
            item_by_id[item_id]
            for item_id in authority_ids
            if item_id in item_by_id
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
        ]

        executable: list[BoundObligation] = []
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
            reasons.append("standard input has no executable standard obligation")

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
