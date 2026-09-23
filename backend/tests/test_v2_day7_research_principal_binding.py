"""Day7 principal-bound Research execution and receipt identity proofs."""

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
    ResearchTask,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tasks import ResearchTaskLifecycleError, ResearchTaskRegistry
from app.v2.research_tools import (
    ResearchTaskKind,
    ResearchToolContractError,
    ResearchToolRunner,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _Service:
    mdl_version = "mdl-principal-binding-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "PRINCIPAL:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        query = json.loads(sql.removeprefix("PRINCIPAL:"))
        measures = list(query.get("measures") or ())
        return {
            "columns": measures,
            "rows": [{metric: 7.0 for metric in measures}],
            "row_count": 1,
            "column_types": ["DOUBLE" for _ in measures],
        }


class _ContractStore:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {"id": f"principal-qc-{self.n}", "sealed": True}


def _fixture(*, canonical_binding: bool = False, use_slug: bool = False):
    tenant = "tenant-principal"
    tenant_slug = "principal"
    runtime_tenant_id = None if use_slug else tenant
    tenant_binding = (
        f"slug:{tenant_slug}"
        if use_slug and canonical_binding
        else f"id:{tenant}"
        if canonical_binding
        else tenant_slug
        if use_slug
        else tenant
    )
    context_version = "ctx-principal-v1"
    message_id = "turn-principal"
    question = "net geliri incele"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface="net geliri")

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant_binding,
        context_version=context_version,
        resolver_provenance_id="principal:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="principal-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )

    service = _Service()
    store = _ContractStore()

    _default = object()

    def principal(
        user_id: str,
        *,
        tenant_id=_default,
        tenant_slug_override: str | None = None,
    ):
        effective_tenant_id = (
            runtime_tenant_id if tenant_id is _default else tenant_id
        )
        return Principal(
            user_id=user_id,
            tenant_id=effective_tenant_id,
            roles=["owner"],
            tenant_slug=tenant_slug_override or tenant_slug,
        )

    def executor(bound_principal: Principal):
        return GovernedManagerExecutor(
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
                principal=bound_principal,
                service=service,
                tenant_runtime=TenantAnalyticsRuntimeV0(
                    tenant_id=runtime_tenant_id,
                    tenant_slug=tenant_slug,
                    principal_user_id=bound_principal.user_id,
                    roles=tuple(bound_principal.roles),
                    mdl_version=service.mdl_version,
                    catalog="principal",
                    schema_name="main",
                    db_online=True,
                ),
                contract_store=store,
                session_id="principal-session",
            ),
        )

    principal_a = principal("user-a")
    executor_a = executor(principal_a)

    runtime = ManagerRuntime(request_ref="principal-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="principal-attempt",
                    turn_id=message_id,
                    request_ref="principal-request",
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
                ).model_dump(mode="json")
            },
        ),
        executor=executor_a,
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
    return {
        "tenant": tenant,
        "tenant_slug": tenant_slug,
        "tenant_binding": tenant_binding,
        "principal": principal,
        "executor": executor,
        "principal_a": principal_a,
        "executor_a": executor_a,
        "service": service,
        "store": store,
        "runtime": runtime,
        "task": task,
        "call": call,
    }


def test_same_runner_and_executor_principal_executes_and_reuses_receipt():
    fx = _fixture()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()

    first = runner.execute(
        task=fx["task"],
        tool_id="wren.query",
        call=fx["call"],
        runtime=fx["runtime"],
        executor=fx["executor_a"],
        principal=fx["principal_a"],
        task_registry=registry,
    )
    second = runner.execute(
        task=fx["task"],
        tool_id="wren.query",
        call=fx["call"],
        runtime=fx["runtime"],
        executor=fx["executor_a"],
        principal=fx["principal_a"],
        task_registry=registry,
    )

    assert first == second
    assert fx["service"].query_calls == 1
    assert fx["store"].n == 1


def test_runtime_boundary_canonical_id_binding_executes_against_typed_runtime_tenant():
    fx = _fixture(canonical_binding=True)

    result = ResearchToolRunner().execute(
        task=fx["task"],
        tool_id="wren.query",
        call=fx["call"],
        runtime=fx["runtime"],
        executor=fx["executor_a"],
        principal=fx["principal_a"],
        task_registry=ResearchTaskRegistry(),
    )

    assert result.evidence.verified is True
    assert fx["tenant_binding"] == f"id:{fx['tenant']}"
    assert fx["service"].query_calls == 1


