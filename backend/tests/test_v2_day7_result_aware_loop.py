"""Provider-free canonical Day 7 result-aware adaptive Research loop."""

from __future__ import annotations

import json

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationStatus,
    ResearchDirective,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ManagerToolCall, ManagerToolName, ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal
from helpers.manager_action_set_adapter import adapt_legacy_manager_intent


class _AdaptiveService:
    mdl_version = "mdl-day7-adaptive-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "DAY7ADAPT:" + json.dumps(
            cube_query,
            ensure_ascii=False,
            sort_keys=True,
        )

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        query = json.loads(sql.removeprefix("DAY7ADAPT:"))
        dimensions = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dimensions, *measures]
        if dimensions:
            rows = [
                {dimensions[0]: "Kuzey", **{metric: 120.0 for metric in measures}},
                {dimensions[0]: "Güney", **{metric: 75.0 for metric in measures}},
            ]
        else:
            rows = [{metric: 195.0 for metric in measures}]
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": [
                "VARCHAR" if name in dimensions else "DOUBLE"
                for name in columns
            ],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {"id": f"day7-adaptive-qc-{self.n}", "sealed": True}


class _AdaptiveFakeLLM:
    """Deterministic cognition script driven only by typed state/evidence."""

    def __init__(self) -> None:
        self.prompts: list[dict] = []

    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)
        delta = payload.get("CURRENT_RESULT_DELTA")
        recent = payload.get("RECENT_OBSERVATIONS") or []

        if not payload.get("EVIDENCE_REFS"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "run_analytics",
                    "obligation_ids": ["U1"],
                    "metric_handles": ["h1"],
                },
            )

        if (
            delta
            and not delta.get("inspected")
            and not delta.get("disclosed_in_current_prompt")
            and len(payload.get("EVIDENCE_REFS") or []) == 1
        ):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "inspect_evidence",
                    "evidence_ref": delta["evidence_ref"],
                },
            )

        resolved_dimension = None
        for observation in reversed(recent):
            if (
                observation.get("kind") == "tool"
                and observation.get("tool") == "resolve_semantics"
            ):
                resolved = (observation.get("result") or {}).get("resolved") or []
                if resolved:
                    resolved_dimension = resolved[0]["handle"]["handle_id"]
                    break

        # After inspecting the first evidence, discover one evidence-grounded dimension.
        if len(payload.get("EVIDENCE_REFS") or []) == 1 and resolved_dimension is None:
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "resolve_semantics",
                    "resolve_provenance": "AGENT_DERIVED",
                    "target_kind_hints": ["dimension"],
                    "semantic_parent_obligation_id": "U1",
                    "semantic_evidence_ref": delta["evidence_ref"],
                    "semantic_proposal": "bölge",
                },
            )

        ready = payload.get("READY_RESEARCH_TASKS") or []
        fanout_registered = any(
            observation.get("kind") == "fanout_registered"
            for observation in recent
        )

        if (
            len(payload.get("EVIDENCE_REFS") or []) == 1
            and resolved_dimension is not None
            and not fanout_registered
            and not ready
        ):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "propose_branches",
                    "branch_parent_obligation_id": "U1",
                    "branch_evidence_ref": delta["evidence_ref"],
                    "branch_candidates": [
                        {
                            "task_id": "legacy-D1",
                            "capability_key": "breakdown",
                            "input_handles": ["h1", resolved_dimension],
                            "material_reason": "regional breakdown is evidence-grounded",
                        },
                        {
                            "task_id": "legacy-D2",
                            "capability_key": "performance",
                            "input_handles": ["h1"],
                            "material_reason": "bounded metric re-check candidate",
                        },
                        {
                            "task_id": "legacy-D3",
                            "capability_key": "ranking",
                            "input_handles": ["h1", resolved_dimension],
                            "material_reason": "ranked regional follow-up candidate",
                        },
                    ],
                },
            )

        if len(payload.get("EVIDENCE_REFS") or []) == 1 and ready:
            selected = next(
                item for item in ready if item["task_kind"] == "BREAKDOWN"
            )
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "run_analytics",
                    "obligation_ids": ["U1"],
                    "metric_handles": ["h1"],
                    "dimension_handles": [resolved_dimension],
                    "derived_task_id": selected["task_id"],
                    "derived_parent_obligation_id": selected["parent_obligation_id"],
                    "derived_capability_key": "breakdown",
                    "derived_evidence_ref": selected["trigger_evidence_ref"],
                    "derived_reason": "execute one READY bounded branch",
                },
            )

        # Second verified evidence needs no further branch for this canonical case.
        return adapt_legacy_manager_intent(payload, {"action": "finish"})


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-day7-adaptive-v1",
            mdl_version="mdl-day7-adaptive-v1",
            compact_catalog_builder_version="v1",
            business_rules_hash="none",
            prompt_context_policy_version="v1",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales_omega",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_value_x",
                        display="Net Gelir",
                        synonyms=("net gelir", "gelir"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="region_axis_m",
                        display="Bölge",
                        synonyms=("bölge", "region"),
                    ),
                ),
            ),
        ),
    )


