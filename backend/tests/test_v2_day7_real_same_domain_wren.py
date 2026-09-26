"""Day7 real-Wren sentinels for governed COMPARE and RANK Research tools."""

from __future__ import annotations

import json

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
    PeriodKind,
    ResolvedComparison,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tasks import ResearchTaskRegistry, ResearchTaskService
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _CountingWren:
    def __init__(self, wren) -> None:
        self._wren = wren
        self.mdl_version = wren.mdl_version
        self.query_calls = 0

    def cube_sql(self, cube_query: dict):
        return self._wren.cube_sql(cube_query)

    def dry_plan(self, sql: str, *, principal=None):
        return self._wren.dry_plan(sql, principal=principal)

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        return self._wren.query(sql, limit=limit, principal=principal)


def _base_real(
    *,
    capability: ManagerCapabilityKey,
    wren,
    schema: dict,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())
    assert "ariza_tipi" in tuple(cube.get("dimensions") or ())
    assert "tarih" in tuple(cube.get("time_dimensions") or ())

    tenant = f"day7-real-{capability.value}"
    context_version = f"ctx-day7-real-{capability.value}-v1"
    turn_id = f"turn-day7-real-{capability.value}"
    question = f"bakım {capability.value} gerçek Wren kanıtı"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=turn_id, text=question)
    source = spans.mint_exact(message_id=turn_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id=f"real-{capability.value}:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id=f"real-{capability.value}-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )
    dimension = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id=f"real-{capability.value}:dimension",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id=f"real-{capability.value}-dimension",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="ariza_tipi",
            cube_names=("bakim",),
        ),
    )

    semantic_refs = [metric.handle_id]
    comparison_handle = None
    ranking_direction = None
    ranking_limit = None

    if capability == ManagerCapabilityKey.COMPARISON:
        comparison = ResolvedComparison(
            mode="previous_period",
            source_text="Şubat 2024 ile Ocak 2024",
            base_period=ResolvedPeriod(
                kind=PeriodKind.THIS_MONTH,
                source_text="Şubat 2024",
                time_dimension="tarih",
                start="2024-02-01",
                end="2024-02-29",
            ),
            reference_period=ResolvedPeriod(
                kind=PeriodKind.PREVIOUS_MONTH,
                source_text="Ocak 2024",
                time_dimension="tarih",
                start="2024-01-01",
                end="2024-01-31",
            ),
        )
        comparison_handle = handles.mint_from_temporal_engine(
            tenant_binding=tenant,
            context_version=context_version,
            temporal_provenance_id=f"real-{capability.value}:comparison",
            target_kind="comparison",
            canonical_target=comparison,
        )
        semantic_refs.append(comparison_handle.handle_id)
    elif capability == ManagerCapabilityKey.RANKING:
        semantic_refs.append(dimension.handle_id)
        ranking_direction = "desc"
        ranking_limit = 3

    principal = Principal(
        user_id=f"day7-real-{capability.value}-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    service = _CountingWren(wren)

    persisted_rows = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_rows.append(row),
    )
    contract_store = contracts_module.ContractStore()

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
            tenant_runtime=TenantAnalyticsRuntimeV0(
                tenant_id=tenant,
                tenant_slug="demo-boyahane",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=wren.mdl_version,
                catalog=str(schema.get("catalog") or "wren"),
                schema_name=str(
                    schema.get("schema_name")
                    or schema.get("schema")
                    or "public"
                ),
                db_online=True,
            ),
            contract_store=contract_store,
            session_id=f"day7-real-{capability.value}-session",
        ),
    )

    runtime = ManagerRuntime(request_ref=f"day7-real-{capability.value}-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id=f"day7-real-{capability.value}-attempt",
                    turn_id=turn_id,
                    request_ref=f"day7-real-{capability.value}-request",
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
                ).model_dump(mode="json")
            },
        ),
        executor=executor,
    )
    return {
        "metric": metric,
        "dimension": dimension,
        "comparison_handle": comparison_handle,
        "principal": principal,
        "service": service,
        "persisted": persisted_rows,
        "runtime": runtime,
        "executor": executor,
    }


def test_real_wren_compare_executes_base_and_reference_and_seals_both_contracts(
    wren,
    schema,
    monkeypatch,
):
    ctx = _base_real(
        capability=ManagerCapabilityKey.COMPARISON,
        wren=wren,
        schema=schema,
        monkeypatch=monkeypatch,
    )
    task = ResearchTaskService().seed_for_obligation(
        runtime=ctx["runtime"],
        obligation_id="U1",
        task_id="REAL-COMPARE",
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": (ctx["metric"].handle_id,),
            "comparison_handle": ctx["comparison_handle"].handle_id,
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
    assert result.observation.query_count == 2
    assert result.observation.obligations_verified == ("U1",)
    assert ctx["service"].query_calls == 2
    assert len(ctx["persisted"]) == 2
    assert len(result.evidence.query_contract_refs) == 2
    assert [item["role"] for item in result.evidence.payload["executions"]] == [
        "primary",
        "comparison_reference",
    ]

    primary = ctx["persisted"][0].cube_query_json
    reference = ctx["persisted"][1].cube_query_json
    if isinstance(primary, str):
        primary = json.loads(primary)
    if isinstance(reference, str):
        reference = json.loads(reference)
    assert primary["filters"] != reference["filters"]
    assert any(item.get("value") == "2024-02-01" for item in primary["filters"])
    assert any(item.get("value") == "2024-01-01" for item in reference["filters"])

    obligation = next(
        item for item in ctx["runtime"].ledger.items if item.obligation_id == "U1"
    )
    assert obligation.status == ObligationStatus.VERIFIED


def test_real_wren_rank_executes_verified_top_n(
    wren,
    schema,
    monkeypatch,
):
    ctx = _base_real(
        capability=ManagerCapabilityKey.RANKING,
        wren=wren,
        schema=schema,
        monkeypatch=monkeypatch,
    )
    task = ResearchTaskService().seed_for_obligation(
        runtime=ctx["runtime"],
        obligation_id="U1",
        task_id="REAL-RANK",
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_ANALYTICS,
        args={
            "obligation_ids": ("U1",),
            "metric_handles": (ctx["metric"].handle_id,),
            "dimension_handles": (ctx["dimension"].handle_id,),
            "ranking_direction": "desc",
            "limit": 3,
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
    assert result.observation.query_count == 1
    assert result.observation.obligations_verified == ("U1",)
    assert ctx["service"].query_calls == 1
    assert len(ctx["persisted"]) == 1
    assert len(result.evidence.query_contract_refs) == 1

    rows = tuple(result.evidence.payload["executions"][0]["rows"])
    assert len(rows) <= 3
    values = [
        row[ctx["metric"].handle_id]
        for row in rows
        if isinstance(row.get(ctx["metric"].handle_id), (int, float))
    ]
    assert all(left >= right for left, right in zip(values, values[1:]))

    obligation = next(
        item for item in ctx["runtime"].ledger.items if item.obligation_id == "U1"
    )
    assert obligation.status == ObligationStatus.VERIFIED
