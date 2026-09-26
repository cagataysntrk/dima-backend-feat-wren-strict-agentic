"""D10-U provider-free proof for one canonical ManagerActionSet owner."""

from __future__ import annotations

import pytest

from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.manager_action_set import (
    DirectiveActionState,
    HypothesisActionState,
    InspectableEvidenceState,
    ManagerActionSetBuilder,
    ManagerActionSetContext,
    NextTestContractState,
    ParentEvidenceActionState,
    RootActionState,
    SemanticActionRef,
    TaskActionState,
)


def _metric(ref: str) -> SemanticActionRef:
    return SemanticActionRef(ref=ref, kind="metric")


def _dimension(ref: str) -> SemanticActionRef:
    return SemanticActionRef(ref=ref, kind="dimension")


def _comparison(ref: str) -> SemanticActionRef:
    return SemanticActionRef(ref=ref, kind="comparison")


def _query() -> NextTestContractState:
    return NextTestContractState(
        task_kind="QUERY",
        capability_key="performance",
        required_kinds=("metric",),
        allowed_kinds=("metric", "filter", "period"),
    )


def _breakdown() -> NextTestContractState:
    return NextTestContractState(
        task_kind="BREAKDOWN",
        capability_key="breakdown",
        required_kinds=("dimension", "metric"),
        allowed_kinds=("metric", "dimension", "filter", "period"),
    )


def _compare() -> NextTestContractState:
    return NextTestContractState(
        task_kind="COMPARE",
        capability_key="comparison",
        required_kinds=("comparison", "metric"),
        allowed_kinds=("metric", "comparison", "filter", "period"),
    )


def _build(**updates):
    values = {
        "state_version": "prog_N",
        "remaining_research_turns": 4,
    }
    values.update(updates)
    return ManagerActionSetBuilder.build(ManagerActionSetContext(**values))


def _instances(action_set, action: str):
    return tuple(
        item for item in action_set.action_instances if item.action_kind == action
    )


def test_root_bootstrap_exposes_composite_action_directly_from_real_preconditions():
    action_set = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("h9"), _metric("h10")),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_query(),),
            ),
        ),
    )

    composite = _instances(action_set, "propose_hypothesis_with_next_test")
    assert len(composite) == 1
    instance = composite[0]
    assert instance.binding("parent_obligation_id") == "R1"
    assert instance.binding("semantic_handles") == ("h9", "h10")
    assert instance.binding("trigger_evidence_ref") == "E_ROOT"
    assert instance.binding("next_test_task_kind") == "QUERY"

    schema = action_set.provider_schema()
    variants = schema["properties"]["choice"]["anyOf"]
    selected = next(
        item
        for item in variants
        if instance.action_ref
        in item["properties"]["action_ref"]["enum"]
    )
    # Server identities are not provider/model fields.
    assert set(selected["properties"]) == {
        "action_ref",
        "hypothesis_statement",
        "hypothesis_limitations",
        "next_test_material_reason",
        "next_test_ranking_direction",
        "next_test_ranking_limit",
    }


def test_root_composite_is_absent_when_required_semantic_shape_is_missing():
    action_set = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("h9"),),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_breakdown(),),
            ),
        ),
    )
    assert not _instances(action_set, "propose_hypothesis_with_next_test")


def test_multi_root_never_produces_cross_parent_handle_or_evidence_combinations():
    action_set = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("h_r1"),),
                evidence_refs=("E_R1",),
                next_test_evidence_refs=("E_R1",),
                hypotheses=(),
                next_test_contracts=(_query(),),
            ),
            RootActionState(
                root_id="R2",
                semantic_refs=(_metric("h_r2"),),
                evidence_refs=("E_R2",),
                next_test_evidence_refs=("E_R2",),
                hypotheses=(),
                next_test_contracts=(_query(),),
            ),
        ),
    )
    rows = {
        (
            item.binding("parent_obligation_id"),
            item.binding("semantic_handles"),
            item.binding("trigger_evidence_ref"),
        )
        for item in _instances(
            action_set, "propose_hypothesis_with_next_test"
        )
    }
    assert rows == {
        ("R1", ("h_r1",), "E_R1"),
        ("R2", ("h_r2",), "E_R2"),
    }


