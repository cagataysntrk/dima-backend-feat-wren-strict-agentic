"""Bounded structured-action loop for the Day 6.5 Research Manager.

One model call proposes one next action. Runtime/gates/tools remain authoritative.
No chain-of-thought is requested, persisted or returned.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Literal

from pydantic import Field, model_validator

from app.v2.authority_invariants import evidence_belongs_to_parent_lineage
from app.v2.manager_action_set import (
    DirectiveActionState,
    GoalTaskActionState,
    HypothesisActionState,
    InspectableEvidenceState,
    ManagerActionSet,
    ManagerActionSetBuilder,
    ManagerActionSetContext,
    NextTestContractState,
    ParentEvidenceActionState,
    RootActionState,
    SemanticActionRef,
    TaskActionState,
)
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ManagerState,
    ResearchRunTerminal,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
    ResearchDirectiveDisposition,
    ResearchDirectiveDispositionStatus,
    ResearchDirectiveType,
    SemanticBindingRef,
    UserIntentEnvelope,
)
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.capability_bindings import CapabilityBindingValidator
from app.v2.manager_preacceptance import (
    FiniteAcceptanceStatus,
    PreAcceptanceController,
)
from app.v2.manager_progress import DynamicActionFrontier
from app.v2.hypothesis_proposals import (
    HypothesisProposalBoundary,
    HypothesisProposalError,
)
from app.v2.epistemics import (
    EvidenceLinkedFindingBuilder,
    EpistemicFindingError,
    RootCauseObligationVerifier,
)
from app.v2.root_cause_orchestration import (
    HypothesisNextTestBoundary,
    RootCauseBootstrapPolicy,
    RootCauseBootstrapStatus,
    RootCauseLoopContext,
    RootCauseOrchestrationError,
    root_cause_next_test_contract,
    root_cause_next_test_task_kinds,
)
from app.v2.manager_runtime import (
    ManagerBudgetError,
    ManagerRuntime,
    ManagerStateError,
)
from app.v2.research_state import ResearchStateView, build_research_state_view
from app.v2.research_tasks import (
    DerivedResearchTaskProposal,
    ResearchTaskMaterializationError,
    ResearchTaskRegistry,
    ResearchTaskService,
)
from app.v2.research_tools import (
    ResearchExecutionOutcome,
    ResearchToolRunner,
)
from app.v2.research_scheduler import (
    DeterministicResearchScheduler,
    ResearchTaskInvocationCompileError,
)
from app.v2.manager_tools import (
    ManagerToolCall,
    ManagerToolName,
)
from app.v2.models import (
    ConversationStateV2,
    EvidenceLinkedFinding,
    EpistemicLabel,
    FrozenModel,
    HypothesisEvidenceRelation,
    HypothesisStatus,
    HypothesisEvidenceRelationProposal,
    HypothesisLedgerState,
    HypothesisNextTestProposal,
    HypothesisProposal,
    ResearchTask,
    ResearchTaskKind,
)
from app.v2.source_spans import SourceSpanRegistry


class ManagerActionKind(StrEnum):
    RESOLVE_SEMANTICS = "resolve_semantics"
    PROPOSE_ACCEPTANCE = "propose_acceptance"
    PROPOSE_BRANCHES = "propose_branches"
    PROPOSE_GOAL_TASK = "propose_goal_task"
    DISPOSITION_RESEARCH_DIRECTIVE = "disposition_research_directive"
    PROPOSE_HYPOTHESIS = "propose_hypothesis"
    PROPOSE_HYPOTHESIS_WITH_NEXT_TEST = "propose_hypothesis_with_next_test"
    PROPOSE_HYPOTHESIS_EVIDENCE_RELATION = "propose_hypothesis_evidence_relation"
    PROPOSE_HYPOTHESIS_NEXT_TEST = "propose_hypothesis_next_test"
    RUN_ANALYTICS = "run_analytics"
    RUN_RELATIONSHIP = "run_relationship"
    INSPECT_EVIDENCE = "inspect_evidence"
    REQUEST_CLARIFICATION = "request_clarification"
    FINISH = "finish"


class ManagerObligationProposal(FrozenModel):
    obligation_id: str
    capability_key: ManagerCapabilityKey
    origin: Literal["USER_MUST", "USER_OPTIONAL", "SYSTEM_REQUIRED"]
    priority: ObligationPriority
    polarity: ObligationPolarity
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    semantic_handle_refs: tuple[str, ...] = Field(
        default=(),
        description="Use only runtime-issued h1/h2/... aliases from resolve_semantics.",
    )
    open_questions: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = Field(
        default=None,
        description="Required only for ranking obligation.",
    )
    ranking_limit: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Required only for ranking obligation.",
    )

    @model_validator(mode="after")
    def _ranking_contract(self):
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError("ranking direction + limit together")
        if (
            self.capability_key == ManagerCapabilityKey.RANKING
            and self.polarity == ObligationPolarity.REQUIRED
        ):
            if self.ranking_direction is None or self.ranking_limit is None:
                raise ValueError("required ranking proposal requires direction + limit")
        elif self.capability_key != ManagerCapabilityKey.RANKING and (
            self.ranking_direction is not None or self.ranking_limit is not None
        ):
            raise ValueError("ranking params only valid for ranking proposal")
        return self


class ManagerBranchCandidateProposal(FrozenModel):
    task_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    input_handles: tuple[str, ...] = Field(
        min_length=1,
        description="Runtime-issued h* aliases only; no raw sem_* identifiers.",
    )
    material_reason: str = Field(min_length=1, max_length=500)


class ManagerGoalTaskSemanticProposal(FrozenModel):
    surface: str = Field(min_length=1, max_length=240)
    kind_hint: Literal[
        "metric", "dimension", "filter", "time", "comparison", "unknown"
    ]


class ManagerDecisionTransport(FrozenModel):
    action: ManagerActionKind

    resolve_provenance: Literal["USER_SOURCE", "AGENT_DERIVED"] = "USER_SOURCE"
    source_surfaces: tuple[str, ...] = ()
    target_kind_hints: tuple[
        Literal["metric", "dimension", "filter", "time", "comparison", "unknown"], ...
    ] = Field(
        default=(),
        description=(
            "Aligned with source_surfaces. metric/dimension/filter are tenant catalog "
            "concepts; time is a base period phrase; comparison is a reference-period/"
            "comparison phrase. Ranking words/numbers are never semantic hints."
        ),
    )
    temporal_anchor_handle: str | None = Field(
        default=None,
        description="Optional runtime-issued h* alias used only as temporal anchor.",
    )
    base_period_handle: str | None = Field(
        default=None,
        description="Optional runtime-issued h* alias for a resolved base period.",
    )
    semantic_parent_obligation_id: str | None = None
    semantic_evidence_ref: str | None = None
    semantic_proposal: str | None = Field(default=None, max_length=240)

    obligations: tuple[ManagerObligationProposal, ...] = ()

    branch_parent_obligation_id: str | None = None
    branch_evidence_ref: str | None = None
    branch_candidates: tuple[ManagerBranchCandidateProposal, ...] = Field(
        default=(),
        max_length=12,
    )

    goal_parent_obligation_id: str | None = None
    goal_task_capability: ManagerCapabilityKey | None = None
    goal_task_semantic_surfaces: tuple[ManagerGoalTaskSemanticProposal, ...] = ()
    goal_task_material_reason: str | None = Field(default=None, min_length=1, max_length=500)
    goal_task_ranking_direction: Literal["asc", "desc"] | None = None
    goal_task_ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    directive_id: str | None = None
    directive_evidence_ref: str | None = None
    directive_disposition: Literal["NO_MATERIAL_DIRECTION"] | None = None
    directive_reason: str | None = Field(default=None, min_length=1, max_length=500)

    hypothesis_parent_obligation_id: str | None = None
    hypothesis_statement: str | None = Field(default=None, min_length=1, max_length=1000)
    hypothesis_semantic_handles: tuple[str, ...] = ()
    hypothesis_trigger_evidence_refs: tuple[str, ...] = ()
    hypothesis_limitations: tuple[str, ...] = ()

    hypothesis_ref: str | None = None
    hypothesis_relation_evidence_ref: str | None = None
    hypothesis_relation: HypothesisEvidenceRelation | None = None

    next_test_task_kind: ResearchTaskKind | None = None
    next_test_input_handles: tuple[str, ...] = ()
    next_test_trigger_evidence_ref: str | None = None
    next_test_material_reason: str | None = Field(default=None, min_length=1, max_length=500)
    next_test_ranking_direction: Literal["asc", "desc"] | None = None
    next_test_ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    obligation_ids: tuple[str, ...] = ()
    metric_handles: tuple[str, ...] = ()
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handle: str | None = None
    comparison_handle: str | None = None
    ranking_direction: Literal["asc", "desc"] | None = Field(
        default=None,
        description="Operation parameter for ranking; do not resolve ranking wording semantically.",
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Top/bottom N operation parameter; do not resolve this number as semantics.",
    )
    research_task_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Server-hydrated exact READY ResearchTask identity. Never model-authored."
        ),
    )
    derived_task_id: str | None = None
    derived_parent_obligation_id: str | None = None
    derived_capability_key: ManagerCapabilityKey | None = None
    derived_evidence_ref: str | None = None
    derived_reason: str | None = Field(default=None, min_length=1, max_length=500)

    relationship_obligation_id: str | None = None
    focus_handles: tuple[str, ...] = ()
    counterpart_handles: tuple[str, ...] = ()

    evidence_ref: str | None = None
    clarification_reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _action_shape(self):
        if self.action == ManagerActionKind.RESOLVE_SEMANTICS:
            if self.resolve_provenance == "USER_SOURCE":
                if not self.source_surfaces:
                    raise ValueError("USER_SOURCE resolve source_surfaces gerektirir")
                if self.target_kind_hints and len(self.target_kind_hints) != len(self.source_surfaces):
                    raise ValueError("semantic hints source_surfaces ile aynı uzunlukta olmalı")
            else:
                if (
                    not self.semantic_parent_obligation_id
                    or not self.semantic_evidence_ref
                    or not self.semantic_proposal
                    or len(self.target_kind_hints) != 1
                ):
                    raise ValueError(
                        "AGENT_DERIVED resolve parent obligation + evidence + proposal + one kind hint gerektirir"
                    )
        elif self.action == ManagerActionKind.PROPOSE_ACCEPTANCE:
            if not self.obligations:
                raise ValueError("propose_acceptance obligations gerektirir")
        elif self.action == ManagerActionKind.PROPOSE_BRANCHES:
            if (
                not self.branch_parent_obligation_id
                or not self.branch_evidence_ref
                or not self.branch_candidates
            ):
                raise ValueError(
                    "propose_branches parent obligation + evidence + candidates gerektirir"
                )
        elif self.action == ManagerActionKind.PROPOSE_GOAL_TASK:
            if (
                not self.goal_parent_obligation_id
                or self.goal_task_capability is None
                or not self.goal_task_semantic_surfaces
                or not self.goal_task_material_reason
            ):
                raise ValueError(
                    "goal task proposal requires parent + capability + exact semantic surfaces + reason"
                )
            if (self.goal_task_ranking_direction is None) != (
                self.goal_task_ranking_limit is None
            ):
                raise ValueError(
                    "goal task ranking direction + limit must be supplied together"
                )
        elif self.action == ManagerActionKind.DISPOSITION_RESEARCH_DIRECTIVE:
            if (
                not self.directive_id
                or not self.directive_evidence_ref
                or self.directive_disposition != "NO_MATERIAL_DIRECTION"
                or not self.directive_reason
            ):
                raise ValueError(
                    "directive disposition requires directive_id + evidence_ref + "
                    "NO_MATERIAL_DIRECTION + bounded reason"
                )
        elif self.action in {
            ManagerActionKind.PROPOSE_HYPOTHESIS,
            ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST,
        }:
            if (
                not self.hypothesis_parent_obligation_id
                or not self.hypothesis_statement
                or not self.hypothesis_semantic_handles
                or not self.hypothesis_trigger_evidence_refs
            ):
                raise ValueError(
                    "hypothesis proposal root obligation + statement + semantic handles "
                    "+ trigger evidence gerektirir"
                )
            if self.action == ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST:
                if (
                    self.next_test_task_kind is None
                    or not self.next_test_input_handles
                    or not self.next_test_trigger_evidence_ref
                    or not self.next_test_material_reason
                ):
                    raise ValueError(
                        "composite hypothesis proposal requires first governed next-test "
                        "kind + inputs + trigger evidence + material reason"
                    )
                if (
                    self.next_test_trigger_evidence_ref
                    not in self.hypothesis_trigger_evidence_refs
                ):
                    raise ValueError(
                        "composite next-test trigger must also trigger the proposed hypothesis"
                    )
                if (self.next_test_ranking_direction is None) != (
                    self.next_test_ranking_limit is None
                ):
                    raise ValueError(
                        "next-test ranking direction + limit birlikte verilmelidir"
                    )
        elif self.action == ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION:
            if (
                not self.hypothesis_ref
                or not self.hypothesis_relation_evidence_ref
                or self.hypothesis_relation is None
            ):
                raise ValueError(
                    "hypothesis evidence relation hypothesis_ref + evidence_ref + relation gerektirir"
                )
        elif self.action == ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST:
            if (
                not self.hypothesis_ref
                or self.next_test_task_kind is None
                or not self.next_test_input_handles
                or not self.next_test_trigger_evidence_ref
                or not self.next_test_material_reason
            ):
                raise ValueError(
                    "hypothesis next test hypothesis_ref + task kind + inputs + trigger "
                    "evidence + material reason gerektirir"
                )
            if (self.next_test_ranking_direction is None) != (
                self.next_test_ranking_limit is None
            ):
                raise ValueError(
                    "next-test ranking direction + limit birlikte verilmelidir"
                )
        elif self.action == ManagerActionKind.RUN_ANALYTICS:
            if not self.obligation_ids or not self.metric_handles:
                raise ValueError("run_analytics obligation_ids + metric_handles gerektirir")
        elif self.action == ManagerActionKind.RUN_RELATIONSHIP:
            if (
                not self.relationship_obligation_id
                or not self.focus_handles
                or not self.counterpart_handles
            ):
                raise ValueError("run_relationship obligation/focus/counterpart gerektirir")
        elif self.action == ManagerActionKind.INSPECT_EVIDENCE:
            if not self.evidence_ref:
                raise ValueError("inspect_evidence evidence_ref gerektirir")
        elif self.action == ManagerActionKind.REQUEST_CLARIFICATION:
            if not self.clarification_reason:
                raise ValueError("request_clarification reason gerektirir")

        branch_values = (
            self.branch_parent_obligation_id,
            self.branch_evidence_ref,
            self.branch_candidates,
        )
        if self.action != ManagerActionKind.PROPOSE_BRANCHES and (
            self.branch_parent_obligation_id is not None
            or self.branch_evidence_ref is not None
            or bool(self.branch_candidates)
        ):
            raise ValueError("branch fields are valid only for propose_branches")

        goal_values = (
            self.goal_parent_obligation_id,
            self.goal_task_capability,
            self.goal_task_semantic_surfaces,
            self.goal_task_material_reason,
            self.goal_task_ranking_direction,
            self.goal_task_ranking_limit,
        )
        if self.action != ManagerActionKind.PROPOSE_GOAL_TASK and any(
            value not in (None, (), []) for value in goal_values
        ):
            raise ValueError(
                "goal task fields are valid only for propose_goal_task"
            )

        directive_values = (
            self.directive_id,
            self.directive_evidence_ref,
            self.directive_disposition,
            self.directive_reason,
        )
        if self.action != ManagerActionKind.DISPOSITION_RESEARCH_DIRECTIVE and any(
            value is not None for value in directive_values
        ):
            raise ValueError(
                "directive disposition fields are valid only for disposition action"
            )

        hypothesis_register_values = (
            self.hypothesis_parent_obligation_id,
            self.hypothesis_statement,
            self.hypothesis_semantic_handles,
            self.hypothesis_trigger_evidence_refs,
            self.hypothesis_limitations,
        )
        if self.action not in {
            ManagerActionKind.PROPOSE_HYPOTHESIS,
            ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST,
        } and any(
            value not in (None, (), []) for value in hypothesis_register_values
        ):
            raise ValueError(
                "hypothesis registration fields are valid only for propose_hypothesis"
            )

        relation_values = (
            self.hypothesis_relation_evidence_ref,
            self.hypothesis_relation,
        )
        if (
            self.action != ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION
            and any(value is not None for value in relation_values)
        ):
            raise ValueError(
                "hypothesis relation fields are valid only for evidence relation action"
            )

        next_test_values = (
            self.next_test_task_kind,
            self.next_test_input_handles,
            self.next_test_trigger_evidence_ref,
            self.next_test_material_reason,
            self.next_test_ranking_direction,
            self.next_test_ranking_limit,
        )
        if self.action not in {
            ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST,
            ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST,
        } and any(
            value not in (None, (), []) for value in next_test_values
        ):
            raise ValueError(
                "next-test fields are valid only for propose_hypothesis_next_test"
            )

        if self.hypothesis_ref is not None and self.action not in {
            ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION,
            ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST,
        }:
            raise ValueError(
                "hypothesis_ref is valid only for relation or next-test action"
            )

        if (
            self.research_task_id is not None
            and self.action
            not in {
                ManagerActionKind.RUN_ANALYTICS,
                ManagerActionKind.RUN_RELATIONSHIP,
            }
        ):
            raise ValueError(
                "research_task_id is valid only for governed Research execution"
            )

        derived_values = (
            self.derived_task_id,
            self.derived_parent_obligation_id,
            self.derived_capability_key,
            self.derived_evidence_ref,
            self.derived_reason,
        )
        if any(value is not None for value in derived_values):
            if self.action != ManagerActionKind.RUN_ANALYTICS:
                raise ValueError("derived task fields are valid only for run_analytics")
            if not all(value is not None for value in derived_values):
                raise ValueError(
                    "derived task id/parent/capability/evidence_ref/reason birlikte verilmelidir"
                )
        return self


@dataclass(frozen=True)
class ManagerLoopOutcome:
    snapshot: Any
    run_finished: bool
    verified_complete: bool
    terminal_status: ResearchRunTerminal | None
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]
    preacceptance_status: FiniteAcceptanceStatus | None = None
    findings: tuple[EvidenceLinkedFinding, ...] = ()
    research_tasks: tuple[ResearchTask, ...] = ()
    hypothesis_states: tuple[HypothesisLedgerState, ...] = ()
    directive_dispositions: tuple[ResearchDirectiveDisposition, ...] = ()
    cancelled: bool = False
    answer_now_requested: bool = False


def _strict_native_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Pydantic JSON Schema to OpenAI/OpenRouter strict-native rules.

    Strict providers require every object property to appear in `required`. Optional
    semantics are represented by nullable types, not by omitting keys. Defaults are
    application conveniences and are removed from the provider contract.
    """
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


