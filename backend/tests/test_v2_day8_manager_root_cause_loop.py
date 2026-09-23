"""Provider-free Day8-C Manager-loop wiring proof.

The root-cause layer is opt-in. This test exercises deterministic bootstrap plus all
three Day8 cognition actions without changing UOL completion semantics.
"""

from __future__ import annotations

import json

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import (
    ResearchManagerLoop,
    _post_acceptance_native_schema,
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
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.root_cause_orchestration import RootCauseLoopContext
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal


class _Service:
    mdl_version = "mdl-day8-loop-v1"

    def __init__(self) -> None:
        self.query_calls = 0

    def cube_sql(self, cube_query: dict) -> str:
        return "D8LOOP:" + json.dumps(cube_query, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        assert principal is not None
        self.query_calls += 1
        query = json.loads(sql.removeprefix("D8LOOP:"))
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
        return {"id": f"d8-loop-qc-{self.n}", "sealed": True}


class _RootCauseFakeLLM:
    """Deterministic script over typed runtime state only."""

    def __init__(self) -> None:
        self.prompts = []

    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        self.prompts.append(payload)
        ready = payload.get("READY_RESEARCH_TASKS") or []
        evidence_refs = payload.get("EVIDENCE_REFS") or []
        ledgers = payload.get("HYPOTHESIS_LEDGERS") or []
        entries = ledgers[0]["entries"] if ledgers else []

        if not evidence_refs:
            assert len(ready) == 1
            assert ready[0]["task_kind"] == "QUERY"
            return {
                "action": "run_analytics",
                "obligation_ids": ["U_ROOT"],
                "metric_handles": ["h1"],
            }

        latest = payload.get("CURRENT_RESULT_DELTA")
        if latest and not latest.get("inspected"):
            return {
                "action": "inspect_evidence",
                "evidence_ref": latest["evidence_ref"],
            }

        if not entries:
            return {
                "action": "propose_hypothesis",
                "hypothesis_parent_obligation_id": "U_ROOT",
                "hypothesis_statement": "Aday açıklama gözlemsel olarak sınanmalıdır.",
                "hypothesis_semantic_handles": ["h1"],
                "hypothesis_trigger_evidence_refs": [evidence_refs[0]],
                "hypothesis_limitations": ["Gözlemsel kanıt nedenselliği doğrulamaz."],
            }

        hypothesis = entries[0]
        if not hypothesis.get("next_test_task_refs"):
            return {
                "action": "propose_hypothesis_next_test",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": ["h1"],
                "next_test_trigger_evidence_ref": evidence_refs[0],
                "next_test_material_reason": "Aday açıklamayı bir gözlemsel tekrar ölçümle sınırla.",
            }

        if not hypothesis.get("evidence_links"):
            return {
                "action": "propose_hypothesis_evidence_relation",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "hypothesis_relation_evidence_ref": evidence_refs[0],
                "hypothesis_relation": "SUPPORTS",
            }

        return {
            "action": "request_clarification",
            "obligation_ids": ["U_ROOT"],
            "clarification_reason": (
                "Day8 ROOT_CAUSE completion truth is intentionally not auto-promoted "
                "from observational support."
            ),
        }


def _accepted_root_runtime():
    tenant = "day8-loop-tenant"
    context_version = "ctx-day8-loop-v1"
    message_id = "day8-loop-turn"
    question = "net gelirin nedenini araştır"

    spans = SourceSpanRegistry()
    source_hash = spans.register_message(message_id=message_id, text=question)
    source = spans.mint_exact(message_id=message_id, surface=question)

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context_version,
        resolver_provenance_id="day8-loop:metric",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day8-loop-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.revenue",
            cube_names=("Sales",),
        ),
        parent_obligation_id="U_ROOT",
    )

    principal = Principal(
        user_id="day8-loop-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="day8-loop",
    )
    service = _Service()
    contracts = _ContractStore()
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
                tenant_slug="day8-loop",
                principal_user_id=principal.user_id,
                roles=tuple(principal.roles),
                mdl_version=service.mdl_version,
                catalog="day8-loop",
                schema_name="main",
                db_online=True,
            ),
            contract_store=contracts,
            session_id="day8-loop-session",
        ),
    )

    runtime = ManagerRuntime(request_ref="day8-loop-request")
    runtime.begin_understanding()
    runtime.call_tool(
        ManagerToolCall(
            name=ManagerToolName.PROPOSE_ACCEPTANCE,
            args={
                "envelope": UserIntentEnvelope(
                    attempt_id="day8-loop-attempt",
                    turn_id=message_id,
                    request_ref="day8-loop-request",
                    source_message_hash=source_hash,
                    model_role="RESEARCH_MANAGER",
                    obligations=(
                        CandidateObligation(
                            obligation_id="U_ROOT",
                            capability_key=ManagerCapabilityKey.ROOT_CAUSE,
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
    return (
        spans,
        handles,
        runtime,
        executor,
        service,
        contracts,
        question,
        message_id,
        tenant,
        context_version,
    )


def test_day8_actions_are_not_advertised_without_root_cause_context():
    old_schema = json.dumps(_post_acceptance_native_schema(), ensure_ascii=False)
    assert '"propose_hypothesis"' not in old_schema
    assert '"propose_hypothesis_evidence_relation"' not in old_schema
    assert '"propose_hypothesis_next_test"' not in old_schema

    d8_native = _post_acceptance_native_schema(root_cause_enabled=True)
    d8_schema = json.dumps(d8_native, ensure_ascii=False)
    assert '"propose_hypothesis"' in d8_schema
    assert '"propose_hypothesis_evidence_relation"' in d8_schema
    assert '"propose_hypothesis_next_test"' in d8_schema
    assert d8_native["$defs"]["ResearchTaskKind"]["enum"] == [
        "QUERY",
        "COMPARE",
        "BREAKDOWN",
        "RANK",
    ]


def test_root_cause_loop_bootstraps_and_admits_epistemic_actions_without_auto_completion():
    (
        spans,
        handles,
        runtime,
        executor,
        service,
        contracts,
        question,
        message_id,
        tenant,
        context_version,
    ) = _accepted_root_runtime()

    llm = _RootCauseFakeLLM()
    outcome = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=RootCauseLoopContext(
            semantic_handles=handles,
            tenant_binding=tenant,
            context_version=context_version,
        ),
    ).run(
        question=question,
        message_id=message_id,
        request_ref="day8-loop-request",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.run_finished is False
    assert outcome.verified_complete is False
    assert outcome.clarification_required is True
    assert service.query_calls == 1
    assert contracts.n == 1
    assert len(llm.prompts) == 6

    bootstrap = next(
        item for item in outcome.observations
        if item.get("kind") == "root_cause_bootstrap"
    )
    assert bootstrap["status"] == "TASK_READY"
    assert bootstrap["selected_capability"] == "performance"
    assert bootstrap["task_id"].startswith("rt_")

    hypothesis = next(
        item for item in outcome.observations
        if item.get("kind") == "hypothesis_registered"
    )
    assert hypothesis["result"]["hypothesis_id"].startswith("hyp_")

    next_test = next(
        item for item in outcome.observations
        if item.get("kind") == "hypothesis_next_test_registered"
    )
    assert next_test["result"]["task_id"].startswith("rt_")
    assert next_test["result"]["task_id"] != bootstrap["task_id"]

    relation = next(
        item for item in outcome.observations
        if item.get("kind") == "hypothesis_relation_admitted"
    )
    assert relation["result"]["evidence_links"][0]["relation"] == "SUPPORTS"

    root = next(item for item in runtime.ledger.items if item.obligation_id == "U_ROOT")
    assert root.status == ObligationStatus.IN_PROGRESS
    assert runtime.snapshot.evidence_refs
    assert runtime.snapshot.inspected_evidence_refs == runtime.snapshot.evidence_refs

    first_prompt = llm.prompts[0]
    next_test_contract = {
        row["task_kind"]: row
        for row in first_prompt["ROOT_CAUSE_NEXT_TEST_CONTRACT"]
    }
    assert set(next_test_contract) == {"QUERY", "COMPARE", "BREAKDOWN", "RANK"}
    assert next_test_contract["QUERY"]["capability"] == "performance"
    assert next_test_contract["QUERY"]["execution_mode"] == "DIRECT"

    semantic_catalog = {
        row["handle_ref"]: row
        for row in first_prompt["SEMANTIC_HANDLE_CATALOG"]
    }
    assert semantic_catalog["h1"]["target_kind"] == "metric"
    assert semantic_catalog["h1"]["provenance_type"] == "USER_SOURCE"
    assert semantic_catalog["h1"]["parent_obligation_id"] == "U_ROOT"
    assert "canonical_name" not in semantic_catalog["h1"]
    assert not any(
        str(value).startswith("sem_")
        for row in first_prompt["SEMANTIC_HANDLE_CATALOG"]
        for value in row.values()
        if value is not None
    )

    final_prompt = llm.prompts[-1]
    assert final_prompt["HYPOTHESIS_LEDGERS"][0]["entries"][0][
        "evidence_links"
    ][0]["relation"] == "SUPPORTS"
    assert final_prompt["READY_RESEARCH_TASKS"][0]["task_id"] == next_test["result"]["task_id"]
