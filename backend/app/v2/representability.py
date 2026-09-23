"""Deterministic representability proof over typed authority/bindings.

STANDARD_LOSSLESS means one concrete StandardProjection can represent every active
standard executable obligation without dropping capability-specific requirements.

A missing/incomplete standard projection is a StandardBuilder problem, not automatically
a Research-routing decision. RESEARCH_REQUIRED is reserved for accepted research-only
capabilities.
"""

from __future__ import annotations

from app.v2.capability_bindings import BoundObligation
from app.v2.manager_models import (
    AcceptedTurnContract,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationPolarity,
    ObligationStatus,
    RepresentabilityDecision,
    RepresentabilityResult,
    StandardProjection,
    UserObligationLedger,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityLane,
    ManagerCapabilityRegistry,
)


class RepresentabilityGate:
    def __init__(self, registry: ManagerCapabilityRegistry | None = None) -> None:
        self._registry = registry or ManagerCapabilityRegistry()

    @staticmethod
    def _active(item: BoundObligation) -> bool:
        return getattr(item, "status", None) != ObligationStatus.SUPERSEDED

    def decide_bound(
        self,
        *,
        obligations: tuple[CandidateObligation, ...],
        projection: StandardProjection | None = None,
    ) -> RepresentabilityResult:
        """Lightweight StandardBuilder proof without Research contract/UOL."""
        return self._decide_items(
            items=obligations,
            authority_ids=tuple(item.obligation_id for item in obligations),
            projection=projection,
            unresolved=False,
        )

    def decide(
        self,
        *,
        contract: AcceptedTurnContract,
        ledger: UserObligationLedger,
        projection: StandardProjection | None = None,
    ) -> RepresentabilityResult:
        """Compatibility wrapper for the existing Research authority path."""
        if contract.lineage_id != ledger.lineage_id or contract.version != ledger.version:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("contract/ledger lineage mismatch",),
            )

        return self._decide_items(
            items=ledger.items,
            authority_ids=tuple(
                dict.fromkeys((*contract.obligation_ids, *contract.exclusion_ids))
            ),
            projection=projection,
            unresolved=bool(contract.unresolved_ids),
        )

    def decide_execution_slice(
        self,
        *,
        contract: AcceptedTurnContract,
        ledger: UserObligationLedger,
        obligation_ids: tuple[str, ...],
        projection: StandardProjection | None = None,
    ) -> RepresentabilityResult:
        """Prove one task-local Standard sub-analysis inside accepted Research authority.

        This does NOT weaken whole-authority Standard losslessness.  It only scopes the
        proof to obligations explicitly selected for this ResearchTask execution; the
        full ledger remains CompletionGate truth and unselected USER_MUST obligations
        remain outstanding.
        """
        if contract.lineage_id != ledger.lineage_id or contract.version != ledger.version:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("contract/ledger lineage mismatch",),
            )

        selected_ids = tuple(dict.fromkeys(obligation_ids))
        if not selected_ids:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("Research execution slice has no selected obligations",),
            )

        accepted_ids = set(contract.obligation_ids)
        outside = set(selected_ids) - accepted_ids
        if outside:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=(
                    "Research execution slice references obligations outside accepted authority: "
                    + ", ".join(sorted(outside)),
                ),
            )

        item_by_id = {
            item.obligation_id: item
            for item in ledger.items
        }
        missing = set(selected_ids) - set(item_by_id)
        if missing:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=(
                    "Research execution slice references missing ledger obligations: "
                    + ", ".join(sorted(missing)),
                ),
            )

        selected_items = tuple(item_by_id[item_id] for item_id in selected_ids)
        return self._decide_items(
            items=selected_items,
            authority_ids=selected_ids,
            projection=projection,
            unresolved=bool(contract.unresolved_ids),
        )

    def _decide_items(
        self,
        *,
        items: tuple[BoundObligation, ...],
        authority_ids: tuple[str, ...],
        projection: StandardProjection | None,
        unresolved: bool,
    ) -> RepresentabilityResult:
        if unresolved:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.CLARIFICATION_REQUIRED,
                reasons=("accepted authority still contains unresolved obligations",),
            )

        allowed = set(authority_ids)
        active = [
            item
            for item in items
            if self._active(item)
            and item.obligation_id in allowed
            and item.polarity == ObligationPolarity.REQUIRED
        ]

        if any(
            getattr(item, "status", None) == ObligationStatus.NEEDS_CLARIFICATION
            for item in active
        ):
            return RepresentabilityResult(
                decision=RepresentabilityDecision.CLARIFICATION_REQUIRED,
                reasons=("active obligation requires clarification",),
            )
        if any(
            getattr(item, "status", None) == ObligationStatus.UNSUPPORTED
            for item in active
        ):
            return RepresentabilityResult(
                decision=RepresentabilityDecision.UNSUPPORTED,
                reasons=("active obligation is unsupported",),
            )

        executable: list[BoundObligation] = []
        standard: list[ManagerCapabilityKey] = []
        research: list[ManagerCapabilityKey] = []
        for item in active:
            spec = self._registry.get(item.capability_key)
            if spec.execution_mode in {
                ManagerCapabilityExecutionMode.DEFERRED,
                ManagerCapabilityExecutionMode.PRESENTATION,
            }:
                continue
            if spec.execution_mode == ManagerCapabilityExecutionMode.ORCHESTRATED:
                research.append(item.capability_key)
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
                reasons=("accepted authority has no executable analytical capability",),
            )

        if projection is None:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.STANDARD_BUILD_REQUIRED,
                reasons=("standard projection has not been supplied yet",),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
            )

        return self._prove_standard_projection(
            authority_ids=set(authority_ids),
            executable=tuple(executable),
            standard=tuple(standard),
            projection=projection,
        )

    def _prove_standard_projection(
        self,
        *,
        authority_ids: set[str],
        executable: tuple[BoundObligation, ...],
        standard: tuple[ManagerCapabilityKey, ...],
        projection: StandardProjection,
    ) -> RepresentabilityResult:
        reasons: list[str] = []
        expected_ids = {item.obligation_id for item in executable}
        supplied_ids = set(projection.obligation_ids)

        unknown = supplied_ids - authority_ids
        if unknown:
            reasons.append(
                "projection references obligations outside accepted authority: "
                + ", ".join(sorted(unknown))
            )

        missing = expected_ids - supplied_ids
        if missing:
            reasons.append(
                "projection drops executable obligations: "
                + ", ".join(sorted(missing))
            )

        if not projection.metric_handles:
            reasons.append("standard projection requires at least one metric handle")

        projection_handles = {
            *projection.metric_handles,
            *projection.dimension_handles,
            *projection.filter_handles,
            *(() if projection.period_handle is None else (projection.period_handle,)),
            *(
                ()
                if projection.comparison_handle is None
                else (projection.comparison_handle,)
            ),
        }

        for item in executable:
            if item.obligation_id not in supplied_ids:
                continue

            missing_bindings = set(item.semantic_handle_refs) - projection_handles
            if missing_bindings:
                reasons.append(
                    f"{item.obligation_id}: projection misses accepted semantic bindings "
                    + ", ".join(sorted(missing_bindings))
                )

            capability = item.capability_key
            if capability == ManagerCapabilityKey.PERFORMANCE:
                if not projection.metric_handles:
                    reasons.append(f"{item.obligation_id}: performance requires metric")
            elif capability == ManagerCapabilityKey.BREAKDOWN:
                if not projection.metric_handles or not projection.dimension_handles:
                    reasons.append(
                        f"{item.obligation_id}: breakdown requires metric + dimension"
                    )
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
                    f"{item.obligation_id}: capability is not standard-projectable: "
                    f"{capability.value}"
                )

        if reasons:
            return RepresentabilityResult(
                decision=RepresentabilityDecision.STANDARD_BUILD_REQUIRED,
                reasons=tuple(dict.fromkeys(reasons)),
                standard_capability_keys=tuple(dict.fromkeys(standard)),
            )

        return RepresentabilityResult(
            decision=RepresentabilityDecision.STANDARD_LOSSLESS,
            reasons=(
                "one complete StandardProjection covers every executable standard obligation",
            ),
            standard_capability_keys=tuple(dict.fromkeys(standard)),
            standard_projection=projection,
        )
