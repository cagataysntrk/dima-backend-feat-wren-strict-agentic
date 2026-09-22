"""Focused provider-free Day 7 tests for the first ResearchToolContract vertical."""

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
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import (
    EvidenceArtifact,
    ResearchTask,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import (
    ResearchTaskKind,
    ResearchToolContractError,
    ResearchToolRegistry,
    ResearchToolRunner,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _SyntheticService:
    mdl_version = "mdl-day7-research-tool-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "DAY7:" + json.dumps(
            cube_query,
            ensure_ascii=False,
            sort_keys=True,
        )

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        assert sql.startswith("DAY7:")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        query = json.loads(sql.removeprefix("DAY7:"))
        dimensions = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dimensions, *measures]
        rows = [{metric: 42.0 for metric in measures}]
        return {
            "columns": columns,
            "rows": rows,
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in columns],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.rows = []

    def record_v2_minimum(self, **kwargs):
        self.rows.append(kwargs)
        return {
            "id": f"day7-qc-{len(self.rows)}",
            "sealed": True,
        }


def _accepted_query_vertical():
    tenant = "tenant-day7"
    context_version = "ctx-day7-v1"
    message_id = "turn-day7-v1"
    question = "net geliri incele"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface="net geliri")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day7:metric:revenue",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-metric-revenue",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )

    principal = Principal(
        user_id="day7-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="day7",
    )
    service = _SyntheticService()
    contract_store = _ContractStore()
    runtime_identity = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="day7",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=service.mdl_version,
        catalog="day7",
        schema_name="main",
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
            tenant_binding=tenant,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=runtime_identity,
            contract_store=contract_store,
            session_id="day7-session",
        ),
    )
    runtime = ManagerRuntime(request_ref="day7-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="day7-attempt-1",
                    turn_id=message_id,
                    request_ref="day7-request",
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id="U_QUERY",
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
        task_id="RT_QUERY_1",
        question_id="U_QUERY",
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(metric.handle_id,),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U_QUERY",),
            "metric_handles": (metric.handle_id,),
        },
    )
    return principal, service, contract_store, runtime, executor, task, call


def test_first_research_tool_contract_is_closed_and_declarative():
    registry = ResearchToolRegistry()
    spec = registry.spec("wren.query")
    contract = spec.contract

    assert registry.declared_tools == ("wren.query",)
    assert contract.accepted_task_kinds == (ResearchTaskKind.QUERY,)
    assert contract.input_schema == "RunAnalyticsArgs@v1"
    assert contract.output_schema == "ManagerAnalyticsObservation@v1"
    assert contract.required_permissions == ("query:run",)
    assert contract.max_rows == 20
    assert contract.timeout_ms == 15_000


def test_missing_principal_fails_closed_before_any_execution():
    _, service, _, runtime, executor, task, call = _accepted_query_vertical()

    before = service.query_calls
    with pytest.raises(ResearchToolContractError, match="missing principal"):
        ResearchToolRunner().execute(
            task=task,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=None,
        )

    assert service.query_calls == before


def test_task_tool_mismatch_is_rejected_before_execution():
    principal, service, _, runtime, executor, task, call = _accepted_query_vertical()
    wrong = task.model_copy(update={"task_kind": ResearchTaskKind.RELATIONSHIP.value})

    before = service.query_calls
    with pytest.raises(ResearchToolContractError, match="task kind RELATIONSHIP"):
        ResearchToolRunner().execute(
            task=wrong,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
        )

    assert service.query_calls == before


def test_query_rejects_semantic_handle_not_declared_by_task():
    principal, service, _, runtime, executor, task, call = _accepted_query_vertical()
    undeclared = task.model_copy(update={"input_refs": ()})

    before = service.query_calls
    with pytest.raises(
        ResearchToolContractError,
        match="did not declare semantic inputs",
    ):
        ResearchToolRunner().execute(
            task=undeclared,
            tool_id="wren.query",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
        )

    assert service.query_calls == before


def test_query_vertical_uses_official_boundary_and_returns_verified_evidence():
    principal, service, store, runtime, executor, task, call = _accepted_query_vertical()

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
    assert result.evidence.obligation_ids == ("U_QUERY",)
    assert result.evidence.query_contract_refs == ("day7-qc-1",)
    assert result.observation.evidence_ref == result.evidence.artifact_id
    assert result.observation.evidence_verified is True
    assert result.observation.obligations_verified == ("U_QUERY",)
    assert service.query_calls == 1
    assert len(store.rows) == 1

    exposed = result.evidence.payload["executions"][0]
    assert len(tuple(exposed.get("rows") or ())) <= result.contract.max_rows
    assert "Sales.revenue" not in tuple(exposed.get("columns") or ())
