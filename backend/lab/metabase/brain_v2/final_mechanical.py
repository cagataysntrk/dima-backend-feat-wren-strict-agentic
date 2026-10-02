"""Mechanical gates for final Brain V2 relationship/report composition.

This module owns no Product semantics. It validates receipts emitted by the one
forward LangGraph runtime.
"""
from __future__ import annotations

from typing import Any

from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus


RELATIONSHIP_REPORT = "RELATIONSHIP_REPORT_PHASE2_V1"
MULTI_INTENT = "MULTI_INTENT_PHASE2_V1"


def _policy_value(item: Any, name: str):
    value = getattr(item, name, None)
    return getattr(value, "value", value)


def _budget_delta(
    before: dict[str, int] | None,
    after: dict[str, int],
    owner: str,
) -> int:
    return int(after.get(owner, 0)) - int((before or {}).get(owner, 0))


def phase2_mechanical(
    *,
    probe_id: str,
    state: BrainGraphState,
    first_state: BrainGraphState | None,
    native_occurrences: tuple[dict[str, Any], ...],
    first_native_count: int | None,
    p18_uses: tuple[Any, ...],
    report_present: bool,
    budget_before_report: dict[str, int] | None,
    budget_after: dict[str, int],
    same_research_session: bool,
    same_scope_version: bool,
    checkpoint_roundtrip: bool,
    legacy_composer_calls: int,
    agent_api_request_count: int,
    stale_evidence_count: int,
    cross_tenant_violation_count: int,
    causal_overclaim_count: int,
) -> dict[str, Any]:
    if probe_id not in {RELATIONSHIP_REPORT, MULTI_INTENT}:
        raise ValueError(f"unsupported final phase2 probe:{probe_id}")

    verified = tuple(
        item for item in native_occurrences
        if item.get("status") == "VERIFIED"
    )
    fingerprints = tuple(
        item.get("query_fingerprint")
        for item in verified
        if item.get("query_fingerprint")
    )
    duplicate_native = len(fingerprints) - len(set(fingerprints))
    policy_not_required = bool(p18_uses) and all(
        _policy_value(item, "resolution_status") == "NOT_REQUIRED"
        and getattr(item, "policy_id", None) is None
        for item in p18_uses
    )
    relationship_fulfilled = bool(p18_uses) and all(
        _policy_value(item, "resolution_status") in {"NOT_REQUIRED", "SATISFIED"}
        for item in p18_uses
    )
    analytical = set(
        (
            *state.direct_requirement_ids,
            *state.relationship_requirement_ids,
            *state.root_cause_requirement_ids,
        )
    )
    terminal = set(state.terminal_requirement_ids)
    all_terminal = set(state.open_requirement_ids).issubset(terminal)
    hidden_must_count = len(set(state.open_requirement_ids) - terminal)
    requirement_complete = (
        all_terminal
        and analytical.issubset(terminal)
        and relationship_fulfilled
        and report_present
        and not state.root_cause_requirement_ids
    )

    common = {
        "runtime": "BRAIN_V2_LANGGRAPH",
        "legacy_composer_calls": int(legacy_composer_calls),
        "agent_api_request_count": int(agent_api_request_count),
        "stale_evidence_count": int(stale_evidence_count),
        "cross_tenant_violation_count": int(cross_tenant_violation_count),
        "causal_overclaim_count": int(causal_overclaim_count),
        "hidden_must_count": hidden_must_count,
        "requirement_complete": requirement_complete,
        "terminal_complete": state.workflow_status == BrainWorkflowStatus.COMPLETE,
        "checkpoint_roundtrip": checkpoint_roundtrip,
        "material_group_count": len(state.material_group_ids),
        "completed_material_group_count": len(state.completed_material_group_ids),
        "native_acquisitions": len(verified),
        "duplicate_native": duplicate_native,
        "p18_terminal_count": len(state.p18_requirement_ids),
        "p18_not_required_without_business_policy": policy_not_required,
        "p19_assessment_ref": state.latest_p19_assessment_ref,
        "report_present": report_present,
        "all_analytical_terminal": analytical.issubset(terminal),
        "all_user_must_terminal": all_terminal,
        "completion_revision": state.completion_revision,
        "presentation_revision": state.presentation_revision,
    }
    checks = {
        "one_forward_runtime": common["runtime"] == "BRAIN_V2_LANGGRAPH",
        "legacy_calls_zero": common["legacy_composer_calls"] == 0,
        "agent_api_calls_zero": common["agent_api_request_count"] == 0,
        "stale_evidence_zero": common["stale_evidence_count"] == 0,
        "cross_tenant_zero": common["cross_tenant_violation_count"] == 0,
        "causal_overclaim_zero": common["causal_overclaim_count"] == 0,
        "hidden_must_zero": common["hidden_must_count"] == 0,
        "requirement_complete": bool(common["requirement_complete"]),
        "terminal_complete": bool(common["terminal_complete"]),
        "checkpoint_roundtrip": bool(common["checkpoint_roundtrip"]),
        "duplicate_native_zero": common["duplicate_native"] == 0,
        "p18_observational_not_business_policy": bool(policy_not_required),
        "p19_not_used_for_observational_relationship": (
            state.latest_p19_assessment_ref is None
        ),
        "all_analytical_terminal": bool(common["all_analytical_terminal"]),
        "all_user_must_terminal": bool(common["all_user_must_terminal"]),
        "report_present": bool(report_present),
    }

    if probe_id == RELATIONSHIP_REPORT:
        if first_state is None or first_native_count is None:
            raise ValueError("relationship/report proof requires first-turn receipt")
        deltas = {
            owner: _budget_delta(budget_before_report, budget_after, owner)
            for owner in (
                "research_intake",
                "metabase",
                "p17_manager",
                "p19_manager",
            )
        }
        common["report_turn_budget_delta"] = deltas
        common["report_turn_native_delta"] = len(verified) - first_native_count
        common["same_research_session"] = same_research_session
        common["same_scope_version"] = same_scope_version
        checks.update(
            {
                "first_turn_relationship_terminal": (
                    len(first_state.relationship_requirement_ids) == 1
                    and set(first_state.relationship_requirement_ids).issubset(
                        set(first_state.terminal_requirement_ids)
                    )
                ),
                "same_research_session": same_research_session,
                "same_scope_version": same_scope_version,
                "report_only_native_delta_zero": (
                    common["report_turn_native_delta"] == 0
                ),
                "report_only_owner_delta_zero": all(
                    value == 0 for value in deltas.values()
                ),
                "presentation_revision_advanced": (
                    state.presentation_revision
                    == first_state.presentation_revision + 1
                ),
            }
        )
    else:
        checks.update(
            {
                "one_shared_material_group": (
                    len(state.material_group_ids) == 1
                    and len(state.completed_material_group_ids) == 1
                ),
                "one_native_acquisition": len(verified) == 1,
                "direct_requirement_present": bool(state.direct_requirement_ids),
                "relationship_requirement_present": bool(
                    state.relationship_requirement_ids
                ),
                "report_requirement_present": bool(state.report_requirement_ids),
                "one_p18_terminal": len(state.p18_requirement_ids) == 1,
            }
        )

    return {
        **common,
        "checks": checks,
        "mechanical_green": all(checks.values()),
    }
