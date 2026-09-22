"""Focused Day 7 ResearchTask lifecycle invariants."""

from __future__ import annotations

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_executor import EvidenceStore
from app.v2.manager_models import (
    CandidateObligation,
    ManagerBudget,
    ManagerCapabilityKey,
    ObligationOrigin,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    EvidenceArtifact,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskMaterializationError,
    ResearchTaskService,
)
from app.v2.research_tools import ResearchTaskKind
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


class _AcceptanceExecutor:
    def __init__(self, result):
        self._result = result

    def execute(self, call, validated_args, runtime):
        assert call.name == ManagerToolName.PROPOSE_ACCEPTANCE
        return self._result


def _accepted_runtime():
    tenant = "task-tenant"
    context_version = "ctx-task-v1"
    spans = SourceSpanRegistry()
    text = "net geliri incele"
    source_hash = spans.register_message(message_id="task-turn", text=text)
    source = spans.mint_exact(message_id="task-turn", surface="net geliri")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="task:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="task-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="task:dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="task-dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
        provenance_type="AGENT_DERIVED",
        parent_obligation_id="U1",
        trigger_evidence_ref="E1",
    )

    gate = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )
    envelope = UserIntentEnvelope(
        attempt_id="task-attempt",
        turn_id="task-turn",
        request_ref="task-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id,),
            ),
        ),
    )
    accepted = gate.evaluate(
        envelope=envelope,
        tenant_binding=tenant,
        context_version=context_version,
    )
    assert accepted.contract is not None and accepted.ledger is not None

    runtime = ManagerRuntime(request_ref="task-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={"envelope": envelope.model_dump(mode="json")},
        ),
        executor=_AcceptanceExecutor(accepted),
    )
    return runtime, metric.handle_id, dimension.handle_id


def _verified_evidence() -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id="E1",
        task_id="RT1",
        obligation_ids=("U1",),
        query_contract_refs=("QC1",),
        evidence_kind="standard_analytics",
        verified=True,
        payload={
            "query_count": 1,
            "executions": (
                {
                    "row_count": 2,
                    "rows": ({"h1": 120.0}, {"h1": 90.0}),
                },
            ),
        },
    )


def test_seed_task_materializes_only_from_accepted_obligation():
    runtime, metric_handle, _ = _accepted_runtime()

    task = ResearchTaskService().seed_for_obligation(
        runtime=runtime,
        obligation_id="U1",
        task_id="RT1",
    )

    assert task.task_kind == ResearchTaskKind.QUERY.value
    assert task.origin == "USER_SEED"
    assert task.question_id == "U1"
    assert task.input_refs == (metric_handle,)
    assert task.branch_depth == 0


def test_derived_task_requires_verified_and_inspected_current_evidence():
    runtime, metric_handle, dimension_handle = _accepted_runtime()
    tasks = ResearchTaskService()
    parent = tasks.seed_for_obligation(
        runtime=runtime,
        obligation_id="U1",
        task_id="RT1",
    ).model_copy(update={"state": "complete"})

    store = EvidenceStore()
    evidence = _verified_evidence()
    store.put(evidence)
    runtime.attach_evidence(evidence.artifact_id)

    proposal = DerivedResearchTaskProposal(
        task_id="D1",
        task_kind=ResearchTaskKind.BREAKDOWN,
        parent_task_id=parent.task_id,
        parent_obligation_id="U1",
        trigger_evidence_ref=evidence.artifact_id,
        input_refs=(metric_handle, dimension_handle),
        material_reason="verified result shows a material regional spread worth testing",
    )

    with pytest.raises(
        ResearchTaskMaterializationError,
        match="requires inspected evidence",
    ):
        tasks.materialize_derived(
            runtime=runtime,
            evidence_store=store,
            parent_task=parent,
            proposal=proposal,
        )

    runtime.mark_evidence_inspected(evidence.artifact_id)
    child = tasks.materialize_derived(
        runtime=runtime,
        evidence_store=store,
        parent_task=parent,
        proposal=proposal,
    )

    assert child.origin == "AGENT_DERIVED"
    assert child.parent_task_id == "RT1"
    assert child.parent_obligation_id == "U1"
    assert child.trigger_evidence_ref == "E1"
    assert child.branch_depth == 1
    assert child.task_kind == ResearchTaskKind.BREAKDOWN.value
    assert child.input_refs == (metric_handle, dimension_handle)


def test_derived_task_rejects_unverified_or_wrong_parent_evidence():
    runtime, metric_handle, dimension_handle = _accepted_runtime()
    tasks = ResearchTaskService()
    parent = tasks.seed_for_obligation(
        runtime=runtime,
        obligation_id="U1",
        task_id="RT1",
    ).model_copy(update={"state": "complete"})

    store = EvidenceStore()
    bad = _verified_evidence().model_copy(
        update={
            "verified": False,
            "obligation_ids": ("OTHER",),
        }
    )
    store.put(bad)
    runtime.attach_evidence(bad.artifact_id)
    runtime.mark_evidence_inspected(bad.artifact_id)

    proposal = DerivedResearchTaskProposal(
        task_id="D1",
        task_kind=ResearchTaskKind.BREAKDOWN,
        parent_task_id="RT1",
        parent_obligation_id="U1",
        trigger_evidence_ref="E1",
        input_refs=(metric_handle, dimension_handle),
        material_reason="candidate direction",
    )

    with pytest.raises(
        ResearchTaskMaterializationError,
        match="requires verified evidence",
    ):
        tasks.materialize_derived(
            runtime=runtime,
            evidence_store=store,
            parent_task=parent,
            proposal=proposal,
        )


def test_branch_depth_is_bounded():
    runtime, metric_handle, dimension_handle = _accepted_runtime()
    tasks = ResearchTaskService()
    store = EvidenceStore()
    evidence = _verified_evidence()
    store.put(evidence)
    runtime.attach_evidence("E1")
    runtime.mark_evidence_inspected("E1")

    parent = tasks.seed_for_obligation(
        runtime=runtime,
        obligation_id="U1",
        task_id="RT1",
    ).model_copy(
        update={
            "state": "complete",
            "origin": "AGENT_DERIVED",
            "parent_task_id": "RT0",
            "parent_obligation_id": "U1",
            "trigger_evidence_ref": "E0",
            "branch_depth": 3,
        }
    )
    proposal = DerivedResearchTaskProposal(
        task_id="D4",
        task_kind=ResearchTaskKind.BREAKDOWN,
        parent_task_id="RT1",
        parent_obligation_id="U1",
        trigger_evidence_ref="E1",
        input_refs=(metric_handle, dimension_handle),
        material_reason="another direction",
    )

    with pytest.raises(
        ResearchTaskMaterializationError,
        match="exceeds branch depth 3",
    ):
        tasks.materialize_derived(
            runtime=runtime,
            evidence_store=store,
            parent_task=parent,
            proposal=proposal,
            max_branch_depth=3,
        )


def test_day7_canonical_budget_has_one_runtime_truth():
    budget = ManagerBudget()
    assert budget.max_data_queries == 8
    assert budget.max_tool_calls == 12
    assert budget.max_manager_turns == 6

    with pytest.raises(Exception):
        ManagerBudget(max_data_queries=13)
