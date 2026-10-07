from __future__ import annotations

import pytest

from app.v3.analytical_boundary import (
    AnalyticalBoundaryError,
    AnalyticalEngineIdentityV1,
    AnalyticalExecutionManifestV1,
    AnalyticalFilterV1,
    AnalyticalIntentV1,
    AnalyticalManifestDataV1,
    AnalyticalObservedTemporalScopeV1,
    AnalyticalOperation,
    AnalyticalPeriodV1,
    AnalyticalRankingV1,
    project_analytical_intent_v1,
    verify_analytical_fulfillment_v1,
)
from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    AnalyticalTemporalChangeFrame,
)
from app.v3.research_contracts import (
    RankingBasis,
    RankingSurface,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeVersion,
    SemanticTargetKind,
    TemporalChangeFrameMode,
    TemporalRole,
)


def _intent(*, basis: RankingBasis = RankingBasis.CHANGE) -> AnalyticalIntentV1:
    return AnalyticalIntentV1(
        intent_id="goal-ranking",
        operation=AnalyticalOperation.RANK,
        metrics=("metric.downtime",),
        dimensions=("dimension.department",),
        filters=(
            AnalyticalFilterV1(
                semantic_ref="filter:plant-a",
                dimension_semantic_id="dimension.plant",
                value="Plant A",
            ),
        ),
        temporal_periods=(
            AnalyticalPeriodV1(
                role=TemporalRole.BASELINE_PERIOD,
                time_dimension_semantic_id="dimension.date",
                start="2026-05-01",
                end="2026-06-01",
            ),
            AnalyticalPeriodV1(
                role=TemporalRole.COMPARISON_PERIOD,
                time_dimension_semantic_id="dimension.date",
                start="2026-06-01",
                end="2026-07-01",
            ),
        ),
        ranking=AnalyticalRankingV1(
            kind="native_metric",
            metric="metric.downtime",
            basis=basis,
            direction="desc",
            top_k=1,
        ),
        row_grain=("dimension.department",),
        allowed_semantic_ids=(
            "metric.downtime",
            "dimension.department",
            "dimension.plant",
            "dimension.date",
            "metric.extra",
        ),
        semantic_context_version="ctx-v1",
        scope_lineage_id="lineage-v1",
        scope_version_id="scope_v1",
        scope_fingerprint="a" * 64,
        tenant_id="tenant-a",
        principal_id="principal-a",
        expected_resource_entity_ids=("resource-a",),
        currentness_token="current-v1",
        security_fingerprint="security-v1",
    )


def _manifest(
    intent: AnalyticalIntentV1,
    *,
    basis: RankingBasis | None = None,
) -> AnalyticalExecutionManifestV1:
    ranking = intent.ranking
    if basis is not None and ranking is not None:
        ranking = ranking.model_copy(update={"basis": basis})
    return AnalyticalExecutionManifestV1(
        execution_id="execution-1",
        fulfilled_intent_ids=(intent.intent_id,),
        metrics=intent.metrics,
        dimensions=intent.dimensions,
        filters=intent.filters,
        temporal_periods=intent.temporal_periods,
        temporal_observation_dimension=intent.temporal_observation_dimension,
        ranking=ranking,
        row_grain=intent.row_grain,
        result_dependency=intent.dependency,
        semantic_context_version=intent.semantic_context_version,
        scope_lineage_id=intent.scope_lineage_id,
        scope_version_id=intent.scope_version_id,
        scope_fingerprint=intent.scope_fingerprint,
        tenant_id=intent.tenant_id,
        principal_id=intent.principal_id,
        resource_entity_ids=intent.expected_resource_entity_ids,
        currentness_token=intent.currentness_token,
        security_fingerprint=intent.security_fingerprint,
        query_fingerprint="b" * 64,
        result_hash="c" * 64,
        engine_identity=AnalyticalEngineIdentityV1(
            repository="UpcyTech/dima-metabase-engine",
            revision_sha="d" * 40,
            runtime_tag="0.63.18-dima.11.1",
        ),
        data=AnalyticalManifestDataV1(
            columns=({"name": "department"}, {"name": "change"}),
            rows=(("Assembly", 4.2),),
        ),
        metadata={"latency_ms": 12, "physical_stage_count": 3},
    )


@pytest.mark.parametrize("basis", [RankingBasis.LEVEL, RankingBasis.CHANGE])
def test_level_and_change_are_accepted_only_when_manifest_matches(basis) -> None:
    intent = _intent(basis=basis)
    verify_analytical_fulfillment_v1(intent, _manifest(intent))


def test_change_rejects_level_manifest() -> None:
    intent = _intent(basis=RankingBasis.CHANGE)
    with pytest.raises(AnalyticalBoundaryError) as exc:
        verify_analytical_fulfillment_v1(
            intent,
            _manifest(intent, basis=RankingBasis.LEVEL),
        )
    assert exc.value.code == "ANALYTICAL_V1_RANKING_MISMATCH"


