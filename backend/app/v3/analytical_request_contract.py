"""Dima V1 material analytical request invariants.

This is deliberately not a query planner. It carries only the already-accepted
business request invariants that must survive native Metabot implementation.
SQL, MBQL, join plans, aggregation implementation, temporal implementation and
query optimality are outside this module's authority.
"""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytics_contract import (
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedRanking,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AnalyticalScopeIdentity(FrozenModel):
    lineage_id: str = Field(min_length=1)
    version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")


class AnalyticalFilterInvariant(FrozenModel):
    semantic_ref: str = Field(min_length=1)
    source_candidate_id: str = Field(min_length=1)
    dimension_name: str = Field(min_length=1)
    value: str


class AnalyticalPeriodInvariant(FrozenModel):
    kind: str = Field(min_length=1)
    time_dimension: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str | None = None


class AnalyticalComparisonInvariant(FrozenModel):
    mode: str = Field(min_length=1)
    base_period: AnalyticalPeriodInvariant
    reference_period: AnalyticalPeriodInvariant


class AnalyticalRankingInvariant(FrozenModel):
    measure: str = Field(min_length=1)
    direction: str = Field(pattern=r"^(asc|desc)$")
    limit: int = Field(ge=1, le=1000)


class AnalyticalRequestContract(FrozenModel):
    authority_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    scope_identity: AnalyticalScopeIdentity
    metric_refs: tuple[str, ...] = Field(min_length=1)
    dimension_refs: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterInvariant, ...] = ()
    period: AnalyticalPeriodInvariant | None = None
    comparison: AnalyticalComparisonInvariant | None = None
    ranking: AnalyticalRankingInvariant | None = None
    grain_constraints: tuple[str, ...] = ()
    requested_output_surfaces: tuple[str, ...] = ()


class AnalyticalRequestObservation(FrozenModel):
    """Engine-reported material semantics, never physical query implementation."""

    scope_identity: AnalyticalScopeIdentity
    metric_refs: tuple[str, ...] = Field(min_length=1)
    dimension_refs: tuple[str, ...] = ()
    filters: tuple[AnalyticalFilterInvariant, ...] = ()
    period: AnalyticalPeriodInvariant | None = None
    comparison: AnalyticalComparisonInvariant | None = None
    ranking: AnalyticalRankingInvariant | None = None
    grain_constraints: tuple[str, ...] = ()
    requested_output_surfaces: tuple[str, ...] = ()


class NativeAnalyticalRequestObservation(FrozenModel):
    """Material semantic observation bound to one exact native occurrence.

    The semantics are compared to AnalyticalRequestContract. The identity fields
    bind that observation to the exact engine attestation/artifact; no SQL/MBQL
    representation is carried or interpreted here.
    """

    attestation_id: str = Field(min_length=1)
    native_conversation_id: UUID
    native_query_id: str = Field(min_length=1)
    exact_artifact_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    request: AnalyticalRequestObservation


