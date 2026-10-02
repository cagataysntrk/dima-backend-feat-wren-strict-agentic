from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest
from hypothesis import given, settings, strategies as st

from app.v3.analytical_request_contract import (
    AnalyticalComparisonInvariant,
    AnalyticalFilterInvariant,
    AnalyticalPeriodInvariant,
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research_intake import DraftRanking, ModelGoalDraft
from app.v3.research_analytical_scope import (
    NativeMaterialBinding,
    ResearchAnalyticalScopeError,
    _assert_material_filter_scope,
    _assert_material_ranking_scope,
)
from app.v3.research_contracts import (
    RankingBasis as ProductRankingBasis,
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
)
from app.v3.report_document import P20ReportError, ReportClaimGate
from app.v3.research import ObligationState, StoppingStatus
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
)
from app.v3.substrate.metabase.native_models import (
    NativeMaterialFilter,
    NativeMaterialObservation,
    NativeMaterialRanking,
    NativeMaterialRankingTarget,
)

from tests.semantic_spec.model import (
    EntityCardinality,
    EntityFilterAdmissionSpec,
    GoalKind,
    MaterialShape,
    PeriodStructure,
    PresentationKind,
    RankingBasis,
    RankingKind,
    ResultDependencyDisposition,
    ReferencePatch,
    ReferenceScope,
    apply_reference_patch,
    entity_filter_admission_allowed,
    pair_coverage,
    ranking_basis_is_coherent,
    result_dependency_disposition,
    semantic_matrix,
)


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
    entities = frozenset(
        item.candidate_id
        for item in scope.semantic_refs
        if item.target_kind == SemanticTargetKind.ENTITY_VALUE
    )
    metrics = frozenset(
        item.candidate_id
        for item in scope.semantic_refs
        if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
    )
    breakdowns = frozenset(
        item.candidate_id
        for item in scope.semantic_refs
        if item.target_kind == SemanticTargetKind.DIMENSION
    )
    return ReferenceScope(
        entities=entities,
        metrics=metrics,
        breakdowns=breakdowns,
        periods=frozenset(),
        version=scope.scope_version.ordinal,
    )


def _production_patch(
    source: ReferenceScope,
    patch: ReferencePatch,
) -> TurnScopePatch:
    operations: list[ScopePatchOperation] = []
    specs = (
        (ScopePatchFacet.ENTITY, patch.entities, _entity),
        (ScopePatchFacet.METRIC, patch.metrics, _metric),
        (ScopePatchFacet.BREAKDOWN, patch.breakdowns, _breakdown),
    )
    for facet, values, factory in specs:
        if values is None:
            continue
        if not values:
            operations.append(
                ScopePatchOperation(
                    facet=facet,
                    operation=ScopePatchOperationKind.CLEAR,
                    source_fragment=f"symbolic {facet.value.lower()} clear",
                )
            )
            continue
        operations.append(
            ScopePatchOperation(
                facet=facet,
                operation=ScopePatchOperationKind.SET,
                semantic_refs=tuple(factory(item) for item in sorted(values)),
                source_fragment=f"symbolic {facet.value.lower()} replacement",
            )
        )
    return TurnScopePatch(
        source_scope_version_id=f"scope_v{source.version}",
        operations=tuple(operations),
    )


def test_change_ranking_has_explicit_typed_basis_and_comparison_authority() -> None:
    assert ranking_basis_is_coherent(
        basis=RankingBasis.CHANGE,
        period=PeriodStructure.BASELINE_CANDIDATE,
    )
    assert not ranking_basis_is_coherent(
        basis=RankingBasis.CHANGE,
        period=PeriodStructure.SINGLE_WINDOW,
    )

    ranking = DraftRanking(
        direction="desc",
        limit=1,
        measure_semantic_id="metric.m1",
        source_text="symbolic ranked change",
        basis="change",
    )
    assert ranking.model_dump(mode="json")["basis"] == "change"


