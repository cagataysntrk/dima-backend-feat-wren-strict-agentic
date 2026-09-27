"""Day 7 first REAL Wren ResearchToolContract vertical.

This is intentionally one tool / one task / workers=1.  It proves that the new
ResearchToolContract gate does not create a shadow execution engine:

Accepted Research authority -> ResearchTask -> ResearchToolContract -> existing
ManagerRuntime/GovernedManagerExecutor -> ManagerCoreAnalyticsAdapter -> real Wren ->
QueryContract -> verified EvidenceArtifact.
"""

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
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    ResearchTask,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import (
    ResearchTaskKind,
    ResearchToolRunner,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


def test_day7_query_contract_crosses_real_wren_and_returns_verified_evidence(
    wren,
    schema,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())

    tenant_binding = "day7-real-tenant"
    context_version = "ctx-day7-real-v1"
    message_id = "turn-day7-real"
    question = "arıza sayısını incele"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant_binding,
        context_version=context_version,
        resolver_provenance_id="day7-real:bakim:ariza_sayisi",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-real-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )

    persisted_rows = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_rows.append(row),
    )
    contract_store = contracts_module.ContractStore()

    principal = Principal(
        user_id="day7-real-user",
        tenant_id=tenant_binding,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant_binding,
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
        core_analytics=ManagerCoreAnalyticsAdapter(
            semantic_handles=handles,
        ),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant_binding,
            context_version=context_version,
            principal=principal,
            service=wren,
            tenant_runtime=tenant_runtime,
            contract_store=contract_store,
            session_id="day7-real-session",
        ),
    )
    runtime = ManagerRuntime(request_ref="day7-real-request")
    runtime.begin_understanding()

    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="day7-real-attempt",
                    turn_id=message_id,
                    request_ref="day7-real-request",
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id="U_DAY7_REAL",
                            capability_key=ManagerCapabilityKey.PERFORMANCE,
                            origin=ObligationOrigin.USER_MUST,
                            source_refs=(source.source_ref,),
                            semantic_handle_refs=(metric.handle_id,),
                        ),
                    ),
                ).model_dump(mode="json")
            },
        ),
        executor=executor,
    )

    task = ResearchTask(
        task_id="RT_DAY7_REAL_QUERY",
        question_id="U_DAY7_REAL",
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(metric.handle_id,),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U_DAY7_REAL",),
            "metric_handles": (metric.handle_id,),
        },
    )

    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.query",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
    )

    assert result.task.state == "complete"
    assert result.evidence.task_id == task.task_id
    assert result.evidence.verified is True
    assert result.evidence.evidence_kind == "standard_analytics"
    assert result.evidence.query_contract_refs
    assert result.observation.evidence_ref == result.evidence.artifact_id
    assert result.observation.evidence_verified is True
    assert result.observation.obligations_verified == ("U_DAY7_REAL",)

    obligation = next(
        item
        for item in runtime.ledger.items
        if item.obligation_id == "U_DAY7_REAL"
    )
    assert obligation.status == ObligationStatus.VERIFIED
    assert obligation.evidence_refs == (result.evidence.artifact_id,)

    exposed = result.evidence.payload["executions"][0]
    assert metric.handle_id in tuple(exposed.get("columns") or ())
    assert "ariza_sayisi" not in tuple(exposed.get("columns") or ())

    assert len(persisted_rows) == 1
    persisted = persisted_rows[0]
    assert persisted.result_hash
    assert persisted.sql
    assert persisted.cube_query_json
    assert persisted.provenance_json
