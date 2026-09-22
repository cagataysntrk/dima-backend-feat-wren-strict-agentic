from __future__ import annotations

import pytest

from app.v2.models import (
    PeriodKind,
    ResolvedComparison as V2ResolvedComparison,
    ResolvedFilterRef as V2ResolvedFilterRef,
    ResolvedPeriod as V2ResolvedPeriod,
    ResolvedSemanticRef as V2ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v3.analytics_contract import (
    ResolvedAnalyticsIntentBuilder,
    StandardProjection,
)
from app.v3.authority import (
    SemanticSurfaceCoverage,
    SemanticSurfaceRecord,
    SemanticSurfaceState,
    StandardAuthoritySealer,
    StandardWorkMode,
)
from app.v3.substrate.wren import WrenSubstrateAdapter


TENANT = "tenant-m1-family"
CONTEXT = "ctx-m1-family"


def _registry_and_handles():
    handles = SemanticHandleRegistry()

    metric = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        resolver_provenance_id="candidate:metric",
        target_kind="metric",
        canonical_target=V2ResolvedSemanticRef(
            candidate_id="cand-source-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="net_gelir",
            cube_names=("sales",),
        ),
    )
    dimension_region = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        resolver_provenance_id="candidate:region",
        target_kind="dimension",
        canonical_target=V2ResolvedSemanticRef(
            candidate_id="cand-source-region",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="region",
            cube_names=("sales",),
        ),
    )
    dimension_channel = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        resolver_provenance_id="candidate:channel-dim",
        target_kind="dimension",
        canonical_target=V2ResolvedSemanticRef(
            candidate_id="cand-source-channel-dim",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="channel",
            cube_names=("sales",),
        ),
    )
    filter_web = handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        resolver_provenance_id="candidate:web",
        target_kind="entity_value",
        canonical_target=V2ResolvedFilterRef(
            candidate_id="cand-source-web",
            dimension_name="channel",
            value="Web",
            cube_names=("sales",),
            sensitive=False,
        ),
    )

    base_period = V2ResolvedPeriod(
        kind=PeriodKind.THIS_MONTH,
        source_text="bu ay",
        time_dimension="event_date",
        start="2026-09-01",
        end="2026-09-30",
    )
    period = handles.mint_from_temporal_engine(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        temporal_provenance_id="temporal:period",
        target_kind="period",
        canonical_target=base_period,
    )
    comparison = handles.mint_from_temporal_engine(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        temporal_provenance_id="temporal:comparison",
        target_kind="comparison",
        canonical_target=V2ResolvedComparison(
            mode="previous_period",
            source_text="önceki dönemle karşılaştır",
            base_period=base_period,
            reference_period=V2ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="önceki ay",
                time_dimension="event_date",
                start="2026-08-01",
                end="2026-08-31",
            ),
        ),
    )
    return handles, {
        "metric": metric,
        "region": dimension_region,
        "channel": dimension_channel,
        "filter": filter_web,
        "period": period,
        "comparison": comparison,
    }


def _coverage(*, projection, ids):
    records = []
    for index, (kind, handle_id) in enumerate(ids, start=1):
        records.append(
            SemanticSurfaceRecord(
                source_ref="src_" + f"{index:024x}",
                surface_text=f"surface-{index}",
                kind_hint=kind,
                state=SemanticSurfaceState.BOUND,
                handle_id=handle_id,
            )
        )
    return SemanticSurfaceCoverage(
        turn_id="turn-family",
        attempt_id="attempt-family",
        context_version=CONTEXT,
        surfaces=tuple(records),
    )


def _build_intent(projection, surface_ids):
    handles, _ = _registry_and_handles()
    # Projection handle ids were minted by the caller's registry, so this helper is not used.
    raise AssertionError("use _case()")