def test_multi_hypothesis_relation_keeps_post_test_evidence_bound_to_hypothesis():
    root = RootActionState(
        root_id="R",
        semantic_refs=(_metric("h"),),
        evidence_refs=("E1", "E2"),
        hypotheses=(
            HypothesisActionState(
                hypothesis_ref="H1",
                semantic_refs=(_metric("h"),),
                admissible_evidence_refs=("E1",),
                pending_relation_evidence_refs=("E1",),
            ),
            HypothesisActionState(
                hypothesis_ref="H2",
                semantic_refs=(_metric("h"),),
                admissible_evidence_refs=("E2",),
                pending_relation_evidence_refs=("E2",),
            ),
        ),
        next_test_contracts=(_query(),),
    )
    action_set = _build(root_states=(root,))
    pairs = {
        (
            item.binding("hypothesis_ref"),
            item.binding("evidence_ref"),
        )
        for item in _instances(
            action_set, "propose_hypothesis_evidence_relation"
        )
    }
    assert pairs == {("H1", "E1"), ("H2", "E2")}


def test_multi_directive_never_produces_directive_evidence_cross_product():
    action_set = _build(
        directive_states=(
            DirectiveActionState("D1", "P1", ("E1",)),
            DirectiveActionState("D2", "P2", ("E2",)),
        )
    )
    pairs = {
        (
            item.binding("directive_id"),
            item.binding("parent_obligation_id"),
            item.binding("evidence_ref"),
        )
        for item in _instances(
            action_set, "disposition_research_directive"
        )
    }
    assert pairs == {("D1", "P1", "E1"), ("D2", "P2", "E2")}


def test_resolve_semantics_parent_cannot_select_sibling_evidence():
    action_set = _build(
        directive_states=(
            DirectiveActionState("D1", "P1", ("E1",)),
            DirectiveActionState("D2", "P2", ("E2",)),
        ),
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P1", "performance", "E1", (_metric("H1"),)
            ),
            ParentEvidenceActionState(
                "P2", "performance", "E2", (_metric("H2"),)
            ),
        ),
    )
    pairs = {
        (
            item.binding("parent_obligation_id"),
            item.binding("evidence_ref"),
        )
        for item in _instances(action_set, "resolve_semantics")
    }
    assert pairs == {("P1", "E1"), ("P2", "E2")}


def test_propose_branch_parent_evidence_and_handles_remain_correlated():
    action_set = _build(
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P1",
                "breakdown",
                "E1",
                (_metric("M1"), _dimension("D1")),
            ),
            ParentEvidenceActionState(
                "P2",
                "breakdown",
                "E2",
                (_metric("M2"), _dimension("D2")),
            ),
        ),
    )
    rows = {
        (
            item.binding("parent_obligation_id"),
            item.binding("evidence_ref"),
            dict(item.binding("branch_handles_by_capability")).get("breakdown"),
        )
        for item in _instances(action_set, "propose_branches")
    }
    assert ("P1", "E1", ("M1", "D1")) in rows
    assert ("P2", "E2", ("M2", "D2")) in rows
    assert ("P1", "E2", ("M2", "D2")) not in rows


def test_ready_derived_task_is_one_server_bound_execution_instance():
    action_set = _build(
        ready_tasks=(
            TaskActionState(
                task_id="T1",
                question_id="P1",
                task_kind="BREAKDOWN",
                capability_key="breakdown",
                origin="AGENT_DERIVED",
                semantic_refs=(_metric("M1"), _dimension("D1")),
                parent_obligation_id="P1",
                trigger_evidence_ref="E1",
            ),
            TaskActionState(
                task_id="T2",
                question_id="P2",
                task_kind="BREAKDOWN",
                capability_key="breakdown",
                origin="AGENT_DERIVED",
                semantic_refs=(_metric("M2"), _dimension("D2")),
                parent_obligation_id="P2",
                trigger_evidence_ref="E2",
            ),
        )
    )
    rows = {
        (
            item.binding("derived_task_id"),
            item.binding("derived_parent_obligation_id"),
            item.binding("derived_evidence_ref"),
            item.binding("metric_handles"),
            item.binding("dimension_handles"),
        )
        for item in _instances(action_set, "run_analytics")
    }
    assert rows == {
        ("T1", "P1", "E1", ("M1",), ("D1",)),
        ("T2", "P2", "E2", ("M2",), ("D2",)),
    }


