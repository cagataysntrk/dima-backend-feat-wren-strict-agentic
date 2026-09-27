"""Day 6.5 narrow REAL trust-plane vertical proof.

No LLM and no raw-language parsing are involved here. The test starts from one
Resolver-authoritative opaque semantic handle and proves that the existing Manager
execution boundary can cross the repository's real in-process WrenService + demo
DuckDB:

    accepted obligation
    -> opaque SemanticHandle
    -> Manager RUN_ANALYTICS
    -> AnalyticsIR / RequirementLedger
    -> CubePlanner
    -> real Wren cube_sql / dry_plan / query
    -> ResultValidator
    -> real ContractStore.record_v2_minimum contract construction
    -> verified EvidenceArtifact
    -> verified obligation

Only durable persistence I/O is replaced with an ephemeral capture so the test cannot
write the repository spool or depend on an external control-plane database.
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
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


def test_manager_standard_analysis_crosses_real_wren_trust_plane(
    wren,
    schema,
    monkeypatch,
):
    cube = next(
        item for item in schema["cubes"]
        if item.get("name") == "bakim"
    )
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())

    tenant_binding = "test-tenant"
    context_version = "ctx-day65-real-wren-v1"
    message_id = "turn-day65-real-wren"
    question = "gerçek wren dikey ispatı"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant_binding,
        context_version=context_version,
        resolver_provenance_id="day65-real-wren:bakim:ariza_sayisi",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day65-real-wren-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )

    acceptance = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    )

    # Exercise the real QueryContract construction/seal logic while keeping this
    # integration proof hermetic: no external DB and no contract-spool write.
    persisted_rows = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_rows.append(row),
    )
    contract_store = contracts_module.ContractStore()

    principal = Principal(
        user_id="test-user",
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
        acceptance=acceptance,
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
            session_id="day65-real-wren-session",
        ),
    )

    runtime = ManagerRuntime(request_ref="day65-real-wren-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="day65-real-wren-attempt",
        turn_id=message_id,
        request_ref="day65-real-wren-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U_REAL_WREN",
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
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None

    manager_call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U_REAL_WREN",),
            "metric_handles": (metric.handle_id,),
        },
    )
    assert "sql" not in manager_call.args
    assert "cube_query" not in manager_call.args

    step = runtime.call_tool(manager_call, executor=executor)
    observation = step.tool_result

    assert observation.evidence_verified is True
    assert observation.query_count == 1
    assert observation.obligations_verified == ("U_REAL_WREN",)
    assert observation.obligations_unverified == ()

    obligation = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REAL_WREN"
    )
    assert obligation.status == ObligationStatus.VERIFIED
    assert obligation.evidence_refs == (observation.evidence_ref,)

    evidence = executor.evidence_store.get(observation.evidence_ref)
    assert evidence.verified is True
    assert evidence.evidence_kind == "standard_analytics"
    assert evidence.obligation_ids == ("U_REAL_WREN",)
    assert evidence.payload["query_count"] == 1
    assert len(evidence.query_contract_refs) == 1
    assert evidence.query_contract_refs[0].startswith("c-")
    assert evidence.payload["executions"]

    # Evidence exposed back to the Manager is handle-bounded, not canonical-schema
    # authority. Canonical names remain inside the governed contract/provenance plane.
    exposed = evidence.payload["executions"][0]
    assert metric.handle_id in tuple(exposed.get("columns") or ())
    assert "ariza_sayisi" not in tuple(exposed.get("columns") or ())

    assert len(persisted_rows) == 1
    persisted = persisted_rows[0]
    assert persisted.result_hash
    assert persisted.row_count is not None
    assert persisted.sql
    assert persisted.cube_query_json
    assert persisted.provenance_json
