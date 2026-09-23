"""One deterministic real-Wren Day8-C root-cause orchestration sentinel.

No LLM participates. The test proves:
accepted ORCHESTRATED ROOT_CAUSE
-> deterministic existing COMPARE bootstrap
-> Wren/QueryContract/VERIFIED Evidence
-> inspect
-> server-owned follow-up QUERY task
-> second VERIFIED Evidence
-> explicit SUPPORTS
-> CANDIDATE_CAUSE ceiling.
"""

from __future__ import annotations

import pytest

from app import contracts as contracts_module
from app.v2.acceptance import IntentAcceptanceGate
from app.v2.epistemics import (
    CurrentRunEvidenceView,
    EpistemicFindingError,
    EvidenceLinkedFindingBuilder,
    HypothesisLedger,
)
from app.v2.hypothesis_proposals import HypothesisProposalBoundary
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationStatus,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    EpistemicLabel,
    HypothesisEvidenceRelation,
    HypothesisEvidenceRelationProposal,
    HypothesisNextTestProposal,
    HypothesisProposal,
    PeriodKind,
    ResearchTaskKind,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.research_tools import ResearchToolRunner
from app.v2.root_cause_orchestration import (
    HypothesisNextTestBoundary,
    RootCauseBootstrapPolicy,
    RootCauseBootstrapStatus,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _CountingWren:
    def __init__(self, wren) -> None:
        self._wren = wren
        self.mdl_version = wren.mdl_version
        self.query_calls = 0

    def cube_sql(self, cube_query: dict):
        return self._wren.cube_sql(cube_query)

    def dry_plan(self, sql: str, *, principal=None):
        return self._wren.dry_plan(sql, principal=principal)

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        return self._wren.query(sql, limit=limit, principal=principal)


def test_day8_root_cause_orchestration_crosses_real_wren_without_causal_upgrade(
    wren,
    schema,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())
    assert "tarih" in tuple(cube.get("time_dimensions") or ())

    tenant = "day8-root-real-tenant"
    context_version = "ctx-day8-root-real-v1"
    root_id = "U_ROOT"
    turn_id = "turn-day8-root-real"
    question = "Arıza sayısı neden değişti?"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=turn_id, text=question)
    source = spans.mint_exact(message_id=turn_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day8-root-real:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day8-root-real-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
        parent_obligation_id=root_id,
    )
    comparison = handles.mint_from_temporal_engine(
        tenant_binding=tenant,
        context_version=context_version,
        temporal_provenance_id="day8-root-real:comparison",
        target_kind="comparison",
        canonical_target=ResolvedComparison(
            mode="previous_period",
            source_text="Şubat 2024 ile Ocak 2024",
            base_period=ResolvedPeriod(
                kind=PeriodKind.THIS_MONTH,
                source_text="Şubat 2024",
                time_dimension="tarih",
                start="2024-02-01",
                end="2024-02-29",
            ),
            reference_period=ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="Ocak 2024",
                time_dimension="tarih",
                start="2024-01-01",
                end="2024-01-31",
            ),
        ),
        parent_obligation_id=root_id,
    )

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    principal = Principal(
        user_id="day8-root-real-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    service = _CountingWren(wren)
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=spans,
            semantic_handles=handles,
        ),
        core_analytics=ManagerCoreAnalyticsAdapter(semantic_handles=handles),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=TenantAnalyticsRuntimeV0(
                tenant_id=tenant,
                tenant_slug="demo-boyahane",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=wren.mdl_version,
                catalog=str(schema.get("catalog") or "wren"),
                schema_name=str(
                    schema.get("schema_name")
                    or schema.get("schema")
                    or "public"
                ),
                db_online=True,
            ),
            contract_store=contract_store,
            session_id="day8-root-real-session",
        ),
    )
    runtime = ManagerRuntime(request_ref="day8-root-real-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="day8-root-real-attempt",
                    turn_id=turn_id,
                    request_ref="day8-root-real-request",
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id=root_id,
                            capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                            origin=ObligationOrigin.USER_MUST,
                            source_refs=(source.source_ref,),
                            semantic_handle_refs=(
                                metric.handle_id,
                                comparison.handle_id,
                            ),
                        ),
                    ),
                ).model_dump(mode="json")
            },
        ),
        executor=executor,
    )

    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()
    bootstrap = RootCauseBootstrapPolicy(
        semantic_handles=handles,
    ).prepare(
        runtime=runtime,
        evidence_store=executor.evidence_store,
        task_registry=registry,
        root_obligation_id=root_id,
        tenant_binding=tenant,
        context_version=context_version,
    )
    assert bootstrap.status == RootCauseBootstrapStatus.TASK_READY
    assert bootstrap.selected_capability == ManagerCapabilityKey.COMPARISON
    assert bootstrap.task is not None
    assert bootstrap.task.task_kind == ResearchTaskKind.COMPARE.value

    result1 = runner.execute(
        task=bootstrap.task,
        tool_id=runner.tool_id_for_task(bootstrap.task),
        call=ManagerToolCall(
            name=ManagerToolName.RUN_ANALYTICS,
            args={
                "obligation_ids": (root_id,),
                "metric_handles": (metric.handle_id,),
                "comparison_handle": comparison.handle_id,
            },
        ),
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert result1.evidence.verified is True
    assert len(result1.evidence.query_contract_refs) == 2
    assert result1.observation.obligations_verified == ()
    assert result1.observation.obligations_unverified == (root_id,)
    root_after_bootstrap = next(
        item for item in runtime.ledger.items if item.obligation_id == root_id
    )
    assert root_after_bootstrap.status == ObligationStatus.IN_PROGRESS

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": result1.evidence.artifact_id},
        ),
        executor=executor,
    )

    ledger = HypothesisLedger(
        parent_obligation_id=root_id,
        accepted_contract_id=runtime.accepted_contract.contract_id,
        lineage_id=runtime.ledger.lineage_id,
        run_id=runtime.snapshot.run_id,
        obligation_ledger=runtime.ledger,
        evidence_store=executor.evidence_store,
        evidence_view=CurrentRunEvidenceView(runtime),
        semantic_handles=handles,
        research_tasks=registry,
        tenant_binding=tenant,
        context_version=context_version,
    )
    proposal_boundary = HypothesisProposalBoundary(ledger=ledger)
    hypothesis = proposal_boundary.register(
        HypothesisProposal(
            statement="Önceki dönem farkı aday açıklama olabilir.",
            semantic_handle_refs=(metric.handle_id,),
            trigger_evidence_refs=(result1.evidence.artifact_id,),
            limitations=("Gözlemsel kanıt nedensellik doğrulaması değildir.",),
        )
    )
    assert hypothesis.evidence_links == ()

    next_boundary = HypothesisNextTestBoundary(
        ledger=ledger,
        runtime=runtime,
        evidence_store=executor.evidence_store,
        semantic_handles=handles,
        task_registry=registry,
        tenant_binding=tenant,
        context_version=context_version,
    )
    next_proposal = HypothesisNextTestProposal(
        hypothesis_ref=hypothesis.hypothesis_id,
        task_kind=ResearchTaskKind.QUERY,
        input_refs=(metric.handle_id,),
        trigger_evidence_ref=result1.evidence.artifact_id,
        material_reason="Karşılaştırma sonrası metric seviyesini ayrı gözlemsel testle kontrol et.",
    )
    task2 = next_boundary.materialize(next_proposal)
    replay = next_boundary.materialize(next_proposal)
    assert replay.task_id == task2.task_id
    assert task2.task_id.startswith("rt_")
    assert task2.task_id not in HypothesisNextTestProposal.model_fields

    before_followup_queries = service.query_calls
    followup_call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": (root_id,),
            "metric_handles": (metric.handle_id,),
            "derived_task_id": task2.task_id,
            "derived_parent_obligation_id": root_id,
            "derived_capability_key": ManagerCapabilityKey.PERFORMANCE.value,
            "derived_evidence_ref": result1.evidence.artifact_id,
        },
    )
    result2 = runner.execute(
        task=task2,
        tool_id=runner.tool_id_for_task(task2),
        call=followup_call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert service.query_calls == before_followup_queries + 1
    assert result2.evidence.verified is True
    assert result2.evidence.query_contract_refs

    # Exact replay reuses the task receipt; no duplicate DB side effect.
    replay_result = runner.execute(
        task=task2,
        tool_id=runner.tool_id_for_task(task2),
        call=followup_call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert replay_result.evidence.artifact_id == result2.evidence.artifact_id
    assert service.query_calls == before_followup_queries + 1

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": result2.evidence.artifact_id},
        ),
        executor=executor,
    )
    updated = proposal_boundary.attach_relation(
        HypothesisEvidenceRelationProposal(
            hypothesis_ref=hypothesis.hypothesis_id,
            evidence_ref=result2.evidence.artifact_id,
            relation=HypothesisEvidenceRelation.SUPPORTS,
        )
    )
    assert updated.evidence_links[0].relation == HypothesisEvidenceRelation.SUPPORTS

    finding = EvidenceLinkedFindingBuilder(ledger=ledger).build(
        statement="Bu ilişki yalnız desteklenen aday neden düzeyindedir.",
        epistemic_label=EpistemicLabel.CANDIDATE_CAUSE,
        evidence_refs=(result2.evidence.artifact_id,),
        hypothesis_ref=hypothesis.hypothesis_id,
    )
    assert finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE

    with pytest.raises(EpistemicFindingError, match="CAUSAL_NOT_IDENTIFIED"):
        EvidenceLinkedFindingBuilder(ledger=ledger).build(
            statement="Kesin neden.",
            epistemic_label=EpistemicLabel.CONFIRMED_CAUSE,
            evidence_refs=(result2.evidence.artifact_id,),
            hypothesis_ref=hypothesis.hypothesis_id,
        )

    # COMPARE = 2 Wren queries, follow-up QUERY = 1, replay = 0.
    assert service.query_calls == 3
    assert len(persisted) == 3
    assert all(row.sql for row in persisted)
    assert all(row.result_hash for row in persisted)
    assert ResearchTaskKind.ROOT_CAUSE.value not in {
        task.task_kind for task in registry.tasks
    } if hasattr(ResearchTaskKind, "ROOT_CAUSE") else True
