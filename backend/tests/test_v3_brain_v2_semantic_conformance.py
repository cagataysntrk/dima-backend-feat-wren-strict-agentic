from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest
from hypothesis import given, settings, strategies as st

from app.v3.analytical_request_contract import (
    AnalyticalRankingInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research_analytical_scope import (
    NativeMaterialBinding,
    ResearchAnalyticalScopeError,
    _assert_material_ranking_scope,
)
from app.v3.research_contracts import (
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
    NativeMaterialObservation,
    NativeMaterialRanking,
    NativeMaterialRankingTarget,
)

from tests.semantic_spec.model import (
    EntityCardinality,
    GoalKind,
    MaterialShape,
    PeriodStructure,
    PresentationKind,
    RankingKind,
    ReferencePatch,
    ReferenceScope,
    apply_reference_patch,
    pair_coverage,
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
