"""D10-S provider-free action-surface governance attacks."""

from __future__ import annotations

from typing import Any

import pytest

from app.v2.manager_action_availability import (
    ActionScopeSeed,
    ActionAvailabilityReason,
    AdaptiveDirectiveDispositionState,
    ManagerActionAvailability,
    ManagerActionAvailabilityContext,
    RootActionState,
)
from app.v2.manager_loop import (
    ResearchManagerLoop,
    _post_acceptance_native_schema,
)


def _root(
    *,
    hypothesis_count: int = 0,
    kinds: tuple[str, ...] = ("metric",),
    required: tuple[tuple[str, ...], ...] = (("metric",),),
    handles: tuple[str, ...] = ("h_root",),
    hypothesis_refs: tuple[str, ...] = (),
    evidence: tuple[str, ...] = ("evi_fresh",),
    pending_hypotheses: tuple[str, ...] = (),
    pending_evidence: tuple[str, ...] = (),
) -> RootActionState:
    return RootActionState(
        root_id="U_ROOT",
        hypothesis_count=hypothesis_count,
        root_handle_kinds=kinds,
        next_test_required_kind_sets=required,
        root_handle_refs=handles,
        hypothesis_refs=hypothesis_refs,
        effective_inspected_verified_evidence_refs=evidence,
        pending_relation_hypothesis_refs=pending_hypotheses,
        pending_relation_evidence_refs=pending_evidence,
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


def test_live_root_action_schema_excludes_cross_obligation_handles_before_cognition():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(
                _root(
                    kinds=("metric", "metric"),
                    handles=("h9", "h10"),
                    evidence=("evi_root",),
                ),
            ),
            effective_inspected_verified_evidence_refs=("evi_root",),
            fresh_disclosed_evidence_ref="evi_root",
            fresh_disclosed_verified=True,
            remaining_research_turns=4,
        )
    )
    schema = _post_acceptance_native_schema(
        root_cause_enabled=True,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
        resolve_semantics_parent_obligation_ids=(
            profile.resolve_semantics_parent_obligation_ids
        ),
        root_parent_obligation_ids=profile.root_parent_obligation_ids,
        root_action_handle_refs=profile.root_action_handle_refs,
        root_evidence_refs=profile.root_evidence_refs,
        hypothesis_refs=profile.hypothesis_refs,
        pending_relation_hypothesis_refs=(
            profile.pending_relation_hypothesis_refs
        ),
        pending_relation_evidence_refs=profile.pending_relation_evidence_refs,
    )

    parents = _enum_values(
        _property_schema(schema, "hypothesis_parent_obligation_id")
    )
    hypothesis_handles = _enum_values(
        _property_schema(schema, "hypothesis_semantic_handles")
    )
    next_test_handles = _enum_values(
        _property_schema(schema, "next_test_input_handles")
    )
    trigger_refs = _enum_values(
        _property_schema(schema, "hypothesis_trigger_evidence_refs")
    )

    assert parents == {"U_ROOT"}
    assert hypothesis_handles == {"h9", "h10"}
    assert next_test_handles == {"h9", "h10"}
    assert "h3" not in hypothesis_handles
    assert "h3" not in next_test_handles
    assert trigger_refs == {"evi_root"}


