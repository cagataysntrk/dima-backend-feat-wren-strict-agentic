from __future__ import annotations

import pytest

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    AnalyticalTemporalObservationInvariant,
    material_coverage_contract,
)
from app.v3.brain_v2.adaptive_test_design import (
    AdaptiveTestDesignError,
    NextTestMaterialDisposition,
    evaluate_next_test_material_delta,
    typed_child_material_delta_for_next_test,
    typed_child_scope_for_next_test,
)
from app.v3.hypothesis_root_cause_v1 import (
    ExpectedDiscriminatoryValue,
    NextTestEvidenceSurface,
    NextTestRequest,
)


def _request() -> NextTestRequest:
    return NextTestRequest(
        request_id="ntr_" + "1" * 24,
        ambiguity_code="TEMPORAL_DISCRIMINATION_REQUIRED",
        hypothesis_ids=("p19h_" + "2" * 24, "p19h_" + "3" * 24),
        required_evidence_surface=NextTestEvidenceSurface.TEMPORAL_ORDER,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id="atl_test",
        scope_version_id="scope_v1",
    )


def _base(**updates) -> AnalyticalRequestContract:
    payload = dict(
        authority_id="auth-test",
        request_ref="req-test",
        semantic_context_version="ctx-test",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl_test",
            version_id="scope_v1",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=("metric.effect", "metric.h1", "metric.h2"),
        dimension_refs=(),
        filters=(),
        period=AnalyticalPeriodInvariant(
            kind="explicit_half_open_window",
            time_dimension="dimension.event_date",
            start="2026-05-01T00:00:00Z",
            end="2026-07-01T00:00:00Z",
        ),
        comparison=None,
        temporal_observation=None,
        ranking=None,
        grain_constraints=(),
        requested_output_surfaces=("report",),
    )
    payload.update(updates)
    return AnalyticalRequestContract(**payload)


def test_temporal_order_child_adds_real_time_surface_for_pooled_window():
    parent = _base()

    child = typed_child_scope_for_next_test(
        parent=parent,
        request=_request(),
    )

    assert child.dimension_refs == ("dimension.event_date",)
    assert child.grain_constraints == ("dimension.event_date",)
    assert child.period == parent.period
    assert child.comparison is None
    assert child.temporal_observation is None


def test_temporal_order_child_rejects_comparison_surface_already_observed():
    may = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.event_date",
        start="2026-05-01T00:00:00Z",
        end="2026-06-01T00:00:00Z",
    )
    june = AnalyticalPeriodInvariant(
        kind="explicit_half_open",
        time_dimension="dimension.event_date",
        start="2026-06-01T00:00:00Z",
        end="2026-07-01T00:00:00Z",
    )
    parent = _base(
        period=None,
        comparison=AnalyticalComparisonInvariant(
            mode="explicit_periods",
            reference_period=may,
            base_period=june,
        ),
        temporal_observation=AnalyticalTemporalObservationInvariant(
            time_dimension="dimension.event_date",
            minimum_distinct_values=2,
        ),
    )

    with pytest.raises(AdaptiveTestDesignError, match="already observable"):
        typed_child_scope_for_next_test(
            parent=parent,
            request=_request(),
        )


def test_temporal_order_child_rejects_change_surface_already_observed():
    parent = _base(
        temporal_observation=AnalyticalTemporalObservationInvariant(
            time_dimension="dimension.event_date",
            minimum_distinct_values=2,
        ),
    )

    with pytest.raises(AdaptiveTestDesignError, match="already observable"):
        typed_child_scope_for_next_test(
            parent=parent,
            request=_request(),
        )

def _governed_refs() -> tuple[str, ...]:
    return (
        "metric.effect",
        "metric.h1",
        "metric.h2",
        "dimension.event_date",
    )


def test_material_coverage_projection_separates_required_from_allowed_time_breakout():
    contract = _base()

    coverage = material_coverage_contract(contract)

    assert coverage.scope_fingerprint == contract.scope_fingerprint
    assert coverage.material_fingerprint == contract.material_fingerprint
    assert coverage.required_metric_refs == contract.metric_refs
    assert coverage.allowed_metric_refs == contract.metric_refs
    assert coverage.required_breakout_refs == ()
    assert coverage.allowed_breakout_refs == ("dimension.event_date",)
    assert coverage.exact_filter_source_refs == ()
    assert coverage.time_breakout_requirement == "allowed"


