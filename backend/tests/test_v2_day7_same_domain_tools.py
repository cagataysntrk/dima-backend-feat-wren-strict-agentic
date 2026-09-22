"""Day 7 governed same-domain Research tool proofs for COMPARE and RANK."""

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
from app.v2.models import (
    PeriodKind,
    ResearchTask,
    ResearchTaskKind,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tasks import ResearchTaskRegistry, ResearchTaskService
from app.v2.research_tools import (
    ResearchToolContractError,
    ResearchToolRegistry,
    ResearchToolRunner,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _SyntheticGovernedService:
    mdl_version = "mdl-day7-same-domain-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "D7SD:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        cq = json.loads(sql.removeprefix("D7SD:"))
        dimensions = list(cq.get("dimensions") or ())
        measures = list(cq.get("measures") or ())
        columns = [*dimensions, *measures]

        if dimensions:
            metric = measures[0]
            dim = dimensions[0]
            rows = [
                {dim: "A", metric: 120.0},
                {dim: "B", metric: 90.0},
                {dim: "C", metric: 70.0},
            ]
            order = cq.get("order") or {}
            reverse = order.get("direction") == "desc"
            rows = sorted(rows, key=lambda row: row[metric], reverse=reverse)
            rows = rows[: int(cq.get("limit") or len(rows))]
        else:
            # Different deterministic value when a temporal filter is present. The
            # Core validator owns shape/truth checks; this is only a synthetic source.
            filters = tuple(cq.get("filters") or ())
            marker = json.dumps(filters, sort_keys=True)
            value = 120.0 if "2026-09" in marker else 100.0
            rows = [{measures[0]: value}]

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
        self.rows = []

    def record_v2_minimum(self, **kwargs):
        self.rows.append(kwargs)
        return {"id": f"d7-sd-qc-{len(self.rows)}", "sealed": True}


def _base(
    capability: ManagerCapabilityKey,
    *,
    ranking_direction: str | None = None,
    ranking_limit: int | None = None,
):
    tenant = f"tenant-{capability.value}"
    context_version = f"ctx-{capability.value}-v1"
    question = f"{capability.value} governed proof"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(
        message_id=f"turn-{capability.value}",
        text=question,
    )
    source = spans.mint_exact(
        message_id=f"turn-{capability.value}",
        surface=question,
    )

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id=f"{capability.value}:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id=f"{capability.value}-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id=f"{capability.value}:dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id=f"{capability.value}-dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="Sales.region",
            cube_names=("Sales",),
        ),
    )

    semantic_refs = [metric.handle_id]
    comparison = None
    if capability == ManagerCapabilityKey.RANKING:
        semantic_refs.append(dimension.handle_id)
    elif capability == ManagerCapabilityKey.COMPARISON:
        base_period = ResolvedPeriod(
            kind=PeriodKind.THIS_MONTH,
            source_text="bu ay",
            time_dimension="Sales.order_date",
            start="2026-09-01",
            end="2026-09-22",
        )
        comparison = ResolvedComparison(
            mode="previous_period",
            source_text="geçen ayla",
            base_period=base_period,
            reference_period=ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="geçen ayla",
                time_dimension="Sales.order_date",
                start="2026-08-01",
                end="2026-08-31",
            ),
        )
        comparison_handle = handles.mint_from_temporal_engine(
            tenant_binding=tenant,
            context_version=context_version,
            temporal_provenance_id=f"{capability.value}:comparison",
            target_kind="comparison",
            canonical_target=comparison,
        )
        semantic_refs.append(comparison_handle.handle_id)

    principal = Principal(
        user_id=f"user-{capability.value}",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="same-domain",
    )
    service = _SyntheticGovernedService()
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
                tenant_slug="same-domain",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="same-domain",
                schema_name="main",
                db_online=True,
            ),
            contract_store=store,
            session_id=f"session-{capability.value}",
        ),
    )

    runtime = ManagerRuntime(request_ref=f"request-{capability.value}")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id=f"attempt-{capability.value}",
        turn_id=f"turn-{capability.value}",
        request_ref=f"request-{capability.value}",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U1",
                capability_key=capability,
                origin=ObligationOrigin.USER_MUST,
                source_refs=(source.source_ref,),
                semantic_handle_refs=tuple(semantic_refs),
                ranking_direction=ranking_direction,
                ranking_limit=ranking_limit,
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
    return {
        "handles": handles,
        "metric": metric,
        "dimension": dimension,
        "comparison": comparison,
        "comparison_handle": semantic_refs[-1] if comparison is not None else None,
        "principal": principal,
        "service": service,
        "store": store,
        "executor": executor,
        "runtime": runtime,
    }


