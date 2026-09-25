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
from lab.v2_day10_ns4_provider_free_rehearsal import (
    run_canonical_relationship_topology_rehearsal,
    run_rehearsal,
    run_revision_rehearsal,
)


def test_ns4_runtime_rehearsal_uses_six_turns_within_phase_separated_outer_ceiling():
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
    assert receipt["explicit_old_evidence_inspections"] == 1
    assert receipt["manager_turn_ceiling"] == 8
    assert receipt["manager_turn_headroom"] == 2

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



def test_d10_s_exact_canonical_relationship_parent_clean_path_uses_six_total_turns():
    receipt = run_canonical_relationship_topology_rehearsal(revision=False)

    assert receipt["provider_calls"] == 0
    assert receipt["adaptive_parent_obligation_id"] == "U_REL"
    assert "REPORT" in tuple(receipt["user_must_families"])
    assert receipt["preacceptance_model_calls"] == 2
    assert receipt["research_manager_calls"] == 4
    assert receipt["manager_turn_total"] == 6
    assert receipt["manager_turn_ceiling"] == 8
    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["directive_final_status"] == "APPLIED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["confirmed_cause_count"] == 0
    assert receipt["paid_gate_structural_status"] == "STRUCTURALLY_ADMISSIBLE_AT_CEILING"


def test_d10_s_exact_canonical_relationship_parent_revision_path_completes():
    receipt = run_canonical_relationship_topology_rehearsal(revision=True)

    assert receipt["provider_calls"] == 0
    assert receipt["adaptive_parent_obligation_id"] == "U_REL"
    assert "REPORT" in tuple(receipt["user_must_families"])
    assert receipt["preacceptance_model_calls"] == 4
    assert receipt["research_manager_calls"] == 4
    assert receipt["manager_turn_total"] == 8
    assert receipt["explicit_old_evidence_inspections"] == 1
    assert receipt["manager_turn_ceiling"] == 8
    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["directive_final_status"] == "APPLIED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["confirmed_cause_count"] == 0


def test_same_root_revision_path_remains_efficient_under_phase_separation():
    receipt = run_revision_rehearsal()

    assert receipt["provider_calls"] == 0
    assert receipt["preacceptance_model_calls"] == 4
    assert receipt["research_manager_calls"] == 2
    assert receipt["manager_turn_total"] == 6
    assert receipt["manager_turn_ceiling"] == 8
    assert tuple(receipt["research_cognition_sequence"]) == (
        ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST.value,
        ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION.value,
    )
    assert len(receipt["directive_branch_task_refs"]) == 1
    assert receipt["hypothesis_next_tests"] == 1
    assert receipt["evidence_relations"] == 1
    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["directive_final_status"] == "APPLIED"
    assert receipt["candidate_finding_count"] == 1
    assert receipt["confirmed_cause_count"] == 0
    assert receipt["report_statement_injection_absent"] is True
    assert receipt["paid_gate_structural_status"] == "STRUCTURALLY_ADMISSIBLE_AT_CEILING"



def _schema_property_enum(schema, property_name):
    found = []

    def resolve(node):
        if not isinstance(node, dict):
            return node
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            return (schema.get("$defs") or {})[ref.rsplit("/", 1)[-1]]
        return node

    def walk(node):
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict) and property_name in properties:
                found.append(resolve(properties[property_name]))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    def values(node):
        node = resolve(node)
        out = set()
        if isinstance(node, dict):
            enum = node.get("enum")
            if isinstance(enum, list):
                out.update(str(item) for item in enum if item is not None)
            const = node.get("const")
            if isinstance(const, str):
                out.add(const)
            for value in node.values():
                out.update(values(value))
        elif isinstance(node, list):
            for value in node:
                out.update(values(value))
        return out

    walk(schema)
    assert found, property_name
    return values(found[0])