def test_typed_child_material_delta_preserves_scope_and_changes_material_fingerprint():
    parent = _base()

    delta = typed_child_material_delta_for_next_test(
        parent=parent,
        request=_request(),
        governed_semantic_refs=_governed_refs(),
    )

    assert delta.scope_fingerprint == parent.scope_fingerprint
    assert delta.parent_material_fingerprint == parent.material_fingerprint
    assert delta.child_material_fingerprint == delta.child_contract.material_fingerprint
    assert delta.child_material_fingerprint != delta.parent_material_fingerprint
    assert delta.added_required_breakout_refs == ("dimension.event_date",)
    assert delta.added_allowed_breakout_refs == ()
    assert delta.child_contract.dimension_refs == ("dimension.event_date",)
    assert delta.child_contract.scope_identity == parent.scope_identity


def test_typed_child_material_delta_rejects_ungoverned_semantic_ref():
    parent = _base()

    with pytest.raises(AdaptiveTestDesignError, match="governed"):
        typed_child_material_delta_for_next_test(
            parent=parent,
            request=_request(),
            governed_semantic_refs=(
                "metric.effect",
                "metric.h1",
                "metric.h2",
            ),
        )


def test_same_scope_can_have_distinct_material_fingerprints_without_scope_mutation():
    parent = _base()
    delta = typed_child_material_delta_for_next_test(
        parent=parent,
        request=_request(),
        governed_semantic_refs=_governed_refs(),
    )

    assert parent.scope_fingerprint == delta.child_contract.scope_fingerprint
    assert parent.scope_identity == delta.child_contract.scope_identity
    assert parent.material_fingerprint != delta.child_contract.material_fingerprint

def test_typed_child_material_delta_rejects_scope_lineage_drift():
    parent = _base()
    request = _request().model_copy(
        update={"scope_lineage_id": "atl_other"}
    )

    with pytest.raises(AdaptiveTestDesignError, match="scope"):
        typed_child_material_delta_for_next_test(
            parent=parent,
            request=request,
            governed_semantic_refs=_governed_refs(),
        )


def test_typed_child_material_delta_rejects_scope_version_drift():
    parent = _base()
    request = _request().model_copy(
        update={"scope_version_id": "scope_v2"}
    )

    with pytest.raises(AdaptiveTestDesignError, match="scope"):
        typed_child_material_delta_for_next_test(
            parent=parent,
            request=request,
            governed_semantic_refs=_governed_refs(),
        )



@pytest.mark.parametrize(
    "surface",
    (
        NextTestEvidenceSurface.GOVERNED_EVIDENCE,
        NextTestEvidenceSurface.COUNTER_EVIDENCE,
        NextTestEvidenceSurface.MECHANISM_DISCRIMINATION,
    ),
)
def test_unprojectable_next_test_surface_is_governed_inconclusive_not_exception(
    surface: NextTestEvidenceSurface,
) -> None:
    parent = _base()
    request = _request().model_copy(
        update={
            "required_evidence_surface": surface,
            "ambiguity_code": "SYMBOLIC_UNRESOLVED_DISCRIMINATION",
        }
    )

    decision = evaluate_next_test_material_delta(
        parent=parent,
        request=request,
        governed_semantic_refs=_governed_refs(),
    )

    assert decision.disposition == NextTestMaterialDisposition.INCONCLUSIVE
    assert decision.delta is None
    assert decision.reason_code == "NO_LEGAL_MATERIAL_DELTA"


def test_temporal_order_surface_remains_executable_when_real_delta_exists() -> None:
    parent = _base()

    decision = evaluate_next_test_material_delta(
        parent=parent,
        request=_request(),
        governed_semantic_refs=_governed_refs(),
    )

    assert decision.disposition == NextTestMaterialDisposition.EXECUTABLE
    assert decision.delta is not None
    assert decision.delta.parent_material_fingerprint == parent.material_fingerprint
    assert decision.delta.child_material_fingerprint != parent.material_fingerprint


def test_scope_identity_drift_remains_fail_closed_not_inconclusive() -> None:
    parent = _base()
    request = _request().model_copy(
        update={"scope_version_id": "scope_v2"}
    )

    with pytest.raises(AdaptiveTestDesignError, match="scope"):
        evaluate_next_test_material_delta(
            parent=parent,
            request=request,
            governed_semantic_refs=_governed_refs(),
        )
