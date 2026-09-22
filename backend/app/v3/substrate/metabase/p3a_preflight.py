"""Deterministic P3A compiler prototype for the Metabase structured-execution arm.

Business meaning comes only from Dima-owned ResolvedAnalyticsIntent plus an immutable
DimaExecutionBindingSnapshot. No Metabase search, labels, raw language, or implicit joins
participate in compilation.
"""

from __future__ import annotations

from typing import Any, Literal

from app.v3.analytics_contract import ResolvedAnalyticsIntent, ResolvedPeriod
from app.v3.semantic_spec import DimensionSpec, MetricSpec, SourceLineage
from app.v3.substrate.metabase.p3a_models import (
    BridgeFamily,
    BridgeFamilyFinding,
    BridgePlan,
    BridgePreflightReport,
    BridgeSafetyCounters,
    DimaExecutionBindingSnapshot,
    P3ABridgeBlocked,
    P3AResult,
    PortableQueryStep,
)


class MetabaseBridgePreflightCompiler:
    """Compile a narrow, auditable family without becoming a second semantic owner."""

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

    @staticmethod
    def _metric(snapshot: DimaExecutionBindingSnapshot, candidate_id: str) -> MetricSpec:
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
    def _lineage(item: MetricSpec | DimensionSpec) -> SourceLineage:
        if len(item.source_lineage) != 1:
            raise P3ABridgeBlocked(
                "AMBIGUOUS_SOURCE_LINEAGE",
                "P3A prototype requires exactly one explicit SourceLineage per semantic item",
            )
        lineage = item.source_lineage[0]
        if not lineage.database_ref or not lineage.table_name:
            raise P3ABridgeBlocked(
                "INCOMPLETE_SOURCE_LINEAGE",
                "portable source requires explicit database/table lineage",
            )
        return lineage

    @staticmethod
    def _table(lineage: SourceLineage) -> tuple[str, str | None, str]:
        assert lineage.database_ref is not None
        assert lineage.table_name is not None
        return (lineage.database_ref, lineage.schema_name, lineage.table_name)

    @classmethod
    def _field_ref(cls, item: DimensionSpec) -> list[Any]:
        lineage = cls._lineage(item)
        if not lineage.column_name:
            raise P3ABridgeBlocked(
                "INCOMPLETE_SOURCE_LINEAGE",
                f"dimension {item.dimension_id} has no explicit column lineage",
            )
        return [
            "field",
            {},
            [
                lineage.database_ref,
                lineage.schema_name,
                lineage.table_name,
                lineage.column_name,
            ],
        ]

    @classmethod
    def _metric_clause(cls, metric: MetricSpec) -> list[Any]:
        if metric.formula:
            raise P3ABridgeBlocked(
                "UNPROVEN_METRIC_FORMULA_EXPRESSIVITY",
                "P3A does not redefine or translate arbitrary metric formulas",
            )
        op = cls._AGGREGATIONS.get(metric.aggregation.strip().lower())
        if op is None:
            raise P3ABridgeBlocked(
                "UNSUPPORTED_DIMA_METRIC_AGGREGATION",
                f"aggregation {metric.aggregation!r} has no mechanical P3A mapping",
            )
        if op == "count":
            return ["count", {}]

        lineage = cls._lineage(metric)
        if not lineage.column_name:
            raise P3ABridgeBlocked(
                "INCOMPLETE_SOURCE_LINEAGE",
                f"metric {metric.metric_id} has no explicit aggregation column",
            )
        return [
            op,
            {},
            [
                "field",
                {},
                [
                    lineage.database_ref,
                    lineage.schema_name,
                    lineage.table_name,
                    lineage.column_name,
                ],
            ],
        ]

    @classmethod
    def _assert_same_table(
        cls,
        *,
        base: SourceLineage,
        other: SourceLineage,
    ) -> None:
        if cls._table(base) != cls._table(other):
            raise P3ABridgeBlocked(
                "APPROVED_RELATIONSHIP_PATH_REQUIRED",
                "cross-table compilation requires an explicit approved Dima relationship path",
            )

    @classmethod
    def _period_clauses(
        cls,
        *,
        period: ResolvedPeriod,
        snapshot: DimaExecutionBindingSnapshot,
        base_lineage: SourceLineage,
    ) -> tuple[list[Any], ...]:
        dimension_id = snapshot.temporal_dimension(period.time_dimension)
        dimension = cls._dimension_by_id(snapshot, dimension_id)
        lineage = cls._lineage(dimension)
        cls._assert_same_table(base=base_lineage, other=lineage)
        field = cls._field_ref(dimension)
        clauses: list[list[Any]] = [[">=", {}, field, period.start]]
        if period.end is not None:
            clauses.append(["<=", {}, field, period.end])
        return tuple(clauses)

    @staticmethod
    def _combine_filters(clauses: list[list[Any]]) -> list[list[Any]]:
        if not clauses:
            return []
        if len(clauses) == 1:
            return [clauses[0]]
        return [["and", {}, *clauses]]

    @classmethod
    def _query_for_period(
        cls,
        *,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
        metric: MetricSpec,
        period: ResolvedPeriod | None,
    ) -> tuple[dict[str, Any], tuple[str, ...]]:
        metric_lineage = cls._lineage(metric)
        stage: dict[str, Any] = {
            "lib/type": "mbql.stage/mbql",
            "source-table": list(cls._table(metric_lineage)),
            "aggregation": [cls._metric_clause(metric)],
        }
        semantic_ids: list[str] = [metric.metric_id]

        breakouts: list[list[Any]] = []
        for ref in intent.dimensions:
            dimension = cls._dimension(snapshot, ref.source_candidate_id)
            lineage = cls._lineage(dimension)
            cls._assert_same_table(base=metric_lineage, other=lineage)
            breakouts.append(cls._field_ref(dimension))
            semantic_ids.append(dimension.dimension_id)
        if breakouts:
            stage["breakout"] = breakouts

        filters: list[list[Any]] = []
        for ref in intent.filters:
            dimension = cls._dimension(
                snapshot,
                ref.source_candidate_id,
                kind="filter",
            )
            lineage = cls._lineage(dimension)
            cls._assert_same_table(base=metric_lineage, other=lineage)
            filters.append(["=", {}, cls._field_ref(dimension), ref.value])
            semantic_ids.append(dimension.dimension_id)

        if period is not None:
            filters.extend(
                cls._period_clauses(
                    period=period,
                    snapshot=snapshot,
                    base_lineage=metric_lineage,
                )
            )
            semantic_ids.append(snapshot.temporal_dimension(period.time_dimension))

        combined = cls._combine_filters(filters)
        if combined:
            stage["filters"] = combined

        if intent.ranking is not None:
            stage["order-by"] = [
                [intent.ranking.direction, {}, ["aggregation", {}, 0]]
            ]
            stage["limit"] = intent.ranking.limit

        return (
            {
                "lib/type": "mbql/query",
                "stages": [stage],
            },
            tuple(dict.fromkeys(semantic_ids)),
        )

    @classmethod
    def compile(
        cls,
        *,
        family: BridgeFamily,
        intent: ResolvedAnalyticsIntent,
        snapshot: DimaExecutionBindingSnapshot,
    ) -> BridgePlan:
        if intent.semantic_context_version != snapshot.semantic_context_version:
            raise P3ABridgeBlocked(
                "SEMANTIC_CONTEXT_MISMATCH",
                "intent and Dima execution snapshot are from different semantic contexts",
            )
        if len(intent.metrics) != 1:
            raise P3ABridgeBlocked(
                "P3A_METRIC_CARDINALITY",
                "representative P3A families require exactly one governed metric",
            )

        metric = cls._metric(snapshot, intent.metrics[0].source_candidate_id)
        if intent.comparison is not None:
            base_query, base_ids = cls._query_for_period(
                intent=intent,
                snapshot=snapshot,
                metric=metric,
                period=intent.comparison.base_period,
            )
            ref_query, ref_ids = cls._query_for_period(
                intent=intent,
                snapshot=snapshot,
                metric=metric,
                period=intent.comparison.reference_period,
            )
            return BridgePlan(
                family=family,
                semantic_ids=tuple(dict.fromkeys((*base_ids, *ref_ids))),
                query_steps=(
                    PortableQueryStep(role="base", query=base_query),
                    PortableQueryStep(role="reference", query=ref_query),
                ),
            )

        query, semantic_ids = cls._query_for_period(
            intent=intent,
            snapshot=snapshot,
            metric=metric,
            period=intent.period,
        )
        return BridgePlan(
            family=family,
            semantic_ids=semantic_ids,
            query_steps=(PortableQueryStep(role="primary", query=query),),
        )

    @classmethod
    def audit(
        cls,
        *,
        cases: tuple[tuple[BridgeFamily, ResolvedAnalyticsIntent], ...],
        snapshot: DimaExecutionBindingSnapshot,
    ) -> BridgePreflightReport:
        findings: list[BridgeFamilyFinding] = []
        for family, intent in cases:
            try:
                plan = cls.compile(
                    family=family,
                    intent=intent,
                    snapshot=snapshot,
                )
            except P3ABridgeBlocked as exc:
                findings.append(
                    BridgeFamilyFinding(
                        family=family,
                        compiled=False,
                        blocker_code=exc.code,
                        detail=exc.detail,
                    )
                )
            else:
                findings.append(
                    BridgeFamilyFinding(
                        family=family,
                        compiled=True,
                        query_count=len(plan.query_steps),
                    )
                )

        counters = BridgeSafetyCounters()
        result = (
            P3AResult.PASS_B_SEAM
            if all(item.compiled for item in findings) and counters.clean
            else P3AResult.BLOCKED_DIMA_CONTRACT_GAP
        )
        return BridgePreflightReport(
            result=result,
            findings=tuple(findings),
            counters=counters,
        )