class _Run4AvailabilityManager(ns4.ScriptedNS4Manager):
    """Replay run #4 bad choices and prove they are absent from cognition surface."""

    def __init__(self):
        super().__init__()
        self.research_calls = 0
        self.inventory_snapshots = []
        self.action_snapshots = []

    def structured_json(self, system, user, *, schema, schema_name):
        if schema_name != "dima_research_manager_action_v1":
            return super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )

        payload = json.loads(user)
        self.manager_prompts.append(payload)
        self.research_calls += 1
        actions = _schema_property_enum(schema, "action")
        self.action_snapshots.append(actions)

        delta = payload["CURRENT_RESULT_DELTA"]
        assert delta is not None
        assert delta["verified"] is True
        assert delta["disclosed_in_current_prompt"] is True
        assert delta["inspection_required"] is False

        inventory = tuple(payload["GOVERNED_SEMANTIC_INVENTORY"])
        self.inventory_snapshots.append(inventory)
        department = [
            item
            for item in inventory
            if item["target_kind"] == "dimension"
            and "department" in tuple(item.get("source_surfaces") or ())
        ]
        assert len(department) == 1, inventory

        # These are the exact two redundant run-#4 choices. Current fresh Evidence
        # must be impossible to target for inspection. The action itself may remain when
        # some older undisclosed VERIFIED Evidence is legitimately inspectable.
        inspect_refs = _schema_property_enum(schema, "evidence_ref")
        assert delta["evidence_ref"] not in inspect_refs
        # D10-S parent-scoped availability may keep AGENT_DERIVED semantics for
        # unrelated evidence-grounded obligations. The exact run-4 bug is that the
        # already-satisfied ROOT parent must not be an eligible semantic parent.
        semantic_parents = _schema_property_enum(
            schema,
            "semantic_parent_obligation_id",
        )
        assert "U_ROOT" not in semantic_parents

        ledger = {
            item["obligation_id"]: item
            for item in payload["OBLIGATION_LEDGER"]
        }
        root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
        hypotheses = payload["HYPOTHESIS_LEDGERS"][0]["entries"]

        if not hypotheses:
            assert ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST.value in actions
            self.root_trigger_evidence_ref = delta["evidence_ref"]
            self.actions.append("propose_hypothesis_with_next_test")
            return {
                "action": "propose_hypothesis_with_next_test",
                "hypothesis_parent_obligation_id": "U_ROOT",
                "hypothesis_statement": (
                    "Provider-free run-4 replay hypothesis contains %27 but report must not."
                ),
                "hypothesis_semantic_handles": [root_handle],
                "hypothesis_trigger_evidence_refs": [delta["evidence_ref"]],
                "hypothesis_limitations": [],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": [root_handle],
                "next_test_trigger_evidence_ref": delta["evidence_ref"],
                "next_test_material_reason": (
                    "Use current governed root identity for one material next test."
                ),
            }

        assert ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST.value not in actions
        assert ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION.value in actions
        hypothesis = hypotheses[0]
        self.actions.append("propose_hypothesis_evidence_relation")
        return {
            "action": "propose_hypothesis_evidence_relation",
            "hypothesis_ref": hypothesis["hypothesis_id"],
            "hypothesis_relation_evidence_ref": delta["evidence_ref"],
            "hypothesis_relation": "SUPPORTS",
        }


def test_run4_failure_family_bad_actions_are_absent_and_governed_root_path_completes():
    manager = _Run4AvailabilityManager()
    receipt = run_rehearsal(manager=manager)

    assert receipt["provider_calls"] == 0
    assert manager.research_calls == 2
    assert receipt["research_manager_calls"] == 2
    assert receipt["manager_turn_total"] <= 6
    assert receipt["completion_gate_final_state"] == "COMPLETED"
    assert receipt["root_status"] == "VERIFIED"
    assert receipt["candidate_finding_count"] == 1
    assert receipt["confirmed_cause_count"] == 0
    assert receipt["report_statement_injection_absent"] is True
    assert receipt["directive_final_status"] == "APPLIED"

    # Existing accepted department identity is conserved across both cognition turns.
    assert len(manager.inventory_snapshots) == 2
    first_department = next(
        item
        for item in manager.inventory_snapshots[0]
        if item["target_kind"] == "dimension"
        and "department" in tuple(item.get("source_surfaces") or ())
    )
    second_department = next(
        item
        for item in manager.inventory_snapshots[1]
        if item["target_kind"] == "dimension"
        and "department" in tuple(item.get("source_surfaces") or ())
    )
    assert second_department["handle_ref"] == first_department["handle_ref"]
    assert len(manager.inventory_snapshots[1]) == len(manager.inventory_snapshots[0])


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
        root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
        # Scripted NS4 U_REL is declared as [downtime metric, department dimension].
        # Ledger projection preserves that accepted semantic-handle order; unlike the
        # ROOT_CAUSE semantic catalog, it also exposes the non-root U_REL aliases.
        department_handle = ledger["U_REL"]["semantic_handle_refs"][1]
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
    assert blocked_candidates, diagnostic
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
