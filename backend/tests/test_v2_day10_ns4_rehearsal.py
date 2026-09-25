"""G16 provider-free NS4 runtime-observed cognition receipt."""

import json

from app.v2.context_provider import ContextProviderV0
from app.v2.manager_loop import ManagerActionKind, ResearchManagerLoop
from app.v2.manager_models import ResearchDirectiveDispositionStatus
from app.v2.manager_tools import ManagerRelationshipObservation
from app.v2.model_policy import ModelRole
from app.v2.models import AskV2Request, TenantAnalyticsRuntimeV0
from app.v2.product_models import ProductRequestContext
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.research_tools import (
    ResearchToolExecution,
    ResearchToolRegistry,
)
from control_plane.authorize import Principal
from lab import v2_day10_ns4_provider_free_rehearsal as ns4
from lab.v2_day10_ns4_provider_free_rehearsal import run_rehearsal


def test_ns4_runtime_rehearsal_fits_existing_six_turn_ceiling_without_ceremony():
    receipt = run_rehearsal()

    assert receipt["provider_calls"] == 0
    assert receipt["directive_count"] == 1
    assert receipt["directive_id"] == "R_ADAPT_ROOT"
    assert receipt["directive_type"] == "ADAPT_ON_EVIDENCE"
    assert receipt["directive_final_status"] == "APPLIED"
    assert receipt["directive_accounting_evidence_ref"]
    assert receipt["directive_branch_task_refs"]
    assert receipt["preacceptance_model_calls"] == 2
    assert receipt["research_manager_calls"] == 4
    assert receipt["manager_turn_total"] == 6
    assert receipt["manager_turn_ceiling"] == 6
    assert receipt["manager_turn_headroom"] == 0

    assert receipt["deterministic_task_executions"] == 5
    assert receipt["synthetic_query_calls"] == 5
    assert receipt["actual_wren_queries_in_rehearsal"] == 0
    assert receipt["explicit_old_evidence_inspections"] == 0
    assert receipt["redundant_fresh_inspect_turns"] == 0
    assert receipt["redundant_manager_execution_control_turns"] == 0

    cognition = tuple(receipt["research_cognition_sequence"])
    assert cognition == (
        ManagerActionKind.PROPOSE_BRANCHES.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION.value,
    )
    assert ManagerActionKind.RUN_ANALYTICS.value not in cognition
    assert ManagerActionKind.RUN_RELATIONSHIP.value not in cognition
    assert ManagerActionKind.INSPECT_EVIDENCE.value not in cognition
    assert ManagerActionKind.FINISH.value not in cognition

    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["candidate_finding_count"] == 1
    assert receipt["confirmed_cause_count"] == 0
    assert receipt["report_statement_injection_absent"] is True
    assert receipt["paid_gate_structural_status"] == "STRUCTURALLY_ADMISSIBLE_AT_CEILING"



class _BlockedRelationshipBranchManager(ns4.ScriptedNS4Manager):
    """Use the canonical NS4 authority, but choose one governed RELATIONSHIP branch."""

    def structured_json(self, system, user, *, schema, schema_name):
        if schema_name != "dima_research_manager_action_v1":
            return super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )

        payload = json.loads(user)
        recent = payload.get("RECENT_OBSERVATIONS") or []
        if any(
            item.get("kind") == "deterministic_task_blocked"
            and item.get("context") == "adaptive_branch"
            for item in recent
        ):
            self.manager_prompts.append(payload)
            self.actions.append("request_clarification")
            return {
                "action": "request_clarification",
                "obligation_ids": ["U_ROOT"],
                "clarification_reason": (
                    "The governed adaptive relationship branch is blocked; "
                    "no successful analytical branch result exists."
                ),
            }

        if self.manager_prompts:
            return super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )

        self.manager_prompts.append(payload)
        ledger = {
            item["obligation_id"]: item
            for item in payload["OBLIGATION_LEDGER"]
        }
        catalog = {
            item["handle_ref"]: item
            for item in payload["SEMANTIC_HANDLE_CATALOG"]
        }
        root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
        department_handle = next(
            ref
            for ref in ledger["U_REL"]["semantic_handle_refs"]
            if catalog[ref]["target_kind"] == "dimension"
        )
        delta = payload["CURRENT_RESULT_DELTA"]
        assert delta is not None and delta["verified"] is True
        self.root_trigger_evidence_ref = delta["evidence_ref"]
        self.actions.append("propose_branches")
        return {
            "action": "propose_branches",
            "branch_parent_obligation_id": "U_ROOT",
            "branch_evidence_ref": delta["evidence_ref"],
            "branch_candidates": [
                {
                    "task_id": "D_ROOT_REL_BLOCKED",
                    "capability_key": "relationship",
                    "input_handles": [root_handle, department_handle],
                    "material_reason": (
                        "Test one governed relationship direction without inventing Evidence."
                    ),
                }
            ],
        }


