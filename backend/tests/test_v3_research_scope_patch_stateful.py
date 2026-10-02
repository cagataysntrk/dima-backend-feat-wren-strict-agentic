from __future__ import annotations

from copy import deepcopy

from hypothesis import settings, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
)

from app.v3.research_contracts import (
    ResearchNativeVerificationBinding,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeVersion,
    SemanticTargetKind,
    TemporalRole,
)
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
    scope_fingerprint,
)


def sem(cid: str, kind: SemanticTargetKind, name: str, *, dimension=None, value=None):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=name,
        dimension_name=dimension,
        value=value,
        cube_names=("operations",),
    )


DOWNTIME = sem("metric.downtime", SemanticTargetKind.METRIC, "Downtime")
FAULTS = sem("metric.faults", SemanticTargetKind.METRIC, "Faults")
PERFORMANCE = sem("metric.performance", SemanticTargetKind.METRIC, "Performance")
MACHINE = sem("dimension.machine", SemanticTargetKind.DIMENSION, "Machine")
SHIFT = sem("dimension.shift", SemanticTargetKind.DIMENSION, "Shift")
EVENT_DATE = sem("dimension.event_date", SemanticTargetKind.DIMENSION, "Event Date")
ASSEMBLY = sem(
    "entity.assembly",
    SemanticTargetKind.ENTITY_VALUE,
    "Assembly",
    dimension="Department",
    value="Assembly",
)
PAINT = sem(
    "entity.paint",
    SemanticTargetKind.ENTITY_VALUE,
    "Paint",
    dimension="Department",
    value="Paint",
)
PACKAGING = sem(
    "entity.packaging",
    SemanticTargetKind.ENTITY_VALUE,
    "Packaging",
    dimension="Department",
    value="Packaging",
)


def binding(ref: ResearchSemanticRef):
    return ResearchNativeVerificationBinding(
        candidate_id=ref.candidate_id,
        table_name="machine_operations",
        column_name=ref.candidate_id.replace(".", "_"),
    )


def period(name: str, start: str, end: str) -> ResearchTimePeriod:
    return ResearchTimePeriod(
        source_text=name,
        time_dimension_candidate_id=EVENT_DATE.candidate_id,
        start=start,
        end=end,
        role=TemporalRole.MATERIAL_WINDOW,
    )


P_MAY_JUNE = period("May-June 2026", "2026-05-01", "2026-07-01")
P_JUNE = period("June 2026", "2026-06-01", "2026-07-01")
P_JULY = period("July 2026", "2026-07-01", "2026-08-01")


ALL_REFS = {
    item.candidate_id: item
    for item in (
        DOWNTIME,
        FAULTS,
        PERFORMANCE,
        MACHINE,
        SHIFT,
        EVENT_DATE,
        ASSEMBLY,
        PAINT,
        PACKAGING,
    )
}


def initial_scope() -> ResearchScope:
    refs = (DOWNTIME, MACHINE, EVENT_DATE, ASSEMBLY, PAINT)
    return ResearchScope(
        semantic_refs=refs,
        time_surfaces=(P_MAY_JUNE.source_text,),
        periods=(P_MAY_JUNE,),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(binding(item) for item in refs),
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    )


def ref_model_from(scope: ResearchScope) -> dict:
    temporal = set(scope.temporal_dimension_ids)
    return {
        "entities": {
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        },
        "metrics": {
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        },
        "breakdowns": {
            item.candidate_id
            for item in scope.semantic_refs
            if (
                item.target_kind == SemanticTargetKind.DIMENSION
                and item.candidate_id not in temporal
            )
        },
        "periods": {
            (
                item.time_dimension_candidate_id,
                item.start,
                item.end,
                item.role.value,
            )
            for item in scope.periods
        },
        "version": scope.scope_version.ordinal,
    }


def facet_ids(scope: ResearchScope, facet: ScopePatchFacet):
    temporal = set(scope.temporal_dimension_ids)
    if facet == ScopePatchFacet.ENTITY:
        return {
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        }
    if facet == ScopePatchFacet.METRIC:
        return {
            item.candidate_id
            for item in scope.semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        }
    if facet == ScopePatchFacet.BREAKDOWN:
        return {
            item.candidate_id
            for item in scope.semantic_refs
            if (
                item.target_kind == SemanticTargetKind.DIMENSION
                and item.candidate_id not in temporal
            )
        }
    return {
        (
            item.time_dimension_candidate_id,
            item.start,
            item.end,
            item.role.value,
        )
        for item in scope.periods
    }