def test_two_genuinely_legal_root_directions_become_two_action_instances():
    root = RootActionState(
        root_id="R",
        semantic_refs=(
            _metric("M"),
            _dimension("D"),
            _comparison("C"),
        ),
        evidence_refs=("E",),
                next_test_evidence_refs=("E",),
        hypotheses=(),
        next_test_contracts=(_query(), _breakdown(), _compare()),
    )
    action_set = _build(root_states=(root,))
    task_families = {
        item.context("task_family")
        for item in _instances(
            action_set, "propose_hypothesis_with_next_test"
        )
    }
    assert task_families == {"QUERY", "BREAKDOWN", "COMPARE"}



def test_last_research_turn_with_executable_adapt_directive_is_completion_critical():
    action_set = _build(
        # The current cognition turn has already been charged by ManagerRuntime.
        # Zero therefore means there is no later Research turn after this choice.
        remaining_research_turns=0,
        directive_states=(
            DirectiveActionState("D1", "P_REL", ("E_REL",)),
        ),
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P_REL",
                "relationship",
                "E_REL",
                (_metric("M_REL"), _dimension("D_REL")),
            ),
            ParentEvidenceActionState(
                "P_OTHER",
                "breakdown",
                "E_OTHER",
                (_metric("M_OTHER"), _dimension("D_OTHER")),
            ),
        ),
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("M_ROOT"),),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_query(),),
            ),
        ),
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E_OLD",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )

    # With one cognition turn left, an executable completion-relevant ADAPT
    # directive must not compete with work that necessarily needs a later turn.
    assert set(action_set.available_actions) == {
        "disposition_research_directive",
        "propose_branches",
    }

    dispositions = _instances(action_set, "disposition_research_directive")
    assert len(dispositions) == 1
    assert dispositions[0].binding("directive_id") == "D1"
    assert dispositions[0].binding("parent_obligation_id") == "P_REL"
    assert dispositions[0].binding("evidence_ref") == "E_REL"

    branches = _instances(action_set, "propose_branches")
    assert len(branches) == 1
    assert branches[0].binding("parent_obligation_id") == "P_REL"
    assert branches[0].binding("evidence_ref") == "E_REL"
    branch_schema = dict(branches[0].cognitive_schema)["branch_candidates"]
    assert branch_schema["minItems"] == 1
    assert branch_schema["maxItems"] == 1



def test_final_turn_directive_without_material_path_is_not_greenwashed():
    action_set = _build(
        remaining_research_turns=0,
        directive_states=(
            DirectiveActionState("D1", "P_REL", ("E_REL",)),
        ),
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E_OLD",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )

    # A terminal NO_MATERIAL_DIRECTION action is available, but the server has
    # no material same-turn branch/execution path.  Do not collapse the surface
    # to disposition-only: that would manufacture a negative finding to escape
    # the budget boundary rather than preserve bounded cognition.
    assert set(action_set.available_actions) == {
        "disposition_research_directive",
        "inspect_evidence",
        "finish",
    }
    assert not _instances(action_set, "propose_branches")


def test_completion_critical_projection_is_final_turn_only():
    action_set = _build(
        remaining_research_turns=1,
        directive_states=(
            DirectiveActionState("D1", "P_REL", ("E_REL",)),
        ),
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P_REL",
                "relationship",
                "E_REL",
                (_metric("M_REL"), _dimension("D_REL")),
            ),
        ),
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E_OLD",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )

    # With a later Research turn still available, ordinary bounded cognition
    # remains available; the scheduling rule must not become a global priority
    # layer or second availability authority.
    assert "disposition_research_directive" in action_set.available_actions
    assert "propose_branches" in action_set.available_actions
    assert "inspect_evidence" in action_set.available_actions
    assert "finish" in action_set.available_actions
    branches = _instances(action_set, "propose_branches")
    assert len(branches) == 1
    branch_schema = dict(branches[0].cognitive_schema)["branch_candidates"]
    assert branch_schema["maxItems"] > 1


