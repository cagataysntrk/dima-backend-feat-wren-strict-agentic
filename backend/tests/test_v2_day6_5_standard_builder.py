"""Provider-free invariants for bounded StandardBuilder."""

from __future__ import annotations

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    RepresentabilityDecision,
)
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.representability import RepresentabilityGate
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_builder import (
    StandardBuilderSession,
    StandardBuilderState,
    StandardWorkMode,
)
from app.v2.standard_projection import StandardProjectionCompiler


def _handles():
    handles = SemanticHandleRegistry()

    def mint(candidate_id: str, kind: str, canonical: str):
        return handles.mint_from_resolver(
            tenant_binding="tenant-a",
            context_version="ctx-1",
            resolver_provenance_id=candidate_id,
            target_kind=kind,
            canonical_target=ResolvedSemanticRef(
                candidate_id=candidate_id,
                target_kind=SemanticTargetKind(kind),
                canonical_name=canonical,
                cube_names=("Sales",),
            ),
        )

    metric = mint("metric-net", "metric", "Sales.net_revenue")
    dimension = mint("dim-region", "dimension", "Sales.region")
    return handles, metric, dimension


def _obligation(capability, *handles, obligation_id="U1"):
    return CandidateObligation(
        obligation_id=obligation_id,
        capability_key=capability,
        origin=ObligationOrigin.USER_MUST,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=tuple(handle.handle_id for handle in handles),
    )


def _session(handles, *, max_model_turns=4):
    return StandardBuilderSession(
        compiler=StandardProjectionCompiler(semantic_handles=handles),
        tenant_binding="tenant-a",
        context_version="ctx-1",
        max_model_turns=max_model_turns,
    )


def test_direct_is_first_attempt_success_of_same_builder():
    handles, metric, _ = _handles()
    session = _session(handles)

    result = session.submit(
        (_obligation(ManagerCapabilityKey.PERFORMANCE, metric),)
    )

    assert result.state == StandardBuilderState.PROJECTION_READY
    assert result.work_mode == StandardWorkMode.STANDARD_DIRECT
    assert result.projection is not None
    assert result.projection.metric_handles == (metric.handle_id,)
    assert result.proposal_executions == 1


def test_missing_standard_binding_requests_repair_not_research():
    handles, _, dimension = _handles()
    obligation = _obligation(
        ManagerCapabilityKey.BREAKDOWN,
        dimension,
    )

    pre = RepresentabilityGate().decide_bound(obligations=(obligation,))
    assert pre.decision == RepresentabilityDecision.STANDARD_BUILD_REQUIRED

    result = _session(handles).submit((obligation,))
    assert result.state == StandardBuilderState.NEEDS_REPAIR
    assert result.work_mode is None
    assert any("missing required semantic kinds: metric" in x for x in result.reasons)


def test_repaired_standard_projection_uses_builder_mode():
    handles, metric, dimension = _handles()
    session = _session(handles)

    first = session.submit(
        (_obligation(ManagerCapabilityKey.BREAKDOWN, dimension),)
    )
    assert first.state == StandardBuilderState.NEEDS_REPAIR

    repaired = session.submit(
        (_obligation(ManagerCapabilityKey.BREAKDOWN, metric, dimension),)
    )
    assert repaired.state == StandardBuilderState.PROJECTION_READY
    assert repaired.work_mode == StandardWorkMode.STANDARD_BUILDER
    assert repaired.proposal_executions == 2
    assert repaired.projection is not None
    assert repaired.projection.metric_handles == (metric.handle_id,)
    assert repaired.projection.dimension_handles == (dimension.handle_id,)


def test_same_action_same_unchanged_state_is_no_progress_without_reexecution():
    handles, _, dimension = _handles()
    session = _session(handles)
    proposal = (_obligation(ManagerCapabilityKey.BREAKDOWN, dimension),)

    first = session.submit(proposal)
    assert first.state == StandardBuilderState.NEEDS_REPAIR
    assert first.proposal_executions == 1

    duplicate = session.submit(proposal)
    assert duplicate.state == StandardBuilderState.NO_PROGRESS
    assert duplicate.proposal_executions == 1
    assert "without state progress" in duplicate.reasons[0]


def test_research_capability_routes_to_research_without_standard_compile_retry():
    handles, _, _ = _handles()
    session = _session(handles)
    relationship = _obligation(ManagerCapabilityKey.RELATIONSHIP)

    result = session.submit((relationship,))

    assert result.state == StandardBuilderState.RESEARCH_REQUIRED
    assert result.projection is None
    assert result.proposal_executions == 1


def test_builder_budget_fails_closed_for_changed_repairs():
    handles, metric, dimension = _handles()
    session = _session(handles, max_model_turns=1)

    first = session.submit(
        (_obligation(ManagerCapabilityKey.BREAKDOWN, dimension),)
    )
    assert first.state == StandardBuilderState.NEEDS_REPAIR

    changed = session.submit(
        (_obligation(ManagerCapabilityKey.BREAKDOWN, metric, dimension),)
    )
    assert changed.state == StandardBuilderState.BUDGET_EXHAUSTED
    assert changed.projection is None
    assert changed.proposal_executions == 1