def test_wrong_metric_dimension_period_and_filter_are_rejected() -> None:
    intent = _intent()
    mutations = (
        ("metrics", ("metric.extra",), "ANALYTICAL_V1_METRIC_COVERAGE_MISMATCH"),
        ("dimensions", (), "ANALYTICAL_V1_DIMENSION_COVERAGE_MISMATCH"),
        (
            "temporal_periods",
            intent.temporal_periods[:1],
            "ANALYTICAL_V1_TEMPORAL_SCOPE_MISMATCH",
        ),
        ("filters", (), "ANALYTICAL_V1_FILTER_SCOPE_MISMATCH"),
    )
    for field, value, code in mutations:
        with pytest.raises(AnalyticalBoundaryError) as exc:
            verify_analytical_fulfillment_v1(
                intent,
                _manifest(intent).model_copy(update={field: value}),
            )
        assert exc.value.code == code


def test_foreign_semantic_scope_tenant_and_principal_are_rejected() -> None:
    intent = _intent()
    foreign = _manifest(intent).model_copy(
        update={"metrics": (*intent.metrics, "metric.foreign")}
    )
    with pytest.raises(AnalyticalBoundaryError) as exc:
        verify_analytical_fulfillment_v1(intent, foreign)
    assert exc.value.code == "ANALYTICAL_V1_FOREIGN_SEMANTIC_ID"

    for field, value in (
        ("scope_version_id", "scope_v2"),
        ("tenant_id", "tenant-b"),
        ("principal_id", "principal-b"),
    ):
        with pytest.raises(AnalyticalBoundaryError) as exc:
            verify_analytical_fulfillment_v1(
                intent,
                _manifest(intent).model_copy(update={field: value}),
            )
        assert exc.value.code == "ANALYTICAL_V1_EXACT_CONTEXT_MISMATCH"


def test_legal_extra_metadata_is_ignored() -> None:
    intent = _intent()
    manifest = _manifest(intent).model_copy(
        update={
            "metadata": {
                "latency_ms": 25,
                "physical_stage_count": 99,
                "jvm_datetime_class": "implementation-detail",
            }
        }
    )
    verify_analytical_fulfillment_v1(intent, manifest)


def test_projection_is_a_strangler_view_over_existing_authority() -> None:
    metric = ResearchSemanticRef(
        source_mention="downtime",
        candidate_id="metric.downtime",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Downtime",
    )
    department = ResearchSemanticRef(
        source_mention="department",
        candidate_id="dimension.department",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Department",
    )
    date_ref = ResearchSemanticRef(
        source_mention="month",
        candidate_id="dimension.date",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Month",
    )
    question = ResearchQuestion(
        goal_id="goal-ranking",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank departments by May-to-June downtime change.",
        subject_refs=(metric,),
        related_refs=(department,),
        ranking=RankingSurface(
            text="largest change",
            direction="desc",
            limit=1,
            measure_semantic_id="metric.downtime",
            basis=RankingBasis.CHANGE,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    scope = ResearchScope(
        semantic_refs=(metric, department, date_ref),
        time_surfaces=("May", "June"),
        periods=(
            ResearchTimePeriod(
                source_text="May",
                time_dimension_candidate_id="dimension.date",
                start="2026-05-01",
                end="2026-06-01",
                role=TemporalRole.BASELINE_PERIOD,
            ),
            ResearchTimePeriod(
                source_text="June",
                time_dimension_candidate_id="dimension.date",
                start="2026-06-01",
                end="2026-07-01",
                role=TemporalRole.COMPARISON_PERIOD,
            ),
        ),
        temporal_dimension_ids=("dimension.date",),
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    )
    baseline = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.date",
        start="2026-05-01",
        end="2026-06-01",
    )
    comparison = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.date",
        start="2026-06-01",
        end="2026-07-01",
    )
    contract = AnalyticalRequestContract(
        authority_id="authority-1",
        request_ref="goal-ranking",
        semantic_context_version="ctx-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-v1",
            version_id="scope_v1",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=("metric.downtime",),
        dimension_refs=("dimension.department",),
        comparison=AnalyticalComparisonInvariant(
            mode="explicit_periods",
            reference_period=baseline,
            base_period=comparison,
        ),
        temporal_change_frame=AnalyticalTemporalChangeFrame(
            mode=TemporalChangeFrameMode.PAIR,
            time_dimension="dimension.date",
            baseline_period=baseline,
            comparison_period=comparison,
        ),
        ranking=AnalyticalRankingInvariant(
            measure="metric.downtime",
            direction="desc",
            limit=1,
            basis=RankingBasis.CHANGE,
        ),
    )
    intent = project_analytical_intent_v1(
        question=question,
        scope=scope,
        contract=contract,
        tenant_id="tenant-a",
        principal_id="principal-a",
        currentness_token="current-v1",
        security_fingerprint="security-v1",
    )
    assert intent.operation == AnalyticalOperation.RANK
    assert intent.ranking is not None
    assert intent.ranking.basis == RankingBasis.CHANGE
    assert [item.role for item in intent.temporal_periods] == [
        TemporalRole.BASELINE_PERIOD,
        TemporalRole.COMPARISON_PERIOD,
    ]


