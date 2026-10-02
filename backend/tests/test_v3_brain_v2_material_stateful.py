from __future__ import annotations

import pytest
from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from app.v3.analytical_request_contract import (
    AnalyticalPeriodInvariant,
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
    material_coverage_contract,
)
from app.v3.brain_v2.adaptive_test_design import (
    AdaptiveTestDesignError,
    typed_child_material_delta_for_next_test,
)
from app.v3.hypothesis_root_cause_v1 import (
    ExpectedDiscriminatoryValue,
    NextTestEvidenceSurface,
    NextTestRequest,
)


SCOPE_FP = "a" * 64
GOVERNED = (
    "metric.effect",
    "metric.h1",
    "metric.h2",
    "dimension.event_date",
)


def parent_contract() -> AnalyticalRequestContract:
    return AnalyticalRequestContract(
        authority_id="auth-stateful",
        request_ref="req-stateful",
        semantic_context_version="ctx-stateful-material-v1",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="atl_stateful",
            version_id="scope_v1",
        ),
        scope_fingerprint=SCOPE_FP,
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


def next_test_request() -> NextTestRequest:
    return NextTestRequest(
        request_id="ntr_" + "1" * 24,
        ambiguity_code="TEMPORAL_DISCRIMINATION_REQUIRED",
        hypothesis_ids=("p19h_" + "2" * 24, "p19h_" + "3" * 24),
        required_evidence_surface=NextTestEvidenceSurface.TEMPORAL_ORDER,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id="atl_stateful",
        scope_version_id="scope_v1",
    )


class AnalyticalMaterialStateMachine(RuleBasedStateMachine):
    """Reference lifecycle for material/Evidence/P19/P17 sequencing.

    This is deliberately not a second runtime. It uses production contract
    projectors and tracks only observable revisions/fingerprints so Hypothesis
    can explore legal operation sequences and shrink violations.
    """

    def __init__(self):
        super().__init__()
        self.parent = parent_contract()
        self.current = self.parent
        self.scope_fp = self.parent.scope_fingerprint
        self.executed_material: set[str] = set()
        self.evidence_revision = 0
        self.last_p19_revision = 0
        self.pending_next_test = False
        self.adaptive_reentries = 0
        self.terminal = False

    def _execute_material_once(self) -> bool:
        key = self.current.material_fingerprint
        if key in self.executed_material:
            return False
        self.executed_material.add(key)
        self.evidence_revision += 1
        return True

    @rule()
    @precondition(lambda self: self.evidence_revision == 0)
    def initial_material(self):
        assert self._execute_material_once()

    @rule()
    @precondition(
        lambda self: (
            self.evidence_revision == 1
            and self.last_p19_revision < self.evidence_revision
            and self.adaptive_reentries == 0
        )
    )
    def p19_requests_one_next_test(self):
        self.last_p19_revision = self.evidence_revision
        self.pending_next_test = True

    @rule()
    @precondition(
        lambda self: self.pending_next_test and self.adaptive_reentries == 0
    )
    def p17_projects_child_material(self):
        delta = typed_child_material_delta_for_next_test(
            parent=self.parent,
            request=next_test_request(),
            governed_semantic_refs=GOVERNED,
        )
        self.current = delta.child_contract
        self.pending_next_test = False
        self.adaptive_reentries += 1
        assert delta.scope_fingerprint == self.scope_fp
        assert delta.parent_material_fingerprint == self.parent.material_fingerprint
        assert delta.child_material_fingerprint != delta.parent_material_fingerprint

    @rule()
    @precondition(
        lambda self: (
            self.adaptive_reentries == 1
            and self.current.material_fingerprint
            not in self.executed_material
        )
    )
    def child_material_adds_new_evidence(self):
        before = self.evidence_revision
        assert self._execute_material_once()
        assert self.evidence_revision == before + 1

    @rule()
    @precondition(
        lambda self: self.current.material_fingerprint in self.executed_material
    )
    def duplicate_material_is_effectively_once(self):
        before_execution_count = len(self.executed_material)
        before_evidence_revision = self.evidence_revision
        assert self._execute_material_once() is False
        assert len(self.executed_material) == before_execution_count
        assert self.evidence_revision == before_evidence_revision

    @rule()
    @precondition(
        lambda self: (
            self.evidence_revision >= 2
            and self.last_p19_revision < self.evidence_revision
            and self.adaptive_reentries == 1
        )
    )
    def p19_reassesses_only_after_new_evidence(self):
        self.last_p19_revision = self.evidence_revision
        self.terminal = True

    @rule()
    def unknown_semantic_id_never_enters_child_material(self):
        with pytest.raises(AdaptiveTestDesignError):
            typed_child_material_delta_for_next_test(
                parent=self.parent,
                request=next_test_request(),
                governed_semantic_refs=(
                    "metric.effect",
                    "metric.h1",
                    "metric.h2",
                ),
            )

    @invariant()
    def user_scope_never_changes_when_analysis_deepens(self):
        assert self.current.scope_identity == self.parent.scope_identity
        assert self.current.scope_fingerprint == self.scope_fp

    @invariant()
    def material_projection_remains_internally_coherent(self):
        coverage = material_coverage_contract(self.current)
        assert coverage.scope_fingerprint == self.scope_fp
        assert coverage.material_fingerprint == self.current.material_fingerprint
        assert set(coverage.required_metric_refs).issubset(
            set(coverage.allowed_metric_refs)
        )
        assert set(coverage.required_breakout_refs).issubset(
            set(coverage.allowed_breakout_refs)
        )

    @invariant()
    def one_next_test_never_creates_multiple_reentries(self):
        assert self.adaptive_reentries <= 1
        assert len(self.executed_material) <= 2

    @invariant()
    def p19_revision_never_runs_ahead_of_evidence(self):
        assert self.last_p19_revision <= self.evidence_revision
        if self.terminal:
            assert self.last_p19_revision == self.evidence_revision
            assert self.evidence_revision >= 2


TestAnalyticalMaterialStateMachine = AnalyticalMaterialStateMachine.TestCase
TestAnalyticalMaterialStateMachine.settings = settings(
    max_examples=1000,
    stateful_step_count=24,
    deadline=None,
)
