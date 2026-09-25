"""Provider-free Day 7 Manager-loop integration with ResearchToolContract mode."""

from __future__ import annotations

import json

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop
from helpers.manager_action_set_adapter import adapt_legacy_manager_intent
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ResearchRunTerminal,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.root_cause_orchestration import RootCauseLoopContext
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _SyntheticService:
    mdl_version = "mdl-day7-loop-v1"

    def cube_sql(self, cube_query: dict) -> str:
        return "DAY7LOOP:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        query = json.loads(sql.removeprefix("DAY7LOOP:"))
        measures = list(query.get("measures") or ())
        return {
            "columns": measures,
            "rows": [{metric: 42.0 for metric in measures}],
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in measures],
        }


class _ZeroRowSyntheticService(_SyntheticService):
    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        query = json.loads(sql.removeprefix("DAY7LOOP:"))
        measures = list(query.get("measures") or ())
        return {
            "columns": measures,
            "rows": [],
            "row_count": 0,
            "column_types": ["DOUBLE" for _ in measures],
        }


class _ContractStore:
    def record_v2_minimum(self, **kwargs):
        return {"id": "day7-loop-qc-1", "sealed": True}


class _ResultAwareFakeLLM:
    """No language heuristics: reacts only to typed Manager state exposed by the runtime."""

    def __init__(self) -> None:
        self.prompts: list[dict] = []

    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)

        delta = payload.get("CURRENT_RESULT_DELTA")
        if not payload.get("EVIDENCE_REFS"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "run_analytics",
                    "obligation_ids": ["U1"],
                    "metric_handles": ["h1"],
                },
            )

        if delta and delta.get("inspection_required"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "inspect_evidence",
                    "evidence_ref": delta["evidence_ref"],
                },
            )

        return adapt_legacy_manager_intent(payload, {"action": "finish"})


class _WouldKeepThinkingAfterZeroRowLLM(_ResultAwareFakeLLM):
    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)

        delta = payload.get("CURRENT_RESULT_DELTA")
        if not payload.get("EVIDENCE_REFS"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "run_analytics",
                    "obligation_ids": ["U1"],
                    "metric_handles": ["h1"],
                },
            )
        if delta and delta.get("inspection_required"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "inspect_evidence",
                    "evidence_ref": delta["evidence_ref"],
                },
            )

        return adapt_legacy_manager_intent(payload, {"action": "finish"})


def _accepted_runtime(service=None):
    tenant = "day7-loop-tenant"
    context_version = "ctx-day7-loop-v1"
    message_id = "day7-loop-turn"
    question = "net geliri incele"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface="net geliri")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day7-loop:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-loop-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )

    principal = Principal(
        user_id="day7-loop-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="day7-loop",
    )
    service = service or _SyntheticService()
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
                tenant_slug="day7-loop",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="day7-loop",
                schema_name="main",
                db_online=True,
            ),
            contract_store=_ContractStore(),
            session_id="day7-loop-session",
        ),
    )

    runtime = ManagerRuntime(request_ref="day7-loop-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="day7-loop-attempt",
        turn_id=message_id,
        request_ref="day7-loop-request",
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
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={"envelope": envelope.model_dump(mode="json")},
        ),
        executor=executor,
    )
    return (
        spans,
        runtime,
        executor,
        question,
        message_id,
        RootCauseLoopContext(
            semantic_handles=handles,
            tenant_binding=tenant,
            context_version=context_version,
        ),
    )


def test_manager_loop_contract_mode_finishes_without_redundant_delta_cognition():
    spans, runtime, executor, question, message_id, root_context = _accepted_runtime()
    llm = _ResultAwareFakeLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=root_context,
    )

    outcome = loop.run(
        question=question,
        message_id=message_id,
        request_ref="day7-loop-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.run_finished is True
    assert outcome.verified_complete is True
    assert runtime.snapshot.inspected_evidence_refs == ()
    assert runtime.snapshot.latest_evidence_ref in runtime.snapshot.evidence_refs

    deterministic = [
        item
        for item in outcome.observations
        if item.get("kind") == "deterministic_task_executed"
    ]
    assert [item["task_id"] for item in deterministic] == ["seed:U1"]

    # Canonical seed identity and semantic wiring are server-owned. Once that task
    # produces VERIFIED Evidence and satisfies U1, CompletionGate closes at the loop
    # boundary without spending a post-acceptance cognition turn.
    assert llm.prompts == []
    assert runtime.snapshot.research_manager_turns == 0

def test_zero_row_verified_evidence_finishes_without_spending_another_manager_turn():
    spans, runtime, executor, question, message_id, root_context = _accepted_runtime(
        service=_ZeroRowSyntheticService()
    )
    llm = _WouldKeepThinkingAfterZeroRowLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=root_context,
    )

    outcome = loop.run(
        question=question,
        message_id=message_id,
        request_ref="day7-loop-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.run_finished is True
    assert outcome.verified_complete is True
    assert runtime.snapshot.research_manager_turns == 0
    assert runtime.snapshot.data_queries == 1
    assert runtime.snapshot.inspected_evidence_refs == ()
    assert llm.prompts == []

    finish = [
        item
        for item in outcome.observations
        if item.get("kind") == "finish"
    ]
    assert finish[-1]["reason"] == "loop_boundary_deterministic_completion_gate"

def test_server_executable_seed_does_not_spend_cognition_reconstructing_task_identity():
    spans, runtime, executor, question, message_id, root_context = _accepted_runtime()
    llm = _ResultAwareFakeLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=root_context,
    )
    outcome = loop.run(
        question=question,
        message_id=message_id,
        request_ref="day7-loop-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.verified_complete is True
    assert llm.prompts == []
    assert not any(
        item.get("kind") == "tool"
        and item.get("tool") == "propose_acceptance"
        for item in outcome.observations
    )
    assert [
        item["task_id"]
        for item in outcome.observations
        if item.get("kind") == "deterministic_task_executed"
    ] == ["seed:U1"]

def test_answer_now_after_verified_evidence_pauses_partial_without_completion_laundering():
    spans, runtime, executor, question, message_id, root_context = _accepted_runtime()
    llm = _ResultAwareFakeLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=root_context,
        answer_now_check=lambda: bool(runtime.snapshot.evidence_refs),
    )

    outcome = loop.run(
        question=question,
        message_id=message_id,
        request_ref="day7-loop-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.answer_now_requested is True
    assert outcome.run_finished is False
    assert outcome.verified_complete is False
    assert outcome.terminal_status == ResearchRunTerminal.PARTIAL
    assert runtime.snapshot.terminal_status == ResearchRunTerminal.PARTIAL
    assert runtime.snapshot.evidence_refs
    assert runtime.snapshot.inspected_evidence_refs == ()
    # The governed analytics adapter legitimately VERIFIED U1 from real Evidence before
    # the user control fired. ANSWER_NOW itself must not run CompletionGate/finish.
    assert runtime.ledger.active_user_must[0].status.value == "VERIFIED"
    assert llm.prompts == []
    assert any(item.get("kind") == "answer_now" for item in outcome.observations)
    assert not any(item.get("kind") == "finish" for item in outcome.observations)