@pytest.mark.parametrize(
    ("basis", "period"),
    tuple(
        (basis, period)
        for basis in RankingBasis
        for period in (
            PeriodStructure.NONE,
            PeriodStructure.SINGLE_WINDOW,
            PeriodStructure.BASELINE_CANDIDATE,
        )
    ),
)
def test_product_ranking_basis_matches_independent_period_law(
    basis: RankingBasis,
    period: PeriodStructure,
) -> None:
    coherent = ranking_basis_is_coherent(basis=basis, period=period)
    comparison = None
    single = None
    if period == PeriodStructure.BASELINE_CANDIDATE:
        comparison = AnalyticalComparisonInvariant(
            mode="symbolic",
            reference_period=AnalyticalPeriodInvariant(
                kind="symbolic",
                time_dimension="dimension.t1",
                start="2026-01-01",
                end="2026-02-01",
            ),
            base_period=AnalyticalPeriodInvariant(
                kind="symbolic",
                time_dimension="dimension.t1",
                start="2026-02-01",
                end="2026-03-01",
            ),
        )
    elif period == PeriodStructure.SINGLE_WINDOW:
        single = AnalyticalPeriodInvariant(
            kind="symbolic",
            time_dimension="dimension.t1",
            start="2026-01-01",
            end="2026-03-01",
        )

    payload = dict(
        authority_id="auth-ranking-basis",
        request_ref="req-ranking-basis",
        semantic_context_version="ctx-ranking-basis",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-ranking-basis",
            version_id="scope_v1",
        ),
        scope_fingerprint="1" * 64,
        metric_refs=("metric.m1",),
        period=single,
        comparison=comparison,
        ranking=AnalyticalRankingInvariant(
            measure="metric.m1",
            direction="desc",
            limit=1,
            basis=ProductRankingBasis(basis.value.lower()),
        ),
    )
    if coherent:
        contract = AnalyticalRequestContract(**payload)
        assert contract.ranking is not None
        assert contract.ranking.basis.value == basis.value.lower()
    else:
        with pytest.raises(ValueError, match="baseline/comparison"):
            AnalyticalRequestContract(**payload)


@given(
    direction=st.sampled_from(("asc", "desc")),
    limit=st.one_of(st.none(), st.integers(min_value=1, max_value=50)),
)
@settings(max_examples=80, deadline=None)
def test_change_ranking_symbolic_siblings_preserve_basis(
    direction: str,
    limit: int | None,
) -> None:
    ranking = DraftRanking(
        direction=direction,
        limit=limit,
        measure_semantic_id="metric.m2",
        source_text="symbolic governed change ranking",
        basis="change",
    )
    assert ranking.basis.value == "change"
    assert ranking.measure_semantic_id == "metric.m2"


@pytest.mark.parametrize(
    ("parent_verified", "value_count", "scope_unchanged", "expected"),
    (
        (False, 0, True, ResultDependencyDisposition.WAITING),
        (True, 1, True, ResultDependencyDisposition.READY),
        (True, 0, True, ResultDependencyDisposition.LIMITED),
        (True, 2, True, ResultDependencyDisposition.LIMITED),
        (True, 1, False, ResultDependencyDisposition.INVALID),
    ),
)
def test_result_dependency_independent_law(
    parent_verified: bool,
    value_count: int,
    scope_unchanged: bool,
    expected: ResultDependencyDisposition,
) -> None:
    assert result_dependency_disposition(
        parent_verified=parent_verified,
        selected_value_count=value_count,
        scope_version_unchanged=scope_unchanged,
    ) == expected


def test_goal_can_declare_typed_parent_result_selection_dependency() -> None:
    goal = ModelGoalDraft(
        goal_key="g-child",
        kind="breakdown",
        source_text="Inspect one governed child slice.",
        source_fragment_text="Inspect one governed child slice.",
        subject_semantic_ids=("metric.m2",),
        related_semantic_ids=("dimension.d1",),
        result_dependency={
            "source_goal_key": "g-parent",
            "dimension_semantic_id": "dimension.d1",
            "selection": "first_ranked_entity",
        },
    )
    assert goal.result_dependency is not None
    assert goal.result_dependency.source_goal_key == "g-parent"
    assert goal.result_dependency.dimension_semantic_id == "dimension.d1"