def test_one_manifest_can_fulfill_comparison_and_topk_independently() -> None:
    acquisition = _intent().model_copy(
        update={
            "intent_id": "goal-acquisition",
            "ranking": _intent().ranking.model_copy(update={"top_k": None}),
        }
    )
    comparison = acquisition.model_copy(
        update={
            "intent_id": "goal-comparison",
            "operation": AnalyticalOperation.COMPARE,
            "ranking": None,
        }
    )
    top2 = acquisition.model_copy(
        update={
            "intent_id": "goal-top2",
            "ranking": acquisition.ranking.model_copy(update={"top_k": 2}),
        }
    )
    manifest = _manifest(acquisition).model_copy(
        update={
            "fulfilled_intent_ids": (
                comparison.intent_id,
                top2.intent_id,
            )
        }
    )

    verify_analytical_fulfillment_v1(comparison, manifest)
    verify_analytical_fulfillment_v1(top2, manifest)


def test_shared_manifest_requires_each_consumer_verifier_to_pass() -> None:
    acquisition = _intent().model_copy(
        update={
            "intent_id": "goal-acquisition",
            "ranking": _intent().ranking.model_copy(update={"top_k": None}),
        }
    )
    top2 = acquisition.model_copy(
        update={
            "intent_id": "goal-top2",
            "ranking": acquisition.ranking.model_copy(update={"top_k": 2}),
        }
    )
    wrong_basis = top2.model_copy(
        update={
            "intent_id": "goal-wrong-basis",
            "ranking": top2.ranking.model_copy(update={"basis": RankingBasis.LEVEL}),
        }
    )
    manifest = _manifest(acquisition).model_copy(
        update={
            "fulfilled_intent_ids": (
                top2.intent_id,
                wrong_basis.intent_id,
            )
        }
    )

    verify_analytical_fulfillment_v1(top2, manifest)
    with pytest.raises(AnalyticalBoundaryError) as exc:
        verify_analytical_fulfillment_v1(wrong_basis, manifest)
    assert exc.value.code == "ANALYTICAL_V1_RANKING_MISMATCH"


def test_bounded_result_cannot_fulfill_unbounded_ranking_consumer() -> None:
    intent = _intent().model_copy(
        update={
            "intent_id": "goal-unbounded",
            "ranking": _intent().ranking.model_copy(update={"top_k": None}),
        }
    )
    manifest = _manifest(intent).model_copy(
        update={"ranking": intent.ranking.model_copy(update={"top_k": 2})}
    )

    with pytest.raises(AnalyticalBoundaryError) as exc:
        verify_analytical_fulfillment_v1(intent, manifest)
    assert exc.value.code == "ANALYTICAL_V1_RANKING_MISMATCH"


def test_role_neutral_execution_time_facts_are_judged_only_by_final_verifier() -> None:
    intent = _intent()
    manifest = _manifest(intent).model_copy(
        update={
            "fulfilled_intent_ids": (),
            "consumer_intent_ids": (intent.intent_id,),
            "temporal_periods": (),
            "observed_temporal_scopes": (
                AnalyticalObservedTemporalScopeV1(
                    time_dimension_semantic_id="dimension.date",
                    start="2026-05-01T00:00:00.000Z",
                    end="2026-06-01T00:00:00.000Z",
                    source="change_baseline",
                ),
                AnalyticalObservedTemporalScopeV1(
                    time_dimension_semantic_id="dimension.date",
                    start="2026-06-01T00:00:00.000Z",
                    end="2026-07-01T00:00:00.000Z",
                    source="change_comparison",
                ),
            ),
            "rankings": (intent.ranking,),
            "ranking": None,
        }
    )

    verify_analytical_fulfillment_v1(intent, manifest)


def test_execution_fact_period_mismatch_fails_only_at_final_verifier() -> None:
    intent = _intent()
    manifest = _manifest(intent).model_copy(
        update={
            "fulfilled_intent_ids": (),
            "consumer_intent_ids": (intent.intent_id,),
            "temporal_periods": (),
            "observed_temporal_scopes": (
                AnalyticalObservedTemporalScopeV1(
                    time_dimension_semantic_id="dimension.date",
                    start="2026-04-01T00:00:00Z",
                    end="2026-05-01T00:00:00Z",
                    source="result_bucket",
                ),
            ),
            "rankings": (intent.ranking,),
            "ranking": None,
        }
    )

    with pytest.raises(AnalyticalBoundaryError) as exc:
        verify_analytical_fulfillment_v1(intent, manifest)
    assert exc.value.code == "ANALYTICAL_V1_TEMPORAL_SCOPE_MISMATCH"
