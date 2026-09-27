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
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationStatus,
    UserIntentEnvelope,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_tools import (
    ManagerRelationshipObservation,
    ManagerToolCall,
    ManagerToolName,
)
from app.v2.models import (
    EpistemicLabel,
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.research_tools import (
    ResearchToolExecution,
    ResearchToolRegistry,
    ResearchToolRunner,
)
from app.v2.root_cause_orchestration import (
    RootCauseLoopContext,
    root_cause_next_test_contract,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from control_plane.authorize import Principal
from helpers.manager_action_set_adapter import adapt_legacy_manager_intent


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
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "run_analytics",
                    "obligation_ids": ["U_ROOT"],
                    "metric_handles": ["h1"],
                },
            )

        latest = payload.get("CURRENT_RESULT_DELTA")
        if (
            latest
            and not latest.get("inspected")
            and not latest.get("disclosed_in_current_prompt")
        ):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "inspect_evidence",
                    "evidence_ref": latest["evidence_ref"],
                },
            )

        if not entries:
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "propose_hypothesis",
                    "hypothesis_parent_obligation_id": "U_ROOT",
                    "hypothesis_statement": "Aday açıklama gözlemsel olarak sınanmalıdır.",
                    "hypothesis_semantic_handles": ["h1"],
                    "hypothesis_trigger_evidence_refs": [evidence_refs[0]],
                    "hypothesis_limitations": ["Gözlemsel kanıt nedenselliği doğrulamaz."],
                },
            )

        hypothesis = entries[0]
        if not hypothesis.get("next_test_task_refs"):
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "propose_hypothesis_next_test",
                    "hypothesis_ref": hypothesis["hypothesis_id"],
                    "next_test_task_kind": "QUERY",
                    "next_test_input_handles": ["h1"],
                    "next_test_trigger_evidence_ref": evidence_refs[0],
                    "next_test_material_reason": "Aday açıklamayı bir gözlemsel tekrar ölçümle sınırla.",
                },
            )

        if not hypothesis.get("evidence_links"):
            assert latest is not None
            assert latest["evidence_ref"] != evidence_refs[0]
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "propose_hypothesis_evidence_relation",
                    "hypothesis_ref": hypothesis["hypothesis_id"],
                    "hypothesis_relation_evidence_ref": latest["evidence_ref"],
                    "hypothesis_relation": "SUPPORTS",
                },
            )

        return adapt_legacy_manager_intent(
            payload,
            {
                "action": "request_clarification",
                "obligation_ids": ["U_ROOT"],
                "clarification_reason": (
                    "Day8 ROOT_CAUSE completion truth is intentionally not auto-promoted "
                    "from observational support."
                ),
            },
        )


class _BlockedNextTestLLM(_RootCauseFakeLLM):
    """Stop after the generic next-test consumer observes a governed BLOCKED terminal."""

    def structured_json(self, system, user, **kwargs):
        payload = json.loads(user)
        recent = payload.get("RECENT_OBSERVATIONS") or []
        blocked = next(
            (
                item
                for item in recent
                if item.get("kind") == "deterministic_task_blocked"
                and isinstance(item.get("result"), dict)
                and item["result"].get("hypothesis_id")
            ),
            None,
        )
        if blocked is not None:
            self.prompts.append(payload)
            return adapt_legacy_manager_intent(
                payload,
                {
                    "action": "request_clarification",
                    "obligation_ids": ["U_ROOT"],
                    "clarification_reason": (
                        "Governed next test is blocked; no Evidence exists to support "
                        "or contradict the hypothesis."
                    ),
                },
            )
        return super().structured_json(system, user, **kwargs)


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


def test_day8_root_next_test_contract_remains_bounded_to_governed_direct_families():
    rows = {
        row["task_kind"]: row
        for row in root_cause_next_test_contract()
    }
    assert set(rows) == {"QUERY", "COMPARE", "BREAKDOWN", "RANK"}
    assert rows["QUERY"]["required_semantic_kinds"] == ["metric"]
    assert rows["BREAKDOWN"]["required_semantic_kinds"] == [
        "dimension",
        "metric",
    ]
    assert "RELATIONSHIP" not in rows
    assert "CONTRIBUTION" not in rows