def test_finite_semantic_matrix_has_complete_pair_coverage() -> None:
    cases = semantic_matrix()
    coverage = pair_coverage(cases)

    cardinalities = {
        "goal": len(GoalKind),
        "period": len(PeriodStructure),
        "entity": len(EntityCardinality),
        "material": len(MaterialShape),
        "ranking": len(RankingKind),
        "presentation": len(PresentationKind),
    }
    assert len(cases) == 5040
    assert len(coverage) == 15
    for key, values in coverage.items():
        left, right = key.split("×")
        assert len(values) == cardinalities[left] * cardinalities[right]


_SCOPE_VALUES = st.builds(
    ReferenceScope,
    entities=st.frozensets(
        st.sampled_from(("entity.e1", "entity.e2")), max_size=2
    ),
    metrics=st.frozensets(
        st.sampled_from(("metric.m1", "metric.m2", "metric.m3")),
        min_size=1,
        max_size=3,
    ),
    breakdowns=st.frozensets(
        st.sampled_from(("dimension.d1", "dimension.d2")), max_size=2
    ),
    periods=st.just(frozenset()),
    version=st.integers(min_value=1, max_value=20),
)


@st.composite
def _scope_patches(draw):
    def optional(values, *, allow_empty=True):
        base = st.frozensets(
            st.sampled_from(values),
            min_size=0 if allow_empty else 1,
            max_size=len(values),
        )
        return draw(st.one_of(st.none(), base))

    return ReferencePatch(
        entities=optional(("entity.e1", "entity.e2")),
        metrics=optional(
            ("metric.m1", "metric.m2", "metric.m3"),
            allow_empty=False,
        ),
        breakdowns=optional(("dimension.d1", "dimension.d2")),
        periods=None,
    )


@given(scope=_SCOPE_VALUES, patch=_scope_patches())
@settings(max_examples=400, deadline=None)
def test_production_scope_patch_matches_independent_locality_law(
    scope: ReferenceScope,
    patch: ReferencePatch,
) -> None:
    expected = apply_reference_patch(scope, patch)
    resolved = resolve_scope_patch(
        _production_scope(scope),
        _production_patch(scope, patch),
        context_version="ctx-semantic-spec-v1",
    )
    actual = _reference_scope(resolved.current_scope)
    assert actual == expected


def test_same_facet_explicit_operations_compose_to_one_local_delta() -> None:
    scope = ReferenceScope(
        entities=frozenset({"entity.e1"}),
        metrics=frozenset({"metric.m1", "metric.m2"}),
        breakdowns=frozenset({"dimension.d1"}),
        version=1,
    )
    production = _production_scope(scope)
    operations = (
        ScopePatchOperation(
            facet=ScopePatchFacet.METRIC,
            operation=ScopePatchOperationKind.SET,
            semantic_refs=(_metric("metric.m1"),),
            source_fragment="symbolic metric replacement",
        ),
        ScopePatchOperation(
            facet=ScopePatchFacet.METRIC,
            operation=ScopePatchOperationKind.REMOVE,
            semantic_refs=(_metric("metric.m2"),),
            source_fragment="symbolic metric removal",
        ),
    )
    expected = apply_reference_patch(
        scope,
        ReferencePatch(metrics=frozenset({"metric.m1"})),
    )

    resolved = resolve_scope_patch(
        production,
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=operations,
        ),
        context_version="ctx-semantic-spec-v1",
    )

    assert _reference_scope(resolved.current_scope) == expected
    assert resolved.changed_facets == (ScopePatchFacet.METRIC,)


def test_same_facet_nonconflicting_composition_is_order_independent() -> None:
    scope = ReferenceScope(
        entities=frozenset(),
        metrics=frozenset({"metric.m1", "metric.m2"}),
        breakdowns=frozenset(),
        version=1,
    )
    production = _production_scope(scope)
    add = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.ADD,
        semantic_refs=(_metric("metric.m3"),),
        source_fragment="symbolic add",
    )
    remove = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.REMOVE,
        semantic_refs=(_metric("metric.m2"),),
        source_fragment="symbolic remove",
    )

    left = resolve_scope_patch(
        production,
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=(add, remove),
        ),
        context_version="ctx-semantic-spec-v1",
    )
    right = resolve_scope_patch(
        production,
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=(remove, add),
        ),
        context_version="ctx-semantic-spec-v1",
    )

    assert _reference_scope(left.current_scope) == _reference_scope(
        right.current_scope
    )
    assert left.scope_fingerprint == right.scope_fingerprint