def test_result_aware_loop_observes_verified_evidence_and_executes_bounded_second_task():
    tenant = "tenant-day7-adaptive"
    context = _context()
    spans = SourceSpanRegistry()
    question = "net gelir ne durumda; sonuç başka yere işaret ederse incele"
    source_hash = spans.register_message(message_id="day7-adaptive-turn", text=question)
    metric_span = spans.mint_exact(
        message_id="day7-adaptive-turn",
        surface="net gelir",
    )
    adaptive_span = spans.mint_exact(
        message_id="day7-adaptive-turn",
        surface="sonuç başka yere işaret ederse incele",
    )

    handles = SemanticHandleRegistry()
    semantic = ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema={
            "cubes": [
                {
                    "name": "sales_omega",
                    "measures": ["net_value_x"],
                    "dimensions": ["region_axis_m"],
                    "time_dimensions": [],
                }
            ]
        },
        tenant_binding=tenant,
        session_id=None,
        thread_id=None,
    )
    metric_result = semantic.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=(metric_span.source_ref,),
            target_kind_hints=("metric",),
        )
    )
    metric_handle = metric_result.resolved[0].handle.handle_id

    principal = Principal(
        user_id="day7-adaptive-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="day7-adaptive",
    )
    service = _AdaptiveService()
    store = _ContractStore()
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=spans,
            semantic_handles=handles,
        ),
        core_analytics=ManagerCoreAnalyticsAdapter(semantic_handles=handles),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context.context_version.version,
            principal=principal,
            service=service,
            tenant_runtime=TenantAnalyticsRuntimeV0(
                tenant_id=tenant,
                tenant_slug="day7-adaptive",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="day7-adaptive",
                schema_name="main",
                db_online=True,
            ),
            contract_store=store,
            session_id="day7-adaptive-session",
        ),
        semantic_resolution=semantic,
    )

    runtime = ManagerRuntime(request_ref="day7-adaptive-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="day7-adaptive-attempt",
        turn_id="day7-adaptive-turn",
        request_ref="day7-adaptive-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(metric_span.source_ref,),
                semantic_handle_refs=(metric_handle,),
            ),
        ),
        research_directives=(
            ResearchDirective(
                directive_id="R_ADAPT_U1",
                directive_type=ResearchDirectiveType.ADAPT_ON_EVIDENCE,
                parent_obligation_id="U1",
                source_refs=(adaptive_span.source_ref,),
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

    llm = _AdaptiveFakeLLM()
    outcome = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
    ).run(
        question=question,
        message_id="day7-adaptive-turn",
        request_ref="day7-adaptive-request",
        runtime=runtime,
        executor=executor,
    )

    if not outcome.run_finished:
        directive_dispositions = [
            item.model_dump(mode="json")
            for item in runtime.directive_dispositions
        ]
        task_rows = [
            {
                "task_id": item.task_id,
                "state": item.state,
                "parent_obligation_id": item.parent_obligation_id,
                "trigger_evidence_ref": item.trigger_evidence_ref,
            }
            for item in getattr(outcome, "research_tasks", ())
        ]
        print(
            "DAY7_RESULT_AWARE_DIAGNOSTIC="
            + json.dumps(
                {
                    "actions": [
                        prompt.get("ACTION_AVAILABILITY", {})
                        for prompt in llm.prompts
                    ],
                    "preacceptance_turns": runtime.snapshot.preacceptance_turns,
                    "research_turns": runtime.snapshot.research_manager_turns,
                    "manager_turns": runtime.snapshot.manager_turns,
                    "tool_calls": runtime.snapshot.tool_calls,
                    "data_queries": runtime.snapshot.data_queries,
                    "evidence_refs": list(runtime.snapshot.evidence_refs),
                    "inspected_refs": list(runtime.snapshot.inspected_evidence_refs),
                    "directive_dispositions": directive_dispositions,
                    "tasks": task_rows,
                    "observations": list(outcome.observations),
                    "state": runtime.snapshot.state.value,
                    "terminal_status": runtime.snapshot.terminal_status,
                    "run_finished": outcome.run_finished,
                    "verified_complete": outcome.verified_complete,
                },
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
        )
    assert outcome.run_finished is True
    assert outcome.verified_complete is True
    assert service.query_calls == 2
    assert store.n == 2
    assert len(runtime.snapshot.evidence_refs) == 2
    # The first result is disclosed because cognition uses it to derive the bounded
    # branch. The second result completes the accepted analytical work, so loop-boundary
    # CompletionGate must finish before another cognition turn and must not manufacture
    # inspection/disclosure of Evidence the model never saw.
    assert runtime.snapshot.inspected_evidence_refs == (
        runtime.snapshot.evidence_refs[0],
    )
    assert not any(
        item.get("kind") == "fresh_evidence_disclosed"
        and item.get("evidence_ref") == runtime.snapshot.evidence_refs[1]
        for item in outcome.observations
    )

    parent = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    child = next(item for item in runtime.ledger.items if item.obligation_id == "D1")
    assert parent.origin == ObligationOrigin.USER_MUST
    assert parent.status == ObligationStatus.VERIFIED
    assert child.origin == ObligationOrigin.AGENT_DERIVED
    assert child.parent_obligation_id == "U1"
    assert child.capability_key == ManagerCapabilityKey.BREAKDOWN
    assert child.status == ObligationStatus.VERIFIED

    task_ids = [
        item.get("research_task_id")
        for item in outcome.observations
        if item.get("kind") == "tool" and item.get("research_task_id")
    ]
    assert task_ids == ["seed:U1", "D1"]

    # The second decision was grounded in actual bounded first-result content.
    first_inspection_prompt = llm.prompts[1]
    rows = first_inspection_prompt["CURRENT_RESULT_DELTA"]["bounded_payload"]["executions"][0]["rows"]
    assert rows
    assert len(rows) <= 20

    fanout = next(
        item for item in outcome.observations if item.get("kind") == "fanout_registered"
    )
    assert fanout["result"]["classification"] == "UNKNOWN"
    assert fanout["result"]["strategy"] == "CONSERVATIVE_BOUNDED"
    assert fanout["result"]["allowed_children"] == 2
    assert fanout["result"]["selected_task_ids"] == ["D1", "D2"]

    # Fanout registration is cognition-only; one selected READY branch executes.
    # The accepted ADAPT_ON_EVIDENCE directive is lifecycle-accounted by successful
    # branch execution, so deterministic completion requires no fifth cognition turn.
    assert service.query_calls == 2
    assert len(llm.prompts) == 4
    disposition = runtime.directive_disposition("R_ADAPT_U1")
    assert disposition.status == ResearchDirectiveDispositionStatus.APPLIED
    assert disposition.branch_task_refs == ("D1",)
    assert disposition.evidence_ref == runtime.snapshot.evidence_refs[0]
    assert any(
        item.get("kind") == "research_directive_accounted"
        and item.get("task_id") == "D1"
        and item.get("execution_path") == "manager_selected_derived_task"
        for item in outcome.observations
    )