def _case(*, dimensions=(), filters=(), period=False, comparison=False, ranking=False):
    handles, h = _registry_and_handles()
    projection = StandardProjection(
        obligation_ids=("U_FAMILY",),
        metric_handles=(h["metric"].handle_id,),
        dimension_handles=tuple(h[name].handle_id for name in dimensions),
        filter_handles=tuple(h[name].handle_id for name in filters),
        period_handle=h["period"].handle_id if period else None,
        comparison_handle=h["comparison"].handle_id if comparison else None,
        ranking_direction="desc" if ranking else None,
        limit=5 if ranking else None,
    )
    surface_ids = [("metric", h["metric"].handle_id)]
    surface_ids.extend(("dimension", h[name].handle_id) for name in dimensions)
    surface_ids.extend(("filter", h[name].handle_id) for name in filters)
    if period:
        surface_ids.append(("time", h["period"].handle_id))
    if comparison:
        surface_ids.append(("comparison", h["comparison"].handle_id))

    coverage = _coverage(projection=projection, ids=surface_ids)
    authority = StandardAuthoritySealer(semantic_handles=handles).seal(
        projection=projection,
        coverage=coverage,
        turn_id="turn-family",
        request_ref="request-family",
        source_message_hash="a" * 64,
        context_version=CONTEXT,
        tenant_binding=TENANT,
        accepted_attempt_id="attempt-family",
        model_role="STANDARD_PROFILE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )
    intent = ResolvedAnalyticsIntentBuilder(semantic_handles=handles).build(
        projection=projection,
        authority=authority,
        tenant_binding=TENANT,
        principal_subject="user-family",
        principal_roles=("owner",),
    )
    adapter = WrenSubstrateAdapter(
        service=None,
        principal=None,
        runtime=None,
        receipt_writer=None,
    )
    return intent, adapter._to_ir(intent)


@pytest.mark.parametrize(
    "case_kwargs",
    [
        {},
        {"dimensions": ("region",)},
        {"filters": ("filter",)},
        {"period": True},
        {"period": True, "comparison": True},
        {"dimensions": ("region",), "ranking": True},
        {"dimensions": ("region", "channel")},
        {
            "dimensions": ("region",),
            "filters": ("filter",),
            "period": True,
            "comparison": True,
            "ranking": True,
        },
    ],
    ids=[
        "metric",
        "metric_dimension",
        "metric_filter",
        "metric_period",
        "previous_period_comparison",
        "ranking_limit",
        "two_dimensions",
        "combined",
    ],
)
def test_resolved_intent_to_wren_ir_is_lossless_across_standard_families(case_kwargs):
    intent, ir = _case(**case_kwargs)

    assert ir.context_version == CONTEXT
    assert ir.cube == "sales"
    assert len(ir.metrics) == 1
    assert ir.metrics[0].candidate_id == "cand-source-metric"
    assert ir.metrics[0].canonical_name == "net_gelir"

    assert [item.candidate_id for item in ir.dimensions] == [
        item.source_candidate_id for item in intent.dimensions
    ]
    assert [item.candidate_id for item in ir.filters] == [
        item.source_candidate_id for item in intent.filters
    ]
    assert [item.canonical_name for item in ir.dimensions] == [
        item.canonical_name for item in intent.dimensions
    ]

    assert (ir.period is not None) is bool(case_kwargs.get("period"))
    assert (ir.comparison is not None) is bool(case_kwargs.get("comparison"))
    assert (ir.ranking is not None) is bool(case_kwargs.get("ranking"))

    if ir.period is not None:
        assert ir.period.start == intent.period.start
        assert ir.period.end == intent.period.end
        assert ir.period.time_dimension == intent.period.time_dimension

    if ir.comparison is not None:
        assert ir.comparison.base_period.start == intent.comparison.base_period.start
        assert (
            ir.comparison.reference_period.start
            == intent.comparison.reference_period.start
        )

    if ir.ranking is not None:
        assert ir.ranking.measure == intent.ranking.measure
        assert ir.ranking.direction == intent.ranking.direction
        assert ir.ranking.limit == intent.ranking.limit


def test_combined_family_resolves_every_handle_once_before_substrate():
    handles, h = _registry_and_handles()
    projection = StandardProjection(
        obligation_ids=("U_ALL",),
        metric_handles=(h["metric"].handle_id,),
        dimension_handles=(h["region"].handle_id,),
        filter_handles=(h["filter"].handle_id,),
        period_handle=h["period"].handle_id,
        comparison_handle=h["comparison"].handle_id,
        ranking_direction="desc",
        limit=5,
    )
    coverage = _coverage(
        projection=projection,
        ids=[
            ("metric", h["metric"].handle_id),
            ("dimension", h["region"].handle_id),
            ("filter", h["filter"].handle_id),
            ("time", h["period"].handle_id),
            ("comparison", h["comparison"].handle_id),
        ],
    )
    authority = StandardAuthoritySealer(semantic_handles=handles).seal(
        projection=projection,
        coverage=coverage,
        turn_id="turn-family",
        request_ref="request-family",
        source_message_hash="b" * 64,
        context_version=CONTEXT,
        tenant_binding=TENANT,
        accepted_attempt_id="attempt-family",
        model_role="STANDARD_PROFILE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )

    class CountingRegistry:
        def __init__(self, inner):
            self.inner = inner
            self.calls = []

        def binding_for_execution(self, handle_id, *, tenant_binding, context_version):
            self.calls.append(handle_id)
            return self.inner.binding_for_execution(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )

    counting = CountingRegistry(handles)
    intent = ResolvedAnalyticsIntentBuilder(semantic_handles=counting).build(
        projection=projection,
        authority=authority,
        tenant_binding=TENANT,
        principal_subject="user-family",
        principal_roles=("owner",),
    )

    expected = list(dict.fromkeys([
        h["metric"].handle_id,
        h["region"].handle_id,
        h["filter"].handle_id,
        h["period"].handle_id,
        h["comparison"].handle_id,
    ]))
    assert counting.calls == expected
    assert len(intent.resolved_intent_hash) == 64
