"""D7-A2 execution-path proofs: registry idempotency and cancel/late-result safety."""

from __future__ import annotations

import json

import pytest

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
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind, ResearchTask, TenantAnalyticsRuntimeV0
from app.v2.research_tasks import (
    ResearchTaskLifecycleError,
    ResearchTaskRegistry,
    ResearchTaskTimeoutError,
)
from app.v2.research_tools import ResearchTaskKind, ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _Service:
    mdl_version = "mdl-d7-a2-v1"

    def __init__(self) -> None:
        self.query_calls = 0
        self.on_query = None

    def cube_sql(self, cube_query: dict) -> str:
        return "D7A2:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        if self.on_query is not None:
            self.on_query()
        query = json.loads(sql.removeprefix("D7A2:"))
        measures = list(query.get("measures") or ())
        return {
            "columns": measures,
            "rows": [{metric: 42.0 for metric in measures}],
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in measures],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {"id": f"d7-a2-qc-{self.n}", "sealed": True}


def _vertical():
    tenant = "d7-a2-tenant"
    context_version = "ctx-d7-a2-v1"
    question = "net geliri incele"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id="d7-a2-turn", text=question)
    source = spans.mint_exact(message_id="d7-a2-turn", surface="net geliri")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="d7-a2:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="d7-a2-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    principal = Principal(
        user_id="d7-a2-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="d7-a2",
    )
    service = _Service()
    store = _ContractStore()
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(source_spans=spans, semantic_handles=handles),
        core_analytics=ManagerCoreAnalyticsAdapter(semantic_handles=handles),
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=TenantAnalyticsRuntimeV0(
                tenant_id=tenant,
                tenant_slug="d7-a2",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="d7-a2",
                schema_name="main",
                db_online=True,
            ),
            contract_store=store,
            session_id="d7-a2-session",
        ),
    )
    runtime = ManagerRuntime(request_ref="d7-a2-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="d7-a2-attempt",
        turn_id="d7-a2-turn",
        request_ref="d7-a2-request",
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
    task = ResearchTask(
        task_id="seed:U1",
        question_id="U1",
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(metric.handle_id,),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": (metric.handle_id,),
        },
    )
    return principal, service, store, runtime, executor, task, call


def test_duplicate_delivery_reuses_registry_receipt_and_executes_wren_once():
    principal, service, store, runtime, executor, task, call = _vertical()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()

    first = runner.execute(
        task=task,
        tool_id="wren.query",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    second = runner.execute(
        task=task,
        tool_id="wren.query",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )

    assert first == second
    assert service.query_calls == 1
    assert store.n == 1
    assert runtime.snapshot.data_queries == 1
    assert registry.get(task.task_id).state == "complete"


def test_cancel_during_query_discards_late_result_before_evidence_or_verification_commit():
    principal, service, store, runtime, executor, task, call = _vertical()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()
    service.on_query = lambda: registry.cancel(task.task_id)

    with pytest.raises(ResearchTaskLifecycleError, match="cancelled|late completion"):
        runner.execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
        )

    assert service.query_calls == 1
    assert store.n == 1  # QueryContract may be sealed; it is not accepted Evidence.
    assert registry.get(task.task_id).state == "cancelled"
    assert runtime.snapshot.evidence_refs == ()

    obligation = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    assert obligation.status != ObligationStatus.VERIFIED
    assert obligation.evidence_refs == ()



class _FakeClock:
    def __init__(self, value: float = 100.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_deadline_rejects_late_result_before_accepted_evidence_or_uol_verification():
    principal, service, store, runtime, executor, task, call = _vertical()
    clock = _FakeClock()
    registry = ResearchTaskRegistry(clock=clock)
    runner = ResearchToolRunner()
    service.on_query = lambda: clock.advance(15.001)

    with pytest.raises(ResearchTaskTimeoutError, match="deadline exceeded"):
        runner.execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
        )

    # Low-level query/QueryContract may finish for audit, but Research truth must not.
    assert service.query_calls == 1
    assert store.n == 1
    assert executor.evidence_store.count == 0
    assert runtime.snapshot.evidence_refs == ()
    assert registry.get(task.task_id).state == "failed"

    obligation = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    assert obligation.status != ObligationStatus.VERIFIED
    assert obligation.evidence_refs == ()


def test_timeout_is_terminal_for_duplicate_delivery_and_retry_without_second_query():
    principal, service, _, runtime, executor, task, call = _vertical()
    clock = _FakeClock()
    registry = ResearchTaskRegistry(clock=clock)
    runner = ResearchToolRunner()
    service.on_query = lambda: clock.advance(16.0)

    with pytest.raises(ResearchTaskTimeoutError):
        runner.execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
        )
    assert service.query_calls == 1

    service.on_query = None
    with pytest.raises(ResearchTaskLifecycleError, match="failed ResearchTask"):
        runner.execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
        )

    assert service.query_calls == 1
    assert executor.evidence_store.count == 0


def test_cancel_vs_timeout_race_remains_terminal_and_discards_result():
    principal, service, _, runtime, executor, task, call = _vertical()
    clock = _FakeClock()
    registry = ResearchTaskRegistry(clock=clock)
    runner = ResearchToolRunner()

    def _cancel_and_expire():
        registry.cancel(task.task_id)
        clock.advance(16.0)

    service.on_query = _cancel_and_expire

    with pytest.raises(ResearchTaskLifecycleError, match="cancelled|late completion"):
        runner.execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
        )

    assert registry.get(task.task_id).state == "cancelled"
    assert executor.evidence_store.count == 0
    assert runtime.snapshot.evidence_refs == ()
    obligation = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    assert obligation.status != ObligationStatus.VERIFIED


def test_success_just_before_deadline_commits_once_and_completes():
    principal, service, store, runtime, executor, task, call = _vertical()
    clock = _FakeClock()
    registry = ResearchTaskRegistry(clock=clock)
    runner = ResearchToolRunner()
    service.on_query = lambda: clock.advance(14.999)

    result = runner.execute(
        task=task,
        tool_id="wren.query",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )

    assert service.query_calls == 1
    assert store.n == 1
    assert executor.evidence_store.count == 1
    assert result.evidence.artifact_id in runtime.snapshot.evidence_refs
    assert registry.get(task.task_id).state == "complete"
    assert result.elapsed_ms == pytest.approx(14_999.0)

    obligation = next(item for item in runtime.ledger.items if item.obligation_id == "U1")
    assert obligation.status == ObligationStatus.VERIFIED
