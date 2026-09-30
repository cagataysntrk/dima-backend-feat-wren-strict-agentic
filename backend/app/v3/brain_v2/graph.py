"""Low-level LangGraph runtime for Dima Brain V2 Phase 1."""
from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from .activities import BrainActivities
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

    def intake_node(state: BrainStatePayload):
        current = _snapshot(state)
        if not current.current_user_input:
            raise ValueError("Brain V2 intake requires one current user input")
        result = activities.intake(current)
        return {
            "accepted_brief_ref": result.accepted_brief_ref,
            "scope_version_id": result.scope_version_id,
            "open_requirement_ids": result.open_requirement_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "discovery_required": result.discovery_required,
            "workflow_status": BrainWorkflowStatus.RUNNING,
            "last_completed_node": "INTAKE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def canonicalize_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.canonicalize(current)
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

    def material_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.acquire_material(current)
        return {
            "material_requirement_ids": result.material_requirement_ids,
            "last_completed_node": "ACQUIRE_MATERIAL",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def evidence_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.admit_evidence(current)
        return {
            "evidence_revision": result.evidence_revision,
            "evidence_ids": result.evidence_ids,
            "last_completed_node": "ADMIT_EVIDENCE",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def discovery_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.discover_hypotheses(current)
        return {
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "discovery_required": result.discovery_required,
            "last_completed_node": "P17_DISCOVERY",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def p19_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.assess_p19(current)
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
        result = activities.design_next_test(current)
        return {
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "material_requirement_ids": result.material_requirement_ids,
            "discovery_required": False,
            "pending_next_test_ref": None,
            "adaptive_reentries": current.adaptive_reentries + 1,
            "last_completed_node": "P17_NEXT_TEST",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def report_node(state: BrainStatePayload):
        current = _snapshot(state)
        result = activities.synthesize_report(current)
        return {
            "report_ref": result.report_ref,
            "workflow_status": BrainWorkflowStatus.COMPLETE,
            "last_completed_node": "REPORT",
            "activity_fingerprints": _append_fingerprint(
                current, result.activity_fingerprint
            ),
        }

    def honest_stop_node(state: BrainStatePayload):
        current = _snapshot(state)
        return {
            "workflow_status": BrainWorkflowStatus.INCONCLUSIVE,
            "last_completed_node": "HONEST_STOP",
            "pending_next_test_ref": current.pending_next_test_ref,
        }

    def after_evidence(state: BrainStatePayload) -> str:
        current = _snapshot(state)
        if current.discovery_required:
            if current.hypothesis_ids:
                raise ValueError("discovery route cannot coexist with hypotheses")
            return "p17_discover"
        return "p19_assess"

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
    builder.add_node("acquire_material", material_node)
    builder.add_node("admit_evidence", evidence_node)
    builder.add_node("p17_discover", discovery_node)
    builder.add_node("p19_assess", p19_node)
    builder.add_node("p17_next_test", next_test_node)
    builder.add_node("report", report_node)
    builder.add_node("honest_stop", honest_stop_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "canonicalize")
    builder.add_edge("canonicalize", "acquire_material")
    builder.add_edge("acquire_material", "admit_evidence")
    builder.add_conditional_edges(
        "admit_evidence",
        after_evidence,
        {
            "p17_discover": "p17_discover",
            "p19_assess": "p19_assess",
        },
    )
    builder.add_edge("p17_discover", "p19_assess")
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
    builder.add_edge("report", END)
    builder.add_edge("honest_stop", END)

    return builder.compile(checkpointer=checkpointer)