def test_same_facet_add_remove_overlap_remains_fail_closed() -> None:
    add = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.ADD,
        semantic_refs=(_metric("metric.m2"),),
        source_fragment="symbolic add",
    )
    remove = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.REMOVE,
        semantic_refs=(_metric("metric.m2"),),
        source_fragment="symbolic remove",
    )

    with pytest.raises(ValueError, match="both adds and removes"):
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=(add, remove),
        )


def test_same_facet_multiple_replacements_remain_fail_closed() -> None:
    first = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=(_metric("metric.m1"),),
        source_fragment="symbolic replacement one",
    )
    second = ScopePatchOperation(
        facet=ScopePatchFacet.METRIC,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=(_metric("metric.m2"),),
        source_fragment="symbolic replacement two",
    )

    with pytest.raises(ValueError, match="multiple replacement authorities"):
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=(first, second),
        )


def test_same_patch_replay_from_same_source_is_idempotent() -> None:
    scope = ReferenceScope(
        entities=frozenset({"entity.e1"}),
        metrics=frozenset({"metric.m1", "metric.m2"}),
        breakdowns=frozenset({"dimension.d1"}),
        version=1,
    )
    production = _production_scope(scope)
    patch = TurnScopePatch(
        source_scope_version_id="scope_v1",
        operations=(
            ScopePatchOperation(
                facet=ScopePatchFacet.METRIC,
                operation=ScopePatchOperationKind.SET,
                semantic_refs=(_metric("metric.m1"),),
                source_fragment="symbolic replacement",
            ),
            ScopePatchOperation(
                facet=ScopePatchFacet.METRIC,
                operation=ScopePatchOperationKind.REMOVE,
                semantic_refs=(_metric("metric.m2"),),
                source_fragment="symbolic removal",
            ),
        ),
    )

    first = resolve_scope_patch(
        production,
        patch,
        context_version="ctx-semantic-spec-v1",
    )
    second = resolve_scope_patch(
        production,
        patch,
        context_version="ctx-semantic-spec-v1",
    )

    assert first.current_scope == second.current_scope
    assert first.scope_fingerprint == second.scope_fingerprint


def _entity_filter_contract_and_bindings():
    required = frozenset({"entity.e1", "entity.e2"})
    contract = AnalyticalRequestContract(
        authority_id="auth-semantic-spec",
        request_ref="req-filter-set",
        semantic_context_version="ctx-semantic-spec-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-semantic-spec",
            version_id="scope_v2",
        ),
        metric_refs=("metric.m1",),
        filters=tuple(
            AnalyticalFilterInvariant(
                semantic_ref=candidate_id,
                source_candidate_id=candidate_id,
                dimension_name="dimension.entity",
                value=candidate_id,
            )
            for candidate_id in sorted(required)
        ),
    )
    bindings = {
        candidate_id: NativeMaterialBinding(
            candidate_id=candidate_id,
            candidate_kind="entity_value",
            database_id=1,
            table_id=10,
            field_id=20,
        )
        for candidate_id in required
    }
    return required, contract, bindings


@pytest.mark.parametrize("operator", ("=", "in"))
def test_multi_value_entity_filter_matches_exact_governed_value_set(
    operator: str,
) -> None:
    required, contract, bindings = _entity_filter_contract_and_bindings()
    observed = frozenset({"entity.e2", "entity.e1"})
    assert entity_filter_admission_allowed(
        EntityFilterAdmissionSpec(
            required_values=required,
            observed_values=observed,
        )
    )

    observation = SimpleNamespace(
        filters=(
            NativeMaterialFilter(
                stage_number=0,
                operator=operator,
                values=("entity.e2", "entity.e1"),
                field_id=20,
                table_id=10,
            ),
        )
    )

    _assert_material_filter_scope(contract, observation, bindings)