def test_compare_contract_requires_governed_comparison_handle():
    task = ResearchTask(
        task_id="T-CMP",
        question_id="U1",
        task_kind=ResearchTaskKind.COMPARE.value,
        input_refs=("sem_metric",),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": ("sem_metric",),
        },
    )
    principal = Principal(user_id="u", tenant_id="t", roles=["owner"])
    with pytest.raises(ResearchToolContractError, match="comparison handle"):
        ResearchToolRegistry().validate_invocation(
            task=task,
            tool_id="wren.compare",
            call=call,
            principal=principal,
        )


def test_rank_contract_requires_dimension_direction_and_limit():
    task = ResearchTask(
        task_id="T-RANK",
        question_id="U1",
        task_kind=ResearchTaskKind.RANK.value,
        input_refs=("sem_metric",),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": ("sem_metric",),
        },
    )
    principal = Principal(user_id="u", tenant_id="t", roles=["owner"])
    with pytest.raises(ResearchToolContractError, match="dimension .* direction .* limit"):
        ResearchToolRegistry().validate_invocation(
            task=task,
            tool_id="wren.rank",
            call=call,
            principal=principal,
        )


def test_compare_executes_two_governed_queries_and_verifies_evidence():
    ctx = _base(ManagerCapabilityKey.COMPARISON)
    task = ResearchTaskService().seed_for_obligation(
        runtime=ctx["runtime"],
        obligation_id="U1",
        task_id="T-CMP",
    )
    assert task.task_kind == ResearchTaskKind.COMPARE.value

    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": (ctx["metric"].handle_id,),
            "comparison_handle": ctx["comparison_handle"],
        },
    )
    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.compare",
        call=call,
        runtime=ctx["runtime"],
        executor=ctx["executor"],
        principal=ctx["principal"],
        task_registry=ResearchTaskRegistry(),
    )

    assert result.evidence.verified is True
    assert result.observation.obligations_verified == ("U1",)
    assert result.observation.query_count == 2
    assert ctx["service"].query_calls == 2
    assert len(ctx["store"].rows) == 2
    assert len(result.evidence.query_contract_refs) == 2
    assert [x["role"] for x in result.evidence.payload["executions"]] == [
        "primary",
        "comparison_reference",
    ]

    # Regression proof for the temporal contract bug: primary MUST use comparison.base_period.
    primary_cq = ctx["store"].rows[0]["cube_query"]
    reference_cq = ctx["store"].rows[1]["cube_query"]
    assert primary_cq["filters"]
    assert reference_cq["filters"]
    assert primary_cq["filters"] != reference_cq["filters"]

    obligation = next(x for x in ctx["runtime"].ledger.items if x.obligation_id == "U1")
    assert obligation.status == ObligationStatus.VERIFIED


def test_rank_executes_governed_top_n_and_verifies_evidence():
    ctx = _base(
        ManagerCapabilityKey.RANKING,
        ranking_direction="desc",
        ranking_limit=2,
    )
    task = ResearchTaskService().seed_for_obligation(
        runtime=ctx["runtime"],
        obligation_id="U1",
        task_id="T-RANK",
    )
    assert task.task_kind == ResearchTaskKind.RANK.value

    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": (ctx["metric"].handle_id,),
            "dimension_handles": (ctx["dimension"].handle_id,),
            "ranking_direction": "desc",
            "limit": 2,
        },
    )
    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.rank",
        call=call,
        runtime=ctx["runtime"],
        executor=ctx["executor"],
        principal=ctx["principal"],
        task_registry=ResearchTaskRegistry(),
    )

    assert result.evidence.verified is True
    assert result.observation.obligations_verified == ("U1",)
    assert result.observation.query_count == 1
    assert ctx["service"].query_calls == 1
    assert len(ctx["store"].rows) == 1

    rows = result.evidence.payload["executions"][0]["rows"]
    assert len(rows) == 2
    metric_key = ctx["metric"].handle_id
    assert rows[0][metric_key] >= rows[1][metric_key]

    obligation = next(x for x in ctx["runtime"].ledger.items if x.obligation_id == "U1")
    assert obligation.status == ObligationStatus.VERIFIED
