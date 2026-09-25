"""Day7 real governed RELATIONSHIP vertical: positive + fail-closed negative."""

from __future__ import annotations

import copy
import json

import pytest

from app import contracts as contracts_module
from app import fanout
from app.wren_service import WrenService
from app.v2.acceptance import IntentAcceptanceGate
from app.v2.cross_domain_facts import CrossDomainJoinFactBuilder
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
    ResearchTask,
    ResearchTaskKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.relationship_adapter import (
    GovernedRelationshipAdapter,
    GovernedRelationshipExecutionContext,
)
from app.v2.research_tasks import ResearchTaskLifecycleError, ResearchTaskRegistry
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _CertifiedService:
    """Proxy real Wren while exposing an exact-current measured schema proof."""

    def __init__(self, wren, schema: dict) -> None:
        self._wren = wren
        self._schema = schema
        self.mdl_version = wren.mdl_version
        self.query_calls = 0

    def schema(self):
        return copy.deepcopy(self._schema)

    def cube_sql(self, cube_query: dict):
        return self._wren.cube_sql(cube_query)

    def dry_plan(self, sql: str, *, principal=None):
        return self._wren.dry_plan(sql, principal=principal)

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        return self._wren.query(sql, limit=limit, principal=principal)


def _current_certified_schema(wren):
    schema = copy.deepcopy(wren.schema())
    relationship = next(
        item
        for item in schema["relationships"]
        if item.get("name") == "makine_duruslari_makineler"
    )

    raw_mdl = json.loads(wren._mdl_bytes())
    physical = {
        model.get("name"): WrenService._physical_name(model)
        for model in raw_mdl.get("models", [])
        if model.get("name")
    }
    cert = fanout.certify(
        [relationship],
        fanout.konnektor_sorgu(wren),
        tablolar=set(physical),
        nitelikli=lambda name: physical.get(name, f"main.{name}"),
        mdl_version=wren.mdl_version,
    )
    proof = fanout.kanit(
        cert,
        relationship["name"],
        current_mdl_version=wren.mdl_version,
    )
    assert proof["status"] == "HEALTHY", proof
    relationship["certified"] = proof["certified"]
    relationship["fanout_proof"] = proof

    # The relationship-derived bolum dimension must remain tied to exactly the same
    # relationship provenance; this is analytical target grain, not target PK.
    cube = next(
        item for item in schema["cubes"]
        if item.get("name") == "makine_duruslari"
    )
    origin = cube["dimension_origin"]["bolum"]
    assert origin["relationship"] == relationship["name"]
    assert origin["model"] == "makineler"
    assert origin["column"] == "bolum"
    return schema


