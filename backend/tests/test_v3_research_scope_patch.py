from __future__ import annotations

from app.v3.research_contracts import (
    ResearchNativeVerificationBinding,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutationKind,
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

MAY_JUNE = ResearchTimePeriod(
    source_text="May through June 2026",
    time_dimension_candidate_id=EVENT_DATE.candidate_id,
    start="2026-05-01",
    end="2026-07-01",
    role=TemporalRole.MATERIAL_WINDOW,
)
JUNE = ResearchTimePeriod(
    source_text="June 2026",
    time_dimension_candidate_id=EVENT_DATE.candidate_id,
    start="2026-06-01",
    end="2026-07-01",
    role=TemporalRole.MATERIAL_WINDOW,
)


def binding(ref: ResearchSemanticRef):
    return ResearchNativeVerificationBinding(
        candidate_id=ref.candidate_id,
        table_name="machine_operations",
        column_name=ref.candidate_id.replace(".", "_"),
    )


def base_scope() -> ResearchScope:
    refs = (DOWNTIME, MACHINE, EVENT_DATE, ASSEMBLY, PAINT)
    return ResearchScope(
        semantic_refs=refs,
        time_surfaces=(MAY_JUNE.source_text,),
        periods=(MAY_JUNE,),
        temporal_dimension_ids=(EVENT_DATE.candidate_id,),
        native_verification_bindings=tuple(binding(item) for item in refs),
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    )


def patch(*operations: ScopePatchOperation) -> TurnScopePatch:
    return TurnScopePatch(
        source_scope_version_id="scope_v1",
        operations=operations,
    )


def entity_set(*refs: ResearchSemanticRef) -> ScopePatchOperation:
    return ScopePatchOperation(
        facet=ScopePatchFacet.ENTITY,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=tuple(refs),
        native_verification_bindings=tuple(binding(item) for item in refs),
        source_fragment="only Assembly",
    )


def period_set(*periods: ResearchTimePeriod) -> ScopePatchOperation:
    return ScopePatchOperation(
        facet=ScopePatchFacet.PERIOD,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=(EVENT_DATE,),
        periods=tuple(periods),
        native_verification_bindings=(binding(EVENT_DATE),),
        source_fragment="June only",
    )


def ids(scope: ResearchScope, kind: SemanticTargetKind) -> set[str]:
    return {
        item.candidate_id
        for item in scope.semantic_refs
        if item.target_kind == kind
    }


def test_entity_patch_inherits_every_absent_facet_bit_identically():
    prior = base_scope()
    result = resolve_scope_patch(
        prior,
        patch(entity_set(ASSEMBLY)),
        context_version="ctx-scope-v1",
    )

    assert result.materially_changed is True
    assert result.current_scope.scope_version.version_id == "scope_v2"
    assert result.derived_mutation_kind == ScopeMutationKind.NARROW_ENTITY
    assert result.current_scope.periods == prior.periods
    assert result.current_scope.time_surfaces == prior.time_surfaces
    assert result.current_scope.temporal_dimension_ids == prior.temporal_dimension_ids
    assert ids(result.current_scope, SemanticTargetKind.METRIC) == {"metric.downtime"}
    assert ids(result.current_scope, SemanticTargetKind.DIMENSION) == {
        "dimension.machine",
        "dimension.event_date",
    }
    assert ids(result.current_scope, SemanticTargetKind.ENTITY_VALUE) == {
        "entity.assembly"
    }


def test_period_patch_inherits_entity_metric_and_breakdown():
    prior = base_scope()
    result = resolve_scope_patch(
        prior,
        patch(period_set(JUNE)),
        context_version="ctx-scope-v1",
    )

    assert result.derived_mutation_kind == ScopeMutationKind.CHANGE_PERIOD
    assert result.current_scope.periods == (JUNE,)
    assert ids(result.current_scope, SemanticTargetKind.ENTITY_VALUE) == {
        "entity.assembly",
        "entity.paint",
    }
    assert ids(result.current_scope, SemanticTargetKind.METRIC) == {"metric.downtime"}
    assert MACHINE in result.current_scope.semantic_refs


def test_explicit_clear_entity_filter_is_not_absence():
    prior = base_scope()
    clear = ScopePatchOperation(
        facet=ScopePatchFacet.ENTITY,
        operation=ScopePatchOperationKind.CLEAR,
        source_fragment="remove the department filter",
    )
    result = resolve_scope_patch(
        prior,
        patch(clear),
        context_version="ctx-scope-v1",
    )

    assert result.derived_mutation_kind == ScopeMutationKind.EXPAND_ENTITY
    assert ids(result.current_scope, SemanticTargetKind.ENTITY_VALUE) == set()
    assert result.current_scope.periods == prior.periods


def test_absent_operations_are_noop_and_do_not_mint_fake_scope_version():
    prior = base_scope()
    result = resolve_scope_patch(
        prior,
        patch(),
        context_version="ctx-scope-v1",
    )

    assert result.materially_changed is False
    assert result.current_scope is prior
    assert result.current_scope.scope_version.version_id == "scope_v1"
    assert result.scope_contract is None


def test_combined_entity_and_period_change_is_one_resolved_scope_transition():
    prior = base_scope()
    result = resolve_scope_patch(
        prior,
        patch(entity_set(ASSEMBLY), period_set(JUNE)),
        context_version="ctx-scope-v1",
    )

    assert result.materially_changed is True
    assert result.current_scope.scope_version.version_id == "scope_v2"
    assert result.current_scope.periods == (JUNE,)
    assert ids(result.current_scope, SemanticTargetKind.ENTITY_VALUE) == {
        "entity.assembly"
    }
    assert result.derived_mutation_kind == ScopeMutationKind.REPLACE


def test_scope_fingerprint_ignores_tuple_order_and_source_wording():
    prior = base_scope()
    left = resolve_scope_patch(
        prior,
        patch(entity_set(ASSEMBLY)),
        context_version="ctx-scope-v1",
    )

    reordered = prior.model_copy(
        update={
            "semantic_refs": tuple(reversed(prior.semantic_refs)),
            "native_verification_bindings": tuple(
                reversed(prior.native_verification_bindings)
            ),
        }
    )
    alternate = entity_set(
        ASSEMBLY.model_copy(update={"source_mention": "assembly department"})
    )
    right = resolve_scope_patch(
        reordered,
        TurnScopePatch(
            source_scope_version_id="scope_v1",
            operations=(
                alternate.model_copy(
                    update={"source_fragment": "restrict to Assembly"}
                ),
            ),
        ),
        context_version="ctx-scope-v1",
    )

    assert left.scope_fingerprint == right.scope_fingerprint


def test_same_patch_same_source_version_is_deterministic_and_idempotent():
    prior = base_scope()
    value = patch(entity_set(ASSEMBLY))
    left = resolve_scope_patch(
        prior,
        value,
        context_version="ctx-scope-v1",
    )
    right = resolve_scope_patch(
        prior,
        value,
        context_version="ctx-scope-v1",
    )

    assert left == right
    assert left.scope_fingerprint == right.scope_fingerprint