_SYSTEM = """You are Dima's bounded post-acceptance RESEARCH_MANAGER.

AcceptedTurnContract is already the only semantic authority. Use typed governed tools to
investigate accepted obligations, inspect evidence, open evidence-grounded derived work,
and propose finish. Do not write SQL. Do not invent canonical identifiers or semantic
handles. Capability meanings and semantic shapes come only from CAPABILITY_BINDING_CONTRACT.

Rules:
- Never mutate, reinterpret, drop or replace accepted USER_MUST obligations.
- Research directives are policy/authorization, not user obligations.
- ADAPT_ON_EVIDENCE remains OPEN until a governed material branch is executed/accounted or
  disposition_research_directive records NO_MATERIAL_DIRECTION from current inspected VERIFIED Evidence.
- BROADEN_WITHIN_BUDGET is authorization only; never invent work merely to close it.
- AGENT_DERIVED semantic discovery requires accepted parent + inspected verified evidence.
- Rejected attempts leave no semantic authority to merge.
- run_analytics/run_relationship may reference only accepted/derived obligation IDs.
- Evidence-grounded executable branches MUST first be proposed with propose_branches, EXCEPT the
  first ROOT_CAUSE next test carried by propose_hypothesis_with_next_test. That composite action is
  still only a bounded cognition plan: the server validates the hypothesis, mints its ID, validates
  the next test through HypothesisNextTestBoundary, mints the ResearchTask ID and executes through
  the existing trust plane.
- propose_branches registers bounded typed candidates only; it NEVER executes data work.
- Every derived run_analytics must select a task already listed in READY_RESEARCH_TASKS.
- Every derived branch must cite parent obligation + inspected evidence.
- MANAGER_ACTION_SET is the single server-resolved executable cognition surface for this turn.
  Choose exactly one opaque action_ref from action_instances. Do not echo or reconstruct parent,
  Evidence, semantic-handle, hypothesis, task, or directive identities; the server hydrates them.
- CURRENT_RESULT_DELTA with disclosed_in_current_prompt=true is already visible in this cognition call.
  When inspection_required=false, do NOT spend inspect_evidence on that fresh Evidence; after a
  successful structured response the runtime records it as inspected before applying the action.
  Explicit inspect_evidence remains only for server-listed older Evidence whose bounded payload is
  not present in CURRENT_RESULT_DELTA.
- Follow ACTION_FRONTIER. Never repeat an exact action listed in blocked_exact_actions.
- Semantic ambiguity is Resolver authority; do not guess canonical truth.
- finish is only a proposal; deterministic CompletionGate decides completion truth.
- One action per turn. No prose outside the strict schema.
- Emit every schema field; use []/null for unused fields.
"""

_ROOT_CAUSE_SYSTEM_ADDENDUM = """
DAY8 ROOT_CAUSE RULES:
- Hypotheses are cognition proposals, never Evidence or canonical semantic truth.
- propose_hypothesis may use only runtime-issued h* aliases and current VERIFIED cognition-available
  Evidence: either persisted inspected Evidence or a fresh CURRENT_RESULT_DELTA with
  inspection_required=false. Runtime admission remains authoritative.
- propose_hypothesis_with_next_test is allowed only when one such current VERIFIED Evidence item can
  ground BOTH a new hypothesis and its first material governed next test. Never provide a
  hypothesis ID or ResearchTask ID for this action; server identity owners remain authoritative.
- Trigger Evidence does NOT become SUPPORTS automatically.
- SUPPORTS/CONTRADICTS requires propose_hypothesis_evidence_relation explicitly, including after a
  composite hypothesis+next-test action. Executing a next test never creates an evidence relation.
- propose_hypothesis_next_test and the composite first next test select an opaque action_ref.
  The server binds the legal task kind, existing governed inputs and trigger Evidence; the model
  supplies only the genuinely cognitive hypothesis/relation/reasoning fields exposed by that card.
- ROOT_CAUSE_NEXT_TEST_CONTRACT maps each advertised task kind to its existing DIRECT capability and required semantic shape; do not invent a missing shape.
- h* aliases are opaque identities. Use SEMANTIC_HANDLE_CATALOG for their governed target_kind/provenance; never re-resolve an already-known handle merely to rediscover its type.
- Before AGENT_DERIVED resolve_semantics, check whether a material next test can already be formed from ROOT_CAUSE_NEXT_TEST_CONTRACT + SEMANTIC_HANDLE_CATALOG. Prefer existing governed handles; semantic expansion is for a materially missing concept grounded in inspected Evidence, not a default exploration step.
- Never invent or provide ResearchTask IDs for hypothesis next tests; the server owns identity.
- A planned/running/completed-but-unverified task is not epistemic Evidence.
- ASSOCIATION/CONTRIBUTION/priority/interestingness are not causation.
- Never claim CONFIRMED_CAUSE. Current Day8 ceiling is at most CANDIDATE_CAUSE.
- Use READY_RESEARCH_TASKS only after the server has materialized a governed task.
"""


def _conversation_surface_view(
    conversation: ConversationStateV2 | None,
) -> dict[str, Any]:
    """Expose only bounded surface context; canonical IR/anchors never reach Manager."""
    if conversation is None:
        return {
            "has_prior_analytical_request": False,
            "has_active_result": False,
            "pending_clarification": False,
            "topic_labels": [],
            "focus_labels": [],
            "selected_anchor_label": None,
            "pending_source_mention": None,
        }
    clarification = conversation.clarification_state
    return {
        "has_prior_analytical_request": conversation.has_prior_analytical_request,
        "has_active_result": conversation.has_active_result,
        "pending_clarification": conversation.pending_clarification,
        "topic_labels": list(conversation.topic_labels[:8]),
        "focus_labels": list(conversation.focus_labels[:8]),
        "selected_anchor_label": conversation.selected_anchor_label,
        "pending_source_mention": (
            clarification.source_mention if clarification is not None else None
        ),
    }


def _evidence_was_inspected(
    observations: list[dict[str, Any]],
    evidence_ref: str | None,
) -> bool:
    if not evidence_ref:
        return False
    return any(
        observation.get("kind") == "tool"
        and observation.get("tool") == ManagerToolName.INSPECT_EVIDENCE.value
        and (observation.get("result") or {}).get("artifact_id") == evidence_ref
        for observation in observations
    )


def _zero_row_completion_candidate(
    *,
    runtime: ManagerRuntime,
    evidence_store,
    task_registry: ResearchTaskRegistry,
) -> bool:
    """Return True only when another Manager turn cannot open grounded data work.

    A zero-row current result contains no material row-level direction for an
    evidence-grounded branch. If every registered ResearchTask is already terminal,
    CompletionGate is the only remaining authority: the loop may attempt finish
    without spending another probabilistic Manager turn.
    """
    state = build_research_state_view(
        runtime=runtime,
        evidence_store=evidence_store,
    )
    delta = state.latest_delta
    if (
        delta is None
        or delta.availability.value != "AVAILABLE"
        or not delta.inspected
        or delta.row_count != 0
    ):
        return False
    if any(task.state == "pending" for task in task_registry.tasks):
        return False
    return True


def _clarification_has_governed_grounding(
    observations: list[dict[str, Any]],
    *,
    accepted_contract_present: bool,
) -> bool:
    """Clarification must be grounded by deterministic authority, not Manager intuition.

    After acceptance, blockers in the canonical ledger are sufficient grounding. Before
    acceptance, either SemanticResolver or AcceptanceGate must have produced a concrete
    clarification/unresolved state first.
    """
    if accepted_contract_present:
        return True

    for observation in reversed(observations):
        if observation.get("kind") != "tool":
            continue
        tool = observation.get("tool")
        result = observation.get("result") or {}
        if tool == ManagerToolName.RESOLVE_SEMANTICS.value:
            if (
                result.get("clarification")
                or result.get("unresolved_source_refs")
                or result.get("unresolved_proposals")
            ):
                return True
        if tool == ManagerToolName.PROPOSE_ACCEPTANCE.value:
            if result.get("status") == "NEEDS_CLARIFICATION":
                return True
            if result.get("status") == "REJECTED":
                reasons = tuple(str(reason) for reason in (result.get("reasons") or ()))
                if reasons and all(
                    "missing Resolver semantic kinds:" in reason
                    for reason in reasons
                ):
                    return True
    return False


def _safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "__dict__"):
        return {
            key: _safe(item)
            for key, item in vars(value).items()
            if not key.startswith("_") and key not in {"analytics_ir"}
        }
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


@dataclass(frozen=True)
class ManagerUnderstandingOutcome:
    snapshot: ManagerRunSnapshot
    status: FiniteAcceptanceStatus
    accepted: bool
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]


