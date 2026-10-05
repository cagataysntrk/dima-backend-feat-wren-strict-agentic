from __future__ import annotations

import pytest

from app.v3.analytical_request_contract import (
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research_contracts import RankingBasis
from app.v3.research_result_dependency import (
    ResultDependencyProjectionError,
    resolve_selection_binding_v1,
)


def _contract() -> AnalyticalRequestContract:
    return AnalyticalRequestContract(
        authority_id="authority-selection-v1",
        request_ref="goal-child",
        semantic_context_version="ctx-selection-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-selection-v1",
            version_id="scope_v3",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=("metric.fault_count",),
        dimension_refs=("dimension.machine",),
    )


def _result(rows=(("Assembly", 12.0), ("Packaging", 8.0))):
    return {
        "data": {
            "cols": [
                {
                    "id": 44,
                    "table_id": 10,
                    "name": "department",
                    "field_ref": ["field", 44, None],
                },
                {"name": "change", "field_ref": ["aggregation", 0]},
            ],
            "rows": [list(item) for item in rows],
        }
    }


@pytest.mark.parametrize(
    ("basis", "direction", "top_k"),
    [
        (RankingBasis.LEVEL, "asc", 1),
        (RankingBasis.LEVEL, "desc", 3),
        (RankingBasis.CHANGE, "asc", 2),
        (RankingBasis.CHANGE, "desc", 1),
    ],
)
def test_selection_binding_preserves_parent_order_and_ranking_authority(
    basis, direction, top_k
) -> None:
    base = _contract()
    resolution = resolve_selection_binding_v1(
        base_contract=base,
        source_goal_id="goal-parent",
        source_evidence_id="evidence-parent",
        source_receipt_id="receipt-parent",
        source_result_hash="b" * 64,
        parent_execution_id="execution-parent-1",
        dimension_semantic_id="dimension.department",
        native_field_id=44,
        parent_result=_result(),
        ranking_basis=basis,
        ranking_direction=direction,
        top_k=top_k,
        dimension_name="Department",
        expected_parent_result_hash="b" * 64,
    )

    binding = resolution.selection_binding
    assert binding is not None
    assert binding.parent_execution_id == "execution-parent-1"
    assert binding.parent_result_hash == "b" * 64
    assert binding.selected_row_index == 0
    assert binding.selected_semantic_id == "dimension.department"
    assert binding.selected_value == "Assembly"
    assert binding.selection_rule.ranking_basis == basis
    assert binding.selection_rule.ranking_direction == direction
    assert binding.selection_rule.top_k == top_k
    assert binding.scope_version_id == "scope_v3"

    # Child execution receives exactly one source-backed filter. Accepted scope
    # identity/currentness is not replaced and parent ranking is not recomputed.
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint
    assert resolution.contract.filters[-1].source_candidate_id == "dimension.department"
    assert resolution.contract.filters[-1].value == "Assembly"


def test_selection_binding_wrong_parent_hash_fails_closed_before_selection() -> None:
    with pytest.raises(ResultDependencyProjectionError) as exc:
        resolve_selection_binding_v1(
            base_contract=_contract(),
            source_goal_id="goal-parent",
            source_evidence_id="evidence-parent",
            source_receipt_id="receipt-parent",
            source_result_hash="b" * 64,
            parent_execution_id="execution-parent-1",
            dimension_semantic_id="dimension.department",
            native_field_id=44,
            parent_result=_result(),
            ranking_basis=RankingBasis.CHANGE,
            ranking_direction="desc",
            top_k=1,
            expected_parent_result_hash="c" * 64,
        )
    assert exc.value.code == "R1_SELECTION_BINDING_RESULT_HASH_MISMATCH"


def test_selection_binding_empty_parent_fails_closed_without_fallback() -> None:
    with pytest.raises(ResultDependencyProjectionError) as exc:
        resolve_selection_binding_v1(
            base_contract=_contract(),
            source_goal_id="goal-parent",
            source_evidence_id="evidence-parent",
            source_receipt_id="receipt-parent",
            source_result_hash="b" * 64,
            parent_execution_id="execution-parent-1",
            dimension_semantic_id="dimension.department",
            native_field_id=44,
            parent_result=_result(rows=()),
            ranking_basis=RankingBasis.CHANGE,
            ranking_direction="desc",
            top_k=1,
            expected_parent_result_hash="b" * 64,
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_PARENT_EMPTY"


def test_selection_binding_unsupported_selection_rule_fails_closed() -> None:
    with pytest.raises((ResultDependencyProjectionError, ValueError)):
        resolve_selection_binding_v1(
            base_contract=_contract(),
            source_goal_id="goal-parent",
            source_evidence_id="evidence-parent",
            source_receipt_id="receipt-parent",
            source_result_hash="b" * 64,
            parent_execution_id="execution-parent-1",
            dimension_semantic_id="dimension.department",
            native_field_id=44,
            parent_result=_result(),
            selection="last_ranked_entity",  # type: ignore[arg-type]
            expected_parent_result_hash="b" * 64,
        )
