"""Focused provider-free proofs for optional Research goal late binding."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v2.capability_bindings import (
    CapabilityBindingValidator,
    ResearchGoalExecutionDisposition,
)
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    UserObligationLedger,
)
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.models import (
    ResearchTask,
    ResearchTaskKind,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.research_scheduler import ResearchTaskInvocationCompileError
from app.v2.research_tasks import (
    ResearchTaskLifecycleError,
    ResearchTaskRegistry,
    ResearchTaskService,
)
from app.v2.research_tools import ResearchToolRunner
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


TENANT = "goal-quarantine-tenant"
CONTEXT = "ctx-goal-quarantine-v1"


def _semantic_target(kind: str, name: str) -> ResolvedSemanticRef:
    target_kind = {
        "metric": SemanticTargetKind.METRIC,
        "dimension": SemanticTargetKind.DIMENSION,
    }[kind]
    return ResolvedSemanticRef(
        candidate_id=f"candidate:{name}",
        target_kind=target_kind,
        canonical_name=name,
        cube_names=("Operations",),
    )


def _mint(
    registry: SemanticHandleRegistry,
    *,
    kind: str,
    name: str,
    owner: str,
    binding_gate: bool = False,
):
    kwargs = dict(
        tenant_binding=TENANT,
        context_version=CONTEXT,
        target_kind=kind,
        canonical_target=_semantic_target(kind, name),
        provenance_type="USER_SOURCE",
        parent_obligation_id=owner,
    )
    if binding_gate:
        return registry.mint_from_binding_gate(
            candidate_id="cand_" + ("a" if kind == "metric" else "b") * 24,
            **kwargs,
        )
    return registry.mint_from_resolver(
        resolver_provenance_id=f"resolver:{owner}:{kind}:{name}",
        **kwargs,
    )


def _item(
    obligation_id: str,
    capability: ManagerCapabilityKey,
    *,
    source_refs: tuple[str, ...],
    semantic_handle_refs: tuple[str, ...] = (),
) -> ObligationLedgerItem:
    return ObligationLedgerItem(
        obligation_id=obligation_id,
        capability_key=capability,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=source_refs,
        semantic_handle_refs=semantic_handle_refs,
        introduced_in_version=1,
    )


def _runtime(
    ledger: UserObligationLedger,
    *,
    directives=(),
):
    return SimpleNamespace(
        ledger=ledger,
        accepted_contract=SimpleNamespace(research_directives=tuple(directives)),
        directive_dispositions=(),
        snapshot=SimpleNamespace(
            accepted_contract_id="atc-goal-quarantine",
            run_id="mgr-goal-quarantine",
            inspected_evidence_refs=(),
            evidence_refs=(),
            research_manager_turns=0,
        ),
        budget=SimpleNamespace(max_manager_turns=4),
    )


def _loop(
    *,
    spans: SourceSpanRegistry,
    handles: SemanticHandleRegistry,
) -> ResearchManagerLoop:
    loop = object.__new__(ResearchManagerLoop)
    loop._capabilities = ManagerCapabilityRegistry()
    loop._research_tool_runner = ResearchToolRunner()
    loop._research_tasks = ResearchTaskService()
    loop._root_cause_context = SimpleNamespace(
        semantic_handles=handles,
        tenant_binding=TENANT,
        context_version=CONTEXT,
    )
    loop._source_spans = spans
    loop._alias_by_handle = {}
    loop._handle_by_alias = {}
    return loop


def test_executable_root_is_not_exposed_as_goal_task_action():
    spans = SourceSpanRegistry()
    message_id = "turn-executable-root"
    spans.register_message(
        message_id=message_id,
        text="Makine duruşlarının nedenini araştır ve net geliri incele",
    )
    root_ref = spans.mint_exact(
        message_id=message_id,
        surface="Makine duruşlarının nedenini araştır",
    ).source_ref
    other_ref = spans.mint_exact(
        message_id=message_id,
        surface="net geliri incele",
    ).source_ref

    handles = SemanticHandleRegistry()
    root_metric = _mint(
        handles,
        kind="metric",
        name="downtime_minutes",
        owner="U_ROOT",
    )
    other_metric = _mint(
        handles,
        kind="metric",
        name="net_revenue",
        owner="U_OTHER",
    )
    root = _item(
        "U_ROOT",
        ManagerCapabilityKey.ROOT_CAUSE,
        source_refs=(root_ref,),
        semantic_handle_refs=(root_metric.handle_id,),
    )
    other = _item(
        "U_OTHER",
        ManagerCapabilityKey.PERFORMANCE,
        source_refs=(other_ref,),
        semantic_handle_refs=(other_metric.handle_id,),
    )
    ledger = UserObligationLedger(
        lineage_id="atl-executable-root",
        version=1,
        items=(root, other),
    )
    validator = CapabilityBindingValidator(
        semantic_handles=handles,
        capabilities=ManagerCapabilityRegistry(),
    )
    classification = validator.classify_research_goal_execution(
        root,
        tenant_binding=TENANT,
        context_version=CONTEXT,
        goal_authority_eligible=True,
    )
    assert classification.disposition == ResearchGoalExecutionDisposition.EXECUTABLE_NOW

    ready_other = ResearchTask(
        task_id="seed:U_OTHER",
        question_id="U_OTHER",
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(other_metric.handle_id,),
        origin="USER_SEED",
    )
    loop = _loop(spans=spans, handles=handles)
    action_set = loop._action_set(
        runtime=_runtime(ledger),
        observations=[],
        action_frontier=None,
        research_state=None,
        hypothesis_ledgers=None,
        evidence_store=None,
        research_tasks=(ready_other,),
        governed_semantic_inventory=(),
    )
    assert "run_analytics" in action_set.available_actions
    assert "propose_goal_task" not in action_set.available_actions


def test_incomplete_relationship_exposes_exactly_one_goal_task_action():
    spans = SourceSpanRegistry()
    message_id = "turn-deferred-relationship"
    spans.register_message(message_id=message_id, text="net gelir ilişkisini araştır")
    source_ref = spans.mint_exact(
        message_id=message_id,
        surface="net gelir ilişkisini araştır",
    ).source_ref

    handles = SemanticHandleRegistry()
    metric = _mint(
        handles,
        kind="metric",
        name="net_revenue",
        owner="U_REL",
    )
    relation = _item(
        "U_REL",
        ManagerCapabilityKey.RELATIONSHIP,
        source_refs=(source_ref,),
        semantic_handle_refs=(metric.handle_id,),
    )
    ledger = UserObligationLedger(
        lineage_id="atl-deferred-rel",
        version=1,
        items=(relation,),
    )
    validator = CapabilityBindingValidator(
        semantic_handles=handles,
        capabilities=ManagerCapabilityRegistry(),
    )
    classification = validator.classify_research_goal_execution(
        relation,
        tenant_binding=TENANT,
        context_version=CONTEXT,
        goal_authority_eligible=True,
    )
    assert (
        classification.disposition
        == ResearchGoalExecutionDisposition.MATERIALIZATION_REQUIRED
    )

    loop = _loop(spans=spans, handles=handles)
    action_set = loop._action_set(
        runtime=_runtime(ledger),
        observations=[],
        action_frontier=None,
        research_state=None,
        hypothesis_ledgers=None,
        evidence_store=None,
        research_tasks=(),
        governed_semantic_inventory=(),
    )
    goal_actions = tuple(
        item
        for item in action_set.action_instances
        if item.action_kind == "propose_goal_task"
    )
    assert len(goal_actions) == 1
    assert goal_actions[0].binding("parent_obligation_id") == "U_REL"
    assert goal_actions[0].binding("allowed_task_capabilities") == ("relationship",)


def test_goal_source_authority_is_parent_plus_typed_directive_never_sibling():
    spans = SourceSpanRegistry()
    message_id = "turn-source-quarantine"
    text = "duruş nedenini araştır; kanıt yeni yön gösterirse takip et; arıza sayısını göster"
    spans.register_message(message_id=message_id, text=text)
    parent_ref = spans.mint_exact(
        message_id=message_id,
        surface="duruş nedenini araştır",
    ).source_ref
    directive_ref = spans.mint_exact(
        message_id=message_id,
        surface="kanıt yeni yön gösterirse takip et",
    ).source_ref
    sibling_ref = spans.mint_exact(
        message_id=message_id,
        surface="arıza sayısını göster",
    ).source_ref

    ledger = UserObligationLedger(
        lineage_id="atl-source-quarantine",
        version=1,
        items=(
            _item(
                "U_ROOT",
                ManagerCapabilityKey.ROOT_CAUSE,
                source_refs=(parent_ref,),
            ),
            _item(
                "U_SIBLING",
                ManagerCapabilityKey.PERFORMANCE,
                source_refs=(sibling_ref,),
            ),
        ),
    )
    handles = SemanticHandleRegistry()
    loop = _loop(spans=spans, handles=handles)
    runtime = _runtime(
        ledger,
        directives=(
            SimpleNamespace(
                parent_obligation_id="U_ROOT",
                source_refs=(directive_ref,),
            ),
        ),
    )

    admitted = loop._goal_admitted_source_refs(
        runtime=runtime,
        parent_obligation_id="U_ROOT",
    )
    assert admitted == (parent_ref, directive_ref)
    assert sibling_ref not in admitted


def test_goal_derived_execution_requires_fresh_task_owned_handles_and_preserves_parent():
    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    parent_metric = _mint(
        handles,
        kind="metric",
        name="downtime_minutes",
        owner="U_ROOT",
        binding_gate=True,
    )
    task_id = "goal_" + "1" * 24
    task_metric = _mint(
        handles,
        kind="metric",
        name="downtime_minutes",
        owner=task_id,
        binding_gate=True,
    )
    parent = _item(
        "U_ROOT",
        ManagerCapabilityKey.ROOT_CAUSE,
        source_refs=("src_" + "a" * 24,),
        semantic_handle_refs=(parent_metric.handle_id,),
    )
    ledger = UserObligationLedger(
        lineage_id="atl-fresh-child",
        version=1,
        items=(parent,),
    )
    loop = _loop(spans=spans, handles=handles)
    runtime = SimpleNamespace(ledger=ledger)
    before = ledger.model_dump(mode="json")

    task = ResearchTask(
        task_id=task_id,
        question_id="U_ROOT",
        task_kind=ResearchTaskKind.QUERY.value,
        input_refs=(task_metric.handle_id,),
        origin="GOAL_DERIVED",
        parent_obligation_id="U_ROOT",
    )
    obligation, binding = loop._scheduled_binding(
        runtime=runtime,
        task=task,
        capability_key=ManagerCapabilityKey.PERFORMANCE,
    )
    assert obligation.obligation_id == "U_ROOT"
    assert binding.refs("metric") == (task_metric.handle_id,)
    assert runtime.ledger.model_dump(mode="json") == before

    stale_owner = task.model_copy(
        update={"input_refs": (parent_metric.handle_id,)}
    )
    with pytest.raises(
        ResearchTaskInvocationCompileError,
        match="fresh task-owned USER_SOURCE",
    ):
        loop._scheduled_binding(
            runtime=runtime,
            task=stale_owner,
            capability_key=ManagerCapabilityKey.PERFORMANCE,
        )


def test_goal_task_identity_and_registry_are_idempotent():
    service = ResearchTaskService()
    requests = (
        ("src_" + "a" * 24, "metric"),
        ("src_" + "b" * 24, "dimension"),
    )
    first = service.goal_task_id(
        accepted_contract_id="atc-goal-id",
        parent_obligation_id="U_REL",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        semantic_requests=requests,
    )
    reordered = service.goal_task_id(
        accepted_contract_id="atc-goal-id",
        parent_obligation_id="U_REL",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        semantic_requests=tuple(reversed(requests)),
    )
    changed = service.goal_task_id(
        accepted_contract_id="atc-goal-id",
        parent_obligation_id="U_REL",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        semantic_requests=((requests[0][0], "metric"),),
    )
    assert first == reordered
    assert changed != first

    task = ResearchTask(
        task_id=first,
        question_id="U_REL",
        task_kind=ResearchTaskKind.RELATIONSHIP.value,
        input_refs=("sem_" + "1" * 24, "sem_" + "2" * 24),
        origin="GOAL_DERIVED",
        parent_obligation_id="U_REL",
    )
    registry = ResearchTaskRegistry()
    assert registry.register(task) == task
    assert registry.register(task) == task

    conflict = task.model_copy(
        update={"input_refs": ("sem_" + "3" * 24,)}
    )
    with pytest.raises(
        ResearchTaskLifecycleError,
        match="identity conflict",
    ):
        registry.register(conflict)
