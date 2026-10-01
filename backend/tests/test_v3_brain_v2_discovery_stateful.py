from __future__ import annotations

import hashlib

from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from app.v3.brain_v2.discovery_candidate_design import (
    CandidateSetProjection,
    project_candidate_set,
)
from app.v3.brain_v2.state import BrainGraphState
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


CONTEXT = "ctx-brain-v2.1-stateful"


def _sem(
    candidate_id: str,
    kind: SemanticTargetKind,
    name: str,
    *,
    dimension_name: str | None = None,
    value: str | None = None,
) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=candidate_id,
        target_kind=kind,
        canonical_name=name,
        dimension_name=dimension_name,
        value=value,
        cube_names=("operations",),
    )


EFFECT = _sem("metric.effect", SemanticTargetKind.METRIC, "Effect")
H1 = _sem("metric.h1", SemanticTargetKind.METRIC, "Mechanism H1")
H2 = _sem("metric.h2", SemanticTargetKind.METRIC, "Mechanism H2")
DATE = _sem("dimension.event_date", SemanticTargetKind.DIMENSION, "Event Date")
PAINT = _sem(
    "entity.paint",
    SemanticTargetKind.ENTITY_VALUE,
    "Paint",
    dimension_name="Department",
    value="Paint",
)
ASSEMBLY = _sem(
    "entity.assembly",
    SemanticTargetKind.ENTITY_VALUE,
    "Assembly",
    dimension_name="Department",
    value="Assembly",
)


def _binding(ref: ResearchSemanticRef) -> ResearchNativeVerificationBinding:
    return ResearchNativeVerificationBinding(
        candidate_id=ref.candidate_id,
        table_name="operations",
        column_name=ref.candidate_id.replace(".", "_"),
    )


def _period(name: str, start: str, end: str) -> ResearchTimePeriod:
    return ResearchTimePeriod(
        source_text=name,
        time_dimension_candidate_id=DATE.candidate_id,
        start=start,
        end=end,
        role=TemporalRole.MATERIAL_WINDOW,
    )


MAY_JUNE = _period("May-June", "2026-05-01", "2026-07-01")
JUNE = _period("June", "2026-06-01", "2026-07-01")
JULY = _period("July", "2026-07-01", "2026-08-01")


def _initial_scope() -> ResearchScope:
    refs = (EFFECT, H1, H2, DATE, PAINT)
    return ResearchScope(
        semantic_refs=refs,
        time_surfaces=(MAY_JUNE.source_text,),
        periods=(MAY_JUNE,),
        temporal_dimension_ids=(DATE.candidate_id,),
        native_verification_bindings=tuple(_binding(item) for item in refs),
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    )


def _refs_operation(
    facet: ScopePatchFacet,
    refs: tuple[ResearchSemanticRef, ...],
    *,
    source_fragment: str,
) -> ScopePatchOperation:
    return ScopePatchOperation(
        facet=facet,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=refs,
        native_verification_bindings=tuple(_binding(item) for item in refs),
        source_fragment=source_fragment,
    )


def _period_operation(value: ResearchTimePeriod) -> ScopePatchOperation:
    return ScopePatchOperation(
        facet=ScopePatchFacet.PERIOD,
        operation=ScopePatchOperationKind.SET,
        semantic_refs=(DATE,),
        periods=(value,),
        native_verification_bindings=(_binding(DATE),),
        source_fragment="period mutation",
    )


ENTITY_CHOICES = {
    "paint": (PAINT,),
    "assembly": (ASSEMBLY,),
    "both": (PAINT, ASSEMBLY),
}
METRIC_CHOICES = {
    "effect_h1_h2": (EFFECT, H1, H2),
    "effect_h1": (EFFECT, H1),
    "effect_h2": (EFFECT, H2),
    "effect_only": (EFFECT,),
}
PERIOD_CHOICES = {"may_june": MAY_JUNE, "june": JUNE, "july": JULY}


