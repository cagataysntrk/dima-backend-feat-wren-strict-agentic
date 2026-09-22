"""D7-REAL-ADAPTIVE-WREN: one narrow workers=1 two-query trust-plane proof."""

from __future__ import annotations

from app import contracts as contracts_module
from app.v2.acceptance import IntentAcceptanceGate
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
    ResearchRunTerminal,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    ResearchTaskKind,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskRegistry,
    ResearchTaskService,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


def test_real_wren_result_aware_two_task_chain_is_governed_and_terminal(
    wren,
    schema,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())
    dimensions = tuple(cube.get("dimensions") or ())
    assert dimensions, "real demo bakim cube needs one governed dimension for adaptive proof"
    dimension_name = dimensions[0]

    tenant = "day7-real-adaptive-tenant"
    context_version = "ctx-day7-real-adaptive-v1"
    message_id = "turn-day7-real-adaptive"
    question = "arıza sayısını incele; sonuç varsa bir governed breakdown ile derinleş"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface="arıza sayısını")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day7-real-adaptive:bakim:ariza_sayisi",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-real-adaptive-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )

    persisted_contracts = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_contracts.append(row),
    )
    contract_store = contracts_module.ContractStore()

    real_query = wren.query
    query_count = {"n": 0}

    def counted_query(sql, limit=None, *, principal=None):
        query_count["n"] += 1
        return real_query(sql, limit=limit, principal=principal)

    monkeypatch.setattr(wren, "query", counted_query)

    principal = Principal(
        user_id="day7-real-adaptive-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="demo-boyahane",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema") or "public"),
        db_online=True,
    )
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
            service=wren,
            tenant_runtime=tenant_runtime,
            contract_store=contract_store,
            session_id="day7-real-adaptive-session",
        ),
    )

    runtime = ManagerRuntime(request_ref="day7-real-adaptive-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="day7-real-adaptive-attempt",
        turn_id=message_id,
        request_ref="day7-real-adaptive-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U_REAL_ADAPTIVE",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=(metric.handle_id,),
            ),
        ),
    )
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={"envelope": envelope.model_dump(mode="json")},
        ),
        executor=executor,
    )

    tasks = ResearchTaskService()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()

    task1 = tasks.seed_for_obligation(
        runtime=runtime,
        obligation_id="U_REAL_ADAPTIVE",
        task_id="RT_REAL_1",
    )
    call1 = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U_REAL_ADAPTIVE",),
            "metric_handles": (metric.handle_id,),
        },
    )
    result1 = runner.execute(
        task=task1,
        tool_id="wren.query",
        call=call1,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )

    assert result1.evidence.verified is True
    assert result1.evidence.query_contract_refs
    assert result1.evidence.payload["executions"]
    assert result1.evidence.payload["executions"][0]["rows"]

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": result1.evidence.artifact_id},
        ),
        executor=executor,
    )
    assert result1.evidence.artifact_id in runtime.snapshot.inspected_evidence_refs

    parent_before = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REAL_ADAPTIVE"
    )
    assert parent_before.origin == ObligationOrigin.USER_MUST
    assert parent_before.status == ObligationStatus.VERIFIED

    # Deterministic cognition for this execution-composition proof:
    # actual verified result exists -> investigate one governed dimension from the
    # same real Wren cube.  The new handle remains evidence-grounded and opaque.
    dimension = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id=f"day7-real-adaptive:bakim:{dimension_name}",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-real-adaptive-dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name=dimension_name,
            cube_names=("bakim",),
        ),
        provenance_type="AGENT_DERIVED",
        parent_obligation_id="U_REAL_ADAPTIVE",
        trigger_evidence_ref=result1.evidence.artifact_id,
    )

    proposal = DerivedResearchTaskProposal(
        task_id="D_REAL_2",
        task_kind=ResearchTaskKind.BREAKDOWN,
        parent_task_id=result1.task.task_id,
        parent_obligation_id="U_REAL_ADAPTIVE",
        trigger_evidence_ref=result1.evidence.artifact_id,
        input_refs=(metric.handle_id, dimension.handle_id),
        material_reason="verified first result exists; run one bounded governed breakdown",
    )
    task2 = tasks.materialize_derived(
        runtime=runtime,
        evidence_store=executor.evidence_store,
        parent_task=result1.task,
        proposal=proposal,
    )
    assert task2.origin == "AGENT_DERIVED"
    assert task2.parent_task_id == result1.task.task_id
    assert task2.parent_obligation_id == "U_REAL_ADAPTIVE"
    assert task2.trigger_evidence_ref == result1.evidence.artifact_id
    assert task2.branch_depth == 1

    call2 = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U_REAL_ADAPTIVE",),
            "metric_handles": (metric.handle_id,),
            "dimension_handles": (dimension.handle_id,),
            "derived_task_id": task2.task_id,
            "derived_parent_obligation_id": "U_REAL_ADAPTIVE",
            "derived_capability_key": "breakdown",
            "derived_evidence_ref": result1.evidence.artifact_id,
        },
    )
    result2 = runner.execute(
        task=task2,
        tool_id="wren.breakdown",
        call=call2,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert result2.evidence.verified is True
    assert result2.evidence.query_contract_refs

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.INSPECT_EVIDENCE,
            args={"evidence_ref": result2.evidence.artifact_id},
        ),
        executor=executor,
    )

    parent_after = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REAL_ADAPTIVE"
    )
    child = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "D_REAL_2"
    )
    assert parent_after == parent_before
    assert child.origin == ObligationOrigin.AGENT_DERIVED
    assert child.parent_obligation_id == "U_REAL_ADAPTIVE"
    assert child.status == ObligationStatus.VERIFIED

    terminal = runtime.finish()
    assert terminal.terminal_status == ResearchRunTerminal.VERIFIED_COMPLETE

    assert query_count["n"] == 2
    assert len(persisted_contracts) == 2
    assert len(runtime.snapshot.evidence_refs) == 2
    assert len(runtime.snapshot.inspected_evidence_refs) == 2
    assert registry.get("RT_REAL_1").state == "complete"
    assert registry.get("D_REAL_2").state == "complete"