def test_unlinked_verified_next_test_evidence_requires_relation_before_more_testing():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=(
                _root(
                    hypothesis_count=1,
                    handles=("h9", "h10"),
                    hypothesis_refs=("hyp_1",),
                    evidence=("evi_seed", "evi_post"),
                    pending_hypotheses=("hyp_1",),
                    pending_evidence=("evi_post",),
                ),
            ),
            effective_inspected_verified_evidence_refs=("evi_seed", "evi_post"),
            fresh_disclosed_evidence_ref="evi_post",
            fresh_disclosed_verified=True,
            remaining_research_turns=2,
        )
    )

    assert "propose_hypothesis_next_test" not in profile.available_actions
    assert profile.reasons_for_unavailable("propose_hypothesis_next_test") == (
        ActionAvailabilityReason.POST_TEST_EVIDENCE_RELATION_PENDING.value,
    )
    assert "propose_hypothesis_evidence_relation" in profile.available_actions

    schema = _post_acceptance_native_schema(
        root_cause_enabled=True,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
        resolve_semantics_parent_obligation_ids=(
            profile.resolve_semantics_parent_obligation_ids
        ),
        root_parent_obligation_ids=profile.root_parent_obligation_ids,
        root_action_handle_refs=profile.root_action_handle_refs,
        root_evidence_refs=profile.root_evidence_refs,
        hypothesis_refs=profile.hypothesis_refs,
        pending_relation_hypothesis_refs=(
            profile.pending_relation_hypothesis_refs
        ),
        pending_relation_evidence_refs=profile.pending_relation_evidence_refs,
    )

    actions = _enum_values(_property_schema(schema, "action"))
    assert "propose_hypothesis_next_test" not in actions
    assert "propose_hypothesis_evidence_relation" in actions
    assert _enum_values(_property_schema(schema, "hypothesis_ref")) == {"hyp_1"}
    assert _enum_values(
        _property_schema(schema, "hypothesis_relation_evidence_ref")
    ) == {"evi_post"}



def test_directive_disposition_schema_is_parent_scoped_and_wrong_parent_ref_is_absent():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=(
                "evi_rel",
                "evi_root",
            ),
            open_adaptive_directive_count=1,
            open_adaptive_parent_obligation_ids=("U_REL",),
            adaptive_disposition_states=(
                AdaptiveDirectiveDispositionState(
                    directive_id="R_REL",
                    parent_obligation_id="U_REL",
                    eligible_evidence_refs=("evi_rel",),
                ),
            ),
            remaining_research_turns=1,
        )
    )

    assert "disposition_research_directive" in profile.available_actions
    assert profile.directive_disposition_id == "R_REL"
    assert profile.directive_disposition_parent_obligation_id == "U_REL"
    assert profile.directive_disposition_evidence_refs == ("evi_rel",)

    schema = _post_acceptance_native_schema(
        root_cause_enabled=False,
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
        directive_disposition_ids=(profile.directive_disposition_id,),
        directive_disposition_evidence_refs=(
            profile.directive_disposition_evidence_refs
        ),
    )

    assert _enum_values(_property_schema(schema, "directive_id")) == {"R_REL"}
    evidence_refs = _enum_values(
        _property_schema(schema, "directive_evidence_ref")
    )
    assert evidence_refs == {"evi_rel"}
    assert "evi_root" not in evidence_refs


def test_multiple_open_directives_choose_one_actionable_target_without_cross_product():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=("evi_a", "evi_b"),
            open_adaptive_directive_count=2,
            adaptive_disposition_states=(
                AdaptiveDirectiveDispositionState(
                    directive_id="R_A",
                    parent_obligation_id="U_A",
                    eligible_evidence_refs=("evi_a",),
                ),
                AdaptiveDirectiveDispositionState(
                    directive_id="R_B",
                    parent_obligation_id="U_B",
                    eligible_evidence_refs=("evi_b",),
                ),
            ),
            remaining_research_turns=2,
        )
    )

    # Accepted-contract order selects one structurally actionable target. The model
    # never receives a directive/evidence cross-product it could combine illegally.
    assert profile.directive_disposition_id == "R_A"
    assert profile.directive_disposition_evidence_refs == ("evi_a",)
    assert "evi_b" not in profile.directive_disposition_evidence_refs


def test_first_open_directive_without_evidence_does_not_block_next_actionable_directive():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=("evi_b",),
            open_adaptive_directive_count=2,
            adaptive_disposition_states=(
                AdaptiveDirectiveDispositionState(
                    directive_id="R_A",
                    parent_obligation_id="U_A",
                    eligible_evidence_refs=(),
                ),
                AdaptiveDirectiveDispositionState(
                    directive_id="R_B",
                    parent_obligation_id="U_B",
                    eligible_evidence_refs=("evi_b",),
                ),
            ),
            remaining_research_turns=2,
        )
    )

    assert "disposition_research_directive" in profile.available_actions
    assert profile.directive_disposition_id == "R_B"
    assert profile.directive_disposition_evidence_refs == ("evi_b",)