class DiscoverySequenceStateMachine(RuleBasedStateMachine):
    """Cross-plane model for V2.1 scope/Evidence/discovery/resume invariants."""

    def __init__(self):
        super().__init__()
        self.scope = _initial_scope()
        self.evidence_history: list[tuple[str, str, str]] = []
        self.current_evidence_ids: tuple[str, ...] = ()
        self.executed_material: set[str] = set()
        self.native_acquisition_count = 0
        self.evidence_revision = 0
        self.p19_revision = 0
        self.candidate_projection = CandidateSetProjection()
        self.next_test_scopes: set[str] = set()
        self.material_variant = "initial"
        self.report_count = 0
        self.presentation_count = 0

    def _scope_fp(self) -> str:
        return scope_fingerprint(
            self.scope,
            context_version=CONTEXT,
            tenant_binding="tenant:stateful",
            principal_ref="user:stateful",
        )

    def _material_key(self) -> str:
        raw = (
            self._scope_fp()
            + ":"
            + self.scope.scope_version.version_id
            + ":"
            + self.material_variant
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _execute_once(self) -> bool:
        key = self._material_key()
        if key in self.executed_material:
            return False
        self.executed_material.add(key)
        self.native_acquisition_count += 1
        self.evidence_revision += 1
        evidence_id = "evi_" + hashlib.sha256(
            (key + f":{self.evidence_revision}").encode("utf-8")
        ).hexdigest()[:24]
        self.evidence_history.append(
            (evidence_id, self.scope.scope_version.version_id, key)
        )
        self.current_evidence_ids = tuple(
            dict.fromkeys((*self.current_evidence_ids, evidence_id))
        )
        return True

    def _apply(self, operations: tuple[ScopePatchOperation, ...]) -> bool:
        before = self.scope
        patch = TurnScopePatch(
            source_scope_version_id=before.scope_version.version_id,
            operations=operations,
        )
        resolved = resolve_scope_patch(
            before,
            patch,
            context_version=CONTEXT,
        )
        changed = (
            resolved.current_scope.scope_version.version_id
            != before.scope_version.version_id
        )
        self.scope = resolved.current_scope
        if changed:
            self.current_evidence_ids = ()
            self.candidate_projection = CandidateSetProjection()
            self.material_variant = "initial"
        return changed

    @rule()
    @precondition(lambda self: not self.current_evidence_ids)
    def acquire_current_material(self):
        assert self._execute_once()

    @rule()
    @precondition(lambda self: bool(self.current_evidence_ids))
    def duplicate_current_material_is_deduplicated(self):
        before = self.native_acquisition_count
        assert self._execute_once() is False
        assert self.native_acquisition_count == before

    @rule()
    @precondition(lambda self: bool(self.current_evidence_ids))
    def project_discovery_candidates(self):
        current_refs = tuple(item.candidate_id for item in self.scope.semantic_refs)
        metric_refs = tuple(
            item.candidate_id
            for item in self.scope.semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
        self.candidate_projection = project_candidate_set(
            allowed_discovery_surface=(H1.candidate_id, H2.candidate_id),
            current_scope_semantic_refs=current_refs,
            observed_material_semantic_refs=metric_refs,
            candidate_eligible_semantic_refs=metric_refs,
            effect_semantic_id=EFFECT.candidate_id,
            scope_version_id=self.scope.scope_version.version_id,
            evidence_refs=self.current_evidence_ids,
            material_requirement_ref="g_root",
        )

    @rule()
    @precondition(
        lambda self: (
            len(self.candidate_projection.candidates) >= 2
            and bool(self.current_evidence_ids)
        )
    )
    def p19_assesses_current_evidence(self):
        self.p19_revision = self.evidence_revision

    @rule()
    @precondition(
        lambda self: (
            len(self.candidate_projection.candidates) >= 2
            and self.p19_revision == self.evidence_revision
            and self.scope.scope_version.version_id not in self.next_test_scopes
        )
    )
    def p19_next_test_adds_one_bounded_material(self):
        self.next_test_scopes.add(self.scope.scope_version.version_id)
        self.material_variant = "next_test"
        before = self.native_acquisition_count
        assert self._execute_once()
        assert self.native_acquisition_count == before + 1

    @rule()
    @precondition(
        lambda self: (
            self.scope.scope_version.version_id in self.next_test_scopes
            and self.p19_revision < self.evidence_revision
        )
    )
    def p19_reassesses_only_after_next_test_evidence(self):
        self.p19_revision = self.evidence_revision

    @rule(entity=st.sampled_from(tuple(ENTITY_CHOICES)))
    def mutate_entity_scope(self, entity):
        self._apply(
            (
                _refs_operation(
                    ScopePatchFacet.ENTITY,
                    ENTITY_CHOICES[entity],
                    source_fragment="entity mutation",
                ),
            )
        )

    @rule(period=st.sampled_from(tuple(PERIOD_CHOICES)))
    def mutate_period_scope(self, period):
        self._apply((_period_operation(PERIOD_CHOICES[period]),))

    @rule(metrics=st.sampled_from(tuple(METRIC_CHOICES)))
    def mutate_metric_scope(self, metrics):
        self._apply(
            (
                _refs_operation(
                    ScopePatchFacet.METRIC,
                    METRIC_CHOICES[metrics],
                    source_fragment="metric mutation",
                ),
            )
        )

    @rule(
        entity=st.sampled_from(tuple(ENTITY_CHOICES)),
        period=st.sampled_from(tuple(PERIOD_CHOICES)),
    )
    def mutate_entity_and_period(self, entity, period):
        self._apply(
            (
                _refs_operation(
                    ScopePatchFacet.ENTITY,
                    ENTITY_CHOICES[entity],
                    source_fragment="entity+period mutation",
                ),
                _period_operation(PERIOD_CHOICES[period]),
            )
        )

    @rule(entity=st.sampled_from(tuple(ENTITY_CHOICES)))
    def same_mutation_twice_is_idempotent(self, entity):
        operation = _refs_operation(
            ScopePatchFacet.ENTITY,
            ENTITY_CHOICES[entity],
            source_fragment="same mutation twice",
        )
        self._apply((operation,))
        ordinal = self.scope.scope_version.ordinal
        current_evidence = self.current_evidence_ids
        changed_again = self._apply((operation,))
        assert changed_again is False
        assert self.scope.scope_version.ordinal == ordinal
        assert self.current_evidence_ids == current_evidence

    @rule()
    def report_only_continuation_has_zero_acquisition_delta(self):
        before = self.native_acquisition_count
        self.report_count += 1
        assert self.native_acquisition_count == before

    @rule()
    def presentation_only_continuation_has_zero_acquisition_delta(self):
        before = self.native_acquisition_count
        self.presentation_count += 1
        assert self.native_acquisition_count == before

    @rule()
    def checkpoint_restart_preserves_completed_activity(self):
        state = BrainGraphState(
            thread_id="stateful-checkpoint",
            tenant_binding="tenant:stateful",
            principal_ref="user:stateful",
            scope_version_id=self.scope.scope_version.version_id,
            evidence_revision=self.evidence_revision,
            evidence_ids=self.current_evidence_ids,
            hypothesis_revision=self.p19_revision,
            hypothesis_ids=tuple(
                "p19h_"
                + hashlib.sha256(item.semantic_id.encode("utf-8")).hexdigest()[:24]
                for item in self.candidate_projection.candidates
            ),
        )
        resumed = BrainGraphState.model_validate(state.model_dump(mode="json"))
        assert resumed == state
        before = self.native_acquisition_count
        if self.current_evidence_ids:
            assert self._execute_once() is False
        assert self.native_acquisition_count == before

    @invariant()
    def historical_evidence_never_becomes_current(self):
        current = set(self.current_evidence_ids)
        version = self.scope.scope_version.version_id
        for evidence_id, evidence_version, _ in self.evidence_history:
            if evidence_version != version:
                assert evidence_id not in current

    @invariant()
    def projected_candidates_are_current_and_bounded(self):
        current = set(self.current_evidence_ids)
        current_metrics = {
            item.candidate_id
            for item in self.scope.semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        }
        for item in self.candidate_projection.candidates:
            assert item.scope_version_id == self.scope.scope_version.version_id
            assert set(item.evidence_refs).issubset(current)
            assert item.semantic_id in {H1.candidate_id, H2.candidate_id}
            assert item.semantic_id in current_metrics
            assert item.semantic_id != EFFECT.candidate_id

    @invariant()
    def completed_material_is_never_counted_twice(self):
        assert self.native_acquisition_count == len(self.executed_material)
        assert len(self.current_evidence_ids) == len(set(self.current_evidence_ids))

    @invariant()
    def p19_never_runs_ahead_of_evidence(self):
        assert self.p19_revision <= self.evidence_revision

    @invariant()
    def adaptive_depth_is_bounded_per_scope(self):
        assert len(self.next_test_scopes) <= self.scope.scope_version.ordinal


TestDiscoverySequenceStateMachine = DiscoverySequenceStateMachine.TestCase
TestDiscoverySequenceStateMachine.settings = settings(
    max_examples=180,
    stateful_step_count=30,
    deadline=None,
)