def _accepted_relationship_runtime(wren, schema, monkeypatch, *, multi_metric=False):
    tenant = "day7-rel-tenant"
    context_version = "ctx-day7-rel-v1"
    message_id = "day7-rel-turn"
    question = (
        "duruş süresini ve duruş sayısını makine bölümü ile ilişkilendir"
        if multi_metric
        else "duruş süresini makine bölümü ile ilişkilendir"
    )

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    metric_source = spans.mint_exact(
        message_id=message_id,
        surface="duruş süresini",
    )
    dim_source = spans.mint_exact(
        message_id=message_id,
        surface="makine bölümü",
    )
    second_metric_source = (
        spans.mint_exact(
            message_id=message_id,
            surface="duruş sayısını",
        )
        if multi_metric
        else None
    )

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day7-rel:duration",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-rel-duration",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="toplam_sure_dk",
            cube_names=("makine_duruslari",),
        ),
    )
    second_metric = (
        handles.mint_from_resolver(
            tenant_binding=tenant,
            context_version=context_version,
            resolver_provenance_id="day7-rel:count",
            target_kind="metric",
            canonical_target=ResolvedSemanticRef(
                candidate_id="day7-rel-count",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name="duruş_sayisi",
                cube_names=("makine_duruslari",),
            ),
        )
        if multi_metric
        else None
    )
    department = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day7-rel:department",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day7-rel-department",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name="bolum",
            cube_names=("makine_duruslari",),
        ),
    )

    principal = Principal(
        user_id="day7-rel-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    service = _CertifiedService(wren, schema)

    persisted_rows = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_rows.append(row),
    )
    contract_store = contracts_module.ContractStore()
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="demo-boyahane",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or "public"),
        db_online=True,
    )
    core = ManagerCoreAnalyticsAdapter(semantic_handles=handles)
    fact_builder = CrossDomainJoinFactBuilder(
        semantic_handles=handles,
        tenant_binding=tenant,
        context_version=context_version,
    )
    relationship_adapter = GovernedRelationshipAdapter(
        fact_builder=fact_builder,
        core_analytics=core,
        context=GovernedRelationshipExecutionContext(
            tenant_binding=tenant,
            principal=principal,
            service=service,
            tenant_runtime=tenant_runtime,
            contract_store=contract_store,
            session_id="day7-rel-session",
        ),
    )
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=spans,
            semantic_handles=handles,
        ),
        core_analytics=core,
        context=GovernedManagerExecutionContext(
            tenant_binding=tenant,
            context_version=context_version,
            principal=principal,
            service=service,
            tenant_runtime=tenant_runtime,
            contract_store=contract_store,
            session_id="day7-rel-session",
        ),
        relationship=relationship_adapter,
    )

    runtime = ManagerRuntime(request_ref="day7-rel-request")
    runtime.begin_understanding()
    envelope = UserIntentEnvelope(
        attempt_id="day7-rel-attempt",
        turn_id=message_id,
        request_ref="day7-rel-request",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="U_REL",
                capability_key=ManagerCapabilityKey.RELATIONSHIP,
                origin=ObligationOrigin.USER_MUST,
                source_refs=tuple(
                    ref
                    for ref in (
                        metric_source.source_ref,
                        (
                            second_metric_source.source_ref
                            if second_metric_source is not None
                            else None
                        ),
                        dim_source.source_ref,
                    )
                    if ref is not None
                ),
                semantic_handle_refs=tuple(
                    handle_id
                    for handle_id in (
                        metric.handle_id,
                        (
                            second_metric.handle_id
                            if second_metric is not None
                            else None
                        ),
                        department.handle_id,
                    )
                    if handle_id is not None
                ),
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
        task_id="seed:U_REL",
        question_id="U_REL",
        task_kind=ResearchTaskKind.RELATIONSHIP.value,
        input_refs=tuple(
            handle_id
            for handle_id in (
                metric.handle_id,
                second_metric.handle_id if second_metric is not None else None,
                department.handle_id,
            )
            if handle_id is not None
        ),
    )
    call = ManagerToolCall(
        name=ManagerToolName.RUN_RELATIONSHIP,
        args={
            "obligation_id": "U_REL",
            "focus_handles": tuple(
                handle_id
                for handle_id in (
                    metric.handle_id,
                    second_metric.handle_id if second_metric is not None else None,
                )
                if handle_id is not None
            ),
            "counterpart_handles": (department.handle_id,),
        },
    )
    return (
        principal,
        service,
        persisted_rows,
        runtime,
        executor,
        task,
        call,
    )


def test_real_wren_relationship_vertical_is_governed_and_evidence_producing(
    wren,
    monkeypatch,
):
    schema = _current_certified_schema(wren)
    principal, service, persisted, runtime, executor, task, call = (
        _accepted_relationship_runtime(wren, schema, monkeypatch)
    )
    registry = ResearchTaskRegistry()
    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.relationship",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )

    assert service.query_calls == 1
    assert result.task.state == "complete"
    assert result.evidence.verified is True
    assert result.evidence.evidence_kind == "relationship_analytics"
    assert result.evidence.task_id == task.task_id
    assert result.evidence.query_contract_refs
    assert result.observation.status == "EXECUTED"
    assert result.observation.evidence_ref == result.evidence.artifact_id

    obligation = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REL"
    )
    assert obligation.status == ObligationStatus.VERIFIED
    assert obligation.evidence_refs == (result.evidence.artifact_id,)

    exposed = result.evidence.payload["executions"][0]
    assert len(tuple(exposed.get("rows") or ())) <= result.contract.max_rows
    assert set(exposed["columns"]) == set(task.input_refs)

    assert len(persisted) == 1
    provenance = json.loads(persisted[0].provenance_json)
    extension = provenance["v2_manager"]["governed_extension"]
    assert extension["kind"] == "cross_domain_relationship"
    facts = extension["facts"]
    assert facts["source_model"] == "makine_duruslari"
    assert facts["target_model"] == "makineler"
    assert facts["source_row_grain"] == "id"
    assert facts["target_row_grain"] == "makine"
    assert facts["target_analysis_grain"] == "bolum"
    assert facts["requested_output_grain"] == "bolum"
    assert facts["relationship_path"] == ["makine_duruslari_makineler"]
    assert extension["gate_decision"]["allowed"] is True


