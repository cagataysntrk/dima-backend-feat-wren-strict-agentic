"""D10-U provider-free proof for one canonical ManagerActionSet owner."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.manager_loop import ManagerActionKind, ResearchManagerLoop
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ManagerState,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.manager_tools import ManagerToolRegistry
from app.v2.models import EvidenceArtifact, ResearchTask
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskService,
)
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


def _filter(ref: str) -> SemanticActionRef:
    return SemanticActionRef(ref=ref, kind="filter")


def _period(ref: str) -> SemanticActionRef:
    return SemanticActionRef(ref=ref, kind="period")


def _hydration_loop(*aliases: str) -> ResearchManagerLoop:
    loop = object.__new__(ResearchManagerLoop)
    loop._handle_by_alias = {
        alias: f"sem_{index:024x}"
        for index, alias in enumerate(aliases, start=1)
    }
    return loop


def _hydrate_compile_validate(
    *,
    action_set,
    action_kind: str,
    aliases: tuple[str, ...],
    payload: dict | None = None,
):
    rows = _instances(action_set, action_kind)
    assert len(rows) == 1
    instance = rows[0]
    loop = _hydration_loop(*aliases)
    decision = loop._hydrate_action_choice(
        action_instance=instance,
        payload=payload or {},
    )
    call = loop._compile_tool(
        decision=decision,
        message_id="turn-parity",
        source_hash="0" * 64,
        request_ref="req-parity",
        runtime=None,
    )
    validated = ManagerToolRegistry().validate(
        call,
        state=ManagerState.CONTRACT_ACCEPTED,
        has_accepted_contract=True,
    )
    return instance, decision, call, validated, loop


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


def _rank() -> NextTestContractState:
    return NextTestContractState(
        task_kind="RANK",
        capability_key="ranking",
        required_kinds=("dimension", "metric"),
        allowed_kinds=("metric", "dimension", "filter", "period"),
        required_params=("ranking_direction", "ranking_limit"),
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



def test_direct_actionset_materializability_positive_matrix_reaches_existing_tool_contract():
    cases = (
        (
            TaskActionState(
                task_id="T_PERF",
                question_id="U_PERF",
                task_kind="QUERY",
                capability_key="performance",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _filter("h_f"),
                    _period("h_p"),
                ),
            ),
            "run_analytics",
            ("h_m", "h_f", "h_p"),
        ),
        (
            TaskActionState(
                task_id="T_BREAK",
                question_id="U_BREAK",
                task_kind="BREAKDOWN",
                capability_key="breakdown",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _dimension("h_d"),
                    _filter("h_f"),
                    _period("h_p"),
                ),
            ),
            "run_analytics",
            ("h_m", "h_d", "h_f", "h_p"),
        ),
        (
            TaskActionState(
                task_id="T_RANK",
                question_id="U_RANK",
                task_kind="RANK",
                capability_key="ranking",
                origin="USER_SEED",
                semantic_refs=(_metric("h_m"), _dimension("h_d")),
                ranking_direction="desc",
                ranking_limit=5,
            ),
            "run_analytics",
            ("h_m", "h_d"),
        ),
        (
            TaskActionState(
                task_id="T_COMPARE",
                question_id="U_COMPARE",
                task_kind="COMPARE",
                capability_key="comparison",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _comparison("h_c"),
                    _period("h_p"),
                    _filter("h_f"),
                ),
            ),
            "run_analytics",
            ("h_m", "h_c", "h_p", "h_f"),
        ),
        (
            TaskActionState(
                task_id="T_REL",
                question_id="U_REL",
                task_kind="RELATIONSHIP",
                capability_key="relationship",
                origin="USER_SEED",
                semantic_refs=(_metric("h_m"), _dimension("h_d")),
            ),
            "run_relationship",
            ("h_m", "h_d"),
        ),
    )

    for task, action_kind, aliases in cases:
        action_set = _build(ready_tasks=(task,))
        instance, decision, _call, validated, _loop = _hydrate_compile_validate(
            action_set=action_set,
            action_kind=action_kind,
            aliases=aliases,
        )
        assert instance.reason_codes == ("READY_RESEARCH_TASK",)
        assert decision.research_task_id == task.task_id
        assert validated.research_task_id == task.task_id

        if action_kind == "run_analytics":
            assert validated.metric_handles
            if task.capability_key in {"breakdown", "ranking"}:
                assert validated.dimension_handles
            if task.capability_key == "ranking":
                assert validated.ranking_direction == "desc"
                assert validated.limit == 5
            if task.capability_key == "comparison":
                assert validated.comparison_handle is not None
        else:
            assert validated.focus_handles
            assert len(validated.counterpart_handles) == 1


@pytest.mark.parametrize(
    ("task", "action_kind"),
    (
        (
            TaskActionState(
                task_id="BAD_RANK_NO_DIM",
                question_id="U",
                task_kind="RANK",
                capability_key="ranking",
                origin="USER_SEED",
                semantic_refs=(_metric("h_m"),),
                ranking_direction="desc",
                ranking_limit=5,
            ),
            "run_analytics",
        ),
        (
            TaskActionState(
                task_id="BAD_RANK_MULTI_METRIC",
                question_id="U",
                task_kind="RANK",
                capability_key="ranking",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m1"),
                    _metric("h_m2"),
                    _dimension("h_d"),
                ),
                ranking_direction="desc",
                ranking_limit=5,
            ),
            "run_analytics",
        ),
        (
            TaskActionState(
                task_id="BAD_REL_NO_DIM",
                question_id="U",
                task_kind="RELATIONSHIP",
                capability_key="relationship",
                origin="USER_SEED",
                semantic_refs=(_metric("h_m"),),
            ),
            "run_relationship",
        ),
        (
            TaskActionState(
                task_id="BAD_REL_MULTI_DIM",
                question_id="U",
                task_kind="RELATIONSHIP",
                capability_key="relationship",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _dimension("h_d1"),
                    _dimension("h_d2"),
                ),
            ),
            "run_relationship",
        ),
        (
            TaskActionState(
                task_id="BAD_COMPARE_NONE",
                question_id="U",
                task_kind="COMPARE",
                capability_key="comparison",
                origin="USER_SEED",
                semantic_refs=(_metric("h_m"),),
            ),
            "run_analytics",
        ),
        (
            TaskActionState(
                task_id="BAD_COMPARE_MULTI",
                question_id="U",
                task_kind="COMPARE",
                capability_key="comparison",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _comparison("h_c1"),
                    _comparison("h_c2"),
                ),
            ),
            "run_analytics",
        ),
        (
            TaskActionState(
                task_id="BAD_TEMPORAL_MULTI",
                question_id="U",
                task_kind="QUERY",
                capability_key="performance",
                origin="USER_SEED",
                semantic_refs=(
                    _metric("h_m"),
                    _period("h_p1"),
                    _period("h_p2"),
                ),
            ),
            "run_analytics",
        ),
    ),
)
def test_direct_actionset_negative_materializability_matrix_is_never_exposed(
    task,
    action_kind,
):
    action_set = _build(ready_tasks=(task,))
    assert not _instances(action_set, action_kind)


def test_ready_derived_analytics_hydration_is_lossless_across_all_bound_identity():
    task = TaskActionState(
        task_id="T_DERIVED_COMPARE",
        question_id="P_COMPARE",
        task_kind="COMPARE",
        capability_key="comparison",
        origin="AGENT_DERIVED",
        semantic_refs=(
            _metric("h_m"),
            _filter("h_f"),
            _period("h_p"),
            _comparison("h_c"),
        ),
        parent_obligation_id="P_COMPARE",
        trigger_evidence_ref="E_COMPARE",
    )
    action_set = _build(ready_tasks=(task,))
    instance, decision, _call, validated, _loop = _hydrate_compile_validate(
        action_set=action_set,
        action_kind="run_analytics",
        aliases=("h_m", "h_f", "h_p", "h_c"),
    )

    assert instance.binding("research_task_id") == task.task_id
    assert decision.research_task_id == task.task_id
    assert validated.research_task_id == task.task_id
    assert validated.derived_task_id == task.task_id
    assert validated.derived_parent_obligation_id == "P_COMPARE"
    assert validated.derived_capability_key == ManagerCapabilityKey.COMPARISON
    assert validated.derived_evidence_ref == "E_COMPARE"
    assert validated.metric_handles
    assert validated.filter_handles
    assert validated.period_handle is not None
    assert validated.comparison_handle is not None


def test_adaptive_branch_hydration_materializes_through_real_research_task_service():
    action_set = _build(
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P1",
                "performance",
                "E1",
                (_metric("h_m"), _dimension("h_d")),
            ),
        ),
    )
    branch = _instances(action_set, "propose_branches")
    assert len(branch) == 1
    instance = branch[0]
    loop = _hydration_loop("h_m", "h_d")
    decision = loop._hydrate_action_choice(
        action_instance=instance,
        payload={
            "branch_candidates": (
                {
                    "capability_key": "breakdown",
                    "material_reason": "Verified Evidence supports one bounded breakdown.",
                },
            ),
        },
    )
    assert decision.branch_parent_obligation_id == "P1"
    assert decision.branch_evidence_ref == "E1"
    assert len(decision.branch_candidates) == 1
    candidate = decision.branch_candidates[0]

    parent_task = ResearchTask(
        task_id="seed:P1",
        question_id="P1",
        task_kind="QUERY",
        input_refs=("sem_parent",),
        origin="USER_SEED",
        state="complete",
    )
    evidence = EvidenceArtifact(
        artifact_id="E1",
        task_id=parent_task.task_id,
        obligation_ids=("P1",),
        query_contract_refs=("QC1",),
        evidence_kind="standard_analytics",
        verified=True,
    )
    ledger = UserObligationLedger(
        lineage_id="L1",
        version=1,
        items=(
            ObligationLedgerItem(
                obligation_id="P1",
                capability_key=ManagerCapabilityKey.PERFORMANCE,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                status=ObligationStatus.VERIFIED,
                source_refs=("SRC1",),
                semantic_handle_refs=("sem_parent",),
                evidence_refs=("E1",),
                introduced_in_version=1,
            ),
        ),
    )
    runtime = SimpleNamespace(
        ledger=ledger,
        snapshot=SimpleNamespace(
            evidence_refs=("E1",),
            inspected_evidence_refs=("E1",),
        ),
    )
    store = SimpleNamespace(get=lambda ref: evidence if ref == "E1" else None)
    proposal = DerivedResearchTaskProposal(
        task_id=candidate.task_id,
        task_kind=ResearchTaskService.task_kind_for_capability(
            candidate.capability_key
        ),
        parent_task_id=parent_task.task_id,
        parent_obligation_id=decision.branch_parent_obligation_id,
        trigger_evidence_ref=decision.branch_evidence_ref,
        input_refs=loop._decode_handles(candidate.input_handles),
        material_reason=candidate.material_reason,
    )
    materialized = ResearchTaskService().materialize_derived(
        runtime=runtime,
        evidence_store=store,
        parent_task=parent_task,
        proposal=proposal,
    )

    assert materialized.task_id == candidate.task_id
    assert materialized.parent_obligation_id == "P1"
    assert materialized.trigger_evidence_ref == "E1"
    assert materialized.input_refs == (
        loop._handle_by_alias["h_m"],
        loop._handle_by_alias["h_d"],
    )


def test_root_next_test_action_hydration_preserves_parent_trigger_and_inputs():
    action_set = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("h_m"), _dimension("h_d")),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_breakdown(),),
            ),
        ),
    )
    rows = _instances(action_set, "propose_hypothesis_with_next_test")
    assert len(rows) == 1
    instance = rows[0]
    loop = _hydration_loop("h_m", "h_d")
    decision = loop._hydrate_action_choice(
        action_instance=instance,
        payload={
            "hypothesis_statement": "One bounded candidate explanation.",
            "hypothesis_limitations": (),
            "next_test_material_reason": "Test with one governed breakdown.",
            "next_test_ranking_direction": None,
            "next_test_ranking_limit": None,
        },
    )

    assert decision.action == ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST
    assert decision.hypothesis_parent_obligation_id == "R1"
    assert decision.hypothesis_trigger_evidence_refs == ("E_ROOT",)
    assert decision.next_test_trigger_evidence_ref == "E_ROOT"
    assert decision.next_test_input_handles == ("h_m", "h_d")


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


def test_branch_projection_does_not_advertise_rank_with_multiple_metrics():
    action_set = _build(
        parent_evidence_states=(
            ParentEvidenceActionState(
                "P1",
                "relationship",
                "E1",
                (
                    _metric("M1"),
                    _metric("M2"),
                    _dimension("D1"),
                ),
            ),
        ),
    )

    branches = _instances(action_set, "propose_branches")
    assert len(branches) == 1
    branch_schema = dict(branches[0].cognitive_schema)["branch_candidates"]
    capabilities = set(
        branch_schema["items"]["properties"]["capability_key"]["enum"]
    )
    assert "ranking" not in capabilities
    assert "breakdown" in capabilities
    assert "relationship" in capabilities


def test_ready_rank_task_with_multiple_metrics_is_not_executable_action():
    action_set = _build(
        ready_tasks=(
            TaskActionState(
                task_id="T_RANK_BAD",
                question_id="P1",
                task_kind="RANK",
                capability_key="ranking",
                origin="AGENT_DERIVED",
                semantic_refs=(
                    _metric("M1"),
                    _metric("M2"),
                    _dimension("D1"),
                ),
                parent_obligation_id="P1",
                trigger_evidence_ref="E1",
            ),
        ),
    )

    assert not _instances(action_set, "run_analytics")


def test_root_next_test_rank_requires_lossless_exact_metric_cardinality():
    bad = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(
                    _metric("M1"),
                    _metric("M2"),
                    _dimension("D1"),
                ),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_rank(),),
            ),
        ),
    )
    assert not _instances(bad, "propose_hypothesis_with_next_test")

    good = _build(
        root_states=(
            RootActionState(
                root_id="R1",
                semantic_refs=(_metric("M1"), _dimension("D1")),
                evidence_refs=("E_ROOT",),
                next_test_evidence_refs=("E_ROOT",),
                hypotheses=(),
                next_test_contracts=(_rank(),),
            ),
        ),
    )
    rows = _instances(good, "propose_hypothesis_with_next_test")
    assert len(rows) == 1
    assert rows[0].binding("next_test_task_kind") == "RANK"



def test_ready_relationship_hydration_preserves_exact_research_task_identity():
    action_set = _build(
        ready_tasks=(
            TaskActionState(
                task_id="T_REL_READY",
                question_id="P_REL",
                task_kind="RELATIONSHIP",
                capability_key="relationship",
                origin="AGENT_DERIVED",
                semantic_refs=(_metric("M_REL"), _dimension("D_REL")),
                parent_obligation_id="P_REL",
                trigger_evidence_ref="E_REL",
            ),
        ),
    )
    rows = _instances(action_set, "run_relationship")
    assert len(rows) == 1
    instance = rows[0]
    assert instance.binding("task_id") == "T_REL_READY"

    loop = object.__new__(ResearchManagerLoop)
    decision = loop._hydrate_action_choice(
        action_instance=instance,
        payload={},
    )

    # Exact READY task identity is server-owned authority and must survive
    # opaque action_ref hydration; reconstructing seed:{obligation} is lossy.
    assert decision.research_task_id == "T_REL_READY"
    assert decision.relationship_obligation_id == "P_REL"
    assert decision.focus_handles == ("M_REL",)
    assert decision.counterpart_handles == ("D_REL",)



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
    final_turn_caps = set(
        branch_schema["items"]["properties"]["capability_key"]["enum"]
    )
    assert "ranking" not in final_turn_caps
    assert {"performance", "breakdown", "relationship"}.issubset(final_turn_caps)



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
    ordinary_caps = set(
        branch_schema["items"]["properties"]["capability_key"]["enum"]
    )
    assert "ranking" in ordinary_caps


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