@pytest.mark.parametrize(
    "values",
    (
        ("entity.e1",),
        ("entity.e1", "entity.e2", "entity.e3"),
    ),
)
def test_entity_filter_value_set_must_remain_exact(values) -> None:
    required, contract, bindings = _entity_filter_contract_and_bindings()
    observed = frozenset(values)
    assert not entity_filter_admission_allowed(
        EntityFilterAdmissionSpec(
            required_values=required,
            observed_values=observed,
        )
    )

    observation = SimpleNamespace(
        filters=(
            NativeMaterialFilter(
                stage_number=0,
                operator="=",
                values=values,
                field_id=20,
                table_id=10,
            ),
        )
    )
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="membership values differ",
    ):
        _assert_material_filter_scope(contract, observation, bindings)


def test_entity_filter_foreign_field_remains_fail_closed() -> None:
    _, contract, bindings = _entity_filter_contract_and_bindings()
    observation = SimpleNamespace(
        filters=(
            NativeMaterialFilter(
                stage_number=0,
                operator="=",
                values=("entity.e1", "entity.e2"),
                field_id=21,
                table_id=10,
            ),
        )
    )
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="filter fields differ",
    ):
        _assert_material_filter_scope(contract, observation, bindings)


def test_entity_filter_non_membership_operator_remains_fail_closed() -> None:
    _, contract, bindings = _entity_filter_contract_and_bindings()
    observation = SimpleNamespace(
        filters=(
            NativeMaterialFilter(
                stage_number=0,
                operator="contains",
                values=("entity.e1", "entity.e2"),
                field_id=20,
                table_id=10,
            ),
        )
    )
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="not exact membership",
    ):
        _assert_material_filter_scope(contract, observation, bindings)


def test_multiple_atomic_filters_on_same_field_remain_ambiguous() -> None:
    _, contract, bindings = _entity_filter_contract_and_bindings()
    observation = SimpleNamespace(
        filters=(
            NativeMaterialFilter(
                stage_number=0,
                operator="=",
                values=("entity.e1",),
                field_id=20,
                table_id=10,
            ),
            NativeMaterialFilter(
                stage_number=0,
                operator="=",
                values=("entity.e2",),
                field_id=20,
                table_id=10,
            ),
        )
    )
    with pytest.raises(
        ResearchAnalyticalScopeError,
        match="boolean composition is not observable",
    ):
        _assert_material_filter_scope(contract, observation, bindings)


def _ranking_contract() -> AnalyticalRequestContract:
    return AnalyticalRequestContract(
        authority_id="auth-semantic-spec",
        request_ref="req-semantic-spec",
        semantic_context_version="ctx-semantic-spec-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl-semantic-spec",
            version_id="scope_v1",
        ),
        scope_fingerprint="a" * 64,
        metric_refs=("metric.m1",),
        ranking=AnalyticalRankingInvariant(
            measure="metric.m1",
            direction="desc",
            limit=3,
        ),
    )


def _ranking_observation_with_legal_nonrestrictive_order() -> NativeMaterialObservation:
    return NativeMaterialObservation(
        schema_version="dima_native_material_observation_v1",
        conversation_id=UUID("00000000-0000-4000-8000-000000000101"),
        native_query_id="native-semantic-spec-ranking",
        assistant_message_id=1,
        tool_call_id="tool-semantic-spec-ranking",
        query_fingerprint="b" * 64,
        authenticated_metabase_subject=7,
        database_id=1,
        runtime_identity={},
        ranking=(
            NativeMaterialRanking(
                stage_number=0,
                order_index=0,
                target=NativeMaterialRankingTarget(
                    kind="metric",
                    metabase_metric_id=101,
                    metabase_metric_entity_id="metric-entity-m1",
                ),
                direction="desc",
                limit=3,
            ),
            NativeMaterialRanking(
                stage_number=0,
                order_index=1,
                target=NativeMaterialRankingTarget(
                    kind="field",
                    field_id=999,
                    table_id=10,
                ),
                direction="asc",
                limit=None,
            ),
        ),
    )


def test_native_ranking_admission_allows_extra_nonrestrictive_stability_order() -> None:
    """Law 2: required ranking may coexist with a legal nonrestrictive superset.

    The second ORDER BY has no LIMIT and therefore cannot remove rows. It is
    presentation/stability material, not a second Dima ranking authority.
    """

    contract = _ranking_contract()
    observation = _ranking_observation_with_legal_nonrestrictive_order()
    bindings = {
        "metric.m1": NativeMaterialBinding(
            candidate_id="metric.m1",
            candidate_kind="metric",
            database_id=1,
            metric_id=101,
            metric_entity_id="metric-entity-m1",
        )
    }

    _assert_material_ranking_scope(contract, observation, bindings)


