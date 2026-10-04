from __future__ import annotations

import pytest
from hypothesis import given, seed, settings

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    AnalyticalTemporalChangeFrame,
    RankingBasis as ProductRankingBasis,
)
from tests.semantic_spec.mutation_canaries import mutation_report_payload
from tests.semantic_spec.saturation import (
    ComparisonType,
    RankingDirection,
    SaturationCase,
    expected_pair_value_counts,
    metric_count,
    ranking_period_structure,
    saturation_dimension_values,
    saturation_pair_coverage,
    saturation_pairwise_matrix,
    top_k_value,
    classify_saturation_case,
)
from app.v3.research_contracts import TemporalChangeFrameMode
from tests.semantic_spec.model import PeriodStructure
from tests.semantic_spec.strategies import saturation_cases


def _product_ranking_accepts(case: SaturationCase) -> bool:
    period_structure = ranking_period_structure(case)
    comparison = None
    period = None
    if period_structure == PeriodStructure.BASELINE_CANDIDATE:
        comparison = AnalyticalComparisonInvariant(
            mode="saturation",
            reference_period=AnalyticalPeriodInvariant(
                kind="symbolic",
                time_dimension="dimension.time",
                start="2026-01-01",
                end="2026-02-01",
            ),
            base_period=AnalyticalPeriodInvariant(
                kind="symbolic",
                time_dimension="dimension.time",
                start="2026-02-01",
                end="2026-03-01",
            ),
        )
    elif period_structure == PeriodStructure.SINGLE_WINDOW:
        period = AnalyticalPeriodInvariant(
            kind="symbolic",
            time_dimension="dimension.time",
            start="2026-01-01",
            end="2026-03-01",
        )

    metrics = tuple(
        f"metric.m{index}"
        for index in range(1, metric_count(case) + 1)
    )
    direction = (
        "asc" if case.ranking_direction == RankingDirection.ASC else "desc"
    )
    temporal_change_frame = None
    if (
        case.ranking_basis.value == "CHANGE"
        and comparison is not None
    ):
        temporal_change_frame = AnalyticalTemporalChangeFrame(
            mode=TemporalChangeFrameMode.PAIR,
            time_dimension=comparison.reference_period.time_dimension,
            baseline_period=comparison.reference_period,
            comparison_period=comparison.base_period,
        )
    elif (
        case.ranking_basis.value == "CHANGE"
        and period_structure == PeriodStructure.SINGLE_WINDOW
        and period is not None
    ):
        temporal_change_frame = AnalyticalTemporalChangeFrame(
            mode=TemporalChangeFrameMode.SPAN,
            time_dimension=period.time_dimension,
            span_period=period,
        )

    payload = dict(
        authority_id="auth-saturation",
        request_ref="req-saturation",
        semantic_context_version="ctx-saturation-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-saturation",
            version_id="scope_v1",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=metrics,
        period=period,
        comparison=comparison,
        temporal_change_frame=temporal_change_frame,
        ranking=AnalyticalRankingInvariant(
            measure=metrics[0],
            direction=direction,
            limit=top_k_value(case),
            basis=ProductRankingBasis(case.ranking_basis.value.lower()),
        ),
    )
    try:
        AnalyticalRequestContract(**payload)
    except ValueError:
        return False
    return True


def test_saturation_pairwise_matrix_is_complete_for_13_dimensions() -> None:
    cases = saturation_pairwise_matrix()
    coverage = saturation_pair_coverage(cases)
    expected = expected_pair_value_counts()

    assert len(saturation_dimension_values()) == 13
    assert len(coverage) == 78
    assert set(coverage) == set(expected)
    assert all(len(coverage[key]) == count for key, count in expected.items())
    assert all(not classify_saturation_case(case).new_family for case in cases)


@seed(2026100301)
@settings(max_examples=1200, deadline=None, database=None)
@given(case=saturation_cases())
def test_semantic_saturation_wave_a_matches_generic_product_laws(
    case: SaturationCase,
) -> None:
    outcome = classify_saturation_case(case)
    assert not outcome.new_family
    assert _product_ranking_accepts(case) == outcome.ranking_coherent


def test_semantic_mutation_canaries_are_all_detected() -> None:
    payload = mutation_report_payload()
    assert payload["total"] == 5
    assert payload["killed"] == 5
    assert payload["detection_rate"] == 1.0
    assert payload["all_detected"] is True
