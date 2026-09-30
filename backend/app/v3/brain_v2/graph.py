"""Low-level LangGraph runtime for Dima Brain V2 Phase 1."""
from __future__ import annotations

from typing import Any

from langgraph.func import task
from langgraph.graph import END, START, StateGraph

from .activities import (
    BrainActivities,
    CanonicalizeActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityResult,
    P17ActivityResult,
    P19ActivityResult,
    ReportActivityResult,
)
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

    # Every owner/provider/native boundary is a LangGraph task. Completed task
    # results live in orchestration persistence and are replayed instead of
    # blindly repeating paid/non-deterministic work.
    @task(name="brain_v2_intake_activity")
    def intake_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.intake(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_canonicalize_activity")
    def canonicalize_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.canonicalize(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_material_activity")
    def material_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.acquire_material(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_evidence_activity")
    def evidence_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.admit_evidence(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_p19_activity")
    def p19_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.assess_p19(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_discovery_activity")
    def discovery_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.discover_hypotheses(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_next_test_activity")
    def next_test_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.design_next_test(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

    @task(name="brain_v2_report_activity")
    def report_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return activities.synthesize_report(
            BrainGraphState.model_validate(payload)
        ).model_dump(mode="json")

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
        return {
            "evidence_revision": result.evidence_revision,
            "evidence_ids": result.evidence_ids,
            "hypothesis_revision": result.hypothesis_revision,
            "hypothesis_ids": result.hypothesis_ids,
            "discovery_required": result.discovery_required,
            "pending_evidence_ids": (),
            "pending_receipt_refs": (),
            "last_completed_node": "ADMIT_EVIDENCE",
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
    builder.add_conditional_edges(
        "p17_discover",
        after_discovery,
        {
            "p17_discover": "p17_discover",
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
    builder.add_edge("report", END)
    builder.add_edge("honest_stop", END)

    return builder.compile(checkpointer=checkpointer)
