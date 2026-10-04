from __future__ import annotations

from types import SimpleNamespace

import pytest
from hypothesis import given, settings, strategies as st

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalFilterInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    RankingBasis as ProductRankingBasis,
)
from app.v3.brain_v2.adaptive_test_design import (
    AdaptiveTestDesignError,
    NextTestMaterialDisposition,
    evaluate_next_test_material_delta,
)
from app.v3.hypothesis_root_cause_v1 import (
    ExpectedDiscriminatoryValue,
    NextTestEvidenceSurface,
    NextTestRequest,
)
from app.v3.report_document import P20ReportError, ReportClaimGate
from app.v3.research import ObligationState, StoppingStatus
from app.v3.research_contracts import (
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
)
from app.v3.research_result_dependency import (
    ResultDependencyProjectionError,
    resolve_first_ranked_entity,
)
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
)
from tests.semantic_spec.model import (
    ReferencePatch,
    ReferenceScope,
    ResultDependencyDisposition,
    apply_reference_patch,
)
from tests.semantic_spec.saturation import (
    AdaptiveDecisionKind,
    BreakoutKind,
    ComparisonType,
    EntityCardinality,
    MetricCardinality,
    PeriodRole,
    PresentationRequirement,
    RankingDirection,
    ResultDependencyKind,
    SaturationCase,
    ScopeMutationKind,
    TopK,
    classify_saturation_case,
    expected_pair_value_counts,
    saturation_dimension_values,
    saturation_pair_coverage,
    saturation_pairwise_matrix,
)
from tests.semantic_spec.strategies import saturation_cases


def _metrics(case: SaturationCase) -> tuple[str, ...]:
    count = {
        MetricCardinality.ONE: 1,
        MetricCardinality.TWO: 2,
        MetricCardinality.THREE: 3,
    }[case.metric_cardinality]
    return tuple(f"metric.m{i}" for i in range(1, count + 1))


def _dimensions(case: SaturationCase) -> tuple[str, ...]:
    return {
        BreakoutKind.NONE: (),
        BreakoutKind.ENTITY: ("dimension.entity",),
        BreakoutKind.TEMPORAL: ("dimension.time",),
        BreakoutKind.MULTI: ("dimension.time", "dimension.entity"),
    }[case.breakout]


def _filters(case: SaturationCase) -> tuple[AnalyticalFilterInvariant, ...]:
    count = {
        EntityCardinality.NONE: 0,
        EntityCardinality.ONE: 1,
        EntityCardinality.MULTIPLE: 2,
    }[case.entity_cardinality]
    return tuple(
        AnalyticalFilterInvariant(
            semantic_ref=f"entity-filter:{i}",
            source_candidate_id="dimension.entity",
            dimension_name="dimension.entity",
            value=f"entity.e{i}",
        )
        for i in range(1, count + 1)
    )


def _presentation(case: SaturationCase) -> tuple[str, ...]:
    return {
        PresentationRequirement.NONE: (),
        PresentationRequirement.ANSWER: ("answer",),
        PresentationRequirement.TABLE: ("table",),
        PresentationRequirement.REPORT: ("report",),
    }[case.presentation_requirement]


def _periods(
    case: SaturationCase,
) -> tuple[AnalyticalPeriodInvariant | None, AnalyticalComparisonInvariant | None]:
    if case.comparison_type == ComparisonType.PERIOD:
        return (
            None,
            AnalyticalComparisonInvariant(
                mode="wave-b-period",
                reference_period=AnalyticalPeriodInvariant(
                    kind="explicit_half_open",
                    time_dimension="dimension.time",
                    start="2026-01-01",
                    end="2026-02-01",
                ),
                base_period=AnalyticalPeriodInvariant(
                    kind="explicit_half_open",
                    time_dimension="dimension.time",
                    start="2026-02-01",
                    end="2026-03-01",
                ),
            ),
        )
    if case.period_role != PeriodRole.NONE:
        return (
            AnalyticalPeriodInvariant(
                kind=f"wave-b-{case.period_role.value.lower()}",
                time_dimension="dimension.time",
                start="2026-01-01",
                end="2026-03-01",
            ),
            None,
        )
    return None, None


def _ranking_is_material(case: SaturationCase) -> bool:
    return (
        case.intent.value == "RANKING"
        or case.ranking_direction != RankingDirection.NONE
        or case.top_k != TopK.NONE
    )


