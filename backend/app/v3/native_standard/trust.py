"""P13B/P13C provider-free native Standard trust orchestration.

Metabase owns query cognition and MBQL observation. This module maps already-attested
physical facts to Dima-owned semantics, delegates authorization to P13A, effective
access identity to P10, and receipt sealing to P5. It never parses or rewrites MBQL.
"""
from __future__ import annotations

import copy
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionAccessSnapshot,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.native_execution import (
    ExecutionResourceBinding,
    NativeCandidateAuthorization,
    NativeCandidateAuthorizationGate,
    NativeCandidateOutcome,
    NativeQueryCandidate,
    filter_scope_fingerprint,
    period_scope_fingerprint,
)
from app.v3.entity_value_gate import (
    CurrentLensValueEvidence,
    EntityValueAdoptionGate,
    EntityValueDecision,
    EntityValueProposal,
)
from app.v3.resource_provisioning import ManagedResourceBinding, ResourceKind
from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    SecurityIdentityError,
    VerifiedExecutionSecurityFacts,
)
from app.v3.semantic_spec import DimensionSpec, MetricSpec, SourceLineage
from app.v3.substrate.metabase.execution_binding import (
    CurrentCatalogObject,
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal

from .contracts import (
    NativeAttestationEnvelope,
    NativeDatasetExecutionRequest,
    NativeExecutionManifest,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class NativeStandardTrustError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class NativeStandardAuthorizationResult(FrozenModel):
    authorization: NativeCandidateAuthorization
    candidate: NativeQueryCandidate | None = None
    access_snapshot: ExecutionAccessSnapshot | None = None


def _block(code: str, detail: str) -> NativeCandidateAuthorization:
    return NativeCandidateAuthorization(
        outcome=NativeCandidateOutcome.BLOCK,
        code=code,
        detail=detail,
    )


def _single_lineage(item: MetricSpec | DimensionSpec) -> SourceLineage:
    if len(item.source_lineage) != 1:
        identity = getattr(item, "metric_id", getattr(item, "dimension_id", "semantic"))
        raise NativeStandardTrustError(
            "NATIVE_SEMANTIC_LINEAGE_UNSUPPORTED",
            f"{identity} must have exactly one source lineage for P13B-v1",
        )
    return item.source_lineage[0]


def _resource(current: CurrentCatalogObject) -> ExecutionResourceBinding:
    if not current.resource_entity_id:
        raise NativeStandardTrustError(
            "NATIVE_RESOURCE_IDENTITY_MISSING",
            f"current catalog object {current.source_id} has no resource entity id",
        )
    return ExecutionResourceBinding(
        resource_id=current.resource_entity_id,
        resource_fingerprint=current.resource_fingerprint,
    )


def _unique_resources(
    values: Iterable[ExecutionResourceBinding],
) -> tuple[ExecutionResourceBinding, ...]:
    by_id: dict[str, ExecutionResourceBinding] = {}
    for value in values:
        prior = by_id.get(value.resource_id)
        if prior is not None and prior != value:
            raise NativeStandardTrustError(
                "NATIVE_RESOURCE_IDENTITY_CONFLICT",
                f"resource {value.resource_id} has conflicting fingerprints",
            )
        by_id[value.resource_id] = value
    return tuple(by_id[key] for key in sorted(by_id))


class NativeStandardTrustOrchestrator:
    """P13B→P13D bounded verifier/orchestrator. No analytical planning lives here."""

    @staticmethod
    def _metric(snapshot: DimaExecutionBindingSnapshot, metric_id: str) -> MetricSpec:
        matches = [x for x in snapshot.semantic_spec.metrics if x.metric_id == metric_id]
        if len(matches) != 1:
            raise NativeStandardTrustError(
                "NATIVE_EXPECTED_METRIC_BINDING_INVALID",
                f"Dima metric {metric_id!r} is not uniquely defined",
            )
        return matches[0]

    @staticmethod
    def _dimension(
        snapshot: DimaExecutionBindingSnapshot,
        dimension_id: str,
    ) -> DimensionSpec:
        matches = [
            x for x in snapshot.semantic_spec.dimensions
            if x.dimension_id == dimension_id
        ]
        if len(matches) != 1:
            raise NativeStandardTrustError(
                "NATIVE_EXPECTED_TIME_BINDING_INVALID",
                f"Dima dimension {dimension_id!r} is not uniquely defined",
            )
        return matches[0]

    @classmethod
    def _expected(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
    ) -> tuple[
        MetricSpec,
        DimensionSpec | None,
        DimensionSpec | None,
        DimensionSpec | None,
        tuple[ExecutionResourceBinding, ...],
    ]:
        if (
            len(intent.metrics) != 1
            or len(intent.dimensions) > 1
            or len(intent.filters) > 1
            or intent.comparison is not None
            or intent.approved_relationship_paths
            or intent.grain_constraints
        ):
            raise NativeStandardTrustError(
                "P13_STANDARD_CAPABILITY_UNSUPPORTED",
                "certified native Standard surface is one metric/source, at most one dimension/filter, optional period, and bounded ranking",
            )
        if intent.ranking is not None and len(intent.dimensions) != 1:
            raise NativeStandardTrustError(
                "P13D_RANKING_REQUIRES_DIMENSION",
                "ranking requires exactly one accepted breakout dimension",
            )

        metric_ref = intent.metrics[0]
        metric = cls._metric(
            snapshot,
            snapshot.candidate(metric_ref.source_candidate_id, kind="metric"),
        )
        if metric.name != metric_ref.canonical_name:
            raise NativeStandardTrustError(
                "NATIVE_EXPECTED_METRIC_BINDING_INVALID",
                "accepted metric canonical name differs from its Dima semantic binding",
            )
        metric_current = snapshot.current_lineage(_single_lineage(metric))
        resources = [_resource(metric_current)]

        breakout_dimension = None
        if intent.dimensions:
            dimension_ref = intent.dimensions[0]
            breakout_dimension = cls._dimension(
                snapshot,
                snapshot.candidate(
                    dimension_ref.source_candidate_id,
                    kind="dimension",
                ),
            )
            if breakout_dimension.name != dimension_ref.canonical_name:
                raise NativeStandardTrustError(
                    "NATIVE_EXPECTED_DIMENSION_BINDING_INVALID",
                    "accepted dimension canonical name differs from its Dima semantic binding",
                )
            resources.append(
                _resource(snapshot.current_lineage(_single_lineage(breakout_dimension)))
            )

        time_dimension = None
        if intent.period is not None:
            time_dimension = cls._dimension(
                snapshot,
                snapshot.temporal_dimension(intent.period.time_dimension),
            )
            resources.append(
                _resource(snapshot.current_lineage(_single_lineage(time_dimension)))
            )

        filter_dimension = None
        if intent.filters:
            accepted_filter = intent.filters[0]
            filter_dimension = cls._dimension(
                snapshot,
                snapshot.candidate(
                    accepted_filter.source_candidate_id,
                    kind="filter",
                ),
            )
            if filter_dimension.name != accepted_filter.dimension_name:
                raise NativeStandardTrustError(
                    "FILTER_SCOPE_VIOLATION",
                    "accepted filter dimension name differs from its Dima semantic binding",
                )
            resources.append(
                _resource(snapshot.current_lineage(_single_lineage(filter_dimension)))
            )

        return (
            metric,
            breakout_dimension,
            time_dimension,
            filter_dimension,
            _unique_resources(resources),
        )


    @staticmethod
    def _assert_engine_pin(
        manifest: NativeExecutionManifest,
        expected: NativeEngineIdentity,
    ) -> None:
        actual = manifest.runtime_identity
        checks = [
            ("repository", expected.repository, actual.repository),
            ("engine_sha", expected.engine_sha, actual.revision_sha),
            ("upstream_base_sha", expected.upstream_base_sha, actual.upstream_base_sha),
            ("runtime_tag", expected.runtime_tag, actual.runtime_tag),
        ]
        optional = (
            ("build_identity", expected.build_identity, actual.build_identity),
            (
                "runtime_image_identity",
                expected.runtime_image_identity,
                actual.image_identity,
            ),
            (
                "runtime_instance_id",
                expected.runtime_instance_id,
                actual.runtime_instance_id,
            ),
        )
        checks.extend((name, exp, got) for name, exp, got in optional if exp is not None)
        for name, exp, got in checks:
            if str(exp) != str(got):
                raise NativeStandardTrustError(
                    "NATIVE_ENGINE_PIN_MISMATCH",
                    f"{name}: expected={exp!r} observed={got!r}",
                )

    @staticmethod
    def _assert_shape(manifest: NativeExecutionManifest) -> None:
        if manifest.material_query_count != 1 or manifest.stage_count != 1:
            raise NativeStandardTrustError(
                "QUERY_COUNT_VIOLATION",
                "native Standard requires one material query and one query stage",
            )
        if manifest.explicit_join_count or manifest.implicit_join_count:
            raise NativeStandardTrustError(
                "RELATIONSHIP_GRAIN_VIOLATION",
                "current P13D slice blocks explicit and implicit relationships",
            )


    @staticmethod
    def _observed_table(
        manifest: NativeExecutionManifest,
        snapshot: DimaExecutionBindingSnapshot,
    ) -> CurrentCatalogObject:
        table_id = manifest.primary_source_table_id
        if table_id is None:
            raise NativeStandardTrustError(
                "NATIVE_PRIMARY_SOURCE_MISSING",
                "native manifest has no primary source table",
            )
        if tuple(sorted(manifest.referenced_source_table_ids)) != (table_id,):
            raise NativeStandardTrustError(
                "NATIVE_SOURCE_SCOPE_VIOLATION",
                "P13B-v1 requires exactly the primary source table",
            )
        return snapshot.current_catalog.object_for_metabase_table(
            database_id=manifest.database_id,
            table_id=table_id,
        )

    @staticmethod
    def _assert_exact_count_star(manifest: NativeExecutionManifest) -> None:
        if manifest.aggregation_count != 1 or len(manifest.aggregations) != 1:
            raise NativeStandardTrustError(
                "NATIVE_AGGREGATION_SCOPE_VIOLATION",
                "P13B-v1 requires exactly one aggregation",
            )
        agg = manifest.aggregations[0]
        if (
            agg.operator.lower() != "count"
            or agg.argument_kind != "all_rows"
            or agg.referenced_field_ids
            or agg.distinct
        ):
            raise NativeStandardTrustError(
                "NATIVE_AGGREGATION_MISMATCH",
                "PX-01 requires exact COUNT(*)",
            )

    @staticmethod
    def _native_metric_binding(
        *,
        manifest: NativeExecutionManifest,
        expected_metric: MetricSpec,
        tenant_binding: str,
        semantic_context_version: str,
        managed_resource_bindings: tuple[ManagedResourceBinding, ...],
    ) -> ManagedResourceBinding | None:
        refs = manifest.native_metric_references
        if not refs:
            return None
        if len(refs) != 1:
            raise NativeStandardTrustError(
                "NATIVE_METRIC_REFERENCE_SCOPE_VIOLATION",
                "P13B-v1 certifies exactly one native metric reference",
            )
        ref = refs[0]
        if ref.stage_number != 0 or ref.aggregation_index != 0:
            raise NativeStandardTrustError(
                "NATIVE_METRIC_REFERENCE_SCOPE_VIOLATION",
                "P13B-v1 native metric must be the sole first-stage aggregation",
            )

        matches = [
            binding
            for binding in managed_resource_bindings
            if (
                binding.tenant_binding == tenant_binding
                and binding.resource_kind == ResourceKind.METRIC
                and binding.canonical_id == expected_metric.metric_id
            )
        ]
        if len(matches) != 1:
            raise NativeStandardTrustError(
                "NATIVE_METRIC_BINDING_MISSING"
                if not matches
                else "NATIVE_METRIC_BINDING_AMBIGUOUS",
                (
                    f"expected one Dima-managed binding for {expected_metric.metric_id}, "
                    f"observed {len(matches)}"
                ),
            )
        binding = matches[0]
        if binding.ownership != "DIMA_MANAGED":
            raise NativeStandardTrustError(
                "NATIVE_METRIC_BINDING_OWNERSHIP_INVALID",
                "native metric binding is not DIMA_MANAGED",
            )
        if (
            binding.semantic_context_version != semantic_context_version
            or binding.applied_version != expected_metric.semantic_version
        ):
            raise NativeStandardTrustError(
                "NATIVE_METRIC_BINDING_STALE",
                "native metric binding semantic context/version is stale",
            )
        if (
            binding.metabase_local_id != ref.metabase_metric_id
            or binding.metabase_entity_id != ref.metabase_metric_entity_id
        ):
            raise NativeStandardTrustError(
                "NATIVE_METRIC_BINDING_IDENTITY_MISMATCH",
                "engine-attested native metric identity differs from the P9 binding",
            )
        return binding

    @classmethod
    def _observed_metric(
        cls,
        *,
        manifest: NativeExecutionManifest,
        snapshot: DimaExecutionBindingSnapshot,
        observed_table: CurrentCatalogObject,
        expected_metric: MetricSpec,
        tenant_binding: str,
        managed_resource_bindings: tuple[ManagedResourceBinding, ...],
    ) -> tuple[MetricSpec, ManagedResourceBinding | None]:
        cls._assert_exact_count_star(manifest)

        metric_binding = cls._native_metric_binding(
            manifest=manifest,
            expected_metric=expected_metric,
            tenant_binding=tenant_binding,
            semantic_context_version=snapshot.semantic_context_version,
            managed_resource_bindings=managed_resource_bindings,
        )
        if metric_binding is not None:
            if (
                expected_metric.aggregation.strip().lower() not in {"count", "count(*)"}
                or expected_metric.formula is not None
            ):
                raise NativeStandardTrustError(
                    "NATIVE_EXPECTED_METRIC_DEFINITION_MISMATCH",
                    "bound Dima metric is not the canonical COUNT(*) metric",
                )
            expected_table = snapshot.current_lineage(_single_lineage(expected_metric))
            if (
                expected_table.database_ref != observed_table.database_ref
                or expected_table.schema_name != observed_table.schema_name
                or expected_table.table_name != observed_table.table_name
                or expected_table.column_name is not None
                or expected_table.metabase_database_id != manifest.database_id
                or expected_table.metabase_table_id != manifest.primary_source_table_id
            ):
                raise NativeStandardTrustError(
                    "NATIVE_METRIC_SOURCE_BINDING_MISMATCH",
                    "bound native metric expanded against a different physical source",
                )
            return expected_metric, metric_binding

        matches: list[MetricSpec] = []
        for metric in snapshot.semantic_spec.metrics:
            if metric.aggregation.strip().lower() not in {"count", "count(*)"}:
                continue
            if metric.formula is not None or len(metric.source_lineage) != 1:
                continue
            try:
                current = snapshot.current_lineage(metric.source_lineage[0])
            except MetabaseCompilationBlocked:
                continue
            if (
                current.database_ref == observed_table.database_ref
                and current.schema_name == observed_table.schema_name
                and current.table_name == observed_table.table_name
                and current.column_name is None
                and current.metabase_database_id == manifest.database_id
                and current.metabase_table_id == manifest.primary_source_table_id
            ):
                matches.append(metric)
        if len(matches) != 1:
            raise NativeStandardTrustError(
                "NATIVE_OBSERVED_METRIC_UNMAPPED",
                f"observed COUNT(*) maps to {len(matches)} Dima metrics",
            )
        return matches[0], None

    @classmethod
    def _observed_time(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        manifest: NativeExecutionManifest,
        snapshot: DimaExecutionBindingSnapshot,
    ) -> DimensionSpec | None:
        if intent.period is None:
            if manifest.temporal_predicates:
                raise NativeStandardTrustError(
                    "TIME_SCOPE_VIOLATION",
                    "native query introduced time scope without accepted period",
                )
            return None
        if intent.period.end is None:
            raise NativeStandardTrustError(
                "P13B_CAPABILITY_UNSUPPORTED",
                "P13B-v1 requires an explicit exclusive period end",
            )
        predicates = manifest.temporal_predicates
        if len(predicates) != 2:
            raise NativeStandardTrustError(
                "TIME_SCOPE_VIOLATION",
                "P13B-v1 requires exactly lower and upper temporal predicates",
            )
        field_ids = {x.time_field_id for x in predicates}
        if len(field_ids) != 1:
            raise NativeStandardTrustError(
                "TIME_SCOPE_VIOLATION",
                "temporal predicates reference different fields",
            )
        lower = next((x for x in predicates if x.operator == ">="), None)
        upper = next((x for x in predicates if x.operator == "<"), None)
        if lower is None or upper is None:
            raise NativeStandardTrustError(
                "TIME_SCOPE_VIOLATION",
                "P13B-v1 requires >= lower and < upper predicates",
            )
        if (
            lower.lower_bound != intent.period.start
            or lower.lower_inclusive is not True
            or lower.upper_bound is not None
            or upper.upper_bound != intent.period.end
            or upper.upper_inclusive is not False
            or upper.lower_bound is not None
        ):
            raise NativeStandardTrustError(
                "TIME_SCOPE_VIOLATION",
                "observed temporal bounds differ from accepted half-open period",
            )
        observed_field = snapshot.current_catalog.object_for_metabase_field(
            database_id=manifest.database_id,
            field_id=next(iter(field_ids)),
        )
        matches: list[DimensionSpec] = []
        for dimension in snapshot.semantic_spec.dimensions:
            if len(dimension.source_lineage) != 1:
                continue
            try:
                current = snapshot.current_lineage(dimension.source_lineage[0])
            except MetabaseCompilationBlocked:
                continue
            if current == observed_field:
                matches.append(dimension)
        if len(matches) != 1:
            raise NativeStandardTrustError(
                "NATIVE_OBSERVED_TIME_UNMAPPED",
                f"observed time field maps to {len(matches)} Dima dimensions",
            )
        return matches[0]

    @classmethod
    def _observed_filter(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        manifest: NativeExecutionManifest,
        snapshot: DimaExecutionBindingSnapshot,
        expected_filter_dimension: DimensionSpec | None,
    ) -> DimensionSpec | None:
        if not intent.filters:
            if manifest.non_temporal_filter_count or manifest.textual_equality_predicates:
                raise NativeStandardTrustError(
                    "SEMANTIC_SCOPE_VIOLATION",
                    "native query introduced a non-temporal filter without accepted filter authority",
                )
            return None

        if manifest.non_temporal_filter_count != 1:
            raise NativeStandardTrustError(
                "P13C_FILTER_SCOPE_VIOLATION",
                "P13C-v1 requires exactly one material non-temporal filter",
            )
        if len(manifest.textual_equality_predicates) != 1:
            raise NativeStandardTrustError(
                "NATIVE_TEXTUAL_FILTER_ATTESTATION_GAP",
                "the one material non-temporal filter is not exactly covered by one typed textual equality predicate",
            )

        predicate = manifest.textual_equality_predicates[0]
        if predicate.stage_number != 0 or predicate.operator != "=":
            raise NativeStandardTrustError(
                "NATIVE_TEXTUAL_FILTER_SHAPE_UNSUPPORTED",
                "P13C-v1 certifies stage-0 exact textual equality only",
            )

        accepted_filter = intent.filters[0]
        if predicate.literal_value != accepted_filter.value:
            raise NativeStandardTrustError(
                "NATIVE_TEXTUAL_FILTER_VALUE_MISMATCH",
                "engine-observed native literal differs from accepted Dima filter value",
            )

        observed_field = snapshot.current_catalog.object_for_metabase_field(
            database_id=manifest.database_id,
            field_id=predicate.field_id,
        )
        if expected_filter_dimension is None:
            raise NativeStandardTrustError(
                "FILTER_SCOPE_VIOLATION",
                "accepted filter has no Dima dimension binding",
            )
        expected_field = snapshot.current_lineage(
            _single_lineage(expected_filter_dimension)
        )
        if observed_field != expected_field:
            raise NativeStandardTrustError(
                "NATIVE_TEXTUAL_FILTER_FIELD_MISMATCH",
                "engine-observed filter field differs from accepted Dima filter dimension",
            )
        return expected_filter_dimension

    @classmethod
    def _observed_breakout(
        cls,
        *,
        manifest: NativeExecutionManifest,
        snapshot: DimaExecutionBindingSnapshot,
        expected_dimension: DimensionSpec | None,
    ) -> DimensionSpec | None:
        if expected_dimension is None:
            if manifest.breakout_count or manifest.breakouts:
                raise NativeStandardTrustError(
                    "P13D_BREAKOUT_SCOPE_VIOLATION",
                    "native query introduced a breakout without accepted dimension authority",
                )
            return None

        if manifest.breakout_count != 1 or len(manifest.breakouts) != 1:
            raise NativeStandardTrustError(
                "P13D_BREAKOUT_SCOPE_VIOLATION",
                "P13D-v1 requires exactly one observed breakout",
            )
        breakout = manifest.breakouts[0]
        if breakout.stage_number != 0 or breakout.breakout_index != 0:
            raise NativeStandardTrustError(
                "P13D_BREAKOUT_SHAPE_UNSUPPORTED",
                "P13D-v1 certifies the sole stage-0 breakout",
            )
        observed_field = snapshot.current_catalog.object_for_metabase_field(
            database_id=manifest.database_id,
            field_id=breakout.field_id,
        )
        expected_field = snapshot.current_lineage(_single_lineage(expected_dimension))
        if observed_field != expected_field:
            raise NativeStandardTrustError(
                "P13D_BREAKOUT_FIELD_MISMATCH",
                "engine-observed breakout field differs from accepted Dima dimension lineage",
            )
        return expected_dimension

    @staticmethod
    def _observed_ranking(
        *,
        intent: ResolvedAnalyticsIntent,
        manifest: NativeExecutionManifest,
        expected_metric: MetricSpec,
        expected_dimension: DimensionSpec | None,
    ) -> None:
        ranking = intent.ranking
        if ranking is None:
            if manifest.order_by_count or manifest.order_bys or manifest.limit is not None:
                raise NativeStandardTrustError(
                    "P13D_RANKING_SCOPE_VIOLATION",
                    "native query introduced order/limit without accepted ranking authority",
                )
            return

        if expected_dimension is None:
            raise NativeStandardTrustError(
                "P13D_RANKING_REQUIRES_DIMENSION",
                "accepted ranking has no accepted breakout dimension",
            )
        if ranking.measure != expected_metric.name:
            raise NativeStandardTrustError(
                "P13D_RANKING_MEASURE_MISMATCH",
                "accepted ranking measure differs from the accepted metric",
            )
        if manifest.order_by_count != 1 or len(manifest.order_bys) != 1:
            raise NativeStandardTrustError(
                "P13D_RANKING_SCOPE_VIOLATION",
                "P13D-v1 requires exactly one explicit ranking order",
            )
        order = manifest.order_bys[0]
        if order.stage_number != 0 or order.order_index != 0:
            raise NativeStandardTrustError(
                "P13D_RANKING_SHAPE_UNSUPPORTED",
                "P13D-v1 certifies the sole stage-0 order",
            )
        if order.target_kind != "aggregation" or order.aggregation_index != 0:
            raise NativeStandardTrustError(
                "P13D_RANKING_TARGET_MISMATCH",
                "ranking must order the sole accepted metric aggregation",
            )
        if order.direction != ranking.direction:
            raise NativeStandardTrustError(
                "P13D_RANKING_DIRECTION_MISMATCH",
                "engine-observed ranking direction differs from accepted ranking",
            )
        if manifest.limit != ranking.limit:
            raise NativeStandardTrustError(
                "P13D_RANKING_LIMIT_MISMATCH",
                "engine-observed limit differs from accepted ranking limit",
            )


    @classmethod
    def _candidate(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
        attestation: NativeAttestationEnvelope,
        expected_engine: NativeEngineIdentity,
        dima_request_id: str,
        dima_trace_id: str,
        managed_resource_bindings: tuple[ManagedResourceBinding, ...],
    ) -> tuple[NativeQueryCandidate, tuple[ExecutionResourceBinding, ...]]:
        manifest = attestation.manifest
        cls._assert_engine_pin(manifest, expected_engine)
        cls._assert_shape(manifest)
        (
            expected_metric,
            expected_dimension,
            expected_time,
            expected_filter,
            expected_resources,
        ) = cls._expected(
            intent=intent,
            snapshot=snapshot,
        )

        observed_table = cls._observed_table(manifest, snapshot)
        observed_metric, metric_binding = cls._observed_metric(
            manifest=manifest,
            snapshot=snapshot,
            observed_table=observed_table,
            expected_metric=expected_metric,
            tenant_binding=intent.principal.tenant_binding,
            managed_resource_bindings=managed_resource_bindings,
        )
        if observed_metric.metric_id != expected_metric.metric_id:
            raise NativeStandardTrustError(
                "SEMANTIC_SCOPE_VIOLATION",
                "observed physical COUNT(*) maps to a different Dima metric",
            )

        observed_time = cls._observed_time(
            intent=intent,
            manifest=manifest,
            snapshot=snapshot,
        )
        if (
            (expected_time is None) != (observed_time is None)
            or (
                expected_time is not None
                and observed_time is not None
                and expected_time.dimension_id != observed_time.dimension_id
            )
        ):
            raise NativeStandardTrustError(
                "TIME_SCOPE_VIOLATION",
                "observed physical time field maps to a different Dima time dimension",
            )

        observed_filter = cls._observed_filter(
            intent=intent,
            manifest=manifest,
            snapshot=snapshot,
            expected_filter_dimension=expected_filter,
        )
        if (
            (expected_filter is None) != (observed_filter is None)
            or (
                expected_filter is not None
                and observed_filter is not None
                and expected_filter.dimension_id != observed_filter.dimension_id
            )
        ):
            raise NativeStandardTrustError(
                "FILTER_SCOPE_VIOLATION",
                "observed physical filter field maps to a different Dima filter dimension",
            )

        observed_dimension = cls._observed_breakout(
            manifest=manifest,
            snapshot=snapshot,
            expected_dimension=expected_dimension,
        )
        if (
            (expected_dimension is None) != (observed_dimension is None)
            or (
                expected_dimension is not None
                and observed_dimension is not None
                and expected_dimension.dimension_id != observed_dimension.dimension_id
            )
        ):
            raise NativeStandardTrustError(
                "P13D_BREAKOUT_SCOPE_VIOLATION",
                "observed breakout maps to a different Dima dimension",
            )

        cls._observed_ranking(
            intent=intent,
            manifest=manifest,
            expected_metric=expected_metric,
            expected_dimension=expected_dimension,
        )

        observed_resources = [_resource(observed_table)]
        if observed_time is not None:
            observed_resources.append(
                _resource(snapshot.current_lineage(_single_lineage(observed_time)))
            )
        if observed_dimension is not None:
            observed_resources.append(
                _resource(snapshot.current_lineage(_single_lineage(observed_dimension)))
            )
        if observed_filter is not None:
            observed_resources.append(
                _resource(snapshot.current_lineage(_single_lineage(observed_filter)))
            )

        runtime = manifest.runtime_identity
        native_validation_refs = [
            manifest.attestation_id,
            f"native-producer:{manifest.producer_tool}",
            f"native-permission:{manifest.permission_provenance.permission_check}",
            f"metabase-user:{manifest.authenticated_metabase_subject}",
        ]
        if metric_binding is not None:
            native_validation_refs.extend(
                [
                    f"native-metric:{metric_binding.metabase_entity_id}",
                    (
                        "dima-managed-metric:"
                        f"{metric_binding.canonical_id}:"
                        f"{metric_binding.semantic_context_version}:"
                        f"{metric_binding.applied_version}"
                    ),
                ]
            )
        candidate = NativeQueryCandidate.build(
            engine_identity=NativeEngineIdentity(
                repository=runtime.repository,
                engine_sha=runtime.revision_sha,
                upstream_base_sha=runtime.upstream_base_sha,
                runtime_tag=runtime.runtime_tag,
                build_identity=runtime.build_identity,
                runtime_image_identity=runtime.image_identity,
                runtime_instance_id=runtime.runtime_instance_id,
            ),
            dima_request_id=dima_request_id,
            dima_trace_id=dima_trace_id,
            native_conversation_id=manifest.native_conversation_id,
            native_query_id=manifest.native_query_id,
            resolved_pmbql=copy.deepcopy(attestation.exact_serialized_pmbql),
            portable_query=None,
            semantic_refs=(
                intent.metrics[0].semantic_ref,
                *(item.semantic_ref for item in intent.dimensions),
                *(item.semantic_ref for item in intent.filters),
            ),
            resource_bindings=_unique_resources(observed_resources),
            native_validation_refs=tuple(native_validation_refs),
            time_scope_fingerprint=period_scope_fingerprint(intent.period),
            filter_scope_fingerprint=filter_scope_fingerprint(intent.filters),
            material_filter_count=manifest.non_temporal_filter_count,
            material_join_count=(
                manifest.explicit_join_count + manifest.implicit_join_count
            ),
            query_count=manifest.material_query_count,
        )
        if candidate.candidate_artifact_fingerprint != manifest.exact_pmbql_fingerprint:
            raise NativeStandardTrustError(
                "NATIVE_EXACT_ARTIFACT_FINGERPRINT_MISMATCH",
                "Platform fingerprint differs from engine-attested exact pMBQL",
            )
        return candidate, expected_resources

    @classmethod
    def authorize(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
        attestation: NativeAttestationEnvelope,
        expected_engine: NativeEngineIdentity,
        current_principal: Principal,
        verified_security_facts: VerifiedExecutionSecurityFacts,
        dima_request_id: str,
        dima_trace_id: str,
        managed_resource_bindings: tuple[ManagedResourceBinding, ...] = (),
        current_lens_value_evidence: tuple[CurrentLensValueEvidence, ...] = (),
    ) -> NativeStandardAuthorizationResult:
        try:
            candidate, expected_resources = cls._candidate(
                intent=intent,
                snapshot=snapshot,
                attestation=attestation,
                expected_engine=expected_engine,
                dima_request_id=dima_request_id,
                dima_trace_id=dima_trace_id,
                managed_resource_bindings=managed_resource_bindings,
            )
        except (NativeStandardTrustError, MetabaseCompilationBlocked) as exc:
            return NativeStandardAuthorizationResult(
                authorization=_block(exc.code, exc.detail)
            )

        p13c_access = None
        if intent.filters:
            p13c_access = ExecutionAccessSnapshotIssuer.issue_for_expected_resources(
                current_principal=current_principal,
                accepted_intent=intent,
                verified_security_facts=verified_security_facts,
                expected_source_object_refs=tuple(
                    item.resource_id for item in expected_resources
                ),
            )
            accepted_filter = intent.filters[0]
            value_result = EntityValueAdoptionGate.adjudicate(
                proposal=EntityValueProposal(
                    decision="BIND",
                    semantic_ref=accepted_filter.semantic_ref,
                    value=accepted_filter.value,
                ),
                allowed_semantic_scopes=(accepted_filter.semantic_ref,),
                evidence=current_lens_value_evidence,
                expected_access_lens_ref=p13c_access.execution_access_fingerprint,
            )
            if value_result.decision != EntityValueDecision.BIND:
                return NativeStandardAuthorizationResult(
                    authorization=_block(
                        f"P13C_{value_result.reason_code}",
                        "accepted filter value is not bound by exact current-lens P11 evidence",
                    ),
                    candidate=candidate,
                )

        decision = NativeCandidateAuthorizationGate.authorize(
            intent=intent,
            candidate=candidate,
            authorized_resource_bindings=expected_resources,
        )
        if decision.outcome != NativeCandidateOutcome.ALLOW:
            return NativeStandardAuthorizationResult(
                authorization=decision,
                candidate=candidate,
            )

        manifest = attestation.manifest
        expected_subject = f"metabase-user:{manifest.authenticated_metabase_subject}"
        if verified_security_facts.metabase_subject_ref != expected_subject:
            raise SecurityIdentityError(
                "P13B_METABASE_SUBJECT_MISMATCH",
                "P10 Metabase subject differs from engine-attested subject",
            )
        if manifest.attestation_id not in verified_security_facts.attestation_refs:
            raise SecurityIdentityError(
                "P13B_ATTESTATION_PROOF_MISSING",
                "P10 facts do not reference the native engine attestation",
            )

        artifact = decision.authorized_artifact
        assert artifact is not None
        if p13c_access is None:
            access = ExecutionAccessSnapshotIssuer.issue(
                current_principal=current_principal,
                accepted_intent=intent,
                execution_artifact=artifact,
                verified_security_facts=verified_security_facts,
            )
        else:
            if tuple(sorted(artifact.resource_entity_ids)) != tuple(
                sorted(p13c_access.source_object_refs)
            ):
                raise SecurityIdentityError(
                    "P13C_ACCESS_ARTIFACT_RESOURCE_MISMATCH",
                    "P13A artifact resources differ from the P10 lens used for P11 evidence",
                )
            access = p13c_access
        return NativeStandardAuthorizationResult(
            authorization=decision,
            candidate=candidate,
            access_snapshot=access,
        )

    @staticmethod
    def execution_request(
        *,
        result: NativeStandardAuthorizationResult,
        attestation: NativeAttestationEnvelope,
    ) -> NativeDatasetExecutionRequest:
        if result.authorization.outcome != NativeCandidateOutcome.ALLOW:
            raise NativeStandardTrustError(
                "NATIVE_EXECUTION_NOT_AUTHORIZED",
                "cannot create /api/dataset request from a non-ALLOW decision",
            )
        artifact = result.authorization.authorized_artifact
        assert artifact is not None
        artifact.assert_execution_matches(
            role="primary",
            artifact_representation=attestation.exact_serialized_pmbql,
        )
        return NativeDatasetExecutionRequest(
            artifact_fingerprint=artifact.steps[0].artifact_fingerprint,
            database_id=attestation.manifest.database_id,
            exact_serialized_pmbql=copy.deepcopy(attestation.exact_serialized_pmbql),
        )

    @staticmethod
    def seal_receipt(
        *,
        intent: ResolvedAnalyticsIntent,
        result: NativeStandardAuthorizationResult,
        execution_request: NativeDatasetExecutionRequest,
        runtime: RuntimeIdentity,
        execution_result: ExecutionResultSnapshot,
        execution_event: ExecutionEventIdentity,
    ):
        if result.authorization.outcome != NativeCandidateOutcome.ALLOW:
            raise NativeStandardTrustError(
                "NATIVE_EXECUTION_NOT_AUTHORIZED",
                "cannot seal a receipt for a non-ALLOW decision",
            )
        artifact = result.authorization.authorized_artifact
        assert artifact is not None
        artifact.assert_execution_matches(
            role="primary",
            artifact_representation=execution_request.exact_serialized_pmbql,
        )
        if artifact.steps[0].artifact_fingerprint != execution_request.artifact_fingerprint:
            raise NativeStandardTrustError(
                "EXECUTION_ARTIFACT_MISMATCH",
                "execution request fingerprint differs from authorized artifact",
            )
        if result.access_snapshot is None:
            raise NativeStandardTrustError(
                "ACCESS_SNAPSHOT_REQUIRED",
                "P13B receipt sealing requires the P10 access snapshot",
            )
        return DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            execution_artifact=artifact,
            access_snapshot=result.access_snapshot,
            runtime=runtime,
            results=(execution_result,),
            events=(execution_event,),
        )[0]