def test_runtime_boundary_canonical_slug_binding_executes_when_tenant_id_absent():
    fx = _fixture(canonical_binding=True, use_slug=True)

    result = ResearchToolRunner().execute(
        task=fx["task"],
        tool_id="wren.query",
        call=fx["call"],
        runtime=fx["runtime"],
        executor=fx["executor_a"],
        principal=fx["principal_a"],
        task_registry=ResearchTaskRegistry(),
    )

    assert result.evidence.verified is True
    assert fx["principal_a"].tenant_id is None
    assert fx["tenant_binding"] == f"slug:{fx['tenant_slug']}"
    assert fx["service"].query_calls == 1


def test_foreign_slug_principal_denies_against_governed_slug_runtime():
    fx = _fixture(canonical_binding=True, use_slug=True)
    foreign = fx["principal"](
        "user-foreign",
        tenant_id=None,
        tenant_slug_override="foreign-slug",
    )
    foreign_executor = fx["executor"](foreign)

    with pytest.raises(
        ResearchToolContractError,
        match="tenant does not match governed execution tenant",
    ):
        ResearchToolRunner().execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=foreign_executor,
            principal=foreign,
            task_registry=ResearchTaskRegistry(),
        )

    assert fx["service"].query_calls == 0


def test_runner_principal_subject_mismatch_executor_denies_before_db():
    fx = _fixture()
    principal_b = fx["principal"]("user-b")

    with pytest.raises(ResearchToolContractError, match="principal mismatch"):
        ResearchToolRunner().execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=fx["executor_a"],
            principal=principal_b,
            task_registry=ResearchTaskRegistry(),
        )

    assert fx["service"].query_calls == 0


def test_completed_task_as_principal_a_is_not_reused_for_principal_b():
    fx = _fixture()
    registry = ResearchTaskRegistry()
    runner = ResearchToolRunner()

    runner.execute(
        task=fx["task"],
        tool_id="wren.query",
        call=fx["call"],
        runtime=fx["runtime"],
        executor=fx["executor_a"],
        principal=fx["principal_a"],
        task_registry=registry,
    )
    assert fx["service"].query_calls == 1

    principal_b = fx["principal"]("user-b")
    executor_b = fx["executor"](principal_b)
    with pytest.raises(
        ResearchTaskLifecycleError,
        match="completed with different execution identity",
    ):
        runner.execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=executor_b,
            principal=principal_b,
            task_registry=registry,
        )

    assert fx["service"].query_calls == 1
    assert fx["store"].n == 1


def test_missing_runner_principal_denies_before_db():
    fx = _fixture()

    with pytest.raises(ResearchToolContractError, match="missing principal"):
        ResearchToolRunner().execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=fx["executor_a"],
            principal=None,
            task_registry=ResearchTaskRegistry(),
        )

    assert fx["service"].query_calls == 0


def test_foreign_tenant_principal_denies_even_when_runner_matches_executor_subject():
    fx = _fixture()
    foreign = fx["principal"]("user-foreign", tenant_id="tenant-foreign")
    foreign_executor = fx["executor"](foreign)

    with pytest.raises(
        ResearchToolContractError,
        match="tenant does not match governed execution tenant",
    ):
        ResearchToolRunner().execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=foreign_executor,
            principal=foreign,
            task_registry=ResearchTaskRegistry(),
        )

    assert fx["service"].query_calls == 0


def test_executor_missing_principal_denies_before_db():
    fx = _fixture()
    missing_executor = fx["executor"](fx["principal_a"])
    # Deliberate miswire at governed boundary; no full access fingerprint is needed.
    object.__setattr__(missing_executor._context, "principal", None)

    with pytest.raises(
        ResearchToolContractError,
        match="missing governed executor principal",
    ):
        ResearchToolRunner().execute(
            task=fx["task"],
            tool_id="wren.query",
            call=fx["call"],
            runtime=fx["runtime"],
            executor=missing_executor,
            principal=fx["principal_a"],
            task_registry=ResearchTaskRegistry(),
        )

    assert fx["service"].query_calls == 0