def test_root_cause_loop_bootstraps_executes_next_test_and_completes_bounded_investigation():
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

    assert outcome.run_finished is True
    assert outcome.verified_complete is True
    assert outcome.clarification_required is False
    assert service.query_calls == 2
    assert contracts.n == 2
    assert len(llm.prompts) <= 4

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
        if item.get("kind") == "hypothesis_next_test_executed"
    )
    assert next_test["result"]["task_id"].startswith("rt_")
    assert next_test["result"]["task_id"] != bootstrap["task_id"]

    relation = next(
        item for item in outcome.observations
        if item.get("kind") == "hypothesis_relation_admitted"
    )
    assert relation["result"]["evidence_links"][0]["relation"] == "SUPPORTS"

    assert len(outcome.findings) == 1
    finding = outcome.findings[0]
    assert finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert finding.hypothesis_ref == hypothesis["result"]["hypothesis_id"]
    assert finding.evidence_refs == (
        relation["result"]["evidence_links"][0]["evidence_ref"],
    )
    assert finding.statement
    assert finding.limitations
    assert finding.provenance.run_id == runtime.snapshot.run_id

    root = next(item for item in runtime.ledger.items if item.obligation_id == "U_ROOT")
    assert root.status == ObligationStatus.VERIFIED
    assert "nedensel doğruluk" in (root.verdict or "")
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

    # Canonical relation/finding assertions above own final epistemic truth.
    # The last cognition packet may precede deterministic relation reconciliation.



def test_blocked_next_test_terminal_does_not_crash_or_create_epistemic_evidence(
    monkeypatch,
):
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

    llm = _BlockedNextTestLLM()
    loop = ResearchManagerLoop(
        llm=llm,
        source_spans=spans,
        research_tool_runner=ResearchToolRunner(),
        root_cause_context=RootCauseLoopContext(
            semantic_handles=handles,
            tenant_binding=tenant,
            context_version=context_version,
        ),
    )
    real_execute = loop._execute_scheduled_task
    execution_count = 0

    def _execute_with_blocked_next_test(**kwargs):
        nonlocal execution_count
        execution_count += 1
        if execution_count == 1:
            return real_execute(**kwargs)

        task = kwargs["task"]
        registry = kwargs["task_registry"]
        fingerprint = f"test-governed-blocked:{task.task_id}"
        assert registry.begin_execution(
            task=task,
            tool_id="wren.relationship",
            action_fingerprint=fingerprint,
            timeout_ms=15_000,
        ) is None
        execution = ResearchToolExecution(
            task=task.model_copy(update={"state": "blocked"}),
            contract=ResearchToolRegistry().spec("wren.relationship").contract,
            observation=ManagerRelationshipObservation(
                obligation_id="U_ROOT",
                available=False,
                status="UNSUPPORTED",
                reason="provider-free governed blocked terminal",
            ),
            evidence=None,
            elapsed_ms=0.0,
        )
        registry.block_execution(
            task_id=task.task_id,
            tool_id="wren.relationship",
            action_fingerprint=fingerprint,
            result=execution,
        )
        return execution

    monkeypatch.setattr(loop, "_execute_scheduled_task", _execute_with_blocked_next_test)
    outcome = loop.run(
        question=question,
        message_id=message_id,
        request_ref="day8-loop-request",
        runtime=runtime,
        executor=executor,
    )

    blocked = next(
        item
        for item in outcome.observations
        if item.get("kind") == "deterministic_task_blocked"
        and isinstance(item.get("result"), dict)
        and item["result"].get("hypothesis_id")
    )
    assert blocked["result"]["state"] == "blocked"
    assert blocked["result"]["evidence_ref"] is None
    assert service.query_calls == 1
    assert contracts.n == 1
    assert len(runtime.snapshot.evidence_refs) == 1
    assert not any(
        item.get("kind") == "hypothesis_next_test_executed"
        for item in outcome.observations
    )
    assert not any(
        item.get("kind") == "hypothesis_relation_admitted"
        for item in outcome.observations
    )
    assert outcome.findings == ()
    assert not any(
        finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
        for finding in outcome.findings
    )

    # Production authority remains frozen: RELATIONSHIP is still not a
    # ROOT_CAUSE next-test family. This reads the real contract owner directly.
    task_kinds = {
        row["task_kind"] for row in root_cause_next_test_contract()
    }
    assert "RELATIONSHIP" not in task_kinds
