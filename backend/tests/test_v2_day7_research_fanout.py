"""Provider-free D7 fanout policy attacks."""

from __future__ import annotations

from app.v2.manager_models import ManagerBudget
from app.v2.manager_runtime import ManagerRuntime
from app.v2.research_fanout import (
    CardinalityClass,
    CardinalityObservation,
    CardinalitySource,
    FanoutRequest,
    FanoutStrategy,
    PriorityProvenance,
    ResearchFanoutPolicy,
    governed_dimension_cardinality,
)


def _known(n: int) -> CardinalityObservation:
    return CardinalityObservation(
        estimate=n,
        source=CardinalitySource.GOVERNED_METADATA,
        exact=True,
    )


def _request(
    *,
    candidates=("A", "B", "C", "D", "E", "F"),
    cardinality=None,
    budget=8,
    depth=0,
    max_depth=3,
    max_children=4,
    unknown_children=2,
    priority=PriorityProvenance.NONE,
):
    return FanoutRequest(
        candidate_keys=tuple(candidates),
        cardinality=cardinality or CardinalityObservation(source=CardinalitySource.UNKNOWN),
        priority_provenance=priority,
        remaining_query_budget=budget,
        current_branch_depth=depth,
        max_branch_depth=max_depth,
        max_children=max_children,
        unknown_children=unknown_children,
    )


def test_low_cardinality_allows_complete_bounded_family():
    result = ResearchFanoutPolicy().decide(
        _request(cardinality=_known(3))
    )
    assert result.classification == CardinalityClass.LOW
    assert result.strategy == FanoutStrategy.COMPLETE_BOUNDED
    assert result.allowed_children == 3
    assert result.selected_candidate_keys == ("A", "B", "C")


def test_high_cardinality_without_governed_priority_is_bounded_subset_not_fake_top_k():
    result = ResearchFanoutPolicy().decide(
        _request(cardinality=_known(250))
    )
    assert result.classification == CardinalityClass.HIGH
    assert result.strategy == FanoutStrategy.BOUNDED_SUBSET
    assert result.allowed_children == 4
    assert result.selected_candidate_keys == ("A", "B", "C", "D")
    assert "Top-K" in result.reason


def test_high_cardinality_with_verified_evidence_priority_may_be_called_top_k():
    result = ResearchFanoutPolicy().decide(
        _request(
            cardinality=_known(250),
            priority=PriorityProvenance.VERIFIED_EVIDENCE,
        )
    )
    assert result.classification == CardinalityClass.HIGH
    assert result.strategy == FanoutStrategy.BOUNDED_TOP_K
    assert result.allowed_children == 4
    assert result.selected_candidate_keys == ("A", "B", "C", "D")
    assert "VERIFIED_EVIDENCE" in result.reason
    assert "synthetic Other" in result.reason


def test_unknown_cardinality_is_conservative_not_unlimited():
    result = ResearchFanoutPolicy().decide(_request())
    assert result.classification == CardinalityClass.UNKNOWN
    assert result.strategy == FanoutStrategy.CONSERVATIVE_BOUNDED
    assert result.allowed_children == 2
    assert result.selected_candidate_keys == ("A", "B")


def test_nearly_exhausted_query_budget_caps_children():
    result = ResearchFanoutPolicy().decide(
        _request(cardinality=_known(100), budget=1)
    )
    assert result.allowed_children == 1
    assert result.selected_candidate_keys == ("A",)


def test_exhausted_query_budget_stops_fanout():
    result = ResearchFanoutPolicy().decide(
        _request(cardinality=_known(2), budget=0)
    )
    assert result.strategy == FanoutStrategy.STOP
    assert result.allowed_children == 0


def test_branch_depth_limit_stops_fanout():
    result = ResearchFanoutPolicy().decide(
        _request(cardinality=_known(3), depth=3, max_depth=3)
    )
    assert result.strategy == FanoutStrategy.STOP
    assert result.allowed_children == 0
    assert "depth" in result.reason


def test_duplicate_candidate_branches_are_deduplicated_before_bound():
    result = ResearchFanoutPolicy().decide(
        _request(
            candidates=("A", "A", "B", "B", "C"),
            cardinality=_known(3),
        )
    )
    assert result.deduplicated_candidate_count == 3
    assert result.selected_candidate_keys == ("A", "B", "C")


def test_more_proposals_than_safety_bound_are_capped_not_executed_unbounded():
    result = ResearchFanoutPolicy().decide(
        _request(
            candidates=tuple(f"C{i}" for i in range(20)),
            cardinality=_known(20),
            max_children=4,
        )
    )
    assert result.allowed_children == 4
    assert len(result.selected_candidate_keys) == 4


def test_wren_dimension_values_prove_only_exposed_exact_low_cardinality():
    schema = {
        "cubes": [
            {
                "name": "sales",
                "dimension_values": {
                    "region": ["North", "South", "West"],
                },
            }
        ]
    }
    obs = governed_dimension_cardinality(
        schema=schema,
        cube_name="sales",
        dimension_name="region",
    )
    assert obs.source == CardinalitySource.GOVERNED_METADATA
    assert obs.exact is True
    assert obs.estimate == 3


def test_missing_wren_dimension_values_are_unknown_not_assumed_high():
    schema = {"cubes": [{"name": "sales", "dimension_values": {}}]}
    obs = governed_dimension_cardinality(
        schema=schema,
        cube_name="sales",
        dimension_name="customer",
    )
    assert obs.source == CardinalitySource.UNKNOWN
    assert obs.estimate is None
    assert obs.exact is False


def test_fanout_uses_same_canonical_manager_query_budget_truth():
    runtime = ManagerRuntime(
        request_ref="fanout-budget",
        budget=ManagerBudget(
            max_tool_calls=12,
            max_data_queries=2,
            max_manager_turns=6,
        ),
    )
    assert runtime.remaining_data_queries == 2

    result = ResearchFanoutPolicy().decide(
        _request(
            cardinality=_known(100),
            budget=runtime.remaining_data_queries,
        )
    )
    assert result.allowed_children == 2
