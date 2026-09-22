"""Synthetic Dima-owned fixture for P3A bridge preflight tests only."""

from __future__ import annotations

import hashlib
from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
)
from app.v3.semantic_spec import DimensionSpec, DimaSemanticSpec, MetricSpec, SourceLineage, TimeSpec
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    TemporalSemanticBinding,
)
from app.v3.substrate.metabase.p3a_models import BridgeFamily

CTX = "p3a-lab-v1"
TIME_KEY = "legacy-wren/orders.order_date"
HEX_A = "a" * 64
HEX_B = "b" * 64


def _lineage(column: str):
    return (
        SourceLineage(
            source_id=f"orders.{column}",
            database_ref="Dima Analytics Lab",
            schema_name="public",
            table_name="orders",
            column_name=column,
        ),
    )


def _catalog_object(column: str) -> CurrentCatalogObject:
    entity_id = f"lab:orders.{column}"
    fingerprint = hashlib.sha256(
        f"Dima Analytics Lab|public|orders|{column}|{entity_id}".encode("utf-8")
    ).hexdigest()
    return CurrentCatalogObject(
        source_id=f"orders.{column}",
        database_ref="Dima Analytics Lab",
        schema_name="public",
        table_name="orders",
        column_name=column,
        resource_entity_id=entity_id,
        resource_fingerprint=fingerprint,
    )


def build_snapshot() -> DimaExecutionBindingSnapshot:
    spec = DimaSemanticSpec(
        semantic_context_version=CTX,
        metrics=(
            MetricSpec(
                metric_id="metric.revenue",
                name="Revenue",
                aggregation="sum",
                semantic_version="1",
                compatibility_hash=HEX_A,
                source_lineage=_lineage("amount"),
            ),
        ),
        dimensions=(
            DimensionSpec(
                dimension_id="dimension.region",
                name="Region",
                data_type="text",
                semantic_version="1",
                source_lineage=_lineage("region"),
            ),
            DimensionSpec(
                dimension_id="dimension.channel",
                name="Channel",
                data_type="text",
                semantic_version="1",
                source_lineage=_lineage("channel"),
            ),
            DimensionSpec(
                dimension_id="dimension.order_date",
                name="Order Date",
                data_type="date",
                semantic_version="1",
                source_lineage=_lineage("order_date"),
            ),
        ),
        time_specs=(
            TimeSpec(
                time_id="time.order_date",
                dimension_ref="dimension.order_date",
                grain="day",
            ),
        ),
    )
    current_catalog = CurrentCatalogSnapshot(
        catalog_version="p3a-lab-catalog-v1",
        objects=tuple(
            _catalog_object(column)
            for column in ("amount", "region", "channel", "order_date")
        ),
    )
    return DimaExecutionBindingSnapshot(
        semantic_context_version=CTX,
        semantic_spec=spec,
        candidate_bindings=(
            CandidateSemanticBinding(
                candidate_id="cand_metric",
                semantic_id="metric.revenue",
                kind="metric",
            ),
            CandidateSemanticBinding(
                candidate_id="cand_region",
                semantic_id="dimension.region",
                kind="dimension",
            ),
            CandidateSemanticBinding(
                candidate_id="cand_channel",
                semantic_id="dimension.channel",
                kind="dimension",
            ),
            CandidateSemanticBinding(
                candidate_id="cand_filter_north",
                semantic_id="dimension.region",
                kind="filter",
            ),
        ),
        temporal_bindings=(
            TemporalSemanticBinding(
                compatibility_key=TIME_KEY,
                dimension_id="dimension.order_date",
            ),
        ),
        current_catalog=current_catalog,
    )


def _metric_ref():
    return ResolvedSemanticRef(
        semantic_ref="handle_metric",
        source_candidate_id="cand_metric",
        kind="metric",
        canonical_name="DO NOT USE THIS AS A PHYSICAL FIELD",
        source_scopes=("legacy_wren_cube_name",),
    )


def _dimension(candidate: str, handle: str):
    return ResolvedSemanticRef(
        semantic_ref=handle,
        source_candidate_id=candidate,
        kind="dimension",
        canonical_name="DISPLAY NAME IS NOT A LOCATOR",
        source_scopes=("legacy_wren_cube_name",),
    )


def build_period(start="2026-06-01", end="2026-06-30"):
    return ResolvedPeriod(
        kind="this_month",
        source_text="surface is provenance only",
        time_dimension=TIME_KEY,
        start=start,
        end=end,
    )


def _principal():
    return PrincipalContextRef(
        tenant_binding="tenant-lab",
        principal_subject="p3a-user",
        roles=("analyst",),
    )


def build_intent(
    *,
    dimensions=(),
    filters=(),
    period_value=None,
    comparison=None,
    ranking=None,
):
    return ResolvedAnalyticsIntent(
        authority_id="auth-p3a",
        request_ref="request-provenance-not-language-input",
        source_message_hash=HEX_A,
        projection_hash=HEX_B,
        semantic_context_version=CTX,
        obligation_ids=("obl-1",),
        metrics=(_metric_ref(),),
        dimensions=dimensions,
        filters=filters,
        period=period_value,
        comparison=comparison,
        ranking=ranking,
        principal=_principal(),
    )


def build_cases():
    comparison = ResolvedComparison(
        mode="previous_period",
        source_text="comparison provenance",
        base_period=build_period("2026-06-01", "2026-06-30"),
        reference_period=build_period("2026-05-01", "2026-05-31"),
    )
    north = ResolvedFilterRef(
        semantic_ref="handle_filter",
        source_candidate_id="cand_filter_north",
        dimension_name="DO NOT USE AS PHYSICAL FIELD",
        value="North",
        source_scopes=("legacy_wren_cube_name",),
    )
    return (
        (BridgeFamily.METRIC, build_intent()),
        (
            BridgeFamily.METRIC_DIMENSION,
            build_intent(dimensions=(_dimension("cand_region", "handle_region"),)),
        ),
        (
            BridgeFamily.METRIC_FILTER,
            build_intent(filters=(north,)),
        ),
        (
            BridgeFamily.METRIC_PERIOD,
            build_intent(period_value=build_period()),
        ),
        (
            BridgeFamily.PREVIOUS_PERIOD_COMPARISON,
            build_intent(comparison=comparison),
        ),
        (
            BridgeFamily.RANKING_LIMIT,
            build_intent(
                dimensions=(_dimension("cand_region", "handle_region"),),
                ranking=ResolvedRanking(
                    measure="DO NOT USE AS PHYSICAL METRIC",
                    direction="desc",
                    limit=3,
                ),
            ),
        ),
        (
            BridgeFamily.TWO_DIMENSIONS,
            build_intent(
                dimensions=(
                    _dimension("cand_region", "handle_region"),
                    _dimension("cand_channel", "handle_channel"),
                )
            ),
        ),
        (
            BridgeFamily.FILTER_PERIOD_DIMENSION,
            build_intent(
                dimensions=(_dimension("cand_channel", "handle_channel"),),
                filters=(north,),
                period_value=build_period(),
            ),
        ),
    )
