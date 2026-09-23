"""Provider-free D8-C1/C2 orchestration attacks."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.epistemics import (
    CurrentRunEvidenceView,
    CurrentRunObligationView,
    HypothesisLedger,
)
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ManagerRunSnapshot,
    ManagerState,
    ObligationOrigin,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.models import (
    EvidenceArtifact,
    HypothesisNextTestProposal,
    PeriodKind,
    ResearchTask,
    ResearchTaskKind,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.obligation_ledger import UserObligationLedgerService
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.root_cause_orchestration import (
    HypothesisNextTestBoundary,
    RootCauseBootstrapPolicy,
    RootCauseBootstrapStatus,
    RootCauseOrchestrationError,
    root_cause_next_test_contract,
    root_cause_next_test_task_kinds,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


TENANT = "tenant-d8-c"
CTX = "ctx-d8-c"
ROOT = "U_ROOT"


class _EvidenceStore:
    def __init__(self):
        self.items = {}

    def put(self, evidence):
        self.items[evidence.artifact_id] = evidence

    def get(self, ref):
        return self.items[ref]


def _metric(handles, *, parent=ROOT, candidate="metric"):
    return handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id=f"resolver:{candidate}",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id=candidate,
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Ops.oee",
            cube_names=("Ops",),
        ),
        parent_obligation_id=parent,
    )


def _dimension(handles, *, parent=ROOT):
    return handles.mint_from_resolver(
        tenant_binding=TENANT,
        context_version=CTX,
        resolver_provenance_id="resolver:dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Ops.shift",
            cube_names=("Ops",),
        ),
        parent_obligation_id=parent,
    )


def _comparison(handles, *, parent=ROOT):
    base = ResolvedPeriod(
        kind=PeriodKind.PREVIOUS_MONTH,
        source_text="geçen ay",
        time_dimension="Ops.date",
        start="2026-08-01",
        end="2026-08-31",
    )
    ref = ResolvedPeriod(
        kind=PeriodKind.PREVIOUS_MONTH,
        source_text="önceki ay",
        time_dimension="Ops.date",
        start="2026-07-01",
        end="2026-07-31",
    )
    return handles.mint_from_temporal_engine(
        tenant_binding=TENANT,
        context_version=CTX,
        temporal_provenance_id="temporal:comparison",
        target_kind="comparison",
        canonical_target=ResolvedComparison(
            mode="previous_period",
            source_text="geçen ayla karşılaştır",
            base_period=base,
            reference_period=ref,
        ),
        parent_obligation_id=parent,
    )


def _accepted_runtime(handles, semantic_refs):
    spans = SourceSpanRegistry()
    message_id = "turn-d8-c"
    question = "OEE neden düştü?"
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface=question)

    runtime = ManagerRuntime(request_ref="req-d8-c")
    runtime.begin_understanding()
    gate = IntentAcceptanceGate(source_spans=spans, semantic_handles=handles)

    class _AcceptanceOnly:
        def execute(self, call, validated_args, rt):
            result = gate.evaluate(
                envelope=validated_args.envelope,
                tenant_binding=TENANT,
                context_version=CTX,
                active_contract=rt.accepted_contract,
                active_ledger=rt.ledger,
                semantic_receipts=rt.semantic_resolution_receipts,
            )
            return result

    from app.v2.manager_tools import ManagerToolCall, ManagerToolName

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="attempt-d8-c",
                    turn_id=message_id,
                    request_ref="req-d8-c",
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id=ROOT,
                            capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                            origin=ObligationOrigin.USER_MUST,
                            source_refs=(source.source_ref,),
                            semantic_handle_refs=tuple(semantic_refs),
                        ),
                    ),
                ).model_dump(mode="json")
            },
        ),
        executor=_AcceptanceOnly(),
    )
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None
    return runtime


def _evidence(ref, task_id, *, verified=True, obligation_ids=(ROOT,)):
    return EvidenceArtifact(
        artifact_id=ref,
        task_id=task_id,
        obligation_ids=tuple(obligation_ids),
        query_contract_refs=("QC1",),
        evidence_kind="standard_analytics",
        verified=verified,
        payload={"query_count": 1, "executions": ()},
    )


def test_metric_only_root_bootstrap_selects_one_server_owned_query_seed():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    runtime = _accepted_runtime(handles, (metric.handle_id,))
    registry = ResearchTaskRegistry()

    result = RootCauseBootstrapPolicy(semantic_handles=handles).prepare(
        runtime=runtime,
        evidence_store=_EvidenceStore(),
        task_registry=registry,
        root_obligation_id=ROOT,
        tenant_binding=TENANT,
        context_version=CTX,
    )

    assert result.status == RootCauseBootstrapStatus.TASK_READY
    assert result.selected_capability == ManagerCapabilityKey.PERFORMANCE
    assert result.task is not None
    assert result.task.task_kind == ResearchTaskKind.QUERY.value
    assert result.task.question_id == ROOT
    assert result.task.task_id.startswith("rt_")
    assert result.task.task_id != f"seed:{ROOT}"


def test_comparison_root_bootstrap_preserves_comparison_and_selects_compare():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    comparison = _comparison(handles)
    runtime = _accepted_runtime(handles, (metric.handle_id, comparison.handle_id))

    result = RootCauseBootstrapPolicy(semantic_handles=handles).prepare(
        runtime=runtime,
        evidence_store=_EvidenceStore(),
        task_registry=ResearchTaskRegistry(),
        root_obligation_id=ROOT,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    assert result.status == RootCauseBootstrapStatus.TASK_READY
    assert result.selected_capability == ManagerCapabilityKey.COMPARISON
    assert result.task.task_kind == ResearchTaskKind.COMPARE.value


def test_metric_dimension_root_bootstrap_is_ambiguous_and_does_not_silently_pick():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    dimension = _dimension(handles)
    runtime = _accepted_runtime(handles, (metric.handle_id, dimension.handle_id))
    registry = ResearchTaskRegistry()

    result = RootCauseBootstrapPolicy(semantic_handles=handles).prepare(
        runtime=runtime,
        evidence_store=_EvidenceStore(),
        task_registry=registry,
        root_obligation_id=ROOT,
        tenant_binding=TENANT,
        context_version=CTX,
    )

    assert result.status == RootCauseBootstrapStatus.AMBIGUOUS_TASK
    assert set(result.candidate_task_kinds) == {
        ResearchTaskKind.BREAKDOWN,
        ResearchTaskKind.RELATIONSHIP,
    }
    assert registry.tasks == ()


def test_existing_inspected_verified_evidence_blocks_unnecessary_bootstrap():
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    runtime = _accepted_runtime(handles, (metric.handle_id,))
    task_id = "seed-existing"
    evidence = _evidence("E_EXISTING", task_id)
    store = _EvidenceStore()
    store.put(evidence)
    runtime.attach_evidence("E_EXISTING")
    runtime.mark_evidence_inspected("E_EXISTING")

    result = RootCauseBootstrapPolicy(semantic_handles=handles).prepare(
        runtime=runtime,
        evidence_store=store,
        task_registry=ResearchTaskRegistry(),
        root_obligation_id=ROOT,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    assert result.status == RootCauseBootstrapStatus.EVIDENCE_READY
    assert result.evidence_refs == ("E_EXISTING",)


def _next_test_fixture(*, inspected=True, verified=True):
    handles = SemanticHandleRegistry()
    metric = _metric(handles)
    dimension = _dimension(handles)
    runtime = _accepted_runtime(handles, (metric.handle_id,))
    registry = ResearchTaskRegistry()

    parent = ResearchTask(
        task_id="rt_parent",
        question_id=ROOT,
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(metric.handle_id,),
        origin="USER_SEED",
        state="complete",
    )
    registry.register(parent)
    evidence = _evidence("E1", parent.task_id, verified=verified)
    store = _EvidenceStore()
    store.put(evidence)
    runtime.attach_evidence("E1")
    if inspected:
        runtime.mark_evidence_inspected("E1")

    ledger = HypothesisLedger(
        parent_obligation_id=ROOT,
        accepted_contract_id=runtime.accepted_contract.contract_id,
        lineage_id=runtime.ledger.lineage_id,
        run_id=runtime.snapshot.run_id,
        obligation_ledger=runtime.ledger,
        evidence_store=store,
        evidence_view=CurrentRunEvidenceView(runtime),
        obligation_view=CurrentRunObligationView(runtime),
        semantic_handles=handles,
        research_tasks=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    hypothesis = ledger.register(
        statement="Vardiya etkisi aday açıklama olabilir.",
        semantic_handle_refs=(metric.handle_id,),
        trigger_evidence_refs=("E1",),
        limitations=("Gözlemsel testtir.",),
    )
    boundary = HypothesisNextTestBoundary(
        ledger=ledger,
        runtime=runtime,
        evidence_store=store,
        semantic_handles=handles,
        task_registry=registry,
        tenant_binding=TENANT,
        context_version=CTX,
    )
    return boundary, ledger, runtime, registry, metric, dimension, hypothesis, store


def _breakdown_proposal(hypothesis, metric, dimension):
    return HypothesisNextTestProposal(
        hypothesis_ref=hypothesis.hypothesis_id,
        task_kind=ResearchTaskKind.BREAKDOWN,
        input_refs=(metric.handle_id, dimension.handle_id),
        trigger_evidence_ref="E1",
        material_reason="Vardiya kırılımı aday açıklamayı sınar.",
    )




def test_next_test_contract_advertises_only_runtime_admissible_direct_families():
    kinds = root_cause_next_test_task_kinds()
    assert kinds == (
        ResearchTaskKind.QUERY,
        ResearchTaskKind.COMPARE,
        ResearchTaskKind.BREAKDOWN,
        ResearchTaskKind.RANK,
    )

    rows = {row["task_kind"]: row for row in root_cause_next_test_contract()}
    assert set(rows) == {"QUERY", "COMPARE", "BREAKDOWN", "RANK"}
    assert all(row["execution_mode"] == "DIRECT" for row in rows.values())
    assert rows["QUERY"]["capability"] == "performance"
    assert rows["QUERY"]["required_semantic_kinds"] == ["metric"]
    assert rows["BREAKDOWN"]["required_semantic_kinds"] == ["dimension", "metric"]
    assert rows["COMPARE"]["required_semantic_kinds"] == ["comparison", "metric"]
    assert rows["RANK"]["required_operation_params"] == [
        "ranking_direction",
        "ranking_limit",
    ]
    assert "TREND" not in rows
    assert "RELATIONSHIP" not in rows
    assert "CONTRIBUTION" not in rows
    assert "PEER_COMPARE" not in rows


def test_next_test_proposal_schema_has_no_model_owned_identity_fields():
    fields = set(HypothesisNextTestProposal.model_fields)
    assert "task_id" not in fields
    assert "parent_task_id" not in fields
    assert "parent_obligation_id" not in fields


def test_next_test_requires_inspected_verified_evidence():
    boundary, _, _, _, metric, dimension, hypothesis, _ = _next_test_fixture(
        inspected=False
    )
    with pytest.raises(RootCauseOrchestrationError, match="INSPECTION_REQUIRED"):
        boundary.materialize(_breakdown_proposal(hypothesis, metric, dimension))


def test_next_test_rejects_foreign_evidence_before_materialization():
    boundary, _, runtime, registry, metric, dimension, hypothesis, store = _next_test_fixture()
    foreign = _evidence(
        "E_FOREIGN",
        "rt_parent",
        obligation_ids=("U_OTHER",),
    )
    store.put(foreign)
    runtime.attach_evidence(foreign.artifact_id)
    runtime.mark_evidence_inspected(foreign.artifact_id)
    before = registry.tasks

    with pytest.raises(RootCauseOrchestrationError, match="unrelated obligation"):
        boundary.materialize(
            HypothesisNextTestProposal(
                hypothesis_ref=hypothesis.hypothesis_id,
                task_kind=ResearchTaskKind.BREAKDOWN,
                input_refs=(metric.handle_id, dimension.handle_id),
                trigger_evidence_ref=foreign.artifact_id,
                material_reason="test",
            )
        )
    assert registry.tasks == before


def test_next_test_rejects_unverified_evidence_before_materialization():
    boundary, _, runtime, registry, metric, dimension, hypothesis, store = _next_test_fixture()
    bad = _evidence("E_BAD", "rt_parent", verified=False)
    store.put(bad)
    runtime.attach_evidence(bad.artifact_id)
    runtime.mark_evidence_inspected(bad.artifact_id)
    before = registry.tasks

    with pytest.raises(RootCauseOrchestrationError, match="VERIFIED"):
        boundary.materialize(
            HypothesisNextTestProposal(
                hypothesis_ref=hypothesis.hypothesis_id,
                task_kind=ResearchTaskKind.BREAKDOWN,
                input_refs=(metric.handle_id, dimension.handle_id),
                trigger_evidence_ref=bad.artifact_id,
                material_reason="test",
            )
        )
    assert registry.tasks == before


def test_next_test_rejects_fake_semantic_handle_before_materialization():
    boundary, _, _, registry, metric, _, hypothesis, _ = _next_test_fixture()
    proposal = HypothesisNextTestProposal(
        hypothesis_ref=hypothesis.hypothesis_id,
        task_kind=ResearchTaskKind.BREAKDOWN,
        input_refs=(metric.handle_id, "sem_" + "f" * 24),
        trigger_evidence_ref="E1",
        material_reason="test",
    )
    before = registry.tasks
    with pytest.raises(RootCauseOrchestrationError, match="non-governed"):
        boundary.materialize(proposal)
    assert registry.tasks == before


def test_next_test_invalid_shape_rejected_before_materialization():
    boundary, _, _, registry, metric, _, hypothesis, _ = _next_test_fixture()
    proposal = HypothesisNextTestProposal(
        hypothesis_ref=hypothesis.hypothesis_id,
        task_kind=ResearchTaskKind.BREAKDOWN,
        input_refs=(metric.handle_id,),
        trigger_evidence_ref="E1",
        material_reason="test",
    )
    before = registry.tasks
    with pytest.raises(RootCauseOrchestrationError, match="not applicable"):
        boundary.materialize(proposal)
    assert registry.tasks == before


def test_next_test_materializes_server_owned_id_and_replay_is_idempotent():
    boundary, ledger, _, registry, metric, dimension, hypothesis, _ = _next_test_fixture()
    proposal = _breakdown_proposal(hypothesis, metric, dimension)

    first = boundary.materialize(proposal)
    second = boundary.materialize(proposal)

    assert first.task_id.startswith("rt_")
    assert second.task_id == first.task_id
    assert first.origin == "AGENT_DERIVED"
    assert first.parent_obligation_id == ROOT
    assert first.parent_task_id == "rt_parent"
    assert first.trigger_evidence_ref == "E1"
    assert len([task for task in registry.tasks if task.task_id == first.task_id]) == 1
    assert ledger.get(hypothesis.hypothesis_id).next_test_task_refs == (first.task_id,)


def test_relationship_next_test_fails_closed_before_dead_end_materialization():
    boundary, _, _, registry, metric, dimension, hypothesis, _ = _next_test_fixture()
    before = registry.tasks
    with pytest.raises(RootCauseOrchestrationError, match="derived RELATIONSHIP"):
        boundary.materialize(
            HypothesisNextTestProposal(
                hypothesis_ref=hypothesis.hypothesis_id,
                task_kind=ResearchTaskKind.RELATIONSHIP,
                input_refs=(metric.handle_id, dimension.handle_id),
                trigger_evidence_ref="E1",
                material_reason="test",
            )
        )
    assert registry.tasks == before


def test_live_obligation_view_accepts_evidence_from_child_added_after_ledger_creation():
    boundary, ledger, runtime, registry, metric, _, hypothesis, store = _next_test_fixture()
    del boundary, hypothesis

    child_id = "D_LIVE_CHILD"
    runtime.replace_ledger(
        UserObligationLedgerService().add_agent_derived(
            runtime.ledger,
            obligation_id=child_id,
            parent_obligation_id=ROOT,
            capability_key=ManagerCapabilityKey.PERFORMANCE,
            source_refs=(),
            semantic_handle_refs=(metric.handle_id,),
        )
    )
    registry.register(
        ResearchTask(
            task_id=child_id,
            question_id=ROOT,
            task_kind=ResearchTaskKind.QUERY.value,
            input_refs=(metric.handle_id,),
            origin="AGENT_DERIVED",
            parent_task_id="rt_parent",
            parent_obligation_id=ROOT,
            trigger_evidence_ref="E1",
            branch_depth=1,
            state="complete",
        )
    )
    child_evidence = _evidence(
        "E_CHILD",
        child_id,
        obligation_ids=(child_id,),
    )
    store.put(child_evidence)
    runtime.attach_evidence(child_evidence.artifact_id)
    runtime.mark_evidence_inspected(child_evidence.artifact_id)

    validated = ledger.validated_evidence(child_evidence.artifact_id)
    assert validated.artifact_id == "E_CHILD"
    assert ledger.obligation_ledger is runtime.ledger