def test_open_directive_without_parent_lineage_evidence_is_not_advertised():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=("evi_wrong_parent",),
            open_adaptive_directive_count=1,
            adaptive_disposition_states=(
                AdaptiveDirectiveDispositionState(
                    directive_id="R_REL",
                    parent_obligation_id="U_REL",
                    eligible_evidence_refs=(),
                ),
            ),
            remaining_research_turns=1,
        )
    )

    assert "disposition_research_directive" not in profile.available_actions
    assert profile.directive_disposition_id is None
    assert profile.directive_disposition_evidence_refs == ()
    assert profile.reasons_for_unavailable("disposition_research_directive") == (
        ActionAvailabilityReason.NO_ELIGIBLE_ADAPTIVE_DIRECTIVE_EVIDENCE.value,
    )


def test_derived_child_evidence_can_be_exposed_only_after_product_lineage_validation():
    profile = ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            effective_inspected_verified_evidence_refs=("evi_child",),
            open_adaptive_directive_count=1,
            adaptive_disposition_states=(
                AdaptiveDirectiveDispositionState(
                    directive_id="R_PARENT",
                    parent_obligation_id="U_PARENT",
                    eligible_evidence_refs=("evi_child",),
                ),
            ),
            remaining_research_turns=1,
        )
    )

    assert profile.directive_disposition_id == "R_PARENT"
    assert profile.directive_disposition_evidence_refs == ("evi_child",)
    view = profile.model_view()["directive_disposition_target"]
    assert view == {
        "directive_id": "R_PARENT",
        "parent_obligation_id": "U_PARENT",
        "eligible_evidence_refs": ["evi_child"],
    }



def _snapshot_profile(
    *seeds: ActionScopeSeed,
    roots: tuple[RootActionState, ...] = (),
    effective_evidence: tuple[str, ...] = (),
    semantic_parents: tuple[str, ...] = (),
    adaptive_states: tuple[AdaptiveDirectiveDispositionState, ...] = (),
    state_version: str = "apsv_test_state",
):
    return ManagerActionAvailability.evaluate(
        ManagerActionAvailabilityContext(
            root_states=roots,
            state_version=state_version,
            scope_seeds=tuple(seeds),
            effective_inspected_verified_evidence_refs=effective_evidence,
            open_adaptive_directive_count=len(adaptive_states),
            open_adaptive_parent_obligation_ids=semantic_parents,
            adaptive_disposition_states=adaptive_states,
            evidence_grounded_parent_obligation_ids=semantic_parents,
            remaining_research_turns=4,
        )
    )


def _choice_variants(schema: dict[str, Any]) -> list[dict[str, Any]]:
    return list(schema["properties"]["choice"]["anyOf"])


def _variant_for_scope(
    schema: dict[str, Any],
    scope_ref: str,
) -> dict[str, Any]:
    matches = []
    for variant in _choice_variants(schema):
        props = variant.get("properties") or {}
        if scope_ref in _enum_values(props.get("scope_ref") or {}):
            matches.append(variant)
    assert len(matches) == 1
    return matches[0]


def _schema_for_profile(profile):
    return _post_acceptance_native_schema(
        root_cause_enabled=bool(profile.root_parent_obligation_ids),
        allowed_actions=profile.available_actions,
        inspectable_evidence_refs=profile.inspectable_evidence_refs,
        resolve_provenance=profile.post_acceptance_resolve_provenance,
        applicability_snapshot=profile.applicability_snapshot,
    )


