"""Provider-free Day 7 Manager-loop integration with ResearchToolContract mode."""

from __future__ import annotations

import json

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop, _post_acceptance_native_schema
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
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
            return {
                "action": "run_analytics",
                "obligation_ids": ["U1"],
                "metric_handles": ["h1"],
            }

        if delta and not delta.get("inspected"):
            return {
                "action": "inspect_evidence",
                "evidence_ref": delta["evidence_ref"],
            }

        return {"action": "finish"}


class _WouldKeepThinkingAfterZeroRowLLM(_ResultAwareFakeLLM):
    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)

        delta = payload.get("CURRENT_RESULT_DELTA")
        if not payload.get("EVIDENCE_REFS"):
            return {
                "action": "run_analytics",
                "obligation_ids": ["U1"],
                "metric_handles": ["h1"],
            }
        if delta and not delta.get("inspected"):
            return {
                "action": "inspect_evidence",
                "evidence_ref": delta["evidence_ref"],
            }

        raise AssertionError(
            "zero-row inspected evidence should complete before another Manager turn"
        )


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
    return spans, runtime, executor, question, message_id


def test_manager_loop_contract_mode_materializes_task_observes_delta_and_finishes():
    spans, runtime, executor, question, message_id = _accepted_runtime()
    llm = _ResultAwareFakeLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
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
    assert runtime.snapshot.inspected_evidence_refs == runtime.snapshot.evidence_refs
    assert runtime.snapshot.latest_evidence_ref in runtime.snapshot.evidence_refs

    tool_observations = [
        item for item in outcome.observations if item.get("kind") == "tool"
    ]
    analytics = next(
        item for item in tool_observations if item.get("tool") == "run_analytics"
    )
    assert analytics["research_task_id"] == "seed:U1"

    inspect = next(
        item for item in tool_observations if item.get("tool") == "inspect_evidence"
    )
    assert inspect["research_task_id"] is None

    assert len(llm.prompts) == 3
    assert llm.prompts[0]["CURRENT_RESULT_DELTA"] is None
    assert llm.prompts[1]["CURRENT_RESULT_DELTA"]["verified"] is True
    assert llm.prompts[1]["CURRENT_RESULT_DELTA"]["inspected"] is False
    assert llm.prompts[2]["CURRENT_RESULT_DELTA"]["inspected"] is True

    # Accumulated state does not smuggle the latest delta back into the same bucket.
    assert llm.prompts[1]["ACCUMULATED_RESEARCH_STATE"]["latest_delta"] is None


def test_zero_row_inspected_evidence_finishes_without_spending_another_manager_turn():
    spans, runtime, executor, question, message_id = _accepted_runtime(
        service=_ZeroRowSyntheticService()
    )
    llm = _WouldKeepThinkingAfterZeroRowLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
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
    assert runtime.snapshot.manager_turns == 2
    assert runtime.snapshot.data_queries == 1
    assert runtime.snapshot.inspected_evidence_refs == runtime.snapshot.evidence_refs
    assert len(llm.prompts) == 2

    finish = [
        item
        for item in outcome.observations
        if item.get("kind") == "finish"
    ]
    assert finish[-1]["reason"] == "inspected_zero_row_no_material_branch"


def test_postacceptance_schema_does_not_advertise_propose_acceptance():
    schema = _post_acceptance_native_schema()
    encoded = json.dumps(schema, ensure_ascii=False)

    assert '"propose_acceptance"' not in encoded
    for action in (
        "resolve_semantics",
        "propose_branches",
        "run_analytics",
        "run_relationship",
        "inspect_evidence",
        "request_clarification",
        "finish",
    ):
        assert f'"{action}"' in encoded