def test_real_wren_relationship_supports_multiple_governed_metrics_against_one_dimension(
    wren,
    monkeypatch,
):
    schema = _current_certified_schema(wren)
    principal, service, persisted, runtime, executor, task, call = (
        _accepted_relationship_runtime(
            wren,
            schema,
            monkeypatch,
            multi_metric=True,
        )
    )
    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.relationship",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=ResearchTaskRegistry(),
    )

    assert service.query_calls == 1
    assert result.evidence.verified is True
    assert result.observation.status == "EXECUTED"
    exposed = result.evidence.payload["executions"][0]
    assert set(exposed["columns"]) == set(task.input_refs)

    provenance = json.loads(persisted[0].provenance_json)["v2_manager"][
        "governed_extension"
    ]
    assert len(provenance["pair_facts"]) == 2
    assert len(provenance["pair_gate_decisions"]) == 2
    assert all(item["allowed"] is True for item in provenance["pair_gate_decisions"])
    assert {
        item["source_metric_handle"] for item in provenance["pair_facts"]
    } == set(call.args["focus_handles"])
    assert {
        item["target_dimension_handle"] for item in provenance["pair_facts"]
    } == set(call.args["counterpart_handles"])


def test_stale_fanout_proof_causes_zero_relationship_execution(
    wren,
    monkeypatch,
):
    schema = _current_certified_schema(wren)
    relationship = next(
        item
        for item in schema["relationships"]
        if item.get("name") == "makine_duruslari_makineler"
    )
    relationship["fanout_proof"] = {
        **relationship["fanout_proof"],
        "status": "MDL_MISMATCH",
        "certified": "olculmedi",
        "certificate_mdl_version": "stale-mdl",
    }
    relationship["certified"] = "olculmedi"

    principal, service, _, runtime, executor, task, call = (
        _accepted_relationship_runtime(wren, schema, monkeypatch)
    )
    observation = runtime.call_tool(call, executor=executor).tool_result

    assert observation.available is False
    assert observation.status == "UNSUPPORTED"
    assert service.query_calls == 0
    assert executor.evidence_store.count == 0
    assert runtime.snapshot.evidence_refs == ()

    obligation = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REL"
    )
    assert obligation.status == ObligationStatus.BLOCKED_DATA_GAP
    assert obligation.evidence_refs == ()


def test_stale_fanout_runner_returns_blocked_terminal_without_fake_evidence(
    wren,
    monkeypatch,
):
    schema = _current_certified_schema(wren)
    relationship = next(
        item
        for item in schema["relationships"]
        if item.get("name") == "makine_duruslari_makineler"
    )
    relationship["fanout_proof"] = {
        **relationship["fanout_proof"],
        "status": "MDL_MISMATCH",
        "certified": "olculmedi",
        "certificate_mdl_version": "stale-mdl",
    }
    relationship["certified"] = "olculmedi"

    principal, service, _, runtime, executor, task, call = (
        _accepted_relationship_runtime(wren, schema, monkeypatch)
    )
    registry = ResearchTaskRegistry()

    result = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.relationship",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )

    assert result.task.state == "blocked"
    assert result.evidence is None
    assert result.observation.available is False
    assert result.observation.status == "UNSUPPORTED"
    assert registry.get(task.task_id).state == "blocked"
    assert service.query_calls == 0
    assert executor.evidence_store.count == 0
    assert runtime.snapshot.evidence_refs == ()

    obligation = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REL"
    )
    assert obligation.status == ObligationStatus.BLOCKED_DATA_GAP
    assert obligation.evidence_refs == ()

    # Duplicate delivery is idempotent and cannot re-enter the governed executor.
    again = ResearchToolRunner().execute(
        task=task,
        tool_id="wren.relationship",
        call=call,
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert again is result
    assert service.query_calls == 0


def test_cancelled_relationship_cannot_commit_blocked_ledger_state(
    wren,
    monkeypatch,
):
    schema = _current_certified_schema(wren)
    relationship = next(
        item
        for item in schema["relationships"]
        if item.get("name") == "makine_duruslari_makineler"
    )
    relationship["fanout_proof"] = {
        **relationship["fanout_proof"],
        "status": "MDL_MISMATCH",
        "certified": "olculmedi",
        "certificate_mdl_version": "stale-mdl",
    }
    relationship["certified"] = "olculmedi"

    principal, service, _, runtime, executor, task, call = (
        _accepted_relationship_runtime(wren, schema, monkeypatch)
    )
    registry = ResearchTaskRegistry()

    with pytest.raises(ResearchTaskLifecycleError, match="cancelled"):
        ResearchToolRunner().execute(
            task=task,
            tool_id="wren.relationship",
            call=call,
            runtime=runtime,
            executor=executor,
            principal=principal,
            task_registry=registry,
            cancel_check=lambda: True,
        )

    assert registry.get(task.task_id).state == "cancelled"
    assert service.query_calls == 0
    assert executor.evidence_store.count == 0
    assert runtime.snapshot.evidence_refs == ()

    obligation = next(
        item for item in runtime.ledger.items
        if item.obligation_id == "U_REL"
    )
    assert obligation.status in {
        ObligationStatus.ACCEPTED,
        ObligationStatus.READY,
        ObligationStatus.IN_PROGRESS,
    }
    assert obligation.evidence_refs == ()