def test_snapshot_multi_root_preserves_parent_handle_evidence_correlation():
    roots = (
        RootActionState(
            root_id="R1",
            hypothesis_count=0,
            root_handle_kinds=("metric",),
            next_test_required_kind_sets=(("metric",),),
            root_handle_refs=("h_r1",),
            effective_inspected_verified_evidence_refs=("e_r1",),
        ),
        RootActionState(
            root_id="R2",
            hypothesis_count=0,
            root_handle_kinds=("metric",),
            next_test_required_kind_sets=(("metric",),),
            root_handle_refs=("h_r2",),
            effective_inspected_verified_evidence_refs=("e_r2",),
        ),
    )
    profile = _snapshot_profile(
        ActionScopeSeed(
            action="propose_hypothesis",
            parent_obligation_id="R1",
            evidence_refs=("e_r1",),
            handle_refs=("h_r1",),
        ),
        ActionScopeSeed(
            action="propose_hypothesis",
            parent_obligation_id="R2",
            evidence_refs=("e_r2",),
            handle_refs=("h_r2",),
        ),
        roots=roots,
        effective_evidence=("e_r1", "e_r2"),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    scopes = snapshot.scopes_for("propose_hypothesis")
    assert len(scopes) == 2
    r1 = next(item for item in scopes if item.parent_obligation_id == "R1")
    r2 = next(item for item in scopes if item.parent_obligation_id == "R2")
    assert r1.handle_refs == ("h_r1",)
    assert r1.evidence_refs == ("e_r1",)
    assert r2.handle_refs == ("h_r2",)
    assert r2.evidence_refs == ("e_r2",)

    schema = _schema_for_profile(profile)
    r1_props = _variant_for_scope(schema, r1.scope_ref)["properties"]
    assert _enum_values(r1_props["hypothesis_parent_obligation_id"]) == {"R1"}
    assert _enum_values(r1_props["hypothesis_semantic_handles"]) == {"h_r1"}
    assert _enum_values(r1_props["hypothesis_trigger_evidence_refs"]) == {"e_r1"}
    assert "h_r2" not in _enum_values(r1_props["hypothesis_semantic_handles"])
    assert "e_r2" not in _enum_values(r1_props["hypothesis_trigger_evidence_refs"])


def test_snapshot_multi_hypothesis_relation_keeps_post_test_evidence_local():
    root = RootActionState(
        root_id="R",
        hypothesis_count=2,
        root_handle_kinds=("metric",),
        next_test_required_kind_sets=(("metric",),),
        root_handle_refs=("h",),
        hypothesis_refs=("H1", "H2"),
        effective_inspected_verified_evidence_refs=("E1", "E2"),
        pending_relation_hypothesis_refs=("H1", "H2"),
        pending_relation_evidence_refs=("E1", "E2"),
    )
    profile = _snapshot_profile(
        ActionScopeSeed(
            action="propose_hypothesis_evidence_relation",
            parent_obligation_id="R",
            hypothesis_ref="H1",
            evidence_refs=("E1",),
        ),
        ActionScopeSeed(
            action="propose_hypothesis_evidence_relation",
            parent_obligation_id="R",
            hypothesis_ref="H2",
            evidence_refs=("E2",),
        ),
        roots=(root,),
        effective_evidence=("E1", "E2"),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    h1 = next(
        item
        for item in snapshot.scopes_for("propose_hypothesis_evidence_relation")
        if item.hypothesis_ref == "H1"
    )
    schema = _schema_for_profile(profile)
    props = _variant_for_scope(schema, h1.scope_ref)["properties"]
    assert _enum_values(props["hypothesis_ref"]) == {"H1"}
    assert _enum_values(props["hypothesis_relation_evidence_ref"]) == {"E1"}
    assert "E2" not in _enum_values(props["hypothesis_relation_evidence_ref"])


def test_snapshot_multi_directive_never_exposes_directive_evidence_cross_product():
    states = (
        AdaptiveDirectiveDispositionState(
            directive_id="D1",
            parent_obligation_id="P1",
            eligible_evidence_refs=("E1",),
        ),
        AdaptiveDirectiveDispositionState(
            directive_id="D2",
            parent_obligation_id="P2",
            eligible_evidence_refs=("E2",),
        ),
    )
    profile = _snapshot_profile(
        ActionScopeSeed(
            action="disposition_research_directive",
            parent_obligation_id="P1",
            directive_id="D1",
            evidence_refs=("E1",),
        ),
        ActionScopeSeed(
            action="disposition_research_directive",
            parent_obligation_id="P2",
            directive_id="D2",
            evidence_refs=("E2",),
        ),
        effective_evidence=("E1", "E2"),
        adaptive_states=states,
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    assert {
        (item.directive_id, item.evidence_refs)
        for item in snapshot.scopes_for("disposition_research_directive")
    } == {("D1", ("E1",)), ("D2", ("E2",))}

    schema = _schema_for_profile(profile)
    for scope in snapshot.scopes_for("disposition_research_directive"):
        props = _variant_for_scope(schema, scope.scope_ref)["properties"]
        assert _enum_values(props["directive_id"]) == {scope.directive_id}
        assert _enum_values(props["directive_evidence_ref"]) == set(scope.evidence_refs)


@pytest.mark.parametrize("action", ("resolve_semantics", "propose_branches"))
def test_snapshot_parent_grounded_actions_reject_sibling_evidence_domains(action):
    seeds = (
        ActionScopeSeed(
            action=action,
            parent_obligation_id="P1",
            evidence_refs=("E1",),
            handle_refs=("H1",),
        ),
        ActionScopeSeed(
            action=action,
            parent_obligation_id="P2",
            evidence_refs=("E2",),
            handle_refs=("H2",),
        ),
    )
    profile = _snapshot_profile(
        *seeds,
        effective_evidence=("E1", "E2"),
        semantic_parents=("P1", "P2"),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    p1 = next(
        item
        for item in snapshot.scopes_for(action)
        if item.parent_obligation_id == "P1"
    )
    assert p1.evidence_refs == ("E1",)
    schema = _schema_for_profile(profile)
    props = _variant_for_scope(schema, p1.scope_ref)["properties"]
    evidence_field = (
        "semantic_evidence_ref"
        if action == "resolve_semantics"
        else "branch_evidence_ref"
    )
    assert _enum_values(props[evidence_field]) == {"E1"}
    assert "E2" not in _enum_values(props[evidence_field])
    if action == "propose_branches":
        encoded = str(props["branch_candidates"])
        assert "H1" in encoded
        assert "H2" not in encoded


def test_snapshot_ready_derived_task_keeps_task_parent_trigger_and_handles_correlated():
    profile = _snapshot_profile(
        ActionScopeSeed(
            action="run_analytics",
            parent_obligation_id="P1",
            task_id="T1",
            capability_key="breakdown",
            obligation_ids=("P1",),
            evidence_refs=("E1",),
            handle_refs=("M1", "D1"),
            metric_handles=("M1",),
            dimension_handles=("D1",),
        ),
        ActionScopeSeed(
            action="run_analytics",
            parent_obligation_id="P2",
            task_id="T2",
            capability_key="breakdown",
            obligation_ids=("P2",),
            evidence_refs=("E2",),
            handle_refs=("M2", "D2"),
            metric_handles=("M2",),
            dimension_handles=("D2",),
        ),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    t1 = next(
        item for item in snapshot.scopes_for("run_analytics") if item.task_id == "T1"
    )
    schema = _schema_for_profile(profile)
    props = _variant_for_scope(schema, t1.scope_ref)["properties"]
    assert _enum_values(props["derived_task_id"]) == {"T1"}
    assert _enum_values(props["derived_parent_obligation_id"]) == {"P1"}
    assert _enum_values(props["derived_evidence_ref"]) == {"E1"}
    assert _enum_values(props["metric_handles"]) == {"M1"}
    assert _enum_values(props["dimension_handles"]) == {"D1"}
    assert "M2" not in _enum_values(props["metric_handles"])


def test_stale_snapshot_ref_fails_closed_against_new_current_state():
    seed = ActionScopeSeed(action="finish")
    old = _snapshot_profile(seed, state_version="apsv_N")
    current = _snapshot_profile(seed, state_version="apsv_N_plus_1")
    old_snapshot = old.applicability_snapshot
    assert old_snapshot is not None
    scope = old_snapshot.scopes_for("finish")[0]

    with pytest.raises(ValueError, match="stale applicability snapshot"):
        ResearchManagerLoop._parse_scoped_decision(
            {
                "snapshot_ref": old_snapshot.snapshot_ref,
                "choice": {
                    "scope_ref": scope.scope_ref,
                    "action": "finish",
                },
            },
            availability=current,
        )


def test_action_scope_mismatch_and_unknown_scope_fail_closed():
    seed = ActionScopeSeed(
        action="disposition_research_directive",
        parent_obligation_id="P",
        directive_id="D",
        evidence_refs=("E",),
    )
    profile = _snapshot_profile(
        seed,
        effective_evidence=("E",),
        adaptive_states=(
            AdaptiveDirectiveDispositionState(
                directive_id="D",
                parent_obligation_id="P",
                eligible_evidence_refs=("E",),
            ),
        ),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    scope = snapshot.scopes_for("disposition_research_directive")[0]

    with pytest.raises(ValueError, match="escape selected applicability scope"):
        ResearchManagerLoop._parse_scoped_decision(
            {
                "snapshot_ref": snapshot.snapshot_ref,
                "choice": {
                    "scope_ref": scope.scope_ref,
                    "action": "finish",
                },
            },
            availability=profile,
        )

    with pytest.raises(KeyError, match="unknown applicability scope"):
        ResearchManagerLoop._parse_scoped_decision(
            {
                "snapshot_ref": snapshot.snapshot_ref,
                "choice": {
                    "scope_ref": "aps_unknown",
                    "action": "finish",
                },
            },
            availability=profile,
        )


def test_candidate_escape_from_selected_scope_is_rejected():
    seed = ActionScopeSeed(
        action="disposition_research_directive",
        parent_obligation_id="P",
        directive_id="D",
        evidence_refs=("E1",),
    )
    profile = _snapshot_profile(
        seed,
        effective_evidence=("E1",),
        adaptive_states=(
            AdaptiveDirectiveDispositionState(
                directive_id="D",
                parent_obligation_id="P",
                eligible_evidence_refs=("E1",),
            ),
        ),
    )
    snapshot = profile.applicability_snapshot
    assert snapshot is not None
    scope = snapshot.scopes_for("disposition_research_directive")[0]
    with pytest.raises(ValueError, match="escape selected applicability scope"):
        ResearchManagerLoop._parse_scoped_decision(
            {
                "snapshot_ref": snapshot.snapshot_ref,
                "choice": {
                    "scope_ref": scope.scope_ref,
                    "action": "disposition_research_directive",
                    "directive_id": "D",
                    "directive_evidence_ref": "E_INVENTED",
                    "directive_disposition": "NO_MATERIAL_DIRECTION",
                    "directive_reason": "bounded",
                },
            },
            availability=profile,
        )


def test_snapshot_identity_is_invariant_to_candidate_order_permutation():
    a = ActionScopeSeed(
        action="inspect_evidence",
        evidence_refs=("E1",),
    )
    b = ActionScopeSeed(
        action="request_clarification",
        obligation_ids=("P1",),
    )
    first = _snapshot_profile(
        a,
        b,
        state_version="apsv_order",
    )
    second = _snapshot_profile(
        b,
        a,
        state_version="apsv_order",
    )
    assert first.applicability_snapshot is not None
    assert second.applicability_snapshot is not None
    assert (
        first.applicability_snapshot.snapshot_ref
        == second.applicability_snapshot.snapshot_ref
    )
    assert (
        first.applicability_snapshot.model_view()
        == second.applicability_snapshot.model_view()
    )
