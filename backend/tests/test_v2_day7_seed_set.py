"""Day7 bounded initial seed-set and multi-obligation Research proof."""

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
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind, TenantAnalyticsRuntimeV0
from app.v2.research_tasks import ResearchTaskRegistry, ResearchTaskService
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _SeedService:
    mdl_version = "mdl-day7-seed-v1"

    def __init__(self) -> None:
        self.query_calls: list[tuple[str, ...]] = []

    def cube_sql(self, cube_query: dict) -> str:
        return "SEED:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        query = json.loads(sql.removeprefix("SEED:"))
        measures = tuple(query.get("measures") or ())
        self.query_calls.append(measures)
        values = {
            "Sales.revenue": 100.0,
            "Sales.orders": 20.0,
            "Sales.discount": 35.0,
        }
        return {
            "columns": list(measures),
            "rows": [{metric: values.get(metric, 1.0) for metric in measures}],
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in measures],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {"id": f"seed-qc-{self.n}", "sealed": True}


class _EvidenceResponsiveLLM:
    """Choose U3 after inspected U1 evidence; never blindly execute registry order."""

    def __init__(self) -> None:
        self.prompts: list[dict] = []

    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)
        verified = set(
            (payload.get("ACCUMULATED_RESEARCH_STATE") or {}).get(
                "verified_user_must_ids"
            )
            or []
        )
        delta = payload.get("CURRENT_RESULT_DELTA")

        if "U1" not in verified:
            return {
                "action": "run_analytics",
                "obligation_ids": ["U1"],
                "metric_handles": ["h1"],
            }
        if (
            delta
            and delta.get("obligation_ids") == ["U1"]
            and not delta.get("inspected")
        ):
            return {
                "action": "inspect_evidence",
                "evidence_ref": delta["evidence_ref"],
            }

        # Inspected U1 result changes the next choice: U3 before U2.
        if "U3" not in verified:
            return {
                "action": "run_analytics",
                "obligation_ids": ["U3"],
                "metric_handles": ["h3"],
            }
        if "U2" not in verified:
            return {
                "action": "run_analytics",
                "obligation_ids": ["U2"],
                "metric_handles": ["h2"],
            }
        return {"action": "finish"}


def _accepted_three_obligation_runtime():
    tenant = "tenant-seed"
    context_version = "ctx-seed-v1"
    message_id = "turn-seed"
    question = "gelir, sipariş ve iskonto metriklerini araştır"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    surfaces = ("gelir", "sipariş", "iskonto")
    refs = tuple(
        spans.mint_exact(message_id=message_id, surface=surface)
        for surface in surfaces
    )

    handles = SemanticHandleRegistry()
    canonicals = ("Sales.revenue", "Sales.orders", "Sales.discount")
    metric_handles = []
    for idx, canonical in enumerate(canonicals, start=1):
        metric_handles.append(
            handles.mint_from_resolver(
                tenant_binding=tenant,
                context_version=context_version,
                resolver_provenance_id=f"seed:metric:{idx}",
                target_kind="metric",
                canonical_target=ResolvedSemanticRef(
                    candidate_id=f"seed-metric-{idx}",
                    target_kind=SemanticTargetKind.METRIC,
                    canonical_name=canonical,
                    cube_names=("Sales",),
                ),
            )
        )

    principal = Principal(
        user_id="seed-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="seed",
    )
    service = _SeedService()
    store = _ContractStore()
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
                tenant_slug="seed",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="seed",
                schema_name="main",
                db_online=True,
            ),
            contract_store=store,
            session_id="seed-session",
        ),
    )

    runtime = ManagerRuntime(request_ref="seed-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="seed-attempt",
        turn_id=message_id,
        request_ref="seed-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=tuple(
            CandidateObligation(
                obligation_id=f"U{idx}",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(refs[idx - 1].source_ref,),
                semantic_handle_refs=(metric_handles[idx - 1].handle_id,),
            )
            for idx in range(1, 4)
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
        service,
        store,
        question,
        message_id,
    )


def test_initial_seed_set_projects_all_three_user_must_without_execution():
    _, runtime, _, service, _, _, _ = _accepted_three_obligation_runtime()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()

    seed = ResearchTaskService().seed_initial_user_must(
        runtime=runtime,
        task_registry=registry,
        executable_task_kinds=runner.declared_task_kinds,
    )

    assert seed.considered_obligation_ids == ("U1", "U2", "U3")
    assert tuple(task.task_id for task in seed.registered_tasks) == (
        "seed:U1",
        "seed:U2",
        "seed:U3",
    )
    assert seed.deferred_obligation_ids == ()
    assert all(task.state == "pending" for task in registry.tasks)
    assert service.query_calls == []
    assert runtime.snapshot.data_queries == 0


def test_multi_obligation_loop_uses_seed_set_but_evidence_changes_next_ready_choice():
    spans, runtime, executor, service, store, question, message_id = (
        _accepted_three_obligation_runtime()
    )
    llm = _EvidenceResponsiveLLM()

    outcome = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
    ).run(
        question=question,
        message_id=message_id,
        request_ref="seed-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.run_finished is True
    assert outcome.verified_complete is True

    seed_observation = next(
        item for item in outcome.observations if item.get("kind") == "seed_tasks_registered"
    )
    assert seed_observation["considered_obligation_ids"] == ["U1", "U2", "U3"]
    assert seed_observation["ready_task_ids"] == ["seed:U1", "seed:U2", "seed:U3"]
    assert seed_observation["deferred_obligation_ids"] == []

    executed = [
        item["research_task_id"]
        for item in outcome.observations
        if item.get("kind") == "tool"
        and item.get("tool") == "run_analytics"
    ]
    assert executed == ["seed:U1", "seed:U3", "seed:U2"]
    assert len(service.query_calls) == 3
    assert store.n == 3

    # U1 evidence was explicitly inspected before it changed the next task choice.
    assert runtime.snapshot.evidence_refs[0] in runtime.snapshot.inspected_evidence_refs
    assert {item.obligation_id for item in runtime.ledger.active_user_must} == {
        "U1",
        "U2",
        "U3",
    }
    assert all(
        item.status.value == "VERIFIED"
        for item in runtime.ledger.active_user_must
    )

    first_prompt = llm.prompts[0]
    assert [item["task_id"] for item in first_prompt["READY_RESEARCH_TASKS"]] == [
        "seed:U1",
        "seed:U2",
        "seed:U3",
    ]