@given(
    extra_direction=st.sampled_from(("asc", "desc")),
    extra_field_id=st.integers(min_value=1, max_value=10000).filter(
        lambda value: value != 9999
    ),
)
@settings(max_examples=80, deadline=None)
def test_native_ranking_admission_generated_nonrestrictive_siblings_are_legal(
    extra_direction: str,
    extra_field_id: int,
) -> None:
    contract = _ranking_contract()
    base = _ranking_observation_with_legal_nonrestrictive_order()
    authorized = base.ranking[0]
    extra = NativeMaterialRanking(
        stage_number=0,
        order_index=1,
        target=NativeMaterialRankingTarget(
            kind="field",
            field_id=extra_field_id,
            table_id=10,
        ),
        direction=extra_direction,
        limit=None,
    )
    observation = base.model_copy(update={"ranking": (authorized, extra)})
    bindings = {
        "metric.m1": NativeMaterialBinding(
            candidate_id="metric.m1",
            candidate_kind="metric",
            database_id=1,
            metric_id=101,
            metric_entity_id="metric-entity-m1",
        )
    }

    _assert_material_ranking_scope(contract, observation, bindings)


@given(
    extra_limit=st.integers(min_value=1, max_value=50),
    extra_direction=st.sampled_from(("asc", "desc")),
)
@settings(max_examples=80, deadline=None)
def test_native_ranking_admission_generated_restrictive_siblings_fail_closed(
    extra_limit: int,
    extra_direction: str,
) -> None:
    contract = _ranking_contract()
    base = _ranking_observation_with_legal_nonrestrictive_order()
    authorized = base.ranking[0]
    unauthorized = NativeMaterialRanking(
        stage_number=0,
        order_index=1,
        target=NativeMaterialRankingTarget(
            kind="field",
            field_id=9999,
            table_id=10,
        ),
        direction=extra_direction,
        limit=extra_limit,
    )
    observation = base.model_copy(update={"ranking": (authorized, unauthorized)})
    bindings = {
        "metric.m1": NativeMaterialBinding(
            candidate_id="metric.m1",
            candidate_kind="metric",
            database_id=1,
            metric_id=101,
            metric_entity_id="metric-entity-m1",
        )
    }

    with pytest.raises(ResearchAnalyticalScopeError) as exc:
        _assert_material_ranking_scope(contract, observation, bindings)
    assert exc.value.code == "R1_NATIVE_RANKING_SCOPE_MISMATCH"


def _completion_session(
    *,
    state: ObligationState,
    stopping: StoppingStatus,
):
    return SimpleNamespace(
        obligations=(
            SimpleNamespace(
                obligation_id="goal.g1",
                state=state,
            ),
        ),
        stopping=SimpleNamespace(status=stopping),
    )


def test_p20_terminal_owner_artifact_is_not_blocked_by_stale_process_flag() -> None:
    """Law 4: owner terminality, not an incidental lifecycle flag, gates P20."""

    session = _completion_session(
        state=ObligationState.VERIFIED,
        stopping=StoppingStatus.ACTIVE,
    )

    ReportClaimGate._assert_sealed(session, ("goal.g1",))


def test_p20_genuinely_open_owner_remains_fail_closed() -> None:
    session = _completion_session(
        state=ObligationState.READY,
        stopping=StoppingStatus.ACTIVE,
    )

    with pytest.raises(P20ReportError) as exc:
        ReportClaimGate._assert_sealed(session, ("goal.g1",))
    assert exc.value.code == "P20_RESEARCH_SESSION_NOT_SEALED"


def test_p20_downstream_terminal_owner_can_close_shared_material_obligation() -> None:
    session = _completion_session(
        state=ObligationState.READY,
        stopping=StoppingStatus.ACTIVE,
    )

    ReportClaimGate._assert_sealed(
        session,
        ("goal.g1",),
        downstream_terminal_ids={"goal.g1"},
    )