def test_action_ref_is_state_bound_and_stale_choice_fails_closed():
    old = _build(
        state_version="prog_N",
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E1",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )
    current = _build(
        state_version="prog_N_plus_1",
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E1",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )
    old_ref = _instances(old, "inspect_evidence")[0].action_ref
    with pytest.raises(KeyError, match="unknown ManagerActionSet action_ref"):
        current.by_ref(old_ref)


def test_invented_action_ref_fails_closed():
    action_set = _build()
    with pytest.raises(KeyError, match="unknown ManagerActionSet action_ref"):
        action_set.resolve_choice(
            {"choice": {"action_ref": "act_invented"}}
        )


def test_choice_cannot_escape_selected_action_cognitive_contract():
    action_set = _build(
        inspectable_evidence=(
            InspectableEvidenceState(
                evidence_ref="E1",
                capability_keys=("performance",),
                evidence_kind="standard_analytics",
            ),
        ),
    )
    instance = _instances(action_set, "inspect_evidence")[0]
    with pytest.raises(ValueError, match="cognitive payload"):
        action_set.resolve_choice(
            {
                "choice": {
                    "action_ref": instance.action_ref,
                    "directive_reason": "escape",
                }
            }
        )


def test_candidate_order_permutation_does_not_change_action_set_identity():
    r1 = RootActionState(
        root_id="R1",
        semantic_refs=(_metric("M1"),),
        evidence_refs=("E1",),
        hypotheses=(),
        next_test_contracts=(_query(),),
    )
    r2 = RootActionState(
        root_id="R2",
        semantic_refs=(_metric("M2"),),
        evidence_refs=("E2",),
        hypotheses=(),
        next_test_contracts=(_query(),),
    )
    first = _build(root_states=(r1, r2))
    second = _build(root_states=(r2, r1))
    assert {
        item.action_ref for item in first.action_instances
    } == {
        item.action_ref for item in second.action_instances
    }
    assert first.model_view() == second.model_view()


def test_no_material_action_leaves_only_finish_when_clarification_is_not_grounded():
    action_set = _build()
    assert action_set.available_actions == ("finish",)


def test_grounded_clarification_is_a_bounded_action_without_model_owned_ids():
    action_set = _build(
        clarification_grounded=True,
        clarification_obligation_ids=("U1", "U2"),
    )
    clarification = _instances(action_set, "request_clarification")
    assert len(clarification) == 1
    instance = clarification[0]
    assert instance.binding("obligation_ids") == ("U1", "U2")
    variant = next(
        item
        for item in action_set.provider_schema()["properties"]["choice"]["anyOf"]
        if instance.action_ref in item["properties"]["action_ref"]["enum"]
    )
    assert set(variant["properties"]) == {
        "action_ref",
        "clarification_reason",
    }


def test_derived_semantic_registry_projection_is_exact_parent_and_evidence_scoped():
    registry = SemanticHandleRegistry()
    common = {
        "tenant_binding": "tenant-A",
        "context_version": "ctx-A",
        "target_kind": "dimension",
        "canonical_target": {"kind": "dimension"},
        "provenance_type": "AGENT_DERIVED",
    }
    wanted = registry.mint_from_resolver(
        **common,
        resolver_provenance_id="derived:wanted",
        parent_obligation_id="P1",
        trigger_evidence_ref="E1",
    )
    registry.mint_from_resolver(
        **common,
        resolver_provenance_id="derived:sibling",
        parent_obligation_id="P2",
        trigger_evidence_ref="E1",
    )
    registry.mint_from_resolver(
        **common,
        resolver_provenance_id="derived:other-evidence",
        parent_obligation_id="P1",
        trigger_evidence_ref="E2",
    )

    projected = registry.handles_for_parent(
        tenant_binding="tenant-A",
        context_version="ctx-A",
        parent_obligation_id="P1",
        trigger_evidence_ref="E1",
    )

    assert tuple(item.handle_id for item in projected) == (wanted.handle_id,)
    assert all(item.provenance_type == "AGENT_DERIVED" for item in projected)