def _product_contract_accepts(case: SaturationCase) -> bool:
    period, comparison = _periods(case)
    metrics = _metrics(case)
    ranking = None
    if _ranking_is_material(case):
        direction = (
            "asc" if case.ranking_direction == RankingDirection.ASC else "desc"
        )
        limit = {
            TopK.NONE: None,
            TopK.ONE: 1,
            TopK.FIVE: 5,
        }[case.top_k]
        ranking = AnalyticalRankingInvariant(
            measure=metrics[0],
            direction=direction,
            limit=limit,
            basis=ProductRankingBasis(case.ranking_basis.value.lower()),
        )
    try:
        AnalyticalRequestContract(
            authority_id="auth-wave-b",
            request_ref=f"req-wave-b-{case.intent.value.lower()}",
            semantic_context_version="ctx-wave-b-v1",
            scope_identity=AnalyticalScopeIdentity(
                lineage_id="atl-wave-b",
                version_id="scope_v1",
            ),
            scope_fingerprint="b" * 64,
            metric_refs=metrics,
            dimension_refs=_dimensions(case),
            filters=_filters(case),
            period=period,
            comparison=comparison,
            ranking=ranking,
            requested_output_surfaces=_presentation(case),
        )
    except ValueError:
        return False
    return True


def _metric(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _entity(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.ENTITY_VALUE,
        canonical_name=candidate_id,
        dimension_name="dimension.entity",
        value=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _breakdown(candidate_id: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=candidate_id,
        cube_names=("symbolic_cube",),
    )


def _production_scope(scope: ReferenceScope) -> ResearchScope:
    refs = (
        *(_metric(item) for item in sorted(scope.metrics)),
        *(_breakdown(item) for item in sorted(scope.breakdowns)),
        *(_entity(item) for item in sorted(scope.entities)),
    )
    return ResearchScope(
        semantic_refs=tuple(refs),
        scope_version=ScopeVersion(
            version_id=f"scope_v{scope.version}",
            ordinal=scope.version,
            parent_version_id=(
                None if scope.version == 1 else f"scope_v{scope.version - 1}"
            ),
        ),
    )


def _reference_scope(scope: ResearchScope) -> ReferenceScope:
    return ReferenceScope(
        entities=frozenset(
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        ),
        metrics=frozenset(
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        ),
        breakdowns=frozenset(
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        ),
        periods=frozenset(),
        version=scope.scope_version.ordinal,
    )


def _scope_probe(case: SaturationCase) -> None:
    reference = ReferenceScope(
        entities=frozenset({"entity.e1"}),
        metrics=frozenset({"metric.m1"}),
        breakdowns=frozenset({"dimension.d1"}),
        version=1,
    )
    production = _production_scope(reference)

    if case.scope_mutation == ScopeMutationKind.NONE:
        expected = reference
        operations: tuple[ScopePatchOperation, ...] = ()
    elif case.scope_mutation == ScopeMutationKind.LOCAL_SET:
        expected = apply_reference_patch(
            reference,
            ReferencePatch(metrics=frozenset({"metric.m2"})),
        )
        operations = (
            ScopePatchOperation(
                facet=ScopePatchFacet.METRIC,
                operation=ScopePatchOperationKind.SET,
                semantic_refs=(_metric("metric.m2"),),
                source_fragment="wave-b metric set",
            ),
        )
    elif case.scope_mutation == ScopeMutationKind.LOCAL_CLEAR:
        expected = apply_reference_patch(
            reference,
            ReferencePatch(breakdowns=frozenset()),
        )
        operations = (
            ScopePatchOperation(
                facet=ScopePatchFacet.BREAKDOWN,
                operation=ScopePatchOperationKind.CLEAR,
                source_fragment="wave-b breakdown clear",
            ),
        )
    else:
        expected = apply_reference_patch(
            reference,
            ReferencePatch(
                entities=frozenset({"entity.e2"}),
                metrics=frozenset({"metric.m3"}),
            ),
        )
        operations = (
            ScopePatchOperation(
                facet=ScopePatchFacet.ENTITY,
                operation=ScopePatchOperationKind.SET,
                semantic_refs=(_entity("entity.e2"),),
                source_fragment="wave-b entity set",
            ),
            ScopePatchOperation(
                facet=ScopePatchFacet.METRIC,
                operation=ScopePatchOperationKind.SET,
                semantic_refs=(_metric("metric.m3"),),
                source_fragment="wave-b metric set",
            ),
        )

    resolved = resolve_scope_patch(
        production,
        TurnScopePatch(
            source_scope_version_id=production.scope_version.version_id,
            operations=operations,
        ),
        context_version="ctx-wave-b-v1",
    )
    assert _reference_scope(resolved.current_scope) == expected


def _adaptive_parent() -> AnalyticalRequestContract:
    return AnalyticalRequestContract(
        authority_id="auth-wave-b-adaptive",
        request_ref="req-wave-b-adaptive",
        semantic_context_version="ctx-wave-b-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-wave-b-adaptive",
            version_id="scope_v1",
        ),
        scope_fingerprint="c" * 64,
        metric_refs=("metric.effect", "metric.h1", "metric.h2"),
        period=AnalyticalPeriodInvariant(
            kind="explicit_half_open_window",
            time_dimension="dimension.event_date",
            start="2026-05-01T00:00:00Z",
            end="2026-07-01T00:00:00Z",
        ),
        requested_output_surfaces=("report",),
    )


def _adaptive_probe(case: SaturationCase, expected: bool) -> None:
    if case.adaptive_decision != AdaptiveDecisionKind.NEXT_TEST:
        assert expected is False
        return

    parent = _adaptive_parent()
    version_id = (
        parent.scope_identity.version_id
        if case.scope_mutation == ScopeMutationKind.NONE
        else "scope_v2"
    )
    request = NextTestRequest(
        request_id="ntr_" + "8" * 24,
        ambiguity_code="TEMPORAL_DISCRIMINATION_REQUIRED",
        hypothesis_ids=("p19h_" + "6" * 24, "p19h_" + "7" * 24),
        required_evidence_surface=NextTestEvidenceSurface.TEMPORAL_ORDER,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id=parent.scope_identity.lineage_id,
        scope_version_id=version_id,
    )
    actual = False
    try:
        decision = evaluate_next_test_material_delta(
            parent=parent,
            request=request,
            governed_semantic_refs=(
                "metric.effect",
                "metric.h1",
                "metric.h2",
                "dimension.event_date",
            ),
        )
    except AdaptiveTestDesignError:
        actual = False
    else:
        actual = decision.disposition == NextTestMaterialDisposition.EXECUTABLE
    assert actual is expected


def _completion_probe(case: SaturationCase, expected: bool) -> None:
    if case.presentation_requirement == PresentationRequirement.NONE:
        assert expected is False
        return
    state = (
        ObligationState.READY
        if case.adaptive_decision == AdaptiveDecisionKind.NEXT_TEST
        else ObligationState.VERIFIED
    )
    session = SimpleNamespace(
        obligations=(SimpleNamespace(obligation_id="goal.g1", state=state),),
        stopping=SimpleNamespace(status=StoppingStatus.ACTIVE),
    )
    error = None
    try:
        ReportClaimGate._assert_sealed(session, ("goal.g1",))
    except P20ReportError as exc:
        error = exc
    assert (error is None) is expected


def test_wave_b_pairwise_matrix_remains_complete_and_has_no_new_family() -> None:
    cases = saturation_pairwise_matrix()
    coverage = saturation_pair_coverage(cases)
    expected = expected_pair_value_counts()
    assert len(saturation_dimension_values()) == 13
    assert len(coverage) == 78
    assert set(coverage) == set(expected)
    assert all(len(coverage[key]) == count for key, count in expected.items())
    assert all(not classify_saturation_case(case).new_family for case in cases)


@settings(max_examples=1800, deadline=None, database=None)
@given(case=saturation_cases())
def test_wave_b_generated_combinations_match_multiple_product_owners(
    case: SaturationCase,
) -> None:
    outcome = classify_saturation_case(case)
    assert not outcome.new_family

    expected_contract = (
        True if not _ranking_is_material(case) else outcome.ranking_coherent
    )
    assert _product_contract_accepts(case) is expected_contract

    _scope_probe(case)
    _adaptive_probe(case, outcome.adaptive_legal)
    _completion_probe(case, outcome.presentation_callable)


@settings(max_examples=500, deadline=None, database=None)
@given(
    selected=st.sampled_from(("entity.e1", "entity.e2", "entity.e3")),
    existing=st.sampled_from(("none", "same", "conflict")),
    dependency_role=st.sampled_from(("filter_only", "filter_and_breakout")),
    parent_state=st.sampled_from(("valid", "empty")),
)
def test_wave_b_result_dependency_is_execution_local_and_fail_closed(
    selected: str,
    existing: str,
    dependency_role: str,
    parent_state: str,
) -> None:
    filters: tuple[AnalyticalFilterInvariant, ...] = ()
    if existing != "none":
        value = selected if existing == "same" else "entity.other"
        filters = (
            AnalyticalFilterInvariant(
                semantic_ref="accepted-filter",
                source_candidate_id="dimension.entity",
                dimension_name="dimension.entity",
                value=value,
            ),
        )
    dimensions = (
        ()
        if dependency_role == "filter_only"
        else ("dimension.entity",)
    )
    base = AnalyticalRequestContract(
        authority_id="auth-wave-b-dependency",
        request_ref="req-wave-b-dependency",
        semantic_context_version="ctx-wave-b-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-wave-b-dependency",
            version_id="scope_v1",
        ),
        scope_fingerprint="d" * 64,
        metric_refs=("metric.m1",),
        dimension_refs=dimensions,
        filters=filters,
    )
    rows = (
        [[selected, 42.0], ["entity.tail", 1.0]]
        if parent_state == "valid"
        else []
    )
    parent_result = {
        "data": {
            "cols": [
                {"id": 501, "name": "entity"},
                {"id": 777, "name": "metric"},
            ],
            "rows": rows,
        }
    }

    if parent_state == "empty":
        with pytest.raises(ResultDependencyProjectionError) as exc:
            resolve_first_ranked_entity(
                base_contract=base,
                source_goal_id="goal.parent",
                source_evidence_id="ev-parent",
                source_receipt_id="rcpt-parent",
                source_result_hash="e" * 64,
                dimension_semantic_id="dimension.entity",
                native_field_id=501,
                parent_result=parent_result,
                dimension_name="dimension.entity",
            )
        assert exc.value.code == "R1_RESULT_DEPENDENCY_PARENT_EMPTY"
        return

    if existing == "conflict":
        with pytest.raises(ResultDependencyProjectionError) as exc:
            resolve_first_ranked_entity(
                base_contract=base,
                source_goal_id="goal.parent",
                source_evidence_id="ev-parent",
                source_receipt_id="rcpt-parent",
                source_result_hash="e" * 64,
                dimension_semantic_id="dimension.entity",
                native_field_id=501,
                parent_result=parent_result,
                dimension_name="dimension.entity",
            )
        assert exc.value.code == "R1_RESULT_DEPENDENCY_SCOPE_CONFLICT"
        return

    resolution = resolve_first_ranked_entity(
        base_contract=base,
        source_goal_id="goal.parent",
        source_evidence_id="ev-parent",
        source_receipt_id="rcpt-parent",
        source_result_hash="e" * 64,
        dimension_semantic_id="dimension.entity",
        native_field_id=501,
        parent_result=parent_result,
        dimension_name="dimension.entity",
    )
    assert resolution.selected_value == selected
    assert resolution.contract.scope_identity == base.scope_identity
    assert resolution.contract.scope_fingerprint == base.scope_fingerprint
    assert resolution.contract.metric_refs == base.metric_refs
    assert resolution.contract.dimension_refs == dimensions
    selected_filters = tuple(
        item
        for item in resolution.contract.filters
        if item.source_candidate_id == "dimension.entity"
        and item.value == selected
    )
    assert len(selected_filters) == 1