class AnalyticalRequestMismatch(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _period(value: ResolvedPeriod) -> AnalyticalPeriodInvariant:
    return AnalyticalPeriodInvariant(
        kind=value.kind,
        time_dimension=value.time_dimension,
        start=value.start,
        end=value.end,
    )


def _comparison(value: ResolvedComparison) -> AnalyticalComparisonInvariant:
    return AnalyticalComparisonInvariant(
        mode=value.mode,
        base_period=_period(value.base_period),
        reference_period=_period(value.reference_period),
    )


def _ranking(value: ResolvedRanking) -> AnalyticalRankingInvariant:
    return AnalyticalRankingInvariant(
        measure=value.measure,
        direction=value.direction,
        limit=value.limit,
    )


def _filter(value: ResolvedFilterRef) -> AnalyticalFilterInvariant:
    return AnalyticalFilterInvariant(
        semantic_ref=value.semantic_ref,
        source_candidate_id=value.source_candidate_id,
        dimension_name=value.dimension_name,
        value=value.value,
    )


def analytical_request_contract_from_intent(
    intent: ResolvedAnalyticsIntent,
    *,
    scope_lineage_id: str,
    scope_version_id: str,
    requested_output_surfaces: tuple[str, ...] = (),
) -> AnalyticalRequestContract:
    """Project accepted material invariants without inspecting a query artifact."""

    return AnalyticalRequestContract(
        authority_id=intent.authority_id,
        request_ref=intent.request_ref,
        semantic_context_version=intent.semantic_context_version,
        scope_identity=AnalyticalScopeIdentity(
            lineage_id=scope_lineage_id,
            version_id=scope_version_id,
        ),
        metric_refs=tuple(item.semantic_ref for item in intent.metrics),
        dimension_refs=tuple(item.semantic_ref for item in intent.dimensions),
        filters=tuple(_filter(item) for item in intent.filters),
        period=_period(intent.period) if intent.period is not None else None,
        comparison=(
            _comparison(intent.comparison)
            if intent.comparison is not None
            else None
        ),
        ranking=_ranking(intent.ranking) if intent.ranking is not None else None,
        grain_constraints=intent.grain_constraints,
        requested_output_surfaces=tuple(
            dict.fromkeys(requested_output_surfaces)
        ),
    )


def observation_from_contract(
    contract: AnalyticalRequestContract,
) -> AnalyticalRequestObservation:
    """Test/adapter seam for a native semantic observation with no query-plan facts."""

    return AnalyticalRequestObservation(
        scope_identity=contract.scope_identity,
        metric_refs=contract.metric_refs,
        dimension_refs=contract.dimension_refs,
        filters=contract.filters,
        period=contract.period,
        comparison=contract.comparison,
        ranking=contract.ranking,
        grain_constraints=contract.grain_constraints,
        requested_output_surfaces=contract.requested_output_surfaces,
    )


def native_observation_from_contract(
    contract: AnalyticalRequestContract,
    *,
    attestation_id: str,
    native_conversation_id: UUID | str,
    native_query_id: str,
    exact_artifact_fingerprint: str,
) -> NativeAnalyticalRequestObservation:
    """Adapter/test seam for already-observed native material semantics."""

    return NativeAnalyticalRequestObservation(
        attestation_id=attestation_id,
        native_conversation_id=native_conversation_id,
        native_query_id=native_query_id,
        exact_artifact_fingerprint=exact_artifact_fingerprint,
        request=observation_from_contract(contract),
    )



def _filter_identity(
    value: AnalyticalFilterInvariant,
) -> tuple[str, str, str, str]:
    return (
        value.semantic_ref,
        value.source_candidate_id,
        value.dimension_name,
        value.value,
    )


def _set_is_narrowing_or_extension(
    parent_values,
    child_values,
) -> bool:
    parent_set = set(parent_values)
    child_set = set(child_values)
    return (
        parent_set.issubset(child_set)
        or child_set.issubset(parent_set)
    )


def assert_child_request_scope(
    parent: AnalyticalRequestContract,
    child: AnalyticalRequestContract,
) -> None:
    """Validate one typed P17 child scope without creating a second planner.

    Child execution stays inside the same accepted authority/context/version.
    It may retain the parent material scope or explicitly narrow/extend exactly
    one set-like analytical family. Time, comparison, ranking and output intent
    require a versioned ResearchScope change rather than a P17 child mutation.
    """

    immutable_checks = (
        ("AUTHORITY", parent.authority_id, child.authority_id),
        (
            "SEMANTIC_CONTEXT",
            parent.semantic_context_version,
            child.semantic_context_version,
        ),
        ("SCOPE", parent.scope_identity, child.scope_identity),
    )
    for label, expected, actual in immutable_checks:
        if expected != actual:
            raise AnalyticalRequestMismatch(
                f"ANALYTICAL_CHILD_{label}_MISMATCH",
                f"P17 child changed accepted {label.lower()} identity",
            )

    if parent.period != child.period:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_TIME_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted time without a scope version change",
        )
    if parent.comparison != child.comparison:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_COMPARISON_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted comparison intent",
        )
    if parent.ranking != child.ranking:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_RANKING_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted ranking basis",
        )
    if parent.requested_output_surfaces != child.requested_output_surfaces:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_OUTPUT_MUTATION_FORBIDDEN",
            "P17 child cannot change accepted output surfaces",
        )

    changed: list[tuple[str, tuple, tuple]] = []
    if parent.metric_refs != child.metric_refs:
        changed.append(("METRIC", parent.metric_refs, child.metric_refs))

    dimension_changed = (
        parent.dimension_refs != child.dimension_refs
        or parent.grain_constraints != child.grain_constraints
    )
    if dimension_changed:
        if (
            parent.grain_constraints != parent.dimension_refs
            or child.grain_constraints != child.dimension_refs
        ):
            raise AnalyticalRequestMismatch(
                "ANALYTICAL_CHILD_DIMENSION_GRAIN_MISMATCH",
                "P17 child dimension mutation must preserve dimension/grain identity",
            )
        changed.append(
            ("DIMENSION", parent.dimension_refs, child.dimension_refs)
        )

    parent_filters = tuple(_filter_identity(x) for x in parent.filters)
    child_filters = tuple(_filter_identity(x) for x in child.filters)
    if parent_filters != child_filters:
        changed.append(("FILTER", parent_filters, child_filters))

    if len(changed) > 1:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_MULTI_DIMENSION_MUTATION",
            "P17 child may narrow or extend only one analytical family",
        )
    if not changed:
        return

    label, expected, actual = changed[0]
    if label == "METRIC" and not actual:
        raise AnalyticalRequestMismatch(
            "ANALYTICAL_CHILD_METRIC_SCOPE_EMPTY",
            "P17 child must retain at least one accepted metric",
        )
    if not _set_is_narrowing_or_extension(expected, actual):
        raise AnalyticalRequestMismatch(
            f"ANALYTICAL_CHILD_{label}_REPLACEMENT_FORBIDDEN",
            (
                "P17 child scope must be a typed narrowing/extension, "
                "not an unrelated replacement"
            ),
        )


def assert_request_invariants(
    contract: AnalyticalRequestContract,
    observation: AnalyticalRequestObservation,
) -> None:
    checks = (
        ("SCOPE", contract.scope_identity, observation.scope_identity),
        ("METRIC", contract.metric_refs, observation.metric_refs),
        ("DIMENSION", contract.dimension_refs, observation.dimension_refs),
        ("FILTER", contract.filters, observation.filters),
        ("TIME", contract.period, observation.period),
        ("COMPARISON", contract.comparison, observation.comparison),
        ("RANKING", contract.ranking, observation.ranking),
        ("GRAIN", contract.grain_constraints, observation.grain_constraints),
        (
            "OUTPUT_SURFACE",
            contract.requested_output_surfaces,
            observation.requested_output_surfaces,
        ),
    )
    for label, expected, actual in checks:
        if expected != actual:
            raise AnalyticalRequestMismatch(
                f"ANALYTICAL_REQUEST_{label}_MISMATCH",
                f"accepted {label.lower()} invariant changed",
            )
