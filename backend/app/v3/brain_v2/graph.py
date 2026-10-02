"""Low-level LangGraph runtime for Dima Brain V2 Phase 1."""
from __future__ import annotations

from typing import Any

from langgraph.func import task
from langgraph.graph import END, START, StateGraph

from .activities import (
    BrainActivities,
    CandidateProjectionActivityResult,
    CanonicalizeActivityResult,
    CompletionActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityResult,
    MaterialGroupActivityResult,
    P18ActivityResult,
    RequirementPlanActivityResult,
    P17ActivityResult,
    P19ActivityResult,
    ReportActivityResult,
)
from .telemetry import BoundaryName, OpenTelemetryBridge
from .state import (
    BrainGraphState,
    BrainP19Route,
    BrainStatePayload,
    BrainWorkflowStatus,
)


def _snapshot(state: BrainStatePayload | dict[str, Any]) -> BrainGraphState:
    return BrainGraphState.model_validate(state)


def _append_fingerprint(
    state: BrainGraphState,
    fingerprint: str,
) -> tuple[str, ...]:
    if fingerprint in state.activity_fingerprints:
        return state.activity_fingerprints
    return (*state.activity_fingerprints, fingerprint)


def build_brain_v2_graph(*, activities: BrainActivities, checkpointer=None):
    """Build the explicit Phase-1 graph over injected canonical-owner activities."""

    builder = StateGraph(BrainStatePayload)
    otel = getattr(activities, "otel_bridge", None) or OpenTelemetryBridge()

    def run_activity(boundary: BoundaryName, payload: dict[str, Any], call):
        state = BrainGraphState.model_validate(payload)
        with otel.operation(boundary, state=state) as span:
            result = call(state)
            if isinstance(result, CandidateProjectionActivityResult):
                span.set_attributes(candidate_count=result.candidate_count)
            return result.model_dump(mode="json")

    # Every owner/provider/native boundary is a LangGraph task. Completed task
    # results live in orchestration persistence and are replayed instead of
    # blindly repeating paid/non-deterministic work.
    @task(name="brain_v2_intake_activity")
    def intake_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.INTENT_INTERPRET,
            payload,
            activities.intake,
        )

    @task(name="brain_v2_canonicalize_activity")
    def canonicalize_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.SCOPE_RESOLVE,
            payload,
            activities.canonicalize,
        )

    @task(name="brain_v2_requirement_plan_activity")
    def requirement_plan_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.REQUIREMENTS_PLAN,
            payload,
            activities.plan_requirements,
        )

    @task(name="brain_v2_material_group_activity")
    def material_group_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.MATERIAL_GROUP,
            payload,
            activities.acquire_material_group,
        )

    @task(name="brain_v2_material_activity")
    def material_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.MATERIAL_COMPILE,
            payload,
            activities.acquire_material,
        )

    @task(name="brain_v2_evidence_activity")
    def evidence_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.EVIDENCE_ADMIT,
            payload,
            activities.admit_evidence,
        )

    @task(name="brain_v2_project_candidates_activity")
    def project_candidates_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.DISCOVERY_PROJECT_CANDIDATES,
            payload,
            activities.project_candidates,
        )

    @task(name="brain_v2_p18_activity")
    def p18_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.P18_ADJUDICATE,
            payload,
            activities.adjudicate_relationship,
        )

    @task(name="brain_v2_completion_activity")
    def completion_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.COMPLETION_EVALUATE,
            payload,
            activities.evaluate_completion,
        )

    @task(name="brain_v2_p19_activity")
    def p19_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.P19_ASSESS,
            payload,
            activities.assess_p19,
        )

    @task(name="brain_v2_discovery_activity")
    def discovery_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.P17_DISCOVER,
            payload,
            activities.discover_hypotheses,
        )

    @task(name="brain_v2_next_test_activity")
    def next_test_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.P17_NEXT_TEST,
            payload,
            activities.design_next_test,
        )

    @task(name="brain_v2_report_activity")
    def report_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return run_activity(
            BoundaryName.P20_REPORT,
            payload,
            activities.synthesize_report,
        )

    def intake_node(state: BrainStatePayload):
        current = _snapshot(state)
        if not current.current_user_input:
            raise ValueError("Brain V2 intake requires one current user input")
        result = IntakeActivityResult.model_validate(
            intake_activity(current.model_dump(mode="json")).result()
        )
        return {
            "research_session_id": result.research_session_id,
            "accepted_brief_ref": result.accepted_brief_ref,
            "scope_version_id": result.scope_version_id,
            "open_requirement_ids": result.open_requirement_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "material_group_ids": (),
            "completed_material_group_ids": (),
            "active_material_group_id": None,
            "active_requirement_id": None,
            "terminal_requirement_ids": (),
            "direct_requirement_ids": (),
            "relationship_requirement_ids": (),
            "root_cause_requirement_ids": (),
            "report_requirement_ids": (),
            "p18_requirement_ids": (),
            "p18_claim_refs": (),
            "p18_policy_use_refs": (),
            "completion_revision": 0,
            "investigation_requirement_ids": result.investigation_requirement_ids,
            "follow_verified_material_goal_ids": (
                result.follow_verified_material_goal_ids
            ),
            # A new accepted turn points at a new canonical Research session.
            # Prior-scope Evidence/hypotheses stay durable in Dima stores but are
            # never silently reused as current graph state.
            "pending_evidence_ids": (),
            "pending_receipt_refs": (),
            "evidence_revision": 0,
            "evidence_ids": (),
            "hypothesis_revision": 0,
            "hypothesis_ids": (),
            "candidate_semantic_ids": (),
            "discovery_required": result.discovery_required,
            "discovery_turns": 0,
            "latest_p19_assessment_ref": None,
            "pending_next_test_ref": None,
            "latest_p19_route": None,
            "adaptive_reentries": 0,
            "report_ref": None,
            "workflow_status": BrainWorkflowStatus.RUNNING,
            "last_completed_node": "INTAKE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def canonicalize_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = CanonicalizeActivityResult.model_validate(
            canonicalize_activity(current.model_dump(mode="json")).result()
        )
        return {
            "research_session_id": result.research_session_id,
            "scope_version_id": result.scope_version_id,
            "open_requirement_ids": result.open_requirement_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "hypothesis_ids": result.hypothesis_ids,
            "discovery_required": result.discovery_required,
            "current_user_input": None,
            "last_completed_node": "CANONICALIZE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def requirement_plan_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = RequirementPlanActivityResult.model_validate(
            requirement_plan_activity(
                current.model_dump(mode="json")
            ).result()
        )
        return {
            "material_group_ids": result.material_group_ids,
            "completed_material_group_ids": (),
            "active_material_group_id": None,
            "active_requirement_id": None,
            "terminal_requirement_ids": (),
            "direct_requirement_ids": result.direct_requirement_ids,
            "relationship_requirement_ids": (
                result.relationship_requirement_ids
            ),
            "root_cause_requirement_ids": (
                result.root_cause_requirement_ids
            ),
            "report_requirement_ids": result.report_requirement_ids,
            "p18_requirement_ids": (),
            "p18_claim_refs": (),
            "p18_policy_use_refs": (),
            "completion_revision": 0,
            "last_completed_node": "REQUIREMENTS_PLAN",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def material_group_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = MaterialGroupActivityResult.model_validate(
            material_group_activity(
                current.model_dump(mode="json")
            ).result()
        )
        return {
            "active_material_group_id": result.material_group_id,
            "pending_evidence_ids": result.produced_evidence_ids,
            "pending_receipt_refs": result.produced_receipt_refs,
            "last_completed_node": "MATERIAL_GROUP",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def material_node(state: BrainStatePayload):
        current = _snapshot(state)
        # P17's sealed follow-up executor may already have performed the exact
        # typed acquisition. In that case the graph advances using its durable
        # Evidence/receipt refs and MUST NOT pay Metabot a second time.
        if current.pending_evidence_ids:
            return {
                "last_completed_node": "ACQUIRE_MATERIAL",
            }
        result = MaterialActivityResult.model_validate(
            material_activity(current.model_dump(mode="json")).result()
        )
        return {
            "material_requirement_ids": result.material_requirement_ids,
            "pending_evidence_ids": result.produced_evidence_ids,
            "pending_receipt_refs": result.produced_receipt_refs,
            "last_completed_node": "ACQUIRE_MATERIAL",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def evidence_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = EvidenceActivityResult.model_validate(
            evidence_activity(current.model_dump(mode="json")).result()
        )
        completed_groups = current.completed_material_group_ids
        active_group = current.active_material_group_id
        if active_group is not None and active_group not in completed_groups:
            completed_groups = (*completed_groups, active_group)
        return {
            "evidence_revision": result.evidence_revision,
            "evidence_ids": result.evidence_ids,
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "discovery_required": result.discovery_required,
            "pending_evidence_ids": (),
            "pending_receipt_refs": (),
            "completed_material_group_ids": completed_groups,
            "active_material_group_id": None,
            "last_completed_node": "ADMIT_EVIDENCE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def requirement_dispatch_node(state: BrainStatePayload):
        current = _snapshot(state)
        with otel.operation(
            BoundaryName.REQUIREMENT_DISPATCH,
            state=current,
        ):
            done = set(current.p18_requirement_ids)
            pending = tuple(
                item
                for item in current.relationship_requirement_ids
                if item not in done
            )
            active = pending[0] if pending else None
        return {
            "active_requirement_id": active,
            "last_completed_node": "REQUIREMENT_DISPATCH",
        }

    def p18_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = P18ActivityResult.model_validate(
            p18_activity(current.model_dump(mode="json")).result()
        )
        if (
            current.active_requirement_id is not None
            and result.requirement_id != current.active_requirement_id
        ):
            raise ValueError("P18 returned a different requirement identity")
        return {
            "p18_requirement_ids": (
                *current.p18_requirement_ids,
                result.requirement_id,
            ),
            "p18_claim_refs": (*current.p18_claim_refs, result.claim_ref),
            "p18_policy_use_refs": (
                *current.p18_policy_use_refs,
                result.policy_use_ref,
            ),
            "active_requirement_id": None,
            "last_completed_node": "P18_ADJUDICATE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def completion_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = CompletionActivityResult.model_validate(
            completion_activity(current.model_dump(mode="json")).result()
        )
        return {
            "completion_revision": result.completion_revision,
            "terminal_requirement_ids": result.terminal_requirement_ids,
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def project_candidates_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = CandidateProjectionActivityResult.model_validate(
            project_candidates_activity(current.model_dump(mode="json")).result()
        )
        return {
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "candidate_semantic_ids": result.candidate_semantic_ids,
            "discovery_required": False,
            "last_completed_node": "PROJECT_CANDIDATES",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def discovery_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = P17ActivityResult.model_validate(
            discovery_activity(current.model_dump(mode="json")).result()
        )
        return {
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "discovery_required": result.discovery_required,
            "discovery_turns": current.discovery_turns + 1,
            "last_completed_node": "P17_DISCOVERY",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def p19_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = P19ActivityResult.model_validate(
            p19_activity(current.model_dump(mode="json")).result()
        )
        return {
            "latest_p19_assessment_ref": result.assessment_ref,
            "latest_p19_route": result.route,
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "pending_next_test_ref": result.pending_next_test_ref,
            "workflow_status": (
                BrainWorkflowStatus.SUFFICIENT
                if result.route == BrainP19Route.SUFFICIENT
                else BrainWorkflowStatus.RUNNING
            ),
            "last_completed_node": "P19_ASSESS",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def next_test_node(state: BrainStatePayload):
        current = _snapshot(state)
        if current.pending_next_test_ref is None:
            raise ValueError("P17 next-test node requires typed P19 NextTestRequest")
        if current.adaptive_reentries >= current.max_adaptive_reentries:
            raise ValueError("P17 next-test node exceeded bounded re-entry limit")
        result = P17ActivityResult.model_validate(
            next_test_activity(current.model_dump(mode="json")).result()
        )
        return {
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "pending_evidence_ids": result.produced_evidence_ids,
            "pending_receipt_refs": result.produced_receipt_refs,
            "discovery_required": False,
            "adaptive_reentries": current.adaptive_reentries + 1,
            "last_completed_node": "P17_NEXT_TEST",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def report_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = ReportActivityResult.model_validate(
            report_activity(current.model_dump(mode="json")).result()
        )
        return {
            "report_ref": result.report_ref,
            "workflow_status": BrainWorkflowStatus.RUNNING,
            "last_completed_node": "REPORT",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def complete_node(state: BrainStatePayload):
        _snapshot(state)
        return {
            "workflow_status": BrainWorkflowStatus.COMPLETE,
        }

    def honest_stop_node(state: BrainStatePayload):
        current = _snapshot(state)
        return {
            "workflow_status": BrainWorkflowStatus.INCONCLUSIVE,
            "last_completed_node": "HONEST_STOP",
            "pending_next_test_ref": current.pending_next_test_ref,
        }

    def is_pure_rca(state: BrainGraphState) -> bool:
        return (
            len(state.root_cause_requirement_ids) == 1
            and not state.direct_requirement_ids
            and not state.relationship_requirement_ids
        )

    def after_plan(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if is_pure_rca(current):
            return "acquire_material"
        if current.material_group_ids:
            return "acquire_material_group"
        return "requirement_dispatch"

    def after_material_group_evidence(state: BrainGraphState) -> str:
        if set(state.completed_material_group_ids) != set(
            state.material_group_ids
        ):
            return "acquire_material_group"
        return "requirement_dispatch"

    def after_dispatch(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if current.active_requirement_id is not None:
            return "p18_adjudicate"
        if current.root_cause_requirement_ids:
            # Mixed RCA orchestration is intentionally fail-closed until a
            # generic multi-RCA owner contract exists. RCA + report is pure RCA
            # and never reaches this branch.
            raise ValueError(
                "mixed ROOT_CAUSE requirements require an explicit forward owner"
            )
        return "completion_evaluate"

    def after_completion(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        terminal = set(current.terminal_requirement_ids)
        analytical = set(
            (
                *current.direct_requirement_ids,
                *current.relationship_requirement_ids,
                *current.root_cause_requirement_ids,
            )
        )
        analytical_complete = analytical.issubset(terminal)
        report_pending = bool(
            set(current.report_requirement_ids) - terminal
        )
        all_terminal = set(current.open_requirement_ids).issubset(terminal)
        if analytical_complete and report_pending:
            return "report"
        if all_terminal or (analytical_complete and not current.report_requirement_ids):
            return "complete"
        return "honest_stop"

    def after_evidence(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if not is_pure_rca(current) and current.material_group_ids:
            return after_material_group_evidence(current)
        if current.discovery_required:
            if current.hypothesis_ids:
                raise ValueError("discovery route cannot coexist with hypotheses")
            return "project_candidates"
        return "p19_assess"

    def after_projection(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        # Candidate cardinality is not an epistemic judgment. Zero means there
        # is nothing for P19 to assess; every real candidate set, including a
        # singleton, goes to P19 without manufacturing a competitor.
        if current.hypothesis_ids:
            return "p19_assess"
        return "honest_stop"

    def after_discovery(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if len(current.hypothesis_ids) >= 2:
            return "p19_assess"
        if not current.discovery_required:
            return "honest_stop"
        if current.discovery_turns < current.max_discovery_turns:
            return "p17_discover"
        return "honest_stop"

    def after_p19(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if current.latest_p19_route == BrainP19Route.SUFFICIENT:
            return "report"
        if current.latest_p19_route == BrainP19Route.INCONCLUSIVE:
            return "honest_stop"
        if current.latest_p19_route == BrainP19Route.NEXT_TEST_REQUIRED:
            if current.adaptive_reentries < current.max_adaptive_reentries:
                return "p17_next_test"
            return "honest_stop"
        raise ValueError("P19 route is absent")

    builder.add_node("intake", intake_node)
    builder.add_node("canonicalize", canonicalize_node)
    builder.add_node("requirements_plan", requirement_plan_node)
    builder.add_node("acquire_material_group", material_group_node)
    builder.add_node("acquire_material", material_node)
    builder.add_node("admit_evidence", evidence_node)
    builder.add_node("requirement_dispatch", requirement_dispatch_node)
    builder.add_node("p18_adjudicate", p18_node)
    builder.add_node("completion_evaluate", completion_node)
    builder.add_node("project_candidates", project_candidates_node)
    builder.add_node("p19_assess", p19_node)
    builder.add_node("p17_next_test", next_test_node)
    builder.add_node("report", report_node)
    builder.add_node("complete", complete_node)
    builder.add_node("honest_stop", honest_stop_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "canonicalize")
    builder.add_edge("canonicalize", "requirements_plan")
    builder.add_conditional_edges(
        "requirements_plan",
        after_plan,
        {
            "acquire_material": "acquire_material",
            "acquire_material_group": "acquire_material_group",
            "requirement_dispatch": "requirement_dispatch",
        },
    )
    builder.add_edge("acquire_material_group", "admit_evidence")
    builder.add_edge("acquire_material", "admit_evidence")
    builder.add_conditional_edges(
        "admit_evidence",
        after_evidence,
        {
            "acquire_material_group": "acquire_material_group",
            "requirement_dispatch": "requirement_dispatch",
            "project_candidates": "project_candidates",
            "p19_assess": "p19_assess",
        },
    )
    builder.add_conditional_edges(
        "requirement_dispatch",
        after_dispatch,
        {
            "p18_adjudicate": "p18_adjudicate",
            "completion_evaluate": "completion_evaluate",
        },
    )
    builder.add_edge("p18_adjudicate", "requirement_dispatch")
    builder.add_conditional_edges(
        "completion_evaluate",
        after_completion,
        {
            "report": "report",
            "complete": "complete",
            "honest_stop": "honest_stop",
        },
    )
    builder.add_conditional_edges(
        "project_candidates",
        after_projection,
        {
            "p19_assess": "p19_assess",
            "honest_stop": "honest_stop",
        },
    )
    builder.add_conditional_edges(
        "p19_assess",
        after_p19,
        {
            "report": "report",
            "honest_stop": "honest_stop",
            "p17_next_test": "p17_next_test",
        },
    )
    builder.add_edge("p17_next_test", "acquire_material")
    builder.add_edge("report", "completion_evaluate")
    builder.add_edge("complete", END)
    builder.add_edge("honest_stop", END)

    return builder.compile(checkpointer=checkpointer)
