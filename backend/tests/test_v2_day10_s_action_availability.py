"""D10-S provider-free action-surface governance attacks."""

from __future__ import annotations

from typing import Any

from app.v2.manager_action_availability import (
    ActionAvailabilityReason,
    ManagerActionAvailability,
    ManagerActionAvailabilityContext,
    RootActionState,
)
from app.v2.manager_loop import _post_acceptance_native_schema


def _root(
    *,
    hypothesis_count: int = 0,
    kinds: tuple[str, ...] = ("metric",),
    required: tuple[tuple[str, ...], ...] = (("metric",),),
    evidence: tuple[str, ...] = ("evi_fresh",),
) -> RootActionState:
    return RootActionState(
        root_id="U_ROOT",
        hypothesis_count=hypothesis_count,
        root_handle_kinds=kinds,
        next_test_required_kind_sets=required,
        effective_inspected_verified_evidence_refs=evidence,
    )


def _property_schema(schema: dict[str, Any], name: str) -> dict[str, Any]:
    found: list[dict[str, Any]] = []

    def resolve(node: dict[str, Any]) -> dict[str, Any]:
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            return (schema.get("$defs") or {})[ref.rsplit("/", 1)[-1]]
        return node

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict) and isinstance(properties.get(name), dict):
                found.append(resolve(properties[name]))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    assert found, f"schema property missing: {name}"
    return found[0]


def _enum_values(node: Any) -> set[str]:
    out: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            enum = value.get("enum")
            if isinstance(enum, list):
                out.update(str(item) for item in enum if item is not None)
            const = value.get("const")
            if isinstance(const, str):
                out.add(const)
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(node)
    return out


def test_fresh_disclosed_evidence_removes_inspect_and_known_handle_rediscovery():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            open_adaptive_directive_count=1,
            remaining_research_turns=2,
        )
    )

    assert "inspect_evidence" not in profile.available_actions
    assert profile.reasons_for_unavailable("inspect_evidence") == (
        ActionAvailabilityReason.FRESH_EVIDENCE_ALREADY_DISCLOSED.value,
    )
    assert "resolve_semantics" not in profile.available_actions
    assert profile.reasons_for_unavailable("resolve_semantics") == (
        ActionAvailabilityReason.EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST.value,
    )
    assert "propose_hypothesis_with_next_test" in profile.available_actions
    assert profile.inspection_required_for_current_delta is False


def test_old_undisclosed_uninspected_evidence_keeps_explicit_inspection():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            inspectable_old_evidence_refs=("evi_old",),
            remaining_research_turns=3,
        )
    )

    assert "inspect_evidence" in profile.available_actions
    assert profile.inspectable_evidence_refs == ("evi_old",)
    assert profile.inspection_required_for_current_delta is True


def test_genuine_missing_root_shape_keeps_derived_semantic_expansion_available():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(
                _root(
                    kinds=("metric",),
                    required=(("metric", "dimension"),),
                ),
            ),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            remaining_research_turns=3,
        )
    )

    assert "resolve_semantics" in profile.available_actions
    reasons = dict(profile.available_reasons)["resolve_semantics"]
    assert (
        ActionAvailabilityReason.DERIVED_SEMANTIC_EXPANSION_POTENTIALLY_REQUIRED.value
        in reasons
    )
    assert "propose_hypothesis_with_next_test" not in profile.available_actions


def test_no_root_authority_removes_root_only_actions_without_pruning_generic_actions():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=("evi_1",),
            remaining_research_turns=4,
        )
    )

    for action in (
        "propose_hypothesis",
        "propose_hypothesis_with_next_test",
        "propose_hypothesis_next_test",
        "propose_hypothesis_evidence_relation",
    ):
        assert action not in profile.available_actions
        assert profile.reasons_for_unavailable(action) == (
            ActionAvailabilityReason.ROOT_CAUSE_INACTIVE.value,
        )
    assert "run_analytics" in profile.available_actions
    assert "request_clarification" in profile.available_actions


def test_existing_hypothesis_removes_initial_hypothesis_actions_only():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(hypothesis_count=1),),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            remaining_research_turns=2,
        )
    )

    assert "propose_hypothesis" not in profile.available_actions
    assert "propose_hypothesis_with_next_test" not in profile.available_actions
    assert "propose_hypothesis_next_test" in profile.available_actions
    assert "propose_hypothesis_evidence_relation" in profile.available_actions