class ResearchManagerLoop:
    def __init__(
        self,
        *,
        llm,
        source_spans: SourceSpanRegistry,
        research_tool_runner: ResearchToolRunner | None = None,
        research_task_service: ResearchTaskService | None = None,
        root_cause_context: RootCauseLoopContext | None = None,
        progress_callback: Callable[[str, tuple[str, ...]], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
        answer_now_check: Callable[[], bool] | None = None,
        context_scope_by_kind: dict[str, tuple[str, ...]] | None = None,
        signed_section_continuation: bool = False,
        allowed_continuation_parent_refs: tuple[str, ...] = (),
    ) -> None:
        structured = getattr(llm, "structured_json", None)
        if not callable(structured):
            raise ValueError("RESEARCH_MANAGER provider native structured_json desteklemiyor")
        self._structured = structured
        self._source_spans = source_spans
        self._capabilities = ManagerCapabilityRegistry()
        self._research_tool_runner = research_tool_runner
        self._research_tasks = research_task_service or ResearchTaskService()
        self._root_cause_context = root_cause_context
        self._progress_callback = progress_callback
        self._cancel_check = cancel_check
        self._answer_now_check = answer_now_check
        self._context_scope_by_kind = {
            str(kind): tuple(dict.fromkeys(refs))
            for kind, refs in (context_scope_by_kind or {}).items()
            if refs
        }
        self._signed_section_continuation = bool(signed_section_continuation)
        self._allowed_continuation_parent_refs = tuple(
            dict.fromkeys(allowed_continuation_parent_refs)
        )
        self._alias_by_handle: dict[str, str] = {}
        self._handle_by_alias: dict[str, str] = {}

    def _emit_progress(self, kind: str, refs: tuple[str, ...] = ()) -> None:
        if self._progress_callback is not None:
            self._progress_callback(kind, refs)

    @staticmethod
    def _evidence_belongs_to_parent_lineage(
        *,
        runtime: ManagerRuntime,
        evidence,
        parent_obligation_id: str,
    ) -> bool:
        return evidence_belongs_to_parent_lineage(
            ledger=runtime.ledger,
            evidence=evidence,
            parent_obligation_id=parent_obligation_id,
        )


    @classmethod
    def _admit_no_material_direction(
        cls,
        *,
        runtime: ManagerRuntime,
        evidence_store,
        directive_id: str,
        evidence_ref: str,
        reason: str,
    ):
        contract = runtime.accepted_contract
        if contract is None:
            raise ManagerStateError(
                "directive disposition requires accepted contract"
            )
        directive = next(
            (
                item
                for item in contract.research_directives
                if item.directive_id == directive_id
            ),
            None,
        )
        if directive is None:
            raise ManagerStateError(
                "directive_id is not present in accepted contract"
            )
        if directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE:
            raise ManagerStateError(
                "only ADAPT_ON_EVIDENCE has completion-relevant disposition"
            )
        if evidence_ref not in runtime.snapshot.evidence_refs:
            raise ManagerStateError(
                "directive disposition Evidence is outside current run"
            )
        if evidence_ref not in runtime.snapshot.inspected_evidence_refs:
            raise ManagerStateError(
                "directive disposition requires inspected Evidence"
            )
        evidence = evidence_store.get(evidence_ref)
        if not evidence.verified:
            raise ManagerStateError(
                "directive disposition requires VERIFIED Evidence"
            )
        if not cls._evidence_belongs_to_parent_lineage(
            runtime=runtime,
            evidence=evidence,
            parent_obligation_id=directive.parent_obligation_id,
        ):
            raise ManagerStateError(
                "directive disposition Evidence is outside parent obligation lineage"
            )
        return runtime.account_research_directive(
            directive_id=directive.directive_id,
            status=ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
            evidence_ref=evidence_ref,
            reason=reason,
        )

    @staticmethod
    def _reconcile_blocked_research_directives(
        *,
        runtime: ManagerRuntime,
    ) -> tuple[str, ...]:
        """Account ADAPT policy from authoritative partial-terminal parent state.

        BLOCKED is not model cognition and does not manufacture Evidence. CompletionGate
        remains the sole owner of VERIFIED_COMPLETE versus PARTIAL.
        """
        contract = runtime.accepted_contract
        ledger = runtime.ledger
        if contract is None or ledger is None:
            return ()

        parent_by_id = {
            item.obligation_id: item for item in ledger.items
        }
        reconciled: list[str] = []
        for directive in contract.research_directives:
            if directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE:
                continue
            current = runtime.directive_disposition(directive.directive_id)
            if current.status != ResearchDirectiveDispositionStatus.OPEN:
                continue
            parent = parent_by_id.get(directive.parent_obligation_id)
            if parent is None or parent.status not in {
                ObligationStatus.BLOCKED_DATA_GAP,
                ObligationStatus.LIMITED,
                ObligationStatus.UNSUPPORTED,
            }:
                continue
            runtime.account_research_directive(
                directive_id=directive.directive_id,
                status=ResearchDirectiveDispositionStatus.BLOCKED,
                evidence_ref=None,
                branch_task_refs=(),
                reason=(
                    "authoritative parent obligation is terminal partial: "
                    f"{parent.status.value}"
                ),
            )
            reconciled.append(directive.directive_id)
        return tuple(reconciled)

    @staticmethod
    def _try_deterministic_finish(
        *,
        runtime: ManagerRuntime,
        task_registry: ResearchTaskRegistry,
    ) -> bool:
        if any(
            task.origin == "USER_SEED"
            and task.state in {"pending", "running"}
            for task in task_registry.tasks
        ):
            # USER_SEED tasks are the direct execution obligations. Agent-derived
            # candidates are policy/cognition options unless another authority makes
            # them completion-relevant (ROOT_CAUSE next-test or ADAPT disposition).
            return False
        contract = runtime.accepted_contract
        if contract is not None:
            completion_relevant = {
                item.directive_id
                for item in contract.research_directives
                if item.directive_type == ResearchDirectiveType.ADAPT_ON_EVIDENCE
            }
            accounted = {
                item.directive_id
                for item in runtime.directive_dispositions
                if item.status
                in {
                    ResearchDirectiveDispositionStatus.APPLIED,
                    ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION,
                    ResearchDirectiveDispositionStatus.BLOCKED,
                }
            }
            if not completion_relevant.issubset(accounted):
                return False
        try:
            runtime.finish()
            return True
        except ManagerStateError:
            return False

    @staticmethod
    def _reconcile_root_obligations(
        *,
        runtime: ManagerRuntime,
        root_cause_ledgers: dict[str, Any],
        task_registry: ResearchTaskRegistry,
    ) -> bool:
        changed = False
        verifier = RootCauseObligationVerifier()
        for ledger in root_cause_ledgers.values():
            before = next(
                item.status
                for item in runtime.ledger.items
                if item.obligation_id == ledger.state.parent_obligation_id
            )
            verifier.reconcile(
                runtime=runtime,
                hypothesis_ledger=ledger,
                task_registry=task_registry,
            )
            after = next(
                item.status
                for item in runtime.ledger.items
                if item.obligation_id == ledger.state.parent_obligation_id
            )
            changed = changed or before != after
        return changed

    def _handle_alias(self, handle_id: str) -> str:
        if not str(handle_id).startswith("sem_"):
            return str(handle_id)
        existing = self._alias_by_handle.get(handle_id)
        if existing is not None:
            return existing
        alias = f"h{len(self._alias_by_handle) + 1}"
        self._alias_by_handle[handle_id] = alias
        self._handle_by_alias[alias] = handle_id
        return alias

    def _manager_safe(self, value: Any) -> Any:
        """Serialize tool/runtime state for the Manager without exposing raw sem_* ids."""
        if hasattr(value, "model_dump"):
            return self._manager_safe(value.model_dump(mode="json"))
        if hasattr(value, "__dict__"):
            return {
                key: self._manager_safe(item)
                for key, item in vars(value).items()
                if not key.startswith("_") and key not in {"analytics_ir"}
            }
        if isinstance(value, dict):
            return {str(k): self._manager_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._manager_safe(item) for item in value]
        if isinstance(value, str) and value.startswith("sem_"):
            return self._handle_alias(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _decode_handle(self, ref: str | None) -> str | None:
        if ref is None:
            return None
        raw = str(ref)
        if raw.startswith("sem_"):
            raise ValueError(
                "Manager raw sem_* id kullanamaz; resolve_semantics tarafından verilen h* aliasını kullanın"
            )
        if raw.startswith("h"):
            try:
                return self._handle_by_alias[raw]
            except KeyError as exc:
                raise ValueError(f"unknown/unissued Manager handle alias: {raw}") from exc
        raise ValueError(f"invalid Manager handle reference: {raw}")

    def _decode_handles(self, refs: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(self._decode_handle(ref) for ref in refs)

    def _governed_semantic_inventory(
        self,
        *,
        runtime: ManagerRuntime,
        hypothesis_ledgers: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], ...]:
        """Project existing governed identities; never mint or reinterpret semantics."""
        rows: dict[str, dict[str, Any]] = {}
        ledger = runtime.ledger
        if ledger is not None:
            for item in ledger.items:
                for binding in item.semantic_bindings:
                    alias = self._handle_alias(binding.handle_id)
                    try:
                        surface = self._source_spans.validate(
                            binding.source_ref
                        ).exact_surface
                    except Exception:
                        surface = None
                    row = rows.setdefault(
                        binding.handle_id,
                        {
                            "handle_ref": alias,
                            "target_kind": binding.target_kind,
                            "provenance_type": "USER_SOURCE",
                            "parent_obligation_id": item.obligation_id,
                            "source_surfaces": [],
                            "accepted_obligation_ids": [],
                        },
                    )
                    if surface and surface not in row["source_surfaces"]:
                        row["source_surfaces"].append(surface)
                    if item.obligation_id not in row["accepted_obligation_ids"]:
                        row["accepted_obligation_ids"].append(item.obligation_id)

        for root_id, hypothesis_ledger in sorted(
            (hypothesis_ledgers or {}).items()
        ):
            refs: list[str] = []
            try:
                root_item = next(
                    item
                    for item in hypothesis_ledger.obligation_ledger.items
                    if item.obligation_id == root_id
                )
                refs.extend(root_item.semantic_handle_refs)
            except StopIteration:
                pass
            for entry in hypothesis_ledger.state.entries:
                refs.extend(entry.semantic_handle_refs)
            for handle_id in dict.fromkeys(refs):
                try:
                    metadata = hypothesis_ledger.semantic_handle_metadata(handle_id)
                except Exception:
                    continue
                row = rows.setdefault(
                    handle_id,
                    {
                        "handle_ref": self._handle_alias(handle_id),
                        "target_kind": metadata.get("target_kind"),
                        "provenance_type": metadata.get("provenance_type"),
                        "parent_obligation_id": metadata.get("parent_obligation_id"),
                        "source_surfaces": [],
                        "accepted_obligation_ids": [],
                    },
                )
                if (
                    metadata.get("parent_obligation_id")
                    and metadata.get("parent_obligation_id")
                    not in row["accepted_obligation_ids"]
                ):
                    row["accepted_obligation_ids"].append(
                        metadata.get("parent_obligation_id")
                    )

        return tuple(
            {
                **row,
                "source_surfaces": list(row["source_surfaces"]),
                "accepted_obligation_ids": list(row["accepted_obligation_ids"]),
            }
            for _handle_id, row in sorted(
                rows.items(),
                key=lambda item: item[1]["handle_ref"],
            )
        )

    def _action_set(
        self,
        *,
        runtime: ManagerRuntime,
        observations: list[dict[str, Any]],
        action_frontier: dict[str, Any] | None,
        research_state: ResearchStateView | None,
        hypothesis_ledgers: dict[str, Any] | None,
        evidence_store,
        research_tasks: tuple[Any, ...] = (),
        governed_semantic_inventory: tuple[dict[str, Any], ...] = (),
    ) -> ManagerActionSet:
        latest = None if research_state is None else research_state.latest_delta
        fresh_ref = None
        fresh_verified = False
        if (
            latest is not None
            and latest.availability.value == "AVAILABLE"
            and latest.disclosed_in_current_prompt
            and latest.verified is True
        ):
            fresh_ref = latest.evidence_ref
            fresh_verified = True

        inspected_verified: list[str] = []
        for ref in runtime.snapshot.inspected_evidence_refs:
            if ref not in runtime.snapshot.evidence_refs or evidence_store is None:
                continue
            try:
                evidence = evidence_store.get(ref)
            except Exception:
                continue
            if getattr(evidence, "verified", False):
                inspected_verified.append(ref)
        if fresh_ref is not None:
            inspected_verified.append(fresh_ref)
        effective_refs = tuple(dict.fromkeys(inspected_verified))

        inspectable_old: list[str] = []
        if evidence_store is not None:
            for ref in runtime.snapshot.evidence_refs:
                if ref in runtime.snapshot.inspected_evidence_refs or ref == fresh_ref:
                    continue
                try:
                    evidence = evidence_store.get(ref)
                except Exception:
                    continue
                if getattr(evidence, "verified", False):
                    inspectable_old.append(ref)

        inventory_by_alias = {
            str(row.get("handle_ref")): row
            for row in governed_semantic_inventory
            if row.get("handle_ref")
        }
        ledger = runtime.ledger

        def semantic_ref(handle_id: str, *, fallback_kind: str | None = None):
            alias = self._handle_alias(handle_id)
            kind = fallback_kind
            if kind is None and ledger is not None:
                for item in ledger.items:
                    for binding in item.semantic_bindings:
                        if binding.handle_id == handle_id:
                            kind = str(binding.target_kind)
                            break
                    if kind is not None:
                        break
            if kind is None and self._root_cause_context is not None:
                try:
                    handle = self._root_cause_context.semantic_handles.validate(
                        handle_id,
                        tenant_binding=self._root_cause_context.tenant_binding,
                        context_version=self._root_cause_context.context_version,
                    )
                    kind = str(handle.target_kind)
                except Exception:
                    pass
            if kind is None:
                row = inventory_by_alias.get(alias) or {}
                kind = str(row.get("target_kind") or "unknown")
            return SemanticActionRef(ref=alias, kind=str(kind))

        contract_rows = tuple(
            NextTestContractState(
                task_kind=str(row["task_kind"]),
                capability_key=str(row["capability"]),
                required_kinds=tuple(
                    str(value) for value in row.get("required_semantic_kinds", ())
                ),
                allowed_kinds=tuple(
                    str(value) for value in row.get("allowed_semantic_kinds", ())
                ),
                required_params=tuple(
                    str(value) for value in row.get("required_operation_params", ())
                ),
            )
            for row in root_cause_next_test_contract(capabilities=self._capabilities)
        )

        root_states: list[RootActionState] = []
        for root_id, hypothesis_ledger in sorted((hypothesis_ledgers or {}).items()):
            try:
                root_item = next(
                    item
                    for item in hypothesis_ledger.obligation_ledger.items
                    if item.obligation_id == root_id
                )
            except StopIteration:
                continue

            root_refs: list[SemanticActionRef] = []
            seen_aliases: set[str] = set()
            for binding in root_item.semantic_bindings:
                ref = semantic_ref(
                    binding.handle_id,
                    fallback_kind=str(binding.target_kind),
                )
                if ref.ref not in seen_aliases:
                    root_refs.append(ref)
                    seen_aliases.add(ref.ref)
            for handle_id in root_item.semantic_handle_refs:
                ref = semantic_ref(handle_id)
                if ref.ref not in seen_aliases:
                    root_refs.append(ref)
                    seen_aliases.add(ref.ref)
            # Governed derived semantic expansion already bound to this ROOT is Product
            # authority too; preserve it without reconstructing identity joins in schema.
            for row in governed_semantic_inventory:
                alias = str(row.get("handle_ref") or "")
                if not alias or alias in seen_aliases:
                    continue
                parents = {
                    str(value)
                    for value in (row.get("accepted_obligation_ids") or ())
                }
                if (
                    str(row.get("parent_obligation_id") or "") != root_id
                    and root_id not in parents
                ):
                    continue
                root_refs.append(
                    SemanticActionRef(
                        ref=alias,
                        kind=str(row.get("target_kind") or "unknown"),
                    )
                )
                seen_aliases.add(alias)

            root_evidence: list[str] = []
            root_next_test_evidence: list[str] = []
            task_by_id = {task.task_id: task for task in research_tasks}
            for ref in effective_refs:
                try:
                    evidence = hypothesis_ledger.validated_evidence(ref)
                except Exception:
                    continue
                root_evidence.append(ref)
                parent_task = task_by_id.get(
                    getattr(evidence, "task_id", None)
                )
                if (
                    root_id
                    in tuple(getattr(evidence, "obligation_ids", ()) or ())
                    and parent_task is not None
                    and parent_task.state == "complete"
                    and parent_task.question_id == root_id
                ):
                    root_next_test_evidence.append(ref)


            hypotheses: list[HypothesisActionState] = []
            for entry in hypothesis_ledger.state.entries:
                entry_refs: list[SemanticActionRef] = []
                for handle_id in entry.semantic_handle_refs:
                    entry_refs.append(semantic_ref(handle_id))
                admissible = tuple(
                    ref
                    for ref in dict.fromkeys(
                        (
                            *entry.trigger_evidence_refs,
                            *(link.evidence_ref for link in entry.evidence_links),
                        )
                    )
                    if ref in set(root_evidence)
                )
                next_test_admissible = tuple(
                    ref
                    for ref in admissible
                    if ref in set(root_next_test_evidence)
                )
                linked = {link.evidence_ref for link in entry.evidence_links}
                complete_next_tests = {
                    task_ref
                    for task_ref in entry.next_test_task_refs
                    if (
                        task_ref in task_by_id
                        and task_by_id[task_ref].state == "complete"
                    )
                }
                pending: list[str] = []
                if complete_next_tests and evidence_store is not None:
                    for evidence_ref in root_evidence:
                        if evidence_ref in linked:
                            continue
                        try:
                            evidence = evidence_store.get(evidence_ref)
                        except Exception:
                            continue
                        if (
                            getattr(evidence, "verified", False)
                            and evidence.task_id in complete_next_tests
                        ):
                            pending.append(evidence_ref)
                hypotheses.append(
                    HypothesisActionState(
                        hypothesis_ref=entry.hypothesis_id,
                        semantic_refs=tuple(dict.fromkeys(entry_refs)),
                        admissible_evidence_refs=admissible,
                        next_test_evidence_refs=next_test_admissible,
                        pending_relation_evidence_refs=tuple(dict.fromkeys(pending)),
                    )
                )

            root_states.append(
                RootActionState(
                    root_id=root_id,
                    semantic_refs=tuple(root_refs),
                    evidence_refs=tuple(dict.fromkeys(root_evidence)),
                    next_test_evidence_refs=tuple(
                        dict.fromkeys(root_next_test_evidence)
                    ),
                    hypotheses=tuple(hypotheses),
                    next_test_contracts=contract_rows,
                )
            )

        open_dispositions = {
            item.directive_id
            for item in runtime.directive_dispositions
            if item.status == ResearchDirectiveDispositionStatus.OPEN
        }
        directive_states: list[DirectiveActionState] = []
        contract = runtime.accepted_contract
        evidence_by_ref: dict[str, Any] = {}
        if evidence_store is not None:
            for ref in effective_refs:
                try:
                    evidence_by_ref[ref] = evidence_store.get(ref)
                except Exception:
                    continue
        if contract is not None:
            for directive in contract.research_directives:
                if (
                    directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE
                    or directive.directive_id not in open_dispositions
                ):
                    continue
                eligible = tuple(
                    ref
                    for ref, evidence in evidence_by_ref.items()
                    if (
                        getattr(evidence, "verified", False)
                        and evidence_belongs_to_parent_lineage(
                            ledger=runtime.ledger,
                            evidence=evidence,
                            parent_obligation_id=directive.parent_obligation_id,
                        )
                    )
                )
                directive_states.append(
                    DirectiveActionState(
                        directive_id=directive.directive_id,
                        parent_obligation_id=directive.parent_obligation_id,
                        eligible_evidence_refs=eligible,
                    )
                )

        parent_evidence_states: list[ParentEvidenceActionState] = []
        if ledger is not None:
            for item in ledger.items:
                if item.polarity != ObligationPolarity.REQUIRED:
                    continue
                if item.status == ObligationStatus.SUPERSEDED:
                    continue
                semantic_rows: list[SemanticActionRef] = [
                    semantic_ref(handle_id)
                    for handle_id in item.semantic_handle_refs
                ]
                seen_parent_aliases = {row.ref for row in semantic_rows}
                for row in governed_semantic_inventory:
                    alias = str(row.get("handle_ref") or "")
                    if not alias or alias in seen_parent_aliases:
                        continue
                    accepted_parents = {
                        str(value)
                        for value in (row.get("accepted_obligation_ids") or ())
                    }
                    if (
                        str(row.get("parent_obligation_id") or "")
                        != item.obligation_id
                        and item.obligation_id not in accepted_parents
                    ):
                        continue
                    semantic_rows.append(
                        SemanticActionRef(
                            ref=alias,
                            kind=str(row.get("target_kind") or "unknown"),
                        )
                    )
                    seen_parent_aliases.add(alias)
                semantic_refs = tuple(semantic_rows)
                if item.obligation_id in {root.root_id for root in root_states}:
                    root = next(
                        root
                        for root in root_states
                        if root.root_id == item.obligation_id
                    )
                    semantic_refs = root.semantic_refs
                for ref, evidence in evidence_by_ref.items():
                    if not getattr(evidence, "verified", False):
                        continue
                    if not evidence_belongs_to_parent_lineage(
                        ledger=ledger,
                        evidence=evidence,
                        parent_obligation_id=item.obligation_id,
                    ):
                        continue

                    # Derived semantic discovery is canonical Resolver/registry state,
                    # not observation text. Project only exact parent + trigger-Evidence
                    # handles into this parent/Evidence action card. This preserves
                    # correlated applicability while making newly legal branch shapes
                    # visible immediately after governed semantic resolution.
                    scoped_semantic_refs = list(semantic_refs)
                    scoped_aliases = {row.ref for row in scoped_semantic_refs}
                    if self._root_cause_context is not None:
                        for handle in (
                            self._root_cause_context.semantic_handles.handles_for_parent(
                                tenant_binding=self._root_cause_context.tenant_binding,
                                context_version=self._root_cause_context.context_version,
                                parent_obligation_id=item.obligation_id,
                                trigger_evidence_ref=ref,
                            )
                        ):
                            alias = self._handle_alias(handle.handle_id)
                            if alias in scoped_aliases:
                                continue
                            scoped_semantic_refs.append(
                                SemanticActionRef(
                                    ref=alias,
                                    kind=str(handle.target_kind),
                                )
                            )
                            scoped_aliases.add(alias)

                    parent_evidence_states.append(
                        ParentEvidenceActionState(
                            parent_obligation_id=item.obligation_id,
                            capability_key=item.capability_key.value,
                            evidence_ref=ref,
                            semantic_refs=tuple(scoped_semantic_refs),
                            branch_eligible=(
                                item.obligation_id
                                in tuple(getattr(evidence, "obligation_ids", ()) or ())
                                and any(
                                    task.task_id == getattr(evidence, "task_id", None)
                                    and task.state == "complete"
                                    and task.question_id == item.obligation_id
                                    for task in research_tasks
                                )
                            ),
                        )
                    )

        goal_task_states: list[GoalTaskActionState] = []
        if ledger is not None and self._research_tool_runner is not None:
            task_owner_ids = {
                (
                    task.question_id
                    if task.origin == "USER_SEED"
                    else task.parent_obligation_id
                )
                for task in research_tasks
                if (
                    task.question_id
                    or task.parent_obligation_id
                )
            }
            directive_parent_ids_all = {
                directive.parent_obligation_id
                for directive in (
                    runtime.accepted_contract.research_directives
                    if runtime.accepted_contract is not None
                    else ()
                )
            }
            declared_kinds = set(
                self._research_tool_runner.declared_task_kinds
            )
            for item in ledger.active_user_must:
                if item.status not in {
                    ObligationStatus.ACCEPTED,
                    ObligationStatus.READY,
                    ObligationStatus.IN_PROGRESS,
                }:
                    continue
                spec = self._capabilities.get(item.capability_key)
                is_research_goal = (
                    spec.lane.value == "RESEARCH"
                    or item.obligation_id in directive_parent_ids_all
                )
                if not is_research_goal:
                    continue
                if item.obligation_id in task_owner_ids:
                    continue

                allowed: list[str] = []
                candidates = (
                    tuple(ManagerCapabilityKey)
                    if item.capability_key == ManagerCapabilityKey.ROOT_CAUSE
                    else (item.capability_key,)
                )
                for capability in candidates:
                    candidate_spec = self._capabilities.get(capability)
                    if candidate_spec.execution_mode.value != "DIRECT":
                        continue
                    if candidate_spec.lane.value not in {"STANDARD", "RESEARCH"}:
                        continue
                    try:
                        kind = self._research_tasks.task_kind_for_capability(
                            capability
                        )
                    except Exception:
                        continue
                    if kind not in declared_kinds:
                        continue
                    allowed.append(capability.value)

                source_surfaces: list[str] = []
                for source_ref in item.source_refs:
                    try:
                        span = self._source_spans.validate(source_ref)
                    except Exception:
                        continue
                    value = str(span.exact_surface).strip()
                    if value and value not in source_surfaces:
                        source_surfaces.append(value)
                if allowed and source_surfaces:
                    goal_task_states.append(
                        GoalTaskActionState(
                            parent_obligation_id=item.obligation_id,
                            goal_capability_key=item.capability_key.value,
                            source_surfaces=tuple(source_surfaces),
                            allowed_task_capabilities=tuple(dict.fromkeys(allowed)),
                        )
                    )

        ready_task_states: list[TaskActionState] = []
        for task in research_tasks:
            if task.state != "pending":
                continue
            try:
                capability = self._research_tasks.capability_for_task_kind(
                    ResearchTaskKind(task.task_kind)
                )
            except Exception:
                continue
            ranking_direction = None
            ranking_limit = None
            if ledger is not None:
                owner_id = (
                    task.question_id
                    if task.origin == "USER_SEED"
                    else task.parent_obligation_id
                )
                owner = next(
                    (
                        item
                        for item in ledger.items
                        if item.obligation_id == owner_id
                    ),
                    None,
                )
                if owner is not None:
                    ranking_direction = owner.ranking_direction
                    ranking_limit = owner.ranking_limit
            task_semantic_refs = tuple(
                semantic_ref(handle_id)
                for handle_id in task.input_refs
            )
            source_context: list[str] = []
            by_alias = {
                str(row.get("handle_ref")): row
                for row in governed_semantic_inventory
                if row.get("handle_ref")
            }
            for semantic in task_semantic_refs:
                row = by_alias.get(semantic.ref) or {}
                for surface in row.get("source_surfaces") or ():
                    value = str(surface).strip()
                    if value and value not in source_context:
                        source_context.append(value)
            ready_task_states.append(
                TaskActionState(
                    task_id=task.task_id,
                    question_id=task.question_id,
                    task_kind=task.task_kind,
                    capability_key=capability.value,
                    origin=task.origin,
                    semantic_refs=task_semantic_refs,
                    parent_obligation_id=task.parent_obligation_id,
                    trigger_evidence_ref=task.trigger_evidence_ref,
                    ranking_direction=ranking_direction,
                    ranking_limit=ranking_limit,
                    semantic_context=tuple(source_context),
                )
            )

        active_obligation_ids = (
            tuple(item.obligation_id for item in ledger.active_user_must)
            if ledger is not None
            else ()
        )
        state_version = str(
            (action_frontier or {}).get("progress_fingerprint")
            or runtime.snapshot.accepted_contract_id
            or runtime.snapshot.run_id
        )
        inspectable_states: list[InspectableEvidenceState] = []
        directive_parent_ids = {
            item.parent_obligation_id for item in directive_states
        }
        for ref in dict.fromkeys(inspectable_old):
            if evidence_store is None:
                continue
            try:
                evidence = evidence_store.get(ref)
            except Exception:
                continue
            capability_keys: list[str] = []
            lifecycle_relevance: list[str] = []
            if ledger is not None:
                for item in ledger.items:
                    if item.obligation_id in tuple(
                        getattr(evidence, "obligation_ids", ()) or ()
                    ):
                        capability_keys.append(item.capability_key.value)
                    if (
                        item.obligation_id in directive_parent_ids
                        and evidence_belongs_to_parent_lineage(
                            ledger=ledger,
                            evidence=evidence,
                            parent_obligation_id=item.obligation_id,
                        )
                    ):
                        lifecycle_relevance.append("OPEN_ADAPTIVE_DIRECTIVE")
                    if (
                        item.capability_key == ManagerCapabilityKey.ROOT_CAUSE
                        and evidence_belongs_to_parent_lineage(
                            ledger=ledger,
                            evidence=evidence,
                            parent_obligation_id=item.obligation_id,
                        )
                    ):
                        lifecycle_relevance.append("ACTIVE_ROOT")
            inspectable_states.append(
                InspectableEvidenceState(
                    evidence_ref=ref,
                    capability_keys=tuple(dict.fromkeys(capability_keys)),
                    evidence_kind=str(
                        getattr(evidence, "evidence_kind", "") or ""
                    )
                    or None,
                    lifecycle_relevance=tuple(
                        dict.fromkeys(lifecycle_relevance)
                    ),
                )
            )

        context = ManagerActionSetContext(
            state_version=state_version,
            root_states=tuple(root_states),
            directive_states=tuple(directive_states),
            parent_evidence_states=tuple(parent_evidence_states),
            goal_tasks=tuple(goal_task_states),
            ready_tasks=tuple(ready_task_states),
            inspectable_evidence=tuple(inspectable_states),
            fresh_disclosed_evidence_ref=fresh_ref,
            fresh_disclosed_verified=fresh_verified,
            remaining_research_turns=max(
                runtime.budget.max_manager_turns
                - runtime.snapshot.research_manager_turns,
                0,
            ),
            clarification_obligation_ids=active_obligation_ids,
            clarification_grounded=_clarification_has_governed_grounding(
                observations,
                accepted_contract_present=runtime.accepted_contract is not None,
            ),
        )
        return ManagerActionSetBuilder.build(context)


    def _prompt(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations: list[dict[str, Any]],
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state: ResearchStateView | None = None,
        ready_tasks: tuple[Any, ...] = (),
        hypothesis_ledgers: dict[str, Any] | None = None,
        action_set: ManagerActionSet | None = None,
        governed_semantic_inventory: tuple[dict[str, Any], ...] = (),
    ) -> str:
        ledger = runtime.ledger
        ledger_view = []
        if ledger is not None:
            ledger_view = [
                {
                    "obligation_id": item.obligation_id,
                    "capability": item.capability_key.value,
                    "origin": item.origin.value,
                    "priority": item.priority.value,
                    "polarity": item.polarity.value,
                    "status": item.status.value,
                    "semantic_handle_refs": [
                        self._handle_alias(handle_id)
                        for handle_id in item.semantic_handle_refs
                    ],
                    "evidence_refs": list(item.evidence_refs),
                    "blocker": item.blocker,
                }
                for item in ledger.items
            ]
        semantic_handle_catalog: list[dict[str, Any]] = []
        seen_semantic_aliases: set[str] = set()
        for root_id, hypothesis_ledger in sorted(
            (hypothesis_ledgers or {}).items()
        ):
            try:
                root_item = next(
                    item
                    for item in hypothesis_ledger.obligation_ledger.items
                    if item.obligation_id == root_id
                )
            except StopIteration:
                continue
            refs = list(root_item.semantic_handle_refs)
            for entry in hypothesis_ledger.state.entries:
                refs.extend(entry.semantic_handle_refs)
            for handle_id in dict.fromkeys(refs):
                alias = self._handle_alias(handle_id)
                if alias in seen_semantic_aliases:
                    continue
                metadata = hypothesis_ledger.semantic_handle_metadata(handle_id)
                semantic_handle_catalog.append(
                    {
                        "handle_ref": alias,
                        **metadata,
                    }
                )
                seen_semantic_aliases.add(alias)

        payload = {
            "USER_MESSAGE": question,
            "MANAGER_STATE": runtime.snapshot.state.value,
            "ACCEPTED_CONTRACT_ID": runtime.snapshot.accepted_contract_id,
            "OBLIGATION_LEDGER": ledger_view,
            "EVIDENCE_REFS": list(runtime.snapshot.evidence_refs),
            "CONVERSATION_SURFACE": _conversation_surface_view(conversation),
            "CAPABILITY_BINDING_CONTRACT": self._capabilities.manager_contract(),
            "ROOT_CAUSE_NEXT_TEST_CONTRACT": (
                list(root_cause_next_test_contract(capabilities=self._capabilities))
                if hypothesis_ledgers
                else []
            ),
            "SEMANTIC_HANDLE_CATALOG": semantic_handle_catalog,
            "ACCEPTED_RESEARCH_DIRECTIVES": (
                [
                    item.model_dump(mode="json")
                    for item in runtime.accepted_contract.research_directives
                ]
                if runtime.accepted_contract is not None
                else []
            ),
            "RESEARCH_DIRECTIVE_DISPOSITIONS": [
                item.model_dump(mode="json")
                for item in runtime.directive_dispositions
            ],
            "ACTION_FRONTIER": action_frontier or {},
            "HYPOTHESIS_LEDGERS": [
                {
                    "parent_obligation_id": root_id,
                    "entries": [
                        {
                            "hypothesis_id": entry.hypothesis_id,
                            "statement": entry.statement,
                            "status": entry.status.value,
                            "semantic_handle_refs": [
                                self._handle_alias(ref)
                                for ref in entry.semantic_handle_refs
                            ],
                            "trigger_evidence_refs": list(entry.trigger_evidence_refs),
                            "evidence_links": [
                                {
                                    "evidence_ref": link.evidence_ref,
                                    "relation": link.relation.value,
                                }
                                for link in entry.evidence_links
                            ],
                            "next_test_task_refs": list(entry.next_test_task_refs),
                            "limitations": list(entry.limitations),
                        }
                        for entry in ledger.state.entries
                    ],
                }
                for root_id, ledger in sorted(
                    (hypothesis_ledgers or {}).items()
                )
            ],
            "READY_RESEARCH_TASKS": [
                {
                    "task_id": task.task_id,
                    "question_id": task.question_id,
                    "task_kind": task.task_kind,
                    "input_refs": [
                        self._handle_alias(handle_id)
                        for handle_id in task.input_refs
                    ],
                    "parent_task_id": task.parent_task_id,
                    "parent_obligation_id": task.parent_obligation_id,
                    "trigger_evidence_ref": task.trigger_evidence_ref,
                    "branch_depth": task.branch_depth,
                }
                for task in ready_tasks
                if task.state == "pending"
            ],
            "ACCUMULATED_RESEARCH_STATE": (
                None
                if research_state is None
                else research_state.model_copy(update={"latest_delta": None}).model_dump(mode="json")
            ),
            "CURRENT_RESULT_DELTA": (
                None
                if research_state is None or research_state.latest_delta is None
                else {
                    **research_state.latest_delta.model_dump(mode="json"),
                    "inspection_required": (
                        True
                        if action_set is None
                        else not bool(
                            research_state.latest_delta.disclosed_in_current_prompt
                            and research_state.latest_delta.verified is True
                        )
                    ),
                }
            ),
            "MANAGER_ACTION_SET": (
                {}
                if action_set is None
                else action_set.model_view()
            ),
            "GOVERNED_SEMANTIC_INVENTORY": list(governed_semantic_inventory),
            # Diagnostic tail only. It is never the sole Research state authority.
            "RECENT_OBSERVATIONS": observations[-4:],
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _branch_task_id(
        *,
        action_ref: str,
        index: int,
        capability_key: str,
    ) -> str:
        import hashlib

        raw = f"{action_ref}|{index}|{capability_key}".encode("utf-8")
        return "branch_" + hashlib.sha256(raw).hexdigest()[:24]

    def _hydrate_action_choice(
        self,
        *,
        action_instance,
        payload: dict[str, Any],
    ) -> ManagerDecisionTransport:
        action = ManagerActionKind(action_instance.action_kind)
        bindings = dict(action_instance.bindings)

        if action == ManagerActionKind.RESOLVE_SEMANTICS:
            return ManagerDecisionTransport(
                action=action,
                resolve_provenance="AGENT_DERIVED",
                target_kind_hints=(payload["target_kind_hint"],),
                semantic_parent_obligation_id=bindings["parent_obligation_id"],
                semantic_evidence_ref=bindings["evidence_ref"],
                semantic_proposal=payload["semantic_proposal"],
            )
        if action == ManagerActionKind.PROPOSE_BRANCHES:
            handles_by_capability = dict(
                bindings["branch_handles_by_capability"]
            )
            candidates = []
            seen_caps: set[str] = set()
            for index, item in enumerate(payload["branch_candidates"]):
                capability = str(item["capability_key"])
                if capability in seen_caps:
                    raise ValueError(
                        "branch candidate capability must be unique in one action"
                    )
                seen_caps.add(capability)
                handles = handles_by_capability.get(capability)
                if not handles:
                    raise ValueError(
                        "branch candidate capability is not executable in selected action"
                    )
                candidates.append(
                    ManagerBranchCandidateProposal(
                        task_id=self._branch_task_id(
                            action_ref=action_instance.action_ref,
                            index=index,
                            capability_key=capability,
                        ),
                        capability_key=ManagerCapabilityKey(capability),
                        input_handles=tuple(handles),
                        material_reason=str(item["material_reason"]),
                    )
                )
            return ManagerDecisionTransport(
                action=action,
                branch_parent_obligation_id=bindings["parent_obligation_id"],
                branch_evidence_ref=bindings["evidence_ref"],
                branch_candidates=tuple(candidates),
            )
        if action == ManagerActionKind.PROPOSE_GOAL_TASK:
            selected = str(payload["task_capability"])
            allowed = tuple(str(value) for value in bindings["allowed_task_capabilities"])
            if selected not in allowed:
                raise ValueError(
                    "goal task capability is not admitted by selected action_ref"
                )
            return ManagerDecisionTransport(
                action=action,
                goal_parent_obligation_id=bindings["parent_obligation_id"],
                goal_task_capability=ManagerCapabilityKey(selected),
                goal_task_semantic_surfaces=tuple(
                    ManagerGoalTaskSemanticProposal.model_validate(item)
                    for item in payload["semantic_surfaces"]
                ),
                goal_task_material_reason=str(payload["material_reason"]),
                goal_task_ranking_direction=payload["ranking_direction"],
                goal_task_ranking_limit=payload["ranking_limit"],
            )
        if action == ManagerActionKind.DISPOSITION_RESEARCH_DIRECTIVE:
            return ManagerDecisionTransport(
                action=action,
                directive_id=bindings["directive_id"],
                directive_evidence_ref=bindings["evidence_ref"],
                directive_disposition="NO_MATERIAL_DIRECTION",
                directive_reason=payload["directive_reason"],
            )
        if action in {
            ManagerActionKind.PROPOSE_HYPOTHESIS,
            ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST,
        }:
            kwargs: dict[str, Any] = {
                "action": action,
                "hypothesis_parent_obligation_id": bindings[
                    "parent_obligation_id"
                ],
                "hypothesis_statement": payload["hypothesis_statement"],
                "hypothesis_semantic_handles": tuple(
                    bindings["semantic_handles"]
                ),
                "hypothesis_trigger_evidence_refs": (
                    bindings["trigger_evidence_ref"],
                ),
                "hypothesis_limitations": tuple(
                    payload["hypothesis_limitations"]
                ),
            }
            if action == ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST:
                kwargs.update(
                    {
                        "next_test_task_kind": ResearchTaskKind(
                            bindings["next_test_task_kind"]
                        ),
                        "next_test_input_handles": tuple(
                            bindings["next_test_input_handles"]
                        ),
                        "next_test_trigger_evidence_ref": bindings[
                            "trigger_evidence_ref"
                        ],
                        "next_test_material_reason": payload[
                            "next_test_material_reason"
                        ],
                        "next_test_ranking_direction": payload[
                            "next_test_ranking_direction"
                        ],
                        "next_test_ranking_limit": payload[
                            "next_test_ranking_limit"
                        ],
                    }
                )
            return ManagerDecisionTransport(**kwargs)
        if action == ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION:
            return ManagerDecisionTransport(
                action=action,
                hypothesis_ref=bindings["hypothesis_ref"],
                hypothesis_relation_evidence_ref=bindings["evidence_ref"],
                hypothesis_relation=HypothesisEvidenceRelation(
                    payload["hypothesis_relation"]
                ),
            )
        if action == ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST:
            return ManagerDecisionTransport(
                action=action,
                hypothesis_ref=bindings["hypothesis_ref"],
                next_test_task_kind=ResearchTaskKind(
                    bindings["next_test_task_kind"]
                ),
                next_test_input_handles=tuple(
                    bindings["next_test_input_handles"]
                ),
                next_test_trigger_evidence_ref=bindings[
                    "trigger_evidence_ref"
                ],
                next_test_material_reason=payload[
                    "next_test_material_reason"
                ],
                next_test_ranking_direction=payload[
                    "next_test_ranking_direction"
                ],
                next_test_ranking_limit=payload[
                    "next_test_ranking_limit"
                ],
            )
        if action == ManagerActionKind.RUN_ANALYTICS:
            ranking_direction = bindings.get("ranking_direction")
            ranking_limit = bindings.get("ranking_limit")
            if "ranking_direction" in payload:
                ranking_direction = payload["ranking_direction"]
                ranking_limit = payload["ranking_limit"]
            return ManagerDecisionTransport(
                action=action,
                research_task_id=bindings.get("research_task_id"),
                obligation_ids=tuple(bindings["obligation_ids"]),
                metric_handles=tuple(bindings.get("metric_handles") or ()),
                dimension_handles=tuple(
                    bindings.get("dimension_handles") or ()
                ),
                filter_handles=tuple(bindings.get("filter_handles") or ()),
                period_handle=bindings.get("period_handle"),
                comparison_handle=bindings.get("comparison_handle"),
                ranking_direction=ranking_direction,
                limit=ranking_limit,
                derived_task_id=bindings.get("derived_task_id"),
                derived_parent_obligation_id=bindings.get(
                    "derived_parent_obligation_id"
                ),
                derived_capability_key=(
                    ManagerCapabilityKey(bindings["derived_capability_key"])
                    if bindings.get("derived_capability_key")
                    else None
                ),
                derived_evidence_ref=bindings.get("derived_evidence_ref"),
                derived_reason=(
                    "server-hydrated READY ResearchTask execution"
                    if bindings.get("derived_task_id")
                    else None
                ),
            )
        if action == ManagerActionKind.RUN_RELATIONSHIP:
            return ManagerDecisionTransport(
                action=action,
                research_task_id=bindings.get("task_id"),
                relationship_obligation_id=bindings["obligation_id"],
                focus_handles=tuple(bindings["focus_handles"]),
                counterpart_handles=tuple(bindings["counterpart_handles"]),
            )
        if action == ManagerActionKind.INSPECT_EVIDENCE:
            return ManagerDecisionTransport(
                action=action,
                evidence_ref=bindings["evidence_ref"],
            )
        if action == ManagerActionKind.REQUEST_CLARIFICATION:
            return ManagerDecisionTransport(
                action=action,
                obligation_ids=tuple(bindings["obligation_ids"]),
                clarification_reason=payload["clarification_reason"],
            )
        if action == ManagerActionKind.FINISH:
            return ManagerDecisionTransport(action=action)
        raise RuntimeError(
            f"unsupported ManagerActionSet action: {action_instance.action_kind}"
        )

    def _decision_with_action_set(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations,
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state: ResearchStateView | None = None,
        ready_tasks: tuple[Any, ...] = (),
        hypothesis_ledgers: dict[str, Any] | None = None,
        evidence_store=None,
    ):
        governed_semantic_inventory = self._governed_semantic_inventory(
            runtime=runtime,
            hypothesis_ledgers=hypothesis_ledgers,
        )
        action_set = self._action_set(
            runtime=runtime,
            observations=observations,
            action_frontier=action_frontier,
            research_state=research_state,
            hypothesis_ledgers=hypothesis_ledgers,
            evidence_store=evidence_store,
            research_tasks=ready_tasks,
            governed_semantic_inventory=governed_semantic_inventory,
        )
        user = self._prompt(
            question=question,
            runtime=runtime,
            observations=observations,
            conversation=conversation,
            action_frontier=action_frontier,
            research_state=research_state,
            ready_tasks=ready_tasks,
            hypothesis_ledgers=hypothesis_ledgers,
            action_set=action_set,
            governed_semantic_inventory=governed_semantic_inventory,
        )
        root_cause_enabled = bool(hypothesis_ledgers)
        system_prompt = (
            _SYSTEM + _ROOT_CAUSE_SYSTEM_ADDENDUM
            if root_cause_enabled
            else _SYSTEM
        )
        kwargs = {
            "schema": action_set.provider_schema(),
            "schema_name": "dima_research_manager_action_v2",
        }
        raw = self._structured(system_prompt, user, **kwargs)
        try:
            instance, payload = action_set.resolve_choice(raw)
            return (
                self._hydrate_action_choice(
                    action_instance=instance,
                    payload=payload,
                ),
                action_set,
                instance.action_ref,
            )
        except Exception as first_error:
            repair_system = (
                system_prompt
                + "\n\nFORMAT_REPAIR_ONLY: Previous output failed the current "
                  "ManagerActionSet schema. Keep the SAME action_ref and cognitive "
                  "decision. Only repair fields required by that action card."
            )
            repair_user = (
                user
                + "\n\nPREVIOUS_INVALID_OUTPUT:\n"
                + (
                    raw
                    if isinstance(raw, str)
                    else json.dumps(raw, ensure_ascii=False)
                )
                + "\n\nFORMAT_ERROR:\n"
                + str(first_error)[:1200]
            )
            repaired = self._structured(
                repair_system,
                repair_user,
                **kwargs,
            )
            try:
                instance, payload = action_set.resolve_choice(repaired)
                return (
                    self._hydrate_action_choice(
                        action_instance=instance,
                        payload=payload,
                    ),
                    action_set,
                    instance.action_ref,
                )
            except Exception as exc:
                raise RuntimeError(
                    "RESEARCH_MANAGER ActionSet output invalid after one format retry: "
                    f"{exc}"
                ) from exc


    def _decision(
        self,
        *,
        question: str,
        runtime: ManagerRuntime,
        observations,
        conversation: ConversationStateV2 | None = None,
        action_frontier: dict[str, Any] | None = None,
        research_state: ResearchStateView | None = None,
        ready_tasks: tuple[Any, ...] = (),
        hypothesis_ledgers: dict[str, Any] | None = None,
        evidence_store=None,
    ):
        decision, _action_set, _action_ref = self._decision_with_action_set(
            question=question,
            runtime=runtime,
            observations=observations,
            conversation=conversation,
            action_frontier=action_frontier,
            research_state=research_state,
            ready_tasks=ready_tasks,
            hypothesis_ledgers=hypothesis_ledgers,
            evidence_store=evidence_store,
        )
        return decision


    def _source_refs(self, *, message_id: str, surfaces: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            self._source_spans.mint_exact(message_id=message_id, surface=surface).source_ref
            for surface in surfaces
        )

    def _compile_tool(
        self,
        *,
        decision: ManagerDecisionTransport,
        message_id: str,
        source_hash: str,
        request_ref: str,
        runtime: ManagerRuntime,
    ) -> ManagerToolCall | None:
        if decision.action in {
            ManagerActionKind.FINISH,
            ManagerActionKind.PROPOSE_BRANCHES,
        }:
            return None

        if decision.action == ManagerActionKind.RESOLVE_SEMANTICS:
            if decision.resolve_provenance == "USER_SOURCE":
                refs = self._source_refs(
                    message_id=message_id,
                    surfaces=decision.source_surfaces,
                )
                args = {
                    "provenance": "USER_SOURCE",
                    "source_refs": refs,
                    "target_kind_hints": decision.target_kind_hints,
                    "temporal_anchor_handle": self._decode_handle(decision.temporal_anchor_handle),
                    "base_period_handle": self._decode_handle(decision.base_period_handle),
                }
            else:
                args = {
                    "provenance": "AGENT_DERIVED",
                    "source_refs": (),
                    "target_kind_hints": decision.target_kind_hints,
                    "temporal_anchor_handle": self._decode_handle(decision.temporal_anchor_handle),
                    "base_period_handle": self._decode_handle(decision.base_period_handle),
                    "parent_obligation_id": decision.semantic_parent_obligation_id,
                    "evidence_ref": decision.semantic_evidence_ref,
                    "natural_language_proposal": decision.semantic_proposal,
                }
            return ManagerToolCall(
                name=ManagerToolName.RESOLVE_SEMANTICS,
                args=args,
            )

        if decision.action == ManagerActionKind.PROPOSE_ACCEPTANCE:
            obligations = []
            for item in decision.obligations:
                refs = self._source_refs(
                    message_id=message_id,
                    surfaces=item.source_surfaces,
                )
                obligations.append(
                    CandidateObligation(
                        obligation_id=item.obligation_id,
                        capability_key=item.capability_key,
                        origin=ObligationOrigin(item.origin),
                        priority=item.priority,
                        polarity=item.polarity,
                        source_refs=refs,
                        semantic_handle_refs=self._decode_handles(item.semantic_handle_refs),
                        open_questions=item.open_questions,
                        ranking_direction=item.ranking_direction,
                        ranking_limit=item.ranking_limit,
                    )
                )
            envelope = UserIntentEnvelope(
                attempt_id=f"{runtime.snapshot.run_id}:attempt:{runtime.snapshot.manager_turns}",
                turn_id=message_id,
                request_ref=request_ref,
                source_message_hash=source_hash,
                model_role="RESEARCH_MANAGER",
                obligations=tuple(obligations),
            )
            return ManagerToolCall(
                name=ManagerToolName.PROPOSE_ACCEPTANCE,
                args={"envelope": envelope.model_dump(mode="json")},
            )

        if decision.action == ManagerActionKind.RUN_ANALYTICS:
            return ManagerToolCall(
                name=ManagerToolName.RUN_ANALYTICS,
                args={
                    "research_task_id": decision.research_task_id,
                    "obligation_ids": decision.obligation_ids,
                    "metric_handles": self._decode_handles(decision.metric_handles),
                    "dimension_handles": self._decode_handles(decision.dimension_handles),
                    "filter_handles": self._decode_handles(decision.filter_handles),
                    "period_handle": self._decode_handle(decision.period_handle),
                    "comparison_handle": self._decode_handle(decision.comparison_handle),
                    "ranking_direction": decision.ranking_direction,
                    "limit": decision.limit,
                    "derived_task_id": decision.derived_task_id,
                    "derived_parent_obligation_id": decision.derived_parent_obligation_id,
                    "derived_capability_key": (
                        decision.derived_capability_key.value
                        if decision.derived_capability_key is not None
                        else None
                    ),
                    "derived_evidence_ref": decision.derived_evidence_ref,
                },
            )

        if decision.action == ManagerActionKind.RUN_RELATIONSHIP:
            return ManagerToolCall(
                name=ManagerToolName.RUN_RELATIONSHIP,
                args={
                    "research_task_id": decision.research_task_id,
                    "obligation_id": decision.relationship_obligation_id,
                    "focus_handles": self._decode_handles(decision.focus_handles),
                    "counterpart_handles": self._decode_handles(decision.counterpart_handles),
                },
            )

        if decision.action == ManagerActionKind.INSPECT_EVIDENCE:
            return ManagerToolCall(
                name=ManagerToolName.INSPECT_EVIDENCE,
                args={"evidence_ref": decision.evidence_ref},
            )

        if decision.action == ManagerActionKind.REQUEST_CLARIFICATION:
            return ManagerToolCall(
                name=ManagerToolName.REQUEST_CLARIFICATION,
                args={
                    "obligation_ids": decision.obligation_ids,
                    "reason": decision.clarification_reason,
                },
            )

        raise RuntimeError(f"unsupported Manager action: {decision.action}")

    @staticmethod
    def _ledger_for_hypothesis(
        ledgers: dict[str, Any],
        hypothesis_ref: str,
    ):
        matches = []
        for ledger in ledgers.values():
            try:
                ledger.get(hypothesis_ref)
                matches.append(ledger)
            except Exception:
                continue
        if len(matches) != 1:
            raise RootCauseOrchestrationError(
                f"hypothesis_ref resolves to {len(matches)} active ROOT_CAUSE ledgers"
            )
        return matches[0]

    def _materialize_goal_task_from_decision(
        self,
        *,
        message_id: str,
        runtime: ManagerRuntime,
        executor,
        task_registry: ResearchTaskRegistry,
        decision: ManagerDecisionTransport,
        action_ref: str,
    ) -> tuple[ResearchTask | None, dict[str, Any]]:
        """Late-bind one concrete analytical task under accepted Research goal authority.

        The Manager supplies only task family + exact current-user-source substrings.
        Canonical semantic identity remains Resolver/registry-owned. Failure to ground the
        child task never rewrites or clarifies the already-accepted parent USER_MUST goal.
        """

        parent_id = decision.goal_parent_obligation_id
        capability = decision.goal_task_capability
        if parent_id is None or capability is None or runtime.ledger is None:
            return None, {
                "kind": "goal_task_materialization_rejected",
                "reason": "missing accepted parent/capability",
            }
        parent = next(
            (
                item
                for item in runtime.ledger.items
                if item.obligation_id == parent_id
            ),
            None,
        )
        if parent is None:
            return None, {
                "kind": "goal_task_materialization_rejected",
                "reason": "accepted parent obligation unavailable",
                "parent_obligation_id": parent_id,
            }

        parent_surfaces: list[str] = []
        for source_ref in parent.source_refs:
            try:
                span = self._source_spans.validate(source_ref)
            except Exception:
                continue
            if span.message_id != message_id:
                continue
            parent_surfaces.append(str(span.exact_surface))

        proposed = tuple(decision.goal_task_semantic_surfaces)
        if not proposed:
            return None, {
                "kind": "goal_task_materialization_rejected",
                "reason": "no concrete semantic surfaces proposed",
                "parent_obligation_id": parent_id,
            }

        refs: list[str] = []
        hints: list[str] = []
        for item in proposed:
            surface = str(item.surface)
            if not any(surface in parent_surface for parent_surface in parent_surfaces):
                return None, {
                    "kind": "goal_task_materialization_rejected",
                    "reason": "task semantic surface is outside accepted parent source lineage",
                    "parent_obligation_id": parent_id,
                    "surface": surface,
                }
            if item.kind_hint == "unknown":
                return None, {
                    "kind": "goal_task_materialization_rejected",
                    "reason": "concrete task semantic kind cannot remain unknown",
                    "parent_obligation_id": parent_id,
                    "surface": surface,
                }
            try:
                ref = self._source_spans.mint_exact(
                    message_id=message_id,
                    surface=surface,
                ).source_ref
            except Exception as exc:
                return None, {
                    "kind": "goal_task_materialization_rejected",
                    "reason": f"exact task source invalid: {exc}",
                    "parent_obligation_id": parent_id,
                    "surface": surface,
                }
            refs.append(ref)
            hints.append(item.kind_hint)

        step = runtime.call_tool(
            ManagerToolCall(
                name=ManagerToolName.RESOLVE_SEMANTICS,
                args={
                    "provenance": "USER_SOURCE",
                    "source_refs": tuple(refs),
                    "source_obligation_ids": tuple(parent_id for _ in refs),
                    "target_kind_hints": tuple(hints),
                    "temporal_anchor_handle": None,
                    "base_period_handle": None,
                },
            ),
            executor=executor,
        )
        result = step.tool_result
        resolved = tuple(getattr(result, "resolved", ()) or ())
        by_ref = {
            item.source_ref: item
            for item in resolved
            if getattr(item, "source_ref", None)
        }
        bindings: list[SemanticBindingRef] = []
        handles: list[str] = []
        for ref in refs:
            item = by_ref.get(ref)
            if item is None:
                continue
            handle = item.handle
            bindings.append(
                SemanticBindingRef(
                    source_ref=ref,
                    handle_id=handle.handle_id,
                    target_kind=handle.target_kind,
                )
            )
            handles.append(handle.handle_id)

        candidate = parent.model_copy(
            update={
                "capability_key": capability,
                "semantic_handle_refs": tuple(dict.fromkeys(handles)),
                "semantic_bindings": tuple(bindings),
                "scope_refs": (),
                "ranking_direction": decision.goal_task_ranking_direction,
                "ranking_limit": decision.goal_task_ranking_limit,
            }
        )
        if self._root_cause_context is None:
            return None, {
                "kind": "goal_task_materialization_rejected",
                "reason": "semantic authority registry unavailable",
                "parent_obligation_id": parent_id,
            }
        validator = CapabilityBindingValidator(
            semantic_handles=self._root_cause_context.semantic_handles,
            capabilities=self._capabilities,
        )
        validation = validator.validate(
            candidate,
            tenant_binding=self._root_cause_context.tenant_binding,
            context_version=self._root_cause_context.context_version,
        )
        if not validation.valid or validation.binding is None:
            return None, {
                "kind": "goal_task_grounding_failed",
                "parent_obligation_id": parent_id,
                "capability": capability.value,
                "reasons": list(validation.reasons),
            }

        import hashlib
        payload = (
            f"{runtime.snapshot.run_id}|{action_ref}|{parent_id}|{capability.value}|"
            + "|".join(sorted(handles))
        )
        task_id = "goal_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        task = self._research_tasks.materialize_goal_task(
            runtime=runtime,
            parent_obligation_id=parent_id,
            capability_key=capability,
            task_id=task_id,
            input_refs=tuple(dict.fromkeys(handles)),
        )
        task = task_registry.register(task)
        return task, {
            "kind": "goal_task_materialized",
            "parent_obligation_id": parent_id,
            "task_id": task.task_id,
            "task_kind": task.task_kind,
            "capability": capability.value,
            "semantic_handle_count": len(task.input_refs),
        }

    @staticmethod
    def _pending_user_seed_for_obligation(
        *,
        task_registry: ResearchTaskRegistry,
        obligation_id: str,
    ):
        candidates = [
            task
            for task in task_registry.tasks
            if task.origin == "USER_SEED"
            and task.question_id == obligation_id
            and task.state == "pending"
        ]
        if len(candidates) > 1:
            raise ResearchTaskMaterializationError(
                "multiple pending USER_SEED tasks exist for one obligation; "
                "explicit orchestration selection is required"
            )
        return candidates[0] if candidates else None

    def _scheduled_binding(
        self,
        *,
        runtime: ManagerRuntime,
        task,
        capability_key: ManagerCapabilityKey | None = None,
        ranking_direction: str | None = None,
        ranking_limit: int | None = None,
    ):
        if runtime.ledger is None or self._root_cause_context is None:
            raise ResearchTaskInvocationCompileError(
                "deterministic scheduling requires accepted ledger + semantic authority"
            )
        obligation_id = (
            task.question_id
            if task.origin == "USER_SEED"
            else task.parent_obligation_id
        )
        if obligation_id is None:
            raise ResearchTaskInvocationCompileError(
                "scheduled task has no accepted obligation owner"
            )
        try:
            obligation = next(
                item
                for item in runtime.ledger.items
                if item.obligation_id == obligation_id
            )
        except StopIteration as exc:
            raise ResearchTaskInvocationCompileError(
                "scheduled task obligation is absent from accepted ledger"
            ) from exc

        candidate = obligation
        if capability_key is not None:
            candidate = obligation.model_copy(
                update={
                    "capability_key": capability_key,
                    "semantic_handle_refs": task.input_refs,
                    "ranking_direction": ranking_direction,
                    "ranking_limit": ranking_limit,
                }
            )
        if task.origin == "GOAL_DERIVED":
            for handle_id in task.input_refs:
                handle = self._root_cause_context.semantic_handles.validate(
                    handle_id,
                    tenant_binding=self._root_cause_context.tenant_binding,
                    context_version=self._root_cause_context.context_version,
                )
                if (
                    handle.provenance_type != "USER_SOURCE"
                    or handle.parent_obligation_id != obligation_id
                ):
                    raise ResearchTaskInvocationCompileError(
                        "goal-derived task semantic authority must be current-goal USER_SOURCE"
                    )

        validator = CapabilityBindingValidator(
            semantic_handles=self._root_cause_context.semantic_handles,
            capabilities=self._capabilities,
        )
        result = validator.validate(
            candidate,
            tenant_binding=self._root_cause_context.tenant_binding,
            context_version=self._root_cause_context.context_version,
        )
        if not result.valid or result.binding is None:
            raise ResearchTaskInvocationCompileError(
                "scheduled task is not losslessly bound: "
                + "; ".join(result.reasons)
            )
        return obligation, result.binding

    def _execute_scheduled_task(
        self,
        *,
        runtime: ManagerRuntime,
        executor,
        task_registry: ResearchTaskRegistry,
        task,
        capability_key: ManagerCapabilityKey | None = None,
        ranking_direction: str | None = None,
        ranking_limit: int | None = None,
    ):
        if self._research_tool_runner is None:
            raise ResearchTaskInvocationCompileError(
                "deterministic scheduler requires ResearchToolRunner"
            )
        obligation, binding = self._scheduled_binding(
            runtime=runtime,
            task=task,
            capability_key=capability_key,
            ranking_direction=ranking_direction,
            ranking_limit=ranking_limit,
        )
        scheduler = DeterministicResearchScheduler(
            runner=self._research_tool_runner,
        )
        return scheduler.execute(
            task=task,
            obligation=obligation,
            binding=binding,
            runtime=runtime,
            executor=executor,
            principal=getattr(executor, "principal", None),
            task_registry=task_registry,
            cancel_check=self._cancel_check,
        )

    def _account_successful_adaptive_branch(
        self,
        *,
        runtime: ManagerRuntime,
        evidence_store,
        task,
        result_evidence,
    ) -> tuple[str, ...]:
        """Account one successful governed AGENT_DERIVED branch exactly once.

        This is lifecycle accounting, not cognition. A branch can satisfy an accepted
        ADAPT_ON_EVIDENCE directive regardless of whether it was auto-executed at
        materialization time or selected later through RUN_ANALYTICS/RUN_RELATIONSHIP.
        Blocked/failed work, foreign lineage, uninspected trigger Evidence, or a task
        without successful VERIFIED result Evidence can never close the directive.
        """
        contract = runtime.accepted_contract
        if contract is None or task.origin != "AGENT_DERIVED":
            return ()
        trigger_ref = task.trigger_evidence_ref
        parent_id = task.parent_obligation_id
        if not trigger_ref or not parent_id or task.state != "complete":
            return ()

        trigger = evidence_store.get(trigger_ref)
        if (
            not trigger.verified
            or trigger_ref not in runtime.snapshot.inspected_evidence_refs
            or task.parent_task_id != trigger.task_id
        ):
            return ()
        if (
            result_evidence is None
            or not result_evidence.verified
            or result_evidence.task_id != task.task_id
        ):
            return ()

        accounted: list[str] = []
        for directive in contract.research_directives:
            if (
                directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE
                or directive.parent_obligation_id != parent_id
            ):
                continue
            current = runtime.directive_disposition(directive.directive_id)
            if current.status != ResearchDirectiveDispositionStatus.OPEN:
                continue
            runtime.account_research_directive(
                directive_id=directive.directive_id,
                status=ResearchDirectiveDispositionStatus.APPLIED,
                evidence_ref=trigger_ref,
                branch_task_refs=(task.task_id,),
                reason=(
                    "governed material branch executed with VERIFIED Evidence "
                    "and accounted independent of execution transport"
                ),
            )
            accounted.append(directive.directive_id)
        return tuple(accounted)


    def _account_root_next_test_as_adaptive_branch(
        self,
        *,
        runtime: ManagerRuntime,
        evidence_store,
        task,
        root_obligation_id: str,
        trigger_evidence_ref: str,
        result_evidence,
    ) -> tuple[str, ...]:
        """Account only a proven same-root successful next test as ADAPT_ON_EVIDENCE.

        The directive contract is not relaxed here.  The candidate task must already be
        a server-materialized AGENT_DERIVED child under the same ROOT_CAUSE obligation,
        directly descended from the inspected VERIFIED trigger Evidence's task, and its
        own execution must have produced VERIFIED Evidence.  A blocked/failed task can
        never close the directive.
        """
        contract = runtime.accepted_contract
        if contract is None:
            return ()
        trigger = evidence_store.get(trigger_evidence_ref)
        if not trigger.verified:
            raise RootCauseOrchestrationError(
                "adaptive root next-test trigger must be VERIFIED Evidence"
            )
        if trigger_evidence_ref not in runtime.snapshot.inspected_evidence_refs:
            raise RootCauseOrchestrationError(
                "adaptive root next-test trigger must be inspected"
            )
        if (
            task.origin != "AGENT_DERIVED"
            or task.parent_obligation_id != root_obligation_id
            or task.trigger_evidence_ref != trigger_evidence_ref
            or task.parent_task_id != trigger.task_id
            or task.state != "complete"
        ):
            raise RootCauseOrchestrationError(
                "root next-test provenance is not equivalent to a governed material branch"
            )
        if (
            result_evidence is None
            or not result_evidence.verified
            or result_evidence.task_id != task.task_id
        ):
            raise RootCauseOrchestrationError(
                "adaptive root next-test requires successful VERIFIED result Evidence"
            )

        accounted: list[str] = []
        for directive in contract.research_directives:
            if (
                directive.directive_type != ResearchDirectiveType.ADAPT_ON_EVIDENCE
                or directive.parent_obligation_id != root_obligation_id
            ):
                continue
            current = runtime.directive_disposition(directive.directive_id)
            if current.status != ResearchDirectiveDispositionStatus.OPEN:
                continue
            runtime.account_research_directive(
                directive_id=directive.directive_id,
                status=ResearchDirectiveDispositionStatus.APPLIED,
                evidence_ref=trigger_evidence_ref,
                branch_task_refs=(task.task_id,),
                reason=(
                    "same-root governed hypothesis next test executed with "
                    "verified Evidence and accounted as material adaptive branch"
                ),
            )
            accounted.append(directive.directive_id)
        return tuple(accounted)


    def understand(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        runtime: ManagerRuntime,
        executor,
        conversation: ConversationStateV2 | None = None,
    ) -> ManagerUnderstandingOutcome:
        """Finite pre-acceptance boundary; Manager never chooses grounding tools."""

        source_hash = self._source_spans.register_message(
            message_id=message_id,
            text=question,
        )
        if runtime.snapshot.state == ManagerState.INITIAL:
            runtime.begin_understanding()

        controller = PreAcceptanceController(
            structured=self._structured,
            source_spans=self._source_spans,
            capabilities=self._capabilities,
            context_scope_by_kind=self._context_scope_by_kind,
            signed_section_continuation=self._signed_section_continuation,
            allowed_continuation_parent_refs=self._allowed_continuation_parent_refs,
        )
        try:
            outcome = controller.run(
                question=question,
                message_id=message_id,
                request_ref=request_ref,
                source_hash=source_hash,
                runtime=runtime,
                executor=executor,
                conversation=conversation,
            )
        except ManagerBudgetError as exc:
            return ManagerUnderstandingOutcome(
                snapshot=runtime.snapshot,
                status=FiniteAcceptanceStatus.MODEL_FAILURE,
                accepted=False,
                clarification_required=False,
                observations=({"kind": "budget", "message": str(exc)},),
            )

        return ManagerUnderstandingOutcome(
            snapshot=runtime.snapshot,
            status=outcome.status,
            accepted=outcome.accepted,
            clarification_required=outcome.clarification_required,
            observations=outcome.observations,
        )

    def run(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        runtime: ManagerRuntime,
        executor,
        conversation: ConversationStateV2 | None = None,
    ) -> ManagerLoopOutcome:
        observations: list[dict[str, Any]] = []

        if (
            runtime.accepted_contract is None
            or runtime.snapshot.state == ManagerState.UNDERSTANDING
        ):
            understanding = self.understand(
                question=question,
                message_id=message_id,
                request_ref=request_ref,
                runtime=runtime,
                executor=executor,
                conversation=conversation,
            )
            observations.extend(understanding.observations)
            if not understanding.accepted:
                return ManagerLoopOutcome(
                    snapshot=runtime.snapshot,
                    run_finished=False,
                    verified_complete=False,
                    terminal_status=runtime.snapshot.terminal_status,
                    clarification_required=understanding.clarification_required,
                    observations=tuple(observations),
                    preacceptance_status=understanding.status,
                )

        source_hash = self._source_spans.register_message(
            message_id=message_id,
            text=question,
        )
        frontier = DynamicActionFrontier()
        task_registry = ResearchTaskRegistry()

        root_cause_ledgers: dict[str, Any] = {}
        if self._research_tool_runner is not None:
            seed_set = self._research_tasks.seed_initial_user_must(
                runtime=runtime,
                task_registry=task_registry,
                executable_task_kinds=self._research_tool_runner.declared_task_kinds,
            )
            observations.append(
                {
                    "kind": "seed_tasks_registered",
                    "considered_obligation_ids": list(
                        seed_set.considered_obligation_ids
                    ),
                    "ready_task_ids": [
                        task.task_id for task in seed_set.registered_tasks
                    ],
                    "deferred_obligation_ids": list(
                        seed_set.deferred_obligation_ids
                    ),
                    "already_accounted_obligation_ids": list(
                        seed_set.already_accounted_obligation_ids
                    ),
                }
            )

            for task in seed_set.registered_tasks:
                try:
                    execution = self._execute_scheduled_task(
                        runtime=runtime,
                        executor=executor,
                        task_registry=task_registry,
                        task=task,
                    )
                except ResearchTaskInvocationCompileError as exc:
                    observations.append(
                        {
                            "kind": "deterministic_schedule_deferred",
                            "task_id": task.task_id,
                            "reason": str(exc),
                        }
                    )
                    continue
                execution_outcome = ResearchExecutionOutcome.project(execution)
                if execution_outcome.blocked:
                    observations.append(
                        {
                            "kind": "deterministic_task_blocked",
                            "task_id": execution.task.task_id,
                            "tool_id": execution.contract.tool_id,
                            "result": self._manager_safe(execution.observation),
                        }
                    )
                    self._emit_progress(
                        "research_task_blocked",
                        (execution.task.task_id,),
                    )
                    continue

                evidence = execution_outcome.require_evidence()
                observations.append(
                    {
                        "kind": "deterministic_task_executed",
                        "task_id": execution.task.task_id,
                        "tool_id": execution.contract.tool_id,
                        "evidence_ref": evidence.artifact_id,
                    }
                )
                self._emit_progress(
                    "evidence_verified",
                    (evidence.artifact_id,),
                )
                if evidence.evidence_kind == "relationship_analytics":
                    self._emit_progress(
                        "relationship_checked",
                        (evidence.artifact_id,),
                    )

            if (
                self._root_cause_context is not None
                and runtime.ledger is not None
            ):
                evidence_store = getattr(executor, "evidence_store", None)
                if evidence_store is None:
                    raise RootCauseOrchestrationError(
                        "Day8 ROOT_CAUSE loop requires governed EvidenceStore"
                    )
                bootstrap_policy = RootCauseBootstrapPolicy(
                    semantic_handles=self._root_cause_context.semantic_handles,
                    capabilities=self._capabilities,
                    task_service=self._research_tasks,
                )
                for item in runtime.ledger.active_user_must:
                    if item.capability_key != ManagerCapabilityKey.ROOT_CAUSE:
                        continue
                    if item.status not in {
                        ObligationStatus.ACCEPTED,
                        ObligationStatus.READY,
                        ObligationStatus.IN_PROGRESS,
                    }:
                        # Accounted prior-turn ROOT_CAUSE authority is carried by the
                        # versioned ledger but must not reopen hypothesis state.
                        continue
                    ledger = self._root_cause_context.build_ledger(
                        runtime=runtime,
                        evidence_store=evidence_store,
                        task_registry=task_registry,
                        root_obligation_id=item.obligation_id,
                    )
                    root_cause_ledgers[item.obligation_id] = ledger
                    bootstrap = bootstrap_policy.prepare(
                        runtime=runtime,
                        evidence_store=evidence_store,
                        task_registry=task_registry,
                        root_obligation_id=item.obligation_id,
                        tenant_binding=self._root_cause_context.tenant_binding,
                        context_version=self._root_cause_context.context_version,
                    )
                    observations.append(
                        {
                            "kind": "root_cause_bootstrap",
                            "parent_obligation_id": item.obligation_id,
                            "status": bootstrap.status.value,
                            "evidence_refs": list(bootstrap.evidence_refs),
                            "candidate_task_kinds": [
                                kind.value for kind in bootstrap.candidate_task_kinds
                            ],
                            "selected_capability": (
                                bootstrap.selected_capability.value
                                if bootstrap.selected_capability is not None
                                else None
                            ),
                            "task_id": (
                                bootstrap.task.task_id
                                if bootstrap.task is not None
                                else None
                            ),
                            "reason": bootstrap.reason,
                        }
                    )
                    if (
                        bootstrap.status == RootCauseBootstrapStatus.TASK_READY
                        and bootstrap.task is not None
                        and bootstrap.selected_capability is not None
                    ):
                        try:
                            execution = self._execute_scheduled_task(
                                runtime=runtime,
                                executor=executor,
                                task_registry=task_registry,
                                task=bootstrap.task,
                                capability_key=bootstrap.selected_capability,
                            )
                            execution_outcome = ResearchExecutionOutcome.project(
                                execution
                            )
                            if execution_outcome.blocked:
                                observations.append(
                                    {
                                        "kind": "deterministic_task_blocked",
                                        "task_id": execution.task.task_id,
                                        "tool_id": execution.contract.tool_id,
                                        "context": "root_cause_bootstrap",
                                        "result": self._manager_safe(
                                            execution.observation
                                        ),
                                    }
                                )
                                self._emit_progress(
                                    "research_task_blocked",
                                    (execution.task.task_id,),
                                )
                            else:
                                evidence = execution_outcome.require_evidence()
                                observations.append(
                                    {
                                        "kind": "root_cause_bootstrap_executed",
                                        "task_id": execution.task.task_id,
                                        "tool_id": execution.contract.tool_id,
                                        "evidence_ref": evidence.artifact_id,
                                    }
                                )
                                self._emit_progress(
                                    "evidence_verified",
                                    (evidence.artifact_id,),
                                )
                        except ResearchTaskInvocationCompileError as exc:
                            observations.append(
                                {
                                    "kind": "deterministic_schedule_deferred",
                                    "task_id": bootstrap.task.task_id,
                                    "reason": str(exc),
                                }
                            )
                    if bootstrap.status == RootCauseBootstrapStatus.AMBIGUOUS_TASK:
                        runtime.require_clarification(bootstrap.reason)
                    elif bootstrap.status == RootCauseBootstrapStatus.NO_APPLICABLE_TASK:
                        runtime.block_unsupported(bootstrap.reason)
                        return ManagerLoopOutcome(
                            snapshot=runtime.snapshot,
                            run_finished=False,
                            verified_complete=False,
                            terminal_status=runtime.snapshot.terminal_status,
                            clarification_required=False,
                            observations=tuple(observations),
                            preacceptance_status=FiniteAcceptanceStatus.ACCEPTED,
                        )

        cancelled = False
        answer_now_requested = False
        while runtime.snapshot.state not in {
            ManagerState.COMPLETED,
            ManagerState.FAILED,
            ManagerState.BUDGET_EXHAUSTED,
            ManagerState.NEEDS_CLARIFICATION,
        }:
            if self._cancel_check is not None and self._cancel_check():
                for task in task_registry.tasks:
                    task_registry.cancel(task.task_id)
                observations.append({"kind": "cancelled"})
                cancelled = True
                break
            if self._answer_now_check is not None and self._answer_now_check():
                runtime.pause_partial()
                observations.append(
                    {
                        "kind": "answer_now",
                        "evidence_refs": list(runtime.snapshot.evidence_refs),
                    }
                )
                answer_now_requested = True
                break

            # Completion-relevant ADAPT policy follows durable ledger truth. A
            # partial-terminal parent deterministically closes its dependent directive
            # as BLOCKED before another cognition turn is spent.
            blocked_directives = self._reconcile_blocked_research_directives(
                runtime=runtime,
            )
            if blocked_directives:
                observations.append(
                    {
                        "kind": "research_directive_blocked_reconciled",
                        "directive_ids": list(blocked_directives),
                    }
                )

            # CompletionGate is deterministic and is checked at the loop boundary,
            # after user controls but before spending another cognition turn. A fresh
            # Evidence item is not marked inspected here: if no further cognition is
            # necessary, pretending the model saw it would manufacture disclosure.
            if self._try_deterministic_finish(
                runtime=runtime,
                task_registry=task_registry,
            ):
                observations.append(
                    {
                        "kind": "finish",
                        "status": "accepted",
                        "reason": "loop_boundary_deterministic_completion_gate",
                    }
                )
                break

            try:
                runtime.note_manager_turn(phase="research")
            except ManagerBudgetError as exc:
                observations.append({"kind": "budget", "message": str(exc)})
                break

            frontier_view = frontier.view(runtime)
            research_state = build_research_state_view(
                runtime=runtime,
                evidence_store=getattr(executor, "evidence_store", None),
            )
            try:
                decision, action_set, selected_action_ref = self._decision_with_action_set(
                    question=question,
                    runtime=runtime,
                    observations=observations,
                    conversation=conversation,
                    action_frontier=frontier_view,
                    research_state=research_state,
                    ready_tasks=task_registry.tasks,
                    hypothesis_ledgers=root_cause_ledgers,
                    evidence_store=getattr(executor, "evidence_store", None),
                )
                observations.append(
                    {
                        "kind": "manager_action_set",
                        **action_set.model_view(),
                    }
                )
                latest_delta = research_state.latest_delta
                if (
                    latest_delta is not None
                    and latest_delta.availability.value == "AVAILABLE"
                    and latest_delta.verified is True
                    and latest_delta.inspected is False
                    and bool(latest_delta.bounded_payload)
                ):
                    runtime.mark_evidence_inspected(latest_delta.evidence_ref)
                    observations.append(
                        {
                            "kind": "fresh_evidence_disclosed",
                            "evidence_ref": latest_delta.evidence_ref,
                        }
                    )
                    if _zero_row_completion_candidate(
                        runtime=runtime,
                        evidence_store=getattr(executor, "evidence_store", None),
                        task_registry=task_registry,
                    ):
                        try:
                            runtime.finish()
                            observations.append(
                                {
                                    "kind": "finish",
                                    "status": "accepted",
                                    "reason": (
                                        "fresh_disclosed_zero_row_no_material_branch"
                                    ),
                                }
                            )
                            break
                        except ManagerStateError:
                            # CompletionGate remains final authority. If the ledger or
                            # directive state is not complete, continue bounded cognition.
                            pass
            except Exception as exc:
                observations.append({"kind": "model_error", "message": str(exc)})
                break

            current_action_set = self._action_set(
                runtime=runtime,
                observations=observations,
                action_frontier=frontier.view(runtime),
                research_state=research_state,
                hypothesis_ledgers=root_cause_ledgers,
                evidence_store=getattr(executor, "evidence_store", None),
                research_tasks=task_registry.tasks,
                governed_semantic_inventory=self._governed_semantic_inventory(
                    runtime=runtime,
                    hypothesis_ledgers=root_cause_ledgers,
                ),
            )
            try:
                current_action_set.by_ref(selected_action_ref)
            except KeyError:
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": "stale or unknown ManagerActionSet action_ref",
                        "reason_codes": ["STALE_ACTION_REF"],
                    }
                )
                frontier.observe(
                    progress_before=frontier.progress(runtime),
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "stale_action_ref"},
                )
                continue

            progress_before = frontier.progress(runtime)

            if frontier.blocked(progress=progress_before, action=decision):
                observations.append(
                    {
                        "kind": "no_progress_blocked",
                        "action": self._manager_safe(decision),
                        "progress_fingerprint": progress_before,
                    }
                )
                continue

            if (
                decision.action == ManagerActionKind.RESOLVE_SEMANTICS
                and decision.resolve_provenance == "USER_SOURCE"
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "post-acceptance USER_SOURCE semantic reparsing is forbidden; "
                            "use accepted authority or AGENT_DERIVED evidence-grounded discovery"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "post_acceptance_user_source_reparse"},
                )
                continue

            if (
                decision.action == ManagerActionKind.RESOLVE_SEMANTICS
                and decision.resolve_provenance == "AGENT_DERIVED"
                and decision.semantic_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "AGENT_DERIVED semantic discovery requires inspected evidence "
                            "from the current run"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "derived_semantic_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.RUN_ANALYTICS
                and decision.derived_task_id is not None
                and decision.derived_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": (
                            "derived analytics branch requires inspect_evidence on "
                            "derived_evidence_ref first"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "derived_run_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.PROPOSE_BRANCHES
                and decision.branch_evidence_ref
                not in runtime.snapshot.inspected_evidence_refs
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": "branch proposal requires inspected current-run evidence",
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "branch_requires_inspected_evidence"},
                )
                continue

            if (
                decision.action == ManagerActionKind.REQUEST_CLARIFICATION
                and not _clarification_has_governed_grounding(
                    observations,
                    accepted_contract_present=True,
                )
            ):
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": "clarification lacks governed grounding",
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"rejected": "clarification_ungrounded"},
                )
                continue

            if decision.action == ManagerActionKind.PROPOSE_GOAL_TASK:
                try:
                    task, result_view = self._materialize_goal_task_from_decision(
                        message_id=message_id,
                        runtime=runtime,
                        executor=executor,
                        task_registry=task_registry,
                        decision=decision,
                        action_ref=selected_action_ref,
                    )
                    observations.append(result_view)
                    if task is None:
                        frontier.observe(
                            progress_before=progress_before,
                            action=decision,
                            runtime=runtime,
                            result=result_view,
                        )
                        continue

                    scheduled = self._execute_scheduled_task(
                        runtime=runtime,
                        executor=executor,
                        task_registry=task_registry,
                        task=task,
                        capability_key=decision.goal_task_capability,
                        ranking_direction=decision.goal_task_ranking_direction,
                        ranking_limit=decision.goal_task_ranking_limit,
                    )
                    execution_outcome = ResearchExecutionOutcome.project(scheduled)
                    if execution_outcome.blocked:
                        result_view = {
                            **result_view,
                            "execution_state": scheduled.task.state,
                            "evidence_ref": None,
                        }
                        observations.append(
                            {
                                "kind": "goal_task_blocked",
                                "task_id": scheduled.task.task_id,
                                "result": self._manager_safe(
                                    scheduled.observation
                                ),
                            }
                        )
                        self._emit_progress(
                            "research_task_blocked",
                            (scheduled.task.task_id,),
                        )
                    else:
                        evidence = execution_outcome.require_evidence()
                        result_view = {
                            **result_view,
                            "execution_state": scheduled.task.state,
                            "evidence_ref": evidence.artifact_id,
                        }
                        observations.append(
                            {
                                "kind": "goal_task_executed",
                                "task_id": scheduled.task.task_id,
                                "tool_id": scheduled.contract.tool_id,
                                "evidence_ref": evidence.artifact_id,
                            }
                        )
                        self._emit_progress(
                            "evidence_verified",
                            (evidence.artifact_id,),
                        )
                        if evidence.evidence_kind == "relationship_analytics":
                            self._emit_progress(
                                "relationship_checked",
                                (evidence.artifact_id,),
                            )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                except Exception as exc:
                    observations.append(
                        {
                            "kind": "goal_task_materialization_error",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "goal_task_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action == ManagerActionKind.PROPOSE_HYPOTHESIS_WITH_NEXT_TEST:
                try:
                    if not root_cause_ledgers:
                        raise RootCauseOrchestrationError(
                            "Day8 composite epistemic action requires active ROOT_CAUSE authority"
                        )
                    root_id = str(decision.hypothesis_parent_obligation_id)
                    ledger = root_cause_ledgers[root_id]
                    hypothesis = HypothesisProposalBoundary(
                        ledger=ledger
                    ).register(
                        HypothesisProposal(
                            statement=decision.hypothesis_statement,
                            semantic_handle_refs=self._decode_handles(
                                decision.hypothesis_semantic_handles
                            ),
                            trigger_evidence_refs=decision.hypothesis_trigger_evidence_refs,
                            limitations=decision.hypothesis_limitations,
                        )
                    )
                    observations.append(
                        {
                            "kind": "hypothesis_registered",
                            "result": {
                                "hypothesis_id": hypothesis.hypothesis_id,
                                "parent_obligation_id": hypothesis.parent_obligation_id,
                                "status": hypothesis.status.value,
                                "trigger_evidence_refs": list(
                                    hypothesis.trigger_evidence_refs
                                ),
                                "composite_plan": True,
                            },
                        }
                    )

                    next_test_proposal = HypothesisNextTestProposal(
                        hypothesis_ref=hypothesis.hypothesis_id,
                        task_kind=decision.next_test_task_kind,
                        input_refs=self._decode_handles(
                            decision.next_test_input_handles
                        ),
                        trigger_evidence_ref=decision.next_test_trigger_evidence_ref,
                        material_reason=decision.next_test_material_reason,
                        ranking_direction=decision.next_test_ranking_direction,
                        ranking_limit=decision.next_test_ranking_limit,
                    )
                    task = HypothesisNextTestBoundary(
                        ledger=ledger,
                        runtime=runtime,
                        evidence_store=executor.evidence_store,
                        semantic_handles=self._root_cause_context.semantic_handles,
                        task_registry=task_registry,
                        tenant_binding=self._root_cause_context.tenant_binding,
                        context_version=self._root_cause_context.context_version,
                        task_service=self._research_tasks,
                        capabilities=self._capabilities,
                    ).materialize(next_test_proposal)
                    capability = self._research_tasks.capability_for_task_kind(
                        next_test_proposal.task_kind
                    )
                    execution = self._execute_scheduled_task(
                        runtime=runtime,
                        executor=executor,
                        task_registry=task_registry,
                        task=task,
                        capability_key=capability,
                        ranking_direction=decision.next_test_ranking_direction,
                        ranking_limit=decision.next_test_ranking_limit,
                    )
                    execution_outcome = ResearchExecutionOutcome.project(execution)
                    result_view = {
                        "hypothesis_id": hypothesis.hypothesis_id,
                        "task_id": execution.task.task_id,
                        "task_kind": execution.task.task_kind,
                        "state": execution.task.state,
                        "trigger_evidence_ref": execution.task.trigger_evidence_ref,
                        "evidence_ref": None,
                        "tool_id": execution.contract.tool_id,
                    }
                    if execution_outcome.blocked:
                        observations.append(
                            {
                                "kind": "deterministic_task_blocked",
                                "task_id": execution.task.task_id,
                                "tool_id": execution.contract.tool_id,
                                "context": "hypothesis_composite_next_test",
                                "result": self._manager_safe(execution.observation),
                            }
                        )
                        self._emit_progress(
                            "research_task_blocked",
                            (execution.task.task_id,),
                        )
                    else:
                        evidence = execution_outcome.require_evidence()
                        result_view["evidence_ref"] = evidence.artifact_id
                        observations.append(
                            {
                                "kind": "hypothesis_next_test_executed",
                                "result": result_view,
                                "composite_plan": True,
                            }
                        )
                        self._emit_progress(
                            "evidence_verified",
                            (evidence.artifact_id,),
                        )
                        if evidence.evidence_kind == "relationship_analytics":
                            self._emit_progress(
                                "relationship_checked",
                                (evidence.artifact_id,),
                            )
                        accounted = self._account_root_next_test_as_adaptive_branch(
                            runtime=runtime,
                            evidence_store=executor.evidence_store,
                            task=execution.task,
                            root_obligation_id=root_id,
                            trigger_evidence_ref=str(
                                decision.next_test_trigger_evidence_ref
                            ),
                            result_evidence=evidence,
                        )
                        if accounted:
                            observations.append(
                                {
                                    "kind": "adaptive_branch_executed",
                                    "task_id": execution.task.task_id,
                                    "evidence_ref": evidence.artifact_id,
                                    "source": "hypothesis_next_test",
                                    "directive_ids": list(accounted),
                                }
                            )
                            self._emit_progress(
                                "adaptive_branch_opened",
                                (execution.task.task_id,),
                            )

                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                    root_changed = self._reconcile_root_obligations(
                        runtime=runtime,
                        root_cause_ledgers=root_cause_ledgers,
                        task_registry=task_registry,
                    )
                    if root_changed:
                        observations.append(
                            {
                                "kind": "root_cause_obligation_reconciled",
                                "status": "VERIFIED",
                            }
                        )
                    if self._try_deterministic_finish(
                        runtime=runtime,
                        task_registry=task_registry,
                    ):
                        observations.append(
                            {
                                "kind": "finish",
                                "status": "accepted",
                                "reason": "deterministic_completion_gate",
                            }
                        )
                        break
                except (
                    HypothesisProposalError,
                    RootCauseOrchestrationError,
                    ResearchTaskInvocationCompileError,
                    KeyError,
                    ValueError,
                ) as exc:
                    observations.append(
                        {
                            "kind": "tool_rejected",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "root_cause_composite_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action in {
                ManagerActionKind.PROPOSE_HYPOTHESIS,
                ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION,
                ManagerActionKind.PROPOSE_HYPOTHESIS_NEXT_TEST,
            }:
                try:
                    if not root_cause_ledgers:
                        raise RootCauseOrchestrationError(
                            "Day8 epistemic action requires active ROOT_CAUSE authority"
                        )

                    if decision.action == ManagerActionKind.PROPOSE_HYPOTHESIS:
                        ledger = root_cause_ledgers[
                            decision.hypothesis_parent_obligation_id
                        ]
                        hypothesis = HypothesisProposalBoundary(
                            ledger=ledger
                        ).register(
                            HypothesisProposal(
                                statement=decision.hypothesis_statement,
                                semantic_handle_refs=self._decode_handles(
                                    decision.hypothesis_semantic_handles
                                ),
                                trigger_evidence_refs=decision.hypothesis_trigger_evidence_refs,
                                limitations=decision.hypothesis_limitations,
                            )
                        )
                        result_view = {
                            "hypothesis_id": hypothesis.hypothesis_id,
                            "parent_obligation_id": hypothesis.parent_obligation_id,
                            "status": hypothesis.status.value,
                            "trigger_evidence_refs": list(
                                hypothesis.trigger_evidence_refs
                            ),
                        }
                        observation_kind = "hypothesis_registered"

                    elif (
                        decision.action
                        == ManagerActionKind.PROPOSE_HYPOTHESIS_EVIDENCE_RELATION
                    ):
                        ledger = self._ledger_for_hypothesis(
                            root_cause_ledgers,
                            decision.hypothesis_ref,
                        )
                        hypothesis = HypothesisProposalBoundary(
                            ledger=ledger
                        ).attach_relation(
                            HypothesisEvidenceRelationProposal(
                                hypothesis_ref=decision.hypothesis_ref,
                                evidence_ref=decision.hypothesis_relation_evidence_ref,
                                relation=decision.hypothesis_relation,
                            )
                        )
                        result_view = {
                            "hypothesis_id": hypothesis.hypothesis_id,
                            "evidence_links": [
                                {
                                    "evidence_ref": link.evidence_ref,
                                    "relation": link.relation.value,
                                }
                                for link in hypothesis.evidence_links
                            ],
                        }
                        observation_kind = "hypothesis_relation_admitted"

                    else:
                        ledger = self._ledger_for_hypothesis(
                            root_cause_ledgers,
                            decision.hypothesis_ref,
                        )
                        next_test_proposal = HypothesisNextTestProposal(
                            hypothesis_ref=decision.hypothesis_ref,
                            task_kind=decision.next_test_task_kind,
                            input_refs=self._decode_handles(
                                decision.next_test_input_handles
                            ),
                            trigger_evidence_ref=decision.next_test_trigger_evidence_ref,
                            material_reason=decision.next_test_material_reason,
                            ranking_direction=decision.next_test_ranking_direction,
                            ranking_limit=decision.next_test_ranking_limit,
                        )
                        task = HypothesisNextTestBoundary(
                            ledger=ledger,
                            runtime=runtime,
                            evidence_store=executor.evidence_store,
                            semantic_handles=self._root_cause_context.semantic_handles,
                            task_registry=task_registry,
                            tenant_binding=self._root_cause_context.tenant_binding,
                            context_version=self._root_cause_context.context_version,
                            task_service=self._research_tasks,
                            capabilities=self._capabilities,
                        ).materialize(next_test_proposal)
                        capability = self._research_tasks.capability_for_task_kind(
                            next_test_proposal.task_kind
                        )
                        execution = self._execute_scheduled_task(
                            runtime=runtime,
                            executor=executor,
                            task_registry=task_registry,
                            task=task,
                            capability_key=capability,
                            ranking_direction=decision.next_test_ranking_direction,
                            ranking_limit=decision.next_test_ranking_limit,
                        )
                        execution_outcome = ResearchExecutionOutcome.project(
                            execution
                        )
                        result_view = {
                            "hypothesis_id": decision.hypothesis_ref,
                            "task_id": execution.task.task_id,
                            "task_kind": execution.task.task_kind,
                            "state": execution.task.state,
                            "trigger_evidence_ref": execution.task.trigger_evidence_ref,
                            "evidence_ref": None,
                            "tool_id": execution.contract.tool_id,
                        }
                        if execution_outcome.blocked:
                            observation_kind = "deterministic_task_blocked"
                            self._emit_progress(
                                "research_task_blocked",
                                (execution.task.task_id,),
                            )
                        else:
                            evidence = execution_outcome.require_evidence()
                            result_view["evidence_ref"] = evidence.artifact_id
                            self._emit_progress(
                                "evidence_verified",
                                (evidence.artifact_id,),
                            )
                            if evidence.evidence_kind == "relationship_analytics":
                                self._emit_progress(
                                    "relationship_checked",
                                    (evidence.artifact_id,),
                                )
                            observation_kind = "hypothesis_next_test_executed"

                    observations.append(
                        {
                            "kind": observation_kind,
                            "result": result_view,
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                    root_changed = self._reconcile_root_obligations(
                        runtime=runtime,
                        root_cause_ledgers=root_cause_ledgers,
                        task_registry=task_registry,
                    )
                    if root_changed:
                        observations.append(
                            {
                                "kind": "root_cause_obligation_reconciled",
                                "status": "VERIFIED",
                            }
                        )
                    if self._try_deterministic_finish(
                        runtime=runtime,
                        task_registry=task_registry,
                    ):
                        observations.append(
                            {
                                "kind": "finish",
                                "status": "accepted",
                                "reason": "deterministic_completion_gate",
                            }
                        )
                        break
                except (
                    HypothesisProposalError,
                    RootCauseOrchestrationError,
                    KeyError,
                    ValueError,
                ) as exc:
                    observations.append(
                        {
                            "kind": "tool_rejected",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "root_cause_action_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action == ManagerActionKind.DISPOSITION_RESEARCH_DIRECTIVE:
                try:
                    disposition = self._admit_no_material_direction(
                        runtime=runtime,
                        evidence_store=executor.evidence_store,
                        directive_id=str(decision.directive_id),
                        evidence_ref=str(decision.directive_evidence_ref),
                        reason=str(decision.directive_reason),
                    )
                    result_view = disposition.model_dump(mode="json")
                    observations.append(
                        {
                            "kind": "research_directive_disposition",
                            "result": result_view,
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                    if self._try_deterministic_finish(
                        runtime=runtime,
                        task_registry=task_registry,
                    ):
                        observations.append(
                            {
                                "kind": "finish",
                                "status": "accepted",
                                "reason": "deterministic_completion_gate",
                            }
                        )
                        break
                except Exception as exc:
                    observations.append(
                        {
                            "kind": "tool_rejected",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "directive_disposition_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action == ManagerActionKind.PROPOSE_BRANCHES:
                try:
                    evidence = executor.evidence_store.get(
                        decision.branch_evidence_ref
                    )
                    parent_task = task_registry.get(evidence.task_id)
                    proposals = tuple(
                        DerivedResearchTaskProposal(
                            task_id=item.task_id,
                            task_kind=self._research_tasks.task_kind_for_capability(
                                item.capability_key
                            ),
                            parent_task_id=parent_task.task_id,
                            parent_obligation_id=decision.branch_parent_obligation_id,
                            trigger_evidence_ref=decision.branch_evidence_ref,
                            input_refs=self._decode_handles(item.input_handles),
                            material_reason=item.material_reason,
                        )
                        for item in decision.branch_candidates
                    )
                    materialized = self._research_tasks.materialize_derived_candidates(
                        runtime=runtime,
                        evidence_store=executor.evidence_store,
                        task_registry=task_registry,
                        parent_task=parent_task,
                        proposals=proposals,
                    )
                    result_view = {
                        "strategy": materialized.decision.strategy.value,
                        "classification": materialized.decision.classification.value,
                        "allowed_children": materialized.decision.allowed_children,
                        "selected_task_ids": [
                            task.task_id for task in materialized.registered_tasks
                        ],
                        "remaining_query_budget": runtime.remaining_data_queries,
                        "cardinality_source": "UNKNOWN",
                    }
                    observations.append(
                        {
                            "kind": "fanout_registered",
                            "result": result_view,
                        }
                    )
                    if materialized.registered_tasks:
                        self._emit_progress(
                            "adaptive_branch_opened",
                            tuple(task.task_id for task in materialized.registered_tasks),
                        )
                    if len(materialized.registered_tasks) == 1:
                        selected_task = materialized.registered_tasks[0]
                        candidate_by_id = {
                            item.task_id: item
                            for item in decision.branch_candidates
                        }
                        selected_candidate = candidate_by_id[selected_task.task_id]
                        try:
                            scheduled = self._execute_scheduled_task(
                                runtime=runtime,
                                executor=executor,
                                task_registry=task_registry,
                                task=selected_task,
                                capability_key=selected_candidate.capability_key,
                            )
                            execution_outcome = ResearchExecutionOutcome.project(
                                scheduled
                            )
                            if execution_outcome.blocked:
                                result_view["deterministic_execution"] = {
                                    "task_id": scheduled.task.task_id,
                                    "tool_id": scheduled.contract.tool_id,
                                    "state": scheduled.task.state,
                                    "evidence_ref": None,
                                }
                                observations.append(
                                    {
                                        "kind": "deterministic_task_blocked",
                                        "task_id": scheduled.task.task_id,
                                        "tool_id": scheduled.contract.tool_id,
                                        "context": "adaptive_branch",
                                        "result": self._manager_safe(
                                            scheduled.observation
                                        ),
                                    }
                                )
                                self._emit_progress(
                                    "research_task_blocked",
                                    (scheduled.task.task_id,),
                                )
                            else:
                                evidence = execution_outcome.require_evidence()
                                result_view["deterministic_execution"] = {
                                    "task_id": scheduled.task.task_id,
                                    "tool_id": scheduled.contract.tool_id,
                                    "state": scheduled.task.state,
                                    "evidence_ref": evidence.artifact_id,
                                }
                                observations.append(
                                    {
                                        "kind": "adaptive_branch_executed",
                                        "task_id": scheduled.task.task_id,
                                        "tool_id": scheduled.contract.tool_id,
                                        "evidence_ref": evidence.artifact_id,
                                    }
                                )
                                self._emit_progress(
                                    "evidence_verified",
                                    (evidence.artifact_id,),
                                )
                                if evidence.evidence_kind == "relationship_analytics":
                                    self._emit_progress(
                                        "relationship_checked",
                                        (evidence.artifact_id,),
                                    )
                                accounted_directives = (
                                    self._account_successful_adaptive_branch(
                                        runtime=runtime,
                                        evidence_store=executor.evidence_store,
                                        task=scheduled.task,
                                        result_evidence=evidence,
                                    )
                                )
                                if accounted_directives:
                                    observations.append(
                                        {
                                            "kind": "research_directive_accounted",
                                            "directive_ids": list(accounted_directives),
                                            "task_id": scheduled.task.task_id,
                                            "execution_path": "inline_adaptive_branch",
                                        }
                                    )
                        except ResearchTaskInvocationCompileError as exc:
                            observations.append(
                                {
                                    "kind": "deterministic_schedule_deferred",
                                    "task_id": selected_task.task_id,
                                    "reason": str(exc),
                                }
                            )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result=result_view,
                    )
                except Exception as exc:
                    observations.append(
                        {
                            "kind": "tool_rejected",
                            "action": decision.action.value,
                            "message": str(exc),
                        }
                    )
                    frontier.observe(
                        progress_before=progress_before,
                        action=decision,
                        runtime=runtime,
                        result={
                            "branch_error": type(exc).__name__,
                            "message": str(exc),
                        },
                    )
                continue

            if decision.action == ManagerActionKind.FINISH:
                if self._try_deterministic_finish(
                    runtime=runtime,
                    task_registry=task_registry,
                ):
                    observations.append({"kind": "finish", "status": "accepted"})
                    break
                observations.append(
                    {
                        "kind": "finish_rejected",
                        "message": (
                            "deterministic completion/directive/task accounting is incomplete"
                        ),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={
                        "finish_rejected": (
                            "deterministic completion/directive/task accounting is incomplete"
                        )
                    },
                )
                continue

            try:
                call = self._compile_tool(
                    decision=decision,
                    message_id=message_id,
                    source_hash=source_hash,
                    request_ref=request_ref,
                    runtime=runtime,
                )
                assert call is not None

                research_execution = None
                if (
                    self._research_tool_runner is not None
                    and decision.action in {
                        ManagerActionKind.RUN_ANALYTICS,
                        ManagerActionKind.RUN_RELATIONSHIP,
                    }
                ):
                    if decision.research_task_id is not None:
                        try:
                            task = task_registry.get(decision.research_task_id)
                        except Exception as exc:
                            raise ResearchTaskMaterializationError(
                                "server-hydrated READY ResearchTask identity is no longer registered"
                            ) from exc
                        if task.state != "pending":
                            raise ResearchTaskMaterializationError(
                                "server-hydrated READY ResearchTask is no longer pending"
                            )
                        if (
                            decision.derived_task_id is not None
                            and decision.derived_task_id != decision.research_task_id
                        ):
                            raise ResearchTaskMaterializationError(
                                "derived ResearchTask identity drifted during hydration"
                            )
                    elif decision.action == ManagerActionKind.RUN_RELATIONSHIP:
                        obligation_id = decision.relationship_obligation_id
                        task_id = f"seed:{obligation_id}"
                        try:
                            task = task_registry.get(task_id)
                        except Exception:
                            task = self._research_tasks.seed_for_obligation(
                                runtime=runtime,
                                obligation_id=obligation_id,
                                task_id=task_id,
                            )
                            task_registry.register(task)
                    elif decision.derived_task_id is None:
                        if len(decision.obligation_ids) != 1:
                            raise ResearchTaskMaterializationError(
                                "Day7 one tool invocation maps to exactly one ResearchTask"
                            )
                        obligation_id = decision.obligation_ids[0]
                        task_id = f"seed:{obligation_id}"
                        try:
                            task = task_registry.get(task_id)
                        except ResearchTaskMaterializationError:
                            raise
                        except Exception:
                            task = self._pending_user_seed_for_obligation(
                                task_registry=task_registry,
                                obligation_id=obligation_id,
                            )
                            if task is None:
                                task = self._research_tasks.seed_for_obligation(
                                    runtime=runtime,
                                    obligation_id=obligation_id,
                                    task_id=task_id,
                                )
                    else:
                        try:
                            task = task_registry.get(decision.derived_task_id)
                        except Exception as exc:
                            raise ResearchTaskMaterializationError(
                                "derived execution requires pre-registered READY ResearchTask; "
                                "use propose_branches first"
                            ) from exc
                        if task.state != "pending":
                            raise ResearchTaskMaterializationError(
                                "derived execution requires pending READY ResearchTask"
                            )

                    tool_id = self._research_tool_runner.tool_id_for_task(task)
                    research_execution = self._research_tool_runner.execute(
                        task=task,
                        tool_id=tool_id,
                        call=call,
                        runtime=runtime,
                        executor=executor,
                        principal=getattr(executor, "principal", None),
                        task_registry=task_registry,
                        cancel_check=self._cancel_check,
                    )
                    manager_result = self._manager_safe(
                        research_execution.observation
                    )
                    execution_outcome = ResearchExecutionOutcome.project(
                        research_execution
                    )
                    if execution_outcome.blocked:
                        self._emit_progress(
                            "research_task_blocked",
                            (research_execution.task.task_id,),
                        )
                    else:
                        evidence = execution_outcome.require_evidence()
                        self._emit_progress(
                            "evidence_verified",
                            (evidence.artifact_id,),
                        )
                        if evidence.evidence_kind == "relationship_analytics":
                            self._emit_progress(
                                "relationship_checked",
                                (evidence.artifact_id,),
                            )
                        accounted_directives = (
                            self._account_successful_adaptive_branch(
                                runtime=runtime,
                                evidence_store=executor.evidence_store,
                                task=research_execution.task,
                                result_evidence=evidence,
                            )
                        )
                        if accounted_directives:
                            observations.append(
                                {
                                    "kind": "research_directive_accounted",
                                    "directive_ids": list(accounted_directives),
                                    "task_id": research_execution.task.task_id,
                                    "execution_path": "manager_selected_derived_task",
                                }
                            )
                else:
                    result = runtime.call_tool(call, executor=executor)
                    manager_result = self._manager_safe(result.tool_result)

                observations.append(
                    {
                        "kind": "tool",
                        "tool": call.name.value,
                        "research_task_id": (
                            None
                            if research_execution is None
                            else research_execution.task.task_id
                        ),
                        "result": manager_result,
                    }
                )

                if root_cause_ledgers:
                    root_changed = self._reconcile_root_obligations(
                        runtime=runtime,
                        root_cause_ledgers=root_cause_ledgers,
                        task_registry=task_registry,
                    )
                    if root_changed:
                        observations.append(
                            {
                                "kind": "root_cause_obligation_reconciled",
                                "status": "VERIFIED",
                            }
                        )

                if (
                    call.name == ManagerToolName.INSPECT_EVIDENCE
                    and _zero_row_completion_candidate(
                        runtime=runtime,
                        evidence_store=getattr(executor, "evidence_store", None),
                        task_registry=task_registry,
                    )
                ):
                    try:
                        runtime.finish()
                        observations.append(
                            {
                                "kind": "finish",
                                "status": "accepted",
                                "reason": "inspected_zero_row_no_material_branch",
                            }
                        )
                        break
                    except ManagerStateError:
                        # CompletionGate remains the sole completion authority.
                        # If it rejects, the bounded Manager loop may continue.
                        pass

                progressed = frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result=manager_result,
                )
                if not progressed:
                    observations.append(
                        {
                            "kind": "no_progress",
                            "action": self._manager_safe(decision),
                            "progress_fingerprint": frontier.progress(runtime),
                        }
                    )
            except Exception as exc:
                observations.append(
                    {
                        "kind": "tool_rejected",
                        "action": decision.action.value,
                        "message": str(exc),
                    }
                )
                frontier.observe(
                    progress_before=progress_before,
                    action=decision,
                    runtime=runtime,
                    result={"tool_error": type(exc).__name__, "message": str(exc)},
                )
                if runtime.snapshot.state == ManagerState.FAILED:
                    break
                continue

        canonical_findings: list[EvidenceLinkedFinding] = []
        for ledger in root_cause_ledgers.values():
            builder = EvidenceLinkedFindingBuilder(ledger=ledger)
            for hypothesis in ledger.state.entries:
                if hypothesis.status == HypothesisStatus.SUPPORTED:
                    finding_refs = tuple(
                        link.evidence_ref
                        for link in hypothesis.evidence_links
                        if link.relation == HypothesisEvidenceRelation.SUPPORTS
                    )
                    finding_label = EpistemicLabel.CANDIDATE_CAUSE
                elif hypothesis.status == HypothesisStatus.INCONCLUSIVE:
                    finding_refs = tuple(
                        dict.fromkeys(
                            link.evidence_ref
                            for link in hypothesis.evidence_links
                        )
                    )
                    finding_label = EpistemicLabel.OBSERVATION
                else:
                    continue
                if not finding_refs:
                    continue
                try:
                    finding = builder.build(
                        statement=hypothesis.statement,
                        epistemic_label=finding_label,
                        evidence_refs=finding_refs,
                        hypothesis_ref=hypothesis.hypothesis_id,
                    )
                    canonical_findings.append(finding)
                    self._emit_progress(
                        "root_cause_candidate",
                        (finding.finding_id,),
                    )
                except EpistemicFindingError as exc:
                    observations.append(
                        {
                            "kind": "finding_projection_rejected",
                            "hypothesis_id": hypothesis.hypothesis_id,
                            "message": str(exc),
                        }
                    )

        return ManagerLoopOutcome(
            snapshot=runtime.snapshot,
            run_finished=runtime.snapshot.state == ManagerState.COMPLETED,
            verified_complete=(
                runtime.snapshot.terminal_status == ResearchRunTerminal.VERIFIED_COMPLETE
            ),
            terminal_status=runtime.snapshot.terminal_status,
            clarification_required=(
                runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION
            ),
            observations=tuple(observations),
            preacceptance_status=FiniteAcceptanceStatus.ACCEPTED,
            findings=tuple(canonical_findings),
            research_tasks=tuple(task_registry.tasks),
            hypothesis_states=tuple(
                ledger.state
                for _root_id, ledger in sorted(root_cause_ledgers.items())
            ),
            directive_dispositions=runtime.directive_dispositions,
            cancelled=cancelled,
            answer_now_requested=answer_now_requested,
        )