def test_adaptive_relationship_blocked_terminal_does_not_apply_directive(
    monkeypatch,
):
    tenant = "g16-blocked-tenant"
    service = ns4.SyntheticService()
    principal = Principal(
        user_id="g16-blocked-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="g16-blocked",
    )
    schema = service.schema()
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="g16-blocked",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=service.mdl_version,
        catalog="g16",
        schema_name="main",
        db_online=True,
    )
    context = ProductRequestContext(
        request_ref="g16-blocked-correlation",
        tenant_binding=f"id:{tenant}",
        principal=principal,
        tenant_runtime=tenant_runtime,
        service=service,
        schema=schema,
        semantic_context=ContextProviderV0().build(service, tenant_runtime),
        contract_store=ns4.ContractStore(),
        session_id="g16-blocked-session",
        thread_id="g16-blocked-thread",
        turn_ref="g16-blocked-turn",
    )

    manager = _BlockedRelationshipBranchManager()
    lane = ResearchLaneService(
        cognition=ResearchCognition(
            manager_llm=manager,
            manager_profile=ns4.profile(ModelRole.RESEARCH_MANAGER),
            semantic_provider=None,
            semantic_profile=ns4.profile(ModelRole.SEMANTIC_LINKER),
            temporal_provider=None,
            temporal_profile=ns4.profile(ModelRole.TEMPORAL_NORMALIZER),
        )
    )

    original_execute = ResearchManagerLoop._execute_scheduled_task

    def _execute_with_governed_block(self, **kwargs):
        task = kwargs["task"]
        if task.task_id != "D_ROOT_REL_BLOCKED":
            return original_execute(self, **kwargs)

        assert task.task_kind == "RELATIONSHIP"
        registry = kwargs["task_registry"]
        fingerprint = f"test-adaptive-blocked:{task.task_id}"
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
                reason="governed cross-domain data gap",
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

    monkeypatch.setattr(
        ResearchManagerLoop,
        "_execute_scheduled_task",
        _execute_with_governed_block,
    )

    progress = []
    result = lane.run(
        context=context,
        body=AskV2Request(
            question=(
                "Research downtime performance, its governed relationship with department, "
                "and investigate the root cause of faults; doğrulanmış sonuçlar yeni bir maddi "
                "kırılıma işaret ederse onu takip et"
            ),
            session_id=context.session_id,
            thread_id=context.thread_id,
        ),
        progress_callback=lambda kind, refs: progress.append((kind, refs)),
    )

    blocked_candidates = [
        item
        for item in result.outcome.observations
        if item.get("kind") == "deterministic_task_blocked"
        and item.get("context") == "adaptive_branch"
    ]
    diagnostic = tuple(
        item
        for item in result.outcome.observations
        if item.get("kind") in {
            "fanout_registered",
            "tool_rejected",
            "deterministic_schedule_deferred",
            "deterministic_task_blocked",
            "adaptive_branch_executed",
        }
    )
    assert blocked_candidates, {
        "diagnostic": diagnostic,
        "manager_actions": tuple(manager.actions),
        "manager_prompts": len(manager.manager_prompts),
        "runtime_state": result.runtime.snapshot.state.value,
        "clarification_required": result.outcome.clarification_required,
        "observation_kinds": tuple(
            item.get("kind") for item in result.outcome.observations
        ),
        "ledger": tuple(
            (item.obligation_id, item.status.value)
            for item in result.ledger.items
        ),
    }
    blocked = blocked_candidates[0]
    assert blocked["task_id"] == "D_ROOT_REL_BLOCKED"
    assert blocked["result"]["available"] is False
    assert blocked["result"]["status"] == "UNSUPPORTED"
    assert not any(
        item.get("kind") == "adaptive_branch_executed"
        and item.get("task_id") == "D_ROOT_REL_BLOCKED"
        for item in result.outcome.observations
    )
    assert all(
        evidence.task_id != "D_ROOT_REL_BLOCKED"
        for evidence in result.evidence
    )
    assert ("research_task_blocked", ("D_ROOT_REL_BLOCKED",)) in progress

    directive = next(
        item
        for item in result.runtime.directive_dispositions
        if item.directive_id == "R_ADAPT_ROOT"
    )
    assert directive.status == ResearchDirectiveDispositionStatus.OPEN
    assert directive.evidence_ref is None
    assert directive.branch_task_refs == ()
    assert result.findings == ()