def test_strict_schema_matches_runtime_profile_and_never_advertises_user_source_reparse():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            remaining_research_turns=2,
        )
    )
    schema = _post_acceptance_native_schema(
        root_cause_enabled=True,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
    )

    actions = _enum_values(_property_schema(schema, "action"))
    assert "inspect_evidence" not in actions
    assert "resolve_semantics" not in actions
    assert "propose_hypothesis_with_next_test" in actions

    provenance = _enum_values(_property_schema(schema, "resolve_provenance"))
    assert provenance == {"AGENT_DERIVED"}


def test_old_evidence_schema_constrains_inspection_to_server_selected_refs():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            inspectable_old_evidence_refs=("evi_old_1", "evi_old_2"),
            remaining_research_turns=3,
        )
    )
    schema = _post_acceptance_native_schema(
        root_cause_enabled=False,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
    )

    actions = _enum_values(_property_schema(schema, "action"))
    assert "inspect_evidence" in actions
    evidence_refs = _enum_values(_property_schema(schema, "evidence_ref"))
    assert evidence_refs == {"evi_old_1", "evi_old_2"}



def test_tight_revision_headroom_prunes_separate_hypothesis_but_keeps_composite():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            open_adaptive_directive_count=1,
            remaining_research_turns=1,
        )
    )

    assert "propose_hypothesis_with_next_test" in profile.available_actions
    assert "propose_hypothesis" not in profile.available_actions
    assert profile.reasons_for_unavailable("propose_hypothesis") == (
        ActionAvailabilityReason.INSUFFICIENT_HEADROOM_FOR_SEPARATE_HYPOTHESIS.value,
    )
    assert profile.remaining_research_turns == 1


def test_zero_future_turns_prunes_composite_without_raising_manager_ceiling():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_fresh",),
            fresh_disclosed_evidence_ref="evi_fresh",
            fresh_disclosed_verified=True,
            remaining_research_turns=0,
        )
    )

    assert "propose_hypothesis_with_next_test" not in profile.available_actions
    assert profile.reasons_for_unavailable("propose_hypothesis_with_next_test") == (
        ActionAvailabilityReason.INSUFFICIENT_HEADROOM_FOR_COMPOSITE.value,
    )


def test_root_ready_does_not_hide_nonroot_semantic_expansion_parent():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_root", "evi_rel"),
            fresh_disclosed_evidence_ref="evi_root",
            fresh_disclosed_verified=True,
            open_adaptive_directive_count=1,
            open_adaptive_parent_obligation_ids=("U_REL",),
            evidence_grounded_parent_obligation_ids=("U_REL",),
            remaining_research_turns=3,
        )
    )

    assert "resolve_semantics" in profile.available_actions
    assert profile.resolve_semantics_parent_obligation_ids == ("U_REL",)
    assert "U_ROOT" not in profile.resolve_semantics_parent_obligation_ids

    schema = _post_acceptance_native_schema(
        root_cause_enabled=True,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
        resolve_semantics_parent_obligation_ids=(
            profile.resolve_semantics_parent_obligation_ids
        ),
    )
    actions = _enum_values(_property_schema(schema, "action"))
    parents = _enum_values(
        _property_schema(schema, "semantic_parent_obligation_id")
    )

    assert "resolve_semantics" in actions
    assert parents == {"U_REL"}


def test_no_eligible_semantic_parent_removes_resolve_even_with_root_evidence():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(),),
            effective_inspected_verified_evidence_refs=("evi_root",),
            fresh_disclosed_evidence_ref="evi_root",
            fresh_disclosed_verified=True,
            open_adaptive_parent_obligation_ids=(),
            evidence_grounded_parent_obligation_ids=("rt_child",),
            remaining_research_turns=3,
        )
    )

    assert "resolve_semantics" not in profile.available_actions
    assert profile.resolve_semantics_parent_obligation_ids == ()




def test_verified_root_next_test_child_does_not_become_semantic_authority():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(_root(hypothesis_count=1),),
            effective_inspected_verified_evidence_refs=("evi_root", "evi_child"),
            fresh_disclosed_evidence_ref="evi_child",
            fresh_disclosed_verified=True,
            open_adaptive_directive_count=0,
            open_adaptive_parent_obligation_ids=(),
            evidence_grounded_parent_obligation_ids=("U_ROOT", "rt_child"),
            remaining_research_turns=2,
        )
    )

    assert "resolve_semantics" not in profile.available_actions
    assert profile.resolve_semantics_parent_obligation_ids == ()
    assert profile.reasons_for_unavailable("resolve_semantics") == (
        ActionAvailabilityReason.EXISTING_GOVERNED_HANDLES_SATISFY_NEXT_TEST.value,
    )
