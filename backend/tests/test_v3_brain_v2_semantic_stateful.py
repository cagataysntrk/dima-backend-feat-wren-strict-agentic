from __future__ import annotations

from types import SimpleNamespace

from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from app.v3.report_document import P20ReportError, ReportClaimGate
from app.v3.research import ObligationState, StoppingStatus
from app.v3.research_contracts import (
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
)
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
)

from tests.semantic_spec.model import ReferencePatch, ReferenceScope, apply_reference_patch


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


def _read_production(scope: ResearchScope) -> ReferenceScope:
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


def _operation(
    *,
    facet: ScopePatchFacet,
    value: str | None,
) -> ScopePatchOperation:
    if value is None:
        return ScopePatchOperation(
            facet=facet,
            operation=ScopePatchOperationKind.CLEAR,
            source_fragment=f"symbolic {facet.value.lower()} clear",
        )
    factory = {
        ScopePatchFacet.ENTITY: _entity,
        ScopePatchFacet.METRIC: _metric,
        ScopePatchFacet.BREAKDOWN: _breakdown,
    }[facet]
    return ScopePatchOperation(
        facet=facet,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=(factory(value),),
        source_fragment=f"symbolic {facet.value.lower()} set",
    )


class ScopeSemanticConformanceMachine(RuleBasedStateMachine):
    """Long action sequences against an independent partial-update law."""

    def __init__(self) -> None:
        super().__init__()
        self.reference = ReferenceScope(
            entities=frozenset({"entity.e1"}),
            metrics=frozenset({"metric.m1"}),
            breakdowns=frozenset({"dimension.d1"}),
            version=1,
        )
        self.production = _production_scope(self.reference)

    def _apply(
        self,
        *,
        reference_patch: ReferencePatch,
        operation: ScopePatchOperation,
    ) -> None:
        expected = apply_reference_patch(self.reference, reference_patch)
        resolved = resolve_scope_patch(
            self.production,
            TurnScopePatch(
                source_scope_version_id=self.production.scope_version.version_id,
                operations=(operation,),
            ),
            context_version="ctx-semantic-stateful-v1",
        )
        self.reference = expected
        self.production = resolved.current_scope

    @rule(value=st.sampled_from(("entity.e1", "entity.e2")))
    def replace_entity(self, value: str) -> None:
        self._apply(
            reference_patch=ReferencePatch(entities=frozenset({value})),
            operation=_operation(facet=ScopePatchFacet.ENTITY, value=value),
        )

    @rule()
    def clear_entity(self) -> None:
        self._apply(
            reference_patch=ReferencePatch(entities=frozenset()),
            operation=_operation(facet=ScopePatchFacet.ENTITY, value=None),
        )

    @rule(value=st.sampled_from(("metric.m1", "metric.m2", "metric.m3")))
    def replace_metric(self, value: str) -> None:
        self._apply(
            reference_patch=ReferencePatch(metrics=frozenset({value})),
            operation=_operation(facet=ScopePatchFacet.METRIC, value=value),
        )

    @rule(value=st.sampled_from(("dimension.d1", "dimension.d2")))
    def replace_breakdown(self, value: str) -> None:
        self._apply(
            reference_patch=ReferencePatch(breakdowns=frozenset({value})),
            operation=_operation(facet=ScopePatchFacet.BREAKDOWN, value=value),
        )

    @rule()
    def clear_breakdown(self) -> None:
        self._apply(
            reference_patch=ReferencePatch(breakdowns=frozenset()),
            operation=_operation(facet=ScopePatchFacet.BREAKDOWN, value=None),
        )

    @invariant()
    def production_matches_reference_after_every_transition(self) -> None:
        assert _read_production(self.production) == self.reference


class CompletionSemanticConformanceMachine(RuleBasedStateMachine):
    """Completion law remains owner-derived under arbitrary lifecycle churn."""

    def __init__(self) -> None:
        super().__init__()
        self.owner_state = ObligationState.READY
        self.process_status = StoppingStatus.ACTIVE
        self.downstream_terminal = False

    @rule(state=st.sampled_from(tuple(ObligationState)))
    def mutate_owner_state(self, state: ObligationState) -> None:
        self.owner_state = state

    @rule(status=st.sampled_from(tuple(StoppingStatus)))
    def mutate_process_status(self, status: StoppingStatus) -> None:
        self.process_status = status

    @rule(value=st.booleans())
    def mutate_downstream_terminality(self, value: bool) -> None:
        self.downstream_terminal = value

    @invariant()
    def p20_callability_matches_terminal_owner_law(self) -> None:
        session = SimpleNamespace(
            obligations=(
                SimpleNamespace(
                    obligation_id="goal.g1",
                    state=self.owner_state,
                ),
            ),
            stopping=SimpleNamespace(status=self.process_status),
        )
        expected = (
            self.owner_state in {ObligationState.VERIFIED, ObligationState.LIMITED}
            or self.downstream_terminal
        )
        error = None
        try:
            ReportClaimGate._assert_sealed(
                session,
                ("goal.g1",),
                downstream_terminal_ids=(
                    {"goal.g1"} if self.downstream_terminal else set()
                ),
            )
        except P20ReportError as exc:
            error = exc

        if expected:
            assert error is None
        else:
            assert error is not None
            assert error.code == "P20_RESEARCH_SESSION_NOT_SEALED"


TestScopeSemanticConformance = ScopeSemanticConformanceMachine.TestCase
TestScopeSemanticConformance.settings = settings(
    max_examples=200,
    stateful_step_count=30,
    deadline=None,
)

TestCompletionSemanticConformance = CompletionSemanticConformanceMachine.TestCase
TestCompletionSemanticConformance.settings = settings(
    max_examples=200,
    stateful_step_count=20,
    deadline=None,
)