def test_wave_b_result_dependency_ambiguous_native_column_fails_closed() -> None:
    base = AnalyticalRequestContract(
        authority_id="auth-wave-b-dependency-ambiguous",
        request_ref="req-wave-b-dependency-ambiguous",
        semantic_context_version="ctx-wave-b-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-wave-b-dependency",
            version_id="scope_v1",
        ),
        scope_fingerprint="f" * 64,
        metric_refs=("metric.m1",),
        dimension_refs=("dimension.entity",),
    )
    with pytest.raises(ResultDependencyProjectionError) as exc:
        resolve_first_ranked_entity(
            base_contract=base,
            source_goal_id="goal.parent",
            source_evidence_id="ev-parent",
            source_receipt_id="rcpt-parent",
            source_result_hash="a" * 64,
            dimension_semantic_id="dimension.entity",
            native_field_id=501,
            parent_result={
                "data": {
                    "cols": [
                        {"id": 501, "name": "entity-a"},
                        {"field_ref": ["field", 501], "name": "entity-b"},
                    ],
                    "rows": [["entity.e1", "entity.e1"]],
                }
            },
            dimension_name="dimension.entity",
        )
    assert exc.value.code == "R1_RESULT_DEPENDENCY_DIMENSION_COLUMN_AMBIGUOUS"
