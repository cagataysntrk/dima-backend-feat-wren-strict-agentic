"""Production P4 Dima intent -> Metabase portable projection compiler.

This module is pure and deterministic. It performs no HTTP, Metabase metadata search,
semantic-handle resolution, or raw-language interpretation. Physical locators are emitted
only from the production DimaExecutionBindingSnapshot after exact SourceLineage/current
catalog agreement.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.v3.analytics_contract import (
    ResolvedAnalyticsIntent,
    ResolvedPeriod,
)
from app.v3.semantic_spec import DimensionSpec, MetricSpec
from app.v3.substrate.metabase.execution_binding import (
    CurrentCatalogObject,
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class QueryStructuralManifest(FrozenModel):
    source_count: int = Field(ge=0)
    aggregation_operators: tuple[str, ...] = ()
    breakout_count: int = Field(ge=0)
    filter_leaf_count: int = Field(ge=0)
    time_predicate_count: int = Field(ge=0)
    order_by_count: int = Field(ge=0)
    limit: int | None = Field(default=None, ge=1)
    explicit_join_count: int = Field(ge=0)
    implicit_join_reference_count: int = Field(ge=0)


class SemanticSlotManifest(FrozenModel):
    query_count: int = Field(ge=1)
    comparison_query_count: int = Field(ge=0)
    steps: tuple[QueryStructuralManifest, ...] = Field(min_length=1)
    semantic_ids: tuple[str, ...] = Field(min_length=1)
    resource_entity_ids: tuple[str, ...] = ()
    resource_fingerprints: tuple[str, ...] = Field(min_length=1)


class MetabaseProjectionStep(FrozenModel):
    role: Literal["primary", "base", "reference"]
    portable_query: dict[str, Any]


class MetabaseProjectionPlan(FrozenModel):
    authority_id: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_context_version: str = Field(min_length=1)
    steps: tuple[MetabaseProjectionStep, ...] = Field(min_length=1)
    manifest: SemanticSlotManifest
    current_catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


def _normalized_key(value: object) -> str:
    return str(value).lstrip(":")


def _count_filter_leaves(clause: object) -> int:
    if not isinstance(clause, list) or not clause:
        return 0
    op = str(clause[0]).lstrip(":")
    if op in {"and", "or"}:
        return sum(_count_filter_leaves(item) for item in clause[2:])
    return 1


def _count_time_predicates(clause: object) -> int:
    if not isinstance(clause, list) or not clause:
        return 0
    op = str(clause[0]).lstrip(":")
    if op in {"and", "or"}:
        return sum(_count_time_predicates(item) for item in clause[2:])
    return 1 if op in {">=", "<="} else 0


def _count_implicit_join_refs(value: object) -> int:
    if isinstance(value, dict):
        count = sum(
            1
            for key in value
            if _normalized_key(key)
            in {
                "source-field",
                "source-field-name",
                "source-field-join-alias",
            }
        )
        return count + sum(_count_implicit_join_refs(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return sum(_count_implicit_join_refs(item) for item in value)
    return 0


def query_structural_manifest(query: dict[str, Any]) -> QueryStructuralManifest:
    """Extract only semantic-structure slots stable across portable/canonical MBQL."""

    stages = query.get("stages") or ()
    source_count = 0
    aggregation_operators: list[str] = []
    breakout_count = 0
    filter_leaf_count = 0
    time_predicate_count = 0
    order_by_count = 0
    explicit_join_count = 0
    limit: int | None = None

    if not isinstance(stages, (list, tuple)):
        raise MetabaseCompilationBlocked(
            "MALFORMED_QUERY_STRUCTURE",
            "query stages must be a sequence",
        )

    for stage in stages:
        if not isinstance(stage, dict):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "query stage must be an object",
            )
        if stage.get("source-table") is not None:
            source_count += 1
        if stage.get("source-card") is not None:
            source_count += 1

        aggregations = stage.get("aggregation") or ()
        if not isinstance(aggregations, (list, tuple)):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "aggregation must be a sequence",
            )
        for clause in aggregations:
            if not isinstance(clause, (list, tuple)) or not clause:
                raise MetabaseCompilationBlocked(
                    "MALFORMED_QUERY_STRUCTURE",
                    "aggregation clause must be a non-empty sequence",
                )
            aggregation_operators.append(str(clause[0]).lstrip(":"))

        breakouts = stage.get("breakout") or ()
        if not isinstance(breakouts, (list, tuple)):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "breakout must be a sequence",
            )
        breakout_count += len(breakouts)

        filters = stage.get("filters") or ()
        if not isinstance(filters, (list, tuple)):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "filters must be a sequence",
            )
        filter_leaf_count += sum(_count_filter_leaves(item) for item in filters)
        time_predicate_count += sum(_count_time_predicates(item) for item in filters)

        order_by = stage.get("order-by") or ()
        if not isinstance(order_by, (list, tuple)):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "order-by must be a sequence",
            )
        order_by_count += len(order_by)

        joins = stage.get("joins") or ()
        if not isinstance(joins, (list, tuple)):
            raise MetabaseCompilationBlocked(
                "MALFORMED_QUERY_STRUCTURE",
                "joins must be a sequence",
            )
        explicit_join_count += len(joins)

        if stage.get("limit") is not None:
            stage_limit = stage["limit"]
            if not isinstance(stage_limit, int) or isinstance(stage_limit, bool):
                raise MetabaseCompilationBlocked(
                    "MALFORMED_QUERY_STRUCTURE",
                    "limit must be an integer",
                )
            if limit is not None and limit != stage_limit:
                raise MetabaseCompilationBlocked(
                    "MULTI_STAGE_LIMIT_UNSUPPORTED",
                    "P4 structural manifest does not accept multiple different stage limits",
                )
            limit = stage_limit

    return QueryStructuralManifest(
        source_count=source_count,
        aggregation_operators=tuple(aggregation_operators),
        breakout_count=breakout_count,
        filter_leaf_count=filter_leaf_count,
        time_predicate_count=time_predicate_count,
        order_by_count=order_by_count,
        limit=limit,
        explicit_join_count=explicit_join_count,
        implicit_join_reference_count=_count_implicit_join_refs(query),
    )


class MetabaseProjectionCompiler:
    """Compile the first narrow production P4 semantic slice."""

    _AGGREGATIONS = {
        "count": "count",
        "sum": "sum",
        "avg": "avg",
        "average": "avg",
        "min": "min",
        "max": "max",
        "distinct": "distinct",
        "count_distinct": "distinct",
    }
    _TEXT_TYPES = {"text"}

    @staticmethod
    def _metric(
        snapshot: DimaExecutionBindingSnapshot,
        candidate_id: str,
    ) -> MetricSpec:
        semantic_id = snapshot.candidate(candidate_id, kind="metric")
        for item in snapshot.semantic_spec.metrics:
            if item.metric_id == semantic_id:
                return item
        raise AssertionError("validated snapshot lost metric")

    @staticmethod
    def _dimension_by_id(
        snapshot: DimaExecutionBindingSnapshot,
        semantic_id: str,
    ) -> DimensionSpec:
        for item in snapshot.semantic_spec.dimensions:
            if item.dimension_id == semantic_id:
                return item
        raise AssertionError("validated snapshot lost dimension")

    @classmethod
    def _dimension(
        cls,
        snapshot: DimaExecutionBindingSnapshot,
        candidate_id: str,
        *,
        kind: Literal["dimension", "filter"] = "dimension",
    ) -> DimensionSpec:
        semantic_id = snapshot.candidate(candidate_id, kind=kind)
        return cls._dimension_by_id(snapshot, semantic_id)

    @staticmethod
    def _current_for(
        snapshot: DimaExecutionBindingSnapshot,
        item: MetricSpec | DimensionSpec,
    ) -> CurrentCatalogObject:
        if len(item.source_lineage) != 1:
            raise MetabaseCompilationBlocked(
                "AMBIGUOUS_SOURCE_LINEAGE",
                "P4 requires exactly one explicit SourceLineage per semantic item",
            )
        return snapshot.current_lineage(item.source_lineage[0])

    @staticmethod
    def _assert_same_table(
        *,
        base: CurrentCatalogObject,
        other: CurrentCatalogObject,
    ) -> None:
        if base.portable_table != other.portable_table:
            raise MetabaseCompilationBlocked(
                "APPROVED_RELATIONSHIP_PATH_REQUIRED",
                "initial P4 compiler is same-table only",
            )

    @classmethod
    def _field_ref(
        cls,
        *,
        snapshot: DimaExecutionBindingSnapshot,
        item: DimensionSpec,
    ) -> tuple[list[Any], CurrentCatalogObject]:
        current = cls._current_for(snapshot, item)
        return ["field", {}, list(current.portable_field)], current

    @classmethod
    def _metric_clause(
        cls,
        *,
        snapshot: DimaExecutionBindingSnapshot,
        metric: MetricSpec,
    ) -> tuple[list[Any], CurrentCatalogObject]:
        if metric.formula:
            raise MetabaseCompilationBlocked(
                "UNPROVEN_METRIC_FORMULA_EXPRESSIVITY",
                "P4 does not translate arbitrary Dima metric formulas",
            )
        op = cls._AGGREGATIONS.get(metric.aggregation.strip().lower())
        if op is None:
            raise MetabaseCompilationBlocked(
                "UNSUPPORTED_DIMA_METRIC_AGGREGATION",
                f"unsupported mechanical aggregation {metric.aggregation!r}",
            )

        current = cls._current_for(snapshot, metric)
        if op == "count":
            return ["count", {}], current
        return [op, {}, ["field", {}, list(current.portable_field)]], current

    @classmethod
    def _period_clauses(
        cls,
        *,
        snapshot: DimaExecutionBindingSnapshot,
        period: ResolvedPeriod,
        base: CurrentCatalogObject,
    ) -> tuple[tuple[list[Any], ...], str, CurrentCatalogObject]:
        dimension_id = snapshot.temporal_dimension(period.time_dimension)
        dimension = cls._dimension_by_id(snapshot, dimension_id)
        field, current = cls._field_ref(snapshot=snapshot, item=dimension)
        cls._assert_same_table(base=base, other=current)

        clauses: list[list[Any]] = [[">=", {}, field, period.start]]
        if period.end is not None:
            clauses.append(["<=", {}, field, period.end])
        return tuple(clauses), dimension_id, current

    @staticmethod
    def _combine_filters(clauses: list[list[Any]]) -> list[list[Any]]:
        if not clauses:
            return []
        if len(clauses) == 1:
            return [clauses[0]]
        return [["and", {}, *clauses]]

    @staticmethod
    def _unique(values: list[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(values))

    @classmethod
    def _query_for_period(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
        metric: MetricSpec,
        period: ResolvedPeriod | None,
    ) -> tuple[dict[str, Any], tuple[str, ...], tuple[CurrentCatalogObject, ...]]:
        metric_clause, metric_current = cls._metric_clause(
            snapshot=snapshot,
            metric=metric,
        )
        stage: dict[str, Any] = {
            "lib/type": "mbql.stage/mbql",
            "source-table": list(metric_current.portable_table),
            "aggregation": [metric_clause],
        }

        semantic_ids: list[str] = [metric.metric_id]
        objects: list[CurrentCatalogObject] = [metric_current]

        breakouts: list[list[Any]] = []
        for ref in intent.dimensions:
            dimension = cls._dimension(snapshot, ref.source_candidate_id)
            field, current = cls._field_ref(snapshot=snapshot, item=dimension)
            cls._assert_same_table(base=metric_current, other=current)
            breakouts.append(field)
            semantic_ids.append(dimension.dimension_id)
            objects.append(current)
        if breakouts:
            stage["breakout"] = breakouts

        filters: list[list[Any]] = []
        for ref in intent.filters:
            dimension = cls._dimension(
                snapshot,
                ref.source_candidate_id,
                kind="filter",
            )
            if dimension.data_type.strip().lower() not in cls._TEXT_TYPES:
                raise MetabaseCompilationBlocked(
                    "UNTYPED_NON_TEXT_FILTER_UNSUPPORTED",
                    f"filter {dimension.dimension_id} has non-text type {dimension.data_type!r}",
                )
            field, current = cls._field_ref(snapshot=snapshot, item=dimension)
            cls._assert_same_table(base=metric_current, other=current)
            filters.append(["=", {}, field, ref.value])
            semantic_ids.append(dimension.dimension_id)
            objects.append(current)

        if period is not None:
            period_clauses, dimension_id, current = cls._period_clauses(
                snapshot=snapshot,
                period=period,
                base=metric_current,
            )
            filters.extend(period_clauses)
            semantic_ids.append(dimension_id)
            objects.append(current)

        combined = cls._combine_filters(filters)
        if combined:
            stage["filters"] = combined

        if intent.ranking is not None:
            if not intent.dimensions:
                raise MetabaseCompilationBlocked(
                    "RANKING_REQUIRES_BREAKDOWN",
                    "ranking requires at least one governed breakdown",
                )
            stage["order-by"] = [
                [intent.ranking.direction, {}, ["aggregation", {}, 0]]
            ]
            stage["limit"] = intent.ranking.limit

        return (
            {"lib/type": "mbql/query", "stages": [stage]},
            cls._unique(semantic_ids),
            tuple(objects),
        )

    @classmethod
    def compile(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
    ) -> MetabaseProjectionPlan:
        if intent.semantic_context_version != snapshot.semantic_context_version:
            raise MetabaseCompilationBlocked(
                "SEMANTIC_CONTEXT_MISMATCH",
                "intent and execution snapshot are from different semantic contexts",
            )
        if len(intent.metrics) != 1:
            raise MetabaseCompilationBlocked(
                "P4_METRIC_CARDINALITY",
                "initial P4 compiler requires exactly one governed metric",
            )
        if intent.approved_relationship_paths:
            raise MetabaseCompilationBlocked(
                "APPROVED_RELATIONSHIP_PATH_UNSUPPORTED",
                "cross-table relationship compilation is not certified in initial P4",
            )
        if intent.grain_constraints:
            raise MetabaseCompilationBlocked(
                "GRAIN_CONSTRAINT_UNSUPPORTED",
                "explicit grain constraints are not certified in initial P4",
            )
        if intent.period is not None and intent.comparison is not None:
            raise MetabaseCompilationBlocked(
                "PERIOD_COMPARISON_CONFLICT",
                "intent cannot carry both direct period and comparison in initial P4",
            )

        metric = cls._metric(snapshot, intent.metrics[0].source_candidate_id)

        steps: list[MetabaseProjectionStep] = []
        semantic_ids: list[str] = []
        used_objects: list[CurrentCatalogObject] = []

        if intent.comparison is not None:
            if intent.comparison.mode != "previous_period":
                raise MetabaseCompilationBlocked(
                    "UNSUPPORTED_COMPARISON_MODE",
                    f"unsupported comparison mode {intent.comparison.mode!r}",
                )
            for role, period in (
                ("base", intent.comparison.base_period),
                ("reference", intent.comparison.reference_period),
            ):
                query, ids, objects = cls._query_for_period(
                    intent=intent,
                    snapshot=snapshot,
                    metric=metric,
                    period=period,
                )
                steps.append(
                    MetabaseProjectionStep(
                        role=role,
                        portable_query=query,
                    )
                )
                semantic_ids.extend(ids)
                used_objects.extend(objects)
        else:
            query, ids, objects = cls._query_for_period(
                intent=intent,
                snapshot=snapshot,
                metric=metric,
                period=intent.period,
            )
            steps.append(
                MetabaseProjectionStep(
                    role="primary",
                    portable_query=query,
                )
            )
            semantic_ids.extend(ids)
            used_objects.extend(objects)

        unique_objects: dict[str, CurrentCatalogObject] = {}
        for item in used_objects:
            unique_objects[item.source_id] = item

        ordered_objects = tuple(
            unique_objects[key] for key in sorted(unique_objects)
        )
        manifests = tuple(
            query_structural_manifest(step.portable_query)
            for step in steps
        )
        manifest = SemanticSlotManifest(
            query_count=len(steps),
            comparison_query_count=(len(steps) if intent.comparison is not None else 0),
            steps=manifests,
            semantic_ids=cls._unique(semantic_ids),
            resource_entity_ids=tuple(
                item.resource_entity_id
                for item in ordered_objects
                if item.resource_entity_id is not None
            ),
            resource_fingerprints=tuple(
                item.resource_fingerprint for item in ordered_objects
            ),
        )

        if any(
            step.explicit_join_count != 0
            or step.implicit_join_reference_count != 0
            for step in manifest.steps
        ):
            raise AssertionError("initial P4 compiler emitted forbidden join behavior")

        return MetabaseProjectionPlan(
            authority_id=intent.authority_id,
            projection_hash=intent.projection_hash,
            resolved_intent_hash=intent.resolved_intent_hash,
            semantic_context_version=intent.semantic_context_version,
            steps=tuple(steps),
            manifest=manifest,
            current_catalog_fingerprint=snapshot.current_catalog.fingerprint,
        )