def op_refs(
    facet: ScopePatchFacet,
    operation: ScopePatchOperationKind,
    refs: tuple[ResearchSemanticRef, ...],
    *,
    source_fragment: str,
) -> ScopePatchOperation:
    return ScopePatchOperation(
        facet=facet,
        operation=operation,
        semantic_refs=refs,
        native_verification_bindings=tuple(binding(item) for item in refs),
        source_fragment=source_fragment,
    )


def op_period(
    operation: ScopePatchOperationKind,
    periods: tuple[ResearchTimePeriod, ...],
    *,
    source_fragment: str,
) -> ScopePatchOperation:
    refs = () if operation == ScopePatchOperationKind.CLEAR else (EVENT_DATE,)
    return ScopePatchOperation(
        facet=ScopePatchFacet.PERIOD,
        operation=operation,
        semantic_refs=refs,
        periods=periods,
        native_verification_bindings=tuple(binding(item) for item in refs),
        source_fragment=source_fragment,
    )


ENTITY_SETS = {
    "assembly": (ASSEMBLY,),
    "paint": (PAINT,),
    "assembly_paint": (ASSEMBLY, PAINT),
    "assembly_packaging": (ASSEMBLY, PACKAGING),
    "all_three": (ASSEMBLY, PAINT, PACKAGING),
}
METRIC_SETS = {
    "downtime": (DOWNTIME,),
    "faults": (FAULTS,),
    "performance": (PERFORMANCE,),
    "downtime_faults": (DOWNTIME, FAULTS),
}
BREAKDOWN_SETS = {
    "machine": (MACHINE,),
    "shift": (SHIFT,),
    "machine_shift": (MACHINE, SHIFT),
}
PERIOD_SETS = {
    "may_june": (P_MAY_JUNE,),
    "june": (P_JUNE,),
    "july": (P_JULY,),
}


class ScopePatchStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.scope = initial_scope()
        self.model = ref_model_from(self.scope)
        self.last_scope = self.scope
        self.last_changed: set[ScopePatchFacet] = set()
        self.last_material_change = False

    def _apply_reference(self, operations: tuple[ScopePatchOperation, ...]):
        model = deepcopy(self.model)
        for item in operations:
            if item.facet == ScopePatchFacet.PERIOD:
                key = "periods"
                values = {
                    (
                        period.time_dimension_candidate_id,
                        period.start,
                        period.end,
                        period.role.value,
                    )
                    for period in item.periods
                }
            else:
                key = {
                    ScopePatchFacet.ENTITY: "entities",
                    ScopePatchFacet.METRIC: "metrics",
                    ScopePatchFacet.BREAKDOWN: "breakdowns",
                }[item.facet]
                values = {ref.candidate_id for ref in item.semantic_refs}

            if item.operation == ScopePatchOperationKind.SET:
                model[key] = set(values)
            elif item.operation == ScopePatchOperationKind.ADD:
                model[key] |= set(values)
            elif item.operation == ScopePatchOperationKind.REMOVE:
                model[key] -= set(values)
            elif item.operation == ScopePatchOperationKind.CLEAR:
                model[key] = set()
            else:
                raise AssertionError(item.operation)

        changed = {
            facet
            for facet, key in (
                (ScopePatchFacet.ENTITY, "entities"),
                (ScopePatchFacet.PERIOD, "periods"),
                (ScopePatchFacet.METRIC, "metrics"),
                (ScopePatchFacet.BREAKDOWN, "breakdowns"),
            )
            if model[key] != self.model[key]
        }
        if changed:
            model["version"] += 1
        return model, changed

    def _run(self, operations: tuple[ScopePatchOperation, ...]):
        before = self.scope
        patch = TurnScopePatch(
            source_scope_version_id=before.scope_version.version_id,
            operations=operations,
        )
        expected, changed = self._apply_reference(operations)

        # Replay against the same source is deterministic/idempotent.
        left = resolve_scope_patch(
            before,
            patch,
            context_version="ctx-stateful-v1",
        )
        right = resolve_scope_patch(
            before,
            patch,
            context_version="ctx-stateful-v1",
        )
        assert left == right
        assert left.scope_fingerprint == right.scope_fingerprint

        self.last_scope = before
        self.scope = left.current_scope
        self.last_changed = changed
        self.last_material_change = bool(changed)
        self.model = expected

    @rule(entity_key=st.sampled_from(tuple(ENTITY_SETS)))
    def set_entity(self, entity_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.ENTITY,
                    ScopePatchOperationKind.SET,
                    ENTITY_SETS[entity_key],
                    source_fragment="entity set",
                ),
            )
        )

    @rule(entity_key=st.sampled_from(tuple(ENTITY_SETS)))
    def add_entity(self, entity_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.ENTITY,
                    ScopePatchOperationKind.ADD,
                    ENTITY_SETS[entity_key],
                    source_fragment="entity add",
                ),
            )
        )

    @rule(entity_key=st.sampled_from(tuple(ENTITY_SETS)))
    def remove_entity(self, entity_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.ENTITY,
                    ScopePatchOperationKind.REMOVE,
                    ENTITY_SETS[entity_key],
                    source_fragment="entity remove",
                ),
            )
        )

    @rule()
    def clear_entity(self):
        self._run(
            (
                ScopePatchOperation(
                    facet=ScopePatchFacet.ENTITY,
                    operation=ScopePatchOperationKind.CLEAR,
                    source_fragment="clear entity",
                ),
            )
        )

    @rule(metric_key=st.sampled_from(tuple(METRIC_SETS)))
    def change_metric(self, metric_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.METRIC,
                    ScopePatchOperationKind.SET,
                    METRIC_SETS[metric_key],
                    source_fragment="metric set",
                ),
            )
        )

    @rule(breakdown_key=st.sampled_from(tuple(BREAKDOWN_SETS)))
    def change_breakdown(self, breakdown_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.BREAKDOWN,
                    ScopePatchOperationKind.SET,
                    BREAKDOWN_SETS[breakdown_key],
                    source_fragment="breakdown set",
                ),
            )
        )

    @rule(period_key=st.sampled_from(tuple(PERIOD_SETS)))
    def change_period(self, period_key):
        self._run(
            (
                op_period(
                    ScopePatchOperationKind.SET,
                    PERIOD_SETS[period_key],
                    source_fragment="period set",
                ),
            )
        )

    @rule()
    def clear_period(self):
        self._run(
            (
                ScopePatchOperation(
                    facet=ScopePatchFacet.PERIOD,
                    operation=ScopePatchOperationKind.CLEAR,
                    source_fragment="clear period",
                ),
            )
        )

    @rule(
        entity_key=st.sampled_from(tuple(ENTITY_SETS)),
        period_key=st.sampled_from(tuple(PERIOD_SETS)),
    )
    def combined_entity_period(self, entity_key, period_key):
        self._run(
            (
                op_refs(
                    ScopePatchFacet.ENTITY,
                    ScopePatchOperationKind.SET,
                    ENTITY_SETS[entity_key],
                    source_fragment="entity part",
                ),
                op_period(
                    ScopePatchOperationKind.SET,
                    PERIOD_SETS[period_key],
                    source_fragment="period part",
                ),
            )
        )

    @rule()
    def noop_presentation_turn(self):
        self._run(())

    @rule()
    def report_only_turn(self):
        self._run(())

    @rule()
    def resume_after_checkpoint(self):
        # Round-trip through the durable typed representation. No mutation.
        self.scope = ResearchScope.model_validate(
            self.scope.model_dump(mode="json")
        )
        self.model = deepcopy(self.model)
        self.last_scope = self.scope
        self.last_changed = set()
        self.last_material_change = False

    @invariant()
    def production_matches_independent_reference(self):
        actual = ref_model_from(self.scope)
        assert actual == self.model

    @invariant()
    def scope_version_advances_only_on_material_mutation(self):
        if self.last_material_change:
            assert (
                self.scope.scope_version.ordinal
                == self.last_scope.scope_version.ordinal + 1
            )
        else:
            assert (
                self.scope.scope_version.ordinal
                == self.last_scope.scope_version.ordinal
            )

    @invariant()
    def untouched_facets_are_inherited_exactly(self):
        for facet in ScopePatchFacet:
            if facet not in self.last_changed:
                assert facet_ids(self.scope, facet) == facet_ids(
                    self.last_scope,
                    facet,
                )

    @invariant()
    def current_scope_fingerprint_is_deterministic(self):
        left = scope_fingerprint(
            self.scope,
            context_version="ctx-stateful-v1",
        )
        right = scope_fingerprint(
            ResearchScope.model_validate(
                self.scope.model_dump(mode="json")
            ),
            context_version="ctx-stateful-v1",
        )
        assert left == right

    @invariant()
    def tenant_and_principal_binding_change_security_fingerprint(self):
        a = scope_fingerprint(
            self.scope,
            context_version="ctx-stateful-v1",
            tenant_binding="tenant:a",
            principal_ref="user:a",
        )
        b = scope_fingerprint(
            self.scope,
            context_version="ctx-stateful-v1",
            tenant_binding="tenant:b",
            principal_ref="user:a",
        )
        c = scope_fingerprint(
            self.scope,
            context_version="ctx-stateful-v1",
            tenant_binding="tenant:a",
            principal_ref="user:b",
        )
        assert len({a, b, c}) == 3


TestScopePatchStateMachine = ScopePatchStateMachine.TestCase
TestScopePatchStateMachine.settings = settings(
    max_examples=1000,
    stateful_step_count=30,
    deadline=None,
)
